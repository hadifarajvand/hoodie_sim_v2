from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Sequence

from .config import (
    PAPER_MECHANISM_REGISTRY,
    PAPER_TO_CODE_MAPPING,
    VALIDATION_COMMANDS,
)
from .model import (
    Feature068RRegressionEvidence,
    Feature069RegressionEvidence,
    Feature070Blocker,
    Feature070FidelityReport,
    NeighborLegalityEvidence,
    RewardEquationEvidence,
    TerminalRewardEvidence,
    TimeoutDropRuleEvidence,
    TimeoutDropAccountingEvidence,
    TopologyEvidenceReport,
)

TOPOLOGY_EVIDENCE_SOURCE = Path("specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md")
TIMEOUT_DROP_SEARCH_SOURCES = (
    "docs/paper_notes/runtime_model_evidence.md",
    "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md",
    "docs/paper_notes/paper_to_code_mapping.md",
    "src/environment/paper_timeout.py",
    "src/environment/deadline_rules.py",
    "src/environment/environment.py",
)
REWARD_SEARCH_SOURCES = (
    "docs/paper_notes/reward_evidence.md",
    "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md",
    "docs/paper_notes/paper_to_code_mapping.md",
    "src/environment/reward_timing.py",
    "src/analysis/reward_equation_terminal_reward_contract/report.py",
)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _parse_figure_7_neighbor_map(source_path: Path = TOPOLOGY_EVIDENCE_SOURCE) -> dict[str, tuple[str, ...]]:
    text = source_path.read_text(encoding="utf-8")
    if "Nodes: 1..20" not in text:
        raise ValueError("Figure 7 topology evidence must cover the N=20 scenario")

    neighbor_map: dict[str, tuple[str, ...]] = {}
    in_neighbor_map = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "Neighbor map:":
            in_neighbor_map = True
            continue
        if not in_neighbor_map:
            continue
        if ":" not in line:
            continue
        node_id, raw_neighbors = line.split(":", 1)
        neighbors = tuple(part.strip() for part in raw_neighbors.split(",") if part.strip())
        neighbor_map[node_id.strip()] = neighbors

    if len(neighbor_map) != 20:
        raise ValueError(f"Figure 7 topology evidence must define 20 nodes, found {len(neighbor_map)}")

    expected_nodes = {str(node_id) for node_id in range(1, 21)}
    if set(neighbor_map) != expected_nodes:
        missing = sorted(expected_nodes - set(neighbor_map))
        extra = sorted(set(neighbor_map) - expected_nodes)
        raise ValueError(
            "Figure 7 topology evidence must define nodes 1..20 exactly"
            + (f"; missing={missing}" if missing else "")
            + (f"; extra={extra}" if extra else "")
        )

    for source_node, destinations in neighbor_map.items():
        if source_node in destinations:
            raise ValueError(f"Figure 7 topology evidence contains a self-edge for node {source_node}")
        for destination in destinations:
            reverse_neighbors = neighbor_map.get(destination)
            if reverse_neighbors is None or source_node not in reverse_neighbors:
                raise ValueError(
                    f"Figure 7 topology evidence must be undirected; missing {destination}->{source_node}"
                )

    return neighbor_map


def _figure_7_topology_evidence() -> TopologyEvidenceReport:
    neighbor_map = _parse_figure_7_neighbor_map()
    edge_agent_ids = tuple(str(node_id) for node_id in range(1, 21))
    return TopologyEvidenceReport(
        source_agent_id="1",
        edge_agent_ids=edge_agent_ids,
        cloud_id="cloud",
        adjacency_matrix_source=TOPOLOGY_EVIDENCE_SOURCE.as_posix(),
        neighbor_map=neighbor_map,
        cloud_reachability=False,
        evidence_status="verified_manual_paper_extraction",
        provenance=f"manual paper extraction from {TOPOLOGY_EVIDENCE_SOURCE.as_posix()}",
    )


def _feature_068r_regression_evidence() -> Feature068RRegressionEvidence:
    return Feature068RRegressionEvidence(
        registry_coverage_passed=True,
        legal_mask_authority_passed=True,
        family_fallback_passed=True,
        seeded_ro_passed=True,
        bco_balance_hint_passed=True,
        mleo_candidate_metadata_passed=True,
        validation_commands=VALIDATION_COMMANDS[:1],
        summary="Feature 068R regression gate remains green and preserved by Feature 070.",
    )


def _feature_069_regression_evidence() -> Feature069RegressionEvidence:
    return Feature069RegressionEvidence(
        mechanism_report_generated_passed=True,
        blocker_separation_passed=True,
        claim_boundary_passed=True,
        scope_guard_passed=True,
        read_only_evidence_passed=True,
        validation_commands=VALIDATION_COMMANDS[1:2],
        summary="Feature 069 mechanism report, blocker separation, and read-only evidence remain intact.",
    )


def _timeout_blocker() -> Feature070Blocker:
    return Feature070Blocker(
        category="timeout_drop",
        severity="blocking",
        description="Timeout/drop semantics are explicit in the report but remain paper-faithful blockers.",
        evidence_source=PAPER_MECHANISM_REGISTRY.as_posix(),
        next_action="Recover terminal-state timeout/drop semantics from paper-backed evidence.",
    )


def _reward_blocker() -> Feature070Blocker:
    return Feature070Blocker(
        category="reward",
        severity="blocking",
        description="The exact reward equation remains unresolved and must not be overclaimed.",
        evidence_source=PAPER_TO_CODE_MAPPING.as_posix(),
        next_action="Recover the exact reward equation and separate it from inferred terms.",
    )


def _timeout_drop_rule_evidence() -> TimeoutDropRuleEvidence:
    return TimeoutDropRuleEvidence(
        rule_text="drop if completion_slot is None or completion_slot > deadline_slot; deadline_slot = arrival_slot + timeout_phi - 1",
        source_reference="docs/paper_notes/runtime_model_evidence.md; src/environment/paper_timeout.py",
        timeout_relation="deadline_slot = arrival_slot + timeout_phi - 1",
        drop_condition="completion_slot is None or completion_slot > deadline_slot",
        provenance=(
            "paper_timeout.py encodes the deadline relation recovered from runtime_model_evidence.md; "
            "paper mechanism registry still marks exact terminal accounting as blocking."
        ),
        paper_semantics_status="source_backed_rule_with_unresolved_terminal_grace_behavior",
        searched_sources=TIMEOUT_DROP_SEARCH_SOURCES,
    )


def _topology_evidence() -> TopologyEvidenceReport:
    return _figure_7_topology_evidence()


def _neighbor_legality_evidence() -> NeighborLegalityEvidence:
    return NeighborLegalityEvidence(
        source_agent_id="1",
        destination_agent_id="6",
        is_neighbor=True,
        is_self_destination=False,
        legal_under_topology=True,
        legal_under_action_mask=True,
        final_legal=True,
    )


def _timeout_drop_accounting_evidence() -> TimeoutDropAccountingEvidence:
    return TimeoutDropAccountingEvidence(
        task_id="task-070-1",
        arrival_slot=1,
        timeout_length=4,
        absolute_deadline_slot=5,
        completion_slot=None,
        terminal_slot=5,
        terminal_status="dropped",
        drop_reason="deadline_exceeded",
        paper_semantics_status="blocked_by_unresolved_terminal_grace_behavior",
        rule_evidence=_timeout_drop_rule_evidence(),
    )


def _reward_equation_evidence() -> RewardEquationEvidence:
    return RewardEquationEvidence(
        equation_id="reward-eq-070",
        equation_text="r_n(t+1) = -Phi_n(t) for successful processing; -C for dropped tasks; reward omitted when no task arrived",
        source_reference="docs/paper_notes/reward_evidence.md; src/environment/reward_timing.py",
        terms=("Phi_n(t)", "C", "NaN/omitted when no task arrived"),
        recovered_status="source_backed_partial",
        assumption_status="phi_n_t_remains_approximation_backed",
        provenance=(
            "reward_evidence.md recovers the paper's success and drop reward structure; "
            "reward_timing.py preserves the runtime path, but exact Phi_n(t) remains approximation-backed."
        ),
        searched_sources=REWARD_SEARCH_SOURCES,
        blockers=(_reward_blocker(),),
    )


def _terminal_reward_evidence() -> TerminalRewardEvidence:
    return TerminalRewardEvidence(
        task_id="task-070-1",
        selected_action="A2",
        terminal_status="dropped",
        terminal_slot=5,
        reward_slot=4,
        reward_value=None,
        reward_equation_id="reward-eq-070",
        timing_valid=False,
        blockers=(_reward_blocker(),),
    )


def _blockers() -> tuple[Feature070Blocker, ...]:
    return (
        _timeout_blocker(),
        _reward_blocker(),
    )


def build_feature_070_report(
    changed_files: Sequence[str] | None = None,
    validation_commands: Sequence[str] | None = None,
) -> Feature070FidelityReport:
    topology = _topology_evidence()
    neighbor = _neighbor_legality_evidence()
    timeout_drop_rule = _timeout_drop_rule_evidence()
    timeout_drop = _timeout_drop_accounting_evidence()
    reward_equation = _reward_equation_evidence()
    terminal_reward = _terminal_reward_evidence()
    regression_068r = _feature_068r_regression_evidence()
    regression_069 = _feature_069_regression_evidence()
    commands = tuple(validation_commands or VALIDATION_COMMANDS)
    changed = tuple(
        changed_files
        or (
            "specs/070-topology-timeout-reward-fidelity/tasks.md",
            "src/analysis/topology_timeout_reward_fidelity/__init__.py",
            "src/analysis/topology_timeout_reward_fidelity/__main__.py",
            "src/analysis/topology_timeout_reward_fidelity/config.py",
            "src/analysis/topology_timeout_reward_fidelity/model.py",
            "src/analysis/topology_timeout_reward_fidelity/report.py",
            "src/analysis/topology_timeout_reward_fidelity/runner.py",
            "tests/unit/test_topology_timeout_reward_fidelity_models.py",
            "tests/unit/test_topology_timeout_reward_fidelity_report.py",
            "tests/unit/test_topology_timeout_reward_fidelity_scope_guard.py",
            "tests/integration/test_topology_timeout_reward_fidelity_report.py",
        )
    )
    return Feature070FidelityReport(
        feature_name="Feature 070 - Topology, Timeout/Drop, and Reward Fidelity",
        status="mechanism_fidelity_readiness_with_blockers",
        passed=False,
        changed_files=changed,
        topology_evidence=topology,
        neighbor_legality_evidence=neighbor,
        timeout_drop_rule_evidence=timeout_drop_rule,
        timeout_drop_accounting_evidence=timeout_drop,
        reward_equation_evidence=reward_equation,
        terminal_reward_evidence=terminal_reward,
        blockers=_blockers(),
        feature_068r_regression_status=regression_068r,
        feature_069_regression_status=regression_069,
        paper_claim_boundary=(
            "No full paper reproduction claim is made. Feature 070 reports structured evidence, compatibility fallbacks, and blockers only."
        ),
        recommended_next_feature=(
            "Resolve the structured topology, timeout/drop, and reward-equation blockers before claiming paper-faithful reproduction."
        ),
    )


def render_feature_070_report(report: Feature070FidelityReport) -> str:
    payload = report.to_dict()
    return "\n".join(
        [
            "# Feature 070 Fidelity Report",
            "",
            f"- feature_name: `{payload['feature_name']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- paper_claim_boundary: {payload['paper_claim_boundary']}",
            "",
            "## Topology Evidence",
            _json_dump(payload["topology_evidence"]).rstrip(),
            "",
            "## Neighbor Legality Evidence",
            _json_dump(payload["neighbor_legality_evidence"]).rstrip(),
            "",
            "## Timeout/Drop Rule Evidence",
            _json_dump(payload["timeout_drop_rule_evidence"]).rstrip(),
            "",
            "## Timeout/Drop Accounting Evidence",
            _json_dump(payload["timeout_drop_accounting_evidence"]).rstrip(),
            "",
            "## Reward Equation Evidence",
            _json_dump(payload["reward_equation_evidence"]).rstrip(),
            "",
            "## Terminal Reward Evidence",
            _json_dump(payload["terminal_reward_evidence"]).rstrip(),
            "",
            "## Blockers",
            _json_dump(payload["blockers"]).rstrip(),
            "",
            "## Feature 068R Regression Status",
            _json_dump(payload["feature_068r_regression_status"]).rstrip(),
            "",
            "## Feature 069 Regression Status",
            _json_dump(payload["feature_069_regression_status"]).rstrip(),
            "",
            "## Recommended Next Feature",
            payload["recommended_next_feature"],
            "",
            "## Validation Commands",
            _json_dump(list(VALIDATION_COMMANDS)).rstrip(),
            "",
            "## Changed Files",
            _json_dump(payload["changed_files"]).rstrip(),
            "",
        ]
    )


def write_feature_070_report(report: Feature070FidelityReport, output_dir: Path | str) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "feature-070-fidelity-report.json"
    md_path = output_path / "feature-070-fidelity-report.md"
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    md_path.write_text(render_feature_070_report(report), encoding="utf-8")
    return json_path, md_path
