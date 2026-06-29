---
description: Validate changes with tests/build and RuFlo post-command learning
agent: build
---

# /verify

Context: $ARGUMENTS

Do not edit source code unless explicitly requested.

## Lifecycle

1. session-start / restore
2. memory search if the verification is task-related
3. route hook
4. Graphify lookup if validation depends on impacted modules
5. spawn validation agents
6. run safe validation commands
7. store validation result
8. feedback store
9. post-task hook if verification completed the task
10. session-end

## Required agents

```bash
npx ruflo@latest agent spawn -t tester --name tester || true
npx ruflo@latest agent spawn -t production-validator --name production-validator || true
```

## Hooks around each validation command

Before each command:

```bash
npx ruflo@latest hooks pre-command --command "<command>" || true
```

After each command:

```bash
npx ruflo@latest hooks post-command --command "<command>" --exit-code "<exit-code>" || true
```

## Workflow

1. Inspect git diff.
2. Detect package manager and scripts.
3. Run safe validation in order:
   - targeted test
   - unit tests
   - typecheck
   - lint
   - build
   - integration/e2e only if safe
4. Use pre-command and post-command hooks around each validation command.
5. Use Graphify impact check if available.
6. Store the validation result in memory namespace `testing`.
7. Write the run-log instruction.
8. Run post-task learning if this completes a task.

## Testing memory

```bash
npx ruflo@latest memory store \
  --namespace testing \
  --key "<task-slug>-validation" \
  --value "Commands: <commands>. Results: <results>. Failures: <failures>. Reliable next test: <test>." \
  --tags "testing,validation" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-verification-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,testing,quality" || true

npx ruflo@latest hooks post-task \
  --task-id "<task-slug>" \
  --success <true-or-false> \
  --quality <0.00-1.00> \
  --store-results true || true

npx ruflo@latest hooks session-end || true
```

## Final output

- changed files
- commands run
- pass/fail
- likely failure cause
- safe to proceed? yes/no
- next command
