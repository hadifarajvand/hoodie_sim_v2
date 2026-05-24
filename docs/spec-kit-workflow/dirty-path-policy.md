# Dirty Path and Staging Policy

This policy defines how to classify dirty paths before staging any SpecKit feature.

## Always allowed as local-only

| Path | Action |
|---|---|
| `.specify/feature.json` | May remain dirty as active feature pointer; never stage or commit. |

## Always forbidden unless explicitly approved

| Path | Action |
|---|---|
| `AGENTS.md` | Restore before staging unless the feature explicitly changes agent instructions. |
| `.gitignore` | Restore before staging unless the feature explicitly changes ignore rules. |
| dependency files | Restore before staging unless dependency change is explicitly approved. |
| `src/policies/` | Restore before staging unless policy work is explicitly approved. |
| checkpoints/training outputs/campaign outputs | Restore or delete before staging unless feature explicitly allows them. |
| Feature 037+ prior artifacts | Restore before staging unless current feature explicitly repairs that artifact. |

## Required dirty-path classification table

Before staging, print this table:

| Path | Status | Classification | Proposed action |
|---|---|---|---|
| `<path>` | modified/untracked | approved / local-only / forbidden / unrelated | stage / leave / restore / ask approval |

## Staging approval prompt

Use exactly:

```text
Approve staging only approved Feature <ID> paths? Reply APPROVE_STAGE_<ID> or DENY.
```

## Restore approval prompt

If unrelated or forbidden dirty files exist, ask first:

```text
Approve restoring only these unrelated/unapproved dirty paths to HEAD?
- <path 1>
- <path 2>

Reply APPROVE_RESTORE_UNAPPROVED_DIRTY_PATHS or DENY.
```

For the recurring old audit artifact, use:

```text
Approve restoring only the unrelated Feature 043 artifact to HEAD? Reply APPROVE_RESTORE_043_ARTIFACT or DENY.
```

## Commit approval prompt

After staging, print:

```bash
git diff --cached --name-only
```

Then ask:

```text
Approve committing Feature <ID>? Reply APPROVE_COMMIT_<ID> or DENY.
```

## Push approval prompt

After commit, ask:

```text
Approve pushing Feature <ID>? Reply APPROVE_PUSH_<ID> or DENY.
```

## Remote validation

After push, remote validation must check:

- branch ahead/behind relative to main
- changed file list
- forbidden paths absent
- report verdict and readiness fields
- hygiene flags true
- `.specify/feature.json` absent from branch diff

Do not merge if a report records a failed hygiene gate, even if the logic verdict is successful.
