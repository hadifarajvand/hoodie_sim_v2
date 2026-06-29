---
description: Implement from a plan using RuFlo learning, coding, testing, and review
agent: build
---

# /implement

Task or plan: $ARGUMENTS

Use this for scoped implementation from an existing plan.

## Lifecycle

1. session-start / restore
2. read the relevant plan first
3. memory search
4. route hook
5. Graphify lookup if the task spans modules
6. spawn only the needed RuFlo built-in agents
7. pre-edit hook for each file before editing
8. implement the smallest correct change
9. run validation
10. run review if relevant
11. write the run-log instruction
12. store task outcome, pattern, and feedback
13. post-edit hook for each changed file
14. post-task hook
15. session-end

## Rules

- If no plan exists and the task is not tiny-local, stop and create a plan.
- Do not use full swarm for tiny-local tasks.
- Do not invent custom agents.
- Do not edit outside the smallest necessary scope.
- Do not read secrets.
- Do not deploy.
- Do not commit or push.
- Do not install dependencies unless explicitly approved.

## Required agents

```bash
npx ruflo@latest agent spawn -t hierarchical-coordinator --name coordinator || true
npx ruflo@latest agent spawn -t coder --name coder || true
npx ruflo@latest agent spawn -t tester --name tester || true
npx ruflo@latest agent spawn -t reviewer --name reviewer || true
npx ruflo@latest agent spawn -t memory-specialist --name memory-specialist || true
```

Add only when needed:

```bash
npx ruflo@latest agent spawn -t backend-dev --name backend-dev || true
npx ruflo@latest agent spawn -t security-auditor --name security-auditor || true
npx ruflo@latest agent spawn -t performance-engineer --name performance-engineer || true
```

## Commands to run

```bash
npx ruflo@latest daemon status || npx ruflo@latest daemon start || true
npx ruflo@latest hooks session-start || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace project-rules --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace decisions --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace patterns --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace failures --limit 5 || true
npx ruflo@latest hooks route --task "$ARGUMENTS" || true
npx ruflo@latest hooks explain --task "$ARGUMENTS" || true
npx ruflo@latest hooks pre-task --description "$ARGUMENTS" || true
```

Before editing a file:

```bash
npx ruflo@latest hooks pre-edit --file "<file>" || true
```

After editing a file:

```bash
npx ruflo@latest hooks post-edit --file "<file>" --success true || true
```

If the task touches multiple modules, use Graphify to identify impact before coding.

Read the relevant plan, then implement the smallest correct change. Add or update tests only when required by the plan or by the change itself.

## Validation and review

- Run targeted validation first.
- Run review on the diff if the task is non-trivial.
- Do not inflate the scope to chase hypothetical cleanliness.

## Learning storage

After work, store a precise outcome, a reusable pattern if one exists, and honest feedback:

```bash
npx ruflo@latest memory store \
  --namespace tasks \
  --key "<task-slug>-outcome" \
  --value "Task: $ARGUMENTS. Route: <agents-used>. Files: <files-changed>. Validation: <commands-results>. Result: <success-or-failure>. Lesson: <lesson>." \
  --tags "task,outcome,route" || true

npx ruflo@latest memory store \
  --namespace patterns \
  --key "<task-slug>-pattern" \
  --value "<reusable pattern learned, or 'none'>" \
  --tags "pattern,learned" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,routing,quality" || true

npx ruflo@latest hooks post-task \
  --task-id "<task-slug>" \
  --success <true-or-false> \
  --quality <0.00-1.00> \
  --store-results true || true

npx ruflo@latest hooks session-end || true
```

## Final answer

- files changed
- validation run
- review result
- memory/log path
- remaining risk
