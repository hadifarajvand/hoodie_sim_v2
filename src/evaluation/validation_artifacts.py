from __future__ import annotations

from dataclasses import dataclass

from .comparison_runner import ComparisonRunner
from .validation_runner import ValidationRunResult


@dataclass(slots=True)
class ValidationArtifacts:
    validation: ValidationRunResult
    comparison: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        baseline_policy_name = self.validation.baseline_policy_name
        grouped_policies = {
            "baseline": next(
                (
                    {
                        "policy_name": result.policy_name,
                        "trace_results": result.trace_results,
                    }
                    for result in self.validation.policy_results
                    if result.policy_name == baseline_policy_name
                ),
                None,
            ),
            "compared_policies": [
                {
                    "policy_name": result.policy_name,
                    "trace_results": result.trace_results,
                }
                for result in self.validation.policy_results
                if result.policy_name != baseline_policy_name
            ],
        }
        return {
            "evaluation_config_snapshot": self.validation.config_snapshot,
            "evaluation_config_hash": self.validation.config_hash,
            "baseline_policy_name": baseline_policy_name,
            "policy_order": self.validation.policy_order,
            "policy_results": {
                "baseline": grouped_policies["baseline"],
                "compared_policies": grouped_policies["compared_policies"],
            },
            "comparison": self.comparison,
        }


def build_validation_artifacts(validation_result: ValidationRunResult) -> ValidationArtifacts:
    comparison = ComparisonRunner(validation_result).run()
    return ValidationArtifacts(validation=validation_result, comparison=comparison)
