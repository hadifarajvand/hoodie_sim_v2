# Agent Policy

Active agent source of truth: RuFlo built-in agents.

OpenCode `.opencode/commands/` invokes:
- RuFlo hierarchical coordinator
- RuFlo hooks `route` / `pre-task` / `post-task`
- RuFlo memory search / store
- Graphify structural analysis
- validation commands

Archived custom OpenCode agents are not active unless explicitly restored.

Do not duplicate:
- coder
- tester
- reviewer
- planner
- researcher
- security-auditor
- security-architect
- performance-engineer
- hierarchical-coordinator
- memory-specialist
- backend-dev
- system-architect
- code-analyzer
- production-validator

Keep custom OpenCode agents only for project-specific roles.

## Default roles

- `hierarchical-coordinator`: classify work and route specialists
- `planner`: planning only
- `coder`: minimal scoped implementation
- `tester`: validation and regression coverage
- `reviewer`: read-only diff review
- `security-auditor`: read-only security review
- `performance-engineer`: read-only performance review
- `memory-specialist`: procedural memory search/store
- `backend-dev`: backend/API/database-service changes when needed
- `system-architect` / `code-analyzer`: architecture analysis

## Routing rules

- Small local fix: `coder` only.
- Cross-file or unknown architecture: `system-architect` / `code-analyzer` first.
- Large multi-step work: `hierarchical-coordinator` plus specialists.
- Security-sensitive work: include `security-architect` and `security-auditor`.
- Performance-sensitive work: include `performance-engineer`.

## Discipline

- No agent edits outside its scope.
- No agent deploys production.
- No agent reads secret files.
- No agent treats procedural memory as canonical until verified.
