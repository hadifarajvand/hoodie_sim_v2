<!-- Sync Impact Report
Version change: 1.2.0 -> 1.3.0
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
- ✅ `.specify/templates/plan-template.md`
- ✅ `.specify/templates/spec-template.md`
- ✅ `.specify/templates/tasks-template.md`
Follow-up TODOs: none
-->

# hoodie_sim_v2 Constitution

## Core Principles

### 1. Dependency Control Rule

All dependencies MUST remain declared, versioned, and approved before they are added,
upgraded, or removed. No script, notebook, or shell command may install packages implicitly.
The tracked dependency file is the source of truth for direct project dependencies.

Rationale: hidden installs and undeclared dependencies make the environment non-reproducible.

### 2. Environment Rule

Work MUST use the approved virtual environment at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venv`
until the project is explicitly re-baselined. No new virtual environments may be created without
approval. Commands and scripts MUST run through the approved environment, and every execution must
record the Python version and environment details when relevant.

Rationale: a stable interpreter boundary prevents drift between development, evaluation, and
reproduction runs.

### 3. Assumptions Rule

Any missing, ambiguous, or unrecoverable paper detail MUST be recorded before code depends on it.
High-impact assumptions require explicit user review before adoption, especially for reward logic,
topology, task distributions, state representation, and training hyperparameters. Every assumption
entry MUST state the missing detail, the chosen rule, the justification, the expected impact, and
the validation plan.

Rationale: reproduction must remain separate from guesswork.

### 4. Fidelity Rule

The simulator MUST preserve paper behavior for queues, delays, rewards, topology, and timing.
Simplification is forbidden unless it is documented, justified, and explicitly approved. "Cleaner
implementation" is not a valid reason to deviate from paper behavior.

Rationale: scientific value depends on paper-faithful behavior, not convenience.

### 5. Implementation Order Rule

Work MUST proceed in this order unless the user explicitly approves a different sequence:
environment and queue system, baseline policies, HOODIE DRL agent, experiment runners, analysis and
plots. No neural network code may be added before the environment is testable.

Rationale: the simulator foundation must exist before learning logic can be trusted.

### 6. Testing Rule

FIFO behavior, queue waiting time, task completion timing, deadline expiration, offloading
transitions, action legality under topology constraints, and delayed reward assignment MUST each
have unit coverage. Every environment behavior required by the paper MUST map to at least one test.
Bug fixes affecting simulation logic MUST include a regression test, and integration tests MUST
cover at least one baseline policy and one learned-policy placeholder or stub.

Rationale: the simulation core is only credible when behavior is verified directly.

### 7. Reproducibility Rule

Every experiment MUST use fixed seeds, config files, logged environment details, and trace
identifiers. Training and evaluation seeds MUST be recorded separately. All relevant RNG sources
MUST be explicitly seeded.

Rationale: a result without complete traceability cannot be reproduced or audited.

### 8. Configuration Rule

All tunable parameters MUST come from paper values, config files, or documented assumptions.
Hardcoded constants are allowed only when they are named, justified, and stable. Config files MUST
distinguish paper-recovered defaults, assumption-based defaults, and experiment overrides.

Rationale: configuration drift is hidden logic.

### 9. Architecture Rule

Environment, baselines, learning agents, training loop, configs, tests, and analysis MUST remain
separate concerns. Environment code owns simulator lifecycle and queue mechanics. Baselines own
policy behavior. Training owns orchestration only.

Rationale: separation keeps the reproduction maintainable and auditable.

### 10. Validation Rule

Comparison artifacts, metrics, and trace inputs MUST be defined up front. Shared evaluation traces
or paired-seed control MUST be used across compared policies. Any deviation from the paper or from
the recovered protocol MUST be documented and justified before implementation.

Rationale: fair comparison requires a shared evaluation contract.

### 11. Reward Integrity Rule

Reward MUST be emitted only when a task reaches a terminal state: completed or dropped. Reward
must never be emitted at decision time. If an action is selected in slot `t`, the reward belongs to
the later terminal event, not to the action itself.

Rationale: delayed reward timing is part of the simulator semantics.

### 12. Traceability Rule

Debug traces MUST support task lifecycle reconstruction across arrival, queue admission,
offloading, execution, completion, drop, reward emission, and metric updates. Trace records must be
rich enough to explain each terminal outcome without hidden state.

Rationale: traceability is required for reproducibility and debugging.

### 13. Change Scope Rule

Only files required for the approved phase may be modified. Opportunistic refactors, unrelated
cleanup, and broad rewrites are forbidden unless the user approves them explicitly.

Rationale: scoped changes reduce risk and preserve reviewability.

### 14. Hardware Awareness Rule

Work MUST respect the declared local development targets and any explicit hardware constraints in
the repository. Environment-specific behavior must be documented rather than implied.

Rationale: hardware drift can invalidate runtime assumptions.

### 15. Experiment Budget Rule

Staged experiments MUST remain staged. Costly runs, sweeps, and validation passes must be ordered so
that lower-cost checks happen before expensive ones. Resource usage must be justified by the
experiment phase.

Rationale: the reproduction should be economical and intentional.

### 16. Paper-to-Code Mapping Rule

Paper sections, equations, and tables that influence behavior MUST be mapped to code locations in
the paper notes. Any new environment behavior must update the mapping before the implementation is
considered complete.

Rationale: the project must show where the paper lives in the codebase.

### 17. Configuration Freeze Rule

Result-bearing configs MUST be versioned and not edited in place. Reported results must preserve the
exact config snapshot and hash used to generate them.

Rationale: frozen configs prevent accidental result drift.

### 18. Failure Transparency Rule

Missing paper details, rejected assumptions, and unresolved deviations MUST be surfaced explicitly.
They may not be hidden in comments, implicit fallbacks, or silent code paths.

Rationale: the project must distinguish recovery from invention.

### 19. Baseline Fairness Rule

Baselines and HOODIE MUST share the same environment semantics, workload control, and metric
pipeline. No baseline may use a different simulator path or a different definition of evaluation
success.

Rationale: fair comparison is the point of the reproduction.

### 20. Resource Management Rule

Paper resources, OCR artifacts, and vendored reference material MUST be kept separate by authority
level and provenance. Generated outputs, caches, and local virtual environments MUST not be tracked
unless explicitly approved.

Rationale: the repository must preserve provenance without becoming landfill.

## Additional Constraints

- ns-3-gym is forbidden unless the user explicitly changes the architecture.
- New neural-network code is forbidden outside the approved HOODIE agent scope.
- Dependency files may not change without explicit approval.
- Large directory moves, vendoring, and frozen config edits require prior approval.

## Development Workflow

1. Confirm the approved scope before editing.
2. Record assumptions before code depends on them.
3. Write or update tests for every behavior change.
4. Keep environment, policy, evaluation, training, and analysis layers separate.
5. Validate deterministic behavior and shared evaluation semantics before merging.

## Governance

This constitution supersedes ad hoc workflow preferences. Amendments require explicit user approval,
an updated sync impact report, and any necessary propagation to the spec-kit templates or runtime
guidance docs. Versioning follows semantic versioning:

- MAJOR: backward-incompatible principle removals or redefinitions
- MINOR: new principle, new section, or materially expanded guidance
- PATCH: clarifications, wording fixes, or non-semantic refinements

Compliance reviews MUST verify that proposed changes satisfy the constitution before implementation.
If the user has instructed that every action be approved before execution, that instruction MUST be
treated as a governing constraint for the current session and respected before edits, refactors, or
other repository actions.

**Version**: 1.3.0 | **Ratified**: 2026-04-21 | **Last Amended**: 2026-04-30
