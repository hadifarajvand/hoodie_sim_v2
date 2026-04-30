from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from .analysis_runner import AnalysisRunResult


@dataclass(slots=True)
class PlotBuilder:
    analysis_result: AnalysisRunResult

    def build_payload(self) -> dict[str, object]:
        return {
            "baseline_policy_name": self.analysis_result.baseline_policy_name,
            "policy_order": self.analysis_result.policy_order,
            "plots": {
                "average_delay": self._extract_metric("average_delay"),
                "drop_ratio": self._extract_metric("drop_ratio"),
                "throughput": self._extract_metric("throughput"),
            },
        }

    def _extract_metric(self, metric_name: str) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        baseline = self.analysis_result.baseline["trace_results"]["per_trace"]
        for row in baseline:
            rows.append(
                {
                    "policy_name": self.analysis_result.baseline["policy_name"],
                    "trace_id": row["trace_id"],
                    "seed": row["seed"],
                    metric_name: row[metric_name],
                }
            )
        for policy in self.analysis_result.compared_policies:
            for row in policy.trace_results["per_trace"]:
                rows.append(
                    {
                        "policy_name": policy.policy_name,
                        "trace_id": row["trace_id"],
                        "seed": row["seed"],
                        metric_name: row[metric_name],
                    }
                )
        return rows

    def to_json(self) -> str:
        return json.dumps(self.build_payload(), sort_keys=True)

    def save_json(self, output_path: Path) -> Path:
        output_path.write_text(self.to_json(), encoding="utf-8")
        return output_path
