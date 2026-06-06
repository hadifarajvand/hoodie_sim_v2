---

description: "Task list for hoodie reproduction feature"
---

# Tasks: 001-hoodie-reproduction

**Input**: Design documents from `/specs/001-hoodie-reproduction/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Organization**: Tasks are grouped by implementation phase to preserve the required build order
and keep the simulator, policies, evaluation, training, and analysis separated.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel if it does not depend on incomplete tasks
- File paths must be explicit in every task

## Phase 1: Environment and Core Simulation

**Purpose**: Establish the shared simulator foundation used by every baseline and by HOODIE.

- [X] T001 Start the assumptions log with the current paper gaps and approved defaults in `docs/assumptions/hoodie_assumptions.md`
- [X] T002 Record the paper source, OCR references, and simulator reference usage policy in `docs/paper_notes/hoodie_resource_log.md`
- [X] T003 Start the paper-to-code mapping with the current paper section, equation, and table references in `docs/paper_notes/paper_to_code_mapping.md`
- [X] T004 Define the task entity model with timeout length, absolute deadline, selected action, resolved destination, terminal outcome, and reward-emitted state in `src/environment/task.py`
- [X] T005 Define the topology model and legal connectivity rules in `src/environment/topology.py`
- [X] T006 Define the shared environment state container in `src/environment/environment.py` so it stores only the minimal required runtime state, separates task state, queue state, topology state, and metric state, does not duplicate queue logic or policy logic, and remains a coordination structure rather than a dumping ground for unrelated logic
- [X] T007 Add unit tests for task lifecycle state transitions in `tests/unit/test_task_lifecycle.py`
- [X] T008 Add unit tests for topology legality and masked-action eligibility in `tests/unit/test_topology_legality.py`

## Phase 2: Queue Systems and Timing Logic

**Purpose**: Implement queue behavior, slot progression, deadline semantics, and delayed rewards.

- [X] T009 Implement private queue FIFO behavior and waiting-time bookkeeping in `src/environment/private_queue.py`
- [X] T010 Implement offloading queue behavior with resolved destination and transmission/service waiting state in `src/environment/offloading_queue.py`
- [X] T011 Implement public queue identity and FIFO routing by `(host_node_id, source_agent_id)` in `src/environment/public_queue.py`
- [X] T012 Implement the slot execution engine for the 12-step order in `src/environment/slot_engine.py`
- [X] T013 Implement the slot boundary rules for admission, same-slot queue mutation, deadline checking, terminal precedence, and delayed reward timing in `src/environment/slot_boundaries.py`
- [X] T014 Implement timeout and drop handling in `src/environment/deadline_rules.py`
- [X] T015 Implement delayed reward emission in `src/environment/reward_timing.py`
- [X] T016 Implement trace loading or deterministic trace generation support in `src/environment/trace_source.py`
- [X] T017 [P] Add unit tests for FIFO ordering in `tests/unit/test_fifo_ordering.py`
- [X] T018 [P] Add unit tests for queue waiting time correctness in `tests/unit/test_queue_waiting_time.py`
- [X] T019 [P] Add unit tests for offload next-slot admission behavior in `tests/unit/test_offload_next_slot.py`
- [X] T020 [P] Add unit tests for public queue routing correctness in `tests/unit/test_public_queue_routing.py`
- [X] T021 [P] Add unit tests for deadline expiration logic in `tests/unit/test_deadline_expiration.py`
- [X] T022 [P] Add unit tests for completion versus drop precedence in `tests/unit/test_completion_drop_precedence.py`
- [X] T023 [P] Add unit tests for delayed reward emission correctness in `tests/unit/test_delayed_reward.py`

### Phase 2 Correction Block

**Purpose**: Close the Phase 2 implementation gaps identified during review without changing the
overall phase order or expanding scope.

- [X] T081 Refine `src/environment/slot_engine.py` so the slot engine explicitly represents the approved 12-step slot flow and preserves placeholders only for later-phase hooks that are not yet implemented
- [X] T082 Update `src/environment/private_queue.py` so queue waiting-time bookkeeping remains correct after dequeue when a new head becomes active
- [X] T083 Update `src/environment/offloading_queue.py` so queue waiting-time bookkeeping remains correct after dequeue when a new head becomes active
- [X] T084 Update `src/environment/public_queue.py` so queue waiting-time bookkeeping remains correct after dequeue when a new head becomes active
- [X] T085 [P] Add a corrective waiting-time-after-dequeue test for `PrivateQueue` in `tests/unit/test_queue_waiting_time.py`
- [X] T086 [P] Add a corrective waiting-time-after-dequeue test for `OffloadingQueue` in `tests/unit/test_queue_waiting_time.py`
- [X] T087 [P] Add a corrective waiting-time-after-dequeue test for `PublicQueue` in `tests/unit/test_queue_waiting_time.py`
- [X] T088 Tighten `tests/unit/test_offload_next_slot.py` so it verifies actual next-slot public-queue admission semantics rather than only destination preservation
- [X] T089 Tighten `tests/unit/test_public_queue_routing.py` so it verifies routing behavior tied to `(host_node_id, source_agent_id)` rather than only identity exposure

## Phase 3: Policy Interface

**Purpose**: Define the shared policy contract and keep all state mutation inside the environment.

- [X] T072 Define the shared policy interface contract with inputs, outputs, and environment-owned mutation boundaries in `src/policies/policy_interface.py`
- [X] T073 Implement legal action masking integration at the policy boundary in `src/policies/action_masking.py`
- [X] T074 Enforce environment-owned state mutation after action selection in `src/environment/environment.py`
- [X] T075 Add integration test coverage for policy-action flow and environment-owned mutation in `tests/integration/test_policy_interface_flow.py`

## Phase 4: Baseline Policies

**Purpose**: Implement the required comparison baselines through the shared policy interface.

- [X] T076 Implement Random Offloading (RO) as a shared-policy module in `src/policies/ro.py`
- [X] T077 Implement Full Local Computing (FLC) as a shared-policy module in `src/policies/flc.py`
- [X] T078 Implement Horizontal Offloading (HO) as a shared-policy module in `src/policies/ho.py`
- [X] T079 Implement Vertical Offloading (VO) as a shared-policy module in `src/policies/vo.py`
- [X] T080 Implement Minimum Latency Estimate Offloading (MLEO) as a shared-policy module in `src/policies/mleo.py`
- [X] T033 Implement Balanced Cooperation Offloading (BCO) as a shared-policy module in `src/policies/bco.py`
- [X] T034 Add baseline integration coverage for FLC episode execution in `tests/integration/test_flc_episode.py`
- [X] T035 Add placeholder-policy episode coverage in `tests/integration/test_placeholder_policy.py`

## Phase 5: Evaluation Pipeline

**Purpose**: Compute comparable metrics from identical traces and shared simulation outputs.

- [X] T036 Implement the shared evaluation module in `src/evaluation/evaluation_module.py`
- [X] T037 Define and centralize the average delay and drop ratio formulas in `src/evaluation/metric_formulas.py` so average delay matches the paper exactly or is recorded in `docs/assumptions/hoodie_assumptions.md`, drop ratio is clearly defined per task completion/drop outcome, all metric formulas are shared by every evaluation path, and no policy, environment, or training component computes metrics independently
- [X] T038 Implement per-trace metric computation in `src/evaluation/per_trace_metrics.py`
- [X] T039 Implement aggregate metric computation in `src/evaluation/aggregate_metrics.py`
- [X] T040 Implement trace bank and paired-seed evaluation support in `src/evaluation/trace_protocol.py`
- [X] T041 Enforce identical evaluation traces across compared policies in `src/evaluation/fairness_checks.py`
- [X] T042 Implement run metadata capture for trace IDs, seed IDs, and evaluation mode in `src/evaluation/run_metadata.py`
- [X] T043 Persist raw evaluation metrics for reproducibility in `src/evaluation/metric_storage.py`
- [X] T044 Add integration tests for trace replay reproducibility in `tests/integration/test_trace_replay_reproducibility.py`

### Phase 5 Correction Block

**Purpose**: Tighten the evaluation pipeline so it relies on the shared environment path and
documented fairness inputs rather than synthetic shortcuts.

- [X] T090 Refine `src/evaluation/runner.py` so evaluation runs use the shared environment/slot path as far as the implemented phases allow instead of manually simulating policy outcomes outside that path
- [X] T091 Tighten `src/evaluation/fairness_checks.py` so fairness validation covers trace identity, seed basis, episode length, and policy-independent evaluation settings rather than only trace-id equality
- [X] T092 Refine `src/evaluation/runner.py` so policy hints and legal masks are derived consistently from the shared environment/topology path and any fallback observation hints are explicit, minimal, and documented
- [X] T093 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies the runner uses the shared environment/slot path consistently
- [X] T094 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies policy inputs are derived consistently rather than arbitrarily hardcoded
- [X] T095 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies fairness checks reject mismatched evaluation conditions

### Phase 5 Correction Block II

**Purpose**: Reduce the remaining synthetic outcome handling in evaluation by delegating ownership to
the shared runtime wherever the implemented simulator already supports it.

- [X] T096 Refine `src/evaluation/runner.py` so terminal outcomes and reward-emitted flags are no longer manually stamped when the shared environment/slot path can own them
- [X] T097 Refine `src/evaluation/runner.py` so completion timing is derived through shared runtime helpers or pathways as far as the implemented simulator allows instead of being assigned ad hoc in the runner
- [X] T098 Refine `src/evaluation/runner.py` so resolved destinations are derived consistently from the action and available topology/path rules, with any fallback behavior explicitly documented
- [X] T099 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies terminal outcome ownership is not manually bypassed in the runner
- [X] T100 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies reward emission is not manually forced when shared runtime behavior is available
- [X] T101 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies destination resolution is consistent with action and topology expectations

### Phase 5 Correction Block III

**Purpose**: Remove the remaining evaluation-owned fallback synthesis and keep runtime ownership inside
the shared environment/runtime path wherever the implemented simulator can support it.

- [X] T102 Refine `src/evaluation/runner.py` so completion timing moves out of the evaluation runner and into a shared environment/runtime helper
- [X] T103 Refine `src/evaluation/runner.py` so terminal outcome, drop flag, and reward-emitted ownership move out of the evaluation runner and into shared environment/runtime logic whenever unresolved after slot advancement
- [X] T104 Refine `src/evaluation/runner.py` so offload destination resolution is topology-backed for offload actions or fails explicitly, and any synthetic fallback remains explicit, documented, and narrow
- [X] T105 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies the runner no longer owns completion timing directly
- [X] T106 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies the runner no longer owns terminal outcome, drop flag, or reward-emitted state directly
- [X] T107 [P] Add an integration test in `tests/integration/test_evaluation_runner.py` that verifies destination resolution fails explicitly or remains topology-backed instead of using a generic fallback

### Phase 5 Correction Block IV

**Purpose**: Upgrade the shared runtime timing model using paper-backed slot structure and currently available paper parameters so the simulator uses one coherent timing path.

- [X] T108 Add a shared runtime parameter module in `src/environment/runtime_model.py` for slot duration, queue service capacities, and timeout-related values using currently available paper-backed values or documented assumptions
- [X] T109 Refine `src/environment/runtime_model.py` so completion timing uses a shared service model that accounts for queue waiting, offloading progression, and destination-specific execution service rather than only a primitive density rule
- [X] T110 Add a shared runtime progression helper in `src/environment/runtime_model.py` that advances task timing through waiting, offloading, service, and terminal resolution in slot-based form
- [X] T111 Integrate the shared runtime progression helper into `src/environment/slot_engine.py` so evaluation and later phases use the same timing ownership path
- [X] T112 [P] Add integration tests in `tests/integration/test_evaluation_runner.py` and `tests/unit/test_queue_waiting_time.py` that verify destination-specific service timing differs between local/public/cloud paths when runtime parameters differ, offload timing remains one-hop and bounded, drain-slot behavior can continue pending tasks after the action window, and terminal resolution still respects deadlines after runtime progression

### Phase 5 Correction Block V

**Purpose**: Remove the remaining evaluation-owned fallback synthesis by pushing the shared runtime timing path farther into the simulator and keeping the evaluation runner thin.

- [X] T113 Refine `src/environment/runtime_model.py` so shared runtime progression owns completion timing, offloading progression, and delayed reward readiness without relying on evaluation-owned timing shortcuts
- [X] T114 Refine `src/environment/runtime_model.py` so terminal outcome, drop flag, and reward-emitted ownership are resolved by shared runtime logic whenever the slot path cannot complete them directly
- [X] T115 Refine `src/environment/runtime_model.py` so offload destination resolution remains topology-backed for offload actions and any synthetic fallback is explicit, documented, and narrow
- [X] T116 [P] Add integration tests in `tests/integration/test_evaluation_runner.py` that verify the runner no longer owns completion timing, terminal outcome, or reward-emitted state directly when shared runtime behavior is available
- [X] T117 [P] Add integration tests in `tests/integration/test_evaluation_runner.py` that verify offload destination resolution is topology-backed or fails explicitly instead of falling back to a generic peer destination

### Phase 5 Calibration Block VII

**Purpose**: Tighten the remaining runtime calibration artifacts so the shared timing model reads like a paper-backed model instead of a pile of inherited defaults.

- [X] T122 Add a runtime evidence mapping document in `docs/paper_notes/runtime_model_evidence.md` that marks each shared runtime rule and parameter as paper-explicit, paper-implied, OCR-supported, or assumption-backed
- [X] T123 Add a paper-calibrated runtime config file in `configs/runtime_model.yml` with recovered timing and resource values plus explicit assumption-backed placeholders for unresolved entries
- [X] T124 Refactor `src/environment/runtime_model.py` so shared runtime parameters load from the runtime config as the default source instead of relying on hardcoded values alone
- [X] T125 [P] Add calibration tests in `tests/unit/test_runtime_model.py` that verify the runtime config, slot-count split, timeout semantics, and destination-class capacities are loaded and applied consistently

### Phase 5 Experimental Extension Block II

**Purpose**: Add an optional runtime variant framework for service-delay experiments while keeping the current density-based default unchanged.

- [X] T130 [P] [US1] Add a runtime model variant abstraction in `src/environment/runtime_model.py` and `configs/runtime_model.yml` that can select between multiple service-delay models via config without changing the default runtime behavior
- [X] T131 [P] [US1] Define density-based, discrete-slot service, and constant-service runtime variants in `src/environment/runtime_model.py` or a narrowly scoped companion module while preserving the current density-based default
- [X] T132 [P] [US1] Update `src/evaluation/runner.py` only as needed so identical traces can be replayed under different runtime variants without changing evaluation semantics
- [X] T133 [P] [US1] Add comparative tests in `tests/unit/test_runtime_model.py` and `tests/integration/test_evaluation_runner.py` that verify runtime variant selection changes delay outcomes while keeping routing, deadlines, and FIFO behavior unchanged

## Phase 6: HOODIE Agent Components

**Purpose**: Add the learning-specific components required by HOODIE while keeping the shared simulator intact.

- [X] T045 Integrate the shared policy interface with the HOODIE agent entrypoint in `src/agents/hoodie_agent.py`
- [X] T046 Implement state and history construction for HOODIE inputs, including LSTM-ready history structures, in `src/agents/history_builder.py`
- [X] T047 Implement replay buffer behavior in `src/agents/replay_buffer.py`
- [X] T048 Implement target network update logic in `src/agents/target_network.py`
- [X] T049 Implement the Dueling DQN value/advantage decomposition in `src/agents/dueling_dqn.py`
- [X] T050 Implement Double DQN action-target selection logic in `src/agents/double_dqn.py`
- [X] T051 Assemble the full HOODIE model forward path from shared inputs through action values in `src/agents/hoodie_model.py`
- [X] T052 Add integration coverage for the HOODIE placeholder path through the shared environment in `tests/integration/test_hoodie_placeholder.py`

## Phase 7: Training Workflow

**Purpose**: Build the episode-based training loop and preserve delayed-reward semantics.

- [X] T053 Implement the episode-based training loop in `src/training/training_loop.py` without modifying environment dynamics, using only outputs from the shared environment and evaluation pipeline as inputs, and treating training as orchestration rather than simulation logic
- [X] T054 Integrate delayed reward handling into training in `src/training/delayed_reward_training.py` using the same reward semantics defined in the environment and without any training-specific shortcuts or alternative reward paths
- [X] T055 Enforce config-driven training parameters in `src/config/training_config.py` so training remains orchestration only and does not introduce new simulation logic
- [X] T056 Record training seeds and evaluation seeds separately in `src/training/seed_management.py` without altering shared environment behavior or evaluation trace selection, and without changing environment dynamics
- [X] T057 Log training metrics and configuration identifiers in `src/training/training_logging.py` without computing or redefining simulation metrics outside the shared evaluation pipeline, and without introducing any training-owned metric path

### Phase 7 Reward Correction Block

**Purpose**: Align training reward handling with the recovered HOODIE reward definition from A-012 and the paper evidence in Section 3, Equation (20), plus Table 4 penalty constant.

- [X] T134 [P] [US1] Refine `src/training/delayed_reward_training.py` so training reward handoff consumes the paper-backed environment-emitted HOODIE reward semantics from A-012 instead of any placeholder training-owned reward rule, using the recovered Section 3, Equation (20) reward definition and Table 4 drop-penalty constant
- [X] T135 [P] [US1] Refine `src/training/training_loop.py` so reward consumption remains environment-gated and training only records transitions after the shared reward emission path has produced the documented HOODIE reward behavior from A-012
- [X] T136 [P] [US1] Add integration coverage in `tests/integration/test_training_loop.py` that verifies no pre-emission reward usage, consumed reward matches the recovered A-012 reward behavior, and no separate training-owned reward scale exists

## Phase 8: Validation Workflow

**Purpose**: Compare baselines and HOODIE on the same traces and document deviations from the paper.

- [X] T058 Implement validation runs using shared evaluation traces in `src/evaluation/validation_runner.py`
- [X] T059 Compare baselines versus HOODIE with identical trace inputs in `src/evaluation/comparison_runner.py`
- [X] T060 Generate validation artifacts with metrics, plots, and notes in `src/evaluation/validation_artifacts.py`
- [X] T061 Document paper deviations and resolved assumptions in `docs/assumptions/validation_deviations.md`
- [X] T062 Enforce config immutability for reported result sets in `src/config/config_freeze.py`

## Phase 9: Analysis and Output Generation

**Purpose**: Produce the paper-facing outputs used for reproduction, sweeps, and review.

- [X] T063 Generate average delay and drop ratio outputs in `analysis/delay_drop_reports.py`
- [X] T064 Generate convergence traces and learning progress outputs in `analysis/convergence_reports.py`
- [X] T065 Support parameter sweep outputs in `analysis/sweep_reports.py`
- [X] T066 Store outputs with config, seed, and trace identifiers in `analysis/output_registry.py`
- [X] T067 Generate validation comparison plots in `analysis/comparison_plots.py`

## Phase 10: Documentation and Traceability

**Purpose**: Package, freeze, and reproduce the full pipeline without changing simulator behavior.

- [X] T137 Implement unified config loading in `src/config/config_loader.py` so training, evaluation, and runtime sections are read from one serializable and hashable config object without introducing hidden defaults
- [X] T138 Implement the reproducibility guard in `src/repro/repro_guard.py` so config hash consistency, seed consistency, and runtime variant selection are validated before pipeline execution
- [X] T139 Implement the end-to-end pipeline entrypoint in `src/run_pipeline.py` so optional training, validation, analysis, and export are orchestrated through the shared validation and analysis artifacts path
- [X] T140 Implement the CLI interface in `src/cli.py` so the full pipeline, validation-only, and analysis-only entrypoints are exposed without hidden shortcuts
- [X] T141 Implement output packaging in `src/repro/output_packager.py` so config snapshots, hashes, validation artifacts, analysis outputs, and metadata are written into structured run directories
- [X] T142 Document the full pipeline and reproducibility contract in `docs/reproducibility.md`, including seed handling, deterministic mode, and the current paper-backed versus assumption-backed behavior
- [X] T143 Add full-pipeline reproducibility tests in `tests/integration/test_full_pipeline.py` to verify deterministic outputs, config freezing, hidden-state independence, and CLI execution

### Phase 10 Correction Block II

**Purpose**: Make configured policy selection explicit and fail fast for unsupported names without adding fallback behavior.

- [X] T147 Refine `src/config/config_loader.py` so configured validation policy names are loaded and preserved as part of the unified config object
- [X] T148 Refine `src/run_pipeline.py` so supported policy names are resolved through an explicit shared-policy registry, policy order is preserved, and unsupported names fail clearly
- [X] T149 [P] Add integration coverage in `tests/integration/test_full_pipeline.py` that verifies configured policy names are respected, unsupported names fail explicitly, policy order is preserved in metadata, and deterministic packaging remains stable

### Phase 10 Correction Block III

**Purpose**: Make stochastic shared-policy randomness reproducible and seed-controlled without changing simulator behavior.

- [X] T150 Refine `src/policies/ro.py` and any narrow shared policy helper so stochastic shared-policy choices use config-controlled randomness instead of uncontrolled global randomness
- [X] T151 Refine `src/run_pipeline.py` and `src/config/config_loader.py` so the evaluation/pipeline seed is propagated to stochastic policy instances in a deterministic, policy-independent way
- [X] T152 [P] Add regression coverage in `tests/integration/test_full_pipeline.py` that verifies `RO` produces reproducible choices under the same seed and different choices may occur under different seeds

### Phase 10 Correction Block IV

**Purpose**: Decouple stochastic policy randomness from trace-shaping inputs so policy output stays stable when only trace metadata changes.

- [X] T153 Refine `src/run_pipeline.py` and `src/policies/ro.py` so `policy_seed` is separated from `evaluation.seed` and no longer depends on `trace_id` or `episode_length`
- [X] T154 Refine `src/config/config_loader.py` so the unified config preserves an explicit `policy_seed` or equivalent policy RNG control value independent of trace configuration
- [X] T155 [P] Add regression coverage in `tests/integration/test_full_pipeline.py` that verifies stochastic policy output stability under trace changes and keeps policy randomness independent from trace metadata

### Phase 10 Correction Block VII

**Purpose**: Resolve the remaining reproducibility ambiguity by splitting evaluation-level versus full-config provenance in validation artifacts.

- [X] T163 Refine `src/repro/output_packager.py` so `metadata.json` remains authoritative for the full unified config snapshot/hash and `validation_artifacts.json` exposes clearly labeled fields such as `evaluation_config_snapshot`, `evaluation_config_hash`, `full_config_snapshot`, and `full_config_hash`
- [X] T164 Refine `src/evaluation/validation_artifacts.py` so validation payload serialization clearly distinguishes evaluation-only provenance from full unified config provenance without changing metrics or validation behavior
- [X] T165 Refine `docs/reproducibility.md` so the authoritative snapshot/hash fields are explicitly documented for packaged metadata and validation artifacts
- [X] T166 [P] Add regression coverage in `tests/integration/test_validation_pipeline.py` and `tests/integration/test_full_pipeline.py` that verifies metadata and validation artifact provenance fields are unambiguous, metric values remain unchanged, and deterministic packaging stays byte-identical

### Phase 11 Correction Block II

**Purpose**: Add the minimal deterministic HOODIE learning update path and verify it affects future action scoring without changing baseline policies or reward semantics.

- [X] T178 Refine `src/agents/hoodie_model.py` and `src/agents/hoodie_agent.py` so delayed rewards can be consumed by a minimal deterministic Q-update path that changes stored action preferences while keeping learned preferences separate from fallback hints
- [X] T179 Refine `src/training/training_loop.py` and `src/agents/replay_buffer.py` so replay-buffer samples are consumed by a learning step rather than remaining inert storage and the learned update is applied deterministically from the released delayed reward stream
- [X] T180 Refine `src/agents/target_network.py` and `src/agents/hoodie_agent.py` so target-network sync/copy writes observable learned parameters that affect future `choose_action()` scoring
- [X] T181 [P] Add regression coverage in `tests/unit/test_agent_components.py`, `tests/integration/test_training_loop.py`, and `tests/integration/test_hoodie_placeholder.py` that verifies positive or less-negative rewards raise selected-action preference relative to alternatives, drop penalties lower selected-action preference, repeated fixed-config training is deterministic, trained HOODIE action distributions can differ from untrained HOODIE, illegal actions remain impossible, and evaluation can consume a trained HOODIE agent/model state
- [X] T182 Document the learning update rule as assumption-backed unless exact paper equations are recovered in `docs/assumptions/hoodie_assumptions.md` and `docs/analysis/hoodie_superiority_gap.md`

### Phase 11 Correction Block III

**Purpose**: Plan the trained-HOODIE state handoff path without implementing checkpointing yet.

- [X] T183 Define a checkpoint/export representation for learned HOODIE state after training in `src/agents/hoodie_agent.py`, `src/agents/hoodie_model.py`, and `src/run_pipeline.py` without changing training behavior or policy semantics
- [X] [P] T184 Define reload and validation-side injection of learned HOODIE state in `src/run_pipeline.py`, `src/evaluation/validation_runner.py`, and `src/evaluation/runner.py` so validation can consume a trained model instead of a fresh untrained fallback when trained mode is requested
- [X] [P] T185 Extend `docs/reproducibility.md` and `docs/analysis/hoodie_superiority_gap.md` to document deterministic packaging, provenance, and the boundary between fresh validation and trained-agent validation
- [X] [P] T186 Add regression-test tasks in `tests/integration/test_training_loop.py`, `tests/integration/test_full_pipeline.py`, and `tests/integration/test_hoodie_placeholder.py` to prove trained HOODIE state survives process-boundary-style save/load and that trained validation does not silently fall back to a fresh untrained agent

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 must complete before any queue, policy, evaluation, training, validation, or analysis work.
- Phase 2 depends on Phase 1 and blocks all policy and learning work until the simulator timing is
  correct.
- Phase 3 depends on Phases 1 and 2 and establishes the shared contract used by every policy.
- Phase 4 depends on Phase 3 and must reuse the shared simulator rather than duplicating it.
- Phase 5 depends on Phases 1, 2, and 3 so fairness checks and metric computation share the same
  environment.
- Phase 6 depends on Phases 3 and 5 so HOODIE sees the same policy inputs and evaluation rules.
- Phase 7 depends on Phases 3, 5, and 6 so training respects delayed rewards and shared traces.
- Phase 8 depends on Phases 1 through 7 so validation compares trained and baseline policies using
  the same evaluation path.
- Phase 9 depends on all earlier phases because outputs depend on validated metrics and comparison
  runs.
- Phase 10 can run throughout, but final documentation must reflect the completed assumptions and
  paper mappings.

### Parallel Opportunities

- Tasks marked `[P]` can run in parallel when they touch different files and do not depend on
  unfinished tasks.
- Baseline policy tasks can proceed in parallel after the shared policy contract is complete.
- Evaluation metric tasks can proceed in parallel after the shared evaluation module skeleton is in
  place.
- Documentation tasks can proceed in parallel with code tasks as long as they only record approved
  decisions.

## Parallel Example: Phase 2 Queue and Timing

```text
Task: T017 Add unit tests for FIFO ordering in tests/unit/test_fifo_ordering.py
Task: T018 Add unit tests for queue waiting time correctness in tests/unit/test_queue_waiting_time.py
Task: T019 Add unit tests for offload next-slot admission behavior in tests/unit/test_offload_next_slot.py
Task: T020 Add unit tests for public queue routing correctness in tests/unit/test_public_queue_routing.py
Task: T021 Add unit tests for deadline expiration logic in tests/unit/test_deadline_expiration.py
Task: T022 Add unit tests for completion versus drop precedence in tests/unit/test_completion_drop_precedence.py
Task: T023 Add unit tests for delayed reward emission correctness in tests/unit/test_delayed_reward.py
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3.
3. Complete one baseline in Phase 4, preferably FLC.
4. Complete Phase 5.
5. Stop and validate the shared simulator before adding HOODIE training complexity.

### Incremental Delivery

1. Build the simulator and queue timing first.
2. Add the shared policy contract and baselines next.
3. Add shared evaluation before any learning-specific logic.
4. Add HOODIE components only after the shared path is stable.
5. Add training, validation, and analysis only after fairness and replay behavior are reproducible.

## Notes

- All tasks must preserve shared environment usage across baselines and HOODIE.
- All reported results must preserve config immutability and trace reproducibility.
- Unknown paper details remain explicit documentation tasks until resolved.
