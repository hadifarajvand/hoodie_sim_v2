# Link-Rate Contract Report

- schema_version: `1.0`
- feature_id: `027-link-rate-control-transmission-delay-contract`

## Paper-Backed Defaults
- horizontal_data_rate_mbps: `30.0`
- vertical_data_rate_mbps: `10.0`
- cloud_data_rate_status: `unrecoverable`
- source_registry_path: `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json`

## Link-Rate Controls
- horizontal_control_status: `public_configured`
- vertical_control_status: `public_configured`
- per_edge_control_status: `unsupported_without_non_fabricated_evidence`
- cloud_control_status: `unrecoverable`
- public_config_entrypoint: `src/environment/link_rate_config.py`

## Transmission Delay Contract
- formula: `delay_seconds = payload_bits / data_rate_bps`
- output_seconds: `{'horizontal_default': 0.26666666666666666, 'vertical_default': 0.8}`
- output_slots: `{'horizontal_default': 1, 'vertical_default': 1}`
- slot_rounding_policy: `ceil`

## Unit Conversions
- bits_per_mbit: `1000000.0`
- bps_per_mbps: `1000000.0`
- seconds_to_slots_policy: `ceil`
- slots_to_seconds_policy: `exact_multiplication_by_slot_duration_seconds`

## Monotonicity Checks
- horizontal: True
- vertical: True
- per_edge_if_supported: unsupported

## Unsupported Controls
- per_edge_link_rates: Topology evidence is unrecoverable; non-fabricated per-edge control remains unsupported. (artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json)
- cloud_data_rate: Paper evidence does not recover a distinct cloud data-rate constant. (artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json)

## Remaining Blockers
- topology-figure-7 [paper_recovery_gap]: Figure 7 adjacency remains unrecoverable without fabrication.

## Topology Boundaries
- figure_7_adjacency_status: `unrecoverable`
- legal_horizontal_destinations_status: `non-paper-backed`
- paper_topology_injected: `False`

## Validation Summary
Recovered defaults are public and deterministic; unsupported per-edge/cloud controls remain blocked; monotonic delay checks pass for supported horizontal and vertical defaults; no paper-topology fabrication is claimed.
