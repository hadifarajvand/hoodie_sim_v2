# Feature 089 Figure 10 Comparison Analysis Handoff

## Decision

Continue on the same branch:

`089-hoodie-paper-metrics-figure-catalog`

Do not create Feature 090. Do not create a new branch.

## Current Accepted State

Feature 089 has completed the following:

- Figure 8-11 paper figure catalog exists.
- Figure 10a-10f are the only `ready_now` simulator-generated outputs.
- Figure 10a-10f output audit passed.
- Figure 10 rows audited: 266.
- Raw positive delay is preserved.
- Paper-style negative delay is preserved.
- Drop ratio and percent are preserved.
- Figure 9a-9e remain blocked/reference-only.
- Figure 8a, Figure 8b, and Figure 11 remain future-required / training-LSTM-gated.

## Next Goal

Use the validated Figure 10 output artifacts to produce same-feature comparison analysis against the HOODIE paper's Figure 10 claims.

This step should analyze:

- Figure 10a: delay vs task arrival probability
- Figure 10b: delay vs CPU computation capacity
- Figure 10c: delay vs task timeout
- Figure 10d: drop ratio vs task arrival probability
- Figure 10e: drop ratio vs CPU computation capacity
- Figure 10f: drop ratio vs task timeout

The output must focus on trend/ranking/qualitative agreement unless paper values are explicitly available or digitized with a documented method.

## Required Analysis Questions

For each Figure 10 subfigure:

1. Does HOODIE rank best, near-best, tied, or not-best among policies?
2. Does MLEO tie with HOODIE or diverge?
3. Does the simulator reproduce the paper's qualitative claim?
4. Does the sweep trend match the paper claim?
5. Which baseline is worst or among the worst?
6. Are there contradictions with the paper text?
7. Are numeric differences unavailable because the paper figure values were not digitized?
8. Does the result require Feature 088 approximation repair before stronger claims?

## Paper Claims To Compare Against

Use the paper text and Figure 10 captions as qualitative reference:

- Figure 10a: HOODIE should achieve lower average delay across task arrival probability sweeps; MLEO is strong but should fall behind HOODIE at high load.
- Figure 10d: HOODIE should achieve the lowest drop ratio across task arrival probability sweeps; FLC and HO are weak at high load; MLEO is competitive but struggles in extreme conditions.
- Figure 10b: increasing CPU capacity should generally reduce average delay; HOODIE should remain better than baselines.
- Figure 10e: increasing CPU capacity should generally reduce drop ratio; HOODIE should show strong reduction, especially at low CPU capacity.
- Figure 10c: increasing timeout from 9.6 to 10.4 sec should slightly improve average delay; HOODIE should remain lower-delay than baselines.
- Figure 10f: increasing timeout from 1.6 to 2.4 sec should reduce drop ratio; HOODIE should maintain the lowest drop ratio.

## Required Artifacts

Add or update files under:

`artifacts/feature_089_paper_metrics_catalog/`

Required machine-readable artifacts:

- `figure_10_trend_analysis.json`
- `figure_10_ranking_analysis.json`
- `figure_10_paper_claim_alignment.json`
- `figure_10_comparison_analysis_report.json`

Required human-readable artifacts:

- `figure_10_trend_analysis.md`
- `figure_10_ranking_analysis.md`
- `figure_10_paper_claim_alignment.md`
- `figure_10_comparison_analysis_report.md`

Optional but preferred plot-ready artifacts:

- `figure_10a_plot_ready.csv`
- `figure_10b_plot_ready.csv`
- `figure_10c_plot_ready.csv`
- `figure_10d_plot_ready.csv`
- `figure_10e_plot_ready.csv`
- `figure_10f_plot_ready.csv`

## Required Final Verdict

Use exactly one:

- `figure_10_comparison_analysis_ready`
- `figure_10_comparison_analysis_partial`
- `figure_10_comparison_analysis_blocked`

Use `partial` if paper numeric values are not digitized and the comparison is trend/ranking/qualitative only.

## Scope Guard

- Do not create a new branch.
- Do not create a new feature.
- Do not modify HOODIE or baseline policy semantics.
- Do not introduce thesis method.
- Do not introduce DCQ.
- Do not redesign queues.
- Do not claim full empirical paper reproduction.
- Carry Feature 086 system-model approximation boundaries.
- Carry Feature 080 training/LSTM claim boundaries.
- Keep Figure 9 blocked/reference-only unless actual support is added and validated.
- Keep Figure 8 and Figure 11 future-required unless trained DRL/LSTM artifacts exist.

## Validation Requirements

The implementation must validate:

- all six Figure 10 output files exist;
- every Figure 10 subfigure has all seven policies: HOODIE, RO, FLC, VO, HO, BCO, MLEO;
- trend analysis exists for each Figure 10 subfigure;
- ranking analysis exists for each Figure 10 subfigure;
- paper claim alignment exists for each Figure 10 subfigure;
- delay analyses use paper-style negative delay for paper-facing ranking, while preserving raw positive delay;
- drop analyses use both raw ratio and percent;
- report states whether paper numeric digitization was performed or not.
