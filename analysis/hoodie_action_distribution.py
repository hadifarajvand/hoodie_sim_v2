from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import csv
import json


def normalize_action_category(record: Dict[str, Any]) -> str:
    """Normalize a single action record into one of local/horizontal/vertical/unknown.

    Known string fields searched (in order):
      - action_type
      - action_name
      - action_category
      - offload_type
      - decision
      - selected_action
      - policy_action
      - target_tier

    Numeric `action` values return "unknown" unless an explicit mapping is provided externally.
    """
    if not isinstance(record, dict):
        return "unknown"

    def check_str_field(key: str) -> str | None:
        v = record.get(key)
        if isinstance(v, str):
            s = v.lower()
            if "local" in s:
                return "local"
            if "horiz" in s or "horizontal" in s:
                return "horizontal"
            if "vert" in s or "vertical" in s:
                return "vertical"
        return None

    for key in (
        "action_type",
        "action_name",
        "action_category",
        "offload_type",
        "decision",
        "selected_action",
        "policy_action",
        "target_tier",
    ):
        res = check_str_field(key)
        if res:
            return res

    # Numeric action ids are treated as unknown by default
    if "action" in record and isinstance(record["action"], int):
        return "unknown"

    return "unknown"


def aggregate_action_distribution(records: List[Dict[str, Any]], policy_name: str = "HOODIE") -> Dict[str, Any]:
    total = 0
    counts = {"local": 0, "horizontal": 0, "vertical": 0, "unknown": 0}
    warnings: List[str] = []
    for r in records:
        cat = normalize_action_category(r)
        if cat not in counts:
            counts["unknown"] += 1
            warnings.append(f"unmapped_action:{r}")
            total += 1
            continue
        counts[cat] += 1
        total += 1

    def ratio(n: int) -> float:
        return (n / total) if total > 0 else 0.0

    out = {
        "policy_name": policy_name,
        "total_actions": total,
        "local_count": counts["local"],
        "horizontal_count": counts["horizontal"],
        "vertical_count": counts["vertical"],
        "unknown_count": counts["unknown"],
        "local_ratio": ratio(counts["local"]),
        "horizontal_ratio": ratio(counts["horizontal"]),
        "vertical_ratio": ratio(counts["vertical"]),
        "unknown_ratio": ratio(counts["unknown"]),
        "warnings": warnings,
    }

    # Ensure floating point ratios sum to 1.0 when possible (fix tiny rounding)
    if out["total_actions"] > 0:
        s = out["local_ratio"] + out["horizontal_ratio"] + out["vertical_ratio"] + out["unknown_ratio"]
        if abs(s - 1.0) > 1e-12:
            # adjust unknown_ratio to make sum exactly 1.0
            out["unknown_ratio"] = max(0.0, 1.0 - (out["local_ratio"] + out["horizontal_ratio"] + out["vertical_ratio"]))

    if out["unknown_count"] > 0:
        out.setdefault("warnings", []).append("unknown_actions_present")

    return out


def write_action_distribution_outputs(records: List[Dict[str, Any]], output_dir: Path, label: str | None = None, policy_name: str = "HOODIE") -> Dict[str, Any]:
    """Write canonical output files (CSV/JSON/metadata) for action distributions.

    Filenames are fixed to:
      - hoodie_action_distribution.csv
      - hoodie_action_distribution.json
      - hoodie_action_distribution_metadata.json

    The `label` is recorded in metadata but not used in filenames to keep
    artifact names stable for downstream checks.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    agg = aggregate_action_distribution(records, policy_name=policy_name)
    csv_path = output_dir / "hoodie_action_distribution.csv"
    json_path = output_dir / "hoodie_action_distribution.json"
    meta_path = output_dir / "hoodie_action_distribution_metadata.json"

    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["policy_name", "category", "count", "ratio"])
        writer.writerow([policy_name, "local", agg["local_count"], agg["local_ratio"]])
        writer.writerow([policy_name, "horizontal", agg["horizontal_count"], agg["horizontal_ratio"]])
        writer.writerow([policy_name, "vertical", agg["vertical_count"], agg["vertical_ratio"]])
        writer.writerow([policy_name, "unknown", agg["unknown_count"], agg["unknown_ratio"]])

    json_path.write_text(json.dumps(agg, indent=2, sort_keys=True))

    metadata = {
        "policy_name": policy_name,
        "label": label,
        "source": "checkpointed_evaluation_or_synthetic_test",
        "official_figure_claim": False,
        "simulation_rerun": False,
        "training_run": False,
        "checkpoint_required_for_paper": True,
        "warnings": agg.get("warnings", []),
    }
    meta_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))
    return {"csv": str(csv_path), "json": str(json_path), "metadata": str(meta_path)}
