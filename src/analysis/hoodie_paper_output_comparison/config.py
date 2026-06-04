from __future__ import annotations

from pathlib import Path


FEATURE_ID = "087-hoodie-paper-output-comparison"
FEATURE_NAME = "Feature 087 HOODIE Paper Output Comparison"

ROOT_DIR = Path(__file__).resolve().parents[3]
SPEC_DIR = ROOT_DIR / "specs" / "087-hoodie-paper-output-comparison"
ARTIFACT_DIR = ROOT_DIR / "artifacts" / "feature_087_paper_output_comparison"

FEATURE_085_AUDIT_DIR = ROOT_DIR / "artifacts" / "feature_085_full_audit"
FEATURE_086_REPORT_PATH = ROOT_DIR / "reports" / "feature_086_system_model_fidelity_final_review.md"
FEATURE_086_ARTIFACT_DIR = ROOT_DIR / "artifacts" / "feature_086_system_model_fidelity"
PAPER_OCR_PATH = ROOT_DIR / "resources" / "papers" / "hoodie" / "ocr" / "merged.txt"
PAPER_PDF_PATH = ROOT_DIR / "resources" / "papers" / "hoodie" / "original" / "HOODIE_paper.pdf"

ACTIVE_POLICIES = ("HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO")
INVALID_LABELS = ("MQO", "Minimum Queue Offloader", "ORIGINAL_HOODIE_BASELINE", "HOODIE_PROPOSED")

ALLOWED_PAPER_COMPARISON_METRICS = (
    "task_completion_delay",
    "task_drop_ratio",
    "completion_rate",
    "average_reward",
    "total_reward",
    "throughput",
)

REPOSITORY_DIAGNOSTIC_METRICS = (
    "timeout_drop_rate",
    "unavailable_drop_rate",
    "deadline_violation_rate",
    "queue_stability_score",
    "illegal_action_rejection_count",
)

REQUIRED_METRICS = ALLOWED_PAPER_COMPARISON_METRICS + REPOSITORY_DIAGNOSTIC_METRICS

VERDICTS = (
    "paper_output_comparison_ready",
    "paper_output_comparison_partial",
    "paper_output_comparison_blocked",
)

PAPER_COMPATIBLE_FIGURES = ("Figure 10a", "Figure 10b", "Figure 10c", "Figure 10d", "Figure 10e", "Figure 10f")
NON_COMPARABLE_FIGURES = ("Figure 8a", "Figure 8b", "Figure 9a", "Figure 9b", "Figure 9c", "Figure 9d", "Figure 9e", "Figure 11")

