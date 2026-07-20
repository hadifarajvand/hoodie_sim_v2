# Prompt for Codex

Copy everything below into Codex:

---
Work autonomously in two approval-gated phases. Do not change ECHO's scientific method, architecture, reward, state, actions, decision logic, topology, physics, or hyperparameter semantics.

Repository: `https://github.com/hadifarajvand/hoodie_sim_v2.git`

Campaign ID: `echo-hoodie-figures-8-11-3000-20260718-001`

Default output root: `$HOME/echo_outputs` (use an attached high-capacity disk instead if one is already mounted and writable).

## Phase A — fetch, preflight, estimate, then STOP

1. Clone the repository if absent. Otherwise preserve user changes, fetch `origin`, switch to `main`, and fast-forward only. Do not reset, delete, or overwrite user work.
2. Record the exact `origin/main` commit and require a clean worktree before scientific execution.
3. Create/reuse `.venv`, install the project exactly as documented, and set `MPLCONFIGDIR=/tmp/matplotlib`.
4. Run the targeted author-3000 contract/CLI/determinism/cache/figure tests and the full non-long test suite. Do not start the 3,000-episode campaign.
5. Inspect CPU count/model, available RAM, free output-disk space, Python/Torch versions, and whether CUDA is available. Use at most six CPU workers and one Torch/BLAS thread per worker.
6. Run:

   `MPLCONFIGDIR=/tmp/matplotlib .venv/bin/hoodie-experiments echo-author-figures-3000-preflight --run-root "$HOME/echo_outputs" --campaign-id echo-hoodie-figures-8-11-3000-20260718-001`

7. If a completed 100-episode reference campaign exists under the same run root, rerun preflight with:

   `--reference-campaign-id echo-hoodie-figures-8-11-100-20260718-001`

8. Report a concise preflight summary containing:
   - exact commit SHA and clean/dirty state;
   - tests passed/failed;
   - CPU/RAM/disk/device details;
   - locked work counts: 14 panels, 18×3,000 training episodes, 108×200 held-out evaluations, 12 exports;
   - methods: ECHO, HOODIE, RO, FLC, VO, HO, BCO, MLEO, and ECHO-NoLSTM ablation;
   - conservative runtime range, likely runtime, disk estimate, and the assumptions/evidence used;
   - resumability and risks.

9. STOP. Ask for exactly this approval phrase: `APPROVE AUTHOR 3000`. Do not launch training or evaluation before receiving it.

## Phase B — only after I reply `APPROVE AUTHOR 3000`

1. Recheck that the worktree is clean and `HEAD == origin/main` at the preflight SHA. If not, stop and explain.
2. Run repeated bounded slices with this exact scientific command:

   `timeout 3000 env MPLCONFIGDIR=/tmp/matplotlib OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/hoodie-experiments echo-author-figures-3000 --run-root "$HOME/echo_outputs" --campaign-id echo-hoodie-figures-8-11-3000-20260718-001`

3. Exit 124 is expected. After each slice, run `echo-author-figures-3000-status`, report progress and updated ETA, then resume. Never delete or restart completed checkpoints, partial checkpoints, or evaluation caches.
4. Keep all values real: no projection, interpolation, extrapolation, synthetic data, surrogate curves, or fabricated values through episode 5,000. Training-curve samples must be real episodes 250 through 3,000 at 250-episode intervals only.
5. When complete, verify all of the following before claiming success:
   - 14 panels;
   - 18 checkpoints × 3,000 training episodes;
   - 108 points × 200 held-out episodes;
   - all required methods and paired deterministic traces;
   - generated tasks = successful + dropped;
   - zero illegal selected actions;
   - no surrogate/projected values;
   - Figures 8–11 exported as PDF, SVG, and 300-dpi PNG (12 files);
   - verified archive and SHA-256.
6. Finish with paths to the four PNGs, `verification_report.json`, archive, SHA-256, source commit, total wall time, and a concise result summary.

---
