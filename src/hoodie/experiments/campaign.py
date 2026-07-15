from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv
import json
from statistics import mean, pstdev
from typing import Any

from src.evaluation.campaign_config import CampaignConfig
from src.evaluation.config import EvaluationConfig
from src.evaluation.metrics import TaskEvaluationRecord, TraceMetrics
from src.evaluation.paired_evaluation import TaskRecord as PairedTaskRecord, paired_metric_summary, validate_fairness
from src.evaluation.policy_registry import PolicyRegistry
from src.evaluation.runner import EvaluationRunner
from src.evaluation.trace_protocol import TraceTaskBlueprint, build_deterministic_trace
from src.reference_model.models import TaskWorkload
from .specification import ExperimentSpec
from src.hoodie.experiments.aggregation import aggregate_records
from src.hoodie.experiments.job_identity import compute_experiment_id, compute_job_id
from src.hoodie.experiments.panel_registry import PANEL_REGISTRY
from src.hoodie.experiments.provenance import build_provenance_manifest, provenance_hash
from src.hoodie.experiments.schemas import AggregateRecord, DecisionRecord, TaskRecord, TrainingHistoryRecord, TransitionRecord
from src.hoodie.experiments.source_contracts import build_figures_8_11_source_contract, write_figures_8_11_source_contract
from src.hoodie.experiments.storage import AtomicJobStorage
from src.hoodie.experiments.trace_registry import TraceRecord, TraceRegistry
from src.policies.policy_interface import PolicyContext

@dataclass(slots=True)
class SmokeJobResult:
    panel_id: str
    job_id: str
    output_dir: Path
    records: list[TaskRecord]
    aggregate: AggregateRecord
    render_paths: dict[str, str]


def _policy_for_name(name: str):
    return PolicyRegistry.resolve(name)


def _smoke_trace(panel_id: str, seed: int, horizon: int) -> TraceRegistry:
    evaluation_trace = build_deterministic_trace(f"{panel_id}-{seed}", seed, horizon, agent_count=3, arrival_probability=0.5, timeout_length=max(3, horizon // 2), drain_slots=0)
    records = [TraceRecord(TraceTaskBlueprint(task.task_id, task.source_agent_id, task.arrival_slot, task.size, task.processing_density, task.timeout_length, task.absolute_deadline_slot), TaskWorkload(int(task.size), int(task.timeout_length), int(task.arrival_slot)), seed) for task in evaluation_trace.tasks]
    return TraceRegistry.from_records(evaluation_trace.trace_id, records, source_hash="smoke-source")


def _trace_records(trace, policy_name: str, seed: int, campaign_id: str, panel_id: str, job_id: str, variant: str | None, checkpoint_hash: str) -> list[TaskRecord]:
    records: list[TaskRecord] = []
    for task in trace.raw_records:
        records.append(TaskRecord(
            campaign_id=campaign_id,
            panel_id=panel_id,
            job_id=job_id,
            run_id=trace.trace_id,
            policy=policy_name,
            variant=variant,
            seed=seed,
            trace_hash=trace.trace_id,
            task_id=str(task.task_id),
            source_agent=str(task.source_agent_id),
            arrival_slot=int(task.arrival_slot),
            workload={"task_size": task.task_id},
            deadline=None,
            decision_slot=int(task.arrival_slot),
            selected_action=str(task.selected_action or "local"),
            destination=str(task.resolved_destination or "local"),
            completion_or_drop_slot=task.completion_slot,
            outcome=str(task.terminal_outcome or "completed"),
            queue_delay=None,
            transmission_delay=None,
            service_delay=None,
            end_to_end_delay=float(task.delay) if task.delay is not None else None,
            reward=float(-(task.delay or 0)),
            learner_owner=policy_name,
            config_hash="config",
            source_hash="source",
            checkpoint_hash=checkpoint_hash,
        ))
    return records


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _run_campaign(*, campaign_id: str, output_dir: Path, smoke: bool, source_hash: str) -> dict[str, Any]:
    source_contract = build_figures_8_11_source_contract()
    source_contract_path = write_figures_8_11_source_contract(output_dir / "source_contract_snapshot.json")
    campaign_dir = output_dir / campaign_id
    jobs_dir = campaign_dir / "jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    status: dict[str, Any] = {"campaign_id": campaign_id, "smoke": smoke, "jobs": []}
    for panel_id, contract in PANEL_REGISTRY.items():
        spec = contract.spec
        policy_names = spec.policies or ("HOODIE",)
        for seed in (spec.seeds or (0,)):
            trace = _smoke_trace(panel_id, seed, max(4, spec.training_required and 8 or 4))
            policy_name = policy_names[0]
            policy = _policy_for_name(policy_name)
            config = EvaluationConfig(policy_name=policy_name, seed=seed, trace_id=trace.trace_id, episode_count=1, episode_length=max(4, spec.training_required and 8 or 4), output_dir=None)
            runner = EvaluationRunner(policy=policy, config=config)
            result = runner.run()
            trace_metrics = result["per_trace"][0]
            job_id = compute_job_id(
                ExperimentSpec(campaign_id=campaign_id, experiment_id=f"{panel_id}-{seed}", policy=policy_name, variant=spec.variants[0] if spec.variants else None, seed=seed, horizon=config.episode_length, warmup=0, workload={"task_count": len(trace.records)}),
                spec,
                source_commit=__import__('subprocess').run(['git','rev-parse','HEAD'], capture_output=True, text=True).stdout.strip(),
                trace_hash=trace.hash(),
            ).value
            job_dir = jobs_dir / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            raw_records = [TaskRecord(
                campaign_id=campaign_id,
                panel_id=panel_id,
                job_id=job_id,
                run_id=trace_metrics['trace_id'],
                policy=policy_name,
                variant=spec.variants[0] if spec.variants else None,
                seed=seed,
                trace_hash=trace_metrics['trace_id'],
                task_id=str(record['task_id']),
                source_agent=str(record['arrival_slot']),
                arrival_slot=record['arrival_slot'],
                workload={'task_count': len(trace.records)},
                deadline=None,
                decision_slot=record['arrival_slot'],
                selected_action=str(record['selected_action']),
                destination=str(record['resolved_destination']),
                completion_or_drop_slot=record['completion_slot'],
                outcome=str(record['terminal_outcome']),
                queue_delay=None,
                transmission_delay=None,
                service_delay=None,
                end_to_end_delay=float(record['delay']) if record['delay'] is not None else None,
                reward=float(-(record['delay'] or 0)),
                learner_owner=policy_name,
                config_hash='config',
                source_hash='source',
                checkpoint_hash='checkpoint',
            ) for record in trace_metrics['raw_records']]
            aggregate = aggregate_records(raw_records)
            _write_csv(job_dir / 'task_records.csv', [asdict(row) for row in raw_records])
            (job_dir / 'task_records.schema.json').write_text(json.dumps({'fields': list(asdict(raw_records[0]).keys()) if raw_records else []}, indent=2), encoding='utf-8')
            (job_dir / 'evaluation_metrics.json').write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
            (job_dir / 'aggregate.json').write_text(json.dumps(asdict(aggregate), indent=2, sort_keys=True), encoding='utf-8')
            provenance = build_provenance_manifest(config_hash='config', source_hash=source_hash, trace_hash=trace.hash(), checkpoint_hash='checkpoint')
            (job_dir / 'provenance.json').write_text(json.dumps({'manifest': asdict(provenance), 'hash': provenance_hash(provenance)}, indent=2, sort_keys=True), encoding='utf-8')
            (job_dir / 'completion.marker').write_text('complete\n', encoding='utf-8')
            status['jobs'].append({'panel_id': panel_id, 'job_id': job_id, 'completed': True, 'output_dir': str(job_dir)})
    (campaign_dir / 'campaign_specification.json').write_text(json.dumps({'campaign_id': campaign_id, 'smoke': smoke}, indent=2), encoding='utf-8')
    (campaign_dir / 'source_contract_snapshot.json').write_text(source_contract_path.read_text(encoding='utf-8'), encoding='utf-8')
    (campaign_dir / 'job_plan.json').write_text(json.dumps(status['jobs'], indent=2), encoding='utf-8')
    (campaign_dir / 'status.json').write_text(json.dumps({'campaign_id': campaign_id, 'completed_jobs': len(status['jobs'])}, indent=2), encoding='utf-8')
    (campaign_dir / 'environment_manifest.json').write_text(json.dumps({'python': __import__('platform').python_version()}, indent=2), encoding='utf-8')
    (campaign_dir / 'source_manifest.json').write_text(json.dumps({'source_commit': __import__('subprocess').run(['git','rev-parse','HEAD'], capture_output=True, text=True).stdout.strip(), 'source_hash': source_hash}, indent=2), encoding='utf-8')
    (campaign_dir / 'trace_registry.json').write_text(json.dumps({'trace_ids': [job['job_id'] for job in status['jobs']]}, indent=2), encoding='utf-8')
    (campaign_dir / 'checkpoint_registry.json').write_text(json.dumps({'checkpoints': []}, indent=2), encoding='utf-8')
    (campaign_dir / 'aggregation_manifest.json').write_text(json.dumps({'aggregated_jobs': len(status['jobs'])}, indent=2), encoding='utf-8')
    (campaign_dir / 'verification_report.json').write_text(json.dumps({'fairness': 'not_yet_implemented', 'sanity': 'not_yet_implemented'}, indent=2), encoding='utf-8')
    return status


def run_smoke_campaign(*, campaign_id: str, output_dir: Path, smoke: bool = True) -> dict[str, Any]:
    return _run_campaign(campaign_id=campaign_id, output_dir=output_dir, smoke=smoke, source_hash='smoke-source')


def run_production_campaign(*, campaign_id: str, output_dir: Path) -> dict[str, Any]:
    return _run_campaign(campaign_id=campaign_id, output_dir=output_dir, smoke=False, source_hash='production-source')
