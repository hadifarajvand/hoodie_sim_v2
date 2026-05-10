from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
from typing import Any


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/baseline-fairness-rebuild")
JSON_FILENAME = "baseline-fairness-rebuild.json"
MARKDOWN_FILENAME = "baseline-fairness-rebuild.md"
CSV_FILENAME = "baseline-fairness-rebuild.csv"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(slots=True)
class BaselineFairnessRebuildReport:
    metadata: dict[str, Any]
    source_gate_status: dict[str, Any]
    baseline_policies_included: list[str]
    scenarios_traces_used: list[dict[str, Any]]
    fairness_controls: dict[str, Any]
    metrics_reused: list[str]
    collapse_indicators: list[dict[str, Any]]
    anti_collapse_assessment: dict[str, Any]
    unchanged_collapse_explanation: str
    limitations: list[str]
    no_training_disclaimer: str
    no_policy_redesign_disclaimer: str
    no_paper_validity_disclaimer: str
    reproducibility_details: dict[str, Any]
    overall_status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "metadata": dict(self.metadata),
            "source_gate_status": dict(self.source_gate_status),
            "baseline_policies_included": list(self.baseline_policies_included),
            "scenarios_traces_used": list(self.scenarios_traces_used),
            "fairness_controls": dict(self.fairness_controls),
            "metrics_reused": list(self.metrics_reused),
            "collapse_indicators": list(self.collapse_indicators),
            "anti_collapse_assessment": dict(self.anti_collapse_assessment),
            "unchanged_collapse_explanation": self.unchanged_collapse_explanation,
            "limitations": list(self.limitations),
            "no_training_disclaimer": self.no_training_disclaimer,
            "no_policy_redesign_disclaimer": self.no_policy_redesign_disclaimer,
            "no_paper_validity_disclaimer": self.no_paper_validity_disclaimer,
            "reproducibility_details": dict(self.reproducibility_details),
            "overall_status": self.overall_status,
        }


def render_markdown(report: BaselineFairnessRebuildReport) -> str:
    payload = report.to_dict()
    lines: list[str] = []
    lines.append("# Baseline Fairness Rebuild")
    lines.append("")
    lines.append("## Metadata")
    for key in ("feature_id", "generated_by", "deterministic", "source_refs"):
        lines.append(f"- **{key}**: {payload['metadata'].get(key)}")
    lines.append("")
    lines.append("## Source Gate Status")
    lines.append(f"- **passed**: {payload['source_gate_status'].get('passed')}")
    for item in payload["source_gate_status"].get("checks", []):
        lines.append(f"- **{item['artifact']}**: valid={item['valid']} details={item['details']}")
    lines.append("")
    lines.append("## Baseline Policies Included")
    for name in payload["baseline_policies_included"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("## Scenarios And Traces")
    for item in payload["scenarios_traces_used"]:
        lines.append(f"- {item['scenario_name']} trace={item['trace_id']} seed={item['seed']}")
    lines.append("")
    lines.append("## Fairness Controls")
    for key, value in payload["fairness_controls"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("## Metrics Reused")
    for metric in payload["metrics_reused"]:
        lines.append(f"- {metric}")
    lines.append("")
    lines.append("## Collapse Indicators")
    for item in payload["collapse_indicators"]:
        lines.append(f"- {item['policy_name']} / {item['scenario_name']}: {item['signature']}")
    lines.append("")
    lines.append("## Anti-Collapse Assessment")
    lines.append(f"- **status**: {payload['anti_collapse_assessment'].get('status')}")
    for item in payload["anti_collapse_assessment"].get("evidence", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Unchanged Collapse Explanation")
    lines.append(payload["unchanged_collapse_explanation"])
    lines.append("")
    lines.append("## Limitations")
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## No Training Disclaimer")
    lines.append(payload["no_training_disclaimer"])
    lines.append("")
    lines.append("## No Policy Redesign Disclaimer")
    lines.append(payload["no_policy_redesign_disclaimer"])
    lines.append("")
    lines.append("## No Paper Validity Disclaimer")
    lines.append(payload["no_paper_validity_disclaimer"])
    lines.append("")
    lines.append("## Reproducibility Details")
    for key, value in payload["reproducibility_details"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append(f"## Overall Status\n{payload['overall_status']}")
    lines.append("")
    return "\n".join(lines)


def write_baseline_fairness_rebuild_report(report: BaselineFairnessRebuildReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    md_path = target_dir / MARKDOWN_FILENAME
    csv_path = target_dir / CSV_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "policy_name",
                "scenario_name",
                "signature",
            ],
        )
        writer.writeheader()
        for item in report.collapse_indicators:
            writer.writerow(
                {
                    "policy_name": item["policy_name"],
                    "scenario_name": item["scenario_name"],
                    "signature": item["signature"],
                }
            )
    return json_path, md_path
