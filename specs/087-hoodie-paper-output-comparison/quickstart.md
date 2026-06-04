# Quickstart: Feature 087 HOODIE Paper Output Comparison

## Pull Branch

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
git fetch origin
git checkout 087-hoodie-paper-output-comparison
git pull --ff-only origin 087-hoodie-paper-output-comparison
```

## Codex Implementation Prompt

```text
You are working in repository:

/Users/hadi/Documents/GitHub/hoodie_sim_v2

Current branch:

087-hoodie-paper-output-comparison

Goal:

Implement Feature 087: compare the repository's HOODIE simulator outputs against the HOODIE paper's reported evaluation outputs.

This feature starts after Feature 086 declared `system_model_fidelity_ready_for_output_comparison`. Carry forward all Feature 086 approximations as claim boundaries. Do not claim exact full empirical reproduction unless evidence proves it.

Strict scope:
- Do not introduce the user's thesis method.
- Do not introduce DCQ.
- Do not introduce a custom queue redesign.
- Do not introduce a new proposed method.
- Do not change HOODIE algorithm semantics unless a verified output-comparison bug is found and documented.
- Do not claim full empirical reproduction of the HOODIE paper unless exact training, stochastic workload, topology, and paper figures are reproduced and validated.

Canonical active policies:
- HOODIE
- RO
- FLC
- VO
- HO
- BCO
- MLEO

Invalid active labels:
- MQO
- Minimum Queue Offloader
- ORIGINAL_HOODIE_BASELINE
- HOODIE_PROPOSED

Paper sources:
- Read `resources/papers/hoodie/ocr/merged.txt`.
- Use `resources/papers/hoodie/original/HOODIE_paper.pdf` for ambiguous OCR, figures, tables, captions, and numeric values.

Feature 086 boundary sources:
- `reports/feature_086_system_model_fidelity_final_review.md`
- `artifacts/feature_086_system_model_fidelity/feature_086_system_model_fidelity_report.json`
- `artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.json`
- `artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.json`

Required work:

1. Extract paper outputs.
   - Extract all paper evaluation figures, tables, captions, metrics, policies, x-axis variables, scenario parameters, and qualitative claims.
   - Record source location and extraction confidence.
   - Numeric values may be compared only if explicitly reported or carefully digitized with an approximation label.
   - Create `specs/087-hoodie-paper-output-comparison/paper-output-extraction-matrix.md`.

2. Inventory simulator outputs.
   - Inspect `artifacts/feature_085_full_audit/` and `artifacts/feature_086_system_model_fidelity/`.
   - Regenerate simulator outputs if needed.
   - Confirm active policy set is exactly HOODIE, RO, FLC, VO, HO, BCO, MLEO.
   - Create `specs/087-hoodie-paper-output-comparison/simulator-output-inventory.md`.

3. Align metrics.
   - Use approved paper-comparison metrics: task_completion_delay, task_drop_ratio, completion_rate, average_reward, total_reward, throughput.
   - Keep diagnostics separate: timeout_drop_rate, unavailable_drop_rate, deadline_violation_rate, queue_stability_score, illegal_action_rejection_count.
   - Create `specs/087-hoodie-paper-output-comparison/metric-alignment-matrix.md`.

4. Compare outputs.
   - For each comparable paper output, compute simulator value, paper value/reference, absolute difference, relative difference where meaningful, ranking agreement, and qualitative agreement.
   - Mark each row as aligned, partially_aligned, divergent, or not_comparable.

5. Generate artifacts under:

   `artifacts/feature_087_paper_output_comparison/`

   Required files:
   - `paper_output_extraction.json`
   - `paper_output_extraction.md`
   - `simulator_output_inventory.json`
   - `simulator_output_inventory.md`
   - `metric_alignment_matrix.json`
   - `metric_alignment_matrix.md`
   - `comparison_by_metric.json`
   - `comparison_by_metric.csv`
   - `comparison_by_policy.json`
   - `comparison_by_policy.csv`
   - `figure_comparison_coverage.json`
   - `ranking_agreement.json`
   - `feature_087_paper_output_comparison_report.json`
   - `feature_087_paper_output_comparison_report.md`

6. Final report.
   - Include Feature 086 approximation boundary.
   - Include comparable and non-comparable paper outputs.
   - Include numeric differences where possible.
   - Include ranking agreement.
   - Include qualitative agreement/disagreement.
   - Separate paper metrics from repository diagnostics.
   - Declare exactly one verdict: paper_output_comparison_ready, paper_output_comparison_partial, or paper_output_comparison_blocked.
   - Do not overclaim full reproduction.

7. Tests and validation.
   - Add tests for extraction schema, metric alignment, comparison artifact schema, and claim-boundary enforcement.
   - Validate Feature 085 artifacts.
   - Validate Feature 086 artifacts.
   - Generate and validate Feature 087 artifacts.

Validation commands:
- `git diff --check`
- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_*output_comparison*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_*output_comparison*.py'`
- `src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit`
- `src/.venvmac/bin/python -m analysis.hoodie_system_model_fidelity_gate --validate-artifacts --artifact-dir artifacts/feature_086_system_model_fidelity`
- Run or create Feature 087 artifact generation and validation commands.

Commit message:
`Implement Feature 087 HOODIE paper output comparison`

Final response must include:
- branch name
- final commit SHA
- files changed
- commands run and results
- generated artifact paths
- final verdict
- comparable paper outputs
- non-comparable paper outputs
- allowed metrics used
- diagnostics kept separate
- remaining limitations
```
