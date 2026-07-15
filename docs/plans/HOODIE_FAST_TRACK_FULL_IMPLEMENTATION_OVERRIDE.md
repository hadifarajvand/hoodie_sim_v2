# HOODIE Fast-Track Full Implementation Override

## 0. Authority and purpose

This document overrides any workflow rule in the earlier HOODIE plans that causes the implementation agent to stop after inspection, inventory, baseline testing, a phase boundary, or an independent-review checkpoint.

Repository: `hadifarajvand/hoodie_sim_v2`

Execution base: `origin/hoodie-redesign/full-implementation`

Scope: original HOODIE article only. ECHO, ERT, ECHO deadline masks, ECHO reward terms, ECHO event-SMDP behavior, and every ECHO-derived active path are excluded.

Final required outputs:

- a modular, operational `src/hoodie/` implementation;
- complete HOODIE training and evaluation;
- Figures 8a–8b, 9a–9e, 10a–10f, and Figure 11;
- four composite figures;
- SVG, PDF, and deterministic 300-dpi PNG exports;
- raw datasets, checkpoints, logs, manifests, hashes, and reproducibility instructions.

The previous no-change result is rejected. A baseline collection failure under Python 3.14.3 is not a blocker and must not be reported again as the primary outcome.

## 1. Binding fast-track decisions

1. Do not repeat Phase 0.
2. Do not wait for an independent Phase 0 review.
3. Do not create another inventory-only branch.
4. Do not run the entire legacy test suite before bootstrapping a supported environment.
5. Do not stop because the old local phase branch exists.
6. Do not stop because the original worktree is dirty; protect it with a separate worktree.
7. Do not return `REWORK`, `PLAN_CHANGE_REQUIRED`, or a progress-only report unless a hard blocker in Section 12 is present.
8. Implement code before writing broad evidence reports.
9. Use milestone commits for recoverability, but continue automatically after each milestone.
10. Never modify or merge into `main`.

The existing inspection already established that:

- Python 3.14.3 causes two collection errors;
- `src/hoodie/` does not yet exist;
- active ECHO, ERT, and event-SMDP references remain;
- no implementation commit was produced.

Treat those facts as the starting backlog. Do not spend another invocation rediscovering them.

## 2. Worktree and branch rule

Prefer continuing in the already-created isolated worktree and branch when available:

```text
hoodie-redesign/full-implementation-20260715T025447Z
```

If that worktree is no longer available, create exactly one new isolated worktree from `origin/hoodie-redesign/full-implementation`:

```bash
git fetch origin --prune
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
WORKTREE="../hoodie_sim_v2_impl_${RUN_ID}"
BRANCH="hoodie-redesign/implementation-${RUN_ID}"
git worktree add -b "$BRANCH" "$WORKTREE" origin/hoodie-redesign/full-implementation
cd "$WORKTREE"
```

Never reset, clean, stash, delete, or switch the user's original worktree.

## 3. Mandatory first implementation milestone

Before the agent is allowed to return any response, it must create, test, commit, and push a real implementation milestone containing at least:

- `pyproject.toml` with a supported Python range and one dependency strategy;
- an isolated Python 3.12 or 3.11 environment when locally available;
- an importable `src/hoodie/` package;
- typed domain models for tasks, actions, outcomes, identifiers, time, and units;
- topology loading and legal-action mapping;
- FIFO queue primitives;
- local, horizontal, and vertical service calculations;
- timeout and terminal outcome mechanics;
- a deterministic neutral slot kernel that imports no learning or ECHO code;
- immutable workload traces and trace hashing;
- focused tests for those modules;
- a CLI command that runs a deterministic kernel smoke scenario.

Minimum milestone commit message:

```text
HOODIE: implement modular physical kernel foundation
```

Push the branch immediately after this milestone, then continue to the next stages without asking for approval.

A response with no source changes is forbidden unless a hard blocker is proven with exact commands and evidence.

## 4. Source contract without paralysis

Read the original HOODIE PDF, OCR, recovered parameter registry, approved assumption registry, existing paper-to-code audit, and existing verified tests.

Create typed contracts for method-defining fields, but do not spend the entire run producing documentation before implementation.

For an ambiguity:

1. prefer the original PDF;
2. cross-check OCR and the repository's recovered registries;
3. inspect existing implementation evidence and tests;
4. choose the narrowest scientifically honest assumption when the paper is silent;
5. mark it as `approved_assumption_required` or `implementation_choice` with evidence;
6. continue implementation unless the ambiguity changes the identity of the method itself.

Never use digitized paper points as generated simulation outputs.

## 5. Canonical architecture

Build the active implementation under:

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

Dependency direction:

```text
domain
  -> topology, workload, queues, physical
  -> simulation
  -> observation and policy interfaces
  -> forecasting, learning, baselines
  -> training and evaluation
  -> experiments
  -> reporting and verification
```

The physical kernel must not import learning, baselines, plotting, experiments, ECHO, or mixed legacy adapters.

Do not patch `src/environment/gym_adapter.py` or `src/agents/hoodie_model.py` into the final design. Mine verified behavior and replace them with focused modules.

## 6. Continuous implementation order

Execute the following as one uninterrupted engineering run. Internal tests and commits are required; user approval between stages is not.

### Wave A — Foundation

1. Bootstrap supported environment and package metadata.
2. Create domain, units, configuration, and identifiers.
3. Implement topology, action indexing, and physical legality masks.
4. Implement queues, compute, transmission, timeout, completion, and drop mechanics.
5. Implement deterministic neutral slot kernel.
6. Implement immutable workload traces, common random numbers, and trace hashing.
7. Add focused unit, property, and integration tests.
8. Commit and push.

### Wave B — HOODIE learning path

1. Lock the state schema, normalization, and action schema.
2. Implement causal history and non-placeholder observation construction.
3. Implement the operational LSTM forecasting path and a strictly isolated no-LSTM path.
4. Implement Dueling Double DQN with one online network and one target network.
5. Implement legal masked epsilon-greedy selection.
6. Implement replay, Double-DQN target calculation, optimizer, target updates, metrics, and deterministic RNG state.
7. Implement tensor-safe checkpoint save/load and exact resume.
8. Implement delayed reward and transition ownership.
9. Implement independent distributed learner ownership according to the source contract.
10. Add training, checkpoint, resume, masking, and multi-agent tests.
11. Commit and push.

### Wave C — Baselines and evaluation

1. Implement FLC, RO, HO, VO, BCO, and MLEO behind the same policy port.
2. Ensure every policy uses the same kernel and immutable traces.
3. Implement task-level records, delay, drop ratio, reward, throughput, action distributions, aggregation, and uncertainty.
4. Implement paired evaluation and fairness checks.
5. Add policy-contract and common-random-number tests.
6. Commit and push.

### Wave D — ECHO removal and active-path switch

1. Preserve a removal manifest and historical references.
2. Remove ECHO imports, conditionals, ERT fields/orderings, ECHO masks, ECHO rewards, and event-SMDP behavior from active source.
3. Remove or archive ECHO-only tests, configs, scripts, checkpoints, active docs, and control flows.
4. Switch CLI and documented execution to `src/hoodie/`.
5. Keep legacy HOODIE code only until replacement tests pass, then retire unreferenced active paths.
6. Run the zero-active-reference scan.
7. Commit and push.

### Wave E — Experiments and figures

1. Implement typed experiment definitions and content-addressed job IDs.
2. Implement resumable training/evaluation DAGs.
3. Freeze raw datasets before plotting.
4. Implement source-locked experiments for Figures 8–11.
5. Run quick validation, then pilot validation, then the full campaign.
6. Export all 14 panels and four composites.
7. Export SVG, PDF, and deterministic 300-dpi PNG.
8. Verify every plotted point links to raw evidence.
9. Commit code, configs, manifests, and appropriate tracked artifacts; push.

### Wave F — Closure

1. Run the supported unit, property, contract, integration, differential, checkpoint, multi-agent, fairness, DAG, dataset, rendering, and fresh-clone tests.
2. Repair failures.
3. Generate architecture, scientific-authority, reproducing, and limitations documents.
4. Generate the reproducibility bundle.
5. Produce one final report.
6. Push the final branch.

## 7. Environment recovery

Do not use Python 3.14.3 for the supported implementation environment when dependencies do not support it.

Discover local interpreters and prefer:

1. Python 3.12;
2. Python 3.11;
3. another interpreter demonstrably supported by the resolved NumPy/PyTorch stack.

Create an isolated environment inside the implementation worktree or an adjacent safe path. Do not mutate unrelated global environments.

A legacy test collection failure is diagnostic input. Bootstrap the new package and run focused tests first, then repair or classify the supported legacy suite.

## 8. Implementation rules

- Do not hard-code gamma inside learner logic.
- Do not hard-code figure sweep grids inside plotting code.
- Do not mix heuristic hints or learned preference biases into Q-values.
- Do not use two target-network implementations.
- Do not serialize tensors through raw JSON.
- Do not fabricate convergence.
- Do not reuse smoke artifacts as final evidence.
- Do not use paper-digitized values as simulation outputs.
- Do not let policies alter exogenous traces.
- Do not bypass kernel mechanics for baselines.
- Do not claim exact reproduction where the paper leaves an approved assumption.
- Do not stop after scaffolding; continue through the learning, evaluation, and figure pipeline.

## 9. Parallelism and autonomous work

Use parallel subagents or parallel task execution when available for independent workstreams such as:

- source-contract extraction;
- domain/kernel implementation;
- observation/learning implementation;
- baselines/evaluation;
- experiment/reporting pipeline;
- tests and reproducibility.

The primary agent owns integration and must not wait for a separate user message to continue. If subagent spawning is temporarily unavailable, implement sequentially instead of stopping.

## 10. Milestone commits

At minimum, create and push these recoverable milestones:

1. `HOODIE: implement modular physical kernel foundation`
2. `HOODIE: implement observation forecasting and DDQN learner`
3. `HOODIE: implement distributed training baselines and paired evaluation`
4. `HOODIE: remove ECHO from active implementation`
5. `HOODIE: implement Figures 8-11 experiment and rendering pipeline`
6. `HOODIE: complete full campaign and reproducibility closure`

A milestone may contain multiple internal stages. Continue automatically after pushing it.

## 11. Full-campaign requirement

Quick and pilot runs are gates, not final results.

The agent must proceed to the full source-locked campaign, subject only to available memory and storage. Use resumable jobs, reduced safe parallelism, and checkpoint reuse.

Required panels:

- 8a, 8b;
- 9a, 9b, 9c, 9d, 9e;
- 10a, 10b, 10c, 10d, 10e, 10f;
- 11 with both LSTM and no-LSTM series.

Required composites:

- Figure 8;
- Figure 9;
- Figure 10;
- Figure 11.

## 12. Genuine hard blockers

The agent may stop only when at least one condition is proven:

1. continuing would overwrite unrelated user work or expose credentials and no isolated worktree/path is possible;
2. repository write permission is unavailable and no local commit can be created;
3. the original paper and all repository evidence leave a method-defining field unresolved, and every bounded assumption would change the identity of HOODIE;
4. a required original-paper resource is absent and cannot be represented honestly as an explicit assumption;
5. available memory or storage cannot support even resumable serial execution of the required campaign;
6. the execution environment itself prevents all file writes or process execution.

Ordinary test failures, missing modules, stale branches, unsupported Python 3.14, unavailable CUDA, subagent unavailability, and long runtimes are not hard blockers.

## 13. Response suppression rule

Before the first real source milestone is committed and pushed, the agent must not return a report.

After the first milestone, continue automatically. Return only when:

- the entire implementation and full campaign are complete; or
- a genuine hard blocker is proven.

A final response that says `NEXT AUTHORIZED ACTION: Independent Phase 0 review only` is explicitly invalid.

## 14. Final response

Return one final structured implementation report containing:

- verdict;
- worktree path;
- local and remote branch;
- starting and final commits;
- all milestone commits;
- implemented module tree;
- source-contract decisions and assumptions;
- ECHO removal and zero-active-reference evidence;
- supported Python environment and backend;
- complete test results;
- training and evaluation campaign summary;
- paths to all 14 panel datasets and exports;
- paths to all four composite exports;
- reproducibility bundle path;
- remaining honest limitations;
- exact fetch and inspection commands.

Do not return a Phase 0 report. Do not ask for approval between stages. Do not stop at quick or pilot mode.