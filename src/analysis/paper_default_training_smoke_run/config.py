from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig, READINESS_MANUAL_APPROVAL_APPROVED

FEATURE_ID = "055-paper-default-training-smoke-run"
BRANCH_NAME = "055-paper-default-smoke-run"
SMOKE_BASELINE_BRANCH = "phase/013-pre-training-readiness-audit"
OUTPUT_DIR = Path("artifacts/analysis/paper-default-training-smoke-run")
REPORT_JSON = OUTPUT_DIR / "paper-default-training-smoke-run-report.json"
REPORT_MD = OUTPUT_DIR / "paper-default-training-smoke-run-report.md"
READY_NEXT_FEATURE = "Feature 056 — Target Update and Replay Training Validation"
FEATURE_054_REPORT = Path("artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json")
FEATURE_054_COMPLETE_TAG = "054-training-readiness-contract-complete^{}"
FEATURE_054A_COMPLETE_TAG = "054a-speckit-local-state-hygiene-complete^{}"


@dataclass(slots=True)
class PaperDefaultTrainingSmokeConfig:
    feature_id: str = FEATURE_ID
    smoke_episodes: int = 1
    smoke_episode_length: int = 110
    expected_next_feature: str = READY_NEXT_FEATURE
    readiness_report_path: Path = FEATURE_054_REPORT
    full_campaign: bool = False
    baseline_comparison: bool = False
    paper_reproduction_claim: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 055-paper-default-training-smoke-run")
        if self.smoke_episodes != 1:
            raise ValueError("Feature 055 is a one-episode smoke run, not a pilot or campaign")
        if self.smoke_episode_length != 110:
            raise ValueError("Feature 055 must use paper-default episode length 110")
        if self.full_campaign is not False:
            raise ValueError("Feature 055 must not enable a full campaign")
        if self.baseline_comparison is not False:
            raise ValueError("Feature 055 must not enable baseline comparison")
        if self.paper_reproduction_claim is not False:
            raise ValueError("Feature 055 must not claim paper reproduction")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("Feature 055 must route the ready path to Feature 056")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "smoke_episodes": self.smoke_episodes,
            "smoke_episode_length": self.smoke_episode_length,
            "expected_next_feature": self.expected_next_feature,
            "readiness_report_path": str(self.readiness_report_path),
            "full_campaign": self.full_campaign,
            "baseline_comparison": self.baseline_comparison,
            "paper_reproduction_claim": self.paper_reproduction_claim,
        }

    def build_campaign_config(self) -> CampaignConfig:
        return CampaignConfig(
            readiness_manual_approval_status=READINESS_MANUAL_APPROVAL_APPROVED,
            readiness_manual_approval_reference="Feature 054 training readiness contract",
            full_campaign_enabled=self.full_campaign,
            pilot_episode_length=self.smoke_episode_length,
            evaluation_episode_length=self.smoke_episode_length,
        )
