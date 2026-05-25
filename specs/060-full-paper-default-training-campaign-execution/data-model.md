# Data Model: Feature 060

## Report

Represents the controlled run result authorized by Feature 059.

Required fields:

- feature_id
- prerequisite_tags_verified
- feature_059_gate_verified
- campaign_execution_summary
- training_metrics_summary
- evaluation_metrics_summary
- baseline_evaluation_summary
- checkpoint_metadata_summary
- artifact_manifest_summary
- resource_control_summary
- safety_summary
- remaining_blockers
- recommended_next_feature
- final_verdict

## Main summaries

`campaign_execution_summary` records actual run counts, configured budgets, seed bundle, trace-bank IDs, and completion status.

`training_metrics_summary` records optimizer steps, replay size, loss summary, reward summary, target update summary, and action summary.

`evaluation_metrics_summary` records evaluation trace-bank usage and metric schema coverage.

`baseline_evaluation_summary` records baseline policy metrics using the Feature 058 baseline registry.

`checkpoint_metadata_summary` records metadata, not paper claims.

`artifact_manifest_summary` lists all required output artifacts and validates that each one exists.

`resource_control_summary` records runtime limits, output directory, and deterministic seed controls.

`safety_summary` records no reproduction claim, no superiority claim, no uncontrolled loop, no dependency drift, no policy drift, no environment drift, no reward timing drift, and no prior artifact rewrite.
