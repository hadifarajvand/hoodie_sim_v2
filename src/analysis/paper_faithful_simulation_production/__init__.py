"""Paper-faithful simulation production pipeline.

Integrates: paper source audit, mechanism map, explicit profiles, a bounded
medium-smoke campaign (budgets [50, 100, 200, 300]), horizon-aware recovered
reconciliation, the paper-compatible metric schema, readiness gates, figures,
and reporting. Makes no paper-reproduction or superiority claims.
"""

from .metric_schema import PAPER_COMPATIBLE_METRIC_FIELDS, build_metric, validate_metric_schema
from .profiles import ProductionProfile

__all__ = [
    "PAPER_COMPATIBLE_METRIC_FIELDS",
    "build_metric",
    "validate_metric_schema",
    "ProductionProfile",
]
