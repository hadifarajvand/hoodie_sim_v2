# Quickstart — Feature 085 HOODIE Baseline Fidelity Audit and Formula Mapping

1. Confirm you are on the audit branch:

```bash
git branch --show-current
```

2. Generate the audit artifact bundle:

```bash
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --write-artifacts artifacts/feature_085_full_audit
```

3. Validate the regenerated bundle:

```bash
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit
```

4. Run the focused unit tests:

```bash
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'
```

5. Run the focused integration tests:

```bash
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'
```

6. Inspect the report and matrices:

- `artifacts/feature_085_full_audit/feature_085_audit_report.md`
- `specs/085-hoodie-paper-baseline-fidelity-audit/baseline-mapping-matrix.md`
- `specs/085-hoodie-paper-baseline-fidelity-audit/formula-mapping-matrix.md`

7. Check the merge gate:

- `MQO` must not appear in active policy coverage.
- The formula mapping matrix must be complete.
- PR #24 remains blocked until validation passes.
