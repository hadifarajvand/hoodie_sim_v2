# ECHO autonomous handoff

## Current git identity
- Branch: `main`
- HEAD at session start: `cbfca68`
- Working tree: dirty before this handoff; existing legacy validation and runtime edits already present.

## Completed files and evidence
- Authoritative local specs confirmed:
  - `research/ECHO_method_spec.md`
  - `research/ECHO_evaluation_spec.md`
  - `resources/papers/hoodie/original/HOODIE_paper.pdf`
- Legacy bounded validation confirmed complete and non-authoritative:
  - log: `/private/tmp/claude-501/-Users-hadi-Documents-GitHub-hoodie-sim-v2/876d1b52-0544-4f7c-817c-dc60d380840a/tasks/bggsl5lxd.output`
  - driver: `scripts/run_figures_8_11_validation.py`
  - figure export gate fix: `scripts/export_figure_11.py`
- Existing ECHO helper modules found but not integrated:
  - `src/echo_action_space.py`
  - `src/echo_ert.py`
  - `src/echo_types.py`

## Unfinished files / hotspots
- Runtime core:
  - `src/environment/gym_adapter.py`
  - `src/environment/runtime_model.py`
  - `src/environment/offloading_queue.py`
  - `src/environment/private_queue.py`
  - `src/environment/public_queue.py`
- Learning core:
  - `src/training/training_loop.py`
  - `src/agents/hoodie_agent.py`
  - `src/agents/hoodie_model.py`
  - `src/agents/paper_state_builder.py`
  - `src/analysis/full_training_reproduction_campaign/trainer.py`
  - `src/analysis/full_training_reproduction_campaign/replay.py`
- Evaluation / reports:
  - `src/evaluation/runner.py`
  - final report files under `artifacts/reports/`

## Tests and exact results
- Previously confirmed before compaction:
  - `MPLCONFIGDIR="$TMPDIR/mpl" python /Users/hadi/Documents/GitHub/hoodie_sim_v2/scripts/run_figures_8_11_validation.py --output-dir /Users/hadi/Documents/GitHub/hoodie_sim_v2/artifacts/analysis/figure8-11-validation --episodes 5 --episode-length 20`
  - exit code: `0`
- Previously confirmed targeted regression suite:
  - `MPLCONFIGDIR="$TMPDIR/mpl" python -m pytest tests/unit/test_phase0_topology_legality.py tests/unit/test_topology_legality.py tests/integration/test_training_loop.py tests/unit/test_agent_components.py -q`
  - result: `76 passed in 5.02s`
- Compute resource probe this session:
  - command: `python - <<'PY'
import torch, platform
print('torch', torch.__version__)
print('cuda_available', torch.cuda.is_available())
print('mps_available', hasattr(torch.backends,'mps') and torch.backends.mps.is_available())
print('platform', platform.platform())
PY`
  - output: `torch 2.12.1`, `cuda_available False`, `mps_available False`

## Background jobs
- None active.

## Checkpoints
- No ECHO-specific training checkpoints created yet.
- Current campaign trainer still HOODIE-shaped despite paper-default wrappers.

## Experiment manifests
- Non-authoritative legacy validation only:
  - `artifacts/analysis/figure8-11-validation/validation_manifest.json`
- No authoritative ECHO Figure 4/5/6/7/8 manifest yet.

## Defects confirmed
1. ECHO state contract not implemented in live path; env emits ad hoc dict instead of fixed normalized state with ERT vector and canonical mask.
2. Candidate-level ERT helpers exist but are not wired into runtime, masks, or learner.
3. Action masking is only physical/family-level, not deadline-valid canonical masking with minimum-lateness fallback.
4. LSTM load estimate not wired into destination waiting-time estimation.
5. Pending decision record incomplete; missing deadline, predicted-risk, destination metadata.
6. Semi-Markov target wrong; current learners use one-step `gamma`, not `gamma ** delta_slots`.
7. Queue scheduling remains FIFO for local and outbound queues; ERT ordering absent.
8. Source-indexed destination-queue semantics partially modeled, but offloading queue design still binds destination at queue object level and reference lifecycle skips explicit admission event.
9. Final evaluation/report artifacts absent.

## Exact next command
Run focused implementation inspection before editing runtime core:

```bash
python -m pytest tests/integration/test_training_loop.py tests/unit/test_agent_components.py -q
```

Then patch, in order:
1. `src/environment/offloading_queue.py`
2. `src/environment/gym_adapter.py`
3. `src/training/training_loop.py`
4. `src/analysis/full_training_reproduction_campaign/trainer.py`
5. add ECHO-specific tests/manifests/reports
