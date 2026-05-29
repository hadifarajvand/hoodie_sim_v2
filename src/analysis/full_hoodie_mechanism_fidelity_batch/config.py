from __future__ import annotations

from pathlib import Path

FEATURE_ID = "069-full-hoodie-mechanism-fidelity-batch"
FEATURE_068_REPORT = Path("artifacts/analysis/paper-baseline-suite-batch/paper-baseline-suite-batch-report.json")
FEATURE_068_REMOTE_REF = "origin/068-paper-baseline-suite-batch"
OUTPUT_DIR = Path("artifacts/analysis/full-hoodie-mechanism-fidelity-batch")
REPORT_JSON = OUTPUT_DIR / "full-hoodie-mechanism-fidelity-batch-report.json"
REPORT_MD = OUTPUT_DIR / "full-hoodie-mechanism-fidelity-batch-report.md"
CONGESTION_JSON = OUTPUT_DIR / "congestion-control-contract.json"
REWARD_JSON = OUTPUT_DIR / "delayed-reward-contract.json"
COORDINATION_JSON = OUTPUT_DIR / "coordination-graph-contract.json"
SYNC_JSON = OUTPUT_DIR / "synchronization-contract.json"
READY_NEXT_FEATURE = "Feature 070 — Paper-Scale Experimental Reproduction Batch"
