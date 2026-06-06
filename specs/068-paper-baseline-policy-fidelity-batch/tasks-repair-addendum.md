# Tasks Repair Addendum: Feature 068

## Purpose

Track the follow-up implementation pass for Feature 068 after the first merged baseline-policy update.

Feature 068R extends Feature 068. It does not replace it.

## Required Work

- [X] Read the current Feature 068 artifacts.
- [X] Read `paper-exact-baseline-repair.md`.
- [X] Audit the current policy implementation and tests.
- [X] Add targeted tests for the follow-up behavior.
- [X] Repair only the allowed policy and registry areas.
- [X] Keep previous Feature 068 tests passing.
- [X] Run targeted unit and integration tests.
- [X] Record scope audit, fallback behavior, and open risks in the PR.

## Hardening Rules

- Existing registry coverage must remain.
- Existing legal-action-mask compliance must remain.
- Existing family-level fallback behavior must remain.
- Existing seeded RO behavior must remain.
- Existing BCO balance_hint behavior must remain.
- Existing MLEO DelayCandidate, build_delay_candidates, last_candidates, last_fallback_reason, total-delay ranking, candidate filtering, tie handling, and fallback metadata must remain.
- Placement-level behavior is added on top of previous family-level compatibility behavior.
- A repair implementation is invalid if it passes by deleting, weakening, or replacing previous Feature 068 tests.
- The legal-action mask is the final authority for placement availability.

## Scope Guard

Do not update runtime simulation internals, training internals, generated outputs, dependency files, or lock files.
