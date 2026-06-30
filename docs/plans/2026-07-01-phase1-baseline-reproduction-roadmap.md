# Phase 1 Baseline Reproduction Roadmap

**Date**: 2026-07-01
**Repository**: hoodie_sim_v2
**Branch**: main
**Scope**: Minimum route to scientifically useful HOODIE Phase 1 baseline reproduction

---

## 1. Prioritized Roadmap

### Tier 1 — Fix Zero Completions (Immediate)

The bounded 3×200 run produces 0 completions and 4 drops. Until tasks complete, no meaningful metrics exist. This is the single highest-priority blocker.

#### Task 1.1: Investigate Why Agent Drops All Tasks

- **Goal**: Determine whether zero completions are caused by (a) incomplete state, (b) reward scale, (c) exploration failure, or (d) environment configuration
- **Files affected**: `src/analysis/full_training_reproduction_campaign/trainer.py`, `src/environment/gym_adapter.py`, `src/environment/reward_timing.py`
- **Validation**: Run bounded 3×200 with diagnostic logging; check action selection, reward signals, and terminal outcomes
- **Risk**: Low — diagnostic only, no semantic changes
- **Changes semantics**: No

#### Task 1.2: Add Per-Epoch Metric Logging

- **Goal**: Persist per-episode reward, loss, completion count, drop count to JSON/CSV during training
- **Files affected**: `src/analysis/full_training_reproduction_campaign/trainer.py` (add logging in `_episode_rollout()` and `evaluate()`)
- **Validation**: Run bounded 3×200; verify log files contain per-episode rows
- **Risk**: Low — additive logging only
- **Changes semantics**: No

#### Task 1.3: Extend Bounded Run to 50 Episodes

- **Goal**: Run 50 episodes × 200 slots to observe whether completions emerge with more training
- **Files affected**: None (config change only)
- **Validation**: Check completion count > 0
- **Risk**: Low — extends existing pipeline
- **Changes semantics**: No

### Tier 2 — Fix State Representation (High Priority)

#### Task 2.1: Implement Load History Matrix

- **Goal**: Replace zeros placeholder in `paper_state.py` with real queue load history from the environment
- **Files affected**: `src/environment/paper_state.py`, `src/environment/gym_adapter.py` (expose queue history), `src/agents/paper_state_builder.py`
- **Validation**: Verify 74D state vector contains non-zero load history values
- **Risk**: Medium — changes state representation, affects learned policy
- **Changes semantics**: Yes — state vector changes, but this is a bug fix (paper requires non-zero history)

#### Task 2.2: Implement LSTM Load Forecast

- **Goal**: Replace zeros placeholder for forecast input with real or estimated forecast data
- **Files affected**: `src/environment/paper_state.py`, `src/agents/paper_state_builder.py`
- **Validation**: Verify forecast component is non-zero
- **Risk**: Medium — may require LSTM encoder integration
- **Changes semantics**: Yes — state vector changes

#### Task 2.3: Validate State Against Paper Specification

- **Goal**: Compare implemented 74D vector component-by-component against paper's state definition
- **Files affected**: `src/environment/paper_state.py`, `docs/paper_notes/paper_to_code_mapping.md`
- **Validation**: Component checklist matches paper
- **Risk**: Low — read-only audit
- **Changes semantics**: No

### Tier 3 — Enable Campaign Infrastructure (Medium Priority)

#### Task 3.1: Enable Full Campaign Gate

- **Goal**: Set `full_campaign_enabled=True` in `paper_default()` config after readiness criteria are met
- **Files affected**: `src/analysis/full_training_reproduction_campaign/config.py`
- **Validation**: Campaign runs >100 episodes without error
- **Risk**: Low — config change
- **Changes semantics**: No

#### Task 3.2: Implement Convergence Logging

- **Goal**: Log per-epoch metrics (reward, loss, completion rate, drop rate) to a structured format (JSONL or CSV)
- **Files affected**: `src/analysis/full_training_reproduction_campaign/trainer.py`
- **Validation**: Log file contains time series; can plot convergence curves
- **Risk**: Low — additive logging
- **Changes semantics**: No

#### Task 3.3: Implement Multi-Seed Support

- **Goal**: Add seed sweep capability to campaign runner; run N seeds per configuration
- **Files affected**: `src/evaluation/campaign_runner.py`, `src/analysis/full_training_reproduction_campaign/config.py`
- **Validation**: Run 3 seeds; compute mean ± std for metrics
- **Risk**: Medium — extends campaign infrastructure
- **Changes semantics**: No

### Tier 4 — Figure Pipeline (Lower Priority)

#### Task 4.1: Implement Convergence Curve Plotting (Fig 8)

- **Goal**: Generate matplotlib convergence curves from logged per-epoch data
- **Files affected**: New file `src/analysis/figures/convergence_curves.py`
- **Validation**: Produces PNG/PDF matching paper's Figure 8 format
- **Risk**: Low — new file, read-only on data
- **Changes semantics**: No

#### Task 4.2: Implement Delay/Drop Comparison Bar Chart (Fig 10)

- **Goal**: Generate bar chart comparing delay and drop ratio across policies
- **Files affected**: New file `src/analysis/figures/delay_drop_comparison.py`
- **Validation**: Produces bar chart with multiple policies
- **Risk**: Low — new file
- **Changes semantics**: No

#### Task 4.3: Implement CDF Plot (Fig 11)

- **Goal**: Generate CDF of task delay and drop ratio
- **Files affected**: New file `src/analysis/figures/cdf_plots.py`
- **Validation**: Produces CDF matching paper format
- **Risk**: Low — new file
- **Changes semantics**: No

#### Task 4.4: Implement Action Distribution Heatmap (Fig 9)

- **Goal**: Generate heatmap of action distribution across episodes
- **Files affected**: New file `src/analysis/figures/action_heatmap.py`
- **Validation**: Produces heatmap with correct axes
- **Risk**: Low — new file
- **Changes semantics**: No

### Tier 5 — Baseline Comparison (Extended)

#### Task 5.1: Run Heuristic Baseline Comparison

- **Goal**: Execute matrix runner with FLC, VO, HO, RO, BCO, MLEO, ADAPTIVE on paper_default scenario
- **Files affected**: None (uses existing matrix_runner.py)
- **Validation**: All 7 baselines produce metrics on paper_default
- **Risk**: Low — uses existing infrastructure
- **Changes semantics**: No

#### Task 5.2: Compare DDQN vs Heuristic Baselines

- **Goal**: Produce Table 5-style comparison of DDQN against all heuristic baselines
- **Files affected**: New file `src/analysis/figures/baseline_comparison.py`
- **Validation**: Comparison table matches paper format
- **Risk**: Low — new file
- **Changes semantics**: No

---

## 2. Single Next Best Engineering Task

**Task 1.1: Investigate why agent drops all tasks**

This is the single most impactful task because:
- Without completions, no meaningful metrics exist
- All downstream tasks (convergence, figures, comparison) depend on the agent completing tasks
- The root cause may be simple (e.g., reward scale, exploration rate) or complex (incomplete state)
- Understanding this blocks or unblocks everything else

---

## 3. Minimum Route to Scientifically Useful Phase 1 Baseline

The minimum viable scientifically useful Phase 1 baseline reproduction requires:

1. **Agent completes tasks** (Task 1.1, 1.2, 1.3)
2. **State representation is complete** (Task 2.1, 2.2, 2.3)
3. **Multi-seed convergence data exists** (Task 3.2, 3.3)
4. **At least one figure is producible** (Task 4.1)
5. **At least one baseline comparison exists** (Task 5.1, 5.2)

This gives: a trained DDQN agent with convergence curves, compared against heuristic baselines, with statistical validity from multiple seeds.

**Estimated effort**: Tier 1 + Tier 2 + Tier 3 + one figure = scientifically useful baseline.

---

## 4. Risk Assessment

| Task | Risk Level | Semantic Change | Reversibility |
|------|-----------|----------------|---------------|
| 1.1 Investigate zero completions | Low | No | Fully reversible |
| 1.2 Per-epoch logging | Low | No | Fully reversible |
| 1.3 Extend to 50 episodes | Low | No | Config change |
| 2.1 Load history matrix | Medium | Yes (state fix) | Revertible |
| 2.2 LSTM forecast | Medium | Yes (state fix) | Revertible |
| 2.3 Validate state | Low | No | Read-only |
| 3.1 Enable full campaign | Low | No | Config change |
| 3.2 Convergence logging | Low | No | Additive |
| 3.3 Multi-seed support | Medium | No | Additive |
| 4.1-4.4 Figure pipeline | Low | No | New files only |
| 5.1-5.2 Baseline comparison | Low | No | Uses existing infra |

---

## 5. What Is NOT In Scope

- Phase 2 / DCQ-MADRL
- Hyperparameter tuning
- Full campaign execution
- Multi-agent scenario implementation
- Production deployment
- Committing artifacts, caches, .claude-flow, data/memory, ruvector.db

---

*Generated by OpenCode coordinator — 2026-07-01*
