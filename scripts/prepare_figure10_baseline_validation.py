from __future__ import annotations

from pathlib import Path


BASELINE_200_COMMAND = """./.venvmac/bin/python scripts/run_figure10_validation.py \\
  --output-dir artifacts/figure10_validation/runs/baseline-200-seed42 \\
  --episodes 200 \\
  --policies RO,FLC,VO,HO,BCO,MLEO \\
  --seed 42"""

SMOKE_COMMAND = """./.venvmac/bin/python scripts/run_figure10_validation.py \\
  --output-dir artifacts/figure10_validation/runs/smoke-baseline-seed42 \\
  --episodes 2 \\
  --policies RO,FLC,VO,HO,BCO,MLEO \\
  --seed 42 \\
  --test-mode"""

FULL_COMMAND = """./.venvmac/bin/python scripts/run_figure10_validation.py \\
  --output-dir artifacts/figure10_validation/runs/full-figure10-200-seed42 \\
  --episodes 200 \\
  --policies HOODIE,RO,FLC,VO,HO,BCO,MLEO \\
  --hoodie-checkpoint-dir <PATH_TO_TRAINED_HOODIE_CHECKPOINT_DIR> \\
  --seed 42 \\
  --strict-readiness"""

POST_RUN_INSPECTION = """./.venvmac/bin/python - <<'PY'
import json
from pathlib import Path

run_dir = Path("artifacts/figure10_validation/runs/baseline-200-seed42")
readiness = json.loads((run_dir / "figure10_policy_readiness.json").read_text())
summary = json.loads((run_dir / "figure10_policy_metrics_summary.json").read_text())

print("figure10_data_ready:", readiness.get("figure10_data_ready"))
print("baseline_validation_ready:", readiness.get("baseline_validation_ready"))
print("blocking_reasons:", readiness.get("blocking_reasons"))
print("summary_rows:")
for row in summary.get("summary_rows", []):
    print(
        row.get("regime_id"),
        row.get("policy_name"),
        "episodes_completed=", row.get("episodes_completed"),
        "mean_delay=", row.get("mean_average_computation_delay"),
        "mean_drop_ratio=", row.get("mean_drop_ratio"),
        "status=", row.get("policy_readiness_status"),
    )
PY"""

GIT_HYGIENE = """git status --short
git check-ignore -v artifacts/figure10_validation/runs/baseline-200-seed42/figure10_policy_metrics_raw.csv || true
find artifacts/figure10_validation/runs -type f \\( -name "*.png" -o -name "*.pdf" -o -name "*.pth" -o -name "*.pt" -o -name "*.pkl" \\)"""


def main() -> int:
    print("Phase 5 Figure 10 baseline validation runbook")
    print("")
    print("Baseline-only validation")
    print("This is usable now. HOODIE is intentionally excluded.")
    print(BASELINE_200_COMMAND)
    print("")
    print("Tiny smoke run")
    print(SMOKE_COMMAND)
    print("")
    print("Full official Figure 10 validation")
    print("This requires a trained HOODIE checkpoint. Without one, HOODIE is unavailable_not_trained.")
    print(FULL_COMMAND)
    print("")
    print("What to inspect after a run")
    print(POST_RUN_INSPECTION)
    print("")
    print("Git hygiene checks")
    print(GIT_HYGIENE)
    print("")
    print("Notes")
    print("- Generated outputs under artifacts/figure10_validation/runs/ are intentionally ignored by git.")
    print("- Do not commit raw run outputs, plots, or model files.")
    print("- If you need to share large run artifacts, compress them outside git or use a later artifact mechanism.")
    print("- Only commit code, tests, and small audit/runbook files after you confirm the run result.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
