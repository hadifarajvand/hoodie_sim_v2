# Implementation Validation Handoff Contract

This contract defines what every future feature plan, task graph, and implementation prompt must require before a pushed branch can be validated remotely.

## Purpose

The user and local Codex agent perform implementation and local execution. The assistant validates the pushed branch through the GitHub connector. Therefore every feature must produce a clear validation packet that contains both local execution proof and remote-auditable artifacts.

## Validation authority split

The assistant may confirm tests passed only when one of the following evidence sources exists:

1. The user provides local test output.
2. Codex prints local validation output after running the required commands.
3. GitHub Actions or another CI system exposes a passing test result remotely.

If none of these is available, the assistant must say:

```text
Remote artifact/diff validation passes, but tests were not rerun remotely.
```

## Required plan section

Every future feature `plan.md` must include a section named:

```text
## Validation Handoff Packet
```

That section must define:

- required local test command
- required report-generation command
- expected passing final verdict
- expected recommended next feature
- required proof fields to print from the generated JSON report
- required git state commands
- approved path set
- forbidden path set
- whether auto-commit/push is authorized after guards pass

## Required task section

Every future feature `tasks.md` must include a final task group named:

```text
## Validation Handoff and Remote Audit Packet
```

That task group must include checklist items requiring the implementer to print or provide:

- local test command output, or Codex validation output, or CI result URL
- generated JSON report proof fields
- `git status --short`
- `git diff --name-only main...HEAD`
- `git diff --stat main...HEAD`
- `git diff --cached --name-only`
- staged path list if auto-commit is used
- commit SHA
- branch name
- pushed remote ref
- final verdict
- recommended next feature

## Required implementation prompt section

Every `/speckit-implement` prompt must contain:

```text
Validation handoff packet:
After implementation, print the exact local validation command output or CI result. Then print the generated report proof fields and git state. If auto-commit/push is authorized, print commit SHA, branch name, pushed remote ref, final_verdict, recommended_next_feature, and git status --short after push.
```

## Remote validation rules

After the branch is pushed, the assistant validates through GitHub connector by checking:

- branch exists
- branch is based on current `main`
- diff contains only approved feature paths
- forbidden paths are absent
- prior artifacts are not rewritten unless explicitly scoped
- generated report artifact exists
- report final verdict matches expected passing verdict
- report blockers are empty
- report next-feature routing is correct
- provided local validation output or CI result exists when claiming tests passed

## Required wording for assistant validation

If local or CI test proof is present and branch/report checks pass:

```text
Remote validation passes and local/CI validation proof was provided. Feature is mergeable.
```

If branch/report checks pass but local/CI proof is absent:

```text
Remote artifact/diff validation passes, but tests were not rerun remotely and no local/CI test proof was provided. Feature may be structurally mergeable, but test-pass confirmation is missing.
```

If branch/report checks fail:

```text
Validation failed. Do not merge. Failed gates: <exact failed gates>.
```

## Anti-garbage rule

Do not accept vague claims such as `tests passed` without command output, Codex validation transcript, or CI result. Do not accept `ready` without report fields and branch diff proof.
