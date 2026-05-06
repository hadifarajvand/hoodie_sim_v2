# Quickstart: Adaptive Policy and Offloading Decisions

## What this feature adds

An external adaptive offloading policy that consumes the same environment observation path as existing baselines, enriches it with optional traffic and compute summaries, and returns one legal action for the active task.

## Typical flow

1. Call `HoodieGymEnvironment.reset(seed=...)`.
2. Read the current observation from the environment.
3. Build `PolicyContext` from the observation and legal action mask.
4. Enrich it with `build_adaptive_context(...)` if traffic or execution summaries are available.
5. Call `AdaptiveOffloadingPolicy.choose_action(...)`.
6. Pass the returned action to `env.step(action)`.

## Example

```python
from src.policies.policy_interface import PolicyContext
from src.policies.adaptive_context import build_adaptive_context
from src.policies.adaptive_offloading import AdaptiveOffloadingPolicy

policy = AdaptiveOffloadingPolicy()
context = PolicyContext(observation=observation, legal_action_mask=legal_mask)
adaptive_context = build_adaptive_context(
    context,
    traffic_summary=traffic_summary,
    execution_summary=execution_summary,
)
action = policy.choose_action(adaptive_context)
next_observation, reward, terminated, truncated, info = env.step(action)
```

## Guardrails

- Do not run the policy inside `HoodieGymEnvironment`.
- Do not treat the policy as a learned controller.
- Do not inspect the full trace or hidden future arrivals.
- Use the canonical fallback order only when adaptive signals are missing or tied.

## Notes

- No dependency installation is required for this feature.
- No Gymnasium, ns-3, or ns-3-gym changes are needed.
- Existing baseline policies continue to use the same `PolicyContext` path.
- No dependency files were changed for this feature.
