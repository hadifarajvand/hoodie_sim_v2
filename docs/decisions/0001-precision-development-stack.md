# Decision 0001: Precision Development Stack

## Decision

Use OpenCode + Graphify + RuFlo as the project AI development stack.

## Rationale

- OpenCode is the execution cockpit.
- Graphify provides structural memory and architecture impact analysis.
- RuFlo provides swarm coordination, procedural memory, hooks, and background workers.
- CI/test/build output remains the final source of truth.
- Humans approve production-impacting actions.

## Default topology

RuFlo hierarchical-mesh with maximum 8 agents.

## Default workflow

1. plan
2. graph analysis when needed
3. controlled implementation
4. validation
5. review
6. memory/run-log update

## Consequences

- More setup files.
- Better repeatability.
- Less improvisation.
- Clearer permission boundaries.
- Safer production posture.
