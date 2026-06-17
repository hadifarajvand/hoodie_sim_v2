# EULS Phase 3A Contract Arbitration

Phase 3A is a contract arbitration step. It does not change runtime behavior.
It classifies the remaining conflicting tests and selects the canonical EULS contract for Phase 3B.

## Canonical decisions

A task is still valid at `current_slot == absolute_deadline_slot`.
It expires only when `current_slot > absolute_deadline_slot`.

Timeout and drop are evaluated deterministically at the head of each queue and at the pending terminal flush boundary.
When a task is dropped, it is removed from its queue, marked with `terminal_outcome = "dropped"`, and staged for delayed terminal reward exactly once.

Private queues remain FIFO.
Local tasks may complete in the same slot they are admitted if compute capacity allows it.
Completion removes the head task immediately; reward is still emitted through the delayed terminal path on the next step.

Offloading queues remain FIFO.
Transmission completion may be recorded in slot `t`, but public service eligibility does not begin before slot `t + 1`.
Public queue admission may be recorded in slot `t` for observability, but same-slot public execution is forbidden.

Public queues are source-indexed by source EA and grouped by host node.
Cloud public queues use the same source-indexed identity.
Capacity sharing is computed from the active public queue heads at slot start.
Tasks admitted during the slot do not join the active-head set until the next slot.
Same-slot redistribution after a head completes is forbidden.

Delayed reward is terminal-only and one-time.
Terminal completion/drop is detected first, then reward is emitted through the pending terminal flush.
Metrics are updated exactly once per terminal task.

Termination means no pending arrivals, no current task, no queued work, and no pending terminal rewards.
Truncation means the horizon was reached before semantic completion.

Lifecycle instrumentation must follow actual state transitions.
No public-queue event may precede public admission.
No reward event may precede terminal evidence.
Duplicate terminal or reward events are forbidden.

## Arbitration table

| Test file | Test name | Current expected behavior | Actual Phase 2 behavior | Contract category | Judgment | Reason | Action for Phase 3B |
|---|---|---|---|---|---|---|---|
| `tests/unit/test_euls_boundary.py` | multiple | EULS wrapper delegates and preserves runtime shape | Passes | lifecycle boundary | canonical | Matches accepted Phase 1 boundary | Keep unchanged |
| `tests/unit/test_gym_environment.py` | delayed reward / queue / termination tests | Delayed reward, source-indexed queues, semantic termination | Passes | delayed reward / termination / offload visibility | canonical | Already aligned with Phase 1.5b and Phase 2 | Keep unchanged |
| `tests/unit/test_euls_queue_timing_deadline.py` | all | Queue/timing/deadline assertions | Passes | queue/timing/deadline | canonical | Matches current slot-based canonical EULS rules | Keep unchanged |
| `tests/unit/test_deadline_rules.py` | `test_task_not_expired_at_deadline` | Deadline slot is still valid | Passes | deadline boundary | canonical | Matches paper-timeout helper and Phase 2 runtime | Keep unchanged |
| `tests/unit/test_deadline_expiration.py` | `test_task_has_not_expired_at_deadline_slot` | Deadline slot is still valid | Passes | deadline boundary | canonical | Matches paper-timeout helper and Phase 2 runtime | Keep unchanged |
| `tests/unit/test_environment_lifecycle_repair.py` | `test_local_compute_completes_before_timeout_when_deadline_allows` | Finalized tasks visible on same step | Fails because terminal reward is delayed | delayed reward / lifecycle instrumentation | contradictory | Test expects immediate finalization while canonical contract delays reward flush | Update test to inspect pending terminal flush or next step in Phase 3B |
| `tests/unit/test_mechanism_repair_timeout_drop.py` | local completion / timeout drop | Immediate finalized tasks at step boundary | Fails because delayed flush is one step later | delayed reward / timeout/drop | contradictory | Same mismatch as above; test assumes same-step finalization | Update test timing in Phase 3B |
| `tests/unit/test_offload_instrumentation_feature024_regression.py` | `test_local_compute_and_deterministic_ordering_remain_matches` | History should be populated immediately | Fails because history records on terminal emission | lifecycle instrumentation | runtime_bug | Runtime only records history after pending terminal flush, leaving a gap for this regression | Reconcile history recording with terminal staging in Phase 3B |
| `tests/unit/test_offload_next_slot.py` | `test_offload_completes_into_public_queue_on_next_slot` | Offload completion appears on next slot | Fails under current handoff path | offload next-slot | runtime_bug | SlotEngine handoff metadata is not sufficient for this direct unit path | Adjust handoff eligibility / test setup in Phase 3B |
| `tests/unit/test_paper_timeout_semantics.py` | `test_deadline_uses_phi_minus_one` | `completion_slot=deadline_slot` is not dropped | Fails under current helper contract | deadline boundary | contradictory | Paper-timeout helper still encodes strict-before semantics for success, conflicting with deadline-aligned runtime tests | Reconcile helper semantics and its tests in Phase 3B |
| `tests/unit/test_public_cloud_capacity_sharing.py` | multiple | Active-head equal-share capacity at slot start | Fails because direct queue tests expect immediate execution outside the slot-start lifecycle | public/cloud capacity sharing | contradictory | The direct queue tests do not stage slot-start execution in the same way as the environment | Normalize the direct queue test setup or make the helper deterministic in Phase 3B |
| `tests/unit/test_reward_equation_terminal_reward_contract_sign.py` | `test_reward_for_terminal_task_signs` | `reward_for_terminal_task(completed)` returns `-3.0` for the fixture | Fails because runtime reward uses `completion_slot - arrival_slot + 1` | delayed reward / reward equation | canonical | Phase 1.5b and Phase 2 retained the delayed terminal reward convention | Update the obsolete expectation in Phase 3B |
| `tests/unit/test_runtime_paper_faithful_semantics_alignment_deadline.py` | `test_deadline_rules_defaults_to_paper_strict_expiration` | `current_slot == deadline` expired | Fails because canonical deadline boundary keeps equality valid | deadline boundary | contradictory | This test conflicts with the accepted deadline boundary and paper-timeout helper | Update the test to the canonical boundary in Phase 3B |

## Tests updated and why

- `tests/unit/test_deadline_rules.py` and `tests/unit/test_deadline_expiration.py` remain canonical and should not change.
- `tests/unit/test_paper_timeout_semantics.py` is obsolete relative to the canonical runtime boundary and must be reconciled.
- `tests/unit/test_reward_equation_terminal_reward_contract_sign.py` encodes an older reward expectation and must be reconciled to the delayed terminal reward contract.
- `tests/unit/test_environment_lifecycle_repair.py`, `tests/unit/test_mechanism_repair_timeout_drop.py`, and `tests/unit/test_offload_next_slot.py` need timing alignment with the delayed flush and next-slot handoff rules.
- `tests/unit/test_public_cloud_capacity_sharing.py` needs a queue-start aligned setup or helper logic consistent with slot-start capacity allocation.
- `tests/unit/test_offload_instrumentation_feature024_regression.py` needs lifecycle event alignment with actual terminal emission.
- `tests/unit/test_runtime_paper_faithful_semantics_alignment_deadline.py` needs its deadline expectation aligned to the canonical boundary.

## Still deferred

- Full paper-faithful figure reproduction.
- DAL.
- DRL training.
- LSTM.
- Baseline campaign repair.
- Any non-EULS figure generation.
- Any claim that the repository has no remaining contract debt.

## Phase 3B ordered repair plan

1. Normalize deadline boundary across `src/environment/deadline_rules.py`, `src/environment/paper_timeout.py`, and the conflicting deadline tests.
2. Normalize timeout/drop sweep and delayed terminal flush timing in `src/environment/gym_adapter.py` and `src/environment/environment.py`.
3. Normalize offload-to-public next-slot eligibility and the direct offload tests.
4. Normalize public/cloud capacity-sharing expectations and any direct queue setup that bypasses slot-start state.
5. Normalize delayed reward, metrics counting, and reward-sign tests.
6. Normalize lifecycle instrumentation ordering and the regression tests that inspect history/event emission.
7. Run the focused regression sweep and then the canonical boundary suites again.
