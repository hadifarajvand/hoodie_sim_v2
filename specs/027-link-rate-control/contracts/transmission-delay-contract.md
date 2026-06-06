# Transmission Delay Contract

## Contract

For a payload of `payload_bits` transmitted over a link with rate `data_rate_bps`:

```text
delay_seconds = payload_bits / data_rate_bps
```

If the environment reports delay in slots, the slot value must be derived from the explicit slot duration:

```text
delay_slots = round_policy(delay_seconds / slot_duration_seconds)
```

The rounding policy must be documented in the validation artifact and remain deterministic.

## Required Behavior

- `data_rate_bps` must be positive.
- `payload_bits` may be zero, but the result must be explicit and non-ambiguous.
- Negative payload or rate values must fail loudly.
- The contract must support horizontal and vertical public defaults only.
- Per-edge/offload control remains unsupported unless a runtime-backed non-paper hook exists.

## Unit Mapping

- `1 bit = 1 bit`
- `1 Mbit = 1,000,000 bits`
- `1 bps = 1 bit / second`
- `1 Mbps = 1,000,000 bps`
- `seconds` to `slots` requires explicit `slot_duration_seconds`

## Validation Notes

- Higher controllable data rates must not increase delay for the same payload.
- The contract must not depend on curve fitting, simulated topology invention, or paper-validity claims.
