# Feature 089 Hoodie Simulation Fidelity Audit

## Verdict

`hoodie_simulation_not_faithful_to_paper`

## Branch State

- Branch: `089-hoodie-paper-metrics-figure-catalog`
- HEAD: `5b3fa3a066a1d055f5d6738b4c4b60a04cf3fc36`
- Remote branch: `origin/089-hoodie-paper-metrics-figure-catalog`
- State at audit time: clean, remote matched local HEAD

## Bottom Line

The current simulator is a usable current-simulator artifact, but it is not faithful enough to claim paper reproduction. The failure is not one thing. It is a stack of mismatches:

- Figure 9 outputs are explicitly approximation-tagged and derived from current simulator sweeps, not paper-trained validation.
- Figure 10 outputs are generated from simulator sweeps, but the results collapse into degenerate traces with identical or near-identical policy outputs, zero completed tasks, and 100 percent drop ratios in many settings.
- Figure 8 and Figure 11 remain gated because no real training/LSTM traces exist.
- The runtime and metrics code are internally coherent, but they are not producing paper-like dynamics.
- Structured audit artifacts are now available alongside this report:
  - `mechanism_to_code_mapping.csv`
  - `mechanism_to_code_mapping.json`
  - `figure_10_failure_diagnosis.csv`
  - `figure_10_failure_diagnosis.json`
  - `figure_9_failure_diagnosis.csv`
  - `figure_9_failure_diagnosis.json`
  - `policy_behavior_audit.csv`
  - `policy_behavior_audit.json`
  - `metric_computation_audit.csv`
  - `metric_computation_audit.json`

## Findings

| severity | finding | evidence | impact |
| --- | --- | --- | --- |
| high | Figure 10 sweeps are real, but the outputs are degenerate and not paper-faithful | `artifacts/feature_089_paper_metrics_catalog/figure_10_output_audit.md`; `artifacts/feature_089_paper_metrics_catalog/figure_10_paper_claim_alignment.md`; sample rows in `figure_10a_delay_vs_arrival_probability.json`, `figure_10b_delay_vs_cpu_capacity.json`, `figure_10d_drop_ratio_vs_arrival_probability.json`, `figure_10e_drop_ratio_vs_cpu_capacity.json`, `figure_10f_drop_ratio_vs_timeout.json` | The paper claim cannot be supported from these results |
| high | Figure 9 is approximation-tagged and not a faithful paper reproduction | `figure_9a_reward_vs_arrival_probability.json`, `figure_9b_action_distribution_vs_arrival_probability.json`; fields `support_status=generated_with_approximation`, `approximation_note=...` | Figure 9 can only be used as current-simulator output |
| high | Figure 8 and Figure 11 are correctly gated because no training/LSTM traces exist | `artifacts/feature_089_paper_metrics_catalog/paper_figures_8_11_catalog.md`; `figure_8a_learning_rate_convergence_status.json`; `figure_8b_discount_factor_convergence_status.json`; `figure_11_lstm_ablation_status.json` | No paper-style learning curve or LSTM ablation claim is possible |
| medium | Metrics are computed from completed-task subsets, which makes degenerate traces look more stable than they are | `src/evaluation/metrics.py:42-88` | Completed-task means hide the fact that many sweeps complete zero tasks |
| medium | The Gym adapter can spend runs with no current task or a single task in flight, so sweeps can collapse into one-task traces | `src/environment/gym_adapter.py:68-241` | The runtime does not robustly exercise the paper workload regime |
| medium | Paper-timeout semantics exist, but that alone does not make the runtime paper-faithful | `src/environment/paper_timeout.py:31-52` | Contract helpers are present, but the end-to-end behavior still diverges |
| medium | Policy adapters exist, but the runtime still does not create paper-like separation between policies | `src/analysis/hoodie_runtime_evaluation_runner/policies.py:79-241`; `src/evaluation/policy_registry.py:17-60` | The policy layer is not the limiting factor by itself, but it is not sufficient to recover paper results |

## Mechanism To Code Mapping

| mechanism | code location | paper expectation | observed state |
| --- | --- | --- | --- |
| traffic generation | `src/environment/traffic_config.py:61-122`, `src/environment/traffic_generator.py:74-128` | Bernoulli arrivals, paper-default workload parameters, variable sweeps | present, but output traces are still too sparse or degenerate |
| deadline handling | `src/environment/paper_timeout.py:31-89` | Paper deadline semantics | present |
| reward timing | `src/environment/reward_timing.py:116-124` | delayed terminal reward | present, but not sufficient for paper-like learning curves |
| policy selection | `src/analysis/hoodie_runtime_evaluation_runner/policies.py:79-241` | distinct policy behaviors and candidate ranking | present, but separation is weak in generated outputs |
| metric aggregation | `src/evaluation/metrics.py:42-88` | summarize completed tasks and drops | present, but can mask zero-completion sweeps |
| environment stepping | `src/environment/gym_adapter.py:179-241` | multi-slot task progression with queue dynamics | present, but often collapses to a single finalized task |

## Figure 10 Audit

Figure 10 is the strongest current-simulator artifact, but it still fails the paper-faithfulness bar.

- The outputs are simulator-generated, not paper values.
- The sweeps are real and the axes are varied, but the numeric outputs are degenerate.
- In the sample rows:
  - `figure_10b_delay_vs_cpu_capacity.json` contains `task_completion_delay_raw=0.0` and `paper_style_delay_for_plotting=-0.0` for the sampled policies.
  - `figure_10d_drop_ratio_vs_arrival_probability.json` contains repeated `task_drop_ratio=1.0` and `task_drop_percent=100.0`.
  - `figure_10e_drop_ratio_vs_cpu_capacity.json` and `figure_10f_drop_ratio_vs_timeout.json` show the same collapse pattern.
- The existing paper claim alignment report already marks Figures 10a, 10b, 10d, 10e, and 10f as `not_supported`, with only 10c described as `partial_directional_only`.

Conclusion: Figure 10 supports a current-simulator output claim, not a paper-reproduction claim.

## Figure 9 Audit

Figure 9 is explicitly approximation-tagged.

- `support_status=generated_with_approximation`
- `approximation_note` states the artifact uses current simulator sweeps, while paper validation uses 200 episodes.
- The rows show low-information traces, including zero-task or one-task sweeps in places.

Conclusion: Figure 9 is acceptable as an approximation-tagged current-simulator artifact, but not as a faithful paper figure.

## Figure 8 and Figure 11 Audit

These are gated/status plots, which is the correct behavior when no real training or LSTM traces exist.

- Figure 8a: gated/status
- Figure 8b: gated/status
- Figure 11: gated/status

Conclusion: gating is correct, and no numeric curves were faked.

## Metrics Audit

The metric functions are straightforward and not obviously buggy on their own.

- `average_delay` only averages completed-task delays.
- `drop_ratio` uses dropped tasks over total tasks.
- `throughput` is the completed count.

That is not a defect by itself, but it does mean sparse traces can look deceptively tidy.

## Simulation-Flow Audit

The environment is queue-based and honors the paper contract helpers, but the current runtime is not producing the paper dynamics.

- `HoodieGymEnvironment.step()` processes a single pending task, then progresses offloading and execution queues.
- If there is no current task and no queue load, reward can become `nan`.
- The trace source is deterministic and bounded by the current generator.

The issue is not that the simulator lacks structure. The issue is that the generated traces and policy/runtime interaction do not produce paper-like load, completion, and ranking behavior.

## Diagnosis

### What is acceptable

- Current simulator outputs exist.
- Figure 8 and Figure 11 are correctly gated.
- Figure 9 is clearly tagged as approximation-based.
- Figure 10 uses simulator outputs rather than fabricated paper values.

### What is not acceptable

- The simulator is not faithful enough to support a paper reproduction claim.
- The figure 10 sweeps are too degenerate to be considered paper-like.
- There is no evidence of real training/LSTM traces for Figures 8 and 11.

## Top 10 Defects

1. Figure 10 policies tie too often to support paper claims.
2. HOODIE and MLEO tie in current Figure 10 outputs.
3. Figure 10b delay collapses to zero or negative-zero.
4. Figure 10d, 10e, and 10f frequently saturate at 100 percent drop ratio.
5. Figure 9 is approximation-tagged, not paper-validated.
6. Figure 9 action distributions do not preserve the paper-like grouping behavior.
7. Figure 8 and Figure 11 remain gated because no real traces exist.
8. Metrics are computed only over completed tasks, which masks sparse-trace collapse.
9. The runtime can finish with one-task or zero-completion traces.
10. The current outputs are usable as current-simulator outputs only, not as paper reproduction evidence.

## Recommended Repair Order

1. Produce real training and LSTM traces before touching figure claims.
2. Fix runtime sweep depth so Figure 10 episodes actually complete enough tasks to separate policies.
3. Verify x-axis sweep injection for CPU and timeout sweeps.
4. Re-run Figure 10 once the runtime produces non-degenerate traces.
5. Rebuild Figure 9 from real validation episodes rather than approximation-tagged outputs.
6. Add explicit deadline-violation and richer completion diagnostics.
7. Revalidate policy distinctness after the runtime outputs are no longer sparse.
8. Recompute metrics on episodes with non-trivial completion counts.
9. Only after that, revisit any paper-claim wording.
10. Keep Figures 8 and 11 gated until their traces actually exist.

## Final Judgment

The repository should describe this as a current-simulator artifact bundle with approximation-tagged Figure 9 and gated Figure 8/11, not as a faithful recreation of the HOODIE paper simulations.

## Audit-Only Confirmation

- No simulator behavior was changed in this audit.
- No policies were modified.
- No reward, queue, environment, training, or evaluation behavior was tuned.
- The current simulator outputs remain usable only as current-simulator outputs.
- They do not support HOODIE paper reproduction claims.
