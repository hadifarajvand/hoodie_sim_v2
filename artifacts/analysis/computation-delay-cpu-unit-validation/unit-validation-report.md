# Computation Delay / CPU Unit Validation Report

- schema_version: `1.0`
- feature_id: `028-computation-delay-cpu-unit-validation`

## Slot Duration Audit
- paper_delta_seconds: `0.1`
- runtime_delta_seconds: `0.1`
- feature_027_reported_slot_duration_seconds: `0.1`
- mismatch_status: `matched`
- required_action: `none`

## Runtime Unit Contract
- compute_config_path: `src/environment/compute_config.py`
- traffic_config_path: `src/environment/traffic_config.py`
- link_rate_config_path: `src/environment/link_rate_config.py`
- runtime_slot_duration_seconds: `{'traffic_config': 0.1, 'link_rate_config': 0.1}`
- runtime_timeout_slots: `20`
- runtime_task_size_unit: `Mbits`
- runtime_processing_density_unit: `gigacycles/Mbit`

## Validation Summary
Task size and processing density are paper-backed; CPU capacities remain unrecoverable; paper Δ=0.1 sec, runtime Δ=0.1 sec, Feature 027 reported Δ=0.1 sec; mismatch_status=matched; required_action=none.
