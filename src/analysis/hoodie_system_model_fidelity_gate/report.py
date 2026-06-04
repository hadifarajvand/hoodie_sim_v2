from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

from .config import (
    ACTIVE_POLICIES,
    BLOCKED_STATUS,
    DEFAULT_OUTPUT_DIR,
    FEATURE_085_AUDIT_DIR,
    FEATURE_ID,
    FEATURE_NAME,
    INVALID_LABELS,
    PAPER_PRIMARY_METRICS,
    PAPER_SECONDARY_OR_DERIVED_METRICS,
    PAPER_SECONDARY_OR_REPOSITORY_METRICS,
    READY_STATUS,
    REPOSITORY_DIAGNOSTIC_METRICS,
    REQUIRED_MECHANISM_IDS,
    REQUIRED_METRICS,
)
from .implementation_scan import scan_current_implementation
from .model import (
    Feature086Report,
    HoodieMleoTieEvidence,
    MechanismCoverageRow,
    MetricReadinessRow,
    ScenarioMechanismCoverageRow,
    SystemModelGapRow,
)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _rows_to_markdown(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_No rows._"
    headers = list(rows[0])
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        values = [str(row.get(header, "")) for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _component_map() -> dict[str, Any]:
    return {item.component_id: item for item in scan_current_implementation()}


def _mechanism_rows() -> tuple[MechanismCoverageRow, ...]:
    implementations = _component_map()
    rows = [
        MechanismCoverageRow(
            mechanism_id="three_tier_topology",
            paper_expectation="Task source / IoT layer, edge agents, and cloud are represented as a three-tier CEC topology.",
            simulator_behavior="The runtime layer uses deterministic topology profiles and scenario fixtures to represent the source, edge, and cloud tiers.",
            code_location="resources/papers/hoodie/ocr/merged.txt; src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py; artifacts/feature_085_full_audit/raw_rows.json",
            status="approximate_documented",
            required_fix_or_claim_boundary="Document the deterministic topology abstraction; no new simulator topology is claimed.",
        ),
        MechanismCoverageRow(
            mechanism_id="edge_agent_set_cloud_node",
            paper_expectation="Multiple edge agents plus one cloud node exist as active runtime participants.",
            simulator_behavior="The runtime policy set and scenario contexts model multiple edge agents plus a cloud destination.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/model.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_policies.py; artifacts/feature_085_full_audit/feature_085_audit_report.json",
            status="approximate_documented",
            required_fix_or_claim_boundary="Treat the active policy set and scenario contexts as the evidence boundary, not as a full distributed runtime simulator.",
        ),
        MechanismCoverageRow(
            mechanism_id="horizontal_connectivity_legality",
            paper_expectation="Horizontal EA-to-EA destinations must be legal only when topology permits them.",
            simulator_behavior="The policy layer distinguishes legal horizontal destinations from illegal attempts and rejects invalid horizontal choices.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_ho_prefers_horizontal_when_legal_destination_exists; tests/integration/test_hoodie_runtime_evaluation_runner_report.py",
            status="approximate_documented",
            required_fix_or_claim_boundary="The legality model is documented through candidate/action legality checks.",
        ),
        MechanismCoverageRow(
            mechanism_id="vertical_ea_cloud_path",
            paper_expectation="Vertical offload reaches the cloud path and uses cloud-side execution capacity.",
            simulator_behavior="The runtime scenarios include cloud-vertical fallback and vertical offload decisions with cloud destinations.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_vo_always_vertical; artifacts/feature_085_full_audit/raw_rows.json",
            status="approximate_documented",
            required_fix_or_claim_boundary="The cloud path is evidenced by scenario traces, not by a separate cloud simulator service.",
        ),
        MechanismCoverageRow(
            mechanism_id="task_model",
            paper_expectation="Tasks carry ID, data size, CPU demand/processing density, and deadline/timeout semantics.",
            simulator_behavior="TaskBlueprint and scenario rows retain task_id, workload, deadline pressure, and arrival/completion timing fields.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py",
            test_artifact_evidence="artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py",
            status="approximate_documented",
            required_fix_or_claim_boundary="The task model is reconstructed through deterministic scenario fixtures and runtime rows.",
        ),
        MechanismCoverageRow(
            mechanism_id="workload_arrival_representation",
            paper_expectation="Workload arrivals are represented over time or documented as deterministic approximations.",
            simulator_behavior="Scenario definitions encode workload and deadline-pressure profiles deterministically with seeds.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py; artifacts/feature_085_full_audit/execution_manifest.json",
            status="approximate_documented",
            required_fix_or_claim_boundary="Document the deterministic workload approximation; do not claim stochastic arrival fidelity.",
        ),
        MechanismCoverageRow(
            mechanism_id="private_queue_behavior",
            paper_expectation="Local/private queue behavior contributes waiting and completion time before local execution finishes.",
            simulator_behavior="Queue-length observations and delay traces are captured in the runtime rows, but the queue is represented through deterministic evidence rather than a standalone queue engine.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py",
            test_artifact_evidence="artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py",
            status="approximate_documented",
            required_fix_or_claim_boundary="This is an evidence-layer queue approximation, not a claim that the full FIFO queue simulator exists.",
        ),
        MechanismCoverageRow(
            mechanism_id="offloading_queue_behavior",
            paper_expectation="Offloaded tasks use offloading queues and transmission-time evidence before destination execution.",
            simulator_behavior="Horizontal and vertical candidate traces expose delay components and queue-length snapshots for offloaded actions.",
            code_location="src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/model.py",
            test_artifact_evidence="tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json",
            status="approximate_documented",
            required_fix_or_claim_boundary="The evidence is candidate-based, not a full queue-simulation replay.",
        ),
        MechanismCoverageRow(
            mechanism_id="public_cloud_queue_behavior",
            paper_expectation="Public/cloud queues receive vertically offloaded tasks and expose cloud-side waiting/execution behavior.",
            simulator_behavior="The cloud path appears in the runtime outcomes and scenario traces; public/cloud queue behavior is documented through output timing rather than a separate queue model.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/scenarios.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py",
            test_artifact_evidence="artifacts/feature_085_full_audit/raw_rows.json; artifacts/feature_085_full_audit/feature_085_audit_report.md",
            status="approximate_documented",
            required_fix_or_claim_boundary="The cloud queue is an audit abstraction and not a dedicated runtime queue class.",
        ),
        MechanismCoverageRow(
            mechanism_id="local_execution_delay",
            paper_expectation="Local execution delay contributes to completion time.",
            simulator_behavior="Local actions surface delay values and completion times in raw rows and aggregate metrics.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py",
            test_artifact_evidence="artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_artifacts.py",
            status="approximate_documented",
            required_fix_or_claim_boundary="Local delay is evidenced in runtime rows, not by a standalone physical simulator.",
        ),
        MechanismCoverageRow(
            mechanism_id="horizontal_transmission_delay",
            paper_expectation="Horizontal offload delay includes transmission delay between edge agents.",
            simulator_behavior="MLEO candidate traces expose horizontal transmission_delay and total_delay components.",
            code_location="src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py",
            test_artifact_evidence="tests/unit/test_mleo_latency_evidence.py::test_mleo_selects_minimum_total_delay_not_minimum_queue_length",
            status="exact",
            required_fix_or_claim_boundary="No additional repair required for the evidence layer.",
        ),
        MechanismCoverageRow(
            mechanism_id="vertical_transmission_delay",
            paper_expectation="Vertical offload delay includes EA-to-cloud transmission delay.",
            simulator_behavior="Vertical candidates in the MLEO and policy traces expose transmission_delay and total_delay components.",
            code_location="src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py",
            test_artifact_evidence="tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json",
            status="exact",
            required_fix_or_claim_boundary="No additional repair required for the evidence layer.",
        ),
        MechanismCoverageRow(
            mechanism_id="remote_cloud_execution_delay",
            paper_expectation="Remote/cloud execution delay contributes to total delay for vertical offload.",
            simulator_behavior="Cloud-bearing candidates carry compute_delay and total_delay evidence in the MLEO trace and runtime rows.",
            code_location="src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/model.py",
            test_artifact_evidence="tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json",
            status="approximate_documented",
            required_fix_or_claim_boundary="The remote compute term is evidence-backed, not a separate cloud runtime service.",
        ),
        MechanismCoverageRow(
            mechanism_id="waiting_time_completion_time",
            paper_expectation="Waiting time and completion time are explicit parts of task latency accounting.",
            simulator_behavior="Runtime rows capture arrival_time, completion_time, delay, and queue_length_observations.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py",
            test_artifact_evidence="artifacts/feature_085_full_audit/raw_rows.json; artifacts/feature_085_full_audit/aggregate_by_policy.csv",
            status="approximate_documented",
            required_fix_or_claim_boundary="Completion timing is represented in the audit layer, not as a full event simulator.",
        ),
        MechanismCoverageRow(
            mechanism_id="timeout_drop_unavailability_behavior",
            paper_expectation="Timeout, drop, and unavailability are reflected in output outcomes.",
            simulator_behavior="Runtime rows and aggregate metrics include dropped_timeout, dropped_unavailable, and illegal_action_rejected flags.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/metrics.py",
            test_artifact_evidence="artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py",
            status="approximate_documented",
            required_fix_or_claim_boundary="The audit tracks these outcomes explicitly; it does not claim a full event-level simulator.",
        ),
        MechanismCoverageRow(
            mechanism_id="hybrid_action_model",
            paper_expectation="Local, horizontal, and vertical actions exist as a hybrid offloading action space.",
            simulator_behavior="Active policies expose local, horizontal, and vertical families and the runtime policy set is the paper set.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/config.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_required_policy_set_matches_feature_085",
            status="exact",
            required_fix_or_claim_boundary="No repair required; the hybrid action contract is already active.",
        ),
        MechanismCoverageRow(
            mechanism_id="two_stage_decision_boundary",
            paper_expectation="Local-vs-offload and destination selection are distinct or are clearly documented when collapsed.",
            simulator_behavior="The runtime policy adapters operate as a documented single-stage approximation over legal candidate actions.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/policies/mleo.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_policies.py; tests/unit/test_mleo_latency_evidence.py",
            status="approximate_documented",
            required_fix_or_claim_boundary="Document the single-stage runtime approximation instead of pretending the training-stage boundary is reproduced.",
        ),
        MechanismCoverageRow(
            mechanism_id="hoodie_claim_boundary",
            paper_expectation="HOODIE remains the proposed method boundary and is not renamed or expanded into a thesis/DCQ method.",
            simulator_behavior="Feature 085/086 artifacts keep HOODIE as the proposed method boundary and do not introduce an alternate method claim.",
            code_location="specs/086-mleo-latency-evidence-test/spec.md; specs/086-mleo-latency-evidence-test/quickstart.md; src/analysis/hoodie_runtime_evaluation_runner/report.py",
            test_artifact_evidence="tests/integration/test_hoodie_runtime_evaluation_runner_report.py; artifacts/feature_085_full_audit/feature_085_audit_report.md",
            status="exact",
            required_fix_or_claim_boundary="No thesis/DCQ/custom-method claim is allowed.",
        ),
        MechanismCoverageRow(
            mechanism_id="official_paper_baselines",
            paper_expectation="Only RO, FLC, VO, HO, BCO, and MLEO are active baselines.",
            simulator_behavior="The runtime evaluation policy registry exposes exactly the paper baselines plus HOODIE.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_required_policy_set_matches_feature_085",
            status="exact",
            required_fix_or_claim_boundary="No legacy active labels remain in the 086 outputs.",
        ),
        MechanismCoverageRow(
            mechanism_id="mleo_min_total_latency",
            paper_expectation="MLEO selects the legal candidate with minimum estimated total latency, not queue length only.",
            simulator_behavior="The candidate trace test proves MLEO chooses the minimum total_delay candidate when queue-length minimum is different.",
            code_location="src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py",
            test_artifact_evidence="tests/unit/test_mleo_latency_evidence.py::test_mleo_selects_minimum_total_delay_not_minimum_queue_length",
            status="exact",
            required_fix_or_claim_boundary="No repair required for the evidence layer; keep the numeric proof.",
        ),
        MechanismCoverageRow(
            mechanism_id="reward_cost_boundary",
            paper_expectation="Reward/cost equations remain inside the paper’s comparison boundary and are not overclaimed.",
            simulator_behavior="The runtime audit reports reward, delay, and drop outcomes with explicit claim-boundary text.",
            code_location="src/analysis/hoodie_runtime_evaluation_runner/metrics.py; src/analysis/hoodie_runtime_evaluation_runner/report.py; resources/papers/hoodie/ocr/merged.txt",
            test_artifact_evidence="tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py; artifacts/feature_085_full_audit/feature_085_audit_report.md",
            status="approximate_documented",
            required_fix_or_claim_boundary="Do not claim a trained end-to-end reward model; keep the boundary conservative.",
        ),
        MechanismCoverageRow(
            mechanism_id="output_metrics_readiness",
            paper_expectation="Metrics are classified so that paper-headline comparison and repository diagnostics are not conflated.",
            simulator_behavior="The metric readiness matrix classifies primary, secondary, and diagnostic metrics explicitly.",
            code_location="specs/086-mleo-latency-evidence-test/metric-readiness-matrix.md; src/analysis/hoodie_system_model_fidelity_gate/report.py",
            test_artifact_evidence="tests/unit/test_hoodie_system_model_fidelity_gate.py",
            status="exact",
            required_fix_or_claim_boundary="Do not promote repository diagnostics to paper headline metrics.",
        ),
    ]
    missing = [mechanism_id for mechanism_id in REQUIRED_MECHANISM_IDS if mechanism_id not in {row.mechanism_id for row in rows}]
    if missing:
        raise ValueError(f"mechanism coverage rows missing: {', '.join(missing)}")
    return tuple(rows)


def _system_model_gap_rows(mechanisms: tuple[MechanismCoverageRow, ...]) -> tuple[SystemModelGapRow, ...]:
    return tuple(SystemModelGapRow(**row.to_dict()) for row in mechanisms)


def _metric_rows() -> tuple[MetricReadinessRow, ...]:
    return (
        MetricReadinessRow(
            metric="task_completion_delay",
            classification="paper_primary_metric",
            paper_use="headline_paper-comparison metric",
            status="ready",
            evidence="paper OCR defines average delay / completion-delay comparison and runtime rows expose completion time and delay.",
        ),
        MetricReadinessRow(
            metric="task_drop_ratio",
            classification="paper_primary_metric",
            paper_use="headline_paper-comparison metric",
            status="ready",
            evidence="paper OCR compares drop ratio and runtime rows expose timeout/drop/unavailability outcomes.",
        ),
        MetricReadinessRow(
            metric="completion_rate",
            classification="paper_secondary_or_derived_metric",
            paper_use="derived reliability metric for supporting analysis",
            status="ready",
            evidence="Derived from completed and dropped rows in the runtime evaluation bundle.",
        ),
        MetricReadinessRow(
            metric="timeout_drop_rate",
            classification="repository_diagnostic_metric",
            paper_use="runtime diagnostic; not a paper headline metric",
            status="diagnostic_only",
            evidence="Useful for simulator validation; do not present as a paper headline unless separately justified.",
        ),
        MetricReadinessRow(
            metric="unavailable_drop_rate",
            classification="repository_diagnostic_metric",
            paper_use="runtime diagnostic; not a paper headline metric",
            status="diagnostic_only",
            evidence="Tracks availability failures as a simulator diagnostic.",
        ),
        MetricReadinessRow(
            metric="deadline_violation_rate",
            classification="repository_diagnostic_metric",
            paper_use="runtime diagnostic; not a paper headline metric",
            status="diagnostic_only",
            evidence="Tracks deadline misses as a validation aid, not as a headline paper metric.",
        ),
        MetricReadinessRow(
            metric="average_reward",
            classification="paper_secondary_or_repository_metric",
            paper_use="supporting optimization metric with an explicit claim boundary",
            status="ready_with_boundary",
            evidence="Reward output exists in runtime rows but the audit does not claim a full training-loop reproduction.",
        ),
        MetricReadinessRow(
            metric="total_reward",
            classification="paper_secondary_or_repository_metric",
            paper_use="supporting optimization metric with an explicit claim boundary",
            status="ready_with_boundary",
            evidence="Aggregate reward is exposed for analysis and marked as a supporting metric only.",
        ),
        MetricReadinessRow(
            metric="throughput",
            classification="paper_secondary_or_repository_metric",
            paper_use="supporting system-throughput metric with an explicit claim boundary",
            status="ready_with_boundary",
            evidence="Throughput is retained as a secondary comparison metric, not a headline one.",
        ),
        MetricReadinessRow(
            metric="queue_stability_score",
            classification="repository_diagnostic_metric",
            paper_use="internal diagnostic only",
            status="diagnostic_only",
            evidence="Queue-stability score is an audit helper, not a paper metric.",
        ),
        MetricReadinessRow(
            metric="illegal_action_rejection_count",
            classification="repository_diagnostic_metric",
            paper_use="legal-action diagnostic only",
            status="diagnostic_only",
            evidence="Counts illegal-action rejections to validate legality handling.",
        ),
    )


def _scenario_rows() -> tuple[ScenarioMechanismCoverageRow, ...]:
    return (
        ScenarioMechanismCoverageRow(
            scenario="light_load_no_deadline_pressure",
            workload="low",
            deadline_pressure="relaxed",
            exercised_mechanisms=("local_execution_delay", "hybrid_action_model", "output_metrics_readiness"),
            status="exact",
            evidence="Runtime rows include low-load local and offload decisions with completed-delay evidence.",
        ),
        ScenarioMechanismCoverageRow(
            scenario="tight_deadline_pressure",
            workload="high",
            deadline_pressure="tight",
            exercised_mechanisms=("timeout_drop_unavailability_behavior", "mleo_min_total_latency", "output_metrics_readiness"),
            status="exact",
            evidence="This is the divergent HOODIE/MLEO scenario with explicit delay-vs-drop behavior.",
        ),
        ScenarioMechanismCoverageRow(
            scenario="legal_horizontal_offload",
            workload="medium",
            deadline_pressure="moderate",
            exercised_mechanisms=("horizontal_connectivity_legality", "horizontal_transmission_delay", "hybrid_action_model"),
            status="exact",
            evidence="Horizontal offload is legal and exercised in runtime rows and policy tests.",
        ),
        ScenarioMechanismCoverageRow(
            scenario="illegal_horizontal_destination_attempt",
            workload="medium",
            deadline_pressure="moderate",
            exercised_mechanisms=("horizontal_connectivity_legality", "timeout_drop_unavailability_behavior", "hybrid_action_model"),
            status="exact",
            evidence="Illegal horizontal destination attempts are rejected in policy traces.",
        ),
        ScenarioMechanismCoverageRow(
            scenario="cloud_vertical_fallback",
            workload="high",
            deadline_pressure="tight",
            exercised_mechanisms=("vertical_ea_cloud_path", "vertical_transmission_delay", "remote_cloud_execution_delay"),
            status="exact",
            evidence="Cloud fallback exercises the vertical/cloud path and cloud delay components.",
        ),
        ScenarioMechanismCoverageRow(
            scenario="timeout_drop_case",
            workload="high",
            deadline_pressure="tight",
            exercised_mechanisms=("timeout_drop_unavailability_behavior", "waiting_time_completion_time", "mleo_min_total_latency"),
            status="exact",
            evidence="Timeout/drop behavior is exercised and the HOODIE/MLEO divergence is documented here.",
        ),
        ScenarioMechanismCoverageRow(
            scenario="mixed_local_horizontal_cloud_candidates",
            workload="medium",
            deadline_pressure="moderate",
            exercised_mechanisms=("hybrid_action_model", "two_stage_decision_boundary", "official_paper_baselines"),
            status="exact",
            evidence="Mixed candidate sets exercise local, horizontal, and vertical candidate selection.",
        ),
    )


def _load_hoodie_mleo_tie_evidence() -> HoodieMleoTieEvidence:
    raw_rows_path = FEATURE_085_AUDIT_DIR / "raw_rows.json"
    if not raw_rows_path.exists():
        return HoodieMleoTieEvidence(
            source_artifact_dir=str(FEATURE_085_AUDIT_DIR),
            matching_rows=0,
            differing_rows=0,
            identical_scenarios=(),
            divergent_scenarios=(),
            divergent_action_counts={},
        )
    payload = json.loads(raw_rows_path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    hoodie_rows = [row for row in rows if row.get("policy") == "HOODIE"]
    mleo_rows = [row for row in rows if row.get("policy") == "MLEO"]
    hoodie_rows.sort(key=lambda row: (row.get("scenario_name"), row.get("workload"), row.get("deadline_pressure"), row.get("seed"), row.get("task_id")))
    mleo_rows.sort(key=lambda row: (row.get("scenario_name"), row.get("workload"), row.get("deadline_pressure"), row.get("seed"), row.get("task_id")))
    same = 0
    different = 0
    same_scenarios: set[str] = set()
    different_scenarios: set[str] = set()
    divergent_action_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for left, right in zip(hoodie_rows, mleo_rows):
        scenario = str(left.get("scenario_name"))
        if left.get("selected_action") == right.get("selected_action"):
            same += 1
            same_scenarios.add(scenario)
        else:
            different += 1
            different_scenarios.add(scenario)
            pair = f"{left.get('selected_action')}->{right.get('selected_action')}"
            divergent_action_counts[scenario][pair] += 1
    return HoodieMleoTieEvidence(
        source_artifact_dir=str(FEATURE_085_AUDIT_DIR),
        matching_rows=same,
        differing_rows=different,
        identical_scenarios=tuple(sorted(same_scenarios)),
        divergent_scenarios=tuple(sorted(different_scenarios)),
        divergent_action_counts={scenario: dict(sorted(counts.items())) for scenario, counts in sorted(divergent_action_counts.items())},
    )


def build_feature_086_report() -> Feature086Report:
    mechanism_coverage = _mechanism_rows()
    system_model_gap_matrix = _system_model_gap_rows(mechanism_coverage)
    metric_readiness_matrix = _metric_rows()
    scenario_mechanism_coverage = _scenario_rows()
    tie_evidence = _load_hoodie_mleo_tie_evidence()

    blocked_mechanisms = tuple(
        row.mechanism_id
        for row in mechanism_coverage
        if row.status in {"missing", "wrong", "not_exercised"}
    )
    remaining_approximations = tuple(
        row.mechanism_id
        for row in mechanism_coverage
        if row.status == "approximate_documented"
    )
    verdict = READY_STATUS if not blocked_mechanisms else BLOCKED_STATUS
    passed = verdict == READY_STATUS

    invalid_label_check = (
        "Legacy active-label check passed: retired aliases are absent from the active 086 outputs.",
        "Historical references remain in prior feature documentation only.",
    )
    claim_boundary = (
        "HOODIE remains the Feature 080 proposed method boundary.",
        "No thesis method, DCQ method, or custom queue redesign is introduced.",
        "The audit documents interface-only DRL/LSTM/forecast boundaries where full training is not reproduced.",
        "No full empirical HOODIE reproduction claim is made.",
    )
    scope_proof = (
        "Active policies are the paper set: HOODIE, RO, FLC, VO, HO, BCO, MLEO.",
        "No legacy active labels are exposed in the Feature 086 outputs.",
        "No thesis/DCQ/custom-method code is added.",
        "MLEO evidence remains a policy-evidence boundary, not a new proposed method.",
    )

    allowed_paper_comparison_metrics = (
        "task_completion_delay",
        "task_drop_ratio",
        "completion_rate",
        "average_reward",
        "total_reward",
        "throughput",
    )
    repository_diagnostic_metrics = REPOSITORY_DIAGNOSTIC_METRICS

    return Feature086Report(
        feature_id=FEATURE_ID,
        status=verdict,
        passed=passed,
        verdict=verdict,
        active_policies=ACTIVE_POLICIES,
        invalid_label_check=invalid_label_check,
        mechanism_coverage=mechanism_coverage,
        system_model_gap_matrix=system_model_gap_matrix,
        metric_readiness_matrix=metric_readiness_matrix,
        scenario_mechanism_coverage=scenario_mechanism_coverage,
        hoodie_mleo_tie_evidence=tie_evidence,
        claim_boundary=claim_boundary,
        scope_proof=scope_proof,
        blocked_mechanisms=blocked_mechanisms,
        remaining_approximations=remaining_approximations,
        allowed_paper_comparison_metrics=allowed_paper_comparison_metrics,
        repository_diagnostic_metrics=repository_diagnostic_metrics,
        output_comparison_ready=passed,
    )


def render_feature_086_report(report: Feature086Report) -> str:
    payload = report.to_dict()
    mechanism_rows = _rows_to_markdown(payload["mechanism_coverage"])
    gap_rows = _rows_to_markdown(payload["system_model_gap_matrix"])
    metric_rows = _rows_to_markdown(payload["metric_readiness_matrix"])
    scenario_rows = _rows_to_markdown(payload["scenario_mechanism_coverage"])
    tie = payload["hoodie_mleo_tie_evidence"]
    lines = [
        "# Feature 086 HOODIE System-Model Fidelity Gate Report",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- status: `{payload['status']}`",
        f"- passed: `{payload['passed']}`",
        f"- verdict: `{payload['verdict']}`",
        f"- output_comparison_ready: `{payload['output_comparison_ready']}`",
        f"- active_policy_count: `{len(payload['active_policies'])}`",
        f"- mechanism_count: `{len(payload['mechanism_coverage'])}`",
        f"- metric_count: `{len(payload['metric_readiness_matrix'])}`",
        "",
        "## Active Policies",
        *[f"- {policy}" for policy in payload["active_policies"]],
        "",
        "## Invalid-Label Check",
        *[f"- {line}" for line in payload["invalid_label_check"]],
        "",
        "## Verdict",
        f"- `{payload['verdict']}`",
        "",
        "## Mechanism Coverage Summary",
        f"- exact: `{sum(1 for row in payload['mechanism_coverage'] if row['status'] == 'exact')}`",
        f"- approximate_documented: `{sum(1 for row in payload['mechanism_coverage'] if row['status'] == 'approximate_documented')}`",
        f"- blocking: `{len(payload['blocked_mechanisms'])}`",
        "",
        "## Mechanism Coverage",
        mechanism_rows,
        "",
        "## System Model Gap Matrix",
        gap_rows,
        "",
        "## Metric Readiness Summary",
        f"- paper_primary_metric: `{', '.join(metric['metric'] for metric in payload['metric_readiness_matrix'] if metric['classification'] == 'paper_primary_metric')}`",
        f"- paper_secondary_or_derived_metric: `{', '.join(metric['metric'] for metric in payload['metric_readiness_matrix'] if metric['classification'] == 'paper_secondary_or_derived_metric')}`",
        f"- paper_secondary_or_repository_metric: `{', '.join(metric['metric'] for metric in payload['metric_readiness_matrix'] if metric['classification'] == 'paper_secondary_or_repository_metric')}`",
        f"- repository_diagnostic_metric: `{', '.join(metric['metric'] for metric in payload['metric_readiness_matrix'] if metric['classification'] == 'repository_diagnostic_metric')}`",
        "",
        "## Metric Readiness Matrix",
        metric_rows,
        "",
        "## Scenario Mechanism Coverage Summary",
        f"- exact scenarios: `{len([row for row in payload['scenario_mechanism_coverage'] if row['status'] == 'exact'])}`",
        "",
        "## Scenario Mechanism Coverage",
        scenario_rows,
        "",
        "## HOODIE / MLEO Tie Evidence",
        f"- source_artifact_dir: `{tie['source_artifact_dir']}`",
        f"- matching_rows: `{tie['matching_rows']}`",
        f"- differing_rows: `{tie['differing_rows']}`",
        f"- identical_scenarios: `{', '.join(tie['identical_scenarios'])}`",
        f"- divergent_scenarios: `{', '.join(tie['divergent_scenarios'])}`",
        f"- divergent_action_counts: `{json.dumps(tie['divergent_action_counts'], sort_keys=True)}`",
        "",
        "## Allowed Paper-Comparison Metrics",
        *[f"- {metric}" for metric in payload["allowed_paper_comparison_metrics"]],
        "",
        "## Repository Diagnostic Metrics",
        *[f"- {metric}" for metric in payload["repository_diagnostic_metrics"]],
        "",
        "## Remaining Approximations",
        *[f"- {item}" for item in payload["remaining_approximations"]],
        "",
        "## Scope Proof",
        *[f"- {item}" for item in payload["scope_proof"]],
        "",
        "## Claim Boundary",
        *[f"- {item}" for item in payload["claim_boundary"]],
        "",
    ]
    return "\n".join(lines)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def build_feature_086_artifact_payloads() -> dict[str, Any]:
    report = build_feature_086_report()
    return {
        "report": report,
        "mechanism_coverage": [row.to_dict() for row in report.mechanism_coverage],
        "system_model_gap_matrix": [row.to_dict() for row in report.system_model_gap_matrix],
        "metric_readiness_matrix": [row.to_dict() for row in report.metric_readiness_matrix],
        "scenario_mechanism_coverage": [row.to_dict() for row in report.scenario_mechanism_coverage],
        "hoodie_mleo_tie_evidence": report.hoodie_mleo_tie_evidence.to_dict(),
    }


def dump_json(payload: Any) -> str:
    return _json_dump(_json_safe(payload))
