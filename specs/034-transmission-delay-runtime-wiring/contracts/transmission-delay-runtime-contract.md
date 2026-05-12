# Transmission Delay Runtime Contract

## Purpose

Define the runtime boundary for transmission delay wiring in Feature 034.

## Contract

### Payload and Rate

- `task.size` is measured in Mbits.
- Transmission payload is computed as `payload_bits = mbits_to_bits(task.size)`.
- Horizontal offload uses `LinkRateConfig.horizontal_data_rate_bps`.
- Vertical offload uses `LinkRateConfig.vertical_data_rate_bps` / `cloud_facing_vertical_rate_mbps`.
- No separate cloud-specific transmission rate may be introduced.

### Delay Calculation

- `compute_transmission_delay()` is the single source of truth for `delay_slots`.
- `LinkRateConfig.rounding_policy` controls slot rounding.
- Default rounding remains `ceil`.

### Admission Boundary

- A task may enter downstream execution only when `current_slot >= transmission_started_at + transmission_delay_slots`.
- The environment records `transmission_started_at` when transmission begins.
- The environment records `transmission_completed_at` when the admission boundary is first satisfied.
- `SlotEngine` does not infer delay from queue age alone.

### Metadata

The runtime must record:
- `transmission_started_at`
- `transmission_completed_at`
- `transmission_delay_slots`
- `transmission_delay_seconds`
- `transmission_payload_bits`
- `transmission_data_rate_bps`
- `transmission_rate_source`

### Scope Limits

- No execution-capacity changes.
- No topology legality changes.
- No public/cloud capacity-sharing redesign.
- No reward equation changes.
- No baseline campaign reruns.
- No training or policy redesign.
