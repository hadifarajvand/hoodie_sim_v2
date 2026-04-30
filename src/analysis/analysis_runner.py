from __future__ import annotations

from dataclasses import dataclass, field

from src.evaluation.validation_artifacts import ValidationArtifacts


@dataclass(slots=True)
class AnalysisPolicyResult:
    policy_name: str
    trace_results: dict[str, object]


@dataclass(slots=True)
class AnalysisRunResult:
    baseline_policy_name: str
    policy_order: tuple[str, ...]
    baseline: dict[str, object]
    compared_policies: list[AnalysisPolicyResult] = field(default_factory=list)


@dataclass(slots=True)
class AnalysisRunner:
    validation_artifacts: ValidationArtifacts | dict[str, object]

    def _as_dict(self) -> dict[str, object]:
        if isinstance(self.validation_artifacts, ValidationArtifacts):
            return self.validation_artifacts.to_dict()
        return self.validation_artifacts

    def run(self) -> AnalysisRunResult:
        payload = self._as_dict()
        baseline = payload["policy_results"]["baseline"]
        compared = payload["policy_results"]["compared_policies"]
        return AnalysisRunResult(
            baseline_policy_name=payload["baseline_policy_name"],
            policy_order=tuple(payload["policy_order"]),
            baseline=baseline,
            compared_policies=[
                AnalysisPolicyResult(policy_name=policy["policy_name"], trace_results=policy["trace_results"])
                for policy in compared
            ],
        )
