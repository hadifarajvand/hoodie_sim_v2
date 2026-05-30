# Spec Details: Feature 068

## User stories

### US1 Registry coverage

Resolve RO, FLC, VO, HO, BCO, and MLEO from the shared policy registry. Each resolved object must support the shared action-selection interface.

Acceptance:

- all required names resolve
- each policy receives PolicyContext
- missing required names fail coverage tests

### US2 Mask-aware behavior

Each policy must return an action allowed by the supplied mask or report a documented no-choice path.

Acceptance:

- FLC prefers local when allowed
- VO prefers vertical when allowed
- HO prefers horizontal when allowed
- RO samples from allowed actions only
- BCO and MLEO use documented fallback rules

### US3 MLEO delay ranking

MLEO must compare candidate actions by total delay using available observation fields.

Acceptance:

- unavailable candidates are skipped
- comparable candidates are ranked by total delay
- ties are deterministic
- missing fields trigger explicit fallback behavior

### US4 Baseline differentiation

Shared controlled observations must show that FLC, HO, VO, and MLEO can produce different action families.

Acceptance:

- all baselines use the same context format
- differentiation is proven by tests
- seeded behavior is repeatable

## Edge cases

- preferred action is masked out
- only one action is available
- MLEO has partial delay fields
- MLEO total delays tie
- RO receives a fixed seed
- BCO reaches cycle rollover
- action aliases include local and compute_local

## Definition of done

- registry tests pass
- mask tests pass
- MLEO ranking tests pass
- fallback tests pass
- integration flow tests pass
- final audit lists changed files and commands
