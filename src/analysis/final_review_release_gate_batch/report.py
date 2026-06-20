from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import FINAL_REVIEW_SUMMARY_MD, OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import FinalReviewReleaseGateBatchReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Review and Release Gate Batch Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_action: `{payload['recommended_next_action']}`",
            "",
            "## Diagnostic Findings",
            json_dump(payload["diagnostic_findings"]).strip(),
            "",
            "## Reward Stability Review",
            json_dump(payload["reward_stability_review"]).strip(),
            "",
            "## Action Collapse Review",
            json_dump(payload["action_collapse_review"]).strip(),
            "",
            "## Replay Buffer Review",
            json_dump(payload["replay_buffer_review"]).strip(),
            "",
            "## Evaluation Signal Review",
            json_dump(payload["evaluation_signal_review"]).strip(),
            "",
            "## Next Action Decision",
            json_dump(payload["next_action_decision"]).strip(),
            "",
            "## Claim Safety Status",
            json_dump(payload["claim_safety_status"]).strip(),
            "",
            "## Figure Manifest",
            json_dump(payload["figure_manifest"]).strip(),
            "",
            "## Remaining Blockers",
            json_dump(payload["remaining_blockers"]).strip(),
        ]
    )


def render_final_review_summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Final Review Summary",
        "",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_action: `{payload['recommended_next_action']}`",
        f"- evaluation_reward_static_across_budget: `{payload['diagnostic_findings']['evaluation_reward_static_across_budget']}`",
        f"- vertical_action_collapse_detected: `{payload['diagnostic_findings']['vertical_action_collapse_detected']}`",
        f"- replay_size_cap_detected: `{payload['diagnostic_findings']['replay_size_cap_detected']}`",
        f"- evaluation_signal_sufficient_for_claims: `{payload['diagnostic_findings']['evaluation_signal_sufficient_for_claims']}`",
        "",
        "## Question Answers",
    ]
    for question_key, question_payload in payload["diagnostic_findings"]["questions"].items():
        lines.append(f"- {question_key}: {question_payload.get('answer')}")
    lines.extend(
        [
            "",
            "## Claim Safety",
            json_dump(payload["claim_safety_status"]).strip(),
        ]
    )
    return "\n".join(lines) + "\n"


def write_final_review_release_gate_batch_report(
    report: FinalReviewReleaseGateBatchReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    summary_path = target_dir / FINAL_REVIEW_SUMMARY_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    summary_path.write_text(render_final_review_summary_markdown(payload), encoding="utf-8")
    return json_path, md_path, summary_path
