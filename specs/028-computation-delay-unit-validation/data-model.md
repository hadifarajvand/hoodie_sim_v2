# Data Model: Computation Delay and CPU Unit Validation

## Entities

### UnitEvidenceRecord
- `name`: semantic label for the quantity
- `source`: registry, OCR, runtime config, or report
- `value`: recovered numeric or textual value
- `unit`: associated unit string
- `status`: `recovered`, `unrecoverable`, or `mismatched`
- `notes`: evidence and caveat summary

### SlotDurationContract
- `paper_delta_seconds`: recovered paper slot duration
- `runtime_delta_seconds`: current runtime slot duration
- `feature_027_reported_slot_duration_seconds`: slot duration recorded by Feature 027 report
- `status`: `matched`, `repaired`, `blocked`, or `mismatched`
- `rounding_policy`: explicit seconds-to-slots policy
- `affected_formulas`: formulas that depend on Δ

### ComputationDelayContract
- `task_size_unit`: expected task-size unit, typically Mbits
- `processing_density_unit`: expected processing-density unit, gigacycles/Mbit
- `cycles_required_formula`: explicit formula from task size and density
- `completion_slot_formula`: explicit formula from delay and slot duration
- `zero_delay_policy`: how zero delay is represented
- `deadline_interaction`: how deadlines affect completion-slot evaluation

### CPUCapacityContract
- `ea_private_capacity`: private EA CPU capacity evidence
- `ea_public_capacity`: public EA CPU capacity evidence
- `cloud_capacity`: cloud CPU capacity evidence
- `status`: `recovered` or `unrecoverable`

### RuntimeUnitContract
- `compute_config_path`: path to the current compute configuration source
- `traffic_config_path`: path to the current traffic configuration source
- `link_rate_config_path`: path to the current link-rate configuration source
- `runtime_slot_duration_seconds`: slot duration exposed by runtime config
- `runtime_slot_duration_source`: `paper-backed`, `assumption-backed`, `derived`, or `unrecoverable`
- `runtime_timeout_slots`: timeout contract value from runtime config
- `runtime_timeout_source`: provenance of the timeout contract
- `runtime_task_size_unit`: runtime task-size unit
- `runtime_processing_density_unit`: runtime processing-density unit
- `runtime_cpu_capacity_fields`: runtime CPU-capacity fields, if present
- `runtime_contract_classification`: overall classification of the runtime compute/time contract

### ValidationSummary
- `recovered_items`
- `unrecoverable_items`
- `mismatched_items`
- `repaired_items`
- `blocked_items`
- `regression_checks`

## Validation Rules
- CPU capacities must never be invented if the paper registry lacks evidence.
- Paper and runtime Δ must be compared directly.
- Seconds-to-slots conversion must be deterministic and documented.
- Completion-slot calculation must be reproducible across repeated runs.
- If runtime correction is applied, regression tests must prove Feature 027 behavior remains intact.

## Report Schema Contract

`unit-validation-report.json` MUST include:
- `schema_version`
- `feature_id`
- `source_gates`
- `paper_unit_evidence`
- `runtime_unit_contract`
- `slot_duration_audit`
- `computation_delay_contract`
- `cpu_capacity_contract`
- `completion_slot_contract`
- `mismatch_findings`
- `repaired_items`
- `unrecoverable_items`
- `regression_checks`
- `no_curve_fitting`
- `no_policy_or_training_drift`
- `generated_artifacts`
- `validation_summary`

### Runtime Contract Contract

`runtime_unit_contract` MUST include:
- `compute_config_path`
- `traffic_config_path`
- `link_rate_config_path`
- `runtime_slot_duration_seconds`
- `runtime_slot_duration_source`
- `runtime_timeout_slots`
- `runtime_timeout_source`
- `runtime_task_size_unit`
- `runtime_processing_density_unit`
- `runtime_cpu_capacity_fields`
- `runtime_contract_classification`

### Slot Duration Audit Contract

`slot_duration_audit` MUST include:
- `paper_delta_seconds`
- `runtime_delta_seconds`
- `feature_027_reported_slot_duration_seconds`
- `mismatch_status`
- `required_action`
