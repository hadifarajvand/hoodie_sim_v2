from __future__ import annotations

from pathlib import Path

from src.analysis.final_review_release_gate_batch.config import (
    ACTION_COLLAPSE_REVIEW_JSON,
    DIAGNOSTIC_FINDINGS_JSON,
    EVALUATION_SIGNAL_REVIEW_JSON,
    FIGURES_DIR,
    FIGURE_MANIFEST_JSON,
    FINAL_REVIEW_SUMMARY_MD,
    NEXT_ACTION_DECISION_JSON,
    OUTPUT_DIR,
    REPLAY_BUFFER_REVIEW_JSON,
    REPORT_JSON,
    REPORT_MD,
    REWARD_STABILITY_REVIEW_JSON,
)
from src.analysis.final_review_release_gate_batch.runner import main


def test_gate_command_materializes_required_artifacts() -> None:
    assert main(["--json"]) == 0

    required_paths = [
        REPORT_JSON,
        REPORT_MD,
        DIAGNOSTIC_FINDINGS_JSON,
        REWARD_STABILITY_REVIEW_JSON,
        ACTION_COLLAPSE_REVIEW_JSON,
        REPLAY_BUFFER_REVIEW_JSON,
        EVALUATION_SIGNAL_REVIEW_JSON,
        NEXT_ACTION_DECISION_JSON,
        FINAL_REVIEW_SUMMARY_MD,
        FIGURE_MANIFEST_JSON,
        FIGURES_DIR / "figure_01_reward_stability_gate.png",
        FIGURES_DIR / "figure_02_vertical_action_collapse_gate.png",
        FIGURES_DIR / "figure_03_replay_cap_gate.png",
    ]
    assert all(path.exists() for path in required_paths)
    assert OUTPUT_DIR.exists()
