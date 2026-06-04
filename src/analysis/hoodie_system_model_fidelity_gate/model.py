from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import ACTIVE_POLICIES, FEATURE_ID, INVALID_LABELS, READY_STATUS, REQUIRED_MECHANISM_IDS, REQUIRED_METRICS


ALLOWED_MECHANISM_STATUSES = ("exact", "approximate_documented", "missing", "wrong", "not_exercised")
ALLOWED_METRIC_CLASSIFICATIONS = (
    "paper_primary_metric",
    "paper_secondary_or_derived_metric",
    "paper_secondary_or_repository_metric",
    "repository_diagnostic_metric",
    "not_for_paper_comparison",
)


def _non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True, slots=True)
class MechanismCoverageRow:
    mechanism_id: str
    paper_expectation: str
    simulator_behavior: str
    code_location: str
    test_artifact_evidence: str
    status: str
    required_fix_or_claim_boundary: str

    def __post_init__(self) -> None:
        if self.mechanism_id not in REQUIRED_MECHANISM_IDS:
            raise ValueError(f"unknown mechanism_id: {self.mechanism_id}")
        if self.status not in ALLOWED_MECHANISM_STATUSES:
            raise ValueError("status must be an allowed mechanism status")
        for name, value in (
            ("paper_expectation", self.paper_expectation),
            ("simulator_behavior", self.simulator_behavior),
            ("code_location", self.code_location),
            ("test_artifact_evidence", self.test_artifact_evidence),
            ("required_fix_or_claim_boundary", self.required_fix_or_claim_boundary),
        ):
            if not _non_empty(value):
                raise ValueError(f"{name} must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SystemModelGapRow:
    mechanism_id: str
    paper_expectation: str
    simulator_behavior: str
    code_location: str
    test_artifact_evidence: str
    status: str
    required_fix_or_claim_boundary: str

    def __post_init__(self) -> None:
        if self.mechanism_id not in REQUIRED_MECHANISM_IDS:
            raise ValueError(f"unknown mechanism_id: {self.mechanism_id}")
        if self.status not in ALLOWED_MECHANISM_STATUSES:
            raise ValueError("status must be an allowed mechanism status")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MetricReadinessRow:
    metric: str
    classification: str
    paper_use: str
    status: str
    evidence: str

    def __post_init__(self) -> None:
        if self.metric not in REQUIRED_METRICS:
            raise ValueError(f"unknown metric: {self.metric}")
        if self.classification not in ALLOWED_METRIC_CLASSIFICATIONS:
            raise ValueError("classification must be one of the allowed metric classifications")
        for name, value in (("paper_use", self.paper_use), ("status", self.status), ("evidence", self.evidence)):
            if not _non_empty(value):
                raise ValueError(f"{name} must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScenarioMechanismCoverageRow:
    scenario: str
    workload: str
    deadline_pressure: str
    exercised_mechanisms: tuple[str, ...]
    status: str
    evidence: str

    def __post_init__(self) -> None:
        if not _non_empty(self.scenario):
            raise ValueError("scenario must be non-empty")
        if not _non_empty(self.workload):
            raise ValueError("workload must be non-empty")
        if not _non_empty(self.deadline_pressure):
            raise ValueError("deadline_pressure must be non-empty")
        if not self.exercised_mechanisms:
            raise ValueError("exercised_mechanisms must be non-empty")
        if self.status not in ALLOWED_MECHANISM_STATUSES:
            raise ValueError("status must be an allowed mechanism status")
        if not _non_empty(self.evidence):
            raise ValueError("evidence must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["exercised_mechanisms"] = list(self.exercised_mechanisms)
        return payload


@dataclass(frozen=True, slots=True)
class HoodieMleoTieEvidence:
    source_artifact_dir: str
    matching_rows: int
    differing_rows: int
    identical_scenarios: tuple[str, ...]
    divergent_scenarios: tuple[str, ...]
    divergent_action_counts: dict[str, dict[str, int]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_artifact_dir": self.source_artifact_dir,
            "matching_rows": self.matching_rows,
            "differing_rows": self.differing_rows,
            "identical_scenarios": list(self.identical_scenarios),
            "divergent_scenarios": list(self.divergent_scenarios),
            "divergent_action_counts": self.divergent_action_counts,
        }


@dataclass(frozen=True, slots=True)
class Feature086Report:
    feature_id: str
    status: str
    passed: bool
    verdict: str
    active_policies: tuple[str, ...]
    invalid_label_check: tuple[str, ...]
    mechanism_coverage: tuple[MechanismCoverageRow, ...]
    system_model_gap_matrix: tuple[SystemModelGapRow, ...]
    metric_readiness_matrix: tuple[MetricReadinessRow, ...]
    scenario_mechanism_coverage: tuple[ScenarioMechanismCoverageRow, ...]
    hoodie_mleo_tie_evidence: HoodieMleoTieEvidence
    claim_boundary: tuple[str, ...]
    scope_proof: tuple[str, ...]
    blocked_mechanisms: tuple[str, ...]
    remaining_approximations: tuple[str, ...]
    allowed_paper_comparison_metrics: tuple[str, ...]
    repository_diagnostic_metrics: tuple[str, ...]
    output_comparison_ready: bool

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must match Feature 086")
        if self.status not in {READY_STATUS, "system_model_fidelity_blocked"}:
            raise ValueError("status must be explicit and recognized")
        if self.verdict not in {READY_STATUS, "system_model_fidelity_blocked"}:
            raise ValueError("verdict must be explicit and recognized")
        if tuple(self.active_policies) != ACTIVE_POLICIES:
            raise ValueError("active_policies must be the required paper set")
        if not self.invalid_label_check:
            raise ValueError("invalid_label_check must be populated")
        invalid_joined = " ".join(self.invalid_label_check)
        if any(label in invalid_joined for label in INVALID_LABELS):
            raise ValueError("invalid_label_check must not expose legacy active labels")
        if not self.mechanism_coverage:
            raise ValueError("mechanism_coverage must be non-empty")
        if not self.system_model_gap_matrix:
            raise ValueError("system_model_gap_matrix must be non-empty")
        if not self.metric_readiness_matrix:
            raise ValueError("metric_readiness_matrix must be non-empty")
        if not self.scenario_mechanism_coverage:
            raise ValueError("scenario_mechanism_coverage must be non-empty")
        if not self.hoodie_mleo_tie_evidence.identical_scenarios:
            raise ValueError("hoodie_mleo_tie_evidence must include scenario evidence")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")
        if not self.scope_proof:
            raise ValueError("scope_proof must be non-empty")
        if not self.allowed_paper_comparison_metrics:
            raise ValueError("allowed_paper_comparison_metrics must be non-empty")
        if not self.repository_diagnostic_metrics:
            raise ValueError("repository_diagnostic_metrics must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "status": self.status,
            "passed": self.passed,
            "verdict": self.verdict,
            "active_policies": list(self.active_policies),
            "invalid_label_check": list(self.invalid_label_check),
            "mechanism_coverage": [row.to_dict() for row in self.mechanism_coverage],
            "system_model_gap_matrix": [row.to_dict() for row in self.system_model_gap_matrix],
            "metric_readiness_matrix": [row.to_dict() for row in self.metric_readiness_matrix],
            "scenario_mechanism_coverage": [row.to_dict() for row in self.scenario_mechanism_coverage],
            "hoodie_mleo_tie_evidence": self.hoodie_mleo_tie_evidence.to_dict(),
            "claim_boundary": list(self.claim_boundary),
            "scope_proof": list(self.scope_proof),
            "blocked_mechanisms": list(self.blocked_mechanisms),
            "remaining_approximations": list(self.remaining_approximations),
            "allowed_paper_comparison_metrics": list(self.allowed_paper_comparison_metrics),
            "repository_diagnostic_metrics": list(self.repository_diagnostic_metrics),
            "output_comparison_ready": self.output_comparison_ready,
        }

