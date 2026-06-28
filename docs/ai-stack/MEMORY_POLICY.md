# Memory Policy

Use two memories.

## Graphify structural memory

Stores:
- code entities
- file relationships
- dependency paths
- architecture clusters
- schema/docs/code relationships
- impact analysis

Use for:
- where is this implemented?
- what depends on this?
- what path connects X and Y?
- what is impacted by this change?

## RuFlo procedural memory

Stores:
- architecture decisions
- recurring bugs
- successful fix patterns
- failed attempts
- testing rules
- deployment lessons
- project conventions
- task outcomes

Namespaces:
- project-rules
- decisions
- failures
- patterns
- security
- testing
- deployment
- research

## Canonical write rule

Use RuFlo CLI memory as canonical until MCP memory persistence is verified.

Every major task should store:
- task
- files changed
- result
- tests run
- failures
- lesson learned
