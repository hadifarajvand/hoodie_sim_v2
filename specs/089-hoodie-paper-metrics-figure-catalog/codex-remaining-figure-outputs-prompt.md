# Codex Prompt: Feature 089 Remaining Figure Outputs

```text
You are working in repository:

/Users/hadi/Documents/GitHub/hoodie_sim_v2

Current branch:

089-hoodie-paper-metrics-figure-catalog

Goal:

Complete the remaining output artifacts in Feature 089 on the same branch. Do not create a new feature or branch.

The goal is output availability from our simulator, not forcing the outputs to match the HOODIE paper plots.

Hard rule:
Do not tune, edit, bias, or reshape simulator/model/policy/reward/queue logic to make outputs look closer to the paper. If any previous or current change attempts output-sync tuning, report it explicitly and revert or isolate it. Allowed changes are sweep runners, artifact writers, validators, and plot-ready output formatting only.

Source-of-truth files:
- specs/089-hoodie-paper-metrics-figure-catalog/remaining-figure-output-implementation-handoff.md
- specs/089-hoodie-paper-metrics-figure-catalog/paper-figures-8-9-extracted.md
- specs/089-hoodie-paper-metrics-figure-catalog/paper-metrics-extracted.md
- specs/089-hoodie-paper-metrics-figure-catalog/simulator-output-requirements.md
- specs/089-hoodie-paper-metrics-figure-catalog/figure-10-comparison-analysis-handoff.md

Current accepted state:
- Figure 10a-10f outputs already exist and are validated.
- Figure 10 comparison analysis exists.
- Figure 9a-9e are currently blocked/reference-only and must now be emitted as current-simulator output artifacts where feasible.
- Figure 8a, Figure 8b, and Figure 11 are training/LSTM-gated. Do not fake their curves.

Required work:

1. Audit for output-sync tuning.
   - Inspect Feature 089 changes and relevant runner code.
   - Confirm no model/policy/reward/queue semantics were edited to sync outputs with the paper.
   - If such edits exist, report and revert or isolate them.

2. Implement Figure 9 output artifacts.
   Generate these under `artifacts/feature_089_paper_metrics_catalog/`:
   - `figure_9a_reward_vs_arrival_probability.csv`
   - `figure_9a_reward_vs_arrival_probability.json`
   - `figure_9b_action_distribution_vs_arrival_probability.csv`
   - `figure_9b_action_distribution_vs_arrival_probability.json`
   - `figure_9c_reward_vs_cpu_capacity.csv`
   - `figure_9c_reward_vs_cpu_capacity.json`
   - `figure_9d_reward_vs_agent_count_traffic.csv`
   - `figure_9d_reward_vs_agent_count_traffic.json`
   - `figure_9e_reward_vs_agent_count_data_rate.csv`
   - `figure_9e_reward_vs_agent_count_data_rate.json`

   Required handling:
   - Figure 9a: average_reward vs task arrival probability, HOODIE only. Include P values [0.1,0.3,0.5,0.7,0.9]. Include N=10/15/20 only if supported; otherwise mark unsupported rows honestly.
   - Figure 9b: Local/Horizontal/Vertical action count and share vs P, HOODIE only.
   - Figure 9c: average_reward vs CPU capacity [4,5,6,7,8,9], HOODIE only. Include N=10/15/20 only if supported.
   - Figure 9d: average_reward vs N [10,15,20,25,30] for Moderate/Heavy/Extreme traffic. Mark unsupported cases honestly if the simulator cannot vary N or traffic-size ranges.
   - Figure 9e: average_reward vs N [10,15,20,25,30] for Balanced, Horizontal-centric, Vertical-centric data-rate scenarios. Mark unsupported cases honestly if the simulator cannot vary N or data rates.

   Every Figure 9 row must include:
   - `figure_id`
   - `metric`
   - sweep fields
   - `policy` = HOODIE
   - `value` where generated
   - `support_status`: generated, generated_with_approximation, or not_supported
   - `claim_boundary`
   - `approximation_note`

3. Implement Figure 8 and Figure 11 gated status artifacts.
   Generate:
   - `figure_8a_learning_rate_convergence_status.json`
   - `figure_8a_learning_rate_convergence_status.md`
   - `figure_8b_discount_factor_convergence_status.json`
   - `figure_8b_discount_factor_convergence_status.md`
   - `figure_11_lstm_ablation_status.json`
   - `figure_11_lstm_ablation_status.md`

   If real trained DRL/LSTM traces exist, generate plot-ready outputs from those traces. If not, status must be:
   - Figure 8a: `not_generated_training_required`
   - Figure 8b: `not_generated_training_required`
   - Figure 11: `not_generated_lstm_training_required`

   Do not generate fake training curves from deterministic benchmark rows.

4. Generate final remaining-output report.
   Create:
   - `remaining_figure_outputs_report.json`
   - `remaining_figure_outputs_report.md`

   Include:
   - Figure 10 already implemented and validated.
   - Figure 9 status by subfigure.
   - Figure 8 status.
   - Figure 11 status.
   - no-output-sync-tuning proof.
   - claim boundaries carried forward.
   - final verdict: one of
     - `feature_089_all_feasible_outputs_generated`
     - `feature_089_remaining_outputs_partial`
     - `feature_089_remaining_outputs_blocked`

5. Tests and validation.
   Add or update tests to validate:
   - Figure 9 artifacts exist for 9a-9e.
   - Figure 9 rows include support_status and claim_boundary.
   - Figure 8a/8b/11 gated status files exist.
   - no fake Figure 8/11 curves are emitted when training traces do not exist.
   - Figure 10 validation still passes.

Validation commands:
- `git diff --check`
- `src/.venvmac/bin/python -m unittest tests.unit.test_hoodie_paper_metrics_figure_catalog`
- `src/.venvmac/bin/python -m unittest tests.integration.test_hoodie_paper_metrics_figure_catalog_report`
- `src/.venvmac/bin/python -m analysis.hoodie_paper_metrics_figure_catalog --generate-artifacts --validate-artifacts --artifact-dir artifacts/feature_089_paper_metrics_catalog`

Commit message:
`Add Feature 089 remaining figure outputs`

Final response must include:
- branch name
- final commit SHA
- files changed
- commands run and results
- Figure 9 generated/partial/not_supported status by subfigure
- Figure 8a/8b status
- Figure 11 status
- final verdict
- explicit confirmation that no output-sync tuning was performed
```
```