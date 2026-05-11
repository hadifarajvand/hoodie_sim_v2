# Research: Link-Rate Control and Transmission Delay Contract

## Source Gates

- Feature 020 already classified `link_rate` as an `instrumentation_gap`; this feature exists to add a public control contract, not to pretend the gap never existed.
- Feature 025 recovered the paper-backed horizontal and vertical defaults:
  - horizontal data rate = `30 Mbps`
  - vertical data rate = `10 Mbps`
  - cloud data rate remains unrecoverable
  - Figure 7 adjacency remains unrecoverable
- Feature 026 added lifecycle observability and provides the trace surfaces this feature must not break.

## Findings

1. The environment already exposes a public Gym-style boundary in `src/environment/gym_adapter.py`.
2. Link-rate control is not currently a first-class public config contract; it must be introduced without changing policy selection or reward semantics.
3. The structured registry package already owns the recovered paper defaults and unrecoverable statuses. That is the correct source of truth for horizontal and vertical defaults.
4. Transmission delay can be expressed deterministically as `delay_seconds = payload_bits / data_rate_bps`, but the repo needs an explicit rounding and slot conversion policy if slots are reported.
5. Per-edge/offload control is not safely supported by the current evidence. It must remain blocked unless a runtime-backed non-paper hook can prove legality.

## Open Constraints

- Cloud rate is unrecoverable and must stay unrecoverable unless paper evidence exists.
- Figure 7 adjacency is unrecoverable and must not be reconstructed from simulator behavior.
- Legal horizontal destinations remain non-paper-backed; any control contract must not claim otherwise.
- No policy redesign, metric redesign, training, or campaign reruns are allowed.

## Decision

Implement a public link-rate contract for horizontal and vertical defaults only, backed by explicit conversion helpers and deterministic validation artifacts. Keep per-edge/offload control unsupported unless the environment can expose a legal runtime hook without topology fabrication.
