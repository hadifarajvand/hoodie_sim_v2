# Option B Execution Commands

**Status:** Planning only — no execution yet  
**Approval Required:** Before any command execution

---

## Pre-Execution Checklist

- [ ] Option B plan reviewed
- [ ] All figures 8/9/11 plan documents read
- [ ] Runtime estimates understood
- [ ] Safety gates acknowledged
- [ ] Ready to proceed

---

## Figure 8: L-Shaped Hyperparameter Sweep

### Smoke Test (Lightweight, <5 min)

Test one config with just 50 episodes:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Test Fig 8 high-LR config with smoke budget
HOODIE_SMOKE_EPISODE_LIMIT=50 \
python -m src.analysis.figure_8_sweep.run_fig8_lr_1e6_gamma099_smoke \
  --output-dir artifacts/production/figure-completion-option-b-plan/smoke-results/ \
  --log-level info

# Expected: < 5 minutes; produces smoke_metrics.json
```

### Full Sweep (5 Runs, ~5.4 hours)

Once smoke test passes and user approves:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Run all 5 new L-shaped configs
# (Assumes per-EA-distributed-baseline baseline already exists)
APPROVE_OPTION_B_FIG8_SWEEP=1 \
python -m src.analysis.figure_8_sweep.run_all_lshape_configs \
  --configs fig8_lr_1e6_gamma099 \
           fig8_lr_5e7_gamma099 \
           fig8_lr_1e7_gamma099 \
           fig8_lr_7e7_gamma095 \
           fig8_lr_7e7_gamma0995 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig8-results/ \
  --log-level info \
  --save-checkpoints true

# Expected: ~5.4 hours (1.077 h per run)
# Output: 5 run directories with checkpoint_metrics.json and reconciliation_status.json
```

### Individual Runs (If Running Sequentially)

```bash
# Run 1: High learning rate
APPROVE_OPTION_B_FIG8_SWEEP=1 \
python -m src.analysis.figure_8_sweep.run_fig8_lr_1e6_gamma099 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig8-results/fig8_lr_1e6_gamma099/ \
  --log-level info

# Run 2: Mid-low learning rate
APPROVE_OPTION_B_FIG8_SWEEP=1 \
python -m src.analysis.figure_8_sweep.run_fig8_lr_5e7_gamma099 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig8-results/fig8_lr_5e7_gamma099/ \
  --log-level info

# Run 3: Low learning rate
APPROVE_OPTION_B_FIG8_SWEEP=1 \
python -m src.analysis.figure_8_sweep.run_fig8_lr_1e7_gamma099 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig8-results/fig8_lr_1e7_gamma099/ \
  --log-level info

# Run 4: Low gamma
APPROVE_OPTION_B_FIG8_SWEEP=1 \
python -m src.analysis.figure_8_sweep.run_fig8_lr_7e7_gamma095 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig8-results/fig8_lr_7e7_gamma095/ \
  --log-level info

# Run 5: High gamma
APPROVE_OPTION_B_FIG8_SWEEP=1 \
python -m src.analysis.figure_8_sweep.run_fig8_lr_7e7_gamma0995 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig8-results/fig8_lr_7e7_gamma0995/ \
  --log-level info
```

---

## Figure 9: System Parameter Sensitivity Evaluation

### Smoke Test (Lightweight, <2 min)

Test one config with just 10 evaluation episodes:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Test Fig 9 arrival probability eval with smoke budget
HOODIE_SMOKE_EVAL_LIMIT=10 \
python -m src.analysis.figure_9_sensitivity.eval_fig9_arrival_prob_02_smoke \
  --agent-checkpoint artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json \
  --output-dir artifacts/production/figure-completion-option-b-plan/smoke-results/ \
  --log-level info

# Expected: < 2 minutes; produces smoke_eval_results.json
```

### Full Evaluation (6 Configs, ~0.6 hours)

Once smoke test passes and user approves:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Run all 6 system parameter eval configs
# (Uses trained agent from per-EA-distributed-baseline; no new training)
APPROVE_OPTION_B_FIG9_EVAL=1 \
python -m src.analysis.figure_9_sensitivity.run_all_system_param_evals \
  --agent-source per-EA-distributed-baseline \
  --agent-checkpoint 5000 \
  --configs fig9_arrival_prob_02 \
           fig9_arrival_prob_05 \
           fig9_arrival_prob_08 \
           fig9_agent_count_10 \
           fig9_agent_count_20 \
           fig9_agent_count_30 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig9-results/ \
  --eval-episodes 100 \
  --log-level info \
  --seed 7

# Expected: ~0.6 hours (0.1 h per eval config)
# Output: 6 result files with metrics: reward, completion, drop, latency
```

### Individual Evaluations (If Running Sequentially)

```bash
# Arrival probability: low (0.2)
APPROVE_OPTION_B_FIG9_EVAL=1 \
python -m src.analysis.figure_9_sensitivity.eval_fig9_arrival_prob_02 \
  --agent-source per-EA-distributed-baseline \
  --agent-checkpoint 5000 \
  --eval-episodes 100 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig9-results/fig9_arrival_prob_02/ \
  --log-level info

# Arrival probability: medium (0.5)
APPROVE_OPTION_B_FIG9_EVAL=1 \
python -m src.analysis.figure_9_sensitivity.eval_fig9_arrival_prob_05 \
  --agent-source per-EA-distributed-baseline \
  --agent-checkpoint 5000 \
  --eval-episodes 100 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig9-results/fig9_arrival_prob_05/ \
  --log-level info

# Arrival probability: high (0.8)
APPROVE_OPTION_B_FIG9_EVAL=1 \
python -m src.analysis.figure_9_sensitivity.eval_fig9_arrival_prob_08 \
  --agent-source per-EA-distributed-baseline \
  --agent-checkpoint 5000 \
  --eval-episodes 100 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig9-results/fig9_arrival_prob_08/ \
  --log-level info

# Agent count: low (10)
APPROVE_OPTION_B_FIG9_EVAL=1 \
python -m src.analysis.figure_9_sensitivity.eval_fig9_agent_count_10 \
  --agent-source per-EA-distributed-baseline \
  --agent-checkpoint 5000 \
  --eval-episodes 100 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig9-results/fig9_agent_count_10/ \
  --log-level info

# Agent count: medium (20)
APPROVE_OPTION_B_FIG9_EVAL=1 \
python -m src.analysis.figure_9_sensitivity.eval_fig9_agent_count_20 \
  --agent-source per-EA-distributed-baseline \
  --agent-checkpoint 5000 \
  --eval-episodes 100 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig9-results/fig9_agent_count_20/ \
  --log-level info

# Agent count: high (30)
APPROVE_OPTION_B_FIG9_EVAL=1 \
python -m src.analysis.figure_9_sensitivity.eval_fig9_agent_count_30 \
  --agent-source per-EA-distributed-baseline \
  --agent-checkpoint 5000 \
  --eval-episodes 100 \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig9-results/fig9_agent_count_30/ \
  --log-level info
```

---

## Figure 11: No-LSTM Ablation

### Code Implementation (First-time Only)

Before running the ablation, add the feedforward-only agent class:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Edit or create: src/agents/distributed_agent_no_lstm.py
# Copy existing DistributedDDQNAgent, remove LSTM layer from network init
# Expected: ~50 lines of code changes

git diff src/agents/distributed_agent_no_lstm.py
# Should show only network architecture differences
```

### Smoke Test (Lightweight, <5 min)

Test no-LSTM config with just 50 episodes:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Test Fig 11 no-LSTM config with smoke budget
HOODIE_SMOKE_EPISODE_LIMIT=50 \
python -m src.analysis.figure_11_ablation.run_fig11_no_lstm_ablation_smoke \
  --output-dir artifacts/production/figure-completion-option-b-plan/smoke-results/ \
  --log-level info

# Expected: < 5 minutes; produces smoke_metrics.json
# Verify: No LSTM in network, training loop works, metrics captured
```

### Full Ablation (1 Run, ~1.1 hours)

Once smoke test passes and user approves:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Run full no-LSTM ablation
APPROVE_OPTION_B_FIG11_ABLATION=1 \
python -m src.analysis.figure_11_ablation.run_fig11_no_lstm_ablation_full \
  --output-dir artifacts/production/figure-completion-option-b-plan/fig11-results/ \
  --episodes 5000 \
  --checkpoints 250 500 1000 1500 2000 2500 3000 3500 4000 4500 5000 \
  --eval-episodes 100 \
  --log-level info \
  --save-checkpoints true

# Expected: ~1.077 hours
# Output: checkpoint_metrics_no_lstm.json and reconciliation_status_no_lstm.json
```

---

## Post-Execution: Results Aggregation

### Collect All Results

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Verify all outputs exist
ls -lh artifacts/production/figure-completion-option-b-plan/fig8-results/*/checkpoint_metrics.json
ls -lh artifacts/production/figure-completion-option-b-plan/fig9-results/*/evaluation_results.json
ls -lh artifacts/production/figure-completion-option-b-plan/fig11-results/checkpoint_metrics_no_lstm.json
```

### Generate Updated Figures

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Generate Figure 8 with sweep (6 curves: baseline + 5 new)
python -m src.analysis.visualization.generate_figure_8_with_sweep \
  --baseline-results artifacts/production/true-per-EA-distributed-baseline/ \
  --sweep-results artifacts/production/figure-completion-option-b-plan/fig8-results/ \
  --output artifacts/production/paper-output-report/validated-figures-8-11/png/Fig08_reward_sweep_updated.png

# Generate Figure 9 sensitivity (with robustness curves)
python -m src.analysis.visualization.generate_figure_9_with_sensitivity \
  --baseline-results artifacts/production/true-per-EA-distributed-baseline/ \
  --eval-results artifacts/production/figure-completion-option-b-plan/fig9-results/ \
  --output artifacts/production/paper-output-report/validated-figures-8-11/png/Fig09_behavior_with_sensitivity_updated.png

# Generate Figure 11 comparison (with vs without LSTM)
python -m src.analysis.visualization.generate_figure_11_with_ablation \
  --with-lstm-results artifacts/production/true-per-EA-distributed-baseline/ \
  --without-lstm-results artifacts/production/figure-completion-option-b-plan/fig11-results/ \
  --output artifacts/production/paper-output-report/validated-figures-8-11/png/Fig11_lstm_comparison_updated.png
```

---

## Dry-Run Check (No Training)

To verify configs are correct before running:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Validate all configs without training
python -m src.analysis.figure_8_sweep.validate_all_configs --dry-run
python -m src.analysis.figure_9_sensitivity.validate_all_configs --dry-run
python -m src.analysis.figure_11_ablation.validate_config --dry-run

# Expected: All configs parsed, no errors, no training executed
```

---

## Cleanup (If Run Fails)

To remove partial results and retry:

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Remove specific run
rm -rf artifacts/production/figure-completion-option-b-plan/fig8-results/fig8_lr_1e6_gamma099/

# Or remove entire option-b results and start over
rm -rf artifacts/production/figure-completion-option-b-plan/fig8-results/
rm -rf artifacts/production/figure-completion-option-b-plan/fig9-results/
rm -rf artifacts/production/figure-completion-option-b-plan/fig11-results/

# Then re-run from smoke tests
```

---

## Monitoring (Long-Running Jobs)

To watch progress during full runs:

```bash
# Watch Figure 8 sweep progress
watch -n 5 'ls -lh artifacts/production/figure-completion-option-b-plan/fig8-results/*/checkpoint_metrics.json 2>/dev/null | wc -l'

# Watch Figure 11 ablation progress
watch -n 5 'ls -lh artifacts/production/figure-completion-option-b-plan/fig11-results/'

# Follow logs (if available)
tail -f artifacts/production/figure-completion-option-b-plan/fig8-results/*.log
tail -f artifacts/production/figure-completion-option-b-plan/fig11-results/*.log
```

---

## Safety Verification (After Completion)

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Verify no code was modified (only data created)
git status --short | grep -E '^ M src/|^ M configs/' && echo "ERROR: Code was modified!" || echo "OK: No code changes"

# Verify all deltas are 0.0 (reconciliation)
for f in artifacts/production/figure-completion-option-b-plan/*/reconciliation*.json; do
  delta=$(jq '.delta' "$f" 2>/dev/null)
  if [ "$delta" != "0.0" ]; then
    echo "ERROR: Non-zero delta in $f: $delta"
  fi
done

echo "All safety checks complete"
```

---

## Approval Command

**To approve and execute Option B in full:**

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

# Set global approval flag
export APPROVE_OPTION_B_FULL_RUN=1

# Run all smoke tests first
bash artifacts/production/figure-completion-option-b-plan/run-all-smoke-tests.sh

# Once smoke passes, run full execution
bash artifacts/production/figure-completion-option-b-plan/run-all-full-jobs.sh
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Out of memory | Reduce eval_episodes or batch_size (NOT recommended) |
| Agent checkpoint not found | Verify per-EA-distributed-baseline exists and is complete |
| Metrics mismatch | Check reconciliation_profile matches baseline |
| LSTM layer fails to disable | Verify src/agents/distributed_agent_no_lstm.py is correct |
| Figure generation fails | Ensure all results files exist before visualization |

---

**Status:** Ready for execution upon user approval.
