# Figure 10 Validation Runbook

Use this helper when you want to run the official Figure 10 validation workflow manually.

## Baseline-only validation

This is the safe, usable-now path. It excludes `HOODIE` because a trained checkpoint is not available.

```bash
./.venvmac/bin/python scripts/run_figure10_validation.py \
  --output-dir artifacts/figure10_validation/runs/baseline-200-seed42 \
  --episodes 200 \
  --policies RO,FLC,VO,HO,BCO,MLEO \
  --seed 42
```

## Tiny smoke run

Use this to check wiring without a long simulation.

```bash
./.venvmac/bin/python scripts/run_figure10_validation.py \
  --output-dir artifacts/figure10_validation/runs/smoke-baseline-seed42 \
  --episodes 2 \
  --policies RO,FLC,VO,HO,BCO,MLEO \
  --seed 42 \
  --test-mode
```

## Full official Figure 10 validation

This is blocked until you have a trained HOODIE checkpoint.

```bash
./.venvmac/bin/python scripts/run_figure10_validation.py \
  --output-dir artifacts/figure10_validation/runs/full-figure10-200-seed42 \
  --episodes 200 \
  --policies HOODIE,RO,FLC,VO,HO,BCO,MLEO \
  --hoodie-checkpoint-dir <PATH_TO_TRAINED_HOODIE_CHECKPOINT_DIR> \
  --seed 42 \
  --strict-readiness
```

## Post-run inspection

```bash
./.venvmac/bin/python - <<'PY'
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
PY
```

## Git hygiene

```bash
git status --short
git check-ignore -v artifacts/figure10_validation/runs/baseline-200-seed42/figure10_policy_metrics_raw.csv || true
find artifacts/figure10_validation/runs -type f \( -name "*.png" -o -name "*.pdf" -o -name "*.pth" -o -name "*.pt" -o -name "*.pkl" \)
```

## Do not commit

- `artifacts/figure10_validation/runs/`
- raw trace CSVs
- model checkpoints
- plot files
- `.DS_Store`

