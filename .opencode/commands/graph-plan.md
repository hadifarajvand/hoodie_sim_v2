---
description: Use Graphify and RuFlo memory to produce an architecture-sensitive plan.
agent: graph-analyst
subtask: true
---

Use this for architecture-sensitive, cross-file, unfamiliar, or risky tasks.

Task: $ARGUMENTS

Rules:
- Do not edit application code.
- Prefer Graphify first if available.
- If Graphify is unavailable, use read-only search.
- Search RuFlo memory if available.
- Create/update a plan under `docs/plans/`.

Required workflow:
1. Check whether `graphify-out/graph.json` exists.
2. If Graphify exists, query the graph for affected modules and dependency paths.
3. Identify entrypoints, services, database/schema files, tests, and deployment surfaces.
4. Search RuFlo memory namespaces if available:
   - decisions
   - failures
   - patterns
   - project-rules
   - testing
5. Classify task:
   - small
   - medium
   - large
   - security-sensitive
   - production-sensitive
6. Decide whether RuFlo swarm is needed.
7. Write plan file.

Plan must include:
- graph findings
- affected nodes/files
- shortest paths or dependency relationships if available
- risk map
- agent swarm recommendation
- implementation order
- tests/build/lint/typecheck commands
- explicit no-go areas
