# Hook Policy

Hooks exist to improve precision, not to create autonomous chaos.

## Graphify hooks

Use Graphify hooks to keep structural memory fresh after commits and branch checkouts when safe.

Recommended:
- post-commit graph update
- post-checkout graph sync
- manual update after docs/papers/schema changes

## RuFlo hooks

Use RuFlo hooks for:
- pre-task classification
- route selection
- pre-edit risk check
- post-edit changed-file record
- pre-command shell risk check
- post-command command result record
- post-task success/failure memory
- session-start project state restore
- session-end memory consolidation

## OpenCode plugins

Use OpenCode plugins for:
- requiring a plan before large edits
- blocking obvious destructive commands
- nudging architecture questions toward Graphify
- requiring validation before release
- preventing production deployment without human approval

## RuFlo hooks to enable when supported

Precision hooks:
- pre-task
- post-task
- pre-edit
- post-edit
- pre-command
- post-command
- route
- session-start
- session-end

On-demand workers:
- audit
- testgaps
- deepdive
- optimize
- document
- benchmark

Do not run all workers all the time.
Use workers on demand or for scheduled audits only.

## Forbidden automation

Hooks/plugins must not:
- deploy production
- modify secrets
- mutate cloud resources
- modify billing/DNS
- run destructive shell commands
- silently overwrite user files
