# Repository consolidation before HOODIE execution

The repository is not allowed to start a scientific run until the canonical consolidation gate passes from a clean checkout.

## 1. Fetch the exact remote branch

```bash
git fetch origin chatgpt/experiment-correctness-20260716
git switch chatgpt/experiment-correctness-20260716 2>/dev/null \
  || git switch --track -c chatgpt/experiment-correctness-20260716 \
     origin/chatgpt/experiment-correctness-20260716
git merge --ff-only origin/chatgpt/experiment-correctness-20260716
git status --short
git rev-parse HEAD
```

Stop if the worktree is not clean.

## 2. Generate the complete inventory

Set external audit storage:

```bash
export HOODIE_RUN_ROOT=/absolute/path/on-large-storage/hoodie-runs
python scripts/audit/full_repository_audit.py \
  --check \
  --output-dir "$HOODIE_RUN_ROOT/audits/repository"
```

Review:

- `repository_inventory.json`
- `repository_inventory.csv`
- `repository_audit_summary.json`

Every tracked and untracked file must be classified. Do not delete unique scientific evidence without a hash and destination record.

## 3. Run the canonical consolidation gate

```bash
python scripts/audit/repository_consolidation_gate.py \
  --check \
  --report "$HOODIE_RUN_ROOT/audits/repository/consolidation_gate.json"
```

The report must show zero for every issue count.

## 4. Resolve the gate categories

### Tracked artifacts

Move unique evidence to external release/archive storage. Keep only approved immutable manifests under `artifacts/approved/`. Remove generated campaign, analysis, control, report, smoke, reconciliation, and readiness outputs from Git tracking.

### Legacy active roots

Migrate active code and tests into:

- `src/hoodie/`
- `tests/unit/`
- `tests/integration/`
- `tests/acceptance/`

Remove top-level `hoodie/`, `tests_supported/`, and `tests_historical/` after parity and history checks.

### Transitional execution modules

Fold all behavior into the canonical modules, add parity tests, and remove:

- `*_patch.py`
- `*_v2.py`
- competing production-campaign implementations

Do not preserve scientific behavior through import-time monkey patching.

### Imports and packaging

- imports inside `src/hoodie/` use `hoodie.*` or package-relative imports;
- setuptools uses `package-dir = {"" = "src"}`;
- package discovery uses `where = ["src"]`, `include = ["hoodie*"]`;
- CLI entry point is `hoodie.experiments.cli:main`;
- pytest roots are exactly the three active `tests/` directories.

### ECHO separation

Move ECHO thesis implementation and historical ECHO diagnostics outside the active HOODIE package. HOODIE may expose a stable interface for future downstream work, but the paper-reproduction runtime must not import ECHO modules.

## 5. Validate after every consolidation slice

```bash
python scripts/audit/repository_consolidation_gate.py --check
python scripts/audit/full_repository_audit.py --check
python -m pytest -q
python -m pip install -e '.[dev]'
python -c 'import hoodie; import hoodie.experiments'
```

Commit small coherent slices. Never force-push and never target `main` directly.

## 6. Scientific validation

Only after both repository gates pass:

```bash
bash scripts/hoodie/corrected_campaign.sh validate
```

This command must complete the clean-install, compilation, scientific preflight, contract validation, full test suite, matrix validation, and storage checks without launching production.

## 7. Experiment authorization

Production is authorized only when all of the following are true:

- clean checkout at the exact remote SHA;
- consolidation gate passed;
- complete repository audit passed;
- full tests passed;
- tiny end-to-end acceptance run passed;
- external run storage passed the 20 GiB/10% reserve check;
- corrected matrix and checkpoint dependencies are frozen;
- the legacy campaign remains untouched.

Until then, return `REPOSITORY_CONSOLIDATION_REQUIRED` and do not export or execute production shards.
