from __future__ import annotations

from pathlib import Path

FEATURE_ID = "070-topology-timeout-reward-fidelity"
FEATURE_NAME = "Feature 070 - Topology, Timeout/Drop, and Reward Fidelity"
BASE_BRANCH = "main"
IMPLEMENTATION_BRANCH = "070-topology-timeout-reward-fidelity-implementation"

FEATURE_070_SPEC = Path("specs/070-topology-timeout-reward-fidelity/spec.md")
FEATURE_070_PLAN = Path("specs/070-topology-timeout-reward-fidelity/plan.md")
FEATURE_070_RESEARCH = Path("specs/070-topology-timeout-reward-fidelity/research.md")
FEATURE_070_DATA_MODEL = Path("specs/070-topology-timeout-reward-fidelity/data-model.md")
FEATURE_070_TASKS = Path("specs/070-topology-timeout-reward-fidelity/tasks.md")
FEATURE_070_QUICKSTART = Path("specs/070-topology-timeout-reward-fidelity/quickstart.md")
FEATURE_070_CHECKLIST = Path("specs/070-topology-timeout-reward-fidelity/checklists/requirements.md")
FEATURE_070_CONTRACT = Path("specs/070-topology-timeout-reward-fidelity/contracts/feature-070-fidelity-report-schema.md")

FEATURE_069_SPEC = Path("specs/069-full-hoodie-mechanism-fidelity-batch/spec.md")
FEATURE_069_PLAN = Path("specs/069-full-hoodie-mechanism-fidelity-batch/plan.md")
FEATURE_069_TASKS = Path("specs/069-full-hoodie-mechanism-fidelity-batch/tasks.md")

FEATURE_068R_SPEC = Path("specs/068-paper-baseline-policy-fidelity-batch/spec.md")
FEATURE_068R_REPAIR = Path("specs/068-paper-baseline-policy-fidelity-batch/paper-exact-baseline-repair.md")

PAPER_MECHANISM_REGISTRY = Path("artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md")
PAPER_TO_CODE_MAPPING = Path("docs/paper_notes/paper_to_code_mapping.md")

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/topology_timeout_reward_fidelity")

VALIDATION_COMMANDS = (
    "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_policy_registry tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow",
    "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_full_hoodie_mechanism_fidelity_batch_report tests.unit.test_full_hoodie_mechanism_fidelity_batch_scope_guard tests.integration.test_full_hoodie_mechanism_fidelity_batch_report",
    "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests.unit -p 'test_topology_timeout_reward_fidelity_*.py'",
    "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests.integration -p 'test_topology_timeout_reward_fidelity_*.py'",
    "git diff --check",
    "git diff --name-only origin/main...HEAD",
)

ALLOWED_PATH_PREFIXES = (
    "specs/070-topology-timeout-reward-fidelity/",
    "specs/070-topology-timeout-reward-fidelity/tasks.md",
    "src/analysis/topology_timeout_reward_fidelity/",
    "tests/unit/test_topology_timeout_reward_fidelity_",
    "tests/integration/test_topology_timeout_reward_fidelity_",
)

FORBIDDEN_PATH_PREFIXES = (
    "src/environment/",
    "src/training/",
    "src/agents/",
    "artifacts/",
    "resources/",
    "specs/068-paper-baseline-policy-fidelity-batch/",
    "specs/069-full-hoodie-mechanism-fidelity-batch/",
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
