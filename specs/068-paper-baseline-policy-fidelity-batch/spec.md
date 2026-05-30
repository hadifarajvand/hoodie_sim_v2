# Feature Specification: Paper Baseline Policy Fidelity Batch

**Feature Branch**: `068-paper-baseline-policy-fidelity-batch`  
**Created**: 2026-05-29  
**Updated**: 2026-05-31
**Status**: Repair hardening for placement-level fidelity
**Input**: Feature 068 defines paper baseline policy fidelity for RO, FLC, VO, HO, BCO, and MLEO.

## Repair Note

Feature 068R extends Feature 068. It does not replace it.

The first implementation pass completed registry coverage, shared context use, mask-aware baseline behavior, targeted tests, and initial MLEO ranking. A follow-up repair is required to move the remaining baseline logic from action-family behavior to placement-level behavior.

This hardening pass must preserve the earlier Feature 068 guarantees:

- registry coverage stays intact
- legal-action-mask compliance stays intact
- family-level fallback behavior stays intact
- seeded RO behavior stays intact
- BCO balance_hint behavior stays intact
- MLEO DelayCandidate, build_delay_candidates, last_candidates, last_fallback_reason, total-delay ranking, candidate filtering, tie handling, and fallback metadata stay intact
- placement-level behavior is added on top of previous family-level compatibility behavior
- a repair implementation is invalid if it passes by deleting, weakening, or replacing previous Feature 068 tests
- the legal-action mask is the final authority; payload data cannot override it

The detailed repair contract is recorded in this feature directory.
