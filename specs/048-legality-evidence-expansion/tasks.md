# Tasks: Legality Evidence Expansion

## Phase 1: Prerequisite Gates

- [X] T001 Verify the current branch is `048-legality-evidence-expansion`, the branch is not `main`, `main` matches `origin/main`, `main` matches `047-exposure-matrix-review-complete^{}`, and the diff from `047-exposure-matrix-review-complete^{}` to `main` is empty.
- [X] T002 Verify `.specify/feature.json` is not staged or committed, `AGENTS.md` is clean before report generation, `AGENTS.md` is not added to `.gitignore`, and there are no unrelated dirty files.

## Phase 2: Prior Feature Gates

- [X] T003 Verify committed artifacts exist for Feature 037 baseline revalidation.
- [X] T004 Verify committed artifacts exist for Feature 038 training foundation contract.
- [X] T005 Verify committed artifacts exist for Feature 039 network implementation.
- [X] T006 Verify committed artifacts exist for Feature 040 smoke training.
- [X] T007 Verify committed artifacts exist for Feature 041 full-training campaign gate.
- [X] T008 Verify committed artifacts exist for Feature 042 terminal exposure.
- [X] T009 Verify committed artifacts exist for Feature 043 completion lifecycle audit.
- [X] T010 Verify committed artifacts exist for Feature 044 passive lifecycle trace instrumentation.
- [X] T011 Verify committed artifacts exist for Feature 045 completion root-cause analysis.
- [X] T012 Verify committed artifacts exist for Feature 046 load/admission/action exposure review.
- [X] T013 Verify committed artifacts exist for Feature 047 exposure matrix review.

## Phase 3: Config and Schema Foundations

- [X] T014 Define `LegalityEvidenceConfig` with `feature_id`, `episode_length`, `timeout_slots`, `node_count`, `arrival_probability`, `seeds`, `strategies`, `no_runtime_repair`, `no_training`, and `passive_legality_capture`, and validate the paper-default grid.
- [X] T015 Define `LegalitySnapshot` with the required passive legality fields, schema version, and unavailable/null handling rules.
- [X] T016 Define `LegalityEvidenceRecord` so each decision opportunity can hold the snapshot payload, evidence source, and capture metadata without changing runtime behavior.
- [X] T017 Define `BehaviorEquivalenceCheck` so capture-enabled runs can be compared against no-legality-capture baselines using the same seeds, strategies, and paper-default config.
- [X] T018 Define `LegalityEvidenceReport` with all required report fields, verdict routing, and null/unavailable semantics for missing evidence.

## Phase 4: Passive Evidence Capture

- [X] T019 Implement passive legality evidence collection over the full strategy/seed grid, ensuring each decision opportunity can emit a legality snapshot only when evidence is available.
- [X] T020 Extend the passive lifecycle trace schema only if needed to carry legality snapshots without changing action legality, action selection, reward, timeout, capacity, or transmission semantics.
- [X] T021 Extend the environment adapter only if needed to surface passive legality snapshots from existing runtime info masks or helpers without changing runtime behavior.
- [X] T022 Add evidence-source selection logic that prefers an existing runtime action mask, then an existing public legality helper, then a passive trace snapshot, and otherwise marks evidence unavailable.
- [X] T023 Add full-population coverage tracking by strategy and seed, and explicitly distinguish aggregate legality evidence from representative examples.

## Phase 5: Legality Metrics

- [X] T024 Compute legality snapshot coverage, decision-opportunity counts, and legal-evidence coverage ratio from the full population when evidence exists.
- [X] T025 Derive `selected_was_legal` and the selected-illegal-action metrics from captured legality evidence only, never from `lifecycle_trace_sample`.
- [X] T026 Compute `selected_illegal_action_count`, `selected_illegal_local_count`, `selected_illegal_horizontal_count`, `selected_illegal_vertical_count`, `selected_illegal_action_rate`, and `selected_illegal_action_examples` with full-population evidence when available.
- [X] T027 Compute per-action legal counts, selected counts, and legal-but-unselected counts for local, horizontal, and vertical actions.
- [X] T028 Build the action-mask summary, selected-illegal-action summary, and per-strategy/seed legality coverage outputs from the computed legality metrics.
- [X] T029 Add null/unavailable handling for missing legality evidence so the report never synthesizes fake zeros for illegal selections or legal counts.

## Phase 6: Behavior Equivalence

- [X] T030 Implement capture-vs-baseline behavior-equivalence checks for selected action sequence, rewards, terminal outcomes, queue progression, timeout/deadline outcomes, transmission outcomes, and execution progress counts.
- [X] T031 Add a failure mode for any behavior drift detected while legality capture is enabled, including drift in selected actions, rewards, queue progression, terminal outcomes, or timing behavior.
- [X] T032 Add tests that compare capture-enabled runs against no-legality-capture baselines using the same seeds, strategies, and paper-default configuration.

## Phase 7: Report Generation

- [X] T033 Implement the JSON and Markdown report writers for `artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json` and `.md`.
- [X] T034 Require both copies of `legal_evidence_coverage_ratio` in `specs/048-legality-evidence-expansion/spec.md`, `specs/048-legality-evidence-expansion/contracts/legality-evidence-report-schema.md`, and `specs/048-legality-evidence-expansion/data-model.md`, including `report.legal_evidence_coverage_ratio` and `report.legality_evidence_coverage_summary.legal_evidence_coverage_ratio` as non-optional machine-readable fields that must equal each other and must not be implied through prose.
- [X] T035 Validate `legal_evidence_coverage_ratio` semantics in `specs/048-legality-evidence-expansion/spec.md`, `specs/048-legality-evidence-expansion/contracts/legality-evidence-report-schema.md`, and `specs/048-legality-evidence-expansion/data-model.md`, including `legal_evidence_coverage_ratio = legality_snapshot_count / decision_opportunity_count`, `0.0` when known opportunities have no snapshots, and `null` when the denominator is zero.
- [X] T036 Encode verdict routing so full legality coverage plus passing behavior equivalence routes to `legality_evidence_ready_for_exposure_matrix_rerun`, partial coverage routes to `legality_evidence_partial_requires_trace_depth_expansion`, unavailable evidence routes to `legality_evidence_unavailable_requires_runtime_public_helper`, and behavior drift routes to `behavior_drift_detected`.
- [X] T037 Ensure the report explicitly states whether Feature 049 can rerun the exposure matrix with legality evidence.
- [X] T038 Fail the report generation or validation path if `legal_evidence_coverage_ratio` or `legality_evidence_coverage_summary.legal_evidence_coverage_ratio` is missing, only implied in prose, or contradicts `selected_illegal_action_count`, `selected_illegal_action_evidence_status`, or the Feature 049 routing decision.

## Phase 8: Tests

- [X] T039 Add schema tests that require the report schema fields, the legality snapshot schema, the config grid, the top-level `legal_evidence_coverage_ratio` field, the nested `legality_evidence_coverage_summary.legal_evidence_coverage_ratio` field, and the null/unavailable rules, including `test_report_requires_top_level_legal_evidence_coverage_ratio`, `test_coverage_summary_repeats_legal_evidence_coverage_ratio`, `test_report_fails_if_summary_coverage_ratio_missing`, and `test_report_fails_if_top_level_and_summary_coverage_ratio_contradict`.
- [X] T040 Add metrics tests that verify legality coverage, `legal_evidence_coverage_ratio` derivation, selected-illegal-action derivation, denominator rules, representative-example separation, and per-action legality counts, including `test_coverage_ratio_zero_when_known_opportunities_have_no_snapshots`, `test_coverage_ratio_null_when_decision_opportunity_count_zero`, `test_feature_049_not_recommended_when_coverage_ratio_zero`, `test_feature_049_not_recommended_when_coverage_ratio_null`, `test_coverage_ratio_not_prose_only`, and `test_final_verdict_matches_legal_evidence_coverage_ratio`.
- [X] T041 Add behavior-equivalence tests that assert capture-enabled and baseline runs produce the same selected actions, rewards, terminal outcomes, queue progression, timeout/deadline outcomes, transmission outcomes, and execution progress counts.
- [X] T042 Add integration tests that validate the end-to-end legality-evidence pipeline, report generation, Feature 049 routing logic, committed-artifact Feature 047 prerequisite checks, and rejection of Feature 049 routing when `legal_evidence_coverage_ratio` is insufficient.
- [X] T043 Add scope-guard tests that reject runtime repair, policy changes, dependency changes, training, optimizer, replay training, target updates, fake legality evidence, fake zero legal counts, curve fitting, simulator-output tuning, and paper reproduction claims.

## Phase 9: Validation and Cleanup

- [X] T044 Add or update the quickstart and validation instructions to use the approved interpreter, the Feature 048 unittest bundle, and safe prior-artifact checks only.
- [X] T045 Verify the validation command excludes dirty-worktree-sensitive older report tests such as `tests.unit.test_exposure_matrix_schema` while still covering the committed Feature 047 artifact checks and the safe regression suite.
- [X] T046 Run the approved validation command and confirm the Feature 048 tests pass without modifying any forbidden paths or runtime semantics.
- [X] T047 Mark the Feature 048 implementation tasks complete only after the report artifacts are regenerated, the tests pass, and the scope guard confirms no unrelated files changed.
