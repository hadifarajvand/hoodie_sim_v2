from __future__ import annotations

from pathlib import Path

FEATURE_ID = "069-full-hoodie-mechanism-fidelity-batch"
FEATURE_NAME = "Feature 069 - Full HOODIE Mechanism Fidelity Batch"
BASE_BRANCH = "main"
IMPLEMENTATION_BRANCH = "069-full-hoodie-mechanism-fidelity-implementation"

FEATURE_068R_SPEC = Path("specs/068-paper-baseline-policy-fidelity-batch/spec.md")
FEATURE_068R_PLAN = Path("specs/068-paper-baseline-policy-fidelity-batch/plan.md")
FEATURE_068R_REPAIR = Path("specs/068-paper-baseline-policy-fidelity-batch/paper-exact-baseline-repair.md")
FEATURE_068R_TASKS = Path("specs/068-paper-baseline-policy-fidelity-batch/tasks-repair-addendum.md")

FEATURE_069_SPEC = Path("specs/069-full-hoodie-mechanism-fidelity-batch/spec.md")
FEATURE_069_PLAN = Path("specs/069-full-hoodie-mechanism-fidelity-batch/plan.md")
FEATURE_069_RESEARCH = Path("specs/069-full-hoodie-mechanism-fidelity-batch/research.md")
FEATURE_069_DATA_MODEL = Path("specs/069-full-hoodie-mechanism-fidelity-batch/data-model.md")
FEATURE_069_TASKS = Path("specs/069-full-hoodie-mechanism-fidelity-batch/tasks.md")
FEATURE_069_QUICKSTART = Path("specs/069-full-hoodie-mechanism-fidelity-batch/quickstart.md")
FEATURE_069_CONTRACT = Path("specs/069-full-hoodie-mechanism-fidelity-batch/contracts/full-hoodie-mechanism-fidelity-batch-report-schema.md")

PAPER_MECHANISM_REGISTRY = Path("artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md")
PAPER_TO_CODE_MAPPING = Path("docs/paper_notes/paper_to_code_mapping.md")

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/full_hoodie_mechanism_fidelity_batch")

VALIDATION_COMMANDS = (
    "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_policy_registry tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow",
    "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_full_hoodie_mechanism_fidelity_batch_report tests.unit.test_full_hoodie_mechanism_fidelity_batch_scope_guard tests.integration.test_full_hoodie_mechanism_fidelity_batch_report",
    "git diff --check",
    "git diff --name-only origin/main...HEAD",
)

ALLOWED_PATH_PREFIXES = (
    "specs/069-full-hoodie-mechanism-fidelity-batch/",
    "src/analysis/full_hoodie_mechanism_fidelity_batch/",
    "tests/unit/test_full_hoodie_mechanism_fidelity_batch_",
    "tests/integration/test_full_hoodie_mechanism_fidelity_batch",
)

FORBIDDEN_PATH_PREFIXES = (
    "specs/068-paper-baseline-policy-fidelity-batch/",
    "specs/070-",
    "src/environment/",
    "src/training/",
    "src/agents/",
    "artifacts/",
    "resources/",
)

DEPENDENCY_FILE_NAMES = {
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "Pipfile",
    "Pipfile.lock",
}
