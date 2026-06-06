# Contract: Adaptive Policy and Offloading Decisions

## Policy Context Enrichment

### `build_adaptive_context(policy_context, traffic_summary=None, execution_summary=None)`

Inputs:
- `policy_context`: existing `PolicyContext`
- `traffic_summary`: optional mapping or summary object with observed load metadata
- `execution_summary`: optional mapping or summary object with compute/load metadata

Output:
- `AdaptiveDecisionContext` or equivalent immutable decision bundle

Requirements:
- Must not mutate environment state.
- Must preserve the incoming legal action mask.
- Must tolerate missing optional summaries.
- Must derive only from current observation and explicitly supplied summaries.

## Adaptive Policy Interface

### `AdaptiveOffloadingPolicy.choose_action(context)`

Inputs:
- enriched adaptive context or compatible policy context

Output:
- one legal action string for the active task

Requirements:
- Must choose only legal actions.
- Must be deterministic for identical inputs.
- Must not inspect future trace data.
- Must not silently remap illegal requests.
- Must support local, horizontal, and vertical action families.

## Canonical Fallback Behavior

If adaptive fields are absent or tied, the policy must use this order:

1. `local` / `compute_local`
2. `horizontal` / `offload_horizontal`
3. `vertical` / `offload_vertical`

This fallback is assumption-backed and must be documented as such if no paper equation is recovered.

## Compatibility

- Existing policies continue to use the existing `PolicyContext` path.
- No special environment mode is introduced.
- No metric formulas are changed by this feature.
