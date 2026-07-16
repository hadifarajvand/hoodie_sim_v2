# Repository consolidation before HOODIE execution

The repository is not allowed to start a scientific run until the canonical consolidation gate passes from a clean checkout.

## Required order

```bash
export HOODIE_RUN_ROOT=/absolute/path/on-large-storage/hoodie-runs
python scripts/audit/repository_consolidation_gate.py \
  --check \
  --report "$HOODIE_RUN_ROOT/audits/repository/consolidation_gate.json"
python scripts/audit/full_repository_audit.py \
  --check \
  --output-dir "$HOODIE_RUN_ROOT/audits/repository"
```

A nonzero exit means `REPOSITORY_CONSOLIDATION_REQUIRED`; do not start training.

## Resolve all gate categories

- Move unique generated/historical evidence to external archive storage with hashes; retain only approved immutable manifests under `artifacts/approved/`.
- Migrate active code and tests into `src/hoodie/` and `tests/{unit,integration,acceptance}`.
- Fold `*_patch.py`, `*_v2.py`, and competing campaign modules into canonical implementations, then delete them only after parity tests pass.
- Replace `src.*` imports inside `src/hoodie/` with package-relative or `hoodie.*` imports.
- Remove active ECHO dependencies from the HOODIE paper-reproduction package.
- Set setuptools to the `src/` layout and pytest to exactly the three active test roots.
- Create the canonical executor and Figures 8–11 visualization modules.

Do not delete unique scientific evidence blindly. Do not run or mutate the paused legacy campaign `figures-8-11-7587c7c6382c`. Do not use process-killing commands.

## Validation after consolidation

```bash
python -m pip install -e '.[dev]'
python -c 'import hoodie; import hoodie.experiments'
python -m pytest -q
bash scripts/hoodie/corrected_campaign.sh validate
```

Only after all commands pass and a tiny clean-checkout acceptance run succeeds may the corrected production shards be exported.
