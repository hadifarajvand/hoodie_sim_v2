from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from .registry import FEATURE_ID, OUTPUT_PATH, SCHEMA_VERSION, build_registry_entries, build_user_approved_assumption_registry


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/user-approved-assumption-patch-registry")
JSON_FILENAME = "assumption-patch-report.json"
MARKDOWN_FILENAME = "assumption-patch-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class AssumptionPatchReport:
    feature_id: str
    schema_version: str
    source_gates: list[dict[str, Any]]
    registry_path: str
    item_count: int
    status_counts: dict[str, int]
    runtime_usable_items: list[dict[str, Any]]
    proposed_items: list[dict[str, Any]]
    blocked_items: list[dict[str, Any]]
    rejected_items: list[dict[str, Any]]
    entries: list[dict[str, Any]]
    no_paper_recovery_claims: bool
    no_runtime_behavior_change: bool
    no_training_or_policy_drift: bool
    no_dependency_drift: bool
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "schema_version": self.schema_version,
            "source_gates": list(self.source_gates),
            "registry_path": self.registry_path,
            "item_count": self.item_count,
            "status_counts": dict(self.status_counts),
            "runtime_usable_items": [dict(item) for item in self.runtime_usable_items],
            "proposed_items": [dict(item) for item in self.proposed_items],
            "blocked_items": [dict(item) for item in self.blocked_items],
            "rejected_items": [dict(item) for item in self.rejected_items],
            "entries": [dict(item) for item in self.entries],
            "no_paper_recovery_claims": self.no_paper_recovery_claims,
            "no_runtime_behavior_change": self.no_runtime_behavior_change,
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_dependency_drift": self.no_dependency_drift,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# User-Approved Assumption Patch Registry Report",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- schema_version: `{self.schema_version}`",
            f"- registry_path: `{self.registry_path}`",
            f"- item_count: `{self.item_count}`",
            f"- final_verdict: `{self.final_verdict}`",
            "",
            "## Status Counts",
        ]
        for key in sorted(self.status_counts):
            lines.append(f"- {key}: `{self.status_counts[key]}`")
        lines.extend([
            "",
            "## Blocked Items",
        ])
        for item in self.blocked_items:
            lines.append(f"- `{item['item_id']}` | `{item['assumption_status']}` | runtime_use_allowed={item['runtime_use_allowed']}")
        lines.extend([
            "",
            "## Proposed Items",
        ])
        for item in self.proposed_items:
            lines.append(f"- `{item['item_id']}` | `{item['proposed_value']}` | runtime_use_allowed={item['runtime_use_allowed']}")
        lines.extend([
            "",
            "## Runtime-Usable Items",
        ])
        if self.runtime_usable_items:
            for item in self.runtime_usable_items:
                lines.append(f"- `{item['item_id']}`")
        else:
            lines.append("- none")
        lines.extend([
            "",
            "## Final Verdict",
            self.final_verdict,
            "",
        ])
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        markdown_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        markdown_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, markdown_path


def _validate_non_empty_fields(entries: list[dict[str, Any]]) -> None:
    for entry in entries:
        for field in ("rationale", "scientific_risk", "validation_plan"):
            if not str(entry.get(field, "")).strip():
                raise ValueError(f"Empty {field} for {entry.get('item_id')}")
        affected = entry.get("affected_runtime_components")
        if not isinstance(affected, list) or not affected or not all(str(component).strip() for component in affected):
            raise ValueError(f"Empty affected_runtime_components for {entry.get('item_id')}")


def build_assumption_patch_report(repo_root: Path | None = None) -> AssumptionPatchReport:
    registry = build_user_approved_assumption_registry(repo_root)
    entries = registry["entries"]
    _validate_non_empty_fields(entries)
    counts: dict[str, int] = {
        "approved": 0,
        "blocked_no_assumption": 0,
        "proposed": 0,
        "rejected": 0,
    }
    for entry in entries:
        status = entry["assumption_status"]
        counts[status] = counts.get(status, 0) + 1
    blocked_items = [entry for entry in entries if entry["assumption_status"] == "blocked_no_assumption"]
    proposed_items = [entry for entry in entries if entry["assumption_status"] == "proposed"]
    rejected_items = [entry for entry in entries if entry["assumption_status"] == "rejected"]
    runtime_usable_items = [entry for entry in entries if entry["runtime_use_allowed"]]
    final_verdict = "registry_created_with_runtime_approved_assumptions" if runtime_usable_items else "registry_created_no_runtime_approved_assumptions"
    return AssumptionPatchReport(
        feature_id=FEATURE_ID,
        schema_version=SCHEMA_VERSION,
        source_gates=registry["source_gates"],
        registry_path=str(Path(OUTPUT_PATH)),
        item_count=registry["item_count"],
        status_counts=counts,
        runtime_usable_items=runtime_usable_items,
        proposed_items=proposed_items,
        blocked_items=blocked_items,
        rejected_items=rejected_items,
        entries=entries,
        no_paper_recovery_claims=all(entry["no_paper_recovery_claim"] for entry in entries),
        no_runtime_behavior_change=True,
        no_training_or_policy_drift=True,
        no_dependency_drift=True,
        final_verdict=final_verdict,
    )


def write_assumption_patch_report(report: AssumptionPatchReport | None = None, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    resolved = report or build_assumption_patch_report()
    return resolved.write(output_dir)

