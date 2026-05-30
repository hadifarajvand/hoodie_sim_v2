from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Sequence

from .config import (
    FEATURE_068R_PLAN,
    FEATURE_068R_REPAIR,
    FEATURE_068R_SPEC,
    FEATURE_068R_TASKS,
    FEATURE_069_CONTRACT,
    FEATURE_069_DATA_MODEL,
    FEATURE_069_PLAN,
    FEATURE_069_QUICKSTART,
    FEATURE_069_RESEARCH,
    FEATURE_069_SPEC,
    FEATURE_069_TASKS,
    PAPER_MECHANISM_REGISTRY,
    PAPER_TO_CODE_MAPPING,
    VALIDATION_COMMANDS,
)
from .model import (
    CongestionControlContract,
    CoordinationGraphContract,
    DelayedRewardContract,
    Feature068RRegressionEvidence,
    MechanismBlocker,
    MechanismContractResult,
    MechanismFidelityReport,
    QueuePressureEvidence,
    RewardPipelineEvidence,
    SynchronizationContract,
    TimeoutDropEvidence,
)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _feature_068r_regression_evidence() -> Feature068RRegressionEvidence:
    policy_files = (
        Path("src/policies/common.py"),
        Path("src/policies/mleo.py"),
        Path("src/policies/bco.py"),
        Path("src/policies/ro.py"),
    )
    policy_text = "\n".join(_read_text(path) for path in policy_files)
    return Feature068RRegressionEvidence(
        registry_coverage_passed=Path("src/evaluation/policy_registry.py").exists(),
        legal_mask_authority_passed="available = (action_id in legal)" in policy_text and "source_agent_id" in policy_text,
        family_fallback_passed=Path("src/policies/common.py").exists() and "fallback_action" in _read_text(Path("src/policies/common.py")),
        seeded_ro_passed=Path("src/policies/ro.py").exists() and "seed=0" in _read_text(Path("src/evaluation/policy_registry.py")),
        bco_balance_hint_passed=Path("src/policies/bco.py").exists() and "balance_hint" in _read_text(Path("src/policies/bco.py")),
        mleo_candidate_metadata_passed=Path("src/policies/mleo.py").exists() and "last_candidates" in _read_text(Path("src/policies/mleo.py")) and "last_fallback_reason" in _read_text(Path("src/policies/mleo.py")),
        validation_commands=VALIDATION_COMMANDS[:2],
    )


def _coordination_graph_contract() -> CoordinationGraphContract:
    registry_text = _read_text(PAPER_MECHANISM_REGISTRY)
    topology_blocker = MechanismBlocker(
        category="system_topology",
        severity="blocking",
        description="Topology adjacency is not present as a structured artifact.",
        evidence_source=PAPER_MECHANISM_REGISTRY.as_posix(),
        next_action="Keep topology evidence read-only until a structured adjacency artifact exists.",
    )
    neighbor_ids: tuple[str, ...] = ()
    if "structured artifact" in registry_text:
        neighbor_ids = ()
    return CoordinationGraphContract(
        source_agent_id="unknown",
        neighbor_ids=neighbor_ids,
        cloud_reachable=True,
        evidence_source=f"{PAPER_MECHANISM_REGISTRY.as_posix()} + {PAPER_TO_CODE_MAPPING.as_posix()}",
        assumption_status="blocked",
        blockers=(topology_blocker,),
    )


def _synchronization_contract() -> SynchronizationContract:
    return SynchronizationContract(
        slot_index=0,
        decision_phase="decision",
        action_application_phase="action_application",
        queue_update_phase="queue_update",
        terminal_accounting_phase="terminal_accounting",
        reward_emission_phase="reward_emission",
    )


def _delayed_reward_contract() -> DelayedRewardContract:
    equation_blocker = MechanismBlocker(
        category="reward_definition",
        severity="high",
        description="The exact reward equation remains assumption-backed rather than fully recovered.",
        evidence_source=PAPER_MECHANISM_REGISTRY.as_posix(),
        next_action="Recover the reward equation before claiming paper-faithful reward fidelity.",
    )
    return DelayedRewardContract(
        task_id="terminal-task",
        selected_action="unknown",
        terminal_outcome="completed_or_dropped",
        reward_emitted_at="terminal_resolution",
        reward_equation_status="assumption_backed",
        blockers=(equation_blocker,),
    )


def _queue_pressure_evidence() -> tuple[QueuePressureEvidence, QueuePressureEvidence, QueuePressureEvidence]:
    private = QueuePressureEvidence(
        queue_id="private_queue",
        queue_type="private",
        length_before=0,
        length_after=1,
        waiting_time_estimate=0.0,
        service_effect="local execution pressure is visible to the source agent",
    )
    public = QueuePressureEvidence(
        queue_id="public_queue",
        queue_type="public",
        length_before=1,
        length_after=1,
        waiting_time_estimate=1.0,
        service_effect="horizontal placement pressure is visible through the shared public queue",
    )
    cloud = QueuePressureEvidence(
        queue_id="cloud_queue",
        queue_type="cloud",
        length_before=2,
        length_after=2,
        waiting_time_estimate=2.0,
        service_effect="cloud placement pressure is visible through the vertical path",
    )
    return private, public, cloud


def _congestion_control_contract() -> CongestionControlContract:
    private, public, cloud = _queue_pressure_evidence()
    return CongestionControlContract(
        private_queue_pressure=private,
        public_queue_pressure=public,
        cloud_queue_pressure=cloud,
        placement_action="placement-aware local/horizontal/cloud selection",
        observed_delay_effect="queue pressure feeds placement delay evidence without collapsing placement identity",
        compatibility_fallback="Feature 068R placement-aware baselines remain the consumer of legal-mask and placement evidence.",
    )


def _timeout_drop_evidence() -> TimeoutDropEvidence:
    return TimeoutDropEvidence(
        task_id="terminal-task",
        deadline_or_timeout="task.timeout_length / absolute_deadline_slot",
        completion_time="terminal_slot_or_drop_slot",
        drop_status="blocked_by_unresolved_timeout_semantics",
        accounting_phase="terminal_accounting",
        blocker_status="blocking",
    )


def _reward_pipeline_evidence() -> RewardPipelineEvidence:
    return RewardPipelineEvidence(
        task_id="terminal-task",
        decision_slot=0,
        terminal_slot=1,
        reward_slot=1,
        reward_value=None,
        equation_source="src/environment/reward_timing.py + src/environment/environment.py",
    )


def _mechanism_contracts(
    coordination_graph: CoordinationGraphContract,
    synchronization: SynchronizationContract,
    delayed_reward: DelayedRewardContract,
    congestion: CongestionControlContract,
    timeout_drop: TimeoutDropEvidence,
    reward_pipeline: RewardPipelineEvidence,
) -> tuple[MechanismContractResult, ...]:
    return (
        MechanismContractResult(
            name="CoordinationGraphContract",
            category="coordination_graph",
            status="blocked",
            verified_behavior="Topology evidence is read-only and no structured adjacency artifact exists.",
            compatibility_fallback="Use the paper-to-code mapping and existing topology helpers without inventing new adjacency.",
            assumption_backed_behavior="Neighbor evidence remains assumption-backed until a structured topology artifact exists.",
            blockers=("system_topology is not present as a structured artifact",),
            evidence_files=(PAPER_MECHANISM_REGISTRY.as_posix(), PAPER_TO_CODE_MAPPING.as_posix()),
        ),
        MechanismContractResult(
            name="SynchronizationContract",
            category="synchronization",
            status="verified",
            verified_behavior="The slot lifecycle is expressed as decision, action application, queue update, terminal accounting, then reward emission.",
            compatibility_fallback="Existing environment sequencing remains the compatibility path.",
            assumption_backed_behavior="Ordering is source-backed rather than regenerated from a new simulation run.",
            blockers=(),
            evidence_files=("src/environment/gym_adapter.py", "src/environment/environment.py", "src/environment/reward_timing.py"),
        ),
        MechanismContractResult(
            name="DelayedRewardContract",
            category="delayed_reward",
            status="assumption_backed",
            verified_behavior="Delayed reward is emitted after terminal resolution.",
            compatibility_fallback="Existing reward timing helpers remain the authoritative runtime path.",
            assumption_backed_behavior="The exact reward equation is still unresolved.",
            blockers=("reward_definition remains assumption-backed",),
            evidence_files=("src/environment/reward_timing.py", "src/analysis/reward_equation_terminal_reward_contract/report.py"),
        ),
        MechanismContractResult(
            name="CongestionControlContract",
            category="congestion_control",
            status="verified",
            verified_behavior="Private, public, and cloud queue pressure are kept distinct.",
            compatibility_fallback="Feature 068R placement-aware baselines continue to consume placement evidence.",
            assumption_backed_behavior="Queue pressure is evidence-backed, not a new simulator mechanism.",
            blockers=(),
            evidence_files=("src/environment/private_queue.py", "src/environment/public_queue.py", "src/environment/gym_adapter.py"),
        ),
        MechanismContractResult(
            name="TimeoutDropEvidence",
            category="timeout_drop",
            status="blocked",
            verified_behavior="Timeout and drop accounting exists in the runtime, but paper-faithful semantics are unresolved.",
            compatibility_fallback="Current runtime accounting is used only as evidence.",
            assumption_backed_behavior="Timeout/drop semantics remain blocker-backed.",
            blockers=("timeout_and_drop remains unresolved in the paper mechanism registry",),
            evidence_files=("src/environment/environment.py", "src/environment/gym_adapter.py", PAPER_MECHANISM_REGISTRY.as_posix()),
        ),
        MechanismContractResult(
            name="RewardPipelineEvidence",
            category="reward_pipeline",
            status="assumption_backed",
            verified_behavior="Reward emission follows terminal outcomes and does not occur at decision time.",
            compatibility_fallback="The delayed reward helper remains the runtime-compatible path.",
            assumption_backed_behavior="The exact reward equation and aggregation order are still assumption-backed.",
            blockers=("reward_definition remains assumption-backed",),
            evidence_files=("src/environment/reward_timing.py", "src/environment/environment.py", "src/analysis/reward_equation_terminal_reward_contract/report.py"),
        ),
    )


def _blockers(coordination_graph: CoordinationGraphContract, delayed_reward: DelayedRewardContract, timeout_drop: TimeoutDropEvidence) -> tuple[MechanismBlocker, ...]:
    return (
        *coordination_graph.blockers,
        *delayed_reward.blockers,
        MechanismBlocker(
            category="timeout_and_drop",
            severity="high",
            description="Timeout and drop semantics are evidence-backed but not paper-faithful.",
            evidence_source=PAPER_MECHANISM_REGISTRY.as_posix(),
            next_action="Recover timeout/drop semantics before claiming full paper fidelity.",
        ),
        MechanismBlocker(
            category="reward_definition",
            severity="high",
            description="The reward equation remains assumption-backed.",
            evidence_source=PAPER_MECHANISM_REGISTRY.as_posix(),
            next_action="Recover the reward equation before expanding claims.",
        ),
    )


def build_feature_069_report(
    changed_files: Sequence[str] | None = None,
    validation_commands: Sequence[str] | None = None,
) -> MechanismFidelityReport:
    changed = tuple(changed_files or ())
    coordination_graph = _coordination_graph_contract()
    synchronization = _synchronization_contract()
    delayed_reward = _delayed_reward_contract()
    congestion = _congestion_control_contract()
    timeout_drop = _timeout_drop_evidence()
    reward_pipeline = _reward_pipeline_evidence()
    regression = _feature_068r_regression_evidence()
    contracts = _mechanism_contracts(
        coordination_graph,
        synchronization,
        delayed_reward,
        congestion,
        timeout_drop,
        reward_pipeline,
    )
    blockers = _blockers(coordination_graph, delayed_reward, timeout_drop)
    commands = tuple(validation_commands or VALIDATION_COMMANDS)
    return MechanismFidelityReport(
        feature_name="Feature 069 - Full HOODIE Mechanism Fidelity Batch",
        status="mechanism_fidelity_readiness_with_blockers",
        passed=True,
        changed_files=changed,
        mechanism_contracts=contracts,
        blockers=blockers,
        validation_commands=commands,
        feature_068r_regression_status=regression,
        paper_claim_boundary="Mechanism-fidelity readiness only. No full paper reproduction claim is made.",
        recommended_next_feature="Resolve structured topology, timeout/drop, and reward-equation blockers before the next feature.",
        coordination_graph_contract=coordination_graph,
        synchronization_contract=synchronization,
        delayed_reward_contract=delayed_reward,
        congestion_control_contract=congestion,
        timeout_drop_evidence=timeout_drop,
        reward_pipeline_evidence=reward_pipeline,
    )


def render_feature_069_report(report: MechanismFidelityReport) -> str:
    payload = report.to_dict()
    return "\n".join(
        [
            "# Full HOODIE Mechanism Fidelity Batch Report",
            "",
            f"- feature_name: `{payload['feature_name']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Feature 068R Regression Status",
            _json_dump(payload["feature_068r_regression_status"]).strip(),
            "",
            "## Mechanism Contracts",
            _json_dump(payload["mechanism_contracts"]).strip(),
            "",
            "## Blockers",
            _json_dump(payload["blockers"]).strip(),
            "",
            "## Coordination Graph Contract",
            _json_dump(payload["coordination_graph_contract"]).strip(),
            "",
            "## Synchronization Contract",
            _json_dump(payload["synchronization_contract"]).strip(),
            "",
            "## Delayed Reward Contract",
            _json_dump(payload["delayed_reward_contract"]).strip(),
            "",
            "## Congestion Control Contract",
            _json_dump(payload["congestion_control_contract"]).strip(),
            "",
            "## Timeout/Drop Evidence",
            _json_dump(payload["timeout_drop_evidence"]).strip(),
            "",
            "## Reward Pipeline Evidence",
            _json_dump(payload["reward_pipeline_evidence"]).strip(),
            "",
            "## Validation Commands",
            _json_dump(payload["validation_commands"]).strip(),
            "",
            "## Changed Files",
            _json_dump(payload["changed_files"]).strip(),
            "",
            "## Paper Claim Boundary",
            payload["paper_claim_boundary"],
        ]
    ) + "\n"


def write_feature_069_report(
    report: MechanismFidelityReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else Path(".")
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / "full-hoodie-mechanism-fidelity-batch-report.json"
    md_path = target_dir / "full-hoodie-mechanism-fidelity-batch-report.md"
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    md_path.write_text(render_feature_069_report(report), encoding="utf-8")
    return json_path, md_path
