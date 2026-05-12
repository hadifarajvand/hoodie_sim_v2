# Quickstart: User-Approved Assumption Patch Registry

1. Confirm Feature 030 is merged and tagged as `030-paper-assumption-closure-evidence-exhaustion-pipeline-complete`.
2. Verify the Feature 030 closure report exists at `artifacts/analysis/paper-assumption-closure-evidence-exhaustion/assumption-closure-report.json`.
3. Generate the assumption registry from the closure report.
4. Review the registry entries:
   - blocked items remain blocked,
   - proposed items remain report-only,
   - approved items are the only runtime-usable entries.
5. Inspect the report artifact for deterministic counts and unresolved items.
6. Do not treat any approved assumption as paper evidence.
