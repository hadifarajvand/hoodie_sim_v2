from __future__ import annotations

from .config import FEATURE_ID, LegalityEvidenceConfig
from .model import (
    BehaviorEquivalenceCheck,
    LegalityEvidenceCollector,
    LegalityEvidenceRecord,
    LegalityEvidenceReport,
    LegalitySnapshot,
)
from .report import DEFAULT_OUTPUT_DIR, JSON_FILENAME, MARKDOWN_FILENAME, write_legality_evidence_report
from .runner import build_legality_evidence_report, main, run_legality_evidence_expansion

__all__ = [
    "FEATURE_ID",
    "LegalityEvidenceConfig",
    "LegalitySnapshot",
    "LegalityEvidenceRecord",
    "LegalityEvidenceCollector",
    "LegalityEvidenceReport",
    "BehaviorEquivalenceCheck",
    "DEFAULT_OUTPUT_DIR",
    "JSON_FILENAME",
    "MARKDOWN_FILENAME",
    "write_legality_evidence_report",
    "build_legality_evidence_report",
    "run_legality_evidence_expansion",
    "main",
]
