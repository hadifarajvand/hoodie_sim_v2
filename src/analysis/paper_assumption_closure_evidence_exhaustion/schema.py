from __future__ import annotations

FINAL_STATUSES = (
    "recovered",
    "partially_recovered",
    "contradicted",
    "assumption_backed_requires_user_approval",
    "unrecoverable_after_evidence_exhaustion",
    "out_of_scope",
)

CONFIDENCE_LEVELS = ("high", "medium", "low", "invalid")

DOMAIN_VALUES = (
    "topology",
    "connectivity",
    "compute capacity",
    "link/data rate",
    "timeout/deadline",
    "reward aggregation",
    "equation formatting",
    "runtime assumption",
    "other",
)

SOURCE_METHODS = (
    "ocr_keyword_search",
    "registry_lookup",
    "json_artifact_lookup",
    "table_extraction",
    "equation_extraction",
    "visual_pdf_page_inspection",
    "cross_artifact_consistency_check",
    "manual_review",
)
