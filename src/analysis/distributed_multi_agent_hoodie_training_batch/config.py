from __future__ import annotations

from pathlib import Path

FEATURE_ID = "066-distributed-multi-agent-hoodie-training-batch"
FEATURE_065_REPORT = Path("artifacts/analysis/paper-faithful-state-action-space-batch/paper-faithful-state-action-space-batch-report.json")
FEATURE_065_MIGRATION = Path("artifacts/analysis/paper-faithful-state-action-space-batch/migration-readiness-for-feature-066.json")
OUTPUT_DIR = Path("artifacts/analysis/distributed-multi-agent-hoodie-training-batch")
REPORT_JSON = OUTPUT_DIR / "distributed-multi-agent-hoodie-training-batch-report.json"
REPORT_MD = OUTPUT_DIR / "distributed-multi-agent-hoodie-training-batch-report.md"
PER_AGENT_REGISTRY_JSON = OUTPUT_DIR / "per-agent-registry.json"
PER_AGENT_REPLAY_JSON = OUTPUT_DIR / "per-agent-replay-contract.json"
PER_AGENT_POLICY_JSON = OUTPUT_DIR / "per-agent-policy-contract.json"
PER_AGENT_OPTIMIZER_TARGET_JSON = OUTPUT_DIR / "per-agent-optimizer-target-contract.json"
EPSILON_SCHEDULE_JSON = OUTPUT_DIR / "epsilon-schedule-contract.json"
SHARED_ENV_JSON = OUTPUT_DIR / "shared-environment-interaction-contract.json"
DELAYED_REWARD_JSON = OUTPUT_DIR / "delayed-reward-origin-assignment-contract.json"
MIGRATION_READINESS_JSON = OUTPUT_DIR / "migration-readiness-for-feature-067.json"
READY_NEXT_FEATURE = "Feature 067 — Paper Traffic, Queue, and Communication Fidelity Batch"

