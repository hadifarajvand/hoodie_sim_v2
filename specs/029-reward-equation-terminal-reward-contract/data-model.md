# Data Model: Reward Equation and Terminal Reward Contract

## Entities

### RewardEquationRecord
- `equation_id`: `20`, `21`, `22`, `23`, or `24`
- `normalized_formula`: structured text form of the equation
- `ocr_support`: list of OCR snippets with source offsets or line references
- `classification`: `paper_backed`, `artifact_backed`, `runtime_observed`, `assumption_backed`, or `unrecoverable`
- `confidence`: qualitative recovery confidence
- `notes`: OCR noise, normalization notes, or terminology mappings

### RewardTermRecord
- `term_name`: e.g. `Phi_n(t)`, `Phi_n^priv(t)`, `Phi_n^pub(t)`, `C`
- `meaning`: delay cost, drop penalty, or objective term
- `source`: paper OCR or recovered registry
- `value`: recovered value when available
- `unit`: slots, reward units, or symbolic
- `classification`: paper-backed / artifact-backed / assumption-backed / unrecoverable

### RuntimeRewardEventRecord
- `task_id`: task identifier
- `selected_action`: selected action label
- `terminal_outcome`: completed, dropped, or omitted
- `reward_emitted`: boolean
- `reward_value`: numeric reward when emitted
- `reward_timing`: terminal, omitted, or blocked
- `trace_events`: ordered lifecycle events from the offload trace ledger

### AggregationContractRecord
- `scope`: per-task, per-agent, per-slot, per-episode
- `reduction_order`: sum-first, average-first, or other
- `classification`: paper-backed, artifact-backed, assumption-backed, or unrecoverable
- `reporting_mode`: cumulative reward, averaged cumulative reward, or other

## Validation Rules

- Reward emission MUST be terminal-event linked.
- `selected_action` MUST never emit reward.
- Successful completion reward MUST be negative delay cost.
- Drop reward MUST equal negative penalty `-C`.
- No-task slots MUST be omitted or NaN-classified.
- Aggregation details MUST be classified honestly if the reduction order is not fully recoverable.

## Runtime Contract Fields

- `success_reward_formula`
- `drop_reward_formula`
- `drop_penalty_value`
- `no_task_reward_policy`
- `delay_cost_unit`
- `terminal_timing_policy`
- `aggregation_policy`
- `runtime_interpretation_status`
- `assumption_backed_items`
- `unrecoverable_items`

## State Transitions

1. Task arrives and `selected_action` is recorded.
2. Task progresses through execution or offload lifecycle.
3. Terminal outcome becomes `completed` or `dropped`.
4. Reward is emitted once at the terminal event.
5. Trace ledger records `reward_emitted` and outcome-linked events.
6. Analysis report classifies the result and preserves source evidence.
