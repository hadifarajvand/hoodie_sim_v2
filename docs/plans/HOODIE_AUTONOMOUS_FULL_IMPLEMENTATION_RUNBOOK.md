# HOODIE-Only Autonomous Full Implementation Runbook

## 0. Document control

| Field | Value |
|---|---|
| Repository | `hadifarajvand/hoodie_sim_v2` |
| Main branch | `main` — must remain unchanged during implementation |
| Previous plan branch | `hoodie-redesign/integration` |
| Autonomous base branch | `hoodie-redesign/full-implementation` |
| Previous plan | `docs/plans/HOODIE_MODULAR_REDESIGN_IMPLEMENTATION_PLAN.md` |
| Canonical runbook | `docs/plans/HOODIE_AUTONOMOUS_FULL_IMPLEMENTATION_RUNBOOK.md` |
| Baseline code commit inspected | `3464844b3769fa1275e101165bf19de2cfb0ac3e` |
| Previous plan commit | `837b6454be62ad6668bd2d734b15f3a5c34a9152` |
| Scope | Original HOODIE article only; ECHO and every ECHO-derived active mechanism are excluded |
| Final outputs | Figures 8–11, all 14 panels, four composites, raw datasets, checkpoints, manifests, and reproducibility bundle |
| Execution mode | One autonomous end-to-end implementation run; internal gates, no phase-by-phase user handoffs |

This runbook supersedes the previous plan only where that plan required stopping after each phase. The detailed scientific and architectural requirements in the previous plan remain binding unless this runbook explicitly overrides them.

---

## 1. Binding execution decision

Implement the complete HOODIE simulator now. Execute the numbered work stages continuously and repair failed gates automatically. Do not return a Phase 0 report and do not ask for approval between stages.

The prior output is not a blocker:

- the old local phase branch points at another local commit;
- the worktree is detached at `837b6454be62ad6668bd2d734b15f3a5c34a9152`;
- Phase 0 evidence exists as uncommitted files;
- `python -m pytest -q` failed collection under Python 3.14.3;
- no implementation commit was made.

Avoid all of those conflicts by creating a new Git worktree and unique work branch from `origin/hoodie-redesign/full-implementation`. Never clean, reset, stash, delete, or switch the user's existing worktree.

Stop only for a genuine hard blocker:

1. continuing would overwrite unrelated user work or credentials;
2. GitHub write permission is unavailable;
3. the original paper and every repository source leave a method-defining field unresolved and no scientifically honest bounded assumption is possible;
4. a required paper resource is absent and cannot be reconstructed or explicitly represented as an assumption;
5. the full campaign cannot fit available memory or storage even after resumable execution and safe parallelism reduction.

Ordinary test failures, missing code, environment incompatibilities, stale branches, and broken legacy modules are implementation work.

---

## 2. Final definition of done

A clean checkout of the resulting branch must support:

```bash
hoodie verify-source --contracts resources/papers/hoodie/contracts
hoodie verify-kernel --config configs/hoodie/paper/default.toml
hoodie train --config configs/hoodie/paper/train_default.toml
hoodie evaluate --config configs/hoodie/paper/evaluate_default.toml
hoodie campaign --plan configs/hoodie/figures/figures_08_11.toml
hoodie render --campaign artifacts/hoodie/campaigns/<campaign_id>
hoodie verify-artifacts --campaign artifacts/hoodie/campaigns/<campaign_id>
```

Completion requires:

- a modular `src/hoodie/` implementation;
- no ECHO behavior in active HOODIE source, tests, configs, scripts, CLI, or onboarding;
- original-HOODIE source contracts with evidence and hashes;
- operational LSTM and no-LSTM paths;
- Dueling Double DQN with tensor-safe checkpoints and deterministic resume;
- distributed HOODIE learner ownership as established by the paper contract;
- FLC, RO, HO, VO, BCO, and MLEO baselines on the same kernel;
- immutable paired traces and fair evaluation;
- datasets and exports for 8a–8b, 9a–9e, 10a–10f, and Figure 11;
- four composite figures;
- SVG, PDF, and deterministic 300-dpi PNG outputs;
- raw task, decision, transition, episode, training, evaluation, and aggregation records;
- source, config, trace, checkpoint, dataset, environment, and code hashes;
- a fresh-clone verification report.

“Exact figures” means source-locked experiments, axes, labels, series, ordering, aggregation, and deterministic rendering from fresh simulation data. It does not permit hard-coded curves, manual curve shaping, target leakage, or digitized paper values used as simulation results.

---

## 3. Scientific authority

Apply this order:

1. `resources/papers/hoodie/original/HOODIE_paper.pdf`
2. OCR under `resources/papers/hoodie/ocr/`, checked against the PDF
3. `resources/papers/hoodie/recovered/paper-parameter-registry.json`
4. `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
5. new typed contracts under `resources/papers/hoodie/contracts/`
6. this runbook and the previous detailed modular plan
7. new tests and code
8. legacy code and reports only as non-authoritative implementation evidence

Each required contract field must record:

- value;
- unit;
- status: `paper_explicit`, `paper_derived`, `approved_assumption`, or `implementation_choice`;
- source file;
- page;
- equation, algorithm, table, or figure;
- derivation or notes;
- uncertainty when relevant.

Resolve before method-defining implementation:

- state dimension, ordering, normalization, and causal history;
- action count, indexing, local/horizontal/cloud semantics, and legality;
- reward formula, sign, delayed timing, and drop penalty;
- argmax versus argmin behavior;
- LSTM input, target, reset, training, and ablation semantics;
- DDQN architecture, loss, replay, optimizer, epsilon, and target update units;
- learner ownership and parameter sharing;
- slot chronology, queue service, transmission, timeout, completion, and drop rules;
- all Figure 8–11 experiment grids, seeds, episodes, checkpoint reuse/retraining rules, aggregation, uncertainty, and layouts.

Digitized paper curves may be stored only as validation targets with provenance and uncertainty.

---

## 4. Architecture

Create:

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

Dependency direction:

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
reporting, reproducibility, verification
```

The physical kernel must not import learning, baselines, experiments, plotting, ECHO, or legacy adapters.

Core types:

- `TaskSpec`: immutable exogenous task fields;
- `TaskRuntime`: mutable lifecycle state;
- `TaskLocation`: exactly one location at a time;
- `TaskOutcome`: pending, completed, dropped;
- `Action`: local, horizontal(destination), vertical/cloud;
- `DecisionRecord`: observation hash, legal mask, action, policy, agent, slot;
- typed IDs for episode, task, agent, trace, and checkpoint.

Kernel responsibilities:

- deterministic reset and slot step;
- physical action validation;
- queue ownership and transitions;
- local, horizontal, and vertical service;
- timeout, completion, and drop accounting;
- event and task records;
- no learning, reward optimization, plotting, or experiment concerns.

---

## 5. Current-to-target migration map

| Current path | Required action | New target |
|---|---|---|
| `src/environment/task.py` | mine fields and lifecycle; replace | `src/hoodie/domain/task.py` |
| `src/environment/topology.py` | preserve verified data; rewrite API | `src/hoodie/topology/` |
| `src/environment/private_queue.py` | mine FIFO/service invariants; rewrite | `src/hoodie/queues/private.py` |
| `src/environment/public_queue.py` | mine ownership/service invariants; rewrite | `src/hoodie/queues/destination.py` |
| `src/environment/offloading_queue.py` | preserve original-HOODIE transfer only; remove ERT | `src/hoodie/queues/outbound.py` |
| `src/environment/compute_config.py` | normalize units and migrate | `src/hoodie/physical/capacity.py` |
| `src/environment/paper_link_delay.py` | migrate source-locked formula | `src/hoodie/physical/transmission.py` |
| `src/environment/paper_timeout.py` | migrate original timeout only | `src/hoodie/physical/timeout.py` |
| `src/environment/slot_engine.py` | mine mechanics; replace | `physical/computation.py`, `simulation/kernel.py` |
| `src/environment/gym_adapter.py` | retire; never import from new package | split neutral modules |
| `src/environment/paper_state.py` | mine formulas; replace placeholders | `src/hoodie/observation/paper_state.py` |
| `src/agents/paper_state_builder.py` | consolidate | `src/hoodie/observation/builder.py` |
| `src/environment/paper_action_space.py` | source-lock and rewrite | `domain/action.py`, `policies/action_space.py` |
| `src/policies/action_masking.py` | migrate physical legality only | `src/hoodie/policies/masking.py` |
| `src/agents/hoodie_agent.py` | retire after interface mining | `src/hoodie/learning/agent.py` |
| `src/agents/hoodie_model.py` | replace; do not patch | `network.py`, `learner.py`, `checkpoint.py` |
| `src/agents/multi_agent_hoodie_pool.py` | mine ownership idea; rewrite | `src/hoodie/learning/distributed.py` |
| `src/training/training_loop.py` | retire mixed chronology | `src/hoodie/training/` |
| `src/analysis/full_training_reproduction_campaign/` | mine verified mechanics; decompose | learning, training, experiments |
| `src/analysis/paper_hoodie_network_implementation/` | migrate only verified architecture | learning/network, forecasting/lstm |
| `src/evaluation/` | mine formulas; replace with typed records | `src/hoodie/evaluation/` |
| six baseline policy files | migrate to one policy port | `src/hoodie/baselines/` |
| `src/run_pipeline.py` | retire | CLI and experiment runner |
| current figure scripts | source-lock grids, then retire | experiments/figures and reporting |
| ECHO source, tests, configs, docs, control | preserve history, remove active surface | no active target |
| old figure smoke artifacts | never reuse as final evidence | new content-addressed campaign root |

Mandatory defect removal:

- no competing target networks;
- no load-before-network-construction checkpoint bug;
- no JSON serialization of tensor state dictionaries;
- no hard-coded gamma;
- no heuristic hints or compatibility biases added to Q-values;
- no single global policy where the paper requires distributed learners;
- no mixed action vocabulary;
- no monolithic environment adapter;
- no second handwritten configuration system;
- no unverified figure panel mapping;
- no smoke artifact presented as reproduction.

---

## 6. ECHO removal contract

Preserve the baseline commit and create a removal manifest. Then remove from the active redesign line:

- ECHO source imports and conditionals;
- ERT calculations and queue ordering;
- deadline-feasibility masks introduced by ECHO;
- ECHO reward, lateness, risk, and completion-estimate fields;
- event-SMDP transition accumulation;
- ECHO tests and fixtures;
- ECHO configs and scripts;
- ECHO control, reconciliation, validators, gates, and active authority files;
- active ECHO onboarding and architecture documentation;
- ECHO checkpoints and smoke artifacts from active commands.

Archived historical material may retain ECHO text. Active paths must pass:

```bash
rg -n -i '\becho\b|effective remaining time|\bert\b|event.?smdp|deadline[_ -]?mask|predicted[_ -]?risk' \
  src/hoodie tests/hoodie configs/hoodie scripts/hoodie README.md docs/ARCHITECTURE.md docs/REPRODUCING.md
```

Do not delete original paper resources or Git history. Do not remove legacy HOODIE until the replacement passes parity and final gates.

---

## 7. Autonomous implementation stages

The stages are sequential internal gates. The agent continues automatically after repairing each gate.

### Stage 0 — Clean worktree, baseline, and inventory

- fetch `origin/hoodie-redesign/full-implementation`;
- create a new Git worktree and unique branch;
- record source commit, environment, worktree, and hashes;
- preserve the previous Python 3.14 collection failure as historical evidence;
- generate automated inventories for source, tests, ECHO, configs, scripts, papers, checkpoints, artifacts, and large files;
- create the continuous run manifest and progress graph.

Gate: original worktree untouched; clean new worktree; baseline recoverable; no source behavior changed.

### Stage 1 — Paper source contracts

- read PDF and OCR together;
- create typed contracts for parameters, state, actions, topology, chronology, reward, LSTM, DDQN, baselines, metrics, and figures;
- create a 14-panel registry;
- add `hoodie verify-source` and contract tests;
- record explicit assumptions and digitized targets separately.

Gate: all method-defining and Figure 8–11 fields resolved or explicitly bounded; contract hash frozen.

### Stage 2 — Remove ECHO active surface

- apply Section 6;
- archive/remove ECHO tests, configs, scripts, control, and active docs;
- rewrite shared modules that contain ECHO behavior;
- update onboarding to HOODIE-only scope.

Gate: active ECHO scan is zero; repository imports; original-HOODIE evidence remains available.

### Stage 3 — Package and environment bootstrap

- create one `pyproject.toml` and lock strategy;
- choose a supported isolated Python interpreter, preferring 3.12 when available;
- create `src/hoodie/` and CLI skeleton;
- add formatting, lint, typing, and dependency-direction checks;
- make supported test collection work.

Gate: editable install works; CLI help works; collection succeeds; dependency rules pass.

### Stage 4 — Domain and units

- implement typed IDs, task specification, runtime lifecycle, action vocabulary, outcomes, time, and units;
- enforce one location and one outcome per task.

Gate: lifecycle and unit property tests pass; no legacy imports.

### Stage 5 — Topology, action indexing, and legality

- implement graph, registry loader, topology validation, action mapping, and masks;
- verify Figure 7 topology and any source-locked scalable topology rule.

Gate: topology hashes/edges pass; action mapping is bijective; every state has a legal action.

### Stage 6 — Queues and physical services

- implement FIFO private, outbound, destination, and cloud queues;
- implement capacity, computation, horizontal and vertical transmission, service, timeout, completion, and drop;
- add hand-calculated boundary fixtures.

Gate: local, horizontal, vertical, queue, and timeout fixtures pass.

### Stage 7 — Neutral deterministic slot kernel

- freeze source-backed slot-boundary order;
- implement reset, step, state, instrumentation, lifecycle records, and invariants;
- keep kernel independent of learning and plots.

Gate: deterministic reference episodes pass; forbidden-import scan passes.

### Stage 8 — Immutable workloads and common random numbers

- implement source-backed arrivals and task distributions;
- implement immutable trace schema, generator, store, hashing, and seed lineage;
- prevent policies from mutating exogenous work.

Gate: same seed produces byte-identical traces; paired policies receive identical tasks.

### Stage 9 — Observation and LSTM forecasting

- implement ordered non-placeholder state features;
- implement causal load history;
- implement LSTM training/inference and clean no-LSTM bypass;
- verify exact source-locked state dimensions.

Gate: state golden vectors pass; history is causal and non-placeholder; ablation changes only LSTM behavior.

### Stage 10 — Dueling Double DQN learner

- implement online/target networks, dueling combination, masked epsilon-greedy selection, replay, DDQN target, optimizer, epsilon schedule, target updates, metrics, and tensor-safe checkpoints;
- eliminate hard-coded gamma and Q-value hints.

Gate: shape, target, optimization, masking, replay, target-update, and checkpoint round-trip tests pass.

### Stage 11 — Delayed reward and distributed training

- implement source-backed delayed reward and transition construction;
- implement per-agent learner, optimizer, replay, and checkpoint ownership unless the contract proves sharing;
- implement episode coordinator, evaluation mode, resume, and aggregation.

Gate: deterministic multi-agent training smoke passes; ownership and reward timing tests pass.

### Stage 12 — Six baselines

- implement FLC, RO, HO, VO, BCO, and MLEO through the common policy interface;
- forbid baseline bypasses of kernel mechanics.

Gate: one policy contract suite passes for all six.

### Stage 13 — Paired evaluation and fairness

- implement task-level records and source-locked metrics;
- implement paired traces, aggregation, confidence intervals, checkpoint evaluation, and fairness validation.

Gate: equal task counts and trace hashes across compared policies; metric fixtures pass.

### Stage 14 — Reproducibility and deployment

- implement RNG capture/restore, hashes, manifests, deterministic flags, CLI commands, scripts, container, and CI smoke workflow;
- support CUDA, MPS, and CPU with metadata.

Gate: fresh checkout runs verification, kernel smoke, tiny training, resume, paired evaluation, and synthetic render.

### Stage 15 — Resumable Figure 8–11 experiment DAG

- implement typed semantic job specs;
- content-address job IDs and outputs;
- implement quick, pilot, and full profiles;
- implement dry run, atomic completion, resume, checkpoint reuse, trace reuse, aggregation, panel registry, and rendering nodes;
- report compute, memory, disk, backend, parallelism, and resume strategy.

Gate: dry run validates every job and dependency; pilot covers the entire parameter graph.

### Stage 16 — Full Figure 8 campaign

- run all source-locked learning-rate and discount-factor variants across required seeds;
- store true distributed training rewards and raw logs;
- freeze datasets before plotting.

Gate: complete 8a and 8b series and x-grids; every point has raw training evidence.

### Stage 17 — Full Figure 9 campaign

- run source-locked validation sweeps for arrival probability, action distribution, CPU capacity, agent count/traffic, and data-rate scenarios;
- use correct checkpoint reuse or retraining rules and paired traces.

Gate: 9a–9e datasets pass registry, fairness, provenance, and raw-support checks.

### Stage 18 — Full Figure 10 campaign

- evaluate HOODIE and all six baselines across source-locked arrival, CPU, and timeout dimensions;
- use identical immutable traces and task counts.

Gate: 10a–10f contain all seven policies, expected x-grids, equal exogenous tasks, and raw records.

### Stage 19 — Full Figure 11 LSTM ablation

- run with-LSTM and without-LSTM under identical unrelated settings;
- freeze two-series data and lineage.

Gate: ablation isolation and provenance pass; both series are complete.

### Stage 20 — Deterministic rendering

- render 14 panels and four composites only from frozen verified datasets;
- export SVG, PDF, and 300-dpi PNG;
- produce manifests and hashes;
- rerender and compare hashes.

Gate: all exports exist; labels/order match contracts; deterministic rendering passes.

### Stage 21 — Final closure

- run all supported unit, property, contract, integration, differential, smoke, pilot, and reproduction tests;
- update root onboarding and add `ARCHITECTURE.md`, `REPRODUCING.md`, `SCIENTIFIC_AUTHORITY.md`, and `KNOWN_LIMITATIONS.md`;
- retire unreferenced legacy HOODIE paths after archive preservation;
- rebuild dead-code and dependency reports;
- create the final reproducibility bundle;
- run fresh-clone verification;
- push the final work branch without merging to `main`.

Gate: final status `HOODIE_FIGURES_08_11_VERIFIED`.

---

## 8. Figure contracts

### Figure 8

- 8a: accumulated reward over training episodes for learning-rate variants;
- 8b: accumulated reward over training episodes for discount-factor variants.

Rules: true training logs; source-locked distributed-agent aggregation; independent lineage per parameter/seed unless the paper explicitly specifies continuation; no unrecorded smoothing.

### Figure 9

- 9a: reward versus task-arrival probability and edge-layer density;
- 9b: local/horizontal/vertical action distribution versus task-arrival probability;
- 9c: reward versus CPU capacity and agent count;
- 9d: reward versus number of DRL agents under traffic scenarios;
- 9e: reward versus offloading data-rate scenario and agent count.

Use exploitative validation from source-locked checkpoints when required. Reuse immutable traces across compared series.

### Figure 10

Six panels compare HOODIE with FLC, RO, HO, VO, BCO, and MLEO. Lock exact paper panel order and metrics. Candidate dimensions to verify are delay and drop ratio versus arrival probability, CPU capacity, and timeout. Every policy uses paired traces and identical tasks.

### Figure 11

One panel with HOODIE-with-LSTM and HOODIE-without-LSTM. Lock exact y metric, training/evaluation semantics, checkpoint policy, and aggregation. Disabling LSTM must not change unrelated configuration.

Required paths:

```text
artifacts/hoodie/campaigns/<campaign_id>/figures/panels/figure_8a.{svg,pdf,png}
artifacts/hoodie/campaigns/<campaign_id>/figures/panels/figure_8b.{svg,pdf,png}
artifacts/hoodie/campaigns/<campaign_id>/figures/panels/figure_9a.{svg,pdf,png}
...
artifacts/hoodie/campaigns/<campaign_id>/figures/panels/figure_10f.{svg,pdf,png}
artifacts/hoodie/campaigns/<campaign_id>/figures/panels/figure_11.{svg,pdf,png}
artifacts/hoodie/campaigns/<campaign_id>/figures/composites/figure_8.{svg,pdf,png}
artifacts/hoodie/campaigns/<campaign_id>/figures/composites/figure_9.{svg,pdf,png}
artifacts/hoodie/campaigns/<campaign_id>/figures/composites/figure_10.{svg,pdf,png}
artifacts/hoodie/campaigns/<campaign_id>/figures/composites/figure_11.{svg,pdf,png}
```

---

## 9. Dataset and artifact rules

Every plotted point must be traceable to:

- source contract hash;
- code commit;
- environment lock hash;
- configuration hash;
- semantic job ID;
- seed lineage;
- immutable trace hash;
- checkpoint ID and hash;
- raw task/decision/transition/episode records;
- aggregation code and version;
- frozen panel dataset;
- render manifest.

A campaign node writes to a temporary directory and atomically renames only after verification. A verified content-addressed node must not rerun when inputs are unchanged.

Parallelize only independent jobs with disjoint RNG and artifact namespaces. Reduce parallelism on memory pressure. Quick and pilot outputs are gates, never final figures.

---

## 10. Test requirements

### Unit

Units, deadlines, topology, actions, queues, transmission, computation, reward, observation, LSTM, network shapes, DDQN targets, masks, replay, epsilon, metrics, config, and manifests.

### Property

Work never increases; one task has one location; legal masks are nonempty; same seed gives the same trace; policies cannot mutate traces; serialization round-trips; illegal actions are never selected; action count equals decision count.

### Contract

Paper parameters, state schema, action schema, chronology, reward, learner ownership, trace/log/checkpoint schemas, panel registry, and figure mapping.

### Integration

Local completion; horizontal offload; vertical offload; transmission admission; timeout in every location; public/cloud sharing; delayed reward; distributed episode; checkpoint resume; paired evaluation.

### Differential

Compare deterministic small scenarios with hand calculations, accepted scientifically valid legacy behavior, and an independent reference implementation. Classify every difference.

### Reproduction

Panel completeness; expected series and x-grids; manifest linkage; composite order; frozen-dataset regeneration; deterministic rendering; fresh-clone smoke reproduction.

Do not stop when tests fail. Diagnose, repair, rerun, and continue. Archive/delete tests that exclusively assert removed ECHO behavior; migrate or strengthen original-HOODIE tests.

---

## 11. Environment and acceleration

The previous Python 3.14.3 collection failure is not the target environment.

- inspect local interpreters and dependency constraints;
- prefer a supported Python 3.12 environment when available;
- create a project-local isolated environment;
- use one dependency declaration and lock strategy;
- do not mutate unrelated global environments;
- use CUDA if available, MPS on supported Apple Silicon if available, otherwise CPU;
- record backend, determinism flags, package versions, and hashes.

Accelerate safely:

- reuse verified formulas, fixtures, and stable mechanics from current code;
- do not rewrite proven behavior for style alone;
- use targeted tests during development and full tests at milestones;
- parallelize independent audits and experiment jobs;
- reuse verified traces and checkpoints;
- use resumable jobs and skip content-identical completed work;
- do not substitute pilot results for full results.

---

## 12. Git and continuous-run protocol

From the user's current repository directory:

```bash
git fetch origin --prune
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
WORKTREE="../hoodie_sim_v2_full_${RUN_ID}"
BRANCH="hoodie-redesign/full-implementation-${RUN_ID}"
git worktree add -b "$BRANCH" "$WORKTREE" origin/hoodie-redesign/full-implementation
cd "$WORKTREE"
```

Do not touch the original worktree. Do not reuse the old phase branch.

Maintain:

```text
artifacts/hoodie/implementation_run/
├── run_manifest.json
├── progress.json
├── decisions.jsonl
├── commands.log
├── tests/
├── inventories/
├── hashes/
├── migration/
├── campaign/
└── final_report.md
```

Recommended milestone commits:

- A: source lock, ECHO active removal, package bootstrap;
- B: domain, topology, physical services, kernel, traces;
- C: observation, LSTM, DDQN, distributed training, baselines, evaluation;
- D: reproducibility, deployment, experiment DAG;
- E: full Figure 8–11 campaigns and rendering;
- F: final closure and reproducibility bundle.

Push after every milestone. Never force-push, modify `main`, or automatically merge.

---

## 13. Final report

Return only after the complete run, except for a genuine hard blocker. The final report must contain:

- verdict;
- worktree path;
- local and remote work branch;
- starting commit and final commit;
- milestone commits;
- implemented architecture;
- source-contract decisions and assumptions;
- ECHO removal and zero-reference result;
- environment and backend;
- complete test results;
- campaign job counts and status;
- all 14 panel paths;
- all four composite paths;
- reproducibility bundle path;
- remaining scientifically honest limitations;
- exact fetch and inspection commands.

Do not return a Phase 0 report. Do not request per-stage approval. Do not stop at quick or pilot mode.

## Final rating

**Proceed — full autonomous implementation authorized.**
