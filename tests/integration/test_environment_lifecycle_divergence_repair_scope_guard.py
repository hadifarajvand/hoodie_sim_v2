from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


FORBIDDEN_INSTRUMENTATION_PATH_FRAGMENTS = (
    "src/environment/gym_adapter.py",
    "src/environment/slot_engine.py",
    "src/environment/trace_source.py",
    "src/environment/topology.py",
    "src/environment/offloading_queue.py",
    "src/environment/public_queue.py",
    "src/environment/private_queue.py",
)


class EnvironmentLifecycleDivergenceRepairScopeGuardIntegrationTest(unittest.TestCase):
    def test_scope_creep_guard_blocks_instrumentation_cleanup_without_documented_dependency(self) -> None:
        changed_paths = {
            line[3:]
            for line in subprocess.run(
                ["git", "status", "--short", "--untracked-files=normal"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
            if len(line) > 3
        }
        repair_summary = Path("artifacts/analysis/environment-lifecycle-divergence-repair/repair-summary.md")
        repair_summary_text = repair_summary.read_text(encoding="utf-8") if repair_summary.exists() else ""
        documented_dependency = (
            "case-local-compute" in repair_summary_text and "case-deterministic-ordering" in repair_summary_text
        )
        if not documented_dependency:
            for forbidden in FORBIDDEN_INSTRUMENTATION_PATH_FRAGMENTS:
                self.assertFalse(
                    any(path.endswith(forbidden) for path in changed_paths),
                    f"forbidden instrumentation cleanup detected: {forbidden}",
                )


if __name__ == "__main__":
    unittest.main()
