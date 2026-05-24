from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "055-paper-default-training-smoke-run"
OUTPUT_DIR = Path("artifacts/analysis/paper-default-training-smoke-run")
REPORT_JSON = OUTPUT_DIR / "paper-default-training-smoke-run-report.json"
REPORT_MD = OUTPUT_DIR / "paper-default-training-smoke-run-report.md"


@dataclass(slots=True)
class PaperDefaultTrainingSmokeConfig:
    feature_id: str = FEATURE_ID
    smoke_episodes: int = 1
    smoke_episode_length: int = 110
    expected_next_feature: str = "Feature 056 — Target Update and Replay Training Validation"
    readiness_report_path: Path = Path("artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json")

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 055-paper-default-training-smoke-run")
        if self.smoke_episodes != 1:
            raise ValueError("Feature 055 is a one-episode smoke run, not a pilot or campaign")
        if self.smoke_episode_length != 110:
            raise ValueError("Feature 055 must use paper-default episode length 110")
