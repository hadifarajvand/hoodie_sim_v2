# RuFlo Policy

RuFlo is the coordination layer, not the main editor.

## Default topology

Use hierarchical-mesh.

Reason:
- hierarchical control reduces drift
- mesh allows specialist collaboration
- hierarchical-mesh balances precision and parallelism

## Default swarm size

Use 6 agents for normal feature work:

1. coordinator
2. graph-analyst
3. coder
4. tester
5. reviewer
6. security-auditor only when needed

Use up to 8 agents for major refactor/audit:

1. hierarchical-coordinator
2. graph-analyst
3. backend-coder
4. frontend-coder
5. test-engineer
6. reviewer
7. security-architect
8. performance-engineer

Avoid more than 8 unless explicitly approved.

## Editing rules

- coordinator does not edit
- graph-analyst does not edit
- coder edits application files
- tester may edit tests
- reviewer does not edit
- security-auditor does not edit by default
- performance-engineer does not edit by default

## Use RuFlo for

- repo-wide refactor
- multi-module feature
- large audit
- security review
- test gap analysis
- production readiness review
- repeated project workflow
- memory of decisions/failures/patterns

## Do not use RuFlo for

- tiny one-file fixes
- obvious copy changes
- trivial config edits
- production deployment
- secret handling
