# HOODIE-Only Modular Simulation Redesign and Figure-Reproduction Implementation Plan

## 0. Document control

| Field | Value |
|---|---|
| Repository | `hadifarajvand/hoodie_sim_v2` |
| Baseline branch | `main` |
| Redesign integration branch | `hoodie-redesign/integration` |
| Baseline commit inspected | `3464844b3769fa1275e101165bf19de2cfb0ac3e` |
| Canonical path | `docs/plans/HOODIE_MODULAR_REDESIGN_IMPLEMENTATION_PLAN.md` |
| Status | Implementation authority for the HOODIE-only redesign |
| Scope | Original HOODIE simulator only; ECHO and every ECHO-derived mechanism are excluded |
| Deliverable | Reproducible Figures 8, 9, 10, and 11, including all 14 panels |
| Execution policy | One phase at a time; every phase requires evidence and an exit-gate decision |
| Branch policy | Never implement directly on `main` or directly on `hoodie-redesign/integration` |

## 1. Binding verdict

Do not patch the current mixed implementation into the final simulator. The repository currently combines legacy HOODIE behavior, ECHO behavior, compatibility logic, diagnostics, multiple training paths, and several figure scaffolds. The final system must be built as a new modular `src/hoodie/` package and must migrate only behavior proven to belong to the original HOODIE method.

The redesign strategy is:

1. Freeze and inventory the current state.
2. Lock the original HOODIE paper into machine-readable contracts.
3. Remove ECHO from the active redesign line.
4. Build a neutral physical simulation kernel.
5. Build the HOODIE observation, LSTM, Dueling DDQN, and distributed learner modules on top of that kernel.
6. Implement the six baselines against the same policy interface and the same immutable traces.
7. Build a resumable experiment DAG for Figures 8–11.
8. Export raw datasets before rendering any figure.
9. Retire legacy paths only after parity, reproducibility, and artifact-integrity gates pass.

No ECHO class, ERT rule, deadline-feasibility mask, ECHO reward term, ECHO event-SMDP path, ECHO authority file, or ECHO-specific conditional may remain in the active HOODIE package.

## 2. Definition of done

A clean checkout is complete only when it can run the following without manual code edits:

```bash
hoodie verify-source --contracts resources/papers/hoodie/contracts
hoodie verify-kernel --config configs/hoodie/paper/default.toml
hoodie train --config configs/hoodie/paper/train_default.toml
hoodie evaluate --config configs/hoodie/paper/evaluate_default.toml
hoodie campaign --plan configs/hoodie/figures/figures_08_11.toml
hoodie render --campaign artifacts/hoodie/campaigns/<campaign_id>
hoodie verify-artifacts --campaign artifacts/hoodie/campaigns/<campaign_id>
```

The verified campaign must produce:

- paper-faithful HOODIE checkpoints;
- FLC, RO, HO, VO, BCO, and MLEO baseline results;
- raw task, decision, transition, episode, training, evaluation, and aggregation records;
- datasets for panels 8a–8b, 9a–9e, 10a–10f, and Figure 11;
- individual panel SVG, PDF, and deterministic 300-dpi PNG files;
- composite Figure 8, 9, 10, and 11 files in the same formats;
- source, config, trace, checkpoint, dataset, code, and environment hashes;
- a verification report separating paper-explicit facts, paper-derived values, approved assumptions, and implementation choices.

“Exact figures” means exact experiment definitions, axes, labels, series, aggregation semantics, and reproducible rendering from fresh simulation data. It does not permit hard-coded points, manual curve shaping, target leakage, or using digitized paper values as simulation outputs.

## 3. Scientific authority

Apply this hierarchy:

1. `resources/papers/hoodie/original/HOODIE_paper.pdf`
2. OCR under `resources/papers/hoodie/ocr/`, checked against the PDF
3. `resources/papers/hoodie/recovered/paper-parameter-registry.json`
4. `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
5. Contracts created under `resources/papers/hoodie/contracts/`
6. This plan
7. New HOODIE-only tests and code
8. Legacy code and reports as non-authoritative implementation evidence

A required source-contract field must include value, unit, status, source file, page, table/figure/equation, and notes. Allowed statuses are:

```text
paper_explicit
paper_derived
approved_assumption
unresolved
```

No full campaign may run while a required field is unresolved.

## 4. Scope

### Included

- Original HOODIE cloud–edge model
- Time-slotted arrivals, queuing, transmission, service, completion, timeout, and drop behavior
- Original state and action spaces
- Topology legality masks
- LSTM forecasting used by HOODIE
- Dueling Double DQN
- Independent distributed learners per edge agent unless Phase 1 proves parameter sharing
- Replay, epsilon-greedy exploration, target updates, checkpointing, and deterministic evaluation
- Six paper baselines
- Figure 8–11 training, validation, evaluation, aggregation, and rendering
- CPU-first deterministic execution and optional CUDA execution with determinism metadata
- Containerized scientific execution and CI smoke checks

### Excluded

- ECHO
- Effective Remaining Time and ERT queue ordering
- ECHO candidate completion estimation
- ECHO deadline-feasibility masks
- ECHO normalized lateness, risk, and reward terms
- ECHO event-SMDP accumulation and interval closure
- ADAPTIVE as a HOODIE alias
- Heuristics presented as trained HOODIE
- Thesis extensions, web services, databases, or SaaS deployment
- Figures outside 8–11 in this implementation cycle

## 5. Current implementation correspondence matrix

This table is binding. A legacy component marked “mine and replace” may be read for formulas, invariants, and tests, but the final `src/hoodie/` package must not import it.

| Current path | Current role | Required disposition | Target |
|---|---|---|---|
| `src/environment/task.py` | Mutable task and lifecycle | Mine and replace | `src/hoodie/domain/task.py` |
| `src/environment/topology.py` | Topology and Figure 7 adjacency | Preserve verified data; rewrite API | `src/hoodie/topology/` |
| `src/environment/private_queue.py` | Local/private queue | Mine invariants; rewrite | `src/hoodie/queues/private.py` |
| `src/environment/public_queue.py` | Public destination queue | Mine invariants; rewrite | `src/hoodie/queues/destination.py` |
| `src/environment/offloading_queue.py` | In-flight work | Preserve original-HOODIE behavior only; remove ERT | `src/hoodie/queues/outbound.py` |
| `src/environment/compute_config.py` | Compute parameters | Normalize units and migrate | `src/hoodie/physical/capacity.py` |
| `src/environment/paper_link_delay.py` | Transmission delay | Migrate after source lock | `src/hoodie/physical/transmission.py` |
| `src/environment/paper_timeout.py` | Timeout rule | Migrate original rule only | `src/hoodie/physical/timeout.py` |
| `src/environment/slot_engine.py` | Slot compute mechanics | Mine and replace | `src/hoodie/physical/computation.py` and `simulation/kernel.py` |
| `src/environment/gym_adapter.py` | Monolithic mixed environment with ECHO hooks | Retire; never import from new package | Split across neutral modules |
| `src/environment/paper_state.py` | Candidate paper state with placeholders | Mine formulas; replace placeholders | `src/hoodie/observation/paper_state.py` |
| `src/agents/paper_state_builder.py` | State assembly | Consolidate | `src/hoodie/observation/builder.py` |
| `src/environment/paper_action_space.py` | Candidate indexed actions | Source-lock then rewrite | `src/hoodie/domain/action.py` and `policies/action_space.py` |
| `src/policies/action_masking.py` | Physical legality mask | Migrate without aliases | `src/hoodie/policies/masking.py` |
| `src/agents/hoodie_agent.py` | Legacy wrapper | Retire after extracting interface behavior | `src/hoodie/learning/agent.py` |
| `src/agents/hoodie_model.py` | Mixed network, hints, biases, learning, serialization | Retire; do not patch into final design | `learning/network.py`, `learner.py`, `checkpoint.py` |
| `src/agents/multi_agent_hoodie_pool.py` | Candidate per-agent ownership | Mine concept; rewrite | `src/hoodie/learning/distributed.py` |
| `src/training/training_loop.py` | Mixed HOODIE and ECHO training chronology | Retire | `src/hoodie/training/` |
| `src/analysis/full_training_reproduction_campaign/` | Candidate DDQN campaign | Mine verified mechanics; decompose | `learning/`, `training/`, `experiments/` |
| `src/analysis/paper_hoodie_network_implementation/` | Candidate LSTM dueling network | Migrate only source-verified layers | `learning/network.py`, `forecasting/lstm.py` |
| `src/evaluation/` | Metrics, traces, runners | Mine and replace with typed records | `src/hoodie/evaluation/` |
| `src/policies/{flc,ro,ho,vo,bco,mleo}.py` | Six baselines | Migrate to common policy port | `src/hoodie/baselines/` |
| `src/run_pipeline.py` | Legacy orchestration and one main agent | Retire | `src/hoodie/cli/` and `experiments/runner.py` |
| `src/analysis/paper_figures_campaign.py` | Coupled sweep script | Retire after source-locking grids | `src/hoodie/experiments/figures/` |
| `src/analysis/paper_figure_reproduction.py` | Loose aggregation and plotting | Retire | `src/hoodie/reporting/` |
| `src/analysis/figure_generator.py` | Legacy plotting | Mine labels/layout only after source lock | `src/hoodie/reporting/rendering.py` |
| ECHO source, tests, configs, docs, control, and artifacts | Extension method | Preserve in history/archive; remove from active redesign line | No active target |
| Existing figure smoke artifacts | Scaffolds, not final evidence | Never reuse as final output | `artifacts/hoodie/campaigns/<id>/` |

### Binding conclusions

1. Do not repair `gym_adapter.py` in place.
2. Do not repair `hoodie_model.py` in place.
3. Do not reuse ECHO-aware training chronology.
4. Do not treat current figure scripts or smoke artifacts as scientific authority.
5. Do not merge to `main` until Phase 21 is verified and explicitly authorized.

## 6. Target package architecture

```text
src/hoodie/
├── cli/
├── config/
├── domain/
├── topology/
├── workload/
├── queues/
├── physical/
├── simulation/
├── observation/
├── forecasting/
├── policies/
├── learning/
├── training/
├── baselines/
├── evaluation/
├── experiments/
│   └── figures/
├── reporting/
├── reproducibility/
└── verification/
```

External layout:

```text
configs/hoodie/
resources/papers/hoodie/contracts/
resources/papers/hoodie/targets/
scripts/hoodie/
tests/hoodie/
artifacts/hoodie/
docs/plans/
```

### Dependency direction

```text
domain
  ↓
topology, workload, queues, physical
  ↓
simulation
  ↓
observation and policy ports
  ↓
forecasting, learning, baselines
  ↓
training and evaluation
  ↓
experiments
  ↓
reporting and verification
```

The physical kernel must not import learning, baselines, experiments, plotting, ECHO, or legacy adapters.

## 7. Core contracts

### Domain

Use explicit types for:

- `TaskSpec`: immutable exogenous fields
- `TaskRuntime`: mutable lifecycle fields
- `TaskLocation`: exactly one location at a time
- `TaskOutcome`: pending, completed, dropped
- `Action`: local, horizontal(destination), vertical/cloud
- `DecisionRecord`: observation hash, legal mask, selected action, policy, agent, slot
- `EpisodeId`, `TaskId`, `AgentId`, `TraceId`, `CheckpointId`

### Neutral kernel

The kernel accepts a trace and policy decisions and owns only physical state transitions. It must support:

- deterministic reset
- slot-level stepping
- physical action validation
- task movement and ownership
- transmission and computation service
- timeout and completion resolution
- instrumentation events
- invariant checks after every boundary

Required invariants:

- one task occupies at most one location
- completed/dropped tasks never re-enter service
- work never increases during service
- every accepted action is physically legal
- every generated task has one terminal outcome
- exogenous traces are policy-independent

### Observation

The observation builder must be separate from the kernel and must define an ordered, versioned schema. It must include only source-locked features. Placeholder zeros are forbidden unless the source contract explicitly defines them.

### Forecasting

The LSTM module must be causal. Its training target, lookback window, reset semantics, optimizer ownership, and use in the state must be locked during Phase 1. The no-LSTM ablation must bypass the predictor without changing unrelated mechanics.

### Distributed learners

Unless Phase 1 proves sharing, each edge agent owns:

- online network
- target network
- optimizer
- replay buffer
- epsilon state
- RNG stream
- checkpoint lineage

No global mutable learner object may silently serve all agents.

### Checkpoints

Use tensor-safe serialization such as `torch.save`. JSON stores metadata and hashes only. A checkpoint must round-trip model, target model, optimizer, replay state when required, epsilon, counters, RNG states, config hash, source-contract hash, and code commit.

## 8. Configuration and artifacts

Use one typed configuration system. Do not add another handwritten parser. Configuration must be separated into:

- source-locked paper parameters
- run parameters
- compute parameters
- output parameters

Every run creates:

```text
artifacts/hoodie/campaigns/<campaign_id>/
├── manifest.json
├── configs/
├── traces/
├── checkpoints/
├── raw/
│   ├── tasks.parquet
│   ├── decisions.parquet
│   ├── transitions.parquet
│   └── episodes.parquet
├── aggregates/
├── panels/
│   ├── datasets/
│   └── figures/
├── composites/
├── logs/
└── verification/
```

Every panel dataset must contain at least:

```text
figure_id
subfigure_id
series_id
x_value
y_value
x_unit
y_unit
seed
scenario_id
policy_id
trace_id
checkpoint_id
config_hash
source_contract_hash
code_commit
aggregation_method
sample_count
confidence_interval
```

Rendering reads frozen panel datasets only. It must never train, evaluate, or mutate datasets.

## 9. ECHO removal specification

### Preservation

Before removal:

1. require a clean worktree;
2. record the baseline commit;
3. create an annotated preservation tag locally;
4. create `archive/echo-and-legacy-before-hoodie-redesign` locally;
5. write `artifacts/archive/echo-removal-manifest.json` with paths, hashes, reason, baseline commit, and plan hash;
6. never force-update a ref;
7. push archive references only when explicitly authorized.

### Remove or rewrite from the active redesign line

- ECHO source modules and imports
- ERT and ECHO queue-ordering code
- ECHO action masks and reward fields
- ECHO event-SMDP code
- ECHO tests and fixtures
- ECHO configs and run scripts
- ECHO control, validators, reconciliation, gates, and authority snapshots
- `research/ECHO*`, `docs/echo/`, `resources/ECHO*`
- ECHO checkpoints, smoke artifacts, and figure plans

The active scan must pass:

```bash
rg -n -i '\becho\b|effective remaining time|\bert\b|event.?smdp|deadline[_ -]?mask|predicted[_ -]?risk' \
  src/hoodie tests/hoodie configs/hoodie scripts/hoodie README.md docs/ARCHITECTURE.md docs/REPRODUCING.md
```

Archived material and the removal manifest may retain ECHO terminology. Active HOODIE execution paths may not.

## 10. Figure contracts

Phase 1 must freeze for every panel: caption, x-grid, y metric, sign convention, series, ordering, training/evaluation mode, checkpoint reuse rule, episode count, seed count, trace policy, aggregation, uncertainty, and panel layout.

### Figure 8

- 8a: accumulated reward over training episodes for learning-rate variants
- 8b: accumulated reward over training episodes for discount-factor variants

Rules:

- true training logs only;
- aggregate across the distributed HOODIE agents exactly as defined by the paper;
- one independent run lineage per parameter/seed unless the paper explicitly defines continuation;
- no smoothing unless source-locked and recorded.

### Figure 9

- 9a: reward versus task-arrival probability and edge-layer density
- 9b: local/horizontal/vertical action distribution versus task-arrival probability
- 9c: reward versus CPU capacity and agent count
- 9d: reward versus number of DRL agents under traffic scenarios
- 9e: reward versus offloading data-rate scenario and agent count

Use exploitative validation from source-locked checkpoints when the paper requires it. All panels must reuse immutable traces across compared series.

### Figure 10

Six panels compare HOODIE with FLC, RO, HO, VO, BCO, and MLEO. Phase 1 must lock the exact panel order and metrics. The current repository’s panel mapping is not authority. Each comparison must use paired traces and identical exogenous tasks.

Expected candidate dimensions to verify against the paper:

- delay and drop ratio versus arrival probability;
- delay and drop ratio versus CPU capacity;
- delay and drop ratio versus task timeout.

### Figure 11

One panel with both HOODIE-with-LSTM and HOODIE-without-LSTM series. Phase 1 must lock the exact y metric, training/evaluation semantics, checkpoint policy, and aggregation. Disabling LSTM must not alter any unrelated configuration.

### Outputs

```text
panels/figure_8a.svg|pdf|png
panels/figure_8b.svg|pdf|png
panels/figure_9a.svg|pdf|png
...
panels/figure_10f.svg|pdf|png
panels/figure_11.svg|pdf|png
composites/figure_8.svg|pdf|png
composites/figure_9.svg|pdf|png
composites/figure_10.svg|pdf|png
composites/figure_11.svg|pdf|png
```

## 11. Implementation phases

## Phase 0 — Freeze and inventory

Goal: preserve the baseline and establish disciplined execution.

Operations:

1. Fetch `origin/hoodie-redesign/integration`.
2. Create `hoodie-redesign/phase-00-freeze-inventory` from it.
3. Record branch, commit, worktree, OS, Python, pip, NumPy, PyTorch, CUDA, and dependency state.
4. Run `python -m pytest -q`; retain raw stdout, stderr, and exit code. Do not repair failures in Phase 0.
5. Inventory first-party source, ECHO paths, HOODIE candidates, tests, configs, resources, artifacts, and vendored code.
6. Hash the canonical plan.
7. Create `docs/HOODIE_REDESIGN_STATUS.md`.
8. Create the removal manifest and baseline evidence directory.

Allowed writes:

```text
docs/HOODIE_REDESIGN_STATUS.md
artifacts/archive/echo-removal-manifest.json
artifacts/baseline/hoodie-redesign-baseline/*
artifacts/hoodie/phase_evidence/phase_00/*
```

Exit gate: no source modified; baseline recoverable; test and inventory evidence retained; status `PHASE_0_VERIFIED`.

## Phase 1 — Lock the original HOODIE contract

1. Read PDF and OCR side by side.
2. Resolve arrival terminology, action count/indexing, state dimension, learner ownership, reward sign, argmax/argmin, target update units, LSTM target/reset, Figure 10 order, Figure 11 semantics, and topology behavior for non-20-node sweeps.
3. Create typed contracts under `resources/papers/hoodie/contracts/`.
4. Create a 14-panel registry.
5. Add `hoodie verify-source` and contract tests.
6. Store digitized paper curves only under `resources/papers/hoodie/targets/` as validation references with uncertainty.

Exit gate: all Figure 8–11 fields resolved; source-contract hash frozen; verification passes.

## Phase 2 — Remove ECHO from the active redesign line

1. Apply Section 9 inventory.
2. Remove ECHO imports and conditionals.
3. Remove ECHO tests, configs, scripts, control, and active docs.
4. Rewrite shared modules that still contain ECHO behavior.
5. Update onboarding to HOODIE-only scope.
6. Do not delete legacy HOODIE yet.

Exit gate: active ECHO scan returns zero; repository imports; remaining neutral/HOODIE tests do not depend on ECHO.

## Phase 3 — Bootstrap package and tooling

1. Add `pyproject.toml` and one dependency lock strategy.
2. Add `src/hoodie/` package skeleton.
3. Add `hoodie` CLI skeleton.
4. Add architecture dependency tests.
5. Add formatting, lint, typing, and test commands without upgrading scientific dependencies during migration.

Exit gate: package installs; CLI help works; dependency-direction tests pass.

## Phase 4 — Domain and units

Implement immutable identifiers, task specification, runtime lifecycle, action vocabulary, outcomes, time, and unit conversions.

Exit gate: lifecycle and unit property tests pass; no legacy imports.

## Phase 5 — Topology and legality

Implement graph, registry loader, validation, action indexing, and legality masks.

Exit gate: Figure 7 topology hash/edge parity passes; every topology fixture has at least one legal action.

## Phase 6 — Queues and physical services

Implement FIFO queue primitives, private/outbound/destination queues, capacity, computation, transmission, and timeout.

Exit gate: hand-calculated local, horizontal, vertical, and deadline boundary fixtures pass.

## Phase 7 — Neutral slot kernel

Freeze a source-backed slot-boundary order. The candidate order must be verified in Phase 1 before implementation. Implement reset, step, state, instrumentation, and invariants.

Exit gate: deterministic reference episodes pass; kernel imports no learning, baseline, analysis, plotting, ECHO, or legacy adapter code.

## Phase 8 — Workload traces and common random numbers

Implement arrival process, task distribution, immutable trace schema, trace factory/store, seed lineage, and trace hashing.

Exit gate: same seed reproduces byte-identical traces; policies cannot alter exogenous traces.

## Phase 9 — Observation and forecasting

Implement ordered observation schema, task/queue/load features, causal history, LSTM training and inference, and no-LSTM bypass.

Exit gate: exact source-locked dimension/order passes; history is non-placeholder; causality tests pass.

## Phase 10 — HOODIE learner

Implement dueling network, online/target pair, masked epsilon-greedy selector, DDQN target, optimizer step, replay, epsilon schedule, and tensor-safe checkpoints.

Exit gate: no hard-coded gamma; no hints/biases mixed with Q-values; target-update and checkpoint round-trip tests pass.

## Phase 11 — Delayed reward and distributed training

Implement source-backed delayed reward, transition construction, per-agent ownership, episode coordinator, evaluation mode, and resume behavior.

Exit gate: each EA has independent ownership unless contract says otherwise; one deterministic multi-agent training smoke passes.

## Phase 12 — Baselines

Implement FLC, RO, HO, VO, BCO, and MLEO on the same policy port and kernel.

Exit gate: one policy-contract suite passes for all six; no baseline bypasses kernel mechanics.

## Phase 13 — Evaluation and fairness

Implement task records, metrics, paired traces, aggregation, confidence intervals, checkpoint evaluation, and fairness validation.

Exit gate: task counts and exogenous traces match across compared policies; metric fixtures pass.

## Phase 14 — Reproducibility and deployment

Implement RNG capture/restore, config/source/code hashes, environment manifest, deterministic flags, CLI commands, scripts, container, and CI smoke workflow.

Exit gate: fresh checkout runs source verification, kernel smoke, tiny training, checkpoint resume, paired evaluation, and synthetic render.

## Phase 15 — Figure experiment DAG

Implement typed job specs, semantic job IDs, dry-run planning, resumable execution, atomic output directories, aggregation nodes, panel registry, and rendering nodes.

Profiles:

- quick: tiny CI/smoke only;
- pilot: verifies full parameter graph at bounded scale;
- full: source-locked publication campaign.

Exit gate: dry run reports training jobs, evaluation jobs, checkpoints, traces, seeds, estimated compute, RAM/VRAM, disk, parallelism, and resume strategy.

## Phase 16 — Execute Figure 8

Train all source-locked learning-rate and discount-factor variants across required seeds. Freeze logs and datasets. Render only after dataset verification.

Exit gate: 8a and 8b datasets contain expected series/x-grid and traceable raw training evidence.

## Phase 17 — Execute Figure 9

Run source-locked validation sweeps for 9a–9e using proper checkpoint reuse/retraining rules and paired traces.

Exit gate: all five datasets pass registry, fairness, and provenance checks.

## Phase 18 — Execute Figure 10

Evaluate HOODIE and six baselines across all source-locked dimensions using paired immutable traces.

Exit gate: all six panel datasets contain all seven policies, expected x-grid, equal task counts, and raw support.

## Phase 19 — Execute Figure 11

Run the source-locked LSTM ablation with all unrelated settings held constant.

Exit gate: the two-series dataset has complete raw lineage and passes ablation-isolation checks.

## Phase 20 — Render figures

Render 14 panels and four composites from frozen datasets only. Export SVG, PDF, and deterministic 300-dpi PNG. Produce per-panel and composite manifests.

Exit gate: all files exist, hashes verify, panel order/labels match contracts, and rerendering is deterministic.

## Phase 21 — Final closure

1. Run all unit, property, contract, integration, differential, smoke, pilot, and reproduction tests.
2. Replace root onboarding with HOODIE-only instructions.
3. Add `docs/ARCHITECTURE.md`, `REPRODUCING.md`, `SCIENTIFIC_AUTHORITY.md`, and `KNOWN_LIMITATIONS.md`.
4. Remove unreferenced legacy HOODIE paths after archive preservation.
5. Rebuild dependency/dead-code reports.
6. Produce the final reproducibility bundle.
7. Tag the verified release.
8. Merge to `main` only with explicit authorization after the gate passes.

Exit gate: final status `HOODIE_FIGURES_08_11_VERIFIED`.

## 12. Test strategy

### Unit

Units, deadlines, topology, action indexing, queues, transmission, computation, reward, network shapes, DDQN target, masking, replay, epsilon, metrics, and config.

### Property

Work never increases; one task has one location; legal masks are nonempty; same seed gives the same trace; policies cannot alter exogenous traces; serialization round-trips; illegal actions are never selected; action count equals decision count.

### Contract

Paper parameters, state schema, action schema, trace/log/checkpoint schemas, panel registry, and figure mapping.

### Integration

Local completion, horizontal/vertical offload, transmission-boundary admission, timeouts in every location, public/cloud sharing, delayed reward, multi-agent episode, resume, and paired evaluation.

### Differential

Compare small deterministic scenarios with hand calculations, accepted legacy behavior when scientifically valid, and an independent reference implementation. Classify every difference as legacy bug, source-contract correction, intended architectural change, or unresolved failure.

### Reproduction

Panel completeness, expected series/x-grid, manifest linkage, composite order, frozen-dataset regeneration, and deterministic rendering.

## 13. Agent execution protocol

### Before every phase

1. Read this entire plan.
2. Read `docs/HOODIE_REDESIGN_STATUS.md` when it exists.
3. Select only the earliest incomplete phase whose dependencies are verified.
4. Fetch the integration branch.
5. Create the exact phase branch from the latest verified integration commit:

```bash
git fetch origin --prune
git checkout -B hoodie-redesign/phase-<NN>-<slug> origin/hoodie-redesign/integration
```

6. Record the starting commit and clean worktree.
7. Write an exact path allowlist before editing.

### During a phase

- edit only allowed paths;
- never commit directly to `main` or `hoodie-redesign/integration`;
- do not begin later phases;
- do not change source contracts outside Phase 1 or an explicitly reopened Phase 1;
- do not put sweep values in Python code;
- do not add compatibility aliases;
- do not suppress tests;
- do not fabricate paper values;
- do not claim convergence from smoke runs;
- do not commit full generated artifacts unless tracking policy requires them.

### Required evidence

```text
artifacts/hoodie/phase_evidence/phase_<NN>/
├── report.md
├── status.json
├── commands.txt
├── test_output.txt
├── changed_files.json
├── hashes.json
└── diff.patch
```

### Review result

An independent review must classify the phase as exactly one of:

```text
PASS
REWORK
PLAN_CHANGE_REQUIRED
```

Merge into `hoodie-redesign/integration` only on PASS. Update the status file only after merge.

### Stop immediately when

- paper evidence is ambiguous;
- a required contract remains unresolved;
- required edits exceed the path allowlist;
- a frozen physical invariant changes;
- paired policies receive different task traces/counts;
- a checkpoint cannot round-trip;
- a figure point lacks raw data;
- ECHO behavior reappears in active code.

## 14. Phase 0 exact baseline commands

The first implementation invocation runs these commands and stores their outputs; it does not repair failures:

```bash
git fetch origin --prune
git status --short --branch
git rev-parse HEAD
python --version
python -m pip --version
python - <<'PY'
import platform
print(platform.platform())
try:
    import numpy as np
    print("numpy", np.__version__)
except Exception as exc:
    print("numpy unavailable", repr(exc))
try:
    import torch
    print("torch", torch.__version__)
    print("cuda_available", torch.cuda.is_available())
except Exception as exc:
    print("torch unavailable", repr(exc))
PY
python -m pytest -q
```

A missing dependency or failed baseline test is evidence, not authorization to modify dependencies or source during Phase 0.

## 15. Final acceptance checklist

### Scientific

- [ ] Original HOODIE contract locked
- [ ] Required assumptions explicit
- [ ] Reward sign and action selection resolved
- [ ] State/action schema verified
- [ ] LSTM causal and operational
- [ ] Distributed ownership verified
- [ ] Six baselines verified
- [ ] Evaluation fairness verified

### Architecture

- [ ] Neutral kernel imports no learning code
- [ ] Dependency direction enforced
- [ ] No monolithic environment adapter
- [ ] One configuration system
- [ ] One target-network implementation
- [ ] One action vocabulary
- [ ] Tensor-safe checkpoints
- [ ] Legacy execution path retired

### ECHO removal

- [ ] Preservation reference/manifest exists
- [ ] Active ECHO source/imports/conditionals removed
- [ ] ERT removed
- [ ] Event-SMDP removed
- [ ] Active docs/configs/scripts/tests/artifacts cleaned
- [ ] Active reference scan returns zero

### Figures

- [ ] Datasets and exports for 8a, 8b
- [ ] Datasets and exports for 9a–9e
- [ ] Datasets and exports for 10a–10f
- [ ] Two-series dataset and exports for Figure 11
- [ ] Four composite figures
- [ ] SVG, PDF, and 300-dpi PNG integrity verified

### Reproducibility

- [ ] Configs, source hashes, environment hashes, immutable traces, checkpoint lineage, raw logs, frozen datasets, aggregation code, and manifests retained
- [ ] Fresh-clone smoke reproduction passes

## 16. First authorized action

The first agent invocation executes Phase 0 only from `hoodie-redesign/phase-00-freeze-inventory`, based on `origin/hoodie-redesign/integration`.

It must not:

- remove ECHO;
- refactor source;
- update dependencies;
- modify scientific behavior;
- run a full campaign;
- start Phase 1.

It must return the phase branch name, starting commit, resulting commit, files changed, commands run, baseline test result, evidence paths, and a PASS/REWORK/PLAN_CHANGE_REQUIRED self-assessment. Independent review is still required before merge.

## Final rating

**Proceed with Caution.**

The repository contains useful components, but the final simulator is credible only when it is rebuilt around explicit source contracts, a neutral kernel, independent modules, immutable traces, tensor-safe learning state, paired evaluation, and a dataset-first figure pipeline.