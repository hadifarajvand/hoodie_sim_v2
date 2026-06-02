from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import json
from typing import Any

from .action_model import HybridActionDecision
from .communication_model import EdgeControllerBroker, PubSubRecoveryMetadata
from .config import (
    DEFAULT_CHANGED_FILES,
    DEFAULT_OUTPUT_DIR,
    BLOCKED_STATUS,
    FEATURE_ID,
    FEATURE_NAME,
    READY_STATUS,
    REQUIRED_COMPONENT_IDS,
    TARGET_METHOD_ID,
    validate_scope,
)
from .formulas import build_formula_registry, compute_private_cost, compute_public_cost, compute_reward
from .learning_model import (
    DQNInterface,
    DistributedEdgeAgentDecisionModel,
    DoubleDQNTargetRule,
    DuelingDQNInterface,
    EpsilonGreedyTrainingSchedule,
    InferenceMode,
    LSTMForecastRecoveryInterface,
    ReplayMemoryInterface,
)
from .model import ComponentCoverageEntry, HoodieProposedMethodReport
from .queue_model import OffloadingQueueTiming, PrivateQueueTiming, PublicQueueTiming
from .reward_model import private_cost, public_cost, reward_from_task_outcome


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _claim_boundary() -> tuple[str, ...]:
    return (
        "HOODIE_PROPOSED means the base-paper proposed method only.",
        "No ranking is performed.",
        "No baseline evaluation is performed.",
        "No thesis/DCQ extension is introduced.",
        "Partial neural interfaces are reported honestly instead of being inflated into full trainable models.",
    )


def _component_definitions() -> tuple[ComponentCoverageEntry, ...]:
    return (
        ComponentCoverageEntry(
            component_id="hybrid_action_model",
            component_name="Hybrid local/horizontal/vertical action model",
            paper_requirement="a_n(t) = [d_n^(1)(t), D_n(t)]",
            current_implementation="Action decisions are represented as a paper-vector helper and align with the existing local/horizontal/vertical action family used across the simulator.",
            implementation_reference="src/analysis/hoodie_proposed_method/action_model.py; src/environment/task.py; src/policies/common.py",
            status="implemented",
            gap="none",
            required_repair="No repair required for the paper action vector contract.",
        ),
        ComponentCoverageEntry(
            component_id="private_queue_timing",
            component_name="Private queue timing",
            paper_requirement="FIFO private queue with waiting-time based on previous maximum completion slot and timeout-limited completion",
            current_implementation="The environment already tracks private FIFO queue state and exposes waiting-time semantics that can be wrapped directly by the proposed-method package.",
            implementation_reference="src/environment/private_queue.py; src/analysis/hoodie_proposed_method/queue_model.py",
            status="implemented",
            gap="none",
            required_repair="No repair required for the private queue timing contract.",
        ),
        ComponentCoverageEntry(
            component_id="offloading_queue_timing",
            component_name="Offloading queue timing",
            paper_requirement="FIFO offloading queue with horizontal and vertical transmission rates and timeout-limited completion",
            current_implementation="The environment already models an offloading queue and the proposed-method package exposes an explicit completion-slot wrapper.",
            implementation_reference="src/environment/offloading_queue.py; src/analysis/hoodie_proposed_method/queue_model.py",
            status="implemented",
            gap="none",
            required_repair="No repair required for the offloading queue timing contract.",
        ),
        ComponentCoverageEntry(
            component_id="public_queue_timing",
            component_name="Public queue timing",
            paper_requirement="Public queues at edge agents and cloud destinations with FIFO semantics",
            current_implementation="The environment public queue primitive already exists and the proposed-method package exposes public queue timing as a dedicated wrapper.",
            implementation_reference="src/environment/public_queue.py; src/analysis/hoodie_proposed_method/queue_model.py",
            status="implemented",
            gap="none",
            required_repair="No repair required for the public queue timing contract.",
        ),
        ComponentCoverageEntry(
            component_id="reward_cost_model",
            component_name="Reward/cost model",
            paper_requirement="No task => omitted, success => -Phi_n(t), drop => -C",
            current_implementation="The reward timing helpers already encode the paper reward equations and the proposed-method package exposes explicit reward conversion helpers.",
            implementation_reference="src/environment/reward_timing.py; src/analysis/hoodie_proposed_method/reward_model.py",
            status="implemented",
            gap="none",
            required_repair="No repair required for the paper reward mapping.",
        ),
        ComponentCoverageEntry(
            component_id="distributed_edge_agent_decision_model",
            component_name="Distributed edge-agent decision model",
            paper_requirement="Distributed DRL agents at edge servers",
            current_implementation="The repository has a real agent/policy stack, but the proposed-method package only models the distributed decision flow and does not claim a full trainable simulation stack.",
            implementation_reference="src/agents/hoodie_agent.py; src/agents/hoodie_model.py; src/analysis/hoodie_proposed_method/learning_model.py",
            status="partial",
            gap="interface_only_decision_model",
            required_repair="Integrate the decision model with a full training/runtime loop if full distributed execution is required.",
        ),
        ComponentCoverageEntry(
            component_id="dqn_interface",
            component_name="DQN interface",
            paper_requirement="Q-network interface for value estimation",
            current_implementation="The repository exposes Q-value interfaces, but not a trainable DQN implementation wired into Feature 080.",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py; src/agents/hoodie_model.py",
            status="partial",
            gap="interface_only_q_learning",
            required_repair="Add a trainable DQN module if the paper interface must be executed end-to-end.",
        ),
        ComponentCoverageEntry(
            component_id="double_dqn_target_rule",
            component_name="Double DQN target rule",
            paper_requirement="Online action selection with target-network evaluation",
            current_implementation="A deterministic Double-DQN target rule exists as an interface, but not as a full training algorithm.",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py; src/agents/double_dqn.py",
            status="partial",
            gap="interface_only_double_dqn",
            required_repair="Connect the rule to a full replay/training loop if training is required.",
        ),
        ComponentCoverageEntry(
            component_id="dueling_dqn_value_advantage_interface",
            component_name="Dueling DQN value/advantage interface",
            paper_requirement="Value stream plus advantage stream",
            current_implementation="The repository exposes a dueling-style Q decomposition, but it remains a lightweight interface rather than a full neural training module.",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py; src/agents/dueling_dqn.py; src/analysis/paper_hoodie_network_implementation/report.py",
            status="partial",
            gap="interface_only_dueling_dqn",
            required_repair="Replace the interface with a trainable network if full dueling training is required.",
        ),
        ComponentCoverageEntry(
            component_id="lstm_forecast_recovery_interface",
            component_name="LSTM forecast/recovery interface",
            paper_requirement="Load forecast and delayed-message recovery via LSTM",
            current_implementation="Forecast and recovery helpers exist, but the repository does not provide a full trainable LSTM runtime in Feature 080.",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py; src/environment/paper_lstm_forecast.py",
            status="partial",
            gap="interface_only_lstm",
            required_repair="Add a trainable LSTM component and feed it with paper-history features if required.",
        ),
        ComponentCoverageEntry(
            component_id="replay_memory_interface",
            component_name="Replay memory interface",
            paper_requirement="Experience tuple storage and batch sampling",
            current_implementation="Replay storage exists, and the proposed-method package provides explicit batch-sampling semantics, but it is still an interface-level representation rather than the full trainer path.",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py; src/agents/replay_buffer.py",
            status="partial",
            gap="interface_only_replay_memory",
            required_repair="Wire replay sampling into a full update loop if training is required.",
        ),
        ComponentCoverageEntry(
            component_id="epsilon_greedy_training_schedule",
            component_name="Epsilon-greedy training schedule",
            paper_requirement="Epsilon starts at 1 and decays to 0 in the first half of episodes",
            current_implementation="The package exposes the paper-shaped schedule, but the repo-wide training stack still uses other readiness-oriented schedules elsewhere.",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py; src/analysis/distributed_multi_agent_hoodie_training/schedule.py",
            status="partial",
            gap="schedule_not_globally_wired",
            required_repair="Route the paper schedule into the training loop if paper-faithful training is required.",
        ),
        ComponentCoverageEntry(
            component_id="inference_mode_epsilon_zero",
            component_name="Inference mode with epsilon = 0",
            paper_requirement="Deployment uses greedy Q-model inference",
            current_implementation="The package provides an explicit epsilon-zero inference mode helper.",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="implemented",
            gap="none",
            required_repair="No repair required for the inference-mode epsilon contract.",
        ),
        ComponentCoverageEntry(
            component_id="pubsub_recovery_metadata",
            component_name="Pub-Sub recovery metadata",
            paper_requirement="Edge controllers as brokers and delayed/stale message recovery metadata",
            current_implementation="The package exposes broker and recovery metadata structures that track delayed and stale messages across agents.",
            implementation_reference="src/analysis/hoodie_proposed_method/communication_model.py",
            status="implemented",
            gap="none",
            required_repair="No repair required for the pub-sub recovery metadata contract.",
        ),
    )


def _remaining_gaps(component_coverage: Sequence[ComponentCoverageEntry]) -> tuple[str, ...]:
    gaps: list[str] = []
    for component in component_coverage:
        if component.status != "implemented":
            gaps.append(f"{component.component_id}: {component.gap}")
    return tuple(gaps)


def _readiness_level(component_coverage: Sequence[ComponentCoverageEntry]) -> str:
    implemented = sum(1 for component in component_coverage if component.status == "implemented")
    partial = sum(1 for component in component_coverage if component.status == "partial")
    missing = sum(1 for component in component_coverage if component.status == "missing")
    if missing > 0:
        return "blocked" if implemented == 0 else "partial"
    if partial == 0:
        return "fully_implemented"
    if implemented >= partial:
        return "mostly_implemented"
    return "partial"


def build_feature_080_report(changed_files: Sequence[str] | None = None) -> HoodieProposedMethodReport:
    component_coverage = _component_definitions()
    component_ids = {component.component_id for component in component_coverage}
    if component_ids != set(REQUIRED_COMPONENT_IDS):
        raise ValueError("component coverage must match the required Feature 080 component list")
    formula_registry = build_formula_registry()
    readiness_level = _readiness_level(component_coverage)
    passed = readiness_level == "fully_implemented"
    report = HoodieProposedMethodReport(
        feature_id=FEATURE_ID,
        status=READY_STATUS if passed else BLOCKED_STATUS,
        passed=passed,
        component_count=len(component_coverage),
        implemented_count=sum(1 for component in component_coverage if component.status == "implemented"),
        partial_count=sum(1 for component in component_coverage if component.status == "partial"),
        missing_count=sum(1 for component in component_coverage if component.status == "missing"),
        formula_registry=formula_registry,
        component_coverage=component_coverage,
        remaining_gaps=_remaining_gaps(component_coverage),
        readiness_level=readiness_level,
        claim_boundary=_claim_boundary(),
        scope_evidence=tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files)),
    )
    return report


def render_feature_080_report(report: HoodieProposedMethodReport) -> str:
    payload = report.to_dict()
    component_lines = []
    for component in payload["component_coverage"]:
        component_lines.append(
            "\n".join(
                [
                    f"### {component['component_id']}",
                    _json_dump(component).rstrip(),
                ]
            )
        )
    formula_lines = []
    for formula in payload["formula_registry"]:
        formula_lines.append(
            "\n".join(
                [
                    f"### {formula['formula_id']}",
                    _json_dump(formula).rstrip(),
                ]
            )
        )
    return "\n".join(
        [
            "# Feature 080 HOODIE Proposed Method Implementation Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- component_count: `{payload['component_count']}`",
            f"- implemented_count: `{payload['implemented_count']}`",
            f"- partial_count: `{payload['partial_count']}`",
            f"- missing_count: `{payload['missing_count']}`",
            f"- readiness_level: `{payload['readiness_level']}`",
            "",
            "## Claim Boundary",
            *[f"- {item}" for item in payload["claim_boundary"]],
            "",
            "## Scope Evidence",
            *[f"- {item}" for item in payload["scope_evidence"]],
            "",
            "## Formula Registry",
            *formula_lines,
            "",
            "## Component Coverage",
            *component_lines,
            "",
            "## Remaining Gaps",
            *[f"- {item}" for item in payload["remaining_gaps"]],
            "",
        ]
    )


def write_feature_080_report(output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_feature_080_report()
    markdown_path = output_path / "feature-080-hoodie-proposed-method-report.md"
    json_path = output_path / "feature-080-hoodie-proposed-method-report.json"
    markdown_path.write_text(render_feature_080_report(report), encoding="utf-8")
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    return markdown_path
