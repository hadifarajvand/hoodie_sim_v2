# Feature 064 — Final Review and Release Gate Batch

## Batch rule

This feature batches the final release control items into one implementation feature.

Covered items:

1. Final Repository State Audit
2. Final Artifact Completeness Gate
3. Final Claim Boundary Review
4. Release Tag Readiness Package
5. Final Handoff and Next-Work Recommendation

## Purpose

Perform the final release gate for the implemented HOODIE-style simulation/mechanism pipeline. This feature must validate that the repository is ready for a release tag or final handoff without adding new experiments, changing prior artifacts, inflating claims, or rerunning training.

## Required prior inputs

- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-experiment-integrity-audit.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/reproducibility-package.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-artifact-index.json`

## Required output artifacts

- `artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-batch-report.json`
- `artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-batch-report.md`
- `artifacts/analysis/final-review-release-gate-batch/final-repository-state-audit.json`
- `artifacts/analysis/final-review-release-gate-batch/final-artifact-completeness-gate.json`
- `artifacts/analysis/final-review-release-gate-batch/final-claim-boundary-review.json`
- `artifacts/analysis/final-review-release-gate-batch/release-tag-readiness-package.md`
- `artifacts/analysis/final-review-release-gate-batch/final-handoff-and-next-work.md`

## Required report decisions

Required top-level fields:

- `feature_id`
- `batch_items_covered`
- `prerequisite_tags_verified`
- `feature_063_verified`
- `repository_state_audit_summary`
- `artifact_completeness_summary`
- `claim_boundary_review_summary`
- `release_tag_readiness_summary`
- `handoff_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Passing behavior

Passing requires:

- Feature 063 final verdict is `results_export_reproducibility_documentation_batch_passed`
- Feature 063 reports `remaining_blockers = []`
- all final export artifacts from Feature 063 exist
- repository release gate verifies only committed source-backed evidence
- release tag recommendation is explicit but no tag is created in this feature
- final handoff lists supported results, unsupported claims, known limitations, and recommended next work
- no training rerun
- no new experiment execution
- no prior Feature 037–063 artifact rewrites
- no paper reproduction claim
- no unsupported superiority claim
- no dependency, policy, environment, or reward-timing drift

## Allowed final verdicts

- `final_review_release_gate_batch_passed`
- `feature_063_prerequisite_blocked`
- `repository_state_audit_blocked`
- `artifact_completeness_blocked`
- `claim_boundary_review_blocked`
- `release_tag_readiness_blocked`
- `handoff_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = final_review_release_gate_batch_passed`
- `recommended_next_feature = Release tag creation or thesis/paper writing workflow`
- `remaining_blockers = []`

If any gate fails, blockers must name the exact failed gate and route to repair.

## Hard scope

Allowed:

- final repository state audit
- final artifact completeness gate
- final claim boundary review
- release tag readiness package
- final handoff and next-work recommendation
- release report artifacts and tests

Forbidden:

- creating the release tag inside this feature
- rerunning training campaigns
- adding new experiment outputs
- modifying prior Feature 037–063 artifacts
- paper reproduction claim
- unsupported superiority claim
- dependency changes
- policy drift
- environment semantic changes
- reward timing changes
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
