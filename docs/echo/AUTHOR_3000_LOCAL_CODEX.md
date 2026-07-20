# Local Codex run: author-matched 3,000-episode ECHO

This workflow lets Codex fetch the repository, validate the locked protocol, estimate the target machine's runtime, and stop for explicit approval before starting scientific execution.

Campaign: `echo-hoodie-figures-8-11-3000-20260718-001`

The latest compact reference observation is recorded in [`REFERENCE_100_PROGRESS_20260720.json`](REFERENCE_100_PROGRESS_20260720.json). It contains timing and progress only, not raw scientific caches.

The locked run contains 18 learned checkpoints × 3,000 real training episodes, 108 evaluation points × 200 real held-out episodes, one fixed seed, 110 slots, the exact 14-panel HOODIE Figures 8–11 structure, all inherited baselines, and the ECHO/ECHO-NoLSTM ablation. Training curves contain only real samples at episodes 250, 500, …, 3,000.

## Approval-gated flow

1. Give Codex the prompt in [`CODEX_AUTHOR_3000_PROMPT.md`](CODEX_AUTHOR_3000_PROMPT.md).
2. Codex fetches `origin/main`, creates the Python environment, runs contract and non-long tests, checks disk/CPU/RAM, and runs the non-mutating preflight command.
3. Codex reports smoke-test results, the exact commit, resource risks, and a runtime estimate. It must stop without starting the 3,000-episode campaign.
4. Reply `APPROVE AUTHOR 3000` to authorize execution.
5. Codex runs resumable bounded slices until verification completes, preserving every completed checkpoint and evaluation cache.

Manual preflight:

```bash
MPLCONFIGDIR=/tmp/matplotlib .venv/bin/hoodie-experiments \
  echo-author-figures-3000-preflight \
  --run-root "$HOME/echo_outputs" \
  --campaign-id echo-hoodie-figures-8-11-3000-20260718-001
```

Manual run or resume after approval:

```bash
timeout 3000 env MPLCONFIGDIR=/tmp/matplotlib \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  .venv/bin/hoodie-experiments echo-author-figures-3000 \
  --run-root "$HOME/echo_outputs" \
  --campaign-id echo-hoodie-figures-8-11-3000-20260718-001
```

Exit code 124 is a normal resumable boundary. Re-run the same command; never remove the campaign directory.

Status:

```bash
MPLCONFIGDIR=/tmp/matplotlib .venv/bin/hoodie-experiments \
  echo-author-figures-3000-status \
  --run-root "$HOME/echo_outputs" \
  --campaign-id echo-hoodie-figures-8-11-3000-20260718-001
```

The final campaign directory contains `verification_report.json`, `terminal_status.json`, four figures in PDF/SVG/300-dpi PNG, SHA-256 checksums, and a verified results archive. Raw caches and checkpoints stay outside Git.
