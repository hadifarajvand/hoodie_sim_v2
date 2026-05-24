# Project SpecKit Operating Contract

This contract applies to every SpecKit feature in `hoodie_sim_v2` unless the feature explicitly overrides it.

## Pipeline

Use this order:

```text
/speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.analyze -> /speckit.implement
```

Do not implement until `/speckit.analyze` returns `implementation_allowed = true`.

## Feature size

Bundle tightly related fixes into one feature. Do not create a separate feature for every missing field, wording drift, or report hygiene flag.

## Local pointer rule

`.specify/feature.json` may be dirty as the local active SpecKit pointer. It must stay unstaged and uncommitted, and it must not appear in `git diff --name-only main...HEAD`.

Treat pointer handling as commit hygiene, not as prior-feature validation.

## Agent instruction file rule

`AGENTS.md` must not be staged or committed unless the feature explicitly changes it. If a report has an agent-cleanliness flag, regenerate the report only after this file is clean.

## Prior feature validation

Validate prior features through committed JSON artifacts only. Do not run prior-feature report builders that inspect the current worktree, current pointer state, or current dirty paths.

## Prior artifact protection

Do not rewrite prior feature artifacts unless the current feature explicitly exists to repair them. If an old artifact becomes dirty during later work, classify it as contamination and restore it before staging.

## Default forbidden paths

Unless a feature explicitly allows it, do not touch:

- `src/policies/`
- dependency files
- training packages
- checkpoints
- campaign outputs
- prior feature artifacts
- `.gitignore`
- `AGENTS.md`

Runtime-adjacent files such as `src/environment/` require explicit feature permission and must be passive-only unless the feature is a runtime repair.

## Report hygiene

A report must not claim readiness while a prerequisite, hygiene, consistency, or evidence gate is false. If a hygiene flag is false, clean the workspace and regenerate the report, or keep the final verdict blocked.

Reports must not use fake zeros, placeholder counts, sample-derived aggregate counts, or missing join evidence to claim readiness.

## Validation command discipline

Feature validation should include feature-specific tests, safe schema/config/runtime tests, and committed-artifact checks for prior features inside current-feature tests. It must not include dirty-worktree-sensitive prior-feature tests.

## Approval gates

Before staging, print status, cached diff, and a dirty-path classification table. Ask:

```text
Approve staging only approved Feature <ID> paths? Reply APPROVE_STAGE_<ID> or DENY.
```

After staging, print staged paths and ask for commit approval. After commit, ask for push approval.

## Merge and tag rule

A feature is mergeable only when the remote diff contains only approved paths, the report is internally consistent, and no forbidden paths are present. Tags must point to the merge commit on `main`; verify `git rev-parse main` equals `git rev-parse <tag>^{}`.
