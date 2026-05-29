from __future__ import annotations

from pathlib import Path

FEATURE_ID = "068-paper-baseline-suite-batch"
FEATURE_067_REPORT = Path("artifacts/analysis/paper-traffic-queue-communication-fidelity-batch/paper-traffic-queue-communication-fidelity-batch-report.json")
OUTPUT_DIR = Path("artifacts/analysis/paper-baseline-suite-batch")
REPORT_JSON = OUTPUT_DIR / "paper-baseline-suite-batch-report.json"
REPORT_MD = OUTPUT_DIR / "paper-baseline-suite-batch-report.md"
BASELINE_REGISTRY_JSON = OUTPUT_DIR / "baseline-registry.json"
BASELINE_EVAL_SUMMARY_JSON = OUTPUT_DIR / "baseline-evaluation-summary.json"
REPEATABILITY_PROOF_JSON = OUTPUT_DIR / "deterministic-repeatability-proof.json"
READY_NEXT_FEATURE = "Feature 069 — Full HOODIE Mechanism Fidelity Batch"

