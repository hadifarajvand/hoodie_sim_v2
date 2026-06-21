"""Paper-faithful simulation production pipeline (Feature 080).

This package provides:
  * A paper-component alignment audit of the HOODIE-style simulator.
  * A root-cause analysis of the Feature 072 reward/terminal reconciliation
    failure.
  * A corrected, horizon-aware reward/terminal reconciliation (Repair A) that
    is analysis-only and does NOT modify environment, reward, or policy
    semantics.
  * A single paper-compatible metric schema shared by baselines and candidates.

Claim-safety: this pipeline makes no paper-reproduction or superiority claims.
"""

from .reconciliation import (
    REWARD_RECONCILIATION_TOLERANCE,
    horizon_aware_reconciliation,
    horizon_aware_recovered_reconciliation,
    reward_bearing_task,
)
from .schema import PAPER_COMPATIBLE_METRIC_FIELDS, build_paper_compatible_metric

__all__ = [
    "REWARD_RECONCILIATION_TOLERANCE",
    "horizon_aware_reconciliation",
    "horizon_aware_recovered_reconciliation",
    "reward_bearing_task",
    "PAPER_COMPATIBLE_METRIC_FIELDS",
    "build_paper_compatible_metric",
]
