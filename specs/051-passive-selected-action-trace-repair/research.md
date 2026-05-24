# Research: Passive Selected-Action Trace Repair

## Decision 1: Extend passive trace schema with explicit selected-action metadata

**Decision**: The trace must carry `selected_action`, `action_index`, `selected_action_family`, `selected_action_trace_source`, `decision_event_id`, `selected_action_to_task_join_key`, and `terminal_outcome_join_key`.

**Rationale**: Future evidence analysis cannot reconstruct selected-action family counts or join selected actions to lifecycle outcomes if these fields are absent from the passive trace.

**Alternatives considered**:
- Derive selected-action family later from outcomes. Rejected because it makes evidence circular and cannot distinguish missing evidence from zero counts.
- Infer family from legality masks. Rejected because legality is not selection.
- Encode trace repair in a post-processing report only. Rejected because the join keys must exist in the passive trace itself for deterministic downstream analysis.

## Decision 2: Derive selected-action family from the actual selected action only

**Decision**: `selected_action_family` is derived directly from the action chosen by the environment and mapped to `local`, `horizontal`, `vertical`, or `unknown`.

**Rationale**: The evidence must describe what was actually selected, not a later interpretation of legality or outcome.

**Alternatives considered**:
- Infer family from selected outcome. Rejected because the same action can lead to different outcomes.
- Infer family from masks. Rejected because legality and selection are different states.

## Decision 3: Preserve deterministic joins for task and terminal outcome evidence

**Decision**: The trace must preserve deterministic join keys that allow selected actions to be linked to `strategy`, `seed`, `slot`, `agent_id`, `task_id`, and terminal outcomes.

**Rationale**: Feature 050 rerun readiness depends on a deterministic path from selected action to task lifecycle outcome.

**Alternatives considered**:
- Use slot-only coincidence. Rejected unless the slot is explicitly part of a deterministic join key, because coincidence is not evidence.
- Reconstruct joins from report-time heuristics. Rejected because heuristics create fake joins and break auditability.

## Decision 4: Keep behavior equivalence passive and unique

**Decision**: Behavior-equivalence checks will remain passive, will not alter runtime semantics, and will use unique check names to avoid redundant duplicated assertions.

**Rationale**: Trace repair must not become an invisible runtime repair, and duplicate checks obscure what is actually being validated.

**Alternatives considered**:
- Reuse the same equivalence check dozens of times. Rejected because it adds noise, not coverage.
- Skip behavior-equivalence validation entirely. Rejected because a passive trace change that alters selection or outcomes is not acceptable.

## Decision 5: Prior-feature validation must stay committed-artifact-only

**Decision**: Feature 051 tests will validate Features 044, 048, 049, and 050 only through committed artifact checks.

**Rationale**: Dirty-worktree-sensitive prior-feature report builders reject the active Feature 051 worktree and would make validation meaningless.

**Alternatives considered**:
- Re-run prior report builders from the active worktree. Rejected because they are explicitly not valid in this context.
- Validate prior features via `.specify/feature.json` pointer state. Rejected because the pointer is local-only and not a reliable prerequisite gate.
