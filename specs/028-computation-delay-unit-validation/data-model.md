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
