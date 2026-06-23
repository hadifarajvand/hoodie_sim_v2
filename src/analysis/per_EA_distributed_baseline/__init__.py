"""True per-EA distributed-agent baseline (paper-faithful reproduction).

Each Edge Agent (EA) gets its own online + target network, optimizer, replay
buffer, epsilon schedule, and target-sync counter — matching the paper's
distributed multi-agent description (Algorithm 1, §IV). This package implements
ONLY the paper-faithful distributed baseline; it does NOT add any proposed-method
logic (no EDF/LSTF, no new reward shaping, no new queue discipline/routing).

It reuses the existing environment, reward, reconciliation, metric schema, and
calibration/state profiles unchanged.
"""

from .config import DistributedBaselineConfig, build_distributed_config
from .paper_fidelity_audit import build_paper_distributed_agent_audit

__all__ = [
    "DistributedBaselineConfig",
    "build_distributed_config",
    "build_paper_distributed_agent_audit",
]
