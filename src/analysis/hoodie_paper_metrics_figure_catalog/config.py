from __future__ import annotations

from pathlib import Path


FEATURE_ID = "089-hoodie-paper-metrics-figure-catalog"
FEATURE_NAME = "Feature 089 HOODIE Paper Metrics Figure Catalog"

ROOT_DIR = Path(__file__).resolve().parents[3]
SPEC_DIR = ROOT_DIR / "specs" / "089-hoodie-paper-metrics-figure-catalog"
ARTIFACT_DIR = ROOT_DIR / "artifacts" / "feature_089_paper_metrics_catalog"

PAPER_OCR_PATH = ROOT_DIR / "resources" / "papers" / "hoodie" / "ocr" / "merged.txt"
PAPER_PDF_PATH = ROOT_DIR / "resources" / "papers" / "hoodie" / "original" / "HOODIE_paper.pdf"
FEATURE_086_REPORT_PATH = ROOT_DIR / "reports" / "feature_086_system_model_fidelity_final_review.md"

ACTIVE_POLICIES = ("HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO")

FEATURE_086_BOUNDARY = (
    "HOODIE remains the paper proposed method boundary.",
    "No thesis/DCQ/custom-method claim is allowed.",
    "Feature 086 approximations remain in force for output comparison.",
)

FEATURE_080_BOUNDARY = (
    "Feature 080 prepares HOODIE_PROPOSED for later evaluation.",
    "Ranking must wait until HOODIE_PROPOSED is implemented faithfully enough.",
    "Do not rank policies.",
    "Do not evaluate baselines.",
    "Do not introduce thesis method.",
    "Do not use DCQ.",
    "Do not claim full reproduction unless all required components pass.",
)

PRIORITY_1_FIGURES = (
    "Figure 10a",
    "Figure 10b",
    "Figure 10c",
    "Figure 10d",
    "Figure 10e",
    "Figure 10f",
)

PRIORITY_2_FIGURES = (
    "Figure 9a",
    "Figure 9b",
    "Figure 9c",
    "Figure 9d",
    "Figure 9e",
)

PRIORITY_3_FIGURES = ("Figure 8a", "Figure 8b", "Figure 11")

FIGURE_IDS = PRIORITY_3_FIGURES[:2] + PRIORITY_2_FIGURES + PRIORITY_1_FIGURES + ("Figure 11",)

ALLOWED_PRIORITY = (
    "priority_1_comparative_output",
    "priority_2_hoodie_behavior_output",
    "priority_3_training_or_lstm_required",
)

ALLOWED_OUTPUT_STATUS = (
    "required_now",
    "later_training_required",
    "later_lstm_required",
    "reference_only",
)

METRIC_IDS = (
    "average_task_completion_delay",
    "task_drop_ratio",
    "average_reward",
    "accumulated_reward",
    "action_distribution",
    "average_task_delay_with_vs_without_lstm",
)

SIMULATOR_REFERENCE_ARTIFACTS = (
    ROOT_DIR / "artifacts" / "feature_085_full_audit" / "aggregate_by_policy.json",
    ROOT_DIR / "artifacts" / "feature_085_full_audit" / "ranking_by_metric.json",
    ROOT_DIR / "artifacts" / "feature_085_full_audit" / "raw_rows.json",
)

