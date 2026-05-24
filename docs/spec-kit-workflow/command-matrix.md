# SpecKit Command Matrix

Use this matrix to keep future prompts short and phase-specific.

| Command | Purpose | Must contain | Must not contain | Blocks on |
|---|---|---|---|---|
| `/speckit-git-feature` | Create or select branch | feature id, title, base tag, branch name | implementation instructions | wrong base, wrong branch |
| `/speckit.specify` | Define what and why | purpose, problem, required outcomes, scope, acceptance criteria | source-code implementation details | missing required behavior or report contract |
| `/speckit.plan` | Define how | architecture, allowed paths, input artifacts, output artifacts, validation strategy | excessive restatement of hygiene rules, AGENTS.md rewrites, local-pointer mutation | plan/spec mismatch, unsafe allowed paths |
| `/speckit.tasks` | Generate executable work | task groups, tests, report fields, scope guard, commit hygiene | broad prose or duplicated feature narrative | missing task coverage, skipped/duplicate task IDs |
| `/speckit.analyze` | Gate implementation | hard-stop list and severity policy | implementation | CRITICAL/HIGH contract/scope/test issues |
| `/speckit.implement` | Build and validate | allowed paths, validation command, final dirty-path table | auto-stage, auto-commit, auto-push | failed validation or dirty-path contamination |

## Standard phase prompts

### Branch

```text
Create Feature <ID> — <Title>.
Base prerequisite: main must equal <previous-tag>^{}.
Branch: <ID>-<short-name>.
Do not implement. Print branch, main SHA, tag SHA, tag/main diff, and status.
```

### Specify

```text
Create Feature <ID> specification.
Purpose: <one paragraph>.
Problem this resolves: <previous blocker>.
Required outcome: <report/verdict/artifact>.
Hard scope: <allowed and forbidden behavior>.
Use docs/spec-kit-workflow/operating-contract.md.
Do not implement.
```

### Plan

```text
Plan Feature <ID>.
Architecture: <package path, inputs, outputs>.
Allowed paths: <paths>.
Validation: feature tests plus committed-artifact checks for prior features.
Report contract: required top-level fields, verdicts, routing.
Use docs/spec-kit-workflow/operating-contract.md.
Do not implement.
```

### Tasks

```text
Generate Feature <ID> tasks.
Task groups: artifact gates, model/schema, computation, report, tests, scope guard, commit hygiene.
Keep task IDs sequential.
Use docs/spec-kit-workflow/operating-contract.md and severity-policy.md.
Do not implement.
```

### Analyze

```text
Analyze Feature <ID>.
Use docs/spec-kit-workflow/severity-policy.md.
Block only CRITICAL/HIGH contract, scope, artifact, or validation issues.
Return implementation_allowed = true or false.
Do not implement.
```

### Implement

```text
Implement Feature <ID> according to approved spec, plan, and tasks.
Use docs/spec-kit-workflow/operating-contract.md.
Allowed paths: <feature paths>.
Forbidden paths: pointer, AGENTS.md, prior artifacts, policy/deps/training/checkpoints/campaign unless explicitly allowed.
Run validation: <command>.
Print status, main...HEAD diff, cached diff, dirty-path table.
Ask for staging approval.
```
