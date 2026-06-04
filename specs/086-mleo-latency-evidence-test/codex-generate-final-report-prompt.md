# Codex Prompt: Generate and Push Feature 086 Final Review Report

Use this prompt when you want Codex to generate a concise but complete review/report file from the committed Feature 086 artifacts and push it to the repository. Do not manually paste long terminal output into chat.

```text
You are working in repository:

/Users/hadi/Documents/GitHub/hoodie_sim_v2

Current branch:

086-mleo-latency-evidence-test

Goal:

Generate a committed Feature 086 final review report from the repository artifacts, tests, and Spec Kit files, then commit and push it. The report must be repository-backed and must not be a loose chat summary.

Important context:

Feature 086 is the HOODIE System-Model Fidelity Gate before paper-output comparison.

The latest implementation reports:
- Branch: 086-mleo-latency-evidence-test
- Commit: b3f68c971f4eb0caa5c46be6e4bbbd99d6741128
- Commit message: Implement Feature 086 HOODIE system model fidelity gate
- Final verdict: system_model_fidelity_ready_for_output_comparison
- Feature 086 artifacts are under: artifacts/feature_086_system_model_fidelity/

Critical rules:

1. Do not introduce thesis method, DCQ, custom queue redesign, or a new proposed method.
2. Do not claim full empirical HOODIE paper reproduction.
3. HOODIE remains the only proposed paper method.
4. Active policies must remain exactly: HOODIE, RO, FLC, VO, HO, BCO, MLEO.
5. MLEO means Minimum Latency Estimation Offloader.
6. MQO / Minimum Queue Offloader / ORIGINAL_HOODIE_BASELINE / HOODIE_PROPOSED must not be treated as active paper-fidelity policies.
7. Historical legacy-label grep noise must be reported honestly if it exists outside the Feature 086 surface.

Read these source files before writing the report:

- specs/086-mleo-latency-evidence-test/spec.md
- specs/086-mleo-latency-evidence-test/plan.md
- specs/086-mleo-latency-evidence-test/tasks.md
- specs/086-mleo-latency-evidence-test/system-model-gap-matrix.md
- specs/086-mleo-latency-evidence-test/metric-readiness-matrix.md
- specs/086-mleo-latency-evidence-test/contracts/validation-rules.md
- specs/086-mleo-latency-evidence-test/implementation-handoff.md
- artifacts/feature_086_system_model_fidelity/feature_086_system_model_fidelity_report.json
- artifacts/feature_086_system_model_fidelity/feature_086_system_model_fidelity_report.md
- artifacts/feature_086_system_model_fidelity/mechanism_coverage.json
- artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.json
- artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.json
- artifacts/feature_086_system_model_fidelity/scenario_mechanism_coverage.json
- artifacts/feature_086_system_model_fidelity/hoodie_mleo_tie_evidence.json
- artifacts/feature_085_full_audit/feature_085_audit_report.md
- artifacts/feature_085_full_audit/execution_manifest.json

Create this new report file:

reports/feature_086_system_model_fidelity_final_review.md

The report must include these sections exactly:

1. Title
   - `# Feature 086 Final Review: HOODIE System-Model Fidelity Gate`

2. Repository State
   Include:
   - branch name
   - current HEAD SHA from `git rev-parse HEAD`
   - remote HEAD SHA from `git rev-parse origin/086-mleo-latency-evidence-test`
   - whether local/remote SHAs match
   - clean tree proof from `git status --short`

3. Verdict
   Include:
   - final readiness verdict from the Feature 086 report
   - whether the simulator may proceed to paper-output comparison
   - whether any blocking gaps remain

4. Scope Boundary
   State clearly:
   - no thesis method
   - no DCQ
   - no custom queue redesign
   - no new proposed method
   - no full empirical paper reproduction claim
   - HOODIE remains the paper proposed method boundary

5. Active Policy Set
   Include the exact active policy set:
   - HOODIE
   - RO
   - FLC
   - VO
   - HO
   - BCO
   - MLEO

   State that MQO is not an active paper-fidelity baseline.

6. System-Model Mechanism Coverage
   Summarize coverage from mechanism_coverage.json and system_model_gap_matrix.json.
   Include a markdown table with columns:
   - mechanism
   - status
   - evidence
   - remaining approximation / claim boundary

   Do not hide approximations. If many mechanisms are approximate_documented, say so directly.

7. Remaining Approximations
   Include the remaining approximations from the final report, especially:
   - three-tier topology
   - edge agent/cloud representation
   - horizontal legality model
   - vertical cloud path
   - task/workload approximation
   - queue behavior approximation
   - local/offloading/public queue evidence-layer modeling
   - local/horizontal/vertical delay evidence-layer modeling
   - waiting/completion timing approximation
   - timeout/drop semantics approximation
   - two-stage decision boundary approximation
   - reward/cost boundary approximation

   Explain that these are accepted for moving to output comparison only as documented approximations, not full empirical reproduction.

8. Metric Readiness
   Summarize metric_readiness_matrix.json.
   Include two lists:
   - Allowed paper-comparison metrics:
     - task_completion_delay
     - task_drop_ratio
     - completion_rate
     - average_reward
     - total_reward
     - throughput
   - Repository diagnostic metrics:
     - timeout_drop_rate
     - unavailable_drop_rate
     - deadline_violation_rate
     - queue_stability_score
     - illegal_action_rejection_count

   If any metric has caveats, include them.

9. HOODIE/MLEO Tie Evidence
   Summarize hoodie_mleo_tie_evidence.json.
   Include:
   - HOODIE/MLEO match count: 1080 of 1512 rows
   - divergence count: 432 rows
   - identical-action scenarios
   - divergent scenarios
   - divergent action pair: vertical->local x216 in each divergent scenario, if confirmed by the artifact
   - state that aggregate metrics still tie exactly, so this is a metric-level tie, not action-level identity

10. Test and Validation Evidence
    Run and include results for:

    - `git diff --check`
    - `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'`
    - `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_*mleo*.py'`
    - `src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'`
    - `src/.venvmac/bin/python -m unittest tests.unit.test_hoodie_system_model_fidelity_gate`
    - `src/.venvmac/bin/python -m unittest tests.integration.test_hoodie_system_model_fidelity_gate_report`
    - `src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit`
    - `src/.venvmac/bin/python -m analysis.hoodie_system_model_fidelity_gate --validate-artifacts --artifact-dir artifacts/feature_086_system_model_fidelity`

    Include pass/fail and test counts where available.

11. Legacy Label Caveat
    Run:

    `git grep -n "MQO\|Minimum Queue Offloader\|ORIGINAL_HOODIE_BASELINE\|HOODIE_PROPOSED" -- . ':!specs/086-mleo-latency-evidence-test'`

    If it returns hits, summarize them as historical surfaces / compatibility shims only if that is accurate. Do not pretend the repo-wide grep is clean if it is not.

12. Output Comparison Next Step
    State the next step:
    - start paper-output comparison feature only after this final report is accepted
    - compare simulator outputs against paper outputs using only allowed metrics
    - keep repository diagnostics separate from paper metrics

13. Final Conclusion
    Give a concise conclusion:
    - Feature 086 is ready for paper-output comparison if validation passes and no blocking mechanisms remain
    - remaining approximations are documented and must be carried into the output-comparison claim boundary

Report style:

- Be direct and strict.
- Do not overclaim.
- Prefer evidence from artifacts over prose.
- Keep it readable but complete.
- This is a repository report, not a chat response.

After writing the report:

1. Run markdown sanity check manually by reading the file.
2. Run the validation commands above.
3. Commit the new report file with:

   `Add Feature 086 final review report`

4. Push to origin:

   `git push origin 086-mleo-latency-evidence-test`

Final response back to the user must include only:

- branch name
- final commit SHA
- report path
- commands run and pass/fail summary
- whether the report says we can proceed to paper-output comparison
- any blocking issues, if any
```
