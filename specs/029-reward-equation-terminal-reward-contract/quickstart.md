# Quickstart: Reward Equation and Terminal Reward Contract

## Inputs

- Paper OCR: `resources/papers/hoodie/ocr/merged.tex`
- Parameter registry: `resources/papers/hoodie/recovered/paper-parameter-registry.json`
- Mechanism registry: `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`
- Offload lifecycle instrumentation: `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`
- Computation-delay unit validation: `artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json`

## Expected Outputs

- `artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json`
- `artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.md`

## Validation Flow

1. Recover Eq. (20)-(24) into normalized reward evidence records.
2. Audit runtime reward timing in `src/environment/gym_adapter.py` and `src/environment/reward_timing.py`.
3. Inspect `src/environment/offload_trace_ledger.py` and `src/environment/offload_trace_schema.py` to confirm terminal trace linkage.
4. Inspect `src/training/delayed_reward_training.py` read-only to ensure no training-side contract mutation is required.
5. Generate the report artifact pair and classify the runtime status.
6. Run targeted tests that prove:
   - completion reward is negative delay cost
   - dropped/thrown reward is `-40`
   - no-task reward is omitted / NaN-classified
   - `selected_action` does not emit reward
   - `reward_emitted` follows terminal lifecycle events
   - trace linkage can reconstruct the originating task/action

## Interpretation Rules

- `paper_matched` only if the runtime reward path and terminal timing are validated by tests.
- `assumption_backed` if aggregation or algebraic formatting must be normalized beyond explicit OCR support.
- `divergent` if runtime reward sign, timing, or terminal linkage disagrees with paper-backed behavior.
- `blocked` if the contract cannot be validated without training code or forbidden scope expansion.

## Validation Commands Run

- `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_reward_equation_terminal_reward_contract_recovery tests.unit.test_reward_equation_terminal_reward_contract_aggregation tests.unit.test_reward_equation_terminal_reward_contract_sign tests.integration.test_reward_equation_terminal_reward_contract_timing tests.integration.test_reward_equation_terminal_reward_contract_report tests.integration.test_reward_equation_terminal_reward_contract_scope_guard tests.integration.test_reward_equation_terminal_reward_contract_regressions tests.integration.test_offload_instrumentation_trace_regression tests.unit.test_offload_instrumentation_feature019_regression tests.unit.test_offload_instrumentation_feature024_regression tests.integration.test_offload_instrumentation_no_behavior_change tests.integration.test_environment_lifecycle_reference_alignment`
- `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python - <<'PY' import json, pathlib; json.loads(pathlib.Path('artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json').read_text()) PY`
- `git diff --name-only`

## Result

- Generated artifacts:
  - `artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json`
  - `artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.md`
- Final verdict: `paper_backed_with_assumption_backed_aggregation`
- Unrecoverable items:
  - Figure 7 adjacency remains unrecoverable and is not fabricated
- Assumption-backed items:
  - exact multi-agent reduction order
- Unresolved risks:
  - none in the reward-contract scope beyond the assumption-backed aggregation order
- Drift confirmation:
  - no training, dependency, policy, or topology drift occurred in this feature
