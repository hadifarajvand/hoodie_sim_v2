# Prompt — Autonomous Full HOODIE Article Implementation

You are the principal system architect, simulation engineer, reinforcement-learning engineer, and reproducibility owner for the complete HOODIE article implementation.

## Repository authority

- Repository: `hadifarajvand/hoodie_sim_v2`
- Remote execution base: `origin/hoodie-redesign/full-implementation`
- Binding runbook: `docs/plans/HOODIE_AUTONOMOUS_FULL_IMPLEMENTATION_RUNBOOK.md`
- Scope: original HOODIE only
- Explicitly excluded: ECHO, ERT, ECHO deadline masks, ECHO rewards, ECHO event-SMDP behavior, and every ECHO-derived active path
- Required outputs: Figures 8, 9, 10, and 11, including all 14 panels and four composite figures

Your authorization covers the complete implementation. Do not stop after Phase 0 and do not ask for review between phases.

## 1. Protect the current worktree and avoid the old branch conflict

The user's existing worktree may be dirty and may contain the previous Phase 0 evidence. An old local branch named `hoodie-redesign/phase-00-freeze-inventory` may also exist. Neither is a blocker.

Do not reset, clean, stash, delete, or switch the user's existing worktree.

Run from the current repository directory:

```bash
git fetch origin --prune
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
WORKTREE="../hoodie_sim_v2_full_${RUN_ID}"
BRANCH="hoodie-redesign/full-implementation-${RUN_ID}"
git worktree add -b "$BRANCH" "$WORKTREE" origin/hoodie-redesign/full-implementation
cd "$WORKTREE"
git status --short --branch
git rev-parse HEAD
```

If the sibling worktree path is unavailable, choose another new path. Do not reuse or overwrite an existing worktree or branch.

## 2. Read the complete implementation authority

Read the entire file, not only headings or summaries:

```text
docs/plans/HOODIE_AUTONOMOUS_FULL_IMPLEMENTATION_RUNBOOK.md
```

Treat it as binding. Build a machine-readable task graph from Stages 0–21 and execute all of it in dependency order.

Also read `docs/plans/HOODIE_MODULAR_REDESIGN_IMPLEMENTATION_PLAN.md` for the longer module contracts, acceptance details, and paper-to-code correspondence. The autonomous runbook overrides only the previous stop-after-each-phase rule.

Do not create a competing plan. Record clarifications in source contracts, decision logs, progress manifests, tests, or code documentation.

## 3. Execution mode

Execute Stages 0–21 continuously in this invocation.

For every stage:

1. implement the specified modules and migrations;
2. run the targeted tests and acceptance gate;
3. diagnose and repair failures yourself;
4. update the continuous progress manifest;
5. commit and push recoverable milestones;
6. continue automatically to the next stage.

Do not return separate stage reports. Do not wait for independent review. Do not stop because ordinary tests fail, dependencies are incompatible, modules are missing, or legacy code is defective. Those are implementation tasks.

Only stop for a hard blocker defined by Section 1 of the autonomous runbook.

## 4. Environment recovery is authorized

The previous baseline used Python 3.14.3 and failed during test collection. That result is historical evidence, not a blocker.

Create an isolated project environment using the newest locally available Python interpreter supported by the resolved scientific stack, preferring Python 3.12 when available. Do not modify unrelated global environments.

During package bootstrap:

- create one `pyproject.toml`;
- create one dependency lock strategy;
- make test collection work in the isolated environment;
- record Python, NumPy, PyTorch, backend, operating system, and lock hashes;
- use CUDA when available, MPS on supported Apple Silicon when available, otherwise CPU;
- preserve deterministic and backend metadata.

## 5. Implement the modular architecture, not another mixed patch

Build the new canonical package:

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
├── reporting/
├── reproducibility/
└── verification/
```

Follow the current-to-target migration map in the runbook.

Critical constraints:

- the neutral physical kernel must not import learning, baselines, plotting, experiments, ECHO, or legacy adapters;
- do not repair `gym_adapter.py` into the final architecture;
- do not repair `hoodie_model.py` into the final architecture;
- use one canonical action vocabulary;
- use one target-network implementation;
- use tensor-safe checkpoint serialization;
- do not hard-code gamma or sweep values inside Python logic;
- do not mix heuristic hints or compatibility biases into learned Q-values;
- implement the source-backed distributed learner ownership model;
- use immutable traces and common random numbers for fair comparisons;
- use dataset-first rendering with complete provenance.

Reuse verified formulas, fixtures, tests, and stable mechanics from the current repository when they are scientifically valid. Copy/refactor them into the new package rather than rewriting proven behavior unnecessarily. The new package must not import mixed legacy modules.

## 6. Lock the paper before method-defining implementation

Use this authority hierarchy:

1. `resources/papers/hoodie/original/HOODIE_paper.pdf`
2. OCR under `resources/papers/hoodie/ocr/`, checked against the PDF
3. recovered parameter and approved-assumption registries
4. typed source contracts created by this run
5. the autonomous runbook
6. new tests and implementation
7. legacy code only as non-authoritative evidence

Resolve and contract at minimum:

- state dimension, ordering, normalization, and causal history;
- action count, indexing, local/horizontal/cloud mapping, and topology legality;
- reward formula, sign, delayed timing, and drop penalty;
- argmax/argmin semantics;
- LSTM input, target, reset, training, and no-LSTM ablation;
- dueling DDQN architecture and target-update units;
- learner ownership and distributed aggregation;
- queue, transmission, service, and timeout chronology;
- all Figure 8–11 experiment grids, series, checkpoint reuse rules, seeds, episodes, aggregation, uncertainty, and panel layout.

Do not use digitized paper curves as generated results. They may only be validation references with uncertainty and provenance.

## 7. Remove ECHO fully from the active redesign line

Preserve history and create an archive/removal manifest, then remove ECHO from active:

- source imports and conditionals;
- ERT fields and ordering;
- ECHO action masks and reward terms;
- event-SMDP code;
- ECHO tests and fixtures;
- ECHO configs and run scripts;
- active ECHO docs, control, reconciliation, validators, authority snapshots, and onboarding;
- ECHO checkpoints and smoke artifacts from active execution paths.

Archived historical material may retain ECHO terminology. Active HOODIE source, tests, configs, scripts, architecture docs, reproducing docs, and CLI paths must pass the zero-reference scan defined by the runbook.

Do not remove legacy HOODIE modules until the new path passes parity and replacement gates.

## 8. Required learning and simulation implementation

Implement and test:

- typed task specification and lifecycle state;
- topology graph and legal action mapping;
- private, outbound, destination, and cloud queues;
- local compute, horizontal transfer, vertical transfer, service, timeout, completion, and drop mechanics;
- deterministic slot kernel and frozen slot-boundary chronology;
- immutable workload traces, trace hashing, seed lineage, and common random numbers;
- complete non-placeholder HOODIE observations and causal load history;
- operational LSTM forecasting and isolated no-LSTM bypass;
- dueling online/target Q networks;
- masked epsilon-greedy action selection;
- Double-DQN target computation;
- replay, optimizer, target updates, training metrics, checkpoint/resume, and evaluation mode;
- delayed reward and transition ownership;
- distributed per-agent training according to the source contract;
- FLC, RO, HO, VO, BCO, and MLEO on the same policy port and same kernel;
- paired evaluation, task-level records, metrics, aggregation, and confidence intervals;
- deterministic CLI, configuration, deployment, and artifact verification.

## 9. Full figure campaign is mandatory

Quick and pilot campaigns are validation gates only. Continue to the full source-locked campaign.

Produce:

- Figure 8a and 8b;
- Figure 9a, 9b, 9c, 9d, and 9e;
- Figure 10a, 10b, 10c, 10d, 10e, and 10f;
- Figure 11 with HOODIE-with-LSTM and HOODIE-without-LSTM in the same panel;
- composite Figures 8, 9, 10, and 11.

For every panel export:

- raw task, decision, transition, episode, training, and evaluation evidence;
- frozen machine-readable dataset;
- configuration and source hashes;
- trace and checkpoint lineage;
- aggregation manifest;
- SVG;
- PDF;
- deterministic 300-dpi PNG.

Parallelize independent jobs safely. Use content-addressed job IDs, atomic output directories, checkpoint reuse, and automatic resume. Reduce parallelism on memory pressure rather than abandoning the full campaign.

Do not claim completion from smoke artifacts or existing legacy figure directories.

## 10. Testing and verification

Run and repair:

- unit tests;
- property tests;
- source-contract tests;
- integration tests;
- differential tests;
- checkpoint round-trip and resume tests;
- distributed multi-agent training tests;
- baseline policy-contract tests;
- paired-trace fairness tests;
- experiment-DAG tests;
- dataset-schema and provenance tests;
- deterministic rendering tests;
- complete supported repository test suite;
- fresh-clone smoke reproduction.

Legacy tests that only assert removed ECHO behavior may be archived or deleted. Original HOODIE behavior must remain covered by migrated or stronger tests.

## 11. Continuous evidence and commits

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

Use milestone commits corresponding to the runbook. Push the unique branch after every milestone:

```bash
git push -u origin "$BRANCH"
```

After the first push:

```bash
git push origin "$BRANCH"
```

Never force-push. Never modify or merge into `main`. Do not automatically merge the final branch.

## 12. Final acceptance

Do not finish until all of these are true:

- the original HOODIE contract is locked and hashed;
- the new modular package is the active implementation;
- ECHO has zero active references in the defined execution surface;
- one supported isolated environment installs and collects tests successfully;
- the neutral kernel is deterministic and learning-independent;
- the LSTM and no-LSTM paths are operational and isolated;
- distributed learner ownership is verified;
- all six baselines use the same kernel and traces;
- fairness and provenance checks pass;
- all 14 panel datasets and exports exist;
- all four composite figures exist;
- SVG, PDF, and 300-dpi PNG integrity checks pass;
- every plotted point links to raw supporting evidence;
- the reproducibility bundle is complete;
- fresh-clone smoke reproduction passes.

## 13. Final response only

Return one final structured report with:

- verdict;
- worktree path;
- local and remote branch;
- starting and final commits;
- milestone commits;
- implemented architecture;
- source-contract decisions and assumptions;
- ECHO removal summary and zero-reference result;
- environment and backend;
- complete test results;
- training and evaluation campaign summary;
- paths to all 14 panel exports;
- paths to all four composite exports;
- reproducibility bundle path;
- remaining honest limitations;
- exact commands for the user to fetch and inspect the final branch.

Do not return a Phase 0 report. Do not request stage approval. Do not stop at quick or pilot mode.
