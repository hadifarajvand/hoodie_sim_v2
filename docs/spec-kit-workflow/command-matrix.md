# SpecKit Command Matrix

Use this matrix to keep future prompts short, phase-specific, and auditable.

| Command | Purpose | Must contain | Must not contain | Blocks on |
|---|---|---|---|---|
| `/speckit-git-feature` | Create or select branch | feature id, title, base tag, branch name | implementation instructions | wrong base, wrong branch |
| `/speckit.specify` | Define what and why | purpose, problem, required outcomes, scope, acceptance criteria | source-code implementation details | missing required behavior or report contract |
| `/speckit.plan` | Define how | architecture, allowed paths, input artifacts, output artifacts, validation strategy, **Validation Handoff Packet** | excessive restatement of hygiene rules, AGENTS.md rewrites, local-pointer mutation | plan/spec mismatch, unsafe allowed paths, missing validation packet |
| `/speckit.tasks` | Generate executable work | task groups, tests, report fields, scope guard, commit hygiene, **Validation Handoff and Remote Audit Packet** | broad prose or duplicated feature narrative | missing task coverage, skipped/duplicate task IDs, missing validation handoff tasks |
| `/speckit.analyze` | Gate implementation | hard-stop list and severity policy | implementation | CRITICAL/HIGH contract/scope/test/handoff issues |
| `/speckit.implement` | Build and validate | allowed paths, validation command, report proof fields, git-state proof, auto-commit guard if authorized | merge, tag, vague test claims | failed validation, dirty-path contamination, missing test proof |

## Standard phase prompts

### Branch

```text
Create Feature <ID> — <Title>.
Base prerequisite: main must contain <previous-tag>.
Branch: <ID>-<short-name>.
Do not implement. Print branch, main SHA, prerequisite tag SHA, tag/main diff, and status.
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
Add section: ## Validation Handoff Packet.
The packet must define: local test command, report-generation command, expected final verdict, expected next feature, JSON proof fields, git-state commands, approved paths, forbidden paths, and auto-commit/push authorization policy.
Use docs/spec-kit-workflow/operating-contract.md and implementation-validation-handoff.md.
Do not implement.
```

### Tasks

```text
Generate Feature <ID> tasks.
Task groups: artifact gates, model/schema, computation, report, tests, scope guard, commit hygiene.
Add final task group: ## Validation Handoff and Remote Audit Packet.
That group must require: local test output or Codex validation output or CI result, JSON proof fields, git status, main...HEAD diff, cached diff, commit SHA, branch name, pushed remote ref, final_verdict, and recommended_next_feature.
Keep task IDs sequential.
Use docs/spec-kit-workflow/operating-contract.md, severity-policy.md, and implementation-validation-handoff.md.
Do not implement.
```

### Analyze

```text
Analyze Feature <ID>.
Use docs/spec-kit-workflow/severity-policy.md.
Block only CRITICAL/HIGH contract, scope, artifact, validation, or handoff issues.
Return implementation_allowed = true or false.
Do not implement.
```

### Implement

```text
Implement Feature <ID> according to approved spec, plan, and tasks.
Use docs/spec-kit-workflow/operating-contract.md and implementation-validation-handoff.md.
Allowed paths: <feature paths>.
Forbidden paths: pointer, AGENTS.md, prior artifacts, policy/deps/training/checkpoints/campaign unless explicitly allowed.
Run validation: <command>.
Print exact local validation output or CI result.
Print generated report proof fields.
Print git status, main...HEAD diff, cached diff, and dirty-path table.
If auto-commit/push is authorized and all guards pass, stage only approved paths, commit, push, and print commit SHA, branch, pushed ref, final_verdict, recommended_next_feature, and final git status.
If any guard fails, do not stage, commit, or push.
```
