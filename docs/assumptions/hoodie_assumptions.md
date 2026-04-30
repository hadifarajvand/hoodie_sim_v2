# HOODIE Assumptions Log

## A-001: Exact reward scaling

- Missing detail: Exact reward formula and any reward scaling are not fully recoverable from the
  currently available paper text.
- Chosen value or rule: Do not infer a reward formula yet.
- Justification: The constitution forbids undocumented assumptions.
- Expected impact: Training and evaluation logic must not rely on a guessed reward scale.
- Validation plan: Resolve from the source PDF before any reward-dependent implementation uses it.

## A-002: Evaluation trace bank contents

- Missing detail: Exact trace-bank contents or workload seed set are not explicitly recoverable.
- Chosen value or rule: Use a recorded trace identifier or seed identifier only after it is defined
  from the source material.
- Justification: Trace reproducibility must be explicit and auditable.
- Expected impact: Evaluation replay remains blocked from inventing trace contents.
- Validation plan: Record the selected trace-bank identifiers once source-backed values are known.

## A-003: Topology size and scenario configuration

- Missing detail: Exact topology size, node counts, and scenario configuration details for the
  reported experiments are not yet fully resolved.
- Chosen value or rule: Keep the implementation generic until paper-backed values are recovered.
- Justification: The environment must not depend on undocumented scenario assumptions.
- Expected impact: Topology and environment structure remain parameterized but unfilled.
- Validation plan: Fill from the source PDF before any scenario-specific runs.

## A-004: Task-generation distributions

- Missing detail: Exact task-generation distributions are not fully recovered from the available
  project resources.
- Chosen value or rule: Record the gap; do not hardcode a distribution.
- Justification: Task generation is a paper-dependent assumption.
- Expected impact: Environment tests remain structural only for Phase 1.
- Validation plan: Recover from the source PDF or mark as unresolved.

## A-005: Baseline action selection heuristics

- Missing detail: The repository artifacts do not fully specify the exact decision rule for RO, HO,
  VO, MLEO, and BCO beyond their names and their required legal/topology constraints.
- Chosen value or rule: Implement each baseline as the minimal paper-compatible heuristic implied by
  its label: RO selects uniformly among legal actions; FLC selects the local action only; HO selects
  a horizontal offload only; VO selects a vertical offload only; MLEO selects the legal action with
  the lowest observed latency estimate when such an estimate is present in the observation and
  otherwise falls back to the first legal offload action; BCO selects the lowest-cost legal action
  from the observation's reported balance or cooperation hint when present and otherwise falls back
  to local execution.
- Justification: The approved artifacts require the baselines but do not provide a fully recoverable
  implementation recipe in the current repository context.
- Expected impact: Baseline modules remain minimal and auditable, while any future paper-backed
  clarification can replace the fallback rules without changing the shared interface.
- Validation plan: Revisit these heuristics if the source paper or OCR yields explicit baseline
  definitions that differ from the chosen rules.

## A-006: Deterministic evaluation trace generation

- Missing detail: The current project artifacts do not fully specify the exact trace-bank format or
  the exact task-arrival replay mechanism used for evaluation runs.
- Chosen value or rule: Generate deterministic evaluation traces from the supplied seed or trace
  identifier, and require all compared policies to consume the same generated trace for a given run.
- Justification: The evaluation pipeline must be reproducible and fair even before a paper-backed
  trace bank is fully recovered.
- Expected impact: Evaluation results are traceable by seed or trace identifier and comparable
  across policies.
- Validation plan: Replace this fallback with paper-backed trace-bank replay if the source material
  later defines a stricter trace protocol.

## A-007: Centralized metric definitions

- Missing detail: The approved artifacts do not fully spell out the exact evaluation formulas for
  average delay, throughput, and drop ratio.
- Chosen value or rule: Compute average delay as the mean completion delay over completed tasks only;
  compute drop ratio as dropped tasks divided by total tasks; compute throughput as the count of
  completed tasks.
- Justification: The evaluation module needs deterministic, centralized definitions before any
  plotting or downstream analysis is added.
- Expected impact: All policies are compared using the same metric formulas and raw metrics remain
  reproducible.
- Validation plan: Revisit the formulas if the source PDF or OCR gives a different paper-defined
  metric definition.

## A-008: Shared-path evaluation ceiling

- Missing detail: The current implementation phase does not yet provide a fully faithful shared
  environment replay path for evaluation beyond the available slot-engine and task-level
  abstractions.
- Chosen value or rule: Keep the evaluation runner aligned with the shared environment/slot path as
  far as current phases allow, and document any remaining synthetic trace or policy-input fallback
  behavior explicitly.
- Justification: The correction tasks require reducing synthetic shortcuts without inventing absent
  simulator behavior.
- Expected impact: Evaluation remains reproducible and auditable while avoiding premature claims of
  full environment fidelity.
- Validation plan: Replace remaining fallback behavior with environment-backed replay when the
  implemented simulator phases provide it.

## A-009: Shared runtime timing model

- Missing detail: The current repository does not yet fully recover the paper-backed slot-duration,
  queue-service-capacity, and timeout timing parameters needed for a richer shared runtime model.
- Chosen value or rule: Use currently available paper-backed values where recoverable and keep any
  remaining timing parameters documented as explicit assumptions in the shared runtime module.
- Justification: The evaluation and environment layers need a shared timing ownership path that is
  richer than a density-only placeholder.
- Expected impact: Runtime progression can account for waiting, offloading, service, and terminal
  resolution in slot form without pretending the paper parameters are fully known.
- Validation plan: Replace the assumptions with paper-backed values if later recovered from the
  source PDF or OCR.

## A-010: Runtime capacity-to-delay mapping and timeout grace

- Missing detail: The source artifacts do not fully specify how service capacity should translate
  into slot-level delay, nor whether any timeout grace window is present in the paper-backed model.
- Chosen value or rule: Map higher service capacity to lower shared-runtime service delay using the
  shared runtime module, and default timeout grace to zero until a paper-backed value is recovered.
- Justification: The shared runtime model needs an explicit, testable rule instead of a density-only
  placeholder, and the simulator must not invent an unlogged timeout allowance.
- Expected impact: Destination-specific service timing can differ across local, public, and cloud
  paths without claiming a paper-exact parameterization that is not yet recovered.
- Validation plan: Replace the mapping or grace default if the source PDF or OCR provides a stricter
  paper-backed rule.

## A-011: HOODIE agent architecture skeleton

- Missing detail: The staged artifacts do not fully specify the exact HOODIE agent history tensor
  layout, layer widths, or target-network synchronization mechanics needed for a faithful
  implementation.
- Chosen value or rule: Use a minimal architecture skeleton with a configurable history window, a
  replay buffer, a target-network copy/update wrapper, and pure dueling/double-DQN selection
  helpers without adding training behavior.
- Justification: Phase 6 requires the agent architecture to exist, but the repository does not
  recover enough detail to claim paper-exact network internals.
- Expected impact: HOODIE entrypoints can run through the shared policy interface while remaining
  clearly structural rather than training-driven.
- Validation plan: Replace the skeleton components if the source paper later yields exact history
  and network-shape details.

## A-012: HOODIE reward definition

- Missing detail: The staged artifacts recover the paper reward structure, but the exact closed-form
  expression for \(\Phi_n(t)\) is still not fully recovered outside the paper's verbal definition.
- Chosen value or rule: Use the paper-backed reward semantics from the cost function: reward is
  NaN when no task arrives, `-Phi_n(t)` when a task is successfully processed before deadline, and
  `-C` when the task is dropped; `C = 40` from Table 4. In the current implementation,
  `Phi_n(t)` is approximated as `(completion_slot - arrival_slot)` unless an exact recovered formula
  is documented elsewhere.
- Justification: The paper defines reward as the environment-returned cost signal, so training must
  consume that emitted value rather than invent a new scalar.
- Expected impact: Training orchestration remains reward-gated by environment timing, and the reward
  meaning itself is paper-backed while the \(\Phi_n(t)\) approximation stays explicitly documented.
- Validation plan: Revisit only if a later source contradicts the OCR-recovered cost function, the
  table-provided penalty constant, or the documented \(\Phi_n(t)\) approximation.

## A-013: Deterministic untrained HOODIE action scoring

- Missing detail: The available paper-backed material does not yet recover a faithful trained
  inference path for HOODIE, but the implementation still needs a deterministic untrained fallback
  so legal actions can be scored without collapsing to the first legal action.
- Chosen value or rule: Use the evaluation observation's `fallback_hints` as deterministic action
  hints inside `HoodieModel.forward()`, with canonical scoring order local=1, horizontal=2,
  vertical=3 and alias handling for `compute_local`, `offload_horizontal`, and `offload_vertical`.
- Justification: The correction phase requires an auditable, deterministic model path that can
  distinguish legal actions before training is implemented, without inventing random tie-breaking
  or bypassing the model abstraction.
- Expected impact: Untrained HOODIE can select non-local legal actions deterministically while
  remaining constrained by the legal-action mask.
- Validation plan: Replace this fallback scoring rule with paper-backed learned action scoring once
  the full HOODIE training path is implemented.

## A-014: Deterministic HOODIE learning update rule

- Missing detail: The exact paper-equation learning update for HOODIE is not fully recovered.
- Chosen value or rule: Use a deterministic temporal-difference-style preference update in
  `HoodieModel.update_action_preference()`: for each sampled replay transition, update the selected
  action preference toward the observed delayed reward with
  `new_preference = old_preference + learning_rate * (reward - old_preference)`.
- Justification: The implementation needs a simple, auditable learning step that consumes delayed
  rewards and changes future scores without introducing hidden randomness or changing reward
  semantics.
- Expected impact: Delayed rewards and replay samples now influence future HOODIE action scores
  while remaining reproducible under fixed seeds and fixed replay order.
- Validation plan: Replace this assumption-backed update rule with the exact paper equation if and
  when it is recovered.

## A-015: TorchRL dependency boundary

- Missing detail: The current repository does not yet define the exact TorchRL-backed learner boundary and package availability contract for Phase 12.
- Chosen value or rule: Keep TorchRL and PyTorch as optional dependencies that are only required when `training.learner_type` is explicitly set to `torchrl`; validation-only and non-TorchRL fallback paths must not require them.
- Justification: The dependency boundary must be explicit, fail clearly, and avoid turning the entire reproduction workflow into a hard TorchRL dependency.
- Expected impact: Configs can remain backward compatible while Phase 12 preparation adds dependency checks without changing current HOODIE behavior.
- Validation plan: Add guard-level checks that reject TorchRL training when imports are unavailable and confirm that non-TorchRL paths still run.

## A-016: Deterministic learner-adapter fallback

- Missing detail: The current environment does not provide torch/torchrl, but Phase 12 still needs a learner-backed training slice that can be exercised deterministically.
- Chosen value or rule: Treat `training.learner_type = "learner_adapter"` as the explicit assumption-backed learner mode for the current repository state; it uses the dormant deterministic learner adapter without requiring torch or torchrl imports.
- Justification: The implementation must support a learner-backed packaging path now without lying about PyTorch availability or changing the default validation behavior.
- Expected impact: Training runs can produce learner_state-backed checkpoints in the current environment, while fallback non-learner runs remain unchanged.
- Validation plan: Replace or supersede this fallback once an actual TorchRL-backed training environment is available and verified.
