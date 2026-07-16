from __future__ import annotations

import os
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LEGACY_REPOSITORY_RUN_ROOT = REPOSITORY_ROOT / "artifacts" / "hoodie"


def run_root() -> Path:
    """Return the configured scientific runtime root.

    Validation and compatibility tests may use the ignored legacy location when
    no environment variable is supplied. Production operator scripts require an
    explicit absolute ``HOODIE_RUN_ROOT`` outside the repository.
    """

    configured = os.environ.get("HOODIE_RUN_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return LEGACY_REPOSITORY_RUN_ROOT


def campaign_root() -> Path:
    return run_root() / "campaigns"


def distributed_root() -> Path:
    return run_root() / "distributed"


def release_root() -> Path:
    return run_root() / "releases"


def implementation_root() -> Path:
    return run_root() / "implementation_run"


def assert_external_run_root(*, minimum_free_gb: int = 20) -> dict[str, object]:
    configured = os.environ.get("HOODIE_RUN_ROOT")
    if not configured:
        raise RuntimeError("HOODIE_RUN_ROOT must be set for experiment execution")
    root = Path(configured).expanduser()
    if not root.is_absolute():
        raise RuntimeError("HOODIE_RUN_ROOT must be an absolute path")
    root = root.resolve()
    repository = REPOSITORY_ROOT.resolve()
    if root == repository or repository in root.parents or root in repository.parents:
        raise RuntimeError("HOODIE_RUN_ROOT must be outside the Git repository")
    root.mkdir(parents=True, exist_ok=True)

    import shutil

    usage = shutil.disk_usage(root)
    required_bytes = max(minimum_free_gb * 1024**3, int(usage.total * 0.10))
    if usage.free < required_bytes:
        raise RuntimeError(
            "insufficient free space for HOODIE execution: "
            f"free={usage.free}, required={required_bytes}"
        )
    return {
        "run_root": str(root),
        "free_bytes": usage.free,
        "total_bytes": usage.total,
        "required_free_bytes": required_bytes,
        "outside_repository": True,
    }
