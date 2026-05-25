from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "056-target-update-and-replay-training-validation"
BRANCH_NAME = "056-target-update-replay-validation"
OUTPUT_DIR = Path("artifacts/analysis/target-update-replay-training-validation")
REPORT_JSON = OUTPUT_DIR / "target-update-replay-validation-report.json"
REPORT_MD = OUTPUT_DIR / "target-update-replay-validation-report.md"
READY_NEXT_FEATURE = "Feature 057 — Paper-Default Pilot Training Run"
FEATURE_055_NEXT_FEATURE = "Feature 056 — Target Update and Replay Training Validation"
FEATURE_055_REPORT = Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json")
FEATURE_054_REPORT = Path("artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json")
FEATURE_055_COMPLETE_TAG = "055-paper-default-training-smoke-run-complete^{}"
FEATURE_054_COMPLETE_TAG = "054-training-readiness-contract-complete^{}"
FEATURE_054A_COMPLETE_TAG = "054a-speckit-local-state-hygiene-complete^{}"
TARGET_UPDATE_UNIT = "optimizer_step"
TARGET_UPDATE_FREQUENCY = 2000
REPLAY_SAMPLE_SIZE = 16


@dataclass(slots=True)
class TargetUpdateReplayValidationConfig:
    feature_id: str = FEATURE_ID
    output_dir: Path = OUTPUT_DIR
    feature_055_report_path: Path = FEATURE_055_REPORT
    feature_054_report_path: Path = FEATURE_054_REPORT
    smoke_episodes: int = 1
    smoke_episode_length: int = 110
    replay_sample_size: int = REPLAY_SAMPLE_SIZE
    target_update_unit: str = TARGET_UPDATE_UNIT
    target_update_frequency: int = TARGET_UPDATE_FREQUENCY
    expected_next_feature: str = READY_NEXT_FEATURE
    full_campaign: bool = False
    baseline_comparison: bool = False
    paper_reproduction_claim: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 056-target-update-and-replay-training-validation")
        if self.output_dir != OUTPUT_DIR:
            raise ValueError("output_dir must remain the approved Feature 056 artifact directory")
        if self.smoke_episodes != 1:
            raise ValueError("Feature 056 must validate a single controlled smoke episode")
        if self.smoke_episode_length != 110:
            raise ValueError("Feature 056 must preserve the paper-default episode length 110")
        if self.replay_sample_size <= 0:
            raise ValueError("replay_sample_size must be positive")
        if self.target_update_unit != TARGET_UPDATE_UNIT:
            raise ValueError("target_update_unit must remain optimizer_step")
        if self.target_update_frequency != TARGET_UPDATE_FREQUENCY:
            raise ValueError("target_update_frequency must remain 2000")
        if self.full_campaign is not False:
            raise ValueError("Feature 056 must not enable full campaign execution")
        if self.baseline_comparison is not False:
            raise ValueError("Feature 056 must not enable baseline comparison")
        if self.paper_reproduction_claim is not False:
            raise ValueError("Feature 056 must not claim paper reproduction")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("Feature 056 must route the pass path to Feature 057")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "output_dir": str(self.output_dir),
            "feature_055_report_path": str(self.feature_055_report_path),
            "feature_054_report_path": str(self.feature_054_report_path),
            "smoke_episodes": self.smoke_episodes,
            "smoke_episode_length": self.smoke_episode_length,
            "replay_sample_size": self.replay_sample_size,
            "target_update_unit": self.target_update_unit,
            "target_update_frequency": self.target_update_frequency,
            "expected_next_feature": self.expected_next_feature,
            "full_campaign": self.full_campaign,
            "baseline_comparison": self.baseline_comparison,
            "paper_reproduction_claim": self.paper_reproduction_claim,
        }

    def build_campaign_config(self):
        from src.analysis.full_training_reproduction_campaign.config import (
            CampaignConfig,
            READINESS_MANUAL_APPROVAL_APPROVED,
        )

        return CampaignConfig(
            readiness_manual_approval_status=READINESS_MANUAL_APPROVAL_APPROVED,
            readiness_manual_approval_reference="Feature 055 paper-default smoke passed",
            full_campaign_enabled=self.full_campaign,
            pilot_episode_length=self.smoke_episode_length,
            evaluation_episode_length=self.smoke_episode_length,
        )
