from __future__ import annotations

from pathlib import Path

FEATURE_ID = "067-paper-traffic-queue-communication-fidelity-batch"
FEATURE_066_REPORT = Path("artifacts/analysis/distributed-multi-agent-hoodie-training-batch/distributed-multi-agent-hoodie-training-batch-report.json")
OUTPUT_DIR = Path("artifacts/analysis/paper-traffic-queue-communication-fidelity-batch")
REPORT_JSON = OUTPUT_DIR / "paper-traffic-queue-communication-fidelity-batch-report.json"
REPORT_MD = OUTPUT_DIR / "paper-traffic-queue-communication-fidelity-batch-report.md"
TRAFFIC_JSON = OUTPUT_DIR / "paper-traffic-contract.json"
TASK_PROCESSING_JSON = OUTPUT_DIR / "paper-task-processing-contract.json"
TIMEOUT_JSON = OUTPUT_DIR / "paper-timeout-contract.json"
LINK_DELAY_JSON = OUTPUT_DIR / "paper-link-delay-contract.json"
QUEUE_FIDELITY_JSON = OUTPUT_DIR / "paper-queue-fidelity-contract.json"
PUBSUB_JSON = OUTPUT_DIR / "paper-pubsub-contract.json"
RECOVERY_JSON = OUTPUT_DIR / "paper-recovery-contract.json"
MIGRATION_JSON = OUTPUT_DIR / "migration-readiness-for-feature-068.json"
READY_NEXT_FEATURE = "Feature 068 — Paper Baseline Suite Batch"

