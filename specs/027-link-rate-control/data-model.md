# Data Model: Link-Rate Control and Transmission Delay Contract

## Entities

### LinkRateConfig

Represents the public, config-backed rate controls available to HOODIE experiments.

Fields:
- `horizontal_data_rate_bps`: required, positive, public default/control for horizontal offload
- `vertical_data_rate_bps`: required, positive, public default/control for vertical offload
- `cloud_data_rate_bps`: optional, must remain unrecoverable unless paper evidence exists
- `per_edge_link_rates`: optional mapping, unsupported unless a runtime-backed non-paper hook exists
- `slot_duration_seconds`: required, positive, explicit slot duration for second/slot conversion

### ConversionRule

Represents a deterministic conversion between named unit families.

Fields:
- `from_unit`: one of `bits`, `Mbits`, `bps`, `Mbps`, `seconds`, `slots`
- `to_unit`: one of `bits`, `Mbits`, `bps`, `Mbps`, `seconds`, `slots`
- `factor`: numeric conversion factor or explicit rounding policy when conversion is slot-based
- `rounding_policy`: one of `exact`, `ceil`, `floor`, `round_half_up` as explicitly chosen by the contract

### TransmissionDelayContract

Represents the deterministic calculation of transmission delay for a payload and rate.

Fields:
- `payload_bits`: normalized payload size in bits
- `data_rate_bps`: normalized link rate in bits per second
- `delay_seconds`: computed as `payload_bits / data_rate_bps`
- `delay_slots`: derived from `delay_seconds / slot_duration_seconds` using the documented rounding policy
- `status`: `supported`, `unsupported`, or `blocked`
- `reason`: human-readable explanation when unsupported or blocked

### LinkRateValidationArtifact

Represents the deterministic validation output proving controlled rate changes affect delay.

Fields:
- `schema_supported_events`
- `observed_default_audit_events`
- `observed_synthetic_fixture_events`
- `default_runtime_classification`
- `synthetic_fixture_trace_visibility`
- `remaining_topology_blockers`
- `paper_topology_status`
- `no_paper_topology_fabrication`
- `monotonicity_result`
- `unit_conversion_results`

## Invariants

1. Supported horizontal and vertical rates must be positive.
2. Zero or negative rates must fail loudly.
3. Zero payload must produce a defined delay result, not a silent divide-by-zero path.
4. Slot conversion must be explicit and deterministic.
5. Per-edge/offload rates must never be invented from paper topology gaps.
6. Any reported paper-backed default must cite the recovered registry source.

## Relationships

- `LinkRateConfig` feeds `TransmissionDelayContract`.
- `ConversionRule` is used by both config validation and delay reporting.
- `LinkRateValidationArtifact` summarizes the observable outcome of the contract and its tests.
