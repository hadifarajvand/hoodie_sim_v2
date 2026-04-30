<!-- Sync Impact Report
Version change: 1.1.0 -> 1.2.0
Modified principles:
- 1. Dependency Control Rule
- 2. Environment Rule
- 3. Assumptions Rule
- 4. Fidelity Rule
- 5. Implementation Order Rule
- 6. Testing Rule
- 7. Reproducibility Rule
- 8. Configuration Rule
- 9. Architecture Rule
- 10. Validation Rule
- 11. Reward Integrity Rule
- 12. Traceability Rule
- 13. Change Scope Rule
- 14. Hardware Awareness Rule
- 15. Experiment Budget Rule
- 16. Paper-to-Code Mapping Rule
- 17. Configuration Freeze Rule
- 18. Failure Transparency Rule
- 19. Baseline Fairness Rule
- 20. Resource Management Rule
Added sections: none
Removed sections: none
Templates requiring updates:
- ⚠ pending `.specify/templates/plan-template.md`
- ⚠ pending `.specify/templates/spec-template.md`
- ⚠ pending `.specify/templates/tasks-template.md`
- ⚠ pending `.specify/extensions/git/commands/speckit.git.remote.md`
- ⚠ pending `.specify/extensions/git/README.md`
Follow-up TODOs: none
-->

# Project Constitution — hoodie_sim_v2

## Core Principles

### 1. Dependency Control Rule

#### Mandatory Statements

- No package installation, upgrade, or removal may occur without explicit user approval.
- All direct project dependencies must be declared in the tracked project dependency file.
- Scripts, notebooks, and shell commands must not perform implicit installs.
- Any proposed dependency must document:
  - purpose
  - alternative, if one exists
  - impact on reproducibility

#### Rationale

Hidden installs and undeclared dependencies make the environment non-reproducible.

#### Enforcement Implication

Code or changes that introduce undeclared or unapproved dependencies must be rejected.

### 2. Environment Rule

#### Mandatory Statements

- Development must use the user-approved Python virtual environment until the project is
  explicitly re-baselined.
- The approved environment path is `/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venv`.
- If the approved environment changes, the constitution must be updated explicitly.
- No new virtual environments may be created without approval.
- The approved environment must not be modified without approval.
- All commands and scripts must run through the approved environment, not the system interpreter.
- Every run must record Python version and environment details.
- If the approved environment is unavailable or broken, work must stop and be reported.

#### Rationale

This prevents interpreter drift and keeps execution behavior stable.

#### Enforcement Implication

Any execution outside the approved environment or with unapproved environment changes must stop.

### 3. Assumptions Rule

#### Mandatory Statements

- Any missing, ambiguous, or unrecoverable detail from the paper must be recorded before code
  depends on it.
- High-impact assumptions require user review before adoption, especially for:
  - reward logic
  - topology
  - task distributions
  - state representation
  - training hyperparameters
- Each assumption entry must record:
  - missing detail
  - chosen value or rule
  - justification
  - expected impact
  - validation plan
- No code may depend on undocumented assumptions.

#### Rationale

This keeps reproduction separate from guesswork.

#### Enforcement Implication

Undocumented assumptions are not valid implementation inputs.

### 4. Fidelity Rule

#### Mandatory Statements

- The simulator must match paper behavior for queues, delays, rewards, topology, and timing.
- Simplification is forbidden unless it is:
  - documented
  - justified
  - approved
- "Cleaner implementation" is not a valid reason to deviate from paper behavior.
- If a simplification is necessary, it must be proposed before implementation.

#### Rationale

This protects the scientific value of the simulation.

#### Enforcement Implication

Undocumented deviations from paper behavior must be rejected.

### 5. Implementation Order Rule

#### Mandatory Statements

Work must proceed in this order unless the user explicitly approves a different sequence:

1. environment and queue system
2. baseline policies
3. HOODIE DRL agent
4. experiment runners
5. analysis and plots

- No neural network code may be added before the environment is testable.
- Supporting test scaffolding is allowed earlier only when it does not depend on unfinished logic.

#### Rationale

This prevents premature complexity and keeps the foundation testable.

#### Enforcement Implication

Work that violates the approved sequence must be blocked.

### 6. Testing Rule

#### Mandatory Statements

The following behaviors must have unit coverage:

- FIFO behavior
- queue waiting time calculation
- task completion timing
- deadline expiration
- offloading transitions
- action legality under topology constraints
- delayed reward assignment

Additional requirements:

- Every environment behavior required by the paper must map to at least one test.
- Bug fixes affecting simulation logic must include a regression test.
- Integration tests must cover full episode execution for:
  - at least one baseline policy
  - one learned-policy placeholder or stub

#### Rationale

The simulation core is only credible if it is tested at the behavior level.

#### Enforcement Implication

Untested critical logic cannot be merged or trusted.

### 7. Reproducibility Rule

#### Mandatory Statements

Every experiment must:

- use a fixed random seed
- load configuration from a file
- log:
  - config
  - seed
  - commit or version
- save raw outputs used for plots
- log device used (`cpu`, `mps`, or `cuda`)
- log software environment snapshot
- record training and evaluation seeds independently
- log evaluation trace bank ID or workload seed set
- explicitly seed all RNG sources:
  - Python
  - NumPy
  - PyTorch

#### Rationale

Without complete traceability, results cannot be reproduced exactly.

#### Enforcement Implication

Any result without full traceability is invalid.

### 8. Configuration Rule

#### Mandatory Statements

- All parameters must come from:
  - paper values
  - config files
  - documented assumptions
- Hardcoded constants are allowed only when they are named, justified, and stable.
- Configuration files must distinguish:
  - paper-recovered defaults
  - assumption-based defaults
  - experiment overrides
- Config files must be human-readable and version-controlled.

#### Rationale

This prevents hidden logic and configuration drift.

#### Enforcement Implication

Undocumented parameters must be removed or documented.

### 9. Architecture Rule

#### Mandatory Statements

The codebase must keep the following concerns separated:

- environment
- baselines
- learning agents
- training loop
- configs
- tests
- analysis

#### Rationale

This prevents a monolithic implementation that becomes hard to maintain.

#### Enforcement Implication

Structural violations must be refactored before acceptance.

### 10. Validation Rule

#### Mandatory Statements

Implementation is not complete unless:

- results match the paper's workflow and behavior at the level the paper supports
- baseline ordering is consistent with the paper
- parameter sweeps produce directionally correct trends
- deviations are explicitly documented

Validation artifacts must include:

- config used
- seed used
- raw metrics
- generated plot
- short interpretation note

Validation must distinguish:

- exact paper-matched behavior
- assumption-dependent behavior
- calibrated behavior

#### Rationale

This makes validation auditable instead of anecdotal.

#### Enforcement Implication

Unvalidated results are not acceptable.

### 11. Reward Integrity Rule

#### Mandatory Statements

- Rewards must be assigned only on actual task completion or drop timing.
- No shortcut rewards at decision time are allowed unless the paper explicitly defines them.
- Reward timing must remain aligned with the documented simulator event lifecycle.

#### Rationale

Incorrect reward timing invalidates reinforcement learning behavior.

#### Enforcement Implication

Improper reward handling invalidates the model.

### 12. Traceability Rule

#### Mandatory Statements

- The simulator must support a debug mode that records:
  - task creation
  - action selection
  - queue insertion and removal
  - offload completion
  - task completion
  - task drop
- Debug traces must support reconstruction of an individual task lifecycle.
- Normal runs may reduce logging, but summary metrics must remain traceable.

#### Rationale

This enables debugging and forensic verification.

#### Enforcement Implication

Untraceable behavior is a defect.

### 13. Change Scope Rule

#### Mandatory Statements

- Codex must not perform opportunistic refactors, dependency changes, file moves, or style-only edits
  outside the requested scope.
- Broader changes must be proposed before implementation.

#### Rationale

This prevents uncontrolled modifications from polluting a task.

#### Enforcement Implication

Out-of-scope changes must be reverted or blocked.

### 14. Hardware Awareness Rule

#### Mandatory Statements

- Development must account for the real hardware constraints of the current project setup.
- Large experiments must consider runtime and memory limits before execution.
- Heavy runs must be proposed before execution.

#### Rationale

This keeps implementation choices realistic.

#### Enforcement Implication

Unplanned heavy workloads must be halted.

### 15. Experiment Budget Rule

#### Mandatory Statements

Experiments must proceed in stages:

1. environment sanity tests
2. baseline validation runs
3. short HOODIE smoke runs
4. calibration runs
5. final reproduction runs

- Early stages must use reduced configurations for speed.
- Full-scale training must not start before earlier stages pass.

#### Rationale

This avoids wasting compute on broken setups.

#### Enforcement Implication

Skipping stages invalidates the experiment process.

### 16. Paper-to-Code Mapping Rule

#### Mandatory Statements

- Core simulator behavior must map to a paper equation, table, or documented assumption.
- A mapping must be maintained between:
  - paper section, equation, or table
  - code module or function
  - config entry
- The mapping must be stored in a dedicated document, such as `paper_mapping.md`.
- If no mapping exists, the implementation is incomplete.

#### Rationale

This keeps theory-to-code traceability explicit.

#### Enforcement Implication

Unmapped logic must be documented or removed.

### 17. Configuration Freeze Rule

#### Mandatory Statements

- Once a config is used for results, it must not be edited in place.
- Any change requires a new config version or filename.
- Result artifacts must reference the exact frozen config used.

#### Rationale

This prevents silent corruption of prior results.

#### Enforcement Implication

Modified configs invalidate prior results that depended on them.

### 18. Failure Transparency Rule

#### Mandatory Statements

- If a critical paper detail is missing and no approved assumption exists, work must stop and be
  reported.
- Divergence from expected results must be reported with the most plausible cause.
- Silent fallback behavior is forbidden.

#### Rationale

This prevents hidden errors and false confidence.

#### Enforcement Implication

Undocumented failures invalidate the work.

### 19. Baseline Fairness Rule

#### Mandatory Statements

- All baselines and HOODIE must use the same:
  - environment
  - task generation process
  - topology
  - queue semantics
  - deadline rules
  - metric definitions
- For each comparison run, the following must match:
  - episode length
  - number of evaluation episodes
  - fixed evaluation trace bank or identical workload realizations
  - simulator logic
  - validation protocol
- All performance metrics must be computed by a shared evaluation module.
- Baselines must not be handicapped by:
  - reduced state access unless that limitation is intrinsic
  - fewer episodes
  - different traces
  - altered environment logic
- HOODIE must not gain unfair advantages via:
  - privileged future information
  - altered reward timing
  - altered metrics
  - different workload generation
- Baselines must be implemented as policy modules over the shared environment.
- Any deviation or approximation must be documented and tested.

#### Rationale

This keeps comparisons defensible.

#### Enforcement Implication

Any unfair comparison invalidates results.

### 20. Resource Management Rule

#### Mandatory Statements

- All external resources, including papers, OCR text, references, and datasets, must live in a
  structured directory.
- Resources must be categorized as:
  - primary sources
  - derived sources
  - reference materials
- Each resource must include metadata:
  - source
  - purpose
  - version, if applicable
- No resource may influence implementation unless it is explicitly referenced in project
  documentation.

#### Rationale

This prevents undocumented source leakage.

#### Enforcement Implication

Untracked or undocumented resources must not influence implementation.

## Governance

This constitution supersedes all other project guidance. Amendments require explicit user approval
and must preserve traceability. Any amendment must update the version, ratification history if
needed, and the sync impact report at the top of this file. Compliance is expected in reviews,
implementation, testing, and evaluation artifacts. If this constitution conflicts with other
guidance, the constitution wins; if a conflict cannot be resolved cleanly, work must stop and be
reported.

Amendment procedure:

1. Propose the change with a concrete rationale.
2. Classify the change as MAJOR, MINOR, or PATCH.
3. Update the constitution and dependent templates together when the change affects them.
4. Verify the sync impact report and any deferred follow-ups.

Versioning policy:

- MAJOR: backward-incompatible governance or principle redefinition.
- MINOR: new principle, new section, or materially expanded guidance.
- PATCH: wording, clarity, or typo corrections that do not change enforcement meaning.

Compliance review expectations:

- Every feature plan must pass the constitution gate before research begins.
- Every spec, task set, and implementation must remain aligned with the current constitution.
- Any observed divergence must be called out explicitly, not hidden in implementation notes.

**Version**: 1.2.0 | **Ratified**: 2026-04-21 | **Last Amended**: 2026-04-28
