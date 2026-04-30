from __future__ import annotations

from dataclasses import dataclass, field

from .validation_runner import ValidationRunResult


@dataclass(slots=True)
class PolicyComparison:
    policy_name: str
    baseline_policy_name: str
    per_trace: list[dict[str, object]] = field(default_factory=list)
    aggregate: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ComparisonRunner:
    validation_result: ValidationRunResult

    def run(self) -> dict[str, object]:
        if not self.validation_result.policy_results:
            return {
                "baseline_policy_name": self.validation_result.baseline_policy_name,
                "policy_order": self.validation_result.policy_order,
                "comparisons": [],
            }
        baseline = next(
            (result for result in self.validation_result.policy_results if result.policy_name == self.validation_result.baseline_policy_name),
            self.validation_result.policy_results[0],
        )
        comparisons: list[PolicyComparison] = []
        for policy_result in self.validation_result.policy_results[1:]:
            comparisons.append(
                PolicyComparison(
                    policy_name=policy_result.policy_name,
                    baseline_policy_name=baseline.policy_name,
                    per_trace=list(policy_result.trace_results["per_trace"]),
                    aggregate=dict(policy_result.trace_results["aggregate"]),
                )
            )
        return {
            "baseline_policy_name": baseline.policy_name,
            "policy_order": self.validation_result.policy_order,
            "comparisons": [
                {
                    "policy_name": comparison.policy_name,
                    "baseline_policy_name": comparison.baseline_policy_name,
                    "per_trace": comparison.per_trace,
                    "aggregate": comparison.aggregate,
                }
                for comparison in comparisons
            ],
        }
