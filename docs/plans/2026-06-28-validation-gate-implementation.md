# Validation Gate Implementation for Phase 0 Baseline Fidelity

## Objective
Create minimal validation gate automation that explicitly enumerates and asserts all 8 Phase 0 baseline-fidelity gates from a single entry point.

## Non-Goals
- No policy behavior changes
- No simulator algorithm changes
- No Phase 2 work
- No training runs
- No source code edits in `src/agents/`, `src/environment/`, `src/`, `configs/`

## The 8 Validation Gates

| # | Gate | Existing Coverage | Status |
|---|------|------------------|--------|
| 1 | **Registry coverage** - All 6 required paper baselines + ADAPTIVE registered | `test_policy_registry.py:test_required_paper_baselines_are_registered_and_choose_through_context` | ✅ Covered |
| 2 | **Action-mask compliance** - Every policy returns only legal actions | `test_baseline_policy_fidelity.py:test_every_baseline_returns_only_legal_actions_when_preferred_family_is_disabled` + `test_bco_rollover_skips_unavailable_families` | ✅ Covered |
| 3 | **RO seeding** - RO produces reproducible seeded output | `test_baseline_policy_fidelity.py:test_ro_seeded_sampling_is_reproducible_and_legal` | ✅ Covered |
| 4 | **BCO balancing** - BCO uses balance hints before rollover | `test_baseline_policy_fidelity.py:test_bco_uses_balance_hint_before_rollover` + `test_bco_rotates_over_concrete_placements_in_paper_order` | ✅ Covered |
| 5 | **MLEO ranking** - MLEO ranks delay candidates correctly | `test_mleo_policy.py:test_total_delay_ranking_chooses_lowest_comparable_candidate` + `test_total_delay_ranking_prefers_lowest_placement_candidate` + `test_deterministic_tie_handling_prefers_local_then_horizontal_then_vertical` | ✅ Covered |
| 6 | **MLEO fallback** - MLEO has explicit fallback behavior | `test_mleo_policy.py:test_missing_fields_use_visible_fallback_hints` + `test_missing_placement_fields_use_visible_fallback_hints` + `test_missing_fields_without_hints_use_documented_mask_order_fallback` | ✅ Covered |
| 7 | **Controlled differentiation** - Different policies select different actions from same context | `test_baseline_policy_fidelity_flow.py:test_flc_ho_vo_and_mleo_can_select_different_families_from_same_context_shape` + `test_flc_ho_vo_bco_and_mleo_can_select_concrete_placements_from_the_same_context_shape` | ✅ Covered |
| 8 | **Scope audit** - Only allowed paths changed, forbidden paths untouched | `test_baseline_policy_fidelity_flow.py:test_scope_guard_forbids_forbidden_changed_paths` | ✅ Covered |

## Files Created/Changed

| File | Action | Purpose |
|------|--------|---------|
| `tests/unit/test_phase0_validation_gates.py` | **Create** | Explicit gate manifest: enumerates all 8 gates, imports and reruns key assertions per gate |
| `scripts/validation/run_phase0_gates.py` | **Create** | Standalone CLI runner that executes the 8 gates and prints pass/fail per gate |
| `docs/plans/2026-06-28-validation-gate-implementation.md` | **Create** | This plan |

## Implementation Approach
Gate test imports existing test infrastructure (PolicyRegistry, PolicyContext) and re-asserts each gate explicitly. No existing test files are modified. No source code is touched.

## Validation Commands
```bash
python -m pytest tests/unit/test_phase0_validation_gates.py -v
python scripts/validation/run_phase0_gates.py
python -m pytest tests/unit/test_baseline_policy_fidelity.py tests/unit/test_mleo_policy.py tests/unit/test_policy_registry.py tests/integration/test_baseline_policy_fidelity_flow.py -v
```

## Rollback Strategy
Delete the two new files. No existing code is modified.

## Acceptance Criteria
- [x] 8 gates explicitly listed in a single test file
- [x] Each gate has its own test method with clear docstring
- [x] Standalone CLI runner prints pass/fail per gate
- [x] No source code modified
- [x] No existing tests modified
- [x] All 8 gates pass
