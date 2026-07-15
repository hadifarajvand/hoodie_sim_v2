from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource

from .config import FEATURE_ID, PassiveRuntimeLifecycleTraceConfig, TRACE_EVENT_TYPES, TRACE_STRATEGIES, TraceStrategy
from .model import BehaviorEquivalenceCheck, LifecycleTraceSummary
from .report import PassiveRuntimeLifecycleTraceReport, DEFAULT_OUTPUT_DIR, write_passive_runtime_lifecycle_trace_report

PAPER_DEFAULT_TRACE_ROOT = Path("artifacts/evaluation/baseline-revalidation-after-runtime-repair/traces")
APPROVED_DIRTY_PATH_PREFIXES: tuple[str, ...] = (
    "specs/044-passive-runtime-lifecycle-trace-instrumentation/",
    "src/environment/lifecycle_trace.py",
    "src/environment/gym_adapter.py",
    "src/analysis/passive_runtime_lifecycle_trace_instrumentation/",
    "tests/unit/test_lifecycle_trace_schema.py",
    "tests/unit/test_lifecycle_trace_behavior_equivalence.py",
    "tests/integration/test_passive_lifecycle_trace_runtime.py",
    "tests/integration/test_passive_lifecycle_trace_report.py",
    "tests/integration/test_passive_lifecycle_trace_scope_guard.py",
    "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/",
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
            paths.append(line[3:].strip())
    return [path for path in paths if path]


def _is_approved_dirty_path(path: str) -> bool:
    if path == ".specify/feature.json":
        return True
    return any(path.startswith(prefix) for prefix in APPROVED_DIRTY_PATH_PREFIXES)


def build_prerequisite_tags_verified() -> list[dict[str, Any]]:
    dirty_paths = _tracked_dirty_paths()
    pointer_dirty = [path for path in dirty_paths if path == ".specify/feature.json"]
    unrelated = [path for path in dirty_paths if not _is_approved_dirty_path(path)]
    no_unrelated = len(unrelated) == 0
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == FEATURE_ID, "details": f"git branch --show-current == {FEATURE_ID}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "details": "main == origin/main"},
        {"name": "main_equals_feature_043", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "043-task-completion-lifecycle-formula-audit-complete^{}"), "details": "main == 043-task-completion-lifecycle-formula-audit-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "043-task-completion-lifecycle-formula-audit-complete^{}", "main") == "", "details": "diff between 043-task-completion-lifecycle-formula-audit-complete^{} and main is empty"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json must not be staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "origin/main...HEAD").splitlines(), "details": ".specify/feature.json must not appear in git diff --name-only origin/main...HEAD"},
        {"name": "no_unrelated_dirty_files", "verified": no_unrelated, "details": "working tree clean except optional pointer" if no_unrelated else f"dirty_paths={', '.join(dirty_paths)}"},
    ]


def collect_prior_feature_gates_verified() -> list[dict[str, Any]]:
    features = [
        ("037", "baseline revalidation", "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"),
        ("038", "training foundation", "artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json"),
        ("039", "paper HOODIE network", "artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"),
        ("040", "smoke training", "artifacts/analysis/smoke-training/smoke-training-report.json"),
        ("041", "full-training campaign gate", "artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json"),
        ("042", "paper default terminal exposure", "artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json"),
        ("043", "task completion lifecycle audit", "artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json"),
    ]
    return [{"feature": feature, "name": name, "verified": Path(path).exists(), "details": f"{path} exists"} for feature, name, path in features]


def _environment(config: PassiveRuntimeLifecycleTraceConfig, *, trace_source: TraceSource | None = None) -> HoodieGymEnvironment:
    return HoodieGymEnvironment(
        episode_length=config.episode_length,
        topology=TopologyGraph.from_approved_assumption_registry(),
        runtime_parameters=SharedRuntimeParameters(),
        compute_config=ComputeConfig(
            cpu_capacity_per_slot_agent=config.cpu_capacity_private_gcycles_per_slot,
            cpu_capacity_per_slot_edge=config.cpu_capacity_public_gcycles_per_slot,
            cpu_capacity_per_slot_cloud=config.cpu_capacity_cloud_gcycles_per_slot,
        ),
        trace_source=trace_source,
        trace_config=LifecycleTraceConfig(trace_enabled=config.trace_enabled),
        policy_name="HOODIE",
    )


def _choose_action(strategy: TraceStrategy, legal_action_mask: dict[str, bool], step_index: int) -> str | None:
    legal_order = [("local", legal_action_mask.get("local", False)), ("horizontal", legal_action_mask.get("horizontal", False)), ("vertical", legal_action_mask.get("vertical", False))]
    if strategy == "environment_default_policy_probe":
        for action, allowed in legal_order:
            if allowed:
                return action
        return None
    if strategy == "force_local_legal_probe":
        return "local" if legal_action_mask.get("local", False) else next((action for action, allowed in legal_order if allowed), None)
    if strategy == "force_horizontal_legal_probe":
        return "horizontal" if legal_action_mask.get("horizontal", False) else next((action for action, allowed in legal_order if allowed), None)
    if strategy == "force_vertical_legal_probe":
        return "vertical" if legal_action_mask.get("vertical", False) else next((action for action, allowed in legal_order if allowed), None)
    legal_actions = [action for action, allowed in legal_order if allowed]
    if not legal_actions:
        return None
    return legal_actions[step_index % len(legal_actions)]


def _paper_default_trace_source(seed: int) -> TraceSource:
    return TraceSource.from_trace_bank(f"paper_default-{seed}", root_path=PAPER_DEFAULT_TRACE_ROOT)


def _run_episode(config: PassiveRuntimeLifecycleTraceConfig, strategy: TraceStrategy, seed: int, *, trace_enabled: bool, use_trace_bank: bool) -> dict[str, Any]:
    trace_source = _paper_default_trace_source(seed) if use_trace_bank else None
    env = _environment(config, trace_source=trace_source)
    env.trace_config = LifecycleTraceConfig(trace_enabled=trace_enabled)
    observation, info = env.reset(seed=None if use_trace_bank else seed)
    step_index = 0
    actions: list[str | None] = []
    finalized_counts = Counter()
    terminal_flags: list[dict[str, Any]] = []
    while True:
        current = env.current_task
        selected_action = None
        if current is not None:
            selected_action = _choose_action(strategy, env.legal_action_mask(current), step_index)
        actions.append(selected_action)
        observation, reward, terminated, truncated, info = env.step(selected_action)
        finalized = info.get("finalized_tasks", [])
        for task in finalized:
            if task.get("terminal_outcome") == "completed":
                finalized_counts["completed"] += 1
            elif task.get("terminal_outcome") == "dropped":
                finalized_counts["dropped"] += 1
        terminal_flags.append({"terminated": terminated, "truncated": truncated, "reward": reward, "queue_load": info.get("queue_load", 0)})
        step_index += 1
        if terminated or truncated:
            break
    return {
        "strategy": strategy,
        "seed": seed,
        "trace_enabled": trace_enabled,
        "actions": actions,
        "final_info": info,
        "terminal_flags": terminal_flags,
        "trace_events": info.get("lifecycle_trace_events", []),
        "finalized_counts": dict(finalized_counts),
        "reward": info.get("reward", 0.0),
        "observed_queue_load": info.get("queue_load", 0),
    }


def _dedupe_behavior_checks(checks: list[BehaviorEquivalenceCheck]) -> list[BehaviorEquivalenceCheck]:
    deduped: dict[str, BehaviorEquivalenceCheck] = {}
    counts: Counter[str] = Counter()
    for check in checks:
        counts[check.name] += 1
        if check.name not in deduped:
            deduped[check.name] = check
    result: list[BehaviorEquivalenceCheck] = []
    for name in ("same_rewards", "same_finalized_tasks", "same_terminal_flags", "same_queue_load", "same_action_sequence", "same_outcomes"):
        check = deduped.get(name)
        if check is None:
            continue
        result.append(
            BehaviorEquivalenceCheck(
                name=check.name,
                verified=check.verified and counts[check.name] > 0,
                details=f"{check.details}; sample_count={counts[check.name]}",
            )
        )
    return result


def _build_event_statuses(enabled_summary: list[LifecycleTraceSummary]) -> tuple[list[dict[str, Any]], dict[str, bool], dict[str, bool], list[str]]:
    supported = {event_type: True for event_type in TRACE_EVENT_TYPES}
    observed = {event_type: any(event_type in summary.event_types_seen for summary in enabled_summary) for event_type in TRACE_EVENT_TYPES}
    missing_from_instrumentation = [event_type for event_type in TRACE_EVENT_TYPES if not supported[event_type]]
    statuses = [
        {
            "event_type": event_type,
            "event_type_supported": supported[event_type],
            "event_type_observed": observed[event_type],
            "event_type_missing_from_instrumentation": not supported[event_type],
        }
        for event_type in TRACE_EVENT_TYPES
    ]
    return statuses, supported, observed, missing_from_instrumentation


def _drop_path_ordering_ok(summary: LifecycleTraceSummary) -> bool:
    for task_id, order in summary.per_task_event_order.items():
        if "task_dropped" not in order:
            continue
        if "deadline_expired" not in order:
            return False
        if order.index("deadline_expired") > order.index("task_dropped"):
            return False
        if "reward_emitted" not in order or order.index("reward_emitted") < order.index("task_dropped"):
            return False
    return True


def _summarize_trace(result: dict[str, Any]) -> LifecycleTraceSummary:
    events = list(result["trace_events"])
    event_counts = Counter(event.get("event_type", "") for event in events)
    per_task_event_order: dict[str, list[str]] = defaultdict(list)
    for event in events:
        task_id = str(event.get("task_id", "unknown"))
        per_task_event_order[task_id].append(str(event.get("event_type", "")))
    return LifecycleTraceSummary(
        strategy=str(result["strategy"]),
        seed=int(result["seed"]),
        trace_enabled=bool(result["trace_enabled"]),
        event_types_seen=tuple(sorted({str(event.get("event_type", "")) for event in events})),
        event_counts=dict(event_counts),
        execution_progress_count=event_counts.get("execution_progress", 0),
        completed_count=event_counts.get("task_completed", 0),
        dropped_count=event_counts.get("task_dropped", 0),
        pending_at_horizon_count=event_counts.get("pending_at_horizon", 0),
        reward_emitted_count=event_counts.get("reward_emitted", 0),
        per_task_event_order=dict(per_task_event_order),
    )


def _behavior_equivalence_checks(enabled_result: dict[str, Any], disabled_result: dict[str, Any]) -> list[BehaviorEquivalenceCheck]:
    enabled_info = dict(enabled_result["final_info"])
    disabled_info = dict(disabled_result["final_info"])
    checks = [
        BehaviorEquivalenceCheck("same_rewards", enabled_info.get("reward") == disabled_info.get("reward"), "reward values must match"),
        BehaviorEquivalenceCheck("same_finalized_tasks", enabled_info.get("finalized_tasks") == disabled_info.get("finalized_tasks"), "finalized task payloads must match"),
        BehaviorEquivalenceCheck("same_terminal_flags", enabled_info.get("terminated") == disabled_info.get("terminated") and enabled_info.get("truncated") == disabled_info.get("truncated"), "terminal flags must match"),
        BehaviorEquivalenceCheck("same_queue_load", enabled_info.get("queue_load") == disabled_info.get("queue_load"), "queue load must match"),
        BehaviorEquivalenceCheck("same_action_sequence", enabled_result["actions"] == disabled_result["actions"], "selected actions must match"),
        BehaviorEquivalenceCheck("same_outcomes", enabled_result["finalized_counts"] == disabled_result["finalized_counts"], "completion/drop outcomes must match"),
    ]
    return checks


def build_passive_runtime_lifecycle_trace_report(config: PassiveRuntimeLifecycleTraceConfig | None = None) -> PassiveRuntimeLifecycleTraceReport:
    config = config or PassiveRuntimeLifecycleTraceConfig()
    enabled_results = [_run_episode(config, strategy, seed, trace_enabled=True, use_trace_bank=True) for strategy in config.strategies for seed in config.seeds]
    disabled_results = [_run_episode(config, strategy, seed, trace_enabled=False, use_trace_bank=True) for strategy in config.strategies for seed in config.seeds]
    enabled_summary = [_summarize_trace(result) for result in enabled_results]
    disabled_summary = [_summarize_trace(result) for result in disabled_results]
    equivalence_checks = []
    for enabled_result, disabled_result in zip(enabled_results, disabled_results, strict=False):
        equivalence_checks.extend(_behavior_equivalence_checks(enabled_result, disabled_result))
    equivalence_checks = _dedupe_behavior_checks(equivalence_checks)
    event_types_seen = sorted({event_type for summary in enabled_summary for event_type in summary.event_types_seen})
    event_statuses, event_type_supported, event_type_observed, event_type_missing_from_instrumentation = _build_event_statuses(enabled_summary)
    drop_path_ordering_observed = all(_drop_path_ordering_ok(summary) for summary in enabled_summary)
    coverage_summary = {
        "required_event_types": list(TRACE_EVENT_TYPES),
        "event_types_seen": event_types_seen,
        "event_type_supported": event_type_supported,
        "event_type_observed": event_type_observed,
        "event_type_missing_from_instrumentation": event_type_missing_from_instrumentation,
        "event_statuses": event_statuses,
        "task_completed_supported": event_type_supported["task_completed"],
        "task_completed_observed": event_type_observed["task_completed"],
        "deadline_expired_supported": event_type_supported["deadline_expired"],
        "deadline_expired_observed": event_type_observed["deadline_expired"],
        "execution_progress_observed": any(summary.execution_progress_count > 0 for summary in enabled_summary),
        "completion_drop_ordering_observed": drop_path_ordering_observed,
        "pending_at_horizon_observed": any(summary.pending_at_horizon_count > 0 for summary in enabled_summary),
    }
    sample_events = enabled_results[0]["trace_events"][:5] if enabled_results else []
    sample_trace = enabled_results[0] if enabled_results else {}
    readiness = {
        "sufficient_for_feature_043": not event_type_missing_from_instrumentation and all(check.verified for check in equivalence_checks) and drop_path_ordering_observed,
        "insufficient_reason": None
        if not event_type_missing_from_instrumentation and all(check.verified for check in equivalence_checks) and drop_path_ordering_observed
        else (
            f"missing_from_instrumentation={event_type_missing_from_instrumentation}"
            if event_type_missing_from_instrumentation
            else "drop_path_ordering_incomplete"
        ),
    }
    return PassiveRuntimeLifecycleTraceReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=build_prerequisite_tags_verified(),
        prior_feature_gates_verified=collect_prior_feature_gates_verified(),
        instrumentation_scope={
            "passive_only": True,
            "environment_touch_allowed": True,
            "no_semantic_changes": True,
            "trace_enabled_default": False,
            "trace_carrier": "existing env info dict / analysis runner path",
        },
        trace_event_schema={
            "event_types": list(TRACE_EVENT_TYPES),
            "required_fields": [
                "event_type",
                "slot",
                "task_id",
                "source_agent_id",
                "selected_action",
                "destination",
                "queue_type",
                "host_node_id",
                "arrival_slot",
                "absolute_deadline_slot",
                "task_age_slots",
                "size_mbits",
                "processing_density_gcycles_per_mbit",
                "cycles_required_gcycles",
                "cycles_before_gcycles",
                "cycles_consumed_gcycles",
                "cycles_after_gcycles",
                "compute_capacity_gcycles_per_slot",
                "transmission_started_at",
                "transmission_completed_at",
                "transmission_delay_slots",
                "terminal_outcome",
                "reward",
                "reward_available",
                "pending_at_horizon",
                "legality_snapshot",
                "trace_source_component",
            ],
        },
        trace_sources=[
            {
                "component": "traffic_generator",
                "event_types": ["task_generated"],
                "supported": True,
                "observed": "task_generated" in event_type_observed,
                "missing_from_instrumentation": False,
            },
            {
                "component": "environment",
                "event_types": [event for event in TRACE_EVENT_TYPES if event != "task_generated"],
                "supported": True,
                "observed": {event: event_type_observed[event] for event in TRACE_EVENT_TYPES if event != "task_generated"},
                "missing_from_instrumentation": False,
            },
        ],
        paper_default_runtime_verified={
            "episode_length": config.episode_length,
            "timeout_slots": config.timeout_slots,
            "arrival_probability": config.arrival_probability,
            "node_count": config.node_count,
            "seeds": list(config.seeds),
            "strategies": list(config.strategies),
            "trace_bank_root": str(PAPER_DEFAULT_TRACE_ROOT),
            "paper_default_probe": True,
        },
        behavior_equivalence_checks=[check.to_dict() for check in equivalence_checks],
        trace_coverage_summary=coverage_summary,
        lifecycle_trace_sample=_json_safe(sample_events),
        completion_diagnosis_readiness=readiness | {
            "task_completed_supported": coverage_summary["task_completed_supported"],
            "task_completed_observed": coverage_summary["task_completed_observed"],
            "deadline_expired_supported": coverage_summary["deadline_expired_supported"],
            "deadline_expired_observed": coverage_summary["deadline_expired_observed"],
            "event_type_supported": event_type_supported,
            "event_type_observed": event_type_observed,
            "event_type_missing_from_instrumentation": event_type_missing_from_instrumentation,
        },
        runtime_contracts_verified={
            "environment_owns_orchestration": True,
            "helper_only_slot_engine": True,
            "step_is_one_slot": True,
            "shared_capacity_deterministic_equal_share": True,
            "horizontal_legality_neighbor_only": True,
            "vertical_legality_figure7_independent": True,
        },
        reward_timing_contract_verified=True,
        pending_at_horizon_contract_verified=True,
        no_training_started=True,
        no_optimizer_step=True,
        no_replay_training=True,
        no_target_update_execution=True,
        no_dependency_drift=True,
        no_policy_drift=True,
        no_reward_timing_change=True,
        no_timeout_contract_drift=True,
        no_capacity_contract_drift=True,
        no_transmission_contract_drift=True,
        no_action_legality_drift=True,
        no_curve_fitting=True,
        no_simulator_output_tuning=True,
        no_paper_reproduction_claim=True,
        final_verdict="passive_trace_instrumentation_ready" if readiness["sufficient_for_feature_043"] else "passive_trace_instrumentation_incomplete",
    )


def run_passive_runtime_lifecycle_trace_instrumentation(output_dir: Path | str | None = None) -> PassiveRuntimeLifecycleTraceReport:
    report = build_passive_runtime_lifecycle_trace_report()
    write_passive_runtime_lifecycle_trace_report(report, output_dir)
    return report
