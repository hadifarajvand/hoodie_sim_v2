from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import TargetUpdateReplayValidationReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Target Update and Replay Training Validation Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_055_smoke_verified: `{payload['feature_055_smoke_verified']}`",
            f"- replay_insertion_validated: `{payload['replay_insertion_validated']}`",
            f"- replay_sampling_validated: `{payload['replay_sampling_validated']}`",
            f"- optimizer_step_counter_validated: `{payload['optimizer_step_counter_validated']}`",
            f"- target_update_contract_validated: `{payload['target_update_contract_validated']}`",
            f"- target_sync_schedule_validated: `{payload['target_sync_schedule_validated']}`",
            f"- target_sync_before_threshold_blocked: `{payload['target_sync_before_threshold_blocked']}`",
            f"- target_sync_at_threshold_validated: `{payload['target_sync_at_threshold_validated']}`",
            f"- checkpoint_metadata_validated: `{payload['checkpoint_metadata_validated']}`",
            "",
            "## Replay Summary",
            _json_dump(payload["replay_summary"]).strip(),
            "",
            "## Optimizer Step Summary",
            _json_dump(payload["optimizer_step_summary"]).strip(),
            "",
            "## Target Update Summary",
            _json_dump(payload["target_update_summary"]).strip(),
            "",
            "## Checkpoint Metadata Summary",
            _json_dump(payload["checkpoint_metadata_summary"]).strip(),
            "",
            "## Behavior Safety Summary",
            _json_dump(payload["behavior_safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            _json_dump(payload["remaining_blockers"]).strip(),
        ]
    )


def write_target_update_replay_validation_report(
    report: TargetUpdateReplayValidationReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
