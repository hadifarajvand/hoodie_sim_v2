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

Top-level JSON schema keys for `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json`:

- `schema_version`
- `feature_id`
- `source_gates`
- `paper_backed_defaults`
- `link_rate_controls`
- `transmission_delay_contract`
- `unit_conversions`
- `monotonicity_checks`
- `unsupported_controls`
- `remaining_blockers`
- `topology_boundaries`
- `no_curve_fitting`
- `no_topology_fabrication`
- `no_policy_or_metric_redesign`
- `no_training_or_dependency_drift`
- `generated_artifacts`
- `validation_summary`

Required nested fields:

- `paper_backed_defaults.horizontal_data_rate_mbps`
- `paper_backed_defaults.vertical_data_rate_mbps`
- `paper_backed_defaults.cloud_data_rate_status`
- `paper_backed_defaults.source_registry_path`
- `link_rate_controls.horizontal_control_status`
- `link_rate_controls.vertical_control_status`
- `link_rate_controls.per_edge_control_status`
- `link_rate_controls.cloud_control_status`
- `link_rate_controls.public_config_entrypoint`
- `transmission_delay_contract.formula`
- `transmission_delay_contract.payload_unit`
- `transmission_delay_contract.rate_unit`
- `transmission_delay_contract.output_seconds`
- `transmission_delay_contract.output_slots`
- `transmission_delay_contract.slot_duration_seconds`
- `transmission_delay_contract.slot_rounding_policy`
- `transmission_delay_contract.invalid_rate_policy`
- `transmission_delay_contract.zero_payload_policy`
- `unit_conversions.bits_per_mbit`
- `unit_conversions.bps_per_mbps`
- `unit_conversions.seconds_to_slots_policy`
- `unit_conversions.slots_to_seconds_policy`
- `monotonicity_checks.horizontal`
- `monotonicity_checks.vertical`
- `monotonicity_checks.per_edge_if_supported`
- `unsupported_controls.control_name`
- `unsupported_controls.reason`
- `unsupported_controls.evidence_source`
- `remaining_blockers.blocker_id`
- `remaining_blockers.blocker_type`
- `remaining_blockers.reason`
- `topology_boundaries.figure_7_adjacency_status`
- `topology_boundaries.legal_horizontal_destinations_status`
- `topology_boundaries.paper_topology_injected`

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
