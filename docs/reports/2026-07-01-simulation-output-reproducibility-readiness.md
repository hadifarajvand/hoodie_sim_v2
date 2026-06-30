# Simulation Output Reproducibility Readiness

**Date**: 2026-07-01
**Repository**: hoodie_sim_v2
**Branch**: main
**Scope**: paper_default path, Phase 1 only

---

## 1. Output/Figure Reproducibility Matrix

| Paper Output | Paper Ref | Currently Reproducible | Blocker |
|-------------|-----------|----------------------|---------|
| Fig 7: Topology visualization | Section 3 | Yes (adjacency matrix available) | No figure rendering pipeline |
| Fig 8: Training convergence curves | Section 4 | No | No per-epoch logging, no convergence pipeline |
| Fig 9: Action distribution heatmap | Section 4 | Partial (extraction stub) | No multi-seed data, no heatmap rendering |
| Fig 10: Delay/drop ratio bar chart | Section 4 | Partial (extraction stub) | No multi-seed data, no bar chart rendering |
| Fig 11: CDF of delay/drop | Section 4 | No | No CDF computation, no rendering pipeline |
| Table 5: Metric comparison | Section 4 | Partial (metrics exist) | No baseline comparison executed |
| Table 6: Scenario comparison | Section 4 | Partial (scenarios exist) | No cross-scenario comparison executed |

---

## 2. Metrics Currently Available

### 2.1 Implemented Metrics (`src/evaluation/metrics.py`)

| Metric | Formula | Implementation | Status |
|--------|---------|---------------|--------|
| Average delay | mean(delays) for completed tasks | `average_delay()` in `metric_formulas.py` | Available |
| Drop ratio | dropped / total | `drop_ratio()` in `metric_formulas.py` | Available |
| Throughput | count(completed) | `throughput()` in `metric_formulas.py` | Available |
| Completed tasks | count(outcome=="completed") | `evaluate_trace()` | Available |
| Dropped tasks | count(outcome=="dropped") | `evaluate_trace()` | Available |
| Total tasks | count(all records) | `evaluate_trace()` | Available |

### 2.2 Metrics Available from Trainer

| Metric | Source | Status |
|--------|--------|--------|
| Episode reward (cumulative) | `trainer.py:_episode_rollout()` | Available |
| Loss value (per training step) | `trainer.py:_train_batch()` | Available |
| Optimizer step count | `trainer.py` | Available |
| Target sync count | `trainer.py` | Available |
| Replay buffer size | `trainer.py` | Available |
| Illegal action count | `trainer.py:_episode_rollout()` | Available |
| Pending-at-horizon count | `trainer.py:_episode_rollout()` | Available |

### 2.3 Metrics Missing or Unreliable

| Metric | Status | Detail |
|--------|--------|--------|
| Per-epoch reward curve | Missing | Not logged to disk during training |
| Per-epoch loss curve | Missing | Not logged to disk during training |
| Per-epoch completion rate | Missing | Not logged to disk during training |
| Per-epoch drop rate | Missing | Not logged to disk during training |
| Convergence detection | Missing | No convergence criterion implemented |
| Confidence intervals | Missing | No multi-seed aggregation |
| Per-seed variance | Missing | No multi-seed support |
| Deadline violation rate | Partial | `paper_timeout.py` exists but not wired to metrics |
| Queue stability metric | Missing | No queue stability computation |
| Offload distribution per node | Missing | No per-node offload counting in metrics |
| Cloud/edge/local usage ratio | Partial | Action indices exist but not aggregated into metrics |
| Load forecast accuracy | Missing | Forecast is zeros placeholder |

---

## 3. Can These Outputs Be Generated Now?

### 3.1 Reward/Convergence Curves

**Status: NO**

- Per-epoch reward is computed in `evaluate()` but not logged to a time series
- No training curve logging infrastructure exists
- Cannot produce Figure 8 (convergence curves)

### 3.2 Delay Metrics

**Status: PARTIAL**

- `average_delay()` computes mean delay for completed tasks
- With 0 completions in bounded 3×200, delay is undefined
- Cannot produce meaningful delay statistics until tasks complete

### 3.3 Drop Ratio

**Status: YES (but trivial)**

- `drop_ratio()` works correctly
- Current bounded run: 4/4 tasks dropped = 100% drop ratio
- This is a valid (but trivial) output

### 3.4 Deadline Violation

**Status: PARTIAL**

- `paper_timeout.py` implements timeout model
- Timeout-related drops are captured in `terminal_outcome="dropped"`
- No separate "deadline violation" metric is computed

### 3.5 Queue Stability

**Status: NO**

- Queue lengths are observable in the environment
- No queue stability metric (e.g., average queue length over time, queue growth rate) is computed

### 3.6 Offload Distribution

**Status: PARTIAL**

- Action indices map to destinations (local/horizontal/cloud)
- No aggregation of action distribution across episodes
- Cannot produce Figure 9 (action distribution heatmap)

### 3.7 Cloud/Edge/Local Usage

**Status: PARTIAL**

- Action semantics map to cloud (index 21), edge (indices 1-19), local (index 0)
- No usage ratio computation exists
- Cannot produce per-node usage statistics

---

## 4. Bounded Pilot Readiness

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Pipeline executes without error | Yes | 3×200 bounded run complete |
| State vector is 74D | Yes | Gate 4D verified |
| Action space is 22 | Yes | Gate 4C verified |
| Network forward pass works | Yes | 150 transitions, 87 loss steps |
| Replay buffer stores transitions | Yes | 150 transitions stored |
| All losses are finite | Yes | Bounded pilot evidence |
| Zero illegal actions | Yes | Legal action masking works |
| Metrics are computed | Yes | evaluate() returns EvaluationSummary |
| Tasks complete | **NO** | 0 completions, 4 drops across 3×200 |
| Delay statistics are meaningful | **NO** | No completed tasks → no delay |
| Convergence is observable | **NO** | Too few episodes, no logging |

**Bounded Pilot Verdict**: Pipeline is mechanically functional but produces zero completions. The simulator runs without error but the agent does not complete any tasks. This is not a counter bug (verified by diagnostic); it is a behavioral issue.

---

## 5. Medium Campaign Readiness

| Criterion | Status | Blocker |
|-----------|--------|---------|
| Multi-episode training (>100 episodes) | Not tested | Full campaign blocked by `full_campaign_enabled=False` |
| Per-episode metric logging | Not implemented | No logging infrastructure |
| Checkpoint saving/loading | Implemented | `CampaignCheckpointMetadata` exists |
| Evaluation during training | Implemented | `evaluate()` method exists |
| Seed reproducibility | Implemented | Seed bundle exists |
| Statistical aggregation | Not implemented | No multi-seed support |

**Medium Campaign Verdict**: NOT READY. The campaign infrastructure exists (config, trainer, checkpoint) but the full campaign gate is closed and no metric logging pipeline exists.

---

## 6. Full Campaign Readiness

| Criterion | Status | Blocker |
|-----------|--------|---------|
| 5000-episode training | Not tested | `full_campaign_enabled=False` |
| Convergence detection | Not implemented | No convergence criterion |
| Baseline comparison | Not executed | No comparison pipeline |
| Multi-scenario comparison | Not executed | No cross-scenario runner |
| Publication-quality figures | Not implemented | No figure pipeline |
| Reproducibility bundle | Implemented | `reproducibility_bundle.py` exists |
| Determinism verification | Implemented | `campaign_runner.py` has determinism check |

**Full Campaign Verdict**: NOT READY. Multiple P0 gaps remain: no multi-agent, no LSTM forecast, no convergence logging, no figure pipeline.

---

## 7. Figure Reproduction Readiness

| Figure | Data Available | Rendering Available | Ready |
|--------|---------------|-------------------|-------|
| Fig 7: Topology | Yes (adjacency matrix) | No (no visualization code) | No |
| Fig 8: Convergence curves | No (no per-epoch data) | No | No |
| Fig 9: Action heatmap | Partial (extraction stub) | No | No |
| Fig 10: Delay/drop bars | Partial (extraction stub) | No | No |
| Fig 11: CDF | No | No | No |

**Figure Reproduction Verdict**: NOT READY. No figure rendering pipeline exists. Extraction stubs for Fig 9 and 10 exist but produce no usable data without multi-seed campaign results.

---

## 8. Final Readiness Verdict

| Dimension | Verdict | Confidence |
|-----------|---------|------------|
| **Bounded pilot** | Mechanically functional, zero completions | High |
| **Medium campaign** | NOT READY | High |
| **Full campaign** | NOT READY | High |
| **Figure reproduction** | NOT READY | High |
| **Publication readiness** | NOT READY | High |

### Root Causes

1. **Zero completions**: The agent drops all tasks in bounded runs. This is not a counter bug — the diagnostic confirms 4 drops, 0 completions. The agent has not learned to complete tasks. This could be due to:
   - Insufficient training (only 3 episodes × 200 slots)
   - Incomplete state representation (zeros for forecast/history)
   - Reward scale issues
   - Exploration-exploitation imbalance

2. **Incomplete state**: The 74D state vector has zeros for forecast and load history components. The LSTM encoder receives partially-empty input, which may prevent it from learning temporal patterns.

3. **No logging infrastructure**: Per-epoch metrics are not persisted. Without this, convergence analysis is impossible.

4. **No figure pipeline**: Even if data existed, no rendering code produces paper-style figures.

---

*Generated by OpenCode coordinator — 2026-07-01*
