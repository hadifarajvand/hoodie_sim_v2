from __future__ import annotations

from .common import fallback_action, first_legal_placement_action
from .policy_interface import PolicyContext, SharedPolicy


class HorizontalOffloadingPolicy(SharedPolicy):
    """Prefer horizontal offloading when the legal action mask allows it.

    Delegates to ``common.first_legal_placement_action`` which consults
    ``context.legal_action_mask`` to ensure every returned action is legal
    under the topology-constrained mask.  Fallback follows the same documented
    order used by FLC and VO (local → horizontal → vertical).
    """

    def choose_action(self, context: PolicyContext) -> str:
        preferred = first_legal_placement_action(context, "horizontal")
        if preferred is not None:
            return preferred
        return fallback_action(context)