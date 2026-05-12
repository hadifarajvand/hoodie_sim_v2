<!-- Sync Impact Report
Version change: 1.3.0 -> 1.3.1
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
Added principles:
- 21. CI Quality Gate Rule
- 22. Public Interface Stability Rule
- 23. Config Schema Validation Rule
- 24. Structured Logging and Observability Rule
- 25. Security and Secret Hygiene Rule
- 26. Packaging and Execution Rule
- 27. Artifact Lifecycle Rule
- 28. Performance Budget Rule
- 29. Review and Merge Gate Rule
- 30. Definition of Done Rule
Added sections: none
Removed sections: none
Templates requiring updates:
- ✅ `.specify/templates/plan-template.md`
- ✅ `.specify/templates/spec-template.md`
- ✅ `.specify/templates/tasks-template.md`
Follow-up TODOs: Update any runtime guidance still pointing at `.venv` so it matches the re-based interpreter.
-->

# hoodie_sim_v2 Constitution

## Core Principles

### 1. Dependency Control Rule

All dependencies MUST remain declared, versioned, and approved before they are added,
upgraded, or removed. No script, notebook, or shell command may install packages implicitly.
The tracked dependency file is the source of truth for direct project dependencies.

Rationale: hidden installs and undeclared dependencies make the environment non-reproducible.

### 2. Environment Rule

Work MUST use the approved virtual environment at
`/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` until the project is
explicitly re-baselined. No new virtual environments may be created without approval. Commands and
scripts MUST run through the approved environment, and every execution must record the Python
version and environment details when relevant.

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

### 21. CI Quality Gate Rule

Every change intended for merge MUST pass the approved automated quality gate. The minimum gate
includes unit tests, integration tests relevant to the touched area, smoke validation when
environment, evaluation, or training behavior changes, and lint or formatting checks and type
checks when configured. If a check is unavailable because tooling is not configured, the gap MUST
be documented. Failing checks MUST not be bypassed without explicit user approval and a documented
rationale.

Rationale: automated checks are the only scalable way to enforce the constitution.

### 22. Public Interface Stability Rule

Stable interfaces MUST not be changed casually. Protected interfaces include environment reset/step
behavior, the policy interface, the task model, the topology interface, the runtime model
interface, the evaluation metric interface, the config schema, and the artifact schema. Any
breaking interface change MUST document affected callers, migration path, updated tests, and the
reason the break is necessary. Backward-compatible adapters are preferred when practical.

Rationale: the project is split into separate layers, and casual breakage destroys that separation.

### 23. Config Schema Validation Rule

Runtime, experiment, smoke, training, and validation configs MUST be validated before use. Config
validation MUST fail fast on missing required fields, unknown unsupported fields, invalid value
types, invalid ranges, and incompatible option combinations. Config schemas MUST be versioned or
otherwise traceable. Any new config field MUST document its purpose, default behavior, source, and
validation rule.

Rationale: bad configs silently corrupt experiments and make results meaningless.

### 24. Structured Logging and Observability Rule

Runs MUST use structured logging or structured event records where practical. Logs or trace records
MUST include run ID, config ID or path, seed, phase, policy or agent name, key metrics, and failure
reason when applicable. Environment debug traces MUST remain reconstructable at task lifecycle
level. Normal runs may reduce verbosity, but they MUST preserve the link between summary metrics and
run metadata.

Rationale: production-grade research systems need observability, not print-debugging.

### 25. Security and Secret Hygiene Rule

Secrets, tokens, credentials, private keys, API keys, and personal access tokens MUST not be
committed. Config files MUST not contain secrets. Runtime scripts MUST not download or execute
remote code unless explicitly approved. External tools, datasets, and references MUST be documented
before use. Dependency additions MUST consider supply-chain risk as well as reproducibility.

Rationale: even research code can leak credentials or execute unsafe external code if unchecked.

### 26. Packaging and Execution Rule

The project MUST define a clear execution model with CLI entry points, scripts, or documented
module commands, the expected working directory, required config inputs, and output location rules.
If the project becomes installable, packaging metadata MUST be declared in a tracked file such as
`pyproject.toml`. Ad-hoc scripts MUST not become the only way to run important workflows. All
official commands MUST respect the approved virtual environment and dependency rules.

Rationale: a production-grade project must be runnable by someone other than the original author.

### 27. Artifact Lifecycle Rule

Generated artifacts MUST have a defined location, naming convention, and metadata. Artifacts
include raw metrics, plots, reports, checkpoints, debug traces, and validation summaries. Result
artifacts MUST reference config, seed, commit or version, timestamp or run ID, and producing
command. Generated outputs MUST not be committed unless explicitly classified as approved reference
artifacts. Frozen artifacts used for claims MUST not be overwritten in place.

Rationale: unmanaged artifacts make results impossible to audit.

### 28. Performance Budget Rule

Test and experiment stages MUST have explicit runtime expectations when practical. Heavy workloads
MUST be separated from smoke tests. Smoke tests MUST remain fast enough for frequent execution.
Environment changes MUST consider algorithmic complexity and memory growth. Any intentionally
expensive run MUST be documented before execution.

Rationale: slow feedback loops cause broken code to survive longer and waste compute.

### 29. Review and Merge Gate Rule

No major change should be merged without a review checklist. Review MUST check constitution
compliance, scope control, tests, config and schema impact, paper-to-code mapping impact,
reproducibility impact, and baseline fairness impact when relevant. Any known deviation MUST be
documented before merge. "Works on my machine" is not an acceptable merge argument.

Rationale: governance must be enforced at review time, not only after failures.

### 30. Definition of Done Rule

A feature or phase is done only when implementation matches the approved spec and plan, tests pass,
assumptions are documented, configs are validated or updated, paper-to-code mapping is updated when
relevant, metrics are produced by shared evaluation code when relevant, artifacts are stored
according to artifact lifecycle rules when relevant, no dependency or environment changes occurred
without approval, deviations and limitations are documented, and the final summary lists files
changed, commands run, tests run, and unresolved risks.

Rationale: a production-grade workflow needs a hard finish line.

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
