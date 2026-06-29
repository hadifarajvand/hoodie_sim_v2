# Phase 0 Code/Spec Alignment Drift Resolution Plan

Date: 2026-06-28
Task: Resume and complete Phase 0 code/spec alignment drift resolution for HOODIE baseline fidelity
Classification: planning-only, no implementation

## Objective

Complete the in-progress Phase 0 code/spec alignment drift resolution planning task. Verify whether the 2 high-severity audit findings ("Missing Explicit Validation Gate Implementation" and "Documentation Inconsistencies") represent actual code/spec drift or documentation gaps.

## Evidence Table

| Drift Area | Expected Spec Behavior | Graphify/Source/Test Evidence | Evidence Level | Affected Files | Proposed Action | Src Edit? | Test Edit? | Doc Edit? | Human Approval? |
|---|---|---|---|---|---|---|---|---|---|
| **A. PolicyContext contract** | Spec.md + repair contract: `observation` dict with documented keys (`source_agent_id`, `edge_agent_ids`, `cloud_id`, `placement_actions`, `horizontal_destinations`, `cloud_action`, `local_action`, `mleo_placement_candidates`, `queue_delay_estimates`, `fallback_hints`). `legal_action_mask` dict. `trace_history` tuple. | **Source**: `src/policies/policy_interface.py:8-11` defines exactly these 3 fields with correct types. **Tests**: 7 test files (test_baseline_policy_fidelity.py, test_mleo_policy.py, test_phase0_validation_gates.py, test_policy_registry.py, test_bco.py, test_ro.py, test_adaptive_offloading_policy.py) all construct `PolicyContext` with all 3 fields. **Spec**: `specs/068-paper-baseline-policy-fidelity-batch/spec.md` and `paper-exact-baseline-repair.md:26-40` list all valid observation keys. | **SOURCE_CONFIRMED** | `src/policies/policy_interface.py`, `src/policies/common.py`, `src/policies/mleo.py`, `tests/unit/test_baseline_policy_fidelity.py`, `tests/unit/test_mleo_policy.py`, `tests/unit/test_phase0_validation_gates.py`, `specs/068-paper-baseline-policy-fidelity-batch/spec.md` | Add explicit PolicyContext field documentation to spec.md | No | No | Yes | No |
| **B. DelayCandidate fields** | Spec.md + repair contract: "Select available placement with lowest total estimated delay." "Exclude unavailable candidates before ranking." "Missing placement or queue data produces visible fallback reason." | **Source**: `src/policies/mleo.py:18-27` defines 8 fields: `action_family`, `action_id`, `available`, `queue_delay`, `transmission_delay`, `compute_delay`, `total_delay`, `tie_break_key` + `fallback_notes`. **Tests**: `test_mleo_policy.py` (15 tests) covers all field extraction, tie-breaking, exclusion, mask override. `test_phase0_validation_gates.py` Gate 5 covers ranking, Gate 6 covers fallback. | **SOURCE_CONFIRMED** | `src/policies/mleo.py`, `tests/unit/test_mleo_policy.py`, `tests/unit/test_phase0_validation_gates.py`, `specs/068-paper-baseline-policy-fidelity-batch/spec.md` | Document DelayCandidate fields explicitly in spec.md | No | No | Yes | No |
| **C. Fallback behavior docs** | Spec.md: FLC→local, VO→cloud, HO→horizontal, BCO→balance_hint + rotation, MLEO→"compare N+1 options, select lowest delay, missing data = fallback." Compatibility rule: family-level fallback is valid when placement contract unavailable. | **Source**: `src/policies/common.py:60-62` `fallback_action` = local→horizontal→vertical. `mleo.py:43-52` 3-tier fallback: delay ranking → `_fallback_from_hints()` → `fallback_action()`. `flc.py`, `vo.py`, `ho.py`: single preferred family + `fallback_action`. `bco.py`: balance_hint ranking → placement rotation → family fallback. **Tests**: `test_baseline_policy_fidelity.py` lines 19-46 (fallback tests), `test_mleo_policy.py` lines 198-229 (MLEO fallback tests). Gate 6 covers MLEO fallback hierarchy. **Spec**: `paper-exact-baseline-repair.md:10-16` documents expected behavior per policy. | **SOURCE_CONFIRMED** | `src/policies/common.py`, `src/policies/mleo.py`, `src/policies/flc.py`, `src/policies/vo.py`, `src/policies/ho.py`, `src/policies/bco.py`, `tests/unit/test_baseline_policy_fidelity.py`, `tests/unit/test_mleo_policy.py`, `tests/unit/test_phase0_validation_gates.py`, `specs/068-paper-baseline-policy-fidelity-batch/paper-exact-baseline-repair.md` | Add fallback chain documentation to spec.md for MLEO; clarify compatibility rule scope | No | No | Yes | No |
| **D. Mask authority enforcement** | Spec.md + repair contract: "The legal-action mask remains the final authority. A placement payload may describe availability, but it cannot make an illegal action selectable." | **Source**: `src/policies/action_masking.py:10-12` `select_legal_action()` raises `ValueError` on illegal. `src/policies/mleo.py:151` `available = (action_id in legal) and bool(payload.get("available", True))` — mask AND payload. **Tests**: `test_mleo_policy.py:101-113` explicitly tests `available:True cannot override False mask`. `test_baseline_policy_fidelity.py:128-153` (18 tests) all verify returned action exists in mask. Gate 2 covers action-mask compliance. | **SOURCE_CONFIRMED** | `src/policies/action_masking.py`, `src/policies/mleo.py`, `tests/unit/test_baseline_policy_fidelity.py`, `tests/unit/test_mleo_policy.py`, `tests/unit/test_phase0_validation_gates.py`, `specs/068-paper-baseline-policy-fidelity-batch/paper-exact-baseline-repair.md` | Document mask enforcement in spec.md; add architecture decision record | No | No | Yes | No |

## Implementation Safety Classification

| Row | Classification | Rationale |
|-----|--------------|-----------|
| A. PolicyContext contract | **DOC_ONLY_ALIGNMENT** | PolicyContext fields perfectly match spec behavior. Only the spec can be improved by explicitly listing field definitions rather than relying on implicit key enumeration. |
| B. DelayCandidate fields | **DOC_ONLY_ALIGNMENT** | All 8 fields implemented, tested, and match spec intent. Spec should explicitly document the DelayCandidate fields for reference. |
| C. Fallback behavior docs | **DOC_ONLY_ALIGNMENT** | All 3-tier MLEO fallback chain implemented and tested. Per-policy fallback documented in spec.md paper targets. Only spec documentation improvement needed. |
| D. Mask authority enforcement | **DOC_ONLY_ALIGNMENT** | Centralized in `action_masking.py`, enforced at point of use, tested by multiple test layers. Spec states mask as final authority. Only spec documentation improvement needed. |

## Summary: NO ACTUAL CODE/SPEC DRIFT EXISTS

After full source inspection and test evidence review:

- **The "documentation inconsistencies" audit finding is NOT confirmed.** All four claimed drift areas (PolicyContext contract, DelayCandidate fields, fallback behavior, mask authority) are fully aligned between source and spec.
- The audit's claim of "documentation inconsistencies" is actually about the spec being **implicit rather than explicit** — the spec describes expected behavior but does not enumerate the exact dataclass fields or document the MLEO fallback hierarchy.
- **No source edits required. No test edits required. No implementation needed.**
- The only recommended action is documentation improvement to make the spec more explicit.

## Recommended Documentation Improvements

1. **`specs/068-paper-baseline-policy-fidelity-batch/spec.md`** — Add explicit PolicyContext dataclass definition and DelayCandidate field listing
2. **`specs/068-paper-baseline-policy-fidelity-batch/spec.md`** — Add MLEO fallback hierarchy documentation: delay candidates → fallback_hints → mask order
3. **`specs/068-paper-baseline-policy-fidelity-batch/paper-exact-baseline-repair.md`** — Add architecture note on mask authority as single enforcement point in `action_masking.py`
4. **`docs/PROJECT_DECISIONS.md`** (optional) — Record that Phase 0 code/spec alignment was verified; all 4 areas are SOURCE_CONFIRMED

## Human Approval Gate

Not required for this task — all findings are DOC_ONLY_ALIGNMENT. No source, test, or config files modified.

## Routing Result (from prior session)

- coder @ 70% — noted, no implementation will occur
- researcher @ 60% — noted, evidence gathered via read-only search
- tester @ 50% — noted, no test edits needed

## Next Command (for human)

If documentation improvements are desired:
```bash
# Edit spec to add explicit PolicyContext and DelayCandidate definitions
# Then run validation gates:
python -m pytest tests/unit/test_phase0_validation_gates.py -v
```

If no documentation improvements are desired:
```bash
# Phase 0 is complete — all 4 drift areas verified as aligned
# Ready to proceed to Phase 1 or next feature
```

## Verification Commands

```bash
python -m pytest tests/unit/test_phase0_validation_gates.py -v
python -m pytest tests/unit/test_baseline_policy_fidelity.py -v
python -m pytest tests/unit/test_mleo_policy.py -v
```