# Quickstart: Link-Rate Control and Transmission Delay Contract

## Purpose

Validate a public link-rate control contract for horizontal and vertical defaults, prove deterministic transmission-delay calculations, and preserve the hard boundary against fabricated per-edge/topology claims.

## Prerequisites

- Use the approved project interpreter.
- Keep the recovered registry artifacts available.
- Do not modify policy, metric, training, dependency, or campaign files.

## Validation Steps

1. Run the unit tests for conversion and delay math.
2. Run the integration tests for horizontal and vertical environment control.
3. Run the monotonicity test to confirm higher controllable rates do not increase delay for the same payload.
4. Run the regression test for Feature 026 trace instrumentation.
5. Run the scope-guard test to confirm unsupported controls are not silently fabricated.
6. Regenerate the link-rate contract report artifacts.

## Contract Checks

### Unit Conversion

- `bits <-> Mbits`
- `bps <-> Mbps`
- `seconds <-> slots`
- Slot duration must be explicit in the contract output.

### Transmission Delay

- Compute `delay_seconds = payload_bits / data_rate_bps`
- Convert to slots using the documented rounding policy
- Reject zero or negative rates loudly
- Handle zero payload explicitly

### Supported Scope

- Horizontal and vertical defaults are supported and public
- Cloud rate remains unrecoverable unless paper evidence exists
- Per-edge/offload control remains unsupported unless a runtime-backed non-paper hook exists

## Artifact Review

Inspect `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json` and `.md` to confirm:

- paper-backed defaults are recorded
- unsupported controls are labeled honestly
- monotonicity results are deterministic
- no paper-topology fabrication claim is made
