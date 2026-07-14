# ECHO revision-280 reconciliation payload

This directory stores the offline revision-280 authority and planning-reconciliation payload.

Materialize and verify it from a clean repository worktree with:

```bash
python3 scripts/control/materialize_revision_280_reconciliation.py
```

The materializer concatenates the seven ordered files under `source_parts/`, verifies the exact revision-280 snapshot SHA-256, checks equation tags `1..67`, verifies Algorithm 1 has 23 numbered lines and Algorithm 2 has 14, rejects tab-title assertions, and writes the current authority, reconciliation report, revision comparison record, and v4.3 amendment to their repository paths.

The earlier encoded archive and partial encoded files are legacy transport attempts and are not consumed by the authoritative materializer.

After materialization, the reconciliation agent must read and execute `AGENT_PROMPT.txt`. Execution remains paused until the v4.3 validator and source-lock checks pass.
