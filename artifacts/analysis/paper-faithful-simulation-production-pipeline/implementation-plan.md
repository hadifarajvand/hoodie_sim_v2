# Implementation plan (Feature 080)

requires_user_review_before_environment_semantic_change: `False`

## Step A: horizon-aware reward/terminal reconciliation
- scope: analysis_only
- files: ['src/analysis/paper_faithful_simulation_production_pipeline/reconciliation.py (new)']
- gate: gate_6_reward_reconciliation_passed && gate_7_terminal_reconciliation_passed
- risk: shared legacy evaluator unchanged to avoid regressing F067-072; corrected logic isolated.
- rollback: delete new module; no env/legacy code touched.

## Step B: state/profile integration consistency check
- scope: analysis_only
- files: ['src/analysis/paper_faithful_simulation_production_pipeline/ (consumes F072 evidence)']
- gate: gate_9_train_eval_state_profile_consistent
- risk: low
- rollback: n/a

## Step C: paper component alignment audit
- scope: analysis_only
- files: ['src/analysis/paper_faithful_simulation_production_pipeline/runner.py']
- gate: gate_2_paper_component_alignment_audited
- risk: low
- rollback: n/a

## Step D: production-style artifact + schema generation
- scope: analysis_only
- files: ['src/analysis/paper_faithful_simulation_production_pipeline/schema.py']
- gate: gate_8_metric_universe_consistency_passed
- risk: low
- rollback: n/a

## Step E_gated: integrated 50/100 reconciliation re-run (NOT executed this pass)
- scope: analysis_only_but_compute_heavy
- files: ['wires horizon_aware_reconciliation into a 50/100 evaluation campaign']
- gate: all gates -> safe_to_proceed_to_medium_training_smoke
- risk: compute; requires torch trainer + 6 policies x 100 eval episodes.
- rollback: discard run directory.

