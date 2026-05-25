from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "057-paper-default-pilot-training-run"
BRANCH_NAME = "057-paper-default-pilot-training-run"
OUTPUT_DIR = Path("artifacts/analysis/paper-default-pilot-training-run")
REPORT_JSON = OUTPUT_DIR / "paper-default-pilot-training-run-report.json"
REPORT_MD = OUTPUT_DIR / "paper-default-pilot-training-run-report.md"
READY_NEXT_FEATURE = "Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness"
FEATURE_056_REPORT = Path("artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json")
FEATURE_055_REPORT = Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json")
FEATURE_054_REPORT = Path("artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json")
FEATURE_056_COMPLETE_TAG = "056-target-update-replay-training-validation-complete^{}"
FEATURE_055_COMPLETE_TAG = "055-paper-default-training-smoke-run-complete^{}"
FEATURE_054_COMPLETE_TAG = "054-training-readiness-contract-complete^{}"
FEATURE_054A_COMPLETE_TAG = "054a-speckit-local-state-hygiene-complete^{}"


@dataclass(slots=True)
class PaperDefaultPilotTrainingRunConfig:
    feature_id: str = FEATURE_ID
    pilot_episodes: int = 3
    pilot_episode_length: int = 110
    feature_056_report_path: Path = FEATURE_056_REPORT
    feature_055_report_path: Path = FEATURE_055_REPORT
    feature_054_report_path: Path = FEATURE_054_REPORT
    expected_next_feature: str = READY_NEXT_FEATURE
    full_campaign: bool = False
    baseline_comparison: bool = False
    paper_reproduction_claim: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 057-paper-default-pilot-training-run")
        if self.pilot_episodes != 3:
            raise ValueError("Feature 057 must use the approved three-episode pilot")
        if self.pilot_episode_length != 110:
            raise ValueError("Feature 057 must preserve the paper-default episode length 110")
        if self.full_campaign is not False:
            raise ValueError("Feature 057 must not enable a full campaign")
        if self.baseline_comparison is not False:
            raise ValueError("Feature 057 must not enable baseline comparison")
        if self.paper_reproduction_claim is not False:
            raise ValueError("Feature 057 must not claim paper reproduction")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("Feature 057 must route the pass path to Feature 058")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "pilot_episodes": self.pilot_episodes,
            "pilot_episode_length": self.pilot_episode_length,
            "feature_056_report_path": str(self.feature_056_report_path),
            "feature_055_report_path": str(self.feature_055_report_path),
            "feature_054_report_path": str(self.feature_054_report_path),
            "expected_next_feature": self.expected_next_feature,
            "full_campaign": self.full_campaign,
            "baseline_comparison": self.baseline_comparison,
            "paper_reproduction_claim": self.paper_reproduction_claim,
        }

    def build_campaign_config(self) -> CampaignConfig:
        from src.analysis.full_training_reproduction_campaign.config import (
            CampaignConfig,
            READINESS_MANUAL_APPROVAL_APPROVED,
        )

        return CampaignConfig(
            readiness_manual_approval_status=READINESS_MANUAL_APPROVAL_APPROVED,
            readiness_manual_approval_reference="Feature 056 replay/target-update validation passed",
            full_campaign_enabled=self.full_campaign,
            pilot_episode_length=self.pilot_episode_length,
            evaluation_episode_length=self.pilot_episode_length,
        )
