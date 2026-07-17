# Single-repository policy for HOODIE and ECHO

## Canonical remote

All active HOODIE/ECHO implementation work belongs in exactly one GitHub repository:

```text
https://github.com/hadifarajvand/hoodie_sim_v2.git
```

The repository may contain multiple branches and worktrees. A local Git worktree is not a second repository; it shares the same `.git` object database and the same `origin` remote.

## Active branch

The active ECHO Figures 5–8 branch is:

```text
echo/verified-figures-5-8
```

The active draft review is PR #38. Older branches and closed pull requests are historical evidence only. Do not revive, merge, or use them as the source of current scientific claims unless their changes are deliberately reviewed and cherry-picked into the active branch.

## Prohibited remote actions

Agents and contributors must not:

- create another GitHub repository for HOODIE, ECHO, a pilot, a smoke run, an audit, a worktree, or an experiment;
- fork or mirror this repository for the current project;
- change `origin` to `hadifarajvand/HOODIE`, `hadifarajvand/hoodie_sim`, or any other repository;
- push generated run output, checkpoints, trace banks, logs, or figures to a repository;
- force-push active branches;
- merge closed historical pull requests;
- run or mutate the paused legacy campaign `figures-8-11-7587c7c6382c`.

## Required local layout

Use one normal clone, optionally with multiple Git worktrees:

```text
/Users/hadi/Documents/GitHub/hoodie_sim_v2
/Users/hadi/Documents/GitHub/hoodie_sim_v2-echo-verified
```

Both paths must report the same canonical `origin` URL. Worktrees are allowed because they are branches of the same repository, not separate remotes.

## Runtime storage

All generated ECHO run data must stay outside Git under:

```text
/Volumes/ADATA-1TB-External/echo_outputs
```

The repository contains code and immutable scientific contracts. The external run root contains checkpoints, logs, traces, manifests, metrics, figures, and archives.

## Mandatory guard

Before modifying code or executing a run, invoke:

```bash
bash scripts/echo/verify_single_repository.sh
```

The guard fails when `origin` is absent, points to another repository, or the active branch is not the expected ECHO branch.
