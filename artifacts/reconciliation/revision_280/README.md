# ECHO revision-280 reconciliation payload

This directory stores the immutable offline reconciliation bundle produced from the current Google Drive Proposed Method tab.

Apply it from a clean repository worktree with:

```bash
python3 scripts/control/apply_revision_280_reconciliation_bundle.py
```

The script verifies the encoded archive, the revision-280 snapshot SHA-256, revision number, equation count, algorithm counts, and absence of a tab-title assertion before writing the authority, audit, amendment, and agent-prompt files.

Execution remains paused until the agent completes the reconciliation prompt and the updated preflight passes.
