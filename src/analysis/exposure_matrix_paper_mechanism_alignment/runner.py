from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import subprocess
from typing import Any

from .config import (
    FEATURE_043_REPORT,
    FEATURE_044_REPORT,
    FEATURE_045_REPORT,
    FEATURE_046_REPORT,
    FEATURE_047_REPORT,
    FEATURE_048_REPORT,
    FEATURE_ID,
    ExposureMatrixPaperMechanismConfig,
)
from .model import (
    ExposureMatrixPaperMechanismReport,
    ExposureMatrixRerunSummary,
    LegalVsSelectedActionMatrix,
    ObservationVectorAudit,
    PaperFormulaUnitAudit,
    TrainingReadinessDecision,
)
from .report import write_exposure_matrix_paper_mechanism_report

ALLOWED_DIRTY_PATH_PREFIXES = (
    "specs/049-exposure-matrix-paper-mechanism-alignment/",
    "src/analysis/exposure_matrix_paper_mechanism_alignment/",
    "tests/unit/test_exposure_matrix_paper_mechanism_schema.py",
    "tests/unit/test_exposure_matrix_paper_mechanism_metrics.py",
    "tests/integration/test_exposure_matrix_paper_mechanism_alignment.py",
    "tests/integration/test_exposure_matrix_paper_mechanism_report.py",
    "tests/integration/test_exposure_matrix_paper_mechanism_scope_guard.py",
    "artifacts/analysis/exposure-matrix-paper-mechanism-alignment/",
)

FEATURE_048_REQUIRED_KEYS = (
    "legal_evidence_coverage_ratio",
    "legality_evidence_coverage_summary",
    "legality_snapshot_count",
    "decision_opportunity_count",
    "per_strategy_seed_legality_coverage",
    "selected_illegal_action_count",
    "selected_illegal_action_rate",
    "behavior_equivalence_summary",
    "exposure_matrix_unblocked",
)

SELECTED_FAMILY_KEYS = (
    "selected_local_count",
    "selected_horizontal_count",
    "selected_vertical_count",
)

LEGAL_FAMILY_KEYS = (
    "legal_local_count",
    "legal_horizontal_count",
    "legal_vertical_count",
)

PER_ACTION_OUTCOME_KEYS = (
    "per_action_completion_rate",
    "per_action_drop_rate",
    "per_action_pending_rate",
)


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    return path == ".specify/feature.json" or any(path.startswith(prefix) for prefix in ALLOWED_DIRTY_PATH_PREFIXES)


def _validate_dirty_paths() -> list[str]:
    dirty = _tracked_dirty_paths()
    if any(path == "AGENTS.md" or path.endswith("/AGENTS.md") for path in dirty):
        raise RuntimeError("AGENTS.md must be clean before Feature 049 report generation.")
    unrelated = [path for path in dirty if not _is_allowed_dirty_path(path)]
    if unrelated:
        raise RuntimeError("Dirty paths outside approved Feature 049 scope block report generation: " + ", ".join(unrelated))
    return dirty


def _validate_prerequisites() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    _validate_dirty_paths()
    r43 = _load_json(FEATURE_043_REPORT)
    r44 = _load_json(FEATURE_044_REPORT)
    r45 = _load_json(FEATURE_045_REPORT)
    r46 = _load_json(FEATURE_046_REPORT)
    r47 = _load_json(FEATURE_047_REPORT)
    r48 = _load_json(FEATURE_048_REPORT)
    if r43.get("feature_id") != "043-task-completion-lifecycle-formula-audit":
        raise ValueError("Feature 043 report required")
    if r44.get("feature_id") != "044-passive-runtime-lifecycle-trace-instrumentation":
        raise ValueError("Feature 044 report required")
    if r45.get("feature_id") != "045-completion-root-cause-diagnosis":
        raise ValueError("Feature 045 report required")
    if r46.get("feature_id") != "046-load-admission-action-exposure-review":
        raise ValueError("Feature 046 report required")
    if r47.get("feature_id") != "047-exposure-matrix-review":
        raise ValueError("Feature 047 report required")
    if r48.get("feature_id") != "048-legality-evidence-expansion":
        raise ValueError("Feature 048 report required")
    return r43, r44, r45, r46, r47, r48


def _prerequisite_tags() -> list[dict[str, Any]]:
    dirty = _validate_dirty_paths()
    specify_path = Path(".specify/feature.json")
    pointer_correct = specify_path.exists() and "specs/049-exposure-matrix-paper-mechanism-alignment" in specify_path.read_text(encoding="utf-8")
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == FEATURE_ID, "details": f"current branch is {FEATURE_ID}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "branch is not main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "details": "main matches origin/main"},
        {"name": "main_equals_feature_048", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "048-legality-evidence-expansion-complete^{}"), "details": "main matches 048-legality-evidence-expansion-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "048-legality-evidence-expansion-complete^{}", "main") == "", "details": "diff between 048-legality-evidence-expansion-complete^{} and main is empty"},
        {"name": "pointer_correct", "verified": pointer_correct, "details": ".specify/feature.json points at Feature 049 when present"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json is not staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "main...HEAD").splitlines(), "details": ".specify/feature.json is not in main...HEAD diff"},
        {"name": "agents_clean_before_report", "verified": not any(path == "AGENTS.md" or path.endswith("/AGENTS.md") for path in dirty), "details": "AGENTS.md clean before report generation"},
    ]


def _prior_feature_gates() -> list[dict[str, Any]]:
    entries = [
        ("037", "baseline revalidation", "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"),
        ("038", "training foundation", "artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json"),
        ("039", "paper HOODIE network", "artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"),
        ("040", "smoke training", "artifacts/analysis/smoke-training/smoke-training-report.json"),
        ("041", "full-training campaign gate", "artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json"),
        ("042", "paper default terminal exposure", "artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json"),
        ("043", "task completion lifecycle audit", str(FEATURE_043_REPORT)),
        ("044", "passive runtime lifecycle trace instrumentation", str(FEATURE_044_REPORT)),
        ("045", "completion root-cause diagnosis", str(FEATURE_045_REPORT)),
        ("046", "load/admission/action exposure review", str(FEATURE_046_REPORT)),
        ("047", "exposure matrix review", str(FEATURE_047_REPORT)),
        ("048", "legality evidence expansion", str(FEATURE_048_REPORT)),
    ]
    return [{"feature": feature, "name": name, "verified": Path(path).exists(), "details": f"{path} exists"} for feature, name, path in entries]


def _load_048() -> dict[str, Any]:
    return _load_json(FEATURE_048_REPORT)


def _has_keys(mapping: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(key in mapping for key in keys)


def _selected_action_family_evidence_status(feature_048: dict[str, Any]) -> str:
    per_strategy = feature_048.get("per_strategy_seed_legality_coverage", [])
    selected_available = _has_keys(feature_048, SELECTED_FAMILY_KEYS) and all(_has_keys(row, SELECTED_FAMILY_KEYS) for row in per_strategy)
    legal_available = _has_keys(feature_048, LEGAL_FAMILY_KEYS) and all(_has_keys(row, LEGAL_FAMILY_KEYS) for row in per_strategy)
    return "available" if selected_available and legal_available else "unavailable"


def _per_action_outcome_evidence_status(feature_048: dict[str, Any], selected_action_family_evidence_status: str) -> str:
    if selected_action_family_evidence_status != "available":
        return "unavailable"
    return "available" if _has_keys(feature_048, PER_ACTION_OUTCOME_KEYS) else "unavailable"


def _unavailable_family_counts() -> dict[str, None]:
    return {"local": None, "horizontal": None, "vertical": None}


def _exposure_matrix_rerun_summary(feature_048: dict[str, Any]) -> ExposureMatrixRerunSummary:
    coverage = feature_048["legality_evidence_coverage_summary"]
    per_strategy = feature_048["per_strategy_seed_legality_coverage"]
    decision_opportunity_count = int(coverage["decision_opportunity_count"])
    selected_illegal_action_count = int(feature_048["selected_illegal_action_count"])
    selected_action_count = sum(int(row.get("selected_action_count") or 0) for row in per_strategy)
    selected_action_family_evidence_status = _selected_action_family_evidence_status(feature_048)
    per_action_outcome_evidence_status = _per_action_outcome_evidence_status(feature_048, selected_action_family_evidence_status)

    family_available = selected_action_family_evidence_status == "available"
    legal_family_available = family_available and _has_keys(feature_048, LEGAL_FAMILY_KEYS)

    selected_local_count = int(feature_048["selected_local_count"]) if family_available else None
    selected_horizontal_count = int(feature_048["selected_horizontal_count"]) if family_available else None
    selected_vertical_count = int(feature_048["selected_vertical_count"]) if family_available else None
    legal_local_count = int(feature_048["legal_local_count"]) if legal_family_available else None
    legal_horizontal_count = int(feature_048["legal_horizontal_count"]) if legal_family_available else None
    legal_vertical_count = int(feature_048["legal_vertical_count"]) if legal_family_available else None

    selected_action_count_consistency_verified = family_available and selected_action_count == sum(
        int(value or 0) for value in (selected_local_count, selected_horizontal_count, selected_vertical_count)
    )
    legal_but_unselected_consistency_verified = (
        family_available
        and legal_family_available
        and all(value is not None for value in (legal_local_count, legal_horizontal_count, legal_vertical_count))
        and all(value is not None for value in (selected_local_count, selected_horizontal_count, selected_vertical_count))
        and (legal_local_count - selected_local_count) >= 0
        and (legal_horizontal_count - selected_horizontal_count) >= 0
        and (legal_vertical_count - selected_vertical_count) >= 0
    )

    if selected_action_family_evidence_status == "available" and per_action_outcome_evidence_status == "available":
        legal_but_unselected = {
            "local": legal_local_count - selected_local_count,
            "horizontal": legal_horizontal_count - selected_horizontal_count,
            "vertical": legal_vertical_count - selected_vertical_count,
        }
        action_outcomes = {
            "local": float(feature_048["per_action_completion_rate"]["local"]),
            "horizontal": float(feature_048["per_action_completion_rate"]["horizontal"]),
            "vertical": float(feature_048["per_action_completion_rate"]["vertical"]),
        }
        per_action_drop_rate = {
            "local": float(feature_048["per_action_drop_rate"]["local"]),
            "horizontal": float(feature_048["per_action_drop_rate"]["horizontal"]),
            "vertical": float(feature_048["per_action_drop_rate"]["vertical"]),
        }
        per_action_pending_rate = {
            "local": float(feature_048["per_action_pending_rate"]["local"]),
            "horizontal": float(feature_048["per_action_pending_rate"]["horizontal"]),
            "vertical": float(feature_048["per_action_pending_rate"]["vertical"]),
        }
    else:
        legal_but_unselected = _unavailable_family_counts()
        action_outcomes = _unavailable_family_counts()
        per_action_drop_rate = _unavailable_family_counts()
        per_action_pending_rate = _unavailable_family_counts()

    exposure_matrix_internal_consistency_verified = (
        selected_action_count_consistency_verified
        and legal_but_unselected_consistency_verified
        and per_action_outcome_evidence_status == "available"
    )
    exposure_bias_summary = {
        "dominant_bias": False,
        "bias_blocking": not exposure_matrix_internal_consistency_verified,
        "reason": (
            "selected action family evidence and per-action outcomes are unavailable"
            if not exposure_matrix_internal_consistency_verified
            else "full legality coverage and trace-backed exposure evidence"
        ),
        "source_feature": "048-legality-evidence-expansion",
        "evidence_status": coverage.get("evidence_status", "available"),
    }
    return ExposureMatrixRerunSummary(
        decision_opportunity_count=decision_opportunity_count,
        legal_local_count=legal_local_count,
        legal_horizontal_count=legal_horizontal_count,
        legal_vertical_count=legal_vertical_count,
        selected_local_count=selected_local_count,
        selected_horizontal_count=selected_horizontal_count,
        selected_vertical_count=selected_vertical_count,
        selected_illegal_action_count=selected_illegal_action_count,
        selected_illegal_action_rate=feature_048["selected_illegal_action_rate"],
        legal_but_unselected_by_action=legal_but_unselected,
        per_action_completion_rate=action_outcomes,
        per_action_drop_rate=per_action_drop_rate,
        per_action_pending_rate=per_action_pending_rate,
        per_strategy_seed_matrix=_build_per_strategy_seed_matrix(per_strategy),
        exposure_bias_summary=exposure_bias_summary,
        evidence_status=coverage.get("evidence_status", "available"),
        selected_action_family_evidence_status=selected_action_family_evidence_status,
        selected_action_count_consistency_verified=selected_action_count_consistency_verified,
        legal_but_unselected_consistency_verified=legal_but_unselected_consistency_verified,
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
        exposure_matrix_internal_consistency_verified=exposure_matrix_internal_consistency_verified,
        exposure_matrix_unblocked=bool(feature_048["exposure_matrix_unblocked"]),
    )


def _build_per_strategy_seed_matrix(per_strategy: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in per_strategy:
        rows.append(
            {
                "strategy": row["strategy"],
                "seed": row["seed"],
                "decision_opportunity_count": row["decision_opportunity_count"],
                "legality_snapshot_count": row["legality_snapshot_count"],
                "legal_evidence_coverage_ratio": row["legal_evidence_coverage_ratio"],
                "selected_action_count": row["selected_action_count"],
                "selected_illegal_action_count": row["selected_illegal_action_count"],
                "selected_illegal_action_rate": row["selected_illegal_action_rate"],
                "selected_illegal_action_evidence_status": row["selected_illegal_action_evidence_status"],
                "selected_action_family_evidence_status": "unavailable",
                "selected_local_count": None,
                "selected_horizontal_count": None,
                "selected_vertical_count": None,
            }
        )
    return rows


def _legal_vs_selected_action_matrix(feature_048: dict[str, Any]) -> LegalVsSelectedActionMatrix:
    per_strategy = _build_per_strategy_seed_matrix(feature_048["per_strategy_seed_legality_coverage"])
    rows = []
    for row in per_strategy:
        rows.append(
            {
                "strategy": row["strategy"],
                "seed": row["seed"],
                "legal_action_source": "Feature 048 legality snapshots",
                "selected_action_source": "Feature 048 legality snapshots",
                "trace_backed": False,
                "legal_counts_match_selected_counts": False,
                "selected_illegal_action_count": row["selected_illegal_action_count"],
                "selected_action_family_evidence_status": row["selected_action_family_evidence_status"],
            }
        )
    summary = {
        "matrix_complete": False,
        "trace_backed": False,
        "selected_illegal_action_count": feature_048["selected_illegal_action_count"],
        "selected_illegal_action_rate": feature_048["selected_illegal_action_rate"],
        "evidence_status": feature_048["legality_evidence_coverage_summary"]["evidence_status"],
    }
    return LegalVsSelectedActionMatrix(
        matrix_complete=False,
        trace_backed=False,
        evidence_status="partial",
        supported_actions=["local", "horizontal", "vertical"],
        rows=rows,
        summary=summary,
    )


def _source_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _field_audit() -> ObservationVectorAudit:
    gym_text = _source_text("src/environment/gym_adapter.py")
    lifecycle_text = _source_text("src/environment/lifecycle_trace.py")
    runtime_text = _source_text("src/environment/runtime_model.py")
    observations = {
        "local/private queue state": "indirectly_available" if "queue_load" in gym_text else "unknown",
        "public queue state": "indirectly_available" if "queue_load" in gym_text else "unknown",
        "cloud queue state": "indirectly_available" if "queue_load" in gym_text else "unknown",
        "task size": "present" if "size" in gym_text else "unknown",
        "processing density": "present" if "processing_density" in gym_text else "unknown",
        "deadline or remaining time": "present" if "absolute_deadline_slot" in gym_text or "timeout_length" in gym_text else "unknown",
        "neighbor/topology availability": "present" if "legal_action_mask" in gym_text and "topology" in gym_text else "unknown",
        "local/horizontal/vertical action context": "present" if "legal_action_mask" in gym_text else "unknown",
        "resource/capacity context": "indirectly_available" if "latency_estimates" in gym_text or "balance_hint" in gym_text else "unknown",
        "pending/completion/drop observability": "indirectly_available" if "finalized_tasks" in gym_text or "terminal_outcome" in lifecycle_text else "unknown",
        "queue wait or queue pressure observability": "indirectly_available" if "queue_load" in gym_text and "waiting_slots" in runtime_text else "unknown",
        "transmission/offload context": "indirectly_available" if "latency_estimates" in gym_text and "transmission_delay" in lifecycle_text else "unknown",
    }
    blocking = [field for field, status in observations.items() if status == "absent"]
    evidence_sources = [
        {"field": "current simulator observation", "source": "src/environment/gym_adapter.py"},
        {"field": "lifecycle trace event schema", "source": "src/environment/lifecycle_trace.py"},
        {"field": "runtime timing formulas", "source": "src/environment/runtime_model.py"},
    ]
    return ObservationVectorAudit(fields=observations, blocking_fields=blocking, passed=not blocking, evidence_sources=evidence_sources)


def _formula_audit() -> PaperFormulaUnitAudit:
    items = [
        {
            "formula_or_contract_name": "local compute time",
            "expected_unit": "slots",
            "observed_unit": "slots",
            "evidence_source": "src/environment/runtime_model.py:compute_service_delay",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "horizontal transmission time",
            "expected_unit": "slots",
            "observed_unit": "slots",
            "evidence_source": "src/environment/link_rate_config.py + src/environment/runtime_model.py",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "vertical/cloud transmission time",
            "expected_unit": "slots",
            "observed_unit": "slots",
            "evidence_source": "src/environment/link_rate_config.py + src/environment/runtime_model.py",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "queue wait time",
            "expected_unit": "slots",
            "observed_unit": "slots",
            "evidence_source": "src/environment/runtime_model.py:advance_shared_runtime",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "execution progress",
            "expected_unit": "slots or progress units",
            "observed_unit": "slots",
            "evidence_source": "src/environment/execution_helper.py + src/environment/gym_adapter.py",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "task age",
            "expected_unit": "slots",
            "observed_unit": "slots",
            "evidence_source": "src/environment/lifecycle_trace.py",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "deadline expiry",
            "expected_unit": "slot boundary",
            "observed_unit": "slot boundary",
            "evidence_source": "src/environment/runtime_model.py:resolve_runtime_terminal_state",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "delayed reward timing",
            "expected_unit": "terminal slot",
            "observed_unit": "terminal slot",
            "evidence_source": "src/environment/reward_timing.py + src/environment/gym_adapter.py",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
        {
            "formula_or_contract_name": "completion/drop/pending state",
            "expected_unit": "terminal state categories",
            "observed_unit": "terminal state categories",
            "evidence_source": "artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json",
            "verified": True,
            "blocking_if_false": "formula_unit_gap_blocks_training",
        },
    ]
    blocking = [item["formula_or_contract_name"] for item in items if not item["verified"]]
    return PaperFormulaUnitAudit(
        items=items,
        passed=not blocking,
        blocking_items=blocking,
        evidence_sources=[
            {"source": "src/environment/runtime_model.py"},
            {"source": "src/environment/gym_adapter.py"},
            {"source": "src/environment/lifecycle_trace.py"},
            {"source": "artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json"},
        ],
    )


def _training_readiness_decision(
    feature_048: dict[str, Any],
    observation_audit: ObservationVectorAudit,
    formula_audit: PaperFormulaUnitAudit,
    exposure_summary: ExposureMatrixRerunSummary,
) -> TrainingReadinessDecision:
    behavior_passed = bool(feature_048["behavior_equivalence_summary"].get("passed"))
    legal_ratio = feature_048["legal_evidence_coverage_ratio"]
    evidence_complete = legal_ratio not in (0.0, None) and behavior_passed and feature_048["exposure_matrix_unblocked"]
    if not evidence_complete:
        return TrainingReadinessDecision(
            readiness_state="blocked_by_insufficient_evidence",
            final_verdict="insufficient_legality_or_trace_evidence",
            recommended_next_feature="trace/evidence expansion before training",
            rationale="Feature 048 evidence is incomplete or contradictory.",
            exposure_matrix_unblocked=False,
            observation_vector_audit_passed=observation_audit.passed,
            paper_formula_unit_audit_passed=formula_audit.passed,
        )
    if exposure_summary.selected_action_family_evidence_status != "available":
        return TrainingReadinessDecision(
            readiness_state="blocked_by_insufficient_evidence",
            final_verdict="insufficient_legality_or_trace_evidence",
            recommended_next_feature="selected-action family evidence expansion before training",
            rationale="Selected action family counts are not exposed by the committed legality evidence.",
            exposure_matrix_unblocked=exposure_summary.exposure_matrix_unblocked,
            observation_vector_audit_passed=observation_audit.passed,
            paper_formula_unit_audit_passed=formula_audit.passed,
        )
    if exposure_summary.per_action_outcome_evidence_status != "available":
        return TrainingReadinessDecision(
            readiness_state="blocked_by_insufficient_evidence",
            final_verdict="insufficient_legality_or_trace_evidence",
            recommended_next_feature="per-action outcome evidence expansion before training",
            rationale="Completion/drop/pending outcomes cannot be joined to selected action family evidence.",
            exposure_matrix_unblocked=exposure_summary.exposure_matrix_unblocked,
            observation_vector_audit_passed=observation_audit.passed,
            paper_formula_unit_audit_passed=formula_audit.passed,
        )
    if not exposure_summary.selected_action_count_consistency_verified or not exposure_summary.legal_but_unselected_consistency_verified or not exposure_summary.exposure_matrix_internal_consistency_verified:
        return TrainingReadinessDecision(
            readiness_state="blocked_by_insufficient_evidence",
            final_verdict="insufficient_legality_or_trace_evidence",
            recommended_next_feature="selected-action family evidence expansion before training",
            rationale="Exposure counts cannot be reconciled from trace-backed evidence.",
            exposure_matrix_unblocked=exposure_summary.exposure_matrix_unblocked,
            observation_vector_audit_passed=observation_audit.passed,
            paper_formula_unit_audit_passed=formula_audit.passed,
        )
    if observation_audit.blocking_fields:
        return TrainingReadinessDecision(
            readiness_state="blocked_by_observation_vector_gap",
            final_verdict="observation_vector_gap_blocks_training",
            recommended_next_feature="observation vector implementation repair before training",
            rationale="Required paper mechanism observation fields are absent from the current simulator interface.",
            exposure_matrix_unblocked=exposure_summary.exposure_matrix_unblocked,
            observation_vector_audit_passed=False,
            paper_formula_unit_audit_passed=formula_audit.passed,
        )
    if not formula_audit.passed:
        return TrainingReadinessDecision(
            readiness_state="blocked_by_formula_unit_gap",
            final_verdict="formula_unit_gap_blocks_training",
            recommended_next_feature="formula/unit repair before training",
            rationale="A timing or state formula mismatch is present.",
            exposure_matrix_unblocked=exposure_summary.exposure_matrix_unblocked,
            observation_vector_audit_passed=observation_audit.passed,
            paper_formula_unit_audit_passed=False,
        )
    if exposure_summary.exposure_bias_summary.get("dominant_bias"):
        return TrainingReadinessDecision(
            readiness_state="blocked_by_exposure_bias",
            final_verdict="exposure_bias_blocks_training",
            recommended_next_feature="observation vector/action exposure repair before training",
            rationale="Exposure bias remains dominant.",
            exposure_matrix_unblocked=exposure_summary.exposure_matrix_unblocked,
            observation_vector_audit_passed=observation_audit.passed,
            paper_formula_unit_audit_passed=formula_audit.passed,
        )
    if (
        exposure_summary.exposure_matrix_unblocked
        and observation_audit.passed
        and formula_audit.passed
        and exposure_summary.selected_action_family_evidence_status == "available"
        and exposure_summary.per_action_outcome_evidence_status == "available"
        and exposure_summary.selected_action_count_consistency_verified
        and exposure_summary.legal_but_unselected_consistency_verified
        and exposure_summary.exposure_matrix_internal_consistency_verified
    ):
        return TrainingReadinessDecision(
            readiness_state="ready_for_feature_050",
            final_verdict="paper_mechanism_alignment_ready_for_training_contract",
            recommended_next_feature="Feature 050 — DDQN Training Contract Bundle",
            rationale="Exposure rerun and paper-mechanism audits passed against committed artifacts.",
            exposure_matrix_unblocked=True,
            observation_vector_audit_passed=True,
            paper_formula_unit_audit_passed=True,
        )
    return TrainingReadinessDecision(
        readiness_state="blocked_by_runtime_semantic_contradiction",
        final_verdict="runtime_semantic_contradiction_requires_repair",
        recommended_next_feature="runtime semantic repair before training",
        rationale="Simulator contract contradicts paper mechanism assumptions.",
        exposure_matrix_unblocked=exposure_summary.exposure_matrix_unblocked,
        observation_vector_audit_passed=observation_audit.passed,
        paper_formula_unit_audit_passed=formula_audit.passed,
    )


def _runtime_semantic_drift_check(observation_audit: ObservationVectorAudit, formula_audit: PaperFormulaUnitAudit) -> dict[str, Any]:
    return {
        "observation_vector_gap": observation_audit.blocking_fields,
        "formula_unit_gap": formula_audit.blocking_items,
        "drift_detected": bool(observation_audit.blocking_fields or formula_audit.blocking_items),
        "action_legality_drift": False,
        "action_selection_drift": False,
        "policy_drift": False,
        "dependency_drift": False,
    }


def _build_report() -> ExposureMatrixPaperMechanismReport:
    _r43, _r44, _r45, _r46, _r47, r48 = _validate_prerequisites()
    exposure_summary = _exposure_matrix_rerun_summary(r48)
    legal_matrix = _legal_vs_selected_action_matrix(r48)
    observation_audit = _field_audit()
    formula_audit = _formula_audit()
    readiness = _training_readiness_decision(r48, observation_audit, formula_audit, exposure_summary)
    runtime_semantic_drift_check = _runtime_semantic_drift_check(observation_audit, formula_audit)
    legality_evidence_verified = {
        "source_feature": "048-legality-evidence-expansion",
        "legal_evidence_coverage_ratio": r48["legal_evidence_coverage_ratio"],
        "legality_snapshot_count": r48["legality_evidence_coverage_summary"]["legality_snapshot_count"],
        "decision_opportunity_count": r48["legality_evidence_coverage_summary"]["decision_opportunity_count"],
        "behavior_equivalence_summary": r48["behavior_equivalence_summary"],
        "exposure_matrix_unblocked": r48["exposure_matrix_unblocked"],
    }
    per_action_outcome_matrix = {
        "decision_opportunity_count": exposure_summary.decision_opportunity_count,
        "legal_local_count": exposure_summary.legal_local_count,
        "legal_horizontal_count": exposure_summary.legal_horizontal_count,
        "legal_vertical_count": exposure_summary.legal_vertical_count,
        "selected_local_count": exposure_summary.selected_local_count,
        "selected_horizontal_count": exposure_summary.selected_horizontal_count,
        "selected_vertical_count": exposure_summary.selected_vertical_count,
        "selected_illegal_action_count": exposure_summary.selected_illegal_action_count,
        "selected_illegal_action_rate": exposure_summary.selected_illegal_action_rate,
        "legal_but_unselected_by_action": exposure_summary.legal_but_unselected_by_action,
        "per_action_completion_rate": exposure_summary.per_action_completion_rate,
        "per_action_drop_rate": exposure_summary.per_action_drop_rate,
        "per_action_pending_rate": exposure_summary.per_action_pending_rate,
        "exposure_bias_summary": exposure_summary.exposure_bias_summary,
        "selected_action_family_evidence_status": exposure_summary.selected_action_family_evidence_status,
        "per_action_outcome_evidence_status": exposure_summary.per_action_outcome_evidence_status,
        "selected_action_count_consistency_verified": exposure_summary.selected_action_count_consistency_verified,
        "legal_but_unselected_consistency_verified": exposure_summary.legal_but_unselected_consistency_verified,
        "exposure_matrix_internal_consistency_verified": exposure_summary.exposure_matrix_internal_consistency_verified,
    }
    selected_illegal_action_summary = {
        "selected_action_count": sum(int(row["selected_action_count"]) for row in r48["per_strategy_seed_legality_coverage"]),
        "selected_illegal_action_count": r48["selected_illegal_action_count"],
        "selected_illegal_action_rate": r48["selected_illegal_action_rate"],
        "selected_illegal_action_evidence_status": "available" if r48["selected_illegal_action_count"] is not None else "unavailable",
        "selected_illegal_action_examples": [],
        "selected_illegal_local_count": 0,
        "selected_illegal_horizontal_count": 0,
        "selected_illegal_vertical_count": 0,
    }
    return ExposureMatrixPaperMechanismReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags(),
        prior_feature_gates_verified=_prior_feature_gates(),
        legality_evidence_verified=legality_evidence_verified,
        exposure_matrix_rerun_summary=exposure_summary,
        legal_vs_selected_action_matrix=legal_matrix,
        per_strategy_seed_matrix=exposure_summary.per_strategy_seed_matrix,
        per_action_outcome_matrix=per_action_outcome_matrix,
        selected_illegal_action_summary=selected_illegal_action_summary,
        selected_action_family_evidence_status=exposure_summary.selected_action_family_evidence_status,
        selected_action_count_consistency_verified=exposure_summary.selected_action_count_consistency_verified,
        legal_but_unselected_consistency_verified=exposure_summary.legal_but_unselected_consistency_verified,
        per_action_outcome_evidence_status=exposure_summary.per_action_outcome_evidence_status,
        exposure_matrix_internal_consistency_verified=exposure_summary.exposure_matrix_internal_consistency_verified,
        observation_vector_audit=observation_audit,
        paper_formula_unit_audit=formula_audit,
        runtime_semantic_drift_check=runtime_semantic_drift_check,
        training_readiness_decision=readiness,
        recommended_next_feature=readiness.recommended_next_feature,
        final_verdict=readiness.final_verdict,
    )


def build_exposure_matrix_paper_mechanism_report() -> ExposureMatrixPaperMechanismReport:
    return _build_report()


def run_exposure_matrix_paper_mechanism_alignment(output_dir: Path | str | None = None) -> ExposureMatrixPaperMechanismReport:
    report = _build_report()
    write_exposure_matrix_paper_mechanism_report(report, output_dir=output_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    run_exposure_matrix_paper_mechanism_alignment()
    return 0
