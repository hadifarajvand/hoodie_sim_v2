# Single-repository policy for HOODIE and ECHO

## Canonical remote

All active HOODIE/ECHO implementation work belongs in exactly one GitHub repository:

```text
https://github.com/hadifarajvand/hoodie_sim_v2.git
```

The repository may contain multiple branches. The user's local layout now uses one normal clone only:

```text
/Users/hadi/Documents/GitHub/hoodie_sim_v2
```

Do not create another clone, fork, mirror, or worktree for the current project unless the user explicitly requests it.

## Active branch

The active execution branch is now:

```text
main
```

The historical branch `echo/verified-figures-5-8` is preserved as review history only after its changes are merged into `main`. Older branches and closed pull requests are historical evidence only. Do not revive, merge, or use them as the source of current scientific claims unless their changes are deliberately reviewed and reintroduced into `main`.

## Prohibited remote actions

Agents and contributors must not:

- create another GitHub repository for HOODIE, ECHO, a pilot, a smoke run, an audit, or an experiment;
- fork or mirror this repository for the current project;
- change `origin` to `hadifarajvand/HOODIE`, `hadifarajvand/hoodie_sim`, or any other repository;
- push generated run output, checkpoints, trace banks, logs, or figures to Git;
- force-push `main` or any active branch;
- merge closed historical pull requests;
- run or mutate the paused legacy campaign `figures-8-11-7587c7c6382c`.

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

The guard fails when `origin` is absent, points to another repository, or the active branch is not `main`.
