from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import DEFAULT_JSON_FILENAME, DEFAULT_MARKDOWN_FILENAME, DEFAULT_OUTPUT_DIR
from .model import TrainingReadinessContractReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Training Readiness Contract Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_053_readiness_verified: `{payload['feature_053_readiness_verified']}`",
            f"- evidence_chain_ready_for_training_contract: `{payload['evidence_chain_ready_for_training_contract']}`",
            f"- training_execution_allowed_next: `{payload['training_execution_allowed_next']}`",
            "",
            "## Contract Locks",
            _json_dump(
                {
                    key: payload[key]
                    for key in [
                        "paper_default_config_locked",
                        "observation_contract_locked",
                        "action_contract_locked",
                        "legality_contract_locked",
                        "reward_contract_locked",
                        "timeout_contract_locked",
                        "capacity_contract_locked",
                        "transmission_contract_locked",
                        "queue_contract_locked",
                        "metric_contract_locked",
                        "seed_contract_locked",
                        "artifact_contract_locked",
                    ]
                }
            ).strip(),
            "",
            "## Behavior Equivalence Summary",
            _json_dump(payload["behavior_equivalence_summary"]).strip(),
            "",
            "## Remaining Blockers",
            _json_dump(payload["remaining_blockers"]).strip(),
        ]
    )


def write_training_readiness_contract_report(
    report: TrainingReadinessContractReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / DEFAULT_JSON_FILENAME
    md_path = target_dir / DEFAULT_MARKDOWN_FILENAME
    payload = report.to_dict()
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
