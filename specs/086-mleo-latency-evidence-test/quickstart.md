# Quickstart: Feature 086 Full System-Model Fidelity Gate

## Pull Branch

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
git fetch origin
git checkout 086-mleo-latency-evidence-test
git pull --ff-only origin 086-mleo-latency-evidence-test
```

## Important Current State

This branch already contains an implementation pass that added MLEO numeric evidence and HOODIE/MLEO tie evidence. That work is valid but partial.

The next Codex run must complete the **full HOODIE system-model fidelity gate**. Do not stop at MLEO evidence again.

## Codex Implementation Prompt

```text
You are working in repository:

/Users/hadi/Documents/GitHub/hoodie_sim_v2

Current branch:

086-mleo-latency-evidence-test

Goal:

Complete Feature 086 as the HOODIE System-Model Fidelity Gate before output comparison.

The branch already contains a successful partial implementation:
- MLEO numeric non-queue-only evidence exists.
- MLEO selected the minimum estimated total-delay candidate in a controlled test.
- HOODIE/MLEO aggregate tie is documented at action/scenario level in the Feature 085 audit report/manifest.

Preserve that work. Do not redo Feature 086 as only an MLEO test. The remaining task is the full Chapter/System-Model fidelity gate.

Strict scope:
- Do not introduce the user's thesis method.
- Do not introduce DCQ.
- Do not introduce a custom queue redesign.
- Do not introduce any new proposed method.
- Do not claim full empirical reproduction of the HOODIE paper unless trained DRL, trained LSTM/forecast behavior, topology, stochastic traffic, and paper figures/results are actually reproduced and validated.

Canonical policy rules:
- HOODIE is the only proposed paper method.
- Active policies must be exactly: HOODIE, RO, FLC, VO, HO, BCO, MLEO.
- MLEO means Minimum Latency Estimation Offloader.
- MLEO must choose minimum estimated total delay, not minimum queue length.
- Active outputs must not contain: MQO, Minimum Queue Offloader, ORIGINAL_HOODIE_BASELINE, HOODIE_PROPOSED.
- Historical invalid-label notes are allowed only inside Spec Kit documentation.

Paper sources:
- Read `resources/papers/hoodie/ocr/merged.txt`.
- Use `resources/papers/hoodie/original/HOODIE_paper.pdf` only if OCR is ambiguous for formula/table/figure extraction.

Relevant implementation areas:
- `src/analysis/hoodie_runtime_evaluation_runner/`
- `src/analysis/hoodie_proposed_method/`
- `src/policies/`
- `tests/unit/`
- `tests/integration/`
- `artifacts/feature_085_full_audit/`
- `specs/086-mleo-latency-evidence-test/`

Required system-model mechanisms to audit, map, and validate:

1. Three-tier topology: task source / IoT or MD layer, Edge Agents, Cloud.
2. Edge Agent set and Cloud node representation.
3. Horizontal EA-to-EA connectivity and destination legality.
4. Vertical EA-to-cloud path.
5. Task model: task ID, input/data size, processing density or CPU demand, timeout/deadline, arrivals/workload.
6. Queue model: private/local queue, offloading queue, public/cloud queue.
7. Delay model: local execution delay, horizontal transmission delay, vertical transmission delay, remote edge execution delay, cloud execution delay, waiting time, completion time.
8. Drop model: timeout drop, deadline violation, unavailability if represented, illegal action rejection.
9. Action model: local, horizontal offload, vertical offload, and the two-stage decision boundary or a documented single-stage approximation.
10. Policy model: HOODIE, RO, FLC, VO, HO, BCO, MLEO.
11. Reward/cost model and exact/approximate claim boundary.
12. Output metric readiness for paper comparison.

Use exactly these status labels:
- exact
- approximate_documented
- missing
- wrong
- not_exercised

Blocking rules:
- missing blocks readiness.
- wrong blocks readiness.
- not_exercised blocks readiness.
- approximate_documented is acceptable only when the approximation is explicit, conservative, and exercised by tests/scenarios/artifacts.

Implementation requirements:

1. Complete the system-model gap matrix.
   Update `specs/086-mleo-latency-evidence-test/system-model-gap-matrix.md`.
   Replace generic placeholders with concrete rows that include:
   - paper mechanism
   - paper expectation
   - simulator behavior
   - code location
   - test/artifact evidence
   - status
   - required fix or claim boundary

2. Complete the metric readiness matrix.
   Update `specs/086-mleo-latency-evidence-test/metric-readiness-matrix.md`.
   Classify every metric as one of:
   - paper_primary_metric
   - paper_secondary_or_derived_metric
   - paper_secondary_or_repository_metric
   - repository_diagnostic_metric
   - not_for_paper_comparison

   Required metrics:
   - task_completion_delay
   - task_drop_ratio
   - completion_rate
   - timeout_drop_rate
   - unavailable_drop_rate
   - deadline_violation_rate
   - average_reward
   - total_reward
   - throughput
   - queue_stability_score
   - illegal_action_rejection_count

   Do not use repository diagnostics as paper headline metrics.

3. Add or repair tests/evidence for all required mechanisms.
   Required evidence must cover:
   - local execution path
   - horizontal offloading path
   - vertical/cloud path
   - horizontal destination legality / illegal rejection
   - timeout/drop behavior
   - private/local queue timing
   - offloading/public/cloud queue behavior, or explicit documented approximation
   - active policy exact set
   - absence of legacy active labels
   - existing MLEO numeric evidence remains passing

4. Generate Feature 086 artifact directory:

   `artifacts/feature_086_system_model_fidelity/`

   Required files:
   - `mechanism_coverage.json`
   - `mechanism_coverage.csv`
   - `system_model_gap_matrix.json`
   - `system_model_gap_matrix.md`
   - `metric_readiness_matrix.json`
   - `metric_readiness_matrix.md`
   - `scenario_mechanism_coverage.json`
   - `hoodie_mleo_tie_evidence.json`
   - `feature_086_system_model_fidelity_report.json`
   - `feature_086_system_model_fidelity_report.md`

5. Final report requirement.
   The final Feature 086 report must declare exactly one of:
   - `system_model_fidelity_ready_for_output_comparison`
   - `system_model_fidelity_blocked`

   If blocked, list exact blocking mechanisms.
   If ready, list remaining approximations.

   The report must also include:
   - active policy set
   - invalid-label check
   - mechanism coverage summary
   - scenario mechanism coverage summary
   - metric readiness summary
   - allowed paper-comparison metrics
   - repository diagnostic metrics
   - HOODIE/MLEO tie evidence summary
   - no-thesis/no-DCQ/no-custom-method scope proof
   - claim boundary for interface-only DRL/LSTM/forecast components

6. Update Spec Kit files.
   Update these files to reflect implementation evidence:
   - `specs/086-mleo-latency-evidence-test/spec.md`
   - `specs/086-mleo-latency-evidence-test/plan.md`
   - `specs/086-mleo-latency-evidence-test/tasks.md`
   - `specs/086-mleo-latency-evidence-test/contracts/validation-rules.md`
   - `specs/086-mleo-latency-evidence-test/system-model-gap-matrix.md`
   - `specs/086-mleo-latency-evidence-test/metric-readiness-matrix.md`
   - `specs/086-mleo-latency-evidence-test/checklists/requirements.md`
   - `specs/086-mleo-latency-evidence-test/checklists/scope.md`
   - `specs/086-mleo-latency-evidence-test/implementation-handoff.md`
   - `specs/086-mleo-latency-evidence-test/quickstart.md`

   Mark tasks complete only when implementation/test/artifact evidence exists.

Validation commands to run:

- `git diff --check`
- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_*mleo*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'`
- `src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit`
- Run the Feature 086 artifact generation command you create or reuse.
- Run the Feature 086 artifact validation command you create or reuse.

Run grep validation:

`git grep -n "MQO\|Minimum Queue Offloader\|ORIGINAL_HOODIE_BASELINE\|HOODIE_PROPOSED" -- . ':!specs/086-mleo-latency-evidence-test'`

This must return no active code/artifact/report hits.

Commit all changes with:

`Implement Feature 086 HOODIE system model fidelity gate`

Final response must include:
- branch name
- final commit SHA
- files changed
- exact commands run and results
- generated Feature 086 artifact paths
- final readiness verdict
- whether we can proceed to paper output comparison
- blocked mechanisms, if any
- remaining approximations
- allowed paper-comparison metrics
- repository diagnostic metrics
- HOODIE/MLEO tie explanation
- confirmation that no thesis/DCQ/custom method was added
```
