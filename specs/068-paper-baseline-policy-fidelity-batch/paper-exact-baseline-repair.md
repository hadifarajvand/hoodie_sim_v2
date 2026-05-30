# Paper-Exact Baseline Repair Contract

## Purpose

Feature 068 is merged at family-level baseline fidelity. This repair contract upgrades the next implementation pass toward paper placement fidelity without changing simulator internals.

## Paper Targets

- RO: choose between local, vertical, and horizontal families with equal family probability when all are available. If horizontal is chosen, choose a non-source destination EA uniformly when concrete destination actions are available.
- FLC: always prefer local compute when available.
- VO: always prefer Cloud placement when available.
- HO: always prefer horizontal placement to another EA. When multiple destination EAs are available, select among concrete destination actions rather than returning only the horizontal family.
- BCO: rotate over concrete placements in paper order: local, Cloud, then the other EAs in deterministic order.
- MLEO: compare N+1 placement options: private queue, each other EA public queue, and Cloud. Select the available placement with lowest total estimated delay.

## Compatibility Rule

If current PolicyContext exposes only family-level actions, policies may keep family fallback behavior, but tests and PR notes must mark that path as compatibility fallback. It must not be described as paper-exact destination fidelity.

## Expected Context Inputs

Implementation may consume these fields from PolicyContext.observation when present:

- `source_agent_id`
- `edge_agent_ids`
- `cloud_id`
- `placement_actions`
- `horizontal_destinations`
- `cloud_action`
- `local_action`
- `mleo_placement_candidates`
- `queue_delay_estimates`
- `fallback_hints`

The repair must not require environment changes. If the runtime does not expose these fields, Codex must implement explicit compatibility fallback or report a blocker.

## Required Test Evidence

- RO concrete-destination sampling is reproducible with a seed.
- HO never selects the source EA as destination.
- BCO sequence follows local, Cloud, other EAs, then repeats.
- MLEO ranks N+1 placement candidates on a deterministic small topology.
- MLEO excludes unavailable candidates before ranking.
- Missing placement or queue data produces a visible fallback reason.
- Scope audit confirms no environment, training, artifact, campaign, dependency, or lock files changed.
