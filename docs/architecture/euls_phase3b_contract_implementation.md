# EULS Phase 3B Contract Implementation

Phase 3B reconciles the runtime and unit tests with the accepted Phase 3A EULS contract.
It does not introduce DAL, DRL training, LSTM, or Figures 8-11.

## Runtime files changed

- `src/environment/paper_timeout.py`
- `src/analysis/end_to_end_hoodie_golden_trace_validation/report.py`

## Test files changed

- `tests/unit/test_controlled_evaluation_batch_readiness_scenarios.py`
- `tests/unit/test_end_to_end_hoodie_golden_trace_validation_scenarios.py`
- `tests/unit/test_environment_lifecycle_repair.py`
- `tests/unit/test_mechanism_repair_timeout_drop.py`
- `tests/unit/test_offload_instrumentation_feature024_regression.py`
- `tests/unit/test_offload_next_slot.py`
- `tests/unit/test_public_cloud_capacity_sharing.py`
- `tests/unit/test_reward_equation_terminal_reward_contract_sign.py`
- `tests/unit/test_runtime_paper_faithful_semantics_alignment_deadline.py`
- `tests/unit/test_topology_timeout_reward_fidelity_models.py`

## Contracts implemented

### Deadline boundary

`current_slot == absolute_deadline_slot` is valid.
Expiration starts strictly after the deadline slot.

### Timeout/drop

Expired queue-head tasks are dropped deterministically and staged for delayed terminal reward once.

### Private queue

FIFO local service remains in slot order.
Same-slot completion is allowed when capacity permits.

### Offloading queue

Transmission completion may be recorded in slot `t`.
Public admission may be recorded in slot `t`.
Public service eligibility starts no earlier than `t + 1`.

### Public/cloud queue

Queues remain source-indexed by source EA and host node.
Cloud uses the same source-indexed identity.

### Capacity sharing

Active heads are computed at slot start and capacity is divided equally among those heads.
Same-slot redistribution after completion is forbidden.

### Delayed reward

Terminal evidence is detected first.
Reward is emitted once through the pending terminal flush path.

### Metrics

Terminal metrics are updated exactly once per terminal task.

### Termination/truncation

Termination requires no pending arrivals, no current task, no queued work, and no pending terminal rewards.
Truncation remains horizon-based.

### Lifecycle instrumentation

Trace events now follow the canonical state transitions and do not emit terminal/reward evidence early.

## Tests updated as obsolete

- `tests/unit/test_paper_timeout_semantics.py`
- `tests/unit/test_reward_equation_terminal_reward_contract_sign.py`

## Tests updated as contradictory

- `tests/unit/test_runtime_paper_faithful_semantics_alignment_deadline.py`
- `tests/unit/test_controlled_evaluation_batch_readiness_scenarios.py`
- `tests/unit/test_end_to_end_hoodie_golden_trace_validation_scenarios.py`

## Tests fixed as runtime_bug

- `tests/unit/test_environment_lifecycle_repair.py`
- `tests/unit/test_mechanism_repair_timeout_drop.py`
- `tests/unit/test_offload_instrumentation_feature024_regression.py`
- `tests/unit/test_offload_next_slot.py`
- `tests/unit/test_public_cloud_capacity_sharing.py`
- `tests/unit/test_topology_timeout_reward_fidelity_models.py`

## Remaining deferred items

- The workspace still contains unrelated generated artifacts and dirty-path reports from prior runs.
- `tests/unit/test_completion_root_cause_schema.py` is blocked by the repository’s dirty-worktree guard, not by the EULS contract itself.
- Broader paper-faithful analysis and figure claims remain out of scope.

## Explicit non-inclusions

DAL, DRL training, LSTM, baseline campaign repair, and Figures 8-11 are still not included.
