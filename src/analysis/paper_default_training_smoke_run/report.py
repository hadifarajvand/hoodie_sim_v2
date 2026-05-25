from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import PaperDefaultTrainingSmokeReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Paper-Default Training Smoke Run Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_054_readiness_verified: `{payload['feature_054_readiness_verified']}`",
            f"- live_environment_training_used: `{payload['live_environment_training_used']}`",
            f"- fixture_training_used: `{payload['fixture_training_used']}`",
            "",
            "## Smoke Scope",
            _json_dump(payload["paper_default_smoke_scope"]).strip(),
            "",
            "## Replay Summary",
            _json_dump(payload["replay_summary"]).strip(),
            "",
            "## Optimizer Step Summary",
            _json_dump(payload["optimizer_step_summary"]).strip(),
            "",
            "## Loss Summary",
            _json_dump(payload["loss_summary"]).strip(),
            "",
            "## Checkpoint Summary",
            _json_dump(payload["checkpoint_summary"]).strip(),
            "",
            "## Legal Action Summary",
            _json_dump(payload["legal_action_summary"]).strip(),
            "",
            "## Delayed Reward Contract",
            _json_dump(payload["delayed_reward_contract_verified"]).strip(),
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


def write_paper_default_training_smoke_report(
    report: PaperDefaultTrainingSmokeReport,
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
