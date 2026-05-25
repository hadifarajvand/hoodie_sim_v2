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

`.specify/feature.json` is ignored and local-only. It must stay unstaged and uncommitted, and normal dirty-path classification should not treat it as a workflow artifact after the hygiene hardening feature.

Treat pointer handling as commit hygiene, not as prior-feature validation.

## Agent instruction file rule

`AGENTS.md` is stable repository policy and must not be rewritten by normal SpecKit phases. If a report has an agent-cleanliness flag, treat a dirty `AGENTS.md` as a tool regression rather than normal workflow.

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

## Validation handoff packet

Every feature plan must include `## Validation Handoff Packet`.

Every feature task graph must include `## Validation Handoff and Remote Audit Packet`.

Every implementation result must provide one test-proof source:

- local test output
- Codex validation output
- CI result URL

Every implementation result must also provide report proof fields, git status, main...HEAD diff, cached diff, commit SHA, branch name, pushed remote ref, final verdict, and recommended next feature.

## Approval and auto-push gates

Before staging, print status, cached diff, and a dirty-path classification table. Ask:

```text
Approve staging only approved Feature <ID> paths? Reply APPROVE_STAGE_<ID> or DENY.
```

If a feature prompt explicitly grants guarded auto-commit/push authorization, Codex may stage, commit, and push only after tests pass, expected report verdict is present, blockers are empty, dirty paths are approved, and forbidden paths are absent.

## Merge and tag rule

A feature is mergeable only when the remote diff contains only approved paths, the report is internally consistent, required test proof is available, and no forbidden paths are present. Tags must point to the merge commit on `main`; verify `git rev-parse main` equals `git rev-parse <tag>^{}`.
