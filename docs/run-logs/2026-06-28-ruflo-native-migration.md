# Run Log: ruflo-native-migration

Date: 2026-06-28
Agent/tool: Codex
Report: docs/ai-stack/RUFLO_NATIVE_MIGRATION_REPORT.md

## Objective

Migrate the project away from duplicate OpenCode agent stubs and make the RuFlo built-in agent stack the source of truth.

## Files changed

- `AGENTS.md`
- `docs/ai-stack/AGENT_POLICY.md`
- `docs/ai-stack/RUFLO_NATIVE_MIGRATION_REPORT.md`
- `docs/run-logs/2026-06-28-ruflo-native-migration.md`
- `.opencode/commands/coordinator.md`
- `.opencode/commands/plan.md`
- `.opencode/commands/graph-plan.md`
- `.opencode/commands/implement.md`
- `.opencode/commands/swarm-feature.md`
- `.opencode/commands/verify.md`
- `.opencode/commands/review.md`
- `.opencode/commands/security-review.md`
- `.opencode/commands/swarm-audit.md`
- `.opencode/commands/production-check.md`
- `.opencode/agents/_archived-ruflo-duplicates/coordinator.md`
- `.opencode/agents/_archived-ruflo-duplicates/coder.md`
- `.opencode/agents/_archived-ruflo-duplicates/tester.md`
- `.opencode/agents/_archived-ruflo-duplicates/reviewer.md`
- `.opencode/agents/_archived-ruflo-duplicates/security-auditor.md`
- `.opencode/agents/_archived-ruflo-duplicates/performance-engineer.md`
- `.opencode/agents/_archived-ruflo-duplicates/graph-analyst.md`

## Commands run

- `pwd`
- `git status --short || true`
- `find .opencode -maxdepth 3 -type f 2>/dev/null | sort || true`
- `find docs/ai-stack -maxdepth 2 -type f 2>/dev/null | sort || true`
- `test -f AGENTS.md && echo "AGENTS.md exists" || true`
- `npx ruflo@latest agent --help || true`
- `npx ruflo@latest agent list || true`
- `sed -n '1,220p' .opencode/agents/coordinator.md`
- `sed -n '1,220p' .opencode/agents/coder.md`
- `sed -n '1,220p' .opencode/agents/tester.md`
- `sed -n '1,220p' .opencode/agents/reviewer.md`
- `sed -n '1,220p' .opencode/agents/security-auditor.md`
- `sed -n '1,220p' .opencode/agents/performance-engineer.md`
- `sed -n '1,220p' .opencode/agents/graph-analyst.md`
- `sed -n '1,220p' AGENTS.md`
- `sed -n '1,220p' docs/ai-stack/AGENT_POLICY.md`
- `sed -n '1,220p' docs/ai-stack/RUFLO_POLICY.md`
- `sed -n '1,220p' docs/ai-stack/MEMORY_POLICY.md`
- `sed -n '1,220p' docs/ai-stack/STACK_OVERVIEW.md`
- `find .opencode/commands -maxdepth 1 -type f | sort`
- `find .opencode/agents -maxdepth 2 -type f 2>/dev/null | sort || true`
- `npx ruflo@latest agent list || true`
- `npx ruflo@latest daemon status || true`
- `npx ruflo@latest hive-mind status || true`
- `git status --short || true`
- `git diff --check`

## Validation result

- The duplicate OpenCode agents were moved into `.opencode/agents/_archived-ruflo-duplicates/`.
- The requested OpenCode commands exist and now route through RuFlo-oriented workflow text.
- `git diff --check` passed.
- The RuFlo CLI probe failed because `npx` could not resolve `registry.npmjs.org` in this environment (`ENOTFOUND`).

## Failures

- RuFlo CLI verification could not complete locally because npm network resolution is blocked.

## Follow-up

- Re-run `npx ruflo@latest agent list`, `daemon status`, and `hive-mind status` in an environment with npm registry access.
- If any archived agent needs to be restored as a truly project-specific role, restore it from `.opencode/agents/_archived-ruflo-duplicates/` and document why.
