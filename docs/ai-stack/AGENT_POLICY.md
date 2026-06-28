# Agent Policy

## Default roles

- `coordinator`: classifies work and routes specialists
- `graph-analyst`: read-only architecture and dependency analysis
- `coder`: minimal scoped implementation
- `tester`: validation and regression coverage
- `reviewer`: read-only diff review
- `security-auditor`: read-only security review
- `performance-engineer`: read-only performance review

## Routing rules

- Small local fix: `coder` only.
- Cross-file or unknown architecture: `graph-analyst` first.
- Large multi-step work: `coordinator` plus specialists.
- Security-sensitive work: include `security-auditor`.
- Performance-sensitive work: include `performance-engineer`.

## Discipline

- No agent edits outside its scope.
- No agent deploys production.
- No agent reads secret files.
- No agent treats procedural memory as canonical until verified.
