# ECHO Multi-Agent Phase-Gated Implementation Runbook

## Purpose

This runbook implements and evaluates **ECHO — Effective Completion via Hybrid Offloading** as the primary proposed method.

HOODIE is treated only as:

1. the inherited architectural and DRL reference where ECHO explicitly cites it;
2. a reproducibility baseline;
3. a comparison method.

The workflow is deliberately phase-gated. Run one phase at a time. Do not allow a later phase to begin until the previous phase has a written report and receives a `PASS` from the gate-review prompt.

---

# 1. Required project inputs

Before Phase 0, make these sources available to the coding environment:

```text
<REPO_ROOT>/
├── research/
│   ├── HOODIE_paper.pdf
│   ├── ECHO_method_spec.md       # export of Google Doc tab: روش پیشنهادی
│   └── ECHO_evaluation_spec.md   # export of Google Doc tab: ارزیابی
└── ...
```

Authoritative Google Doc:

```text
Document:
https://docs.google.com/document/d/17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE/edit

Method tab:
tab=t.iav4589yyeo7

Evaluation tab:
tab=t.oxhaq5ojy5h6
```

If the agent can access the Google Doc directly, it must still create immutable local snapshots under `research/` and record the document revision or export timestamp.

If direct access is unavailable, stop only long enough to request the two local exports. Do not attempt to reconstruct the specification from memory.

## Runtime variables

The agents should discover these automatically when possible:

```text
REPO_ROOT=<current git repository root>
BASE_PAPER=<path to HOODIE_paper.pdf>
ECHO_METHOD_SPEC=<path to ECHO_method_spec.md/pdf>
ECHO_EVALUATION_SPEC=<path to ECHO_evaluation_spec.md/pdf>
KG_TOOL=<installed KG/Graphify plugin; auto-detect>
AGENT_RUNTIME=<available agent/subagent framework; auto-detect>
COMPUTE_BUDGET=<available GPU/CPU, RAM, maximum wall time, storage>
```

## Global rules for every phase

- Do not read or expose secrets.
- Do not commit, push, delete files, or rewrite history unless explicitly authorized.
- Start each phase with read-only inspection.
- Ask only questions that block correctness.
- Record facts, assumptions, ambiguities, and decisions separately.
- Never treat KG output as the source of truth; verify against actual source files.
- Never fabricate article results.
- Never tune against held-out test traces.
- Never allow ECHO-only logic to leak into HOODIE or heuristic baselines.
- Never launch the full experiment matrix before smoke and pilot gates pass.
- Preserve raw logs and machine-readable evidence for every scientific claim.
- Each specialist agent owns a declared file set. Two agents must not edit the same file concurrently.
- At the end of each phase, write the required Markdown report and stop for gate review.

---

# 2. Reusable phase-gate reviewer prompt

Run this prompt after every phase report.

```text
Act as an independent scientific software gate reviewer with expertise in cloud-edge simulation, deadline-aware scheduling, multi-agent deep reinforcement learning, experiment design, and reproducibility.

You did not implement the work you are reviewing.

Inputs:
- The current phase prompt.
- The phase report.
- All artifacts cited by that report.
- The relevant ECHO method and evaluation specifications.
- The current git diff and test output.

Your job is to decide whether the phase may proceed.

Review rules:
1. Verify evidence directly. Do not accept claims merely because they appear in the report.
2. Check that the phase remained within scope.
3. Check that facts, assumptions, decisions, and unresolved ambiguities are separated.
4. Check traceability to exact ECHO equations, algorithms, or evaluation requirements.
5. Check whether the next phase would be unsafe or scientifically invalid if any current defect remains.
6. Check method isolation: ECHO-only behavior must not contaminate HOODIE or heuristic baselines.
7. Check for hidden test leakage, result fabrication, hard-coded expected outputs, or unsupported claims.
8. Check that artifacts are machine-readable where required.
9. Check that tests actually exercise runtime behavior rather than only names or static structure.
10. Identify the single most serious defect first.

Write:
`docs/echo/gates/gate_<PHASE_NUMBER>.md`

Required structure:

# Gate Review — Phase <N>

## Verdict
PASS / REWORK / BLOCKED

## Critical defect
The most serious issue, or `None`.

## Evidence checked
Exact files, commands, test outputs, and specification locations inspected.

## Failed acceptance criteria
A precise list. Use `None` when all pass.

## Required corrections
Ordered by importance. Each item must be testable.

## Risks carried forward
Risks that remain acceptable but must be monitored.

## Authorization
- `Proceed to Phase <N+1>` only when verdict is PASS.
- Otherwise explicitly prohibit the next phase.

Do not fix the work yourself. Review it independently.
```

---

# 3. Phase 0 — Orchestrator initialization

## Specialist roles

- Principal Orchestrator
- Source-Control and Reproducibility Coordinator
- Agent-Capability Inspector

## Prompt

```text
Act as the principal orchestrator for a multi-agent scientific software implementation.

Project objective:
Implement and evaluate ECHO as the primary proposed method. Treat HOODIE as an inherited reference and comparison baseline, not as the target implementation.

First, inspect the current repository and available agent/KG capabilities. This phase is organizational and read-only. Do not modify application or simulation source code.

Authoritative sources:
1. `research/ECHO_method_spec.*`
2. `research/ECHO_evaluation_spec.*`
3. `research/HOODIE_paper.pdf` only for explicitly inherited mechanics
4. Existing repository code only as implementation evidence, never as specification authority

Required workflow:

1. Resolve the git repository root, branch, HEAD, working-tree state, and existing untracked files.
2. Locate the three authoritative research sources.
3. Hash or otherwise fingerprint the local source snapshots.
4. Detect the available specialist-agent runtime:
   - subagents/tasks;
   - worktrees or isolated branches;
   - file-ownership controls;
   - persistent task tracking.
5. Detect the installed KG/Graphify tool and read its actual help/documentation before proposing commands.
6. Detect the programming language, ML framework, dependency manager, test framework, and experiment runner.
7. Detect available compute resources and estimate whether GPU execution is available.
8. Define specialist agents for later phases:
   - ECHO Specification Agent
   - Evaluation Contract Agent
   - KG Repository Agent
   - Simulation Kernel Agent
   - ECHO Mechanics Agent
   - DRL/LSTM Agent
   - Baseline Agent
   - Experiment/Plotting Agent
   - Verification Agent
   - Independent Reproducibility Auditor
9. Assign non-overlapping file ownership for each future agent.
10. Create a phase dependency graph. No implementation agent may start before the specification, repository-map, and output-contract phases pass.
11. Create persistent project-control files:
   - `docs/echo/PHASE_STATUS.md`
   - `docs/echo/DECISION_LOG.md`
   - `docs/echo/ASSUMPTION_LOG.md`
   - `docs/echo/ARTIFACT_INDEX.md`
   - `docs/echo/AGENT_OWNERSHIP.md`
12. Record a rollback strategy for every future source-changing phase.
13. Do not begin Phase 1 automatically.

Deliverable:
`docs/echo/phases/phase_00_orchestration_plan.md`

The report must include:
- repository identity;
- source snapshot identity;
- tool and agent capabilities;
- compute inventory;
- specialist roles;
- file ownership;
- phase dependency graph;
- detected blockers;
- exact recommended command or invocation method for Phase 1.

Acceptance criteria:
- All authoritative sources are present or a precise blocking request is issued.
- KG and agent capabilities are verified rather than assumed.
- No application source was modified.
- Future agent edit ownership does not overlap.
- Rollback and status files exist.

Stop after writing the report.
```

---

# 4. Phase 1 — Freeze the ECHO scientific contract

## Specialist roles

- ECHO Specification Agent
- Evaluation Contract Agent
- Mathematical Consistency Reviewer
- Independent Critical Reviewer

## Prompt

```text
Act as a team of scientific specification engineers.

Primary objective:
Convert the ECHO method and evaluation documents into a complete, testable implementation contract before any application code is changed.

This phase is read-only with respect to application and simulation source code.

Source authority:
1. ECHO method specification
2. ECHO evaluation specification
3. HOODIE paper only where ECHO explicitly inherits a mechanism
4. Repository code only for later comparison

Required workstreams:

A. Method contract
- Extract every numbered ECHO equation, currently (1) through (67).
- Extract all algorithm steps from ECHO training and inference procedures.
- Extract exact slot-level event ordering.
- Extract task lifecycle rules:
  - arrival;
  - direct action;
  - queue admission;
  - non-preemptive service;
  - transmission;
  - destination insertion;
  - completion;
  - expiration;
  - drop;
  - pending decision;
  - next decision epoch;
  - replay finalization.
- Extract all state features, masks, normalization rules, reward terms, and semi-Markov discount rules.
- Identify which mechanics are ECHO-specific and which are inherited from HOODIE.

B. Evaluation contract
- Enumerate Figures 4 through 8 and all fifteen panels.
- Extract exact axes, sweeps, methods, seeds, held-out episodes, training budgets, fixed parameters, confidence intervals, and output formats.
- Extract every logging and accounting invariant.
- Extract the comparison baselines and their operational definitions.

C. Consistency review
Investigate and resolve or explicitly register:
1. LSTM prediction target, decoder, loss, and joint/separate training.
2. Missing/delayed controller-update model.
3. Deterministic topology rule for N = 10, 15, 20, 25, 30.
4. Whether learning-based methods retrain for every operating point or reuse checkpoints.
5. Fixed normalization bounds for every state feature.
6. Validation-only selection of learning rate, discount factor, lambda_R, lambda_D, and ERT clipping.
7. Episode termination and drain-interval semantics.
8. Meaning of “dropped” for active non-preemptive work that finishes after its deadline.
9. Whether unfinished active work is allowed to consume resources after being marked unsuccessful.
10. HOODIE implementation semantics required for a fair comparison.
11. Whether ECHO-NoLSTM differs only in load estimation.
12. Exact tie-breaking rules and deterministic ordering.
13. Exact handling when no decision occurs and the action mask is all zero.
14. Exact scaling of negative-delay reporting.
15. Exact checkpoint-selection rule and validation split.

For each unresolved issue, write:
- evidence;
- possible interpretations;
- scientific consequence;
- recommended decision;
- test that protects the decision;
- whether user approval is required.

Required files:
- `docs/echo/contracts/01_source_authority.md`
- `docs/echo/contracts/02_echo_equation_contract.md`
- `docs/echo/contracts/03_algorithm_and_event_contract.md`
- `docs/echo/contracts/04_evaluation_output_contract.md`
- `docs/echo/contracts/05_method_isolation_contract.md`
- `docs/echo/contracts/06_ambiguity_register.md`
- `docs/echo/contracts/07_implementation_decisions.md`

The equation contract table must contain:
| Eq. | Source location | Inputs | Output | Runtime behavior | Edge cases | Required test | Status |

The evaluation contract table must contain:
| Figure/panel | Methods | X values | Fixed config | Train policy | Seeds | Test episodes | Metric | Raw evidence | Exports |

Do not invent missing decisions silently.
When a decision can be made safely from the source hierarchy, make and justify it.
When user approval is scientifically necessary, list the minimum decision required.

Deliverable:
`docs/echo/phases/phase_01_scientific_contract.md`

Acceptance criteria:
- All ECHO equations and algorithm steps are represented.
- All fifteen evaluation panels are represented.
- Event ordering is explicit.
- ECHO/HOODIE/baseline isolation is explicit.
- Ambiguities are not hidden.
- No application source was modified.

Stop after writing the report.
```

---

# 5. Phase 2 — KG repository mapping and paper-to-code gap analysis

## Specialist roles

- KG Repository Agent
- Simulation Archaeology Agent
- DRL Code Auditor
- Experiment-Pipeline Auditor

## Prompt

```text
Act as a repository knowledge-graph and runtime-mechanics audit team.

Objective:
Map the current repository to the frozen ECHO contract and identify the exact implementation gap. This phase is read-only.

Use the installed KG/Graphify tool only after reading its actual documentation. Exclude secrets, dependencies, caches, checkpoints, generated figures, large datasets, and build outputs.

Generate focused repository views:

1. Module/package dependency graph.
2. Class/function call graph.
3. Slot-level event and state-transition graph.
4. Task lifecycle graph:
   arrival -> action -> source queue -> active service -> transmission -> destination queue -> completion/drop -> pending record -> replay.
5. DRL graph:
   state -> LSTM/load features -> Q network -> mask -> action -> reward -> semi-Markov target -> optimizer.
6. Configuration propagation graph.
7. Experiment graph:
   configuration -> training -> checkpoint -> validation -> held-out evaluation -> CSV -> aggregation -> figure.
8. Artifact lineage graph.

Ask focused KG questions:
- Where is the simulation clock advanced?
- What is the exact order of operations inside one slot?
- Where are waiting and active tasks stored?
- Where are deadlines checked?
- Where does a task become dropped?
- Where is route choice made?
- Is offloading destination chosen once or twice?
- Where is destination arrival delayed until transmission completion?
- Where is FIFO implemented?
- Where can queue reordering be introduced?
- Where are state vectors built and normalized?
- Where are masks applied in exploration, exploitation, and target selection?
- Where are delayed rewards stored?
- Where is the next decision state chosen?
- Where is gamma or a time-gap discount applied?
- Where are online and target networks updated?
- Where are LSTM inputs and targets formed?
- Where are random seeds propagated?
- Which scripts create each current result?
- Which configuration values affect each metric?

Verify every important KG claim by opening the real source file.

Create:
- `docs/echo/kg/01_repository_map.md`
- `docs/echo/kg/02_task_lifecycle_map.md`
- `docs/echo/kg/03_drl_dataflow_map.md`
- `docs/echo/kg/04_experiment_pipeline_map.md`
- `docs/echo/kg/05_config_propagation_map.md`
- `docs/echo/kg/06_paper_code_traceability.md`
- `docs/echo/kg/07_gap_and_severity_matrix.md`
- graph exports under `docs/echo/kg/graphs/`

Traceability columns:
| Contract ID | Required behavior | Current file/symbol | Current behavior | Match status | Severity | Evidence | Required change |

Allowed statuses:
- Exact runtime match
- Partial
- Behavioral mismatch
- Missing
- Unreachable
- Ambiguous
- Extension contamination
- Not applicable with justification
- Not yet verifiable

Severity:
- S0: invalidates task accounting or reported results
- S1: invalidates ECHO mechanics or learning
- S2: invalidates fairness or reproducibility
- S3: maintainability/documentation only

Also propose a source-edit ownership plan for Phases 4-7 with no overlapping files.

Deliverable:
`docs/echo/phases/phase_02_repository_gap_report.md`

Acceptance criteria:
- KG graphs exist and are verified against code.
- Every executable ECHO contract item has a mapping status.
- The exact slot order is documented.
- The highest-severity gaps are identified.
- No application source was modified.

Stop after writing the report.
```

---

# 6. Phase 3 — Output-first experiment and artifact contract

## Specialist roles

- Experiment Design Agent
- Data Schema Agent
- Plotting Pipeline Agent
- Compute-Budget Planner
- Statistical Reviewer

## Prompt

```text
Act as an experiment-infrastructure and scientific-output team.

Objective:
Build the complete output and experiment contract before implementing ECHO mechanics. This phase may create experiment schemas, manifests, configuration templates, and plotting-pipeline scaffolding, but must not fabricate scientific results.

Required architecture:

experiments/
├── manifest.yaml
├── figure_manifest.yaml
├── configs/
│   ├── smoke/
│   ├── pilot/
│   ├── validation/
│   ├── full_paper/
│   └── ablations/
└── schemas/
    ├── run_manifest.schema.json
    ├── task_log.schema.json
    ├── episode_metrics.schema.json
    ├── seed_metrics.schema.json
    ├── panel_values.schema.json
    └── artifact_manifest.schema.json

artifacts/
├── manifests/
├── configs/
├── topologies/
├── checkpoints/
├── raw_logs/
│   ├── task_level/
│   ├── episode_level/
│   └── training/
├── metrics/
│   ├── seed_level/
│   ├── panel_level/
│   └── confidence_intervals/
├── figures/
│   ├── vector/
│   ├── png_300dpi/
│   └── panel_exports/
└── reports/

Required work:

1. Encode every Figure 4-8 panel in `figure_manifest.yaml`.
2. For every panel define:
   - methods;
   - x-axis values;
   - fixed values;
   - train/retrain policy;
   - seeds;
   - validation and test episodes;
   - metric formula;
   - aggregation rule;
   - 95% confidence-interval method;
   - raw evidence paths;
   - CSV path;
   - vector figure path;
   - 300-dpi PNG path.
3. Define task-level logs including:
   - trace ID;
   - task ID;
   - source;
   - arrival;
   - deadline;
   - route candidates;
   - predicted completion for every physical candidate;
   - candidate ERT vector;
   - action mask;
   - selected action;
   - fallback/risk indicator;
   - queue waiting estimates;
   - actual queue transitions;
   - resolution slot;
   - success/drop;
   - realized duration;
   - reward;
   - replay transition duration.
4. Define invariants:
   generated = successful + dropped;
   no duplicate resolution;
   no masked action;
   no invalid horizontal action;
   identical trace IDs across methods;
   no task in multiple locations;
   destination insertion only after transmission.
5. Define three execution modes:
   - smoke;
   - pilot;
   - full-paper.
6. Calculate the exact number of training and evaluation jobs implied by the current specification under each plausible retraining policy.
7. Estimate compute, storage, and wall time. Flag an infeasible experiment plan before launch.
8. Define resumable job IDs, completion markers, checkpoint metadata, and rerun rules.
9. Define validation-only hyperparameter selection and protect held-out test traces.
10. Build plotting and aggregation interfaces that can run on real simulator outputs later.
11. A synthetic pipeline test is allowed only to verify schemas and plotting. Every synthetic artifact must be stored outside final result paths and labeled:
   `SYNTHETIC_PIPELINE_TEST`.
12. Do not create numerical article claims.

Create:
- `docs/echo/experiments/01_experiment_matrix.md`
- `docs/echo/experiments/02_artifact_contract.md`
- `docs/echo/experiments/03_statistical_protocol.md`
- `docs/echo/experiments/04_compute_budget.md`
- `docs/echo/experiments/05_resume_and_checkpoint_protocol.md`

Deliverable:
`docs/echo/phases/phase_03_output_contract_report.md`

Acceptance criteria:
- All fifteen panels are machine-readable.
- Raw-to-figure lineage is explicit.
- Test leakage is prevented.
- Job count and compute estimate are reported.
- The pipeline is resumable.
- No fabricated scientific output exists.

Stop after writing the report.
```

---

# 7. Phase 4 — Shared simulator kernel and method isolation

## Specialist roles

- Simulation Kernel Agent
- Architecture Agent
- Baseline-Isolation Reviewer
- Verification Agent

## Prompt

```text
Act as a simulation architecture and implementation team.

Objective:
Create or refactor a shared physical simulator kernel that supports ECHO, HOODIE, ECHO-NoLSTM, and heuristic baselines without sharing method-specific behavior.

Before editing:
- Read the Phase 1 contracts.
- Read the Phase 2 gap map.
- Read the Phase 3 artifact contract.
- Confirm the Phase 3 gate is PASS.
- Create a rollback point or patch backup.
- Respect the file-ownership plan.

Shared kernel responsibilities:
- deterministic time slots;
- task generation from reusable traces;
- task identity and descriptors;
- absolute deadlines;
- local processor;
- outbound transfer resource;
- source-indexed destination queues;
- non-preemptive active computation and transmission;
- task movement;
- destination insertion after transmission;
- processing-capacity sharing at destinations;
- successful completion;
- waiting-task expiration;
- active-task late outcome semantics;
- drain interval;
- task-location integrity;
- event logs and accounting invariants.

Method interfaces should be explicit, for example:
- `Policy`
- `SourceQueueScheduler`
- `CompletionEstimator`
- `ActionFilter`
- `RewardModel`
- `TransitionBuilder`
- `LoadEstimator`

Do not force these exact names if the repository has a cleaner native pattern, but preserve equivalent separation.

Required behavior:
1. The physical execution kernel must not import ECHO-specific ERT, mask, reward, or semi-Markov policy code.
2. The policy may select a route; the kernel executes it.
3. A direct offloading action stores its destination with the task.
4. Destination arrival occurs only after transmission completion.
5. A waiting task whose current slot is beyond its deadline is removed and resolved as dropped.
6. An active non-preemptive task retains the resource according to the frozen contract.
7. Reusable trace files allow identical tasks across all methods.
8. Every task has exactly one location/state at a time.
9. All terminal and drain behaviors follow the frozen contract.

Required tests:
- deterministic slot-order test;
- local task lifecycle;
- horizontal task lifecycle;
- vertical task lifecycle;
- source-indexed destination queues;
- simultaneous arrivals from different sources;
- non-preemptive service;
- waiting expiration;
- late active operation;
- drain interval;
- trace reuse across methods;
- generated = successful + dropped;
- no duplicate resolution;
- no multi-location task.

Create:
- architecture decision records under `docs/echo/architecture/`
- `docs/echo/architecture/method_isolation_matrix.md`
- `docs/echo/architecture/shared_kernel_runtime_trace.md`

Run the focused test suite and existing regression tests.

Deliverable:
`docs/echo/phases/phase_04_shared_kernel_report.md`

Report:
- exact files changed;
- old versus new runtime behavior;
- interface boundaries;
- tests and results;
- unresolved risks;
- rollback procedure;
- updated KG graph references.

Acceptance criteria:
- Shared physical mechanics pass deterministic tests.
- ECHO-specific logic is absent from the shared kernel.
- All methods can receive the same task trace.
- Existing unrelated behavior is not silently broken.
- KG graphs are refreshed.

Stop after writing the report.
```

---

# 8. Phase 5 — Implement deterministic ECHO mechanics

## Specialist roles

- ECHO Mechanics Agent
- Deadline/Queue Scheduling Agent
- Completion Estimation Agent
- Mathematical Verification Agent

## Prompt

```text
Act as the ECHO deterministic-mechanics implementation team.

Objective:
Implement ECHO equations and operational rules up to, but not including, neural-network training. Use deterministic or scripted policies initially so mechanics can be verified independently from learning.

Prerequisites:
- Phase 4 gate is PASS.
- Shared simulator interfaces exist.
- Equation and event contracts are frozen.

Implement in dependency order:

1. Absolute deadline and off-by-one semantics.
2. Fixed canonical action output set.
3. Physical action availability from topology.
4. Direct route action selected once at arrival.
5. Stored destination metadata for offloaded tasks.
6. Local service-duration calculation.
7. Local hypothetical waiting and completion estimates.
8. Transfer duration using horizontal or vertical rate.
9. Transfer hypothetical waiting and completion estimates.
10. Destination arrival estimate.
11. Destination workload in CPU cycles.
12. Adjusted active-queue count after hypothetical admission.
13. Effective destination capacity.
14. Destination waiting and processing estimates.
15. End-to-end offloading completion estimate.
16. Local queue-level ERT.
17. End-to-end transfer queue-level ERT.
18. Unified candidate completion estimate.
19. Candidate-level ERT.
20. Predicted-feasible task sets.
21. Non-preemptive local ERT scheduling.
22. Non-preemptive transfer ERT scheduling.
23. Minimum-lateness queue fallback.
24. Deadline-valid candidate set.
25. Minimum-lateness action fallback.
26. Effective action set.
27. Fixed-dimensional action mask.
28. Queue admission and pending decision record creation.
29. ECHO-specific task-level diagnostic logging.

Rules:
- Do not truncate completion estimates at deadlines.
- Negative predicted ERT is not the same as actual expiration.
- Prefer the smallest non-negative queue ERT.
- When all waiting tasks are predicted late, choose minimum lateness.
- FIFO is only a deterministic tie-breaker.
- The source does not reorder destination queues.
- Offloaded tasks retain their selected destination.
- The same action mask definition must later be reusable by exploration, exploitation, and target selection.
- Avoid future-information leakage in completion estimates.

For each executable ECHO equation:
1. add a focused unit test;
2. add edge-case tests;
3. add traceability from equation to file/symbol/test.

Required deterministic scenario:
Construct a hand-verifiable 2-EA + 1-cloud trace with:
- fixed arrivals;
- at least one local task;
- one horizontal task;
- one vertical task;
- queue contention;
- one deadline-feasible and one predicted-late candidate;
- a valid-set mask;
- a minimum-lateness fallback;
- an ERT-induced source-queue reordering;
- one waiting expiration;
- one late active task.

Produce a slot-by-slot table:
| slot | arrivals | estimates | ERT | mask | selected route | queues before | service | movement | resolution | queues after |

Manually verify the trace against the equations.

Create:
- `docs/echo/mechanics/equation_to_code.md`
- `docs/echo/mechanics/deterministic_trace.md`
- `docs/echo/mechanics/edge_case_catalog.md`

Deliverable:
`docs/echo/phases/phase_05_echo_mechanics_report.md`

Acceptance criteria:
- All deterministic ECHO mechanics have tests.
- The hand-calculated trace matches runtime output.
- No neural-network result is needed to verify mechanics.
- No ECHO logic leaks into HOODIE or heuristic modules.
- All masks and routes are dimensionally stable.
- KG graphs are refreshed.

Stop after writing the report.
```

---

# 9. Phase 6 — Implement ECHO DRL, LSTM, and semi-Markov learning

## Specialist roles

- DRL/LSTM Agent
- Semi-Markov Transition Agent
- Numerical Stability Reviewer
- Learning Verification Agent

## Prompt

```text
Act as the ECHO learning-system implementation team.

Objective:
Implement the frozen ECHO state, load estimation, masked Dueling Double-DQL, delayed task-level reward, pending buffer, and semi-Markov transition logic on top of the verified deterministic mechanics.

Do not alter the physical execution semantics established in Phase 4 or the deterministic ECHO mechanics established in Phase 5 except through a documented defect correction.

Implement:

A. Load representation
- observed destination workload and active-queue counts;
- fixed lookback history;
- LSTM encoder;
- frozen prediction target, decoder, loss, and update schedule from the implementation decisions;
- fresh-update versus stale/missing-update behavior;
- ECHO-NoLSTM compatible interface.

B. State
- all equation-defined task, queue, residual-service, workload, load, ERT, candidate-ERT, and mask features;
- zero task-specific features when no task arrives;
- explicit queue occupancy so empty queue differs from ERT=0;
- fixed-dimensional candidate vector;
- fixed normalization bounds;
- symmetric ERT clipping;
- no future-information leakage.

C. Reward and pending decisions
- realized system duration;
- predicted-risk indicator;
- realized-drop indicator;
- reward:
  `-duration - lambda_R*risk - lambda_D*drop`;
- pending record at decision time;
- reward attachment at resolution;
- transition finalization at the next valid decision epoch;
- terminal next-decision state at T+1.

D. Semi-Markov replay
- transition includes elapsed decision gap Delta_i;
- target uses gamma ** Delta_i;
- terminal masking;
- replay capacity;
- mini-batch sampling;
- task-to-transition identity integrity.

E. Network
- fixed canonical output dimension;
- LSTM embedding concatenation;
- fully connected layers from the frozen experiment contract;
- dueling value/advantage decomposition;
- mean advantage across canonical actions;
- online and target networks;
- no gradient through target network;
- target-copy period.

F. Action selection
- uniform exploration only within the effective action set;
- masked exploitation;
- the same mask for target-action selection;
- no invalid or masked action under any epsilon.

G. Reproducibility
- Python, NumPy, framework, environment, and device seeds;
- deterministic flags where supported;
- configuration snapshot with every checkpoint.

Required tests:
- exact state shape and ordering;
- normalization bounds;
- ERT clipping;
- no-arrival state;
- LSTM history ordering;
- stale update fallback;
- ECHO-NoLSTM behavior;
- fixed Q output dimension;
- dueling aggregation;
- mask in exploration;
- mask in exploitation;
- mask in Double-DQL next action;
- online/target separation;
- semi-Markov gamma exponent;
- terminal target;
- reward terms;
- reward linked to original task decision;
- next decision state after resolution;
- multiple tasks resolving before the next arrival;
- pending-buffer cleanup;
- replay capacity and sampling;
- target copy timing;
- deterministic inference.

Run a short learning smoke test, not a paper experiment:
- tiny topology;
- low episode count;
- one seed;
- confirm loss is finite;
- confirm gradients are finite;
- confirm checkpoints save and load;
- confirm no masked action;
- confirm replay transitions finalize.

Create:
- `docs/echo/learning/state_schema.md`
- `docs/echo/learning/lstm_contract.md`
- `docs/echo/learning/reward_and_transition_trace.md`
- `docs/echo/learning/network_and_target_tests.md`

Deliverable:
`docs/echo/phases/phase_06_learning_report.md`

Acceptance criteria:
- All learning components pass unit and integration tests.
- Semi-Markov timing is correct.
- Target selection is masked.
- No future leakage is detected.
- Smoke learning remains numerically finite.
- ECHO-NoLSTM differs only as specified.
- KG graphs are refreshed.

Stop after writing the report.
```

---

# 10. Phase 7 — Implement HOODIE and heuristic comparison methods

## Specialist roles

- Baseline Agent
- HOODIE Reproducibility Agent
- Fairness Reviewer
- Method Isolation Tester

## Prompt

```text
Act as the baseline implementation and comparison-fairness team.

Objective:
Implement or verify HOODIE and the six heuristic baselines on the shared physical kernel without importing ECHO-only behavior.

Methods:
1. HOODIE
2. Random Offloader (RO)
3. Full Local Computing (FLC)
4. Vertical Offloader (VO)
5. Horizontal Offloader (HO)
6. Balanced Cyclic Offloader (BCO)
7. Minimum Latency Estimation Offloader (MLEO)
8. ECHO-NoLSTM as an ECHO ablation, not a generic baseline

Rules:
- Use the same physical task traces, topology, capacities, rates, deadlines, and seeds.
- Use the frozen method-isolation contract.
- HOODIE follows its own documented state, action, reward, queue, and learning semantics.
- Do not give HOODIE ECHO queue scheduling, ECHO action masking, ECHO reward, candidate ERT features, or ECHO semi-Markov transitions unless the frozen fairness decision explicitly requires a shared mechanism.
- Heuristic baselines do not train.
- Heuristic methods use only information permitted by their definitions.
- HO must define deterministic handling when no horizontal neighbor exists.
- RO samples only physically valid actions.
- BCO cycles deterministically over available route types and defines tie/destination rules.
- MLEO uses its own estimated-latency definition, not ECHO’s deadline mask.
- Baseline queue discipline must be explicit, normally FIFO unless the method contract states otherwise.

For each method write:
- allowed information;
- action rule;
- queue scheduler;
- estimator;
- reward/training use;
- tie-breaking;
- fallback;
- expected deterministic behavior.

Required tests:
- same trace IDs and task descriptors across methods;
- no ECHO-specific module imported by HOODIE or heuristics;
- RO never selects invalid physical actions;
- FLC always local;
- VO always cloud;
- HO always horizontal when possible;
- BCO cycle correctness;
- MLEO minimum estimated latency;
- HOODIE deterministic mechanics;
- independent model/checkpoint namespaces;
- identical physical accounting invariants.

Create:
- `docs/echo/baselines/method_definitions.md`
- `docs/echo/baselines/method_isolation_runtime_test.md`
- `docs/echo/baselines/fairness_matrix.md`
- `docs/echo/baselines/hoodie_traceability.md`

Deliverable:
`docs/echo/phases/phase_07_baselines_report.md`

Acceptance criteria:
- All comparison methods run on the shared kernel.
- Method behavior matches its definition.
- ECHO-only components do not contaminate baselines.
- Identical held-out traces can be consumed by all methods.
- Fairness tests pass.
- KG graphs are refreshed.

Stop after writing the report.
```

---

# 11. Phase 8 — Full verification and smoke artifact generation

## Specialist roles

- Verification Agent
- Invariant and Property-Test Agent
- Output Pipeline Agent
- Independent Gate Auditor

## Prompt

```text
Act as the full-system verification team.

Objective:
Prove that the simulator, ECHO, HOODIE, baselines, learning, logging, and artifact pipeline are internally consistent before pilot experiments.

Run:

1. Static analysis, formatting, type checks, and lint where configured.
2. Existing project tests.
3. New equation-level tests.
4. Task lifecycle integration tests.
5. Method isolation tests.
6. State/mask/replay/target tests.
7. Deterministic hand trace.
8. Property-based or randomized invariant tests where practical.
9. One end-to-end smoke run for every method.
10. One tiny ECHO training/evaluation cycle.
11. One tiny HOODIE training/evaluation cycle.
12. One artifact-generation run that produces real:
    - task logs;
    - episode metrics;
    - seed metrics;
    - panel CSV;
    - vector figure;
    - 300-dpi PNG;
    - run manifest;
    - checkpoint metadata.

Do not represent smoke outputs as paper results.

Required invariants:
- generated = successful + dropped;
- one terminal outcome per task;
- no task in multiple locations;
- no masked ECHO action;
- no invalid physical action;
- no disconnected horizontal action;
- destination insertion follows completed transmission;
- identical traces across methods;
- no test trace used for tuning;
- no NaN or infinite reward, loss, Q value, ERT, completion estimate, or metric;
- output files match schemas;
- plots are regenerated from retained CSV rather than hidden state.

Run a differential trace:
- same tiny workload under ECHO and HOODIE;
- identify exactly why their actions or queue orders differ;
- show that differences are intended by the method-isolation contract.

Create:
- `docs/echo/verification/test_inventory.md`
- `docs/echo/verification/invariant_results.md`
- `docs/echo/verification/differential_trace.md`
- `docs/echo/verification/smoke_artifact_index.md`

Deliverable:
`docs/echo/phases/phase_08_verification_report.md`

Acceptance criteria:
- All critical tests pass.
- Every smoke method completes.
- Real simulator data can produce the required artifact types.
- No output is mislabeled as a paper result.
- No S0 or S1 gap remains open.
- S2 gaps are either resolved or explicitly approved.

Stop after writing the report.
```

---

# 12. Phase 9 — Pilot experiments and tuning freeze

## Specialist roles

- Pilot Experiment Agent
- Hyperparameter Selection Agent
- Statistical Diagnostics Agent
- Compute/Failure Auditor

## Prompt

```text
Act as the pilot-experiment and tuning-freeze team.

Objective:
Run a reduced but representative subset of the ECHO evaluation to detect instability, implementation defects, infeasible compute cost, and broken expected mechanisms before launching the full paper matrix.

Prerequisite:
Phase 8 gate is PASS.

Pilot rules:
- Use dedicated validation traces.
- Never use final held-out test traces.
- Use 2-3 seeds unless the compute plan justifies more.
- Use reduced training episodes.
- Include low, medium, and high load.
- Include at least one strict-deadline scenario.
- Include at least one topology size different from N=20.
- Include ECHO, HOODIE, ECHO-NoLSTM, and selected heuristics.
- Preserve paired traces across methods.

Pilot objectives:
1. Verify learning is stable enough to justify full training.
2. Verify candidate masks are neither always empty nor always full.
3. Verify fallback occurs under overloaded/strict conditions.
4. Verify ERT scheduling changes queue order in nontrivial cases.
5. Verify ECHO logs explain actions and outcomes.
6. Verify no result is dominated by an accounting bug.
7. Estimate actual runtime and storage per full-paper job.
8. Validate checkpoint resume.
9. Validate failed-job retry without duplicating completed jobs.
10. Select hyperparameters only from the approved validation grid.
11. Freeze:
    - learning rate;
    - discount factor;
    - lambda_R;
    - lambda_D;
    - ERT clipping;
    - LSTM settings;
    - checkpoint-selection rule.
12. Do not select a value merely because it makes ECHO beat HOODIE.
13. Report unstable or negative ECHO results honestly.

Produce:
- pilot task logs;
- validation metrics;
- confidence intervals where meaningful;
- compute estimates;
- selected configuration;
- rejected configurations and reasons;
- rerun manifest;
- failure log.

Create:
- `docs/echo/pilot/01_pilot_matrix.md`
- `docs/echo/pilot/02_learning_diagnostics.md`
- `docs/echo/pilot/03_mechanism_diagnostics.md`
- `docs/echo/pilot/04_hyperparameter_freeze.md`
- `docs/echo/pilot/05_full_run_resource_forecast.md`

Deliverable:
`docs/echo/phases/phase_09_pilot_report.md`

Acceptance criteria:
- Validation and held-out test data remain separate.
- Hyperparameters are frozen with evidence.
- Resume/retry is proven.
- Actual compute cost is known.
- No unresolved numerical instability remains.
- The full experiment matrix is feasible or a precise reduction proposal is made.

Stop after writing the report.
```

---

# 13. Phase 10 — Full-paper experiment execution

## Specialist roles

- Experiment Orchestrator
- Training Workers
- Evaluation Workers
- Aggregation Agent
- Plotting Agent
- Runtime Integrity Monitor

## Prompt

```text
Act as the full-paper experiment orchestration team.

Objective:
Execute the frozen ECHO evaluation contract using resumable, auditable jobs and generate the final raw and aggregated outputs for Figures 4-8.

Prerequisites:
- Phase 9 gate is PASS.
- Hyperparameters and validation decisions are frozen.
- Final held-out traces have not been used.
- Compute budget is approved.

Execution rules:
1. Use the exact machine-readable experiment manifest.
2. Assign a unique deterministic job ID to every method/seed/configuration.
3. Reuse completed valid jobs.
4. Resume interrupted learning from verified checkpoints.
5. Never overwrite a valid completed run silently.
6. Store the full configuration, source revision, environment, device, seed, topology, trace set, checkpoint, and schema version with every run.
7. Pair identical held-out trace identifiers across methods.
8. Learning-based methods receive the frozen fair training budget.
9. Heuristic baselines do not receive hidden training or ECHO-only information.
10. Evaluate final held-out traces once for reporting.
11. Preserve all task-level logs required by the output contract.
12. Pool generated and dropped counts across the 200 episodes for each method/seed/operating point before computing seed-level drop ratios.
13. Compute reported means and 95% confidence intervals across seeds.
14. Export:
    - panel-level CSV;
    - seed-level CSV;
    - vector composite figure;
    - 300-dpi PNG;
    - panel exports;
    - artifact manifest.
15. Generate Figure 4 directly from the actual topology used by the simulator.
16. Never infer missing points or smooth curves deceptively.
17. Never hide operating points where ECHO equals or underperforms HOODIE.
18. Every plotted value must link back to raw logs.

Continuously validate:
- task accounting;
- no masked ECHO action;
- identical traces;
- finite metrics;
- correct checkpoint identity;
- no test leakage;
- estimator/execution consistency.

Required experiment status:
`artifacts/reports/full_experiment_status.md`

It must list:
| Job ID | Panel | Method | Seed | Config | Status | Checkpoint | Raw logs | Metrics | Retry count |

When all valid jobs complete:
- aggregate;
- calculate confidence intervals;
- create final figures;
- create raw-to-figure lineage;
- generate a result table comparing ECHO and HOODIE by absolute and relative difference.

Create:
- `artifacts/reports/figure_lineage.md`
- `artifacts/reports/full_experiment_integrity.md`
- `artifacts/reports/result_summary_without_claim_inflation.md`

Deliverable:
`docs/echo/phases/phase_10_full_experiments_report.md`

Acceptance criteria:
- All required jobs are complete or explicitly blocked.
- Every figure value is traceable to raw logs.
- All required CSV/vector/PNG outputs exist.
- Statistical aggregation follows the frozen protocol.
- No result is fabricated, hidden, or tuned on test data.
- Incomplete panels are labeled incomplete rather than guessed.

Stop after writing the report.
```

---

# 14. Phase 11 — Independent final audit and final Markdown report

## Specialist roles

- Independent Reproducibility Auditor
- Scientific Claims Auditor
- Code/Artifact Traceability Auditor
- Final Report Writer

## Prompt

```text
Act as an independent final auditor and scientific reproducibility report writer.

You must not assume that phase reports are correct. Verify important claims directly from:
- source specifications;
- source code;
- git diff;
- tests;
- KG graphs;
- configurations;
- raw logs;
- aggregated CSVs;
- checkpoints;
- figures;
- artifact manifests.

Objective:
Produce the final implementation and experimental report for ECHO.

Required audit:

1. Verify source authority and document snapshots.
2. Verify every ECHO equation has:
   - implementation status;
   - file/symbol mapping;
   - test;
   - runtime evidence where applicable.
3. Verify algorithm and slot-order fidelity.
4. Verify method isolation.
5. Verify HOODIE and baseline fairness.
6. Verify state, mask, reward, pending buffer, replay, semi-Markov target, LSTM, and target-network behavior.
7. Verify accounting invariants.
8. Verify smoke, pilot, and full-paper separation.
9. Verify validation/test separation.
10. Verify all figure values against raw logs.
11. Verify statistical calculations.
12. Verify vector and PNG exports.
13. Verify reproducibility commands from a clean environment where feasible.
14. Identify any unsupported article claim.
15. Identify every remaining ambiguity, approximation, or incomplete experiment.
16. Identify cases where ECHO is not better than HOODIE.
17. Check for hard-coded outputs or result manipulation.
18. Check that the final repository can reproduce the outputs with documented commands.

Create this exact file:
`artifacts/reports/ECHO_FINAL_IMPLEMENTATION_REPORT.md`

Required structure:

# ECHO Final Implementation and Reproducibility Report

## 1. Executive verdict
Choose:
- Faithful and fully evaluated
- Faithful with documented approximations
- Mechanically complete but experimentally incomplete
- Partially implemented
- Scientifically unreliable

## 2. Source authority and repository identity
Document revisions, hashes, git commit, environment.

## 3. Implemented ECHO contribution
Explain:
- end-to-end completion estimation;
- local and transfer ERT;
- non-preemptive ERT scheduling;
- valid-action mask;
- minimum-lateness fallback;
- direct route decision;
- delayed reward;
- semi-Markov transition;
- masked Dueling Double-DQL;
- LSTM/recovery behavior.

## 4. Equation-to-code coverage
Counts and full traceability reference.

## 5. Runtime event order
Exact slot sequence.

## 6. Shared-kernel and method isolation
What is shared and what is method-specific.

## 7. Test and invariant results
Pass/fail counts, critical failures, exact commands.

## 8. Smoke and pilot results
Purpose, outputs, and tuning decisions.

## 9. Full experiment status
Completed, failed, skipped, or blocked jobs.

## 10. Figure-by-figure results
For every Figure 4-8 panel:
- configuration;
- methods;
- raw files;
- aggregated values;
- CI;
- interpretation;
- ECHO vs HOODIE difference;
- limitations.

## 11. Ablation results
ECHO versus ECHO-NoLSTM.

## 12. Negative or inconclusive results
Report honestly.

## 13. Reproducibility commands
Environment, tests, smoke, training, evaluation, aggregation, plotting.

## 14. Files created or modified
Purpose of each.

## 15. Remaining risks and assumptions
Ranked by severity.

## 16. Rollback
Exact safe rollback procedure.

## 17. Artifact index
Paths to contracts, configs, logs, CSVs, checkpoints, figures, reports.

## 18. Claim-support table
| Proposed claim | Supporting artifact | Strength | Limitation |

## 19. Final recommendation
Choose exactly one:
- Reject
- Rethink
- Test
- Proceed with Caution
- Strong

Also create:
`artifacts/reports/ECHO_FINAL_ARTIFACT_INDEX.md`

Do not modify scientific source code during this audit.
If a defect is discovered, report it. Do not conceal it by silently fixing outputs.

Stop after writing both reports.
```

---

# 15. Final handoff prompt for ChatGPT analysis

After the agents finish, upload or share:

1. `artifacts/reports/ECHO_FINAL_IMPLEMENTATION_REPORT.md`
2. `artifacts/reports/ECHO_FINAL_ARTIFACT_INDEX.md`
3. `docs/echo/contracts/06_ambiguity_register.md`
4. `docs/echo/contracts/07_implementation_decisions.md`
5. `docs/echo/verification/invariant_results.md`
6. `artifacts/reports/figure_lineage.md`
7. The final figure files or panel CSVs
8. The final git diff summary

Then use:

```text
Act as an independent ruthless scientific reviewer of my ECHO implementation.

I am providing the final multi-agent implementation report and its supporting artifacts.

Evaluate:
1. Whether the implementation actually matches the ECHO method specification.
2. Whether the result pipeline is scientifically defensible.
3. Whether HOODIE and the heuristic baselines were compared fairly.
4. Whether the reported figures are supported by raw evidence.
5. Whether any assumptions weaken the paper contribution.
6. Whether the implementation contains data leakage, reward errors, event-order errors, masking errors, or method contamination.
7. Which claims the article can safely make.
8. Which claims must be weakened or removed.
9. What must be fixed before submission.

Start with the most serious failure point.

Separate:
- confirmed facts;
- assumptions;
- unsupported claims;
- implementation defects;
- experimental limitations;
- recommended corrections.

End with exactly one rating:
Reject / Rethink / Test / Proceed with Caution / Strong
```

---

# 16. Operating sequence

Run exactly in this order:

```text
Phase 0
Gate 0
Phase 1
Gate 1
Phase 2
Gate 2
Phase 3
Gate 3
Phase 4
Gate 4
Phase 5
Gate 5
Phase 6
Gate 6
Phase 7
Gate 7
Phase 8
Gate 8
Phase 9
Gate 9
Phase 10
Gate 10
Phase 11
Final ChatGPT analysis
```

Do not merge phases merely to save time. The major failure risk is allowing implementation assumptions to become invisible before the scientific contract and output contract are frozen.
