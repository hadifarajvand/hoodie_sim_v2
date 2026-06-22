"""Config-only definition of the full HOODIE paper campaign (N_E=5000).

This package builds and emits the *configuration and runbook* for the full
paper-faithful campaign. It deliberately does NOT execute training. The 5000-
episode run is gated behind an explicit, separate operator action documented in
the runbook; importing or invoking this package never starts training.
"""

from .config import FullPaperCampaignConfig, build_full_campaign_config
from .estimates import build_estimates
from .guards import all_guards_pass, claim_safety, validate_config
from .runbook import build_runbook
from .runner import write_all_artifacts

__all__ = [
    "FullPaperCampaignConfig",
    "build_full_campaign_config",
    "build_runbook",
    "write_all_artifacts",
    "build_estimates",
    "validate_config",
    "all_guards_pass",
    "claim_safety",
]
