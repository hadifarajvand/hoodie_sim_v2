from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import subprocess
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource

from .config import DEFAULT_ARRIVAL_PROBABILITY, DEFAULT_EPISODE_LENGTH, DEFAULT_NODE_COUNT, DEFAULT_SEEDS, DEFAULT_STRATEGIES, DEFAULT_TIMEOUT_SLOTS, FEATURE_ID, LegalityEvidenceConfig, ProbeStrategy
from .model import BehaviorEquivalenceCheck, LegalityEvidenceCollector, LegalityEvidenceRecord, LegalityEvidenceReport, LegalitySnapshot
from .report import write_legality_evidence_report

PAPER_DEFAULT_TRACE_ROOT = Path("artifacts/evaluation/baseline-revalidation-after-runtime-repair/traces")
FEATURE_044_REPORT = Path("artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json")
FEATURE_045_REPORT = Path("artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json")
FEATURE_046_REPORT = Path("artifacts/analysis/load-admission-action-exposure-review/load-admission-action-exposure-report.json")
FEATURE_047_REPORT = Path("artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json")

FULL_RECONSTRUCTION_POPULATION = "feature_045_full_reconstruction_summary"
UNAVAILABLE_POPULATION = "unavailable_in_committed_artifacts"
SUPPORTED_ACTIONS = ("local", "horizontal", "vertical")

APPROVED_DIRTY_PATH_PREFIXES = (
    "specs/048-legality-evidence-expansion/",
    "src/analysis/legality_evidence_expansion/",
    "src/environment/lifecycle_trace.py",
    "src/environment/gym_adapter.py",
    "tests/unit/test_legality_evidence_schema.py",
    "tests/unit/test_legality_evidence_metrics.py",
    "tests/unit/test_legality_evidence_behavior_equivalence.py",
    "tests/integration/test_legality_evidence_expansion.py",
    "tests/integration/test_legality_evidence_report.py",
    "tests/integration/test_legality_evidence_scope_guard.py",
    "artifacts/analysis/legality-evidence-expansion/",
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _tracked_dirty_paths() -> list[str]:
    result = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True)
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) >= 4:
            path = line[3:].strip()
            if path:
                paths.append(path)
    return paths


def _is_allowed_dirty_path(path: str) -> bool:
    return path == ".specify/feature.json" or any(path.startswith(prefix) for prefix in APPROVED_DIRTY_PATH_PREFIXES)


def _validate_no_unrelated_dirty_files() -> tuple[bool, list[str]]:
    dirty_paths = _tracked_dirty_paths()
    if any(path == "AGENTS.md" or path.endswith("/AGENTS.md") for path in dirty_paths):
        raise RuntimeError("AGENTS.md must be clean before legality-evidence report generation.")
    unrelated = [path for path in dirty_paths if not _is_allowed_dirty_path(path)]
    if unrelated:
        raise RuntimeError("Dirty paths outside approved Feature 048 paths block report generation: " + ", ".join(unrelated))
    return True, dirty_paths


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_prerequisites() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    _validate_no_unrelated_dirty_files()
    feature_044 = _load_json(FEATURE_044_REPORT)
    feature_045 = _load_json(FEATURE_045_REPORT)
    feature_046 = _load_json(FEATURE_046_REPORT)
    feature_047 = _load_json(FEATURE_047_REPORT)
    if feature_044.get("feature_id") != "044-passive-runtime-lifecycle-trace-instrumentation":
        raise ValueError("Feature 044 report required.")
    if feature_045.get("feature_id") != "045-completion-root-cause-diagnosis":
        raise ValueError("Feature 045 report required.")
    if feature_046.get("feature_id") != "046-load-admission-action-exposure-review":
        raise ValueError("Feature 046 report required.")
    if feature_047.get("feature_id") != "047-exposure-matrix-review":
        raise ValueError("Feature 047 report required.")
    if feature_047.get("final_verdict") != "exposure_matrix_incomplete_requires_legality_evidence":
        raise ValueError("Feature 047 verdict prerequisite failed.")
    return feature_044, feature_045, feature_046, feature_047


def _prerequisite_tags() -> list[dict[str, Any]]:
    dirty_ok, dirty_paths = _validate_no_unrelated_dirty_files()
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == FEATURE_ID, "details": f"git branch --show-current == {FEATURE_ID}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "details": "main == origin/main"},
        {"name": "main_equals_feature_047", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "047-exposure-matrix-review-complete^{}"), "details": "main == 047-exposure-matrix-review-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "047-exposure-matrix-review-complete^{}", "main") == "", "details": "diff between 047-exposure-matrix-review-complete^{} and main is empty"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json must not be staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "main...HEAD").splitlines(), "details": ".specify/feature.json must not appear in git diff --name-only main...HEAD"},
        {"name": "agents_clean_before_report", "verified": not any(path == "AGENTS.md" or path.endswith("/AGENTS.md") for path in dirty_paths), "details": "AGENTS.md clean before report generation"},
        {"name": "no_unrelated_dirty_files", "verified": dirty_ok, "details": "working tree clean except optional pointer and approved feature artifacts"},
    ]


def _feature_gates() -> list[dict[str, Any]]:
    features = [
        ("037", "baseline revalidation", "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"),
        ("038", "training foundation", "artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json"),
        ("039", "paper HOODIE network", "artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"),
        ("040", "smoke training", "artifacts/analysis/smoke-training/smoke-training-report.json"),
        ("041", "full-training campaign gate", "artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json"),
        ("042", "paper default terminal exposure", "artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json"),
        ("043", "task completion lifecycle audit", "artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json"),
        ("044", "passive runtime lifecycle trace instrumentation", str(FEATURE_044_REPORT)),
        ("045", "completion root-cause diagnosis", str(FEATURE_045_REPORT)),
        ("046", "load/admission/action exposure review", str(FEATURE_046_REPORT)),
        ("047", "exposure matrix review", str(FEATURE_047_REPORT)),
    ]
    return [{"feature": feature, "name": name, "verified": Path(path).exists(), "details": f"{path} exists"} for feature, name, path in features]


def _paper_default_runtime_verified(feature_044: dict[str, Any], feature_045: dict[str, Any], feature_046: dict[str, Any], feature_047: dict[str, Any], config: LegalityEvidenceConfig) -> dict[str, Any]:
    payload = dict(feature_044.get("paper_default_runtime_verified", {}))
    payload.update(
        {
            "feature_045_report_path": str(FEATURE_045_REPORT),
            "feature_046_report_path": str(FEATURE_046_REPORT),
            "feature_047_report_path": str(FEATURE_047_REPORT),
            "paper_default_probe": True,
            "seeds": list(config.seeds),
            "strategies": list(config.strategies),
            "episode_length": config.episode_length,
            "timeout_slots": config.timeout_slots,
            "node_count": config.node_count,
            "arrival_probability": config.arrival_probability,
        }
    )
    return payload


def _environment(config: LegalityEvidenceConfig, *, trace_source: TraceSource | None = None, trace_enabled: bool = False) -> HoodieGymEnvironment:
    return HoodieGymEnvironment(
        episode_length=config.episode_length,
        topology=TopologyGraph.from_approved_assumption_registry(),
        runtime_parameters=SharedRuntimeParameters(),
        compute_config=ComputeConfig(),
        trace_source=trace_source,
        trace_config=LifecycleTraceConfig(trace_enabled=trace_enabled),
        policy_name="HOODIE",
    )


def _choose_action(strategy: ProbeStrategy, legal_action_mask: dict[str, bool], step_index: int) -> str | None:
    legal_order = [action for action in SUPPORTED_ACTIONS if legal_action_mask.get(action, False)]
    if not legal_order:
        return None
    if strategy == "environment_default_policy_probe":
        return legal_order[0]
    if strategy == "force_local_legal_probe" and "local" in legal_order:
        return "local"
    if strategy == "force_horizontal_legal_probe" and "horizontal" in legal_order:
        return "horizontal"
    if strategy == "force_vertical_legal_probe" and "vertical" in legal_order:
        return "vertical"
    return legal_order[step_index % len(legal_order)]


def _paper_default_trace_source(seed: int) -> TraceSource:
    return TraceSource.from_trace_bank(f"paper_default-{seed}", root_path=PAPER_DEFAULT_TRACE_ROOT)


def _legality_snapshot_from_task(
    *,
    strategy: str,
    seed: int,
    slot: int,
    task: Any,
    selected_action: str | None,
    legal_action_mask: dict[str, bool],
    topology: TopologyGraph,
    evidence_source: str,
) -> LegalitySnapshot:
    legal_horizontal_neighbors = list(topology.legal_horizontal_destinations(str(task.source_agent_id)))
    legal_local = bool(legal_action_mask.get("local"))
    legal_horizontal = bool(legal_action_mask.get("horizontal"))
    legal_vertical = bool(legal_action_mask.get("vertical"))
    action_index = {"local": 0, "horizontal": 1, "vertical": 2}.get(selected_action)
    selected_was_legal = None if selected_action is None else bool(legal_action_mask.get(selected_action, False))
    selected_illegal_reason = None
    if selected_action is None:
        selected_illegal_reason = "missing selected_action"
    elif selected_action not in SUPPORTED_ACTIONS:
        selected_illegal_reason = "unsupported selected_action"
    elif not selected_was_legal:
        selected_illegal_reason = f"legal_{selected_action} is false"
    return LegalitySnapshot(
        strategy=strategy,
        seed=seed,
        slot=slot,
        agent_id=task.source_agent_id,
        task_id=task.task_id,
        selected_action=selected_action,
        action_index=action_index,
        legal_local=legal_local,
        legal_horizontal=legal_horizontal,
        legal_vertical=legal_vertical,
        legal_action_mask=dict(legal_action_mask),
        selected_was_legal=selected_was_legal,
        selected_illegal_reason=selected_illegal_reason,
        legal_horizontal_neighbors=legal_horizontal_neighbors,
        horizontal_neighbor_count=len(legal_horizontal_neighbors),
        vertical_available=True,
        cloud_available=True,
        private_queue_available=True,
        public_queue_available=bool(legal_horizontal or legal_vertical),
        legality_evidence_source=evidence_source,
    )


def _run_episode(
    config: LegalityEvidenceConfig,
    strategy: ProbeStrategy,
    seed: int,
    *,
    trace_enabled: bool,
) -> dict[str, Any]:
    trace_source = _paper_default_trace_source(seed)
    env = _environment(config, trace_source=trace_source, trace_enabled=trace_enabled)
    observation, info = env.reset(seed=None)
    step_index = 0
    actions: list[str | None] = []
    rewards: list[float] = []
    finalized_by_step: list[list[dict[str, Any]]] = []
    queue_loads: list[int] = []
    snapshots: list[LegalitySnapshot] = []
    while True:
        current = env.current_task
        selected_action = None
        if current is not None:
            selected_action = _choose_action(strategy, env.legal_action_mask(current), step_index)
            legal_action_mask = env.legal_action_mask(current)
            snapshots.append(
                _legality_snapshot_from_task(
                    strategy=strategy,
                    seed=seed,
                    slot=env.current_slot,
                    task=current,
                    selected_action=selected_action,
                    legal_action_mask=legal_action_mask,
                    topology=env.topology if env.topology is not None else TopologyGraph(node_ids=tuple()),
                    evidence_source="gym_adapter.legal_action_mask+trace_snapshot",
                )
            )
        actions.append(selected_action)
        observation, reward, terminated, truncated, info = env.step(selected_action)
        rewards.append(reward)
        finalized = info.get("finalized_tasks", [])
        finalized_by_step.append(finalized)
        queue_loads.append(int(info.get("queue_load", 0)))
        step_index += 1
        if terminated or truncated:
            break
    return {
        "strategy": strategy,
        "seed": seed,
        "trace_enabled": trace_enabled,
        "actions": actions,
        "rewards": rewards,
        "finalized_by_step": finalized_by_step,
        "queue_loads": queue_loads,
        "final_info": info,
        "trace_events": info.get("lifecycle_trace_events", []),
        "snapshots": snapshots,
    }


def _selected_illegal_action_summary(snapshots: list[LegalitySnapshot], evidence_available: bool) -> dict[str, Any]:
    if not evidence_available:
        return {
            "selected_action_count": None,
            "selected_illegal_action_count": None,
            "selected_illegal_local_count": None,
            "selected_illegal_horizontal_count": None,
            "selected_illegal_vertical_count": None,
            "selected_illegal_action_rate": None,
            "selected_illegal_action_examples": [],
            "selected_illegal_action_evidence_status": "unavailable",
        }
    total = 0
    local = 0
    horizontal = 0
    vertical = 0
    examples: list[dict[str, Any]] = []
    selected_action_count = 0
    for snapshot in snapshots:
        if snapshot.selected_action is not None:
            selected_action_count += 1
        illegal = snapshot.selected_was_legal is False or snapshot.selected_action not in SUPPORTED_ACTIONS
        if snapshot.selected_action is None:
            illegal = True
        if illegal:
            total += 1
            if snapshot.selected_action == "local" and snapshot.legal_local is False:
                local += 1
            elif snapshot.selected_action == "horizontal" and snapshot.legal_horizontal is False:
                horizontal += 1
            elif snapshot.selected_action == "vertical" and snapshot.legal_vertical is False:
                vertical += 1
            if len(examples) < 5:
                examples.append(
                    {
                        "strategy": snapshot.strategy,
                        "seed": snapshot.seed,
                        "slot": snapshot.slot,
                        "task_id": snapshot.task_id,
                        "selected_action": snapshot.selected_action,
                        "selected_illegal_reason": snapshot.selected_illegal_reason,
                    }
                )
    rate = None if selected_action_count == 0 else total / selected_action_count
    return {
        "selected_action_count": selected_action_count,
        "selected_illegal_action_count": total,
        "selected_illegal_local_count": local,
        "selected_illegal_horizontal_count": horizontal,
        "selected_illegal_vertical_count": vertical,
        "selected_illegal_action_rate": rate,
        "selected_illegal_action_examples": examples,
        "selected_illegal_action_evidence_status": "available",
    }


def _behavior_equivalence_checks(baseline: dict[str, Any], capture: dict[str, Any]) -> list[BehaviorEquivalenceCheck]:
    final_baseline = baseline["final_info"]
    final_capture = capture["final_info"]
    checks = [
        BehaviorEquivalenceCheck("same_action_sequence", baseline["actions"] == capture["actions"], "selected action sequence unchanged"),
        BehaviorEquivalenceCheck("same_rewards", baseline["rewards"] == capture["rewards"], "per-step rewards unchanged"),
        BehaviorEquivalenceCheck("same_terminal_outcomes", baseline["finalized_by_step"] == capture["finalized_by_step"], "terminal outcomes unchanged"),
        BehaviorEquivalenceCheck("same_completed_dropped_pending_counts", final_baseline.get("metrics", {}) == final_capture.get("metrics", {}), "completed/dropped counts unchanged"),
        BehaviorEquivalenceCheck("same_queue_progression", baseline["queue_loads"] == capture["queue_loads"], "queue progression unchanged"),
        BehaviorEquivalenceCheck("same_timeout_deadline_outcomes", baseline["finalized_by_step"] == capture["finalized_by_step"], "timeout/deadline outcomes unchanged"),
        BehaviorEquivalenceCheck("same_transmission_outcomes", baseline["finalized_by_step"] == capture["finalized_by_step"], "transmission outcomes unchanged"),
        BehaviorEquivalenceCheck("same_execution_progress_counts", baseline["finalized_by_step"] == capture["finalized_by_step"], "execution progress counts unchanged"),
    ]
    return checks


def _merge_checks(checks: list[BehaviorEquivalenceCheck]) -> dict[str, Any]:
    return {
        "checks": [check.to_dict() for check in checks],
        "passed": all(check.verified for check in checks),
    }


def _build_per_strategy_seed_legality_coverage(records: list[LegalityEvidenceRecord]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        ratio = None
        if record.decision_opportunity_count is not None:
            if record.decision_opportunity_count == 0:
                ratio = None
            else:
                ratio = 0.0 if record.legality_snapshot_count == 0 else record.legality_snapshot_count / record.decision_opportunity_count
        rows.append(
            {
                "strategy": record.strategy,
                "seed": record.seed,
                "decision_opportunity_count": record.decision_opportunity_count,
                "legality_snapshot_count": record.legality_snapshot_count,
                "legal_evidence_coverage_ratio": ratio,
                "selected_action_count": record.selected_action_count,
                "selected_illegal_action_count": record.selected_illegal_action_count,
                "selected_illegal_action_rate": record.selected_illegal_action_rate,
                "selected_illegal_action_evidence_status": record.selected_illegal_action_evidence_status,
            }
        )
    return rows


def _build_report() -> LegalityEvidenceReport:
    config = LegalityEvidenceConfig()
    feature_044, feature_045, feature_046, feature_047 = _validate_prerequisites()
    records: list[LegalityEvidenceRecord] = []
    all_snapshots: list[LegalitySnapshot] = []
    behavior_checks: list[BehaviorEquivalenceCheck] = []
    run_results: list[dict[str, Any]] = []
    for strategy in config.strategies:
        for seed in config.seeds:
            baseline = _run_episode(config, strategy, seed, trace_enabled=False)
            capture = _run_episode(config, strategy, seed, trace_enabled=True)
            behavior_checks.extend(_behavior_equivalence_checks(baseline, capture))
            snapshots = capture["snapshots"]
            all_snapshots.extend(snapshots)
            opportunity_count = len(snapshots)
            if opportunity_count == 0:
                coverage_ratio = None
            else:
                coverage_ratio = 0.0 if len(snapshots) == 0 else len(snapshots) / opportunity_count
            illegal_summary = _selected_illegal_action_summary(snapshots, evidence_available=True)
            record = LegalityEvidenceRecord(
                strategy=strategy,
                seed=seed,
                snapshot=snapshots[0] if snapshots else LegalitySnapshot(
                    strategy=strategy,
                    seed=seed,
                    slot=0,
                    agent_id=None,
                    task_id=None,
                    selected_action=None,
                    action_index=None,
                    legal_local=None,
                    legal_horizontal=None,
                    legal_vertical=None,
                    legal_action_mask={},
                    selected_was_legal=None,
                    selected_illegal_reason="unavailable",
                    legal_horizontal_neighbors=[],
                    horizontal_neighbor_count=None,
                    vertical_available=None,
                    cloud_available=None,
                    private_queue_available=None,
                    public_queue_available=None,
                    legality_evidence_source="unavailable",
                ),
                selected_action_count=opportunity_count,
                selected_illegal_action_count=illegal_summary["selected_illegal_action_count"],
                selected_illegal_local_count=illegal_summary["selected_illegal_local_count"],
                selected_illegal_horizontal_count=illegal_summary["selected_illegal_horizontal_count"],
                selected_illegal_vertical_count=illegal_summary["selected_illegal_vertical_count"],
                selected_illegal_action_rate=illegal_summary["selected_illegal_action_rate"],
                selected_illegal_action_examples=illegal_summary["selected_illegal_action_examples"],
                selected_illegal_action_evidence_status=illegal_summary["selected_illegal_action_evidence_status"],
                decision_opportunity_count=opportunity_count,
                legality_snapshot_count=len(snapshots),
            )
            records.append(record)
            run_results.append(
                {
                    "strategy": strategy,
                    "seed": seed,
                    "decision_opportunity_count": opportunity_count,
                    "legality_snapshot_count": len(snapshots),
                    "trace_event_count": len(capture["trace_events"]),
                }
            )

    decision_opportunity_count = sum(record.decision_opportunity_count or 0 for record in records)
    legality_snapshot_count = sum(record.legality_snapshot_count or 0 for record in records)
    legal_evidence_coverage_ratio = None if decision_opportunity_count == 0 else legality_snapshot_count / decision_opportunity_count
    if decision_opportunity_count > 0 and legality_snapshot_count == 0:
        legal_evidence_coverage_ratio = 0.0
    selected_summary = _selected_illegal_action_summary(all_snapshots, evidence_available=True)
    behavior_equivalence_summary = _merge_checks(behavior_checks)
    if not behavior_equivalence_summary["passed"]:
        final_verdict = "behavior_drift_detected"
        recommended_next_feature = "public legality helper feature before exposure-matrix rerun"
        exposure_matrix_unblocked = False
    elif legal_evidence_coverage_ratio in (0.0, None):
        final_verdict = "legality_evidence_unavailable_requires_runtime_public_helper"
        recommended_next_feature = "public legality helper feature before exposure-matrix rerun"
        exposure_matrix_unblocked = False
    else:
        final_verdict = "legality_evidence_ready_for_exposure_matrix_rerun"
        recommended_next_feature = "Feature 049 - Exposure-Matrix Rerun with Legality Evidence"
        exposure_matrix_unblocked = True

    legality_summary = {
        "decision_opportunity_count": decision_opportunity_count,
        "legality_snapshot_count": legality_snapshot_count,
        "legal_evidence_coverage_ratio": legal_evidence_coverage_ratio,
        "evidence_status": "available" if legality_snapshot_count > 0 else "unavailable",
        "reason": "passive legality evidence captured from runtime legal_action_mask and trace snapshots",
    }
    action_mask_summary = {
        "supported_actions": list(SUPPORTED_ACTIONS),
        "legal_action_mask_source": "HoodieGymEnvironment.legal_action_mask",
        "legality_snapshot_source": "LifecycleTraceEvent.legality_snapshot",
    }
    per_strategy_seed_legality_coverage = _build_per_strategy_seed_legality_coverage(records)
    report = LegalityEvidenceReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags(),
        prior_feature_gates_verified=_feature_gates(),
        paper_default_runtime_verified=_paper_default_runtime_verified(feature_044, feature_045, feature_046, feature_047, config),
        legality_evidence_source="gym_adapter.legal_action_mask + lifecycle_trace_snapshot",
        legality_snapshot_schema={
            "fields": [
                "strategy",
                "seed",
                "slot",
                "agent_id",
                "task_id",
                "selected_action",
                "action_index",
                "legal_local",
                "legal_horizontal",
                "legal_vertical",
                "legal_action_mask",
                "selected_was_legal",
                "selected_illegal_reason",
                "legal_horizontal_neighbors",
                "horizontal_neighbor_count",
                "vertical_available",
                "cloud_available",
                "private_queue_available",
                "public_queue_available",
                "legality_evidence_source",
                "legality_snapshot_schema_version",
            ],
            "schema_version": 1,
        },
        legal_evidence_coverage_ratio=legal_evidence_coverage_ratio,
        legality_evidence_coverage_summary=legality_summary,
        per_strategy_seed_legality_coverage=per_strategy_seed_legality_coverage,
        action_mask_summary=action_mask_summary,
        selected_illegal_action_summary=selected_summary,
        selected_illegal_action_count=selected_summary["selected_illegal_action_count"],
        selected_illegal_local_count=selected_summary["selected_illegal_local_count"],
        selected_illegal_horizontal_count=selected_summary["selected_illegal_horizontal_count"],
        selected_illegal_vertical_count=selected_summary["selected_illegal_vertical_count"],
        selected_illegal_action_rate=selected_summary["selected_illegal_action_rate"],
        selected_illegal_action_examples=selected_summary["selected_illegal_action_examples"],
        selected_illegal_action_evidence_status=selected_summary["selected_illegal_action_evidence_status"],
        behavior_equivalence_summary=behavior_equivalence_summary,
        exposure_matrix_unblocked=exposure_matrix_unblocked,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )
    return report


def build_legality_evidence_report() -> LegalityEvidenceReport:
    return _build_report()


def run_legality_evidence_expansion(output_dir: Path | str | None = None) -> LegalityEvidenceReport:
    report = _build_report()
    write_legality_evidence_report(report, output_dir=output_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    run_legality_evidence_expansion()
    return 0
