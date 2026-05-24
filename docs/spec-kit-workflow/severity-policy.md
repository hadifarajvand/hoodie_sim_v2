# SpecKit Analyzer Severity Policy

This policy prevents the workflow from getting stuck on cosmetic issues while still blocking real risks.

## Must block implementation

Block `/speckit.implement` for:

- CRITICAL constitution, scope, or artifact integrity issue
- HIGH schema/spec/plan/tasks inconsistency
- missing required report field
- missing required test gate for a readiness-critical field
- task graph allows forbidden runtime, policy, dependency, training, checkpoint, campaign, or prior-artifact changes
- dirty-worktree-sensitive prior-feature validation
- duplicated or skipped task IDs that make execution order ambiguous
- report can claim readiness while a required gate is false
- report can use fake evidence, fake zeros, placeholder counts, or sample-derived aggregate counts

## Usually block implementation

Block unless there is a written reason not to:

- MEDIUM ambiguity on a readiness or routing field
- terminology drift that affects schema, report, tests, or verdict names
- missing top-level copy of a field that is used as a machine-readable gate
- inconsistent next-feature recommendation vocabulary

## Do not block implementation by default

Do not block for:

- LOW duplicate wording
- cosmetic phrasing
- optional cleanup
- redundant requirement wording that maps to the same tests
- report text verbosity
- minor markdown formatting

Log these issues and continue unless they can cause test, schema, artifact, or routing drift.

## Decision rule

If the issue can make the implementation lie, block.

If the issue only makes the docs ugly, do not block.
