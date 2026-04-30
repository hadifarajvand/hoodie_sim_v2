from __future__ import annotations

from dataclasses import asdict, dataclass

from .analysis_runner import AnalysisRunResult


@dataclass(slots=True)
class ReportBuilder:
    analysis_result: AnalysisRunResult

    def to_dict(self) -> dict[str, object]:
        return {
            "baseline_policy_name": self.analysis_result.baseline_policy_name,
            "policy_order": self.analysis_result.policy_order,
            "baseline": self.analysis_result.baseline,
            "compared_policies": [asdict(policy) for policy in self.analysis_result.compared_policies],
        }

    def to_table_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        rows.append(
            {
                "role": "baseline",
                "policy_name": self.analysis_result.baseline["policy_name"],
                "aggregate": self.analysis_result.baseline["trace_results"]["aggregate"],
            }
        )
        for policy in self.analysis_result.compared_policies:
            rows.append(
                {
                    "role": "compared",
                    "policy_name": policy.policy_name,
                    "aggregate": policy.trace_results["aggregate"],
                }
            )
        return rows
