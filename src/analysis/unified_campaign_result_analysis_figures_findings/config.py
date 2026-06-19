from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "062-unified-campaign-result-analysis-figures-findings"
BRANCH_NAME = "062-unified-campaign-result-analysis-figures-findings"
BASE_BRANCH_NAME = "060-full-paper-default-training-campaign-execution-v2"
READY_NEXT_STEP = "External review of unified campaign analysis artifacts"

FEATURE_060_DIR = Path("artifacts/analysis/full-paper-default-training-campaign-execution")
FEATURE_060_REPORT = FEATURE_060_DIR / "full-paper-default-training-campaign-report.json"
FEATURE_060_TRAINING = FEATURE_060_DIR / "training-metrics.json"
FEATURE_060_EVALUATION = FEATURE_060_DIR / "evaluation-metrics.json"
FEATURE_060_BASELINE = FEATURE_060_DIR / "baseline-evaluation-metrics.json"
FEATURE_060_CHECKPOINT = FEATURE_060_DIR / "checkpoint-metadata.json"
FEATURE_060_MANIFEST = FEATURE_060_DIR / "run-manifest.json"

OUTPUT_DIR = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings")
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORT_JSON = OUTPUT_DIR / "unified-campaign-result-analysis-report.json"
REPORT_MD = OUTPUT_DIR / "unified-campaign-result-analysis-report.md"
INTEGRITY_AUDIT_JSON = OUTPUT_DIR / "integrity-audit.json"
COMPARISON_READINESS_JSON = OUTPUT_DIR / "comparison-readiness.json"
COMPARATIVE_METRICS_TABLE_JSON = OUTPUT_DIR / "comparative-metrics-table.json"
THESIS_TABLES_MD = OUTPUT_DIR / "thesis-result-tables.md"
FINAL_FINDINGS_MD = OUTPUT_DIR / "final-experimental-findings.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

REQUIRED_FIGURES = (
    "figure_01_training_action_distribution.png",
    "figure_02_training_reward_summary.png",
    "figure_03_baseline_policy_action_distribution.png",
    "figure_04_campaign_budget_integrity.png",
)


@dataclass(frozen=True, slots=True)
class UnifiedCampaignAnalysisConfig:
    feature_id: str = FEATURE_ID
    feature_060_report_path: Path = FEATURE_060_REPORT
    feature_060_training_path: Path = FEATURE_060_TRAINING
    feature_060_evaluation_path: Path = FEATURE_060_EVALUATION
    feature_060_baseline_path: Path = FEATURE_060_BASELINE
    feature_060_checkpoint_path: Path = FEATURE_060_CHECKPOINT
    feature_060_manifest_path: Path = FEATURE_060_MANIFEST
    output_dir: Path = OUTPUT_DIR
    figures_dir: Path = FIGURES_DIR
    recommended_next_step: str = READY_NEXT_STEP

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "feature_060_report_path": str(self.feature_060_report_path),
            "feature_060_training_path": str(self.feature_060_training_path),
            "feature_060_evaluation_path": str(self.feature_060_evaluation_path),
            "feature_060_baseline_path": str(self.feature_060_baseline_path),
            "feature_060_checkpoint_path": str(self.feature_060_checkpoint_path),
            "feature_060_manifest_path": str(self.feature_060_manifest_path),
            "output_dir": str(self.output_dir),
            "figures_dir": str(self.figures_dir),
            "recommended_next_step": self.recommended_next_step,
        }
