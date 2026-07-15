# Prompt — Resume and Implement HOODIE Now

You previously returned a no-change `REWORK` report. That output is rejected because it violated the autonomous implementation authority.

Your task now is to continue from the isolated implementation worktree and perform the actual implementation.

## Repository and authority

- Repository: `hadifarajvand/hoodie_sim_v2`
- Remote authority branch: `origin/hoodie-redesign/full-implementation`
- Fast-track override: `docs/plans/HOODIE_FAST_TRACK_FULL_IMPLEMENTATION_OVERRIDE.md`
- Autonomous runbook: `docs/plans/HOODIE_AUTONOMOUS_FULL_IMPLEMENTATION_RUNBOOK.md`
- Detailed architecture plan: `docs/plans/HOODIE_MODULAR_REDESIGN_IMPLEMENTATION_PLAN.md`
- Scope: original HOODIE only
- Final output: Figures 8–11, all 14 panels, four composites, code, datasets, checkpoints, manifests, and reproducibility bundle

The fast-track override is binding wherever older documents require Phase 0 repetition, phase-by-phase user approval, or independent review before implementation.

## 1. Resume the existing isolated implementation branch

The previous isolated local branch was:

```text
hoodie-redesign/full-implementation-20260715T025447Z
```

Locate its worktree:

```bash
git worktree list --porcelain
```

If the branch and worktree still exist, enter that worktree and continue there.

If the worktree does not exist, create one new isolated worktree:

```bash
git fetch origin --prune
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
WORKTREE="../hoodie_sim_v2_impl_${RUN_ID}"
BRANCH="hoodie-redesign/implementation-${RUN_ID}"
git worktree add -b "$BRANCH" "$WORKTREE" origin/hoodie-redesign/full-implementation
cd "$WORKTREE"
```

Do not reset, clean, stash, delete, or switch the user's original worktree.

Fetch the latest authority commit and read the full files:

```bash
git fetch origin --prune
git show origin/hoodie-redesign/full-implementation:docs/plans/HOODIE_FAST_TRACK_FULL_IMPLEMENTATION_OVERRIDE.md
git show origin/hoodie-redesign/full-implementation:docs/plans/HOODIE_AUTONOMOUS_FULL_IMPLEMENTATION_RUNBOOK.md
git show origin/hoodie-redesign/full-implementation:docs/plans/HOODIE_MODULAR_REDESIGN_IMPLEMENTATION_PLAN.md
```

Bring the authority files into the implementation branch by fast-forwarding or merging `origin/hoodie-redesign/full-implementation` only when this does not overwrite implementation work. Since the previous run made no changes, a fast-forward is expected.

## 2. Do not repeat the failed inspection workflow

Do not return another baseline-only report.

Do not rerun `python -m pytest -q` under Python 3.14.3 as your first engineering action.

Do not produce inventories before source implementation.

Do not wait for independent Phase 0 review.

Do not stop because:

- Python 3.14.3 is unsupported;
- the legacy suite has collection errors;
- `src/hoodie/` is missing;
- ECHO references exist;
- ordinary tests fail;
- subagents are unavailable;
- the task is large.

Those are the implementation backlog.

## 3. Immediate mandatory work

Begin editing source now.

Before returning any message, complete, commit, and push the first real milestone defined by the fast-track override:

```text
HOODIE: implement modular physical kernel foundation
```

That milestone must include at least:

- supported project environment and `pyproject.toml`;
- importable `src/hoodie/`;
- typed domain models and units;
- topology and legal actions;
- queue primitives;
- compute, transmission, timeout, completion, and drop mechanics;
- deterministic neutral slot kernel;
- immutable workload traces and trace hashes;
- focused tests;
- a working deterministic kernel smoke CLI.

Push that milestone. Then continue automatically through:

1. observation and causal history;
2. LSTM and no-LSTM paths;
3. Dueling Double DQN;
4. replay, target updates, checkpoints, and resume;
5. delayed reward and distributed learner ownership;
6. six baselines;
7. paired evaluation and fairness;
8. full ECHO removal from active paths;
9. experiment DAG and dataset-first rendering;
10. full Figures 8–11 campaign;
11. 14 panel exports and four composites;
12. reproducibility closure and fresh-clone verification.

## 4. Use a supported environment

Discover local Python versions and prefer Python 3.12, then Python 3.11.

Create an isolated environment. Do not alter unrelated global environments.

Bootstrap and test the new package before attempting to make every legacy test compatible.

Record the supported environment in project metadata and reproducibility artifacts.

## 5. Autonomous execution

Use parallel subagents for independent modules when supported. The primary agent remains responsible for integration.

If subagent spawning fails, continue sequentially. Do not stop.

Create and push recoverable milestone commits throughout the implementation. Do not wait for user approval after a milestone.

Never modify or merge into `main`. Never force-push.

## 6. Output rules

You are not authorized to return:

- `REWORK` merely because implementation is incomplete;
- `PLAN_CHANGE_REQUIRED` for an ordinary engineering issue;
- `NEXT AUTHORIZED ACTION: Independent Phase 0 review only`;
- a report with no source changes;
- another inventory-only report;
- a smoke-only completion claim.

Return only after the complete implementation and full campaign finish, or after proving a genuine hard blocker listed in the fast-track override.

A genuine blocker report must include exact commands, errors, attempted mitigations, and why no safe implementation path remains.

## 7. Final completion report

The final report must include:

- branch and commits;
- implemented module tree;
- source-contract decisions;
- ECHO zero-active-reference evidence;
- environment and backend;
- complete tests;
- full campaign summary;
- all 14 panel dataset/export paths;
- all four composite export paths;
- reproducibility bundle;
- remaining honest limitations;
- fetch and inspection commands.

Start implementing now. Do not respond before the first source milestone is committed and pushed.