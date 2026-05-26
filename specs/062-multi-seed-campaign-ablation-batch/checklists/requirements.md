# Requirements Checklist: Feature 062

## Specification quality

- [x] Feature purpose is explicit.
- [x] Batch coverage is explicit.
- [x] Feature 061 prerequisite is explicit.
- [x] Required output artifacts are explicit.
- [x] Required top-level report fields are explicit.
- [x] Allowed final verdicts are explicit.
- [x] Routing rules are explicit.
- [x] Scope guard is explicit.
- [x] Validation handoff packet is explicit.

## Batch coverage

- [x] Multi-seed campaign gate is covered.
- [x] Multi-seed campaign execution or controlled materialization is covered.
- [x] Multi-seed aggregation is covered.
- [x] Mechanism ablation gate is covered.
- [x] Mechanism ablation execution or controlled materialization is covered.

## Required evidence

- [x] Deterministic seed set with at least three seeds is required.
- [x] Bounded per-seed budget is required.
- [x] Shared trace-bank constraint is required.
- [x] Shared metric schema is required.
- [x] Configured and actual execution budgets must be separated.
- [x] Aggregation must include sample count, mean, min, max, and optional variance/std when numeric values exist.
- [x] Schema-only metrics must be marked as not claimed, not silently dropped.
- [x] Required ablation variants are listed.
- [x] Blocked ablation variants must include exact blockers.

## Safety

- [x] No dependency drift.
- [x] No policy drift.
- [x] No environment contract drift.
- [x] No reward timing change.
- [x] No prior Feature 037–061 artifact rewrite.
- [x] No paper reproduction claim.
- [x] No unsupported superiority claim.
- [x] No uncontrolled campaign loop.
- [x] No checkpoint binary creation.

## Implementation readiness

- [x] Package path is defined.
- [x] Test files are defined.
- [x] Artifact paths are defined.
- [x] Validation command is defined.
- [x] Expected passing verdict is defined.
- [x] Expected next feature is defined.
