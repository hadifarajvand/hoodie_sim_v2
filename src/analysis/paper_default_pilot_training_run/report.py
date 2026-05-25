from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import PaperDefaultPilotTrainingRunReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Paper-Default Pilot Training Run Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_056_validation_verified: `{payload['feature_056_validation_verified']}`",
            f"- live_environment_training_used: `{payload['live_environment_training_used']}`",
            f"- fixture_training_used: `{payload['fixture_training_used']}`",
            "",
            "## Pilot Scope",
            _json_dump(payload["pilot_scope"]).strip(),
            "",
            "## Episode Summary",
            _json_dump(payload["episode_summary"]).strip(),
            "",
            "## Replay Summary",
            _json_dump(payload["replay_summary"]).strip(),
            "",
            "## Optimizer Summary",
            _json_dump(payload["optimizer_summary"]).strip(),
            "",
            "## Target Update Summary",
            _json_dump(payload["target_update_summary"]).strip(),
            "",
            "## Loss Summary",
            _json_dump(payload["loss_summary"]).strip(),
            "",
            "## Reward Summary",
            _json_dump(payload["reward_summary"]).strip(),
            "",
            "## Legal Action Summary",
            _json_dump(payload["legal_action_summary"]).strip(),
            "",
            "## Checkpoint Summary",
            _json_dump(payload["checkpoint_summary"]).strip(),
            "",
            "## Train/Eval Contract",
            _json_dump(payload["train_eval_contract_verified"]).strip(),
            "",
            "## Behavior Safety Summary",
            _json_dump(payload["behavior_safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            _json_dump(payload["remaining_blockers"]).strip(),
        ]
    )


def write_paper_default_pilot_training_run_report(
    report: PaperDefaultPilotTrainingRunReport,
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
