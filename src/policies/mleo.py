from __future__ import annotations

from dataclasses import dataclass, field

from .common import fallback_reason, horizontal_destinations, legal_actions, source_agent_id
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class MinimumLatencyEstimateOffloadingPolicy(SharedPolicy):
    last_fallback_reason: str | None = None

    def choose_action(self, context: PolicyContext) -> str:
        observation = context.observation if isinstance(context.observation, dict) else {}
        queue_delay_estimates = observation.get("queue_delay_estimates")
        placement_candidates = observation.get("mleo_placement_candidates")
        source = source_agent_id(context)
        legal = legal_actions(context)
        candidates: list[tuple[float, str]] = []

        if isinstance(placement_candidates, dict) and isinstance(queue_delay_estimates, dict):
            for family, options in placement_candidates.items():
                if not isinstance(options, (list, tuple)):
                    continue
                for option in options:
                    option_str = str(option)
                    if not context.legal_action_mask.get(option_str, False):
                        continue
                    estimate = queue_delay_estimates.get(option_str)
                    if estimate is None:
                        continue
                    candidates.append((float(estimate), option_str))
            if source is not None:
                for destination in horizontal_destinations(context):
                    if destination == source or not context.legal_action_mask.get(destination, False):
                        continue
                    estimate = queue_delay_estimates.get(destination)
                    if estimate is not None:
                        candidates.append((float(estimate), destination))
        else:
            self.last_fallback_reason = fallback_reason(context, "mleo", detail="fallback: missing placement candidates or queue delay estimates")

        if candidates:
            candidates.sort(key=lambda item: (item[0], item[1]))
            return candidates[0][1]

        legal_order = [action for action in ("local", "compute_local", "cloud", "vertical", "offload_vertical") if context.legal_action_mask.get(action, False)]
        legal_order.extend(destination for destination in horizontal_destinations(context) if destination != source and context.legal_action_mask.get(destination, False))
        if legal_order:
            if self.last_fallback_reason is None:
                self.last_fallback_reason = fallback_reason(context, "mleo", detail="fallback: insufficient placement data; using compatibility fallback")
            return legal_order[0]

        if legal:
            self.last_fallback_reason = fallback_reason(context, "mleo", detail="fallback: no ranked placement candidates were legal; using first legal action")
            return legal[0]
        raise ValueError("No legal actions available")
