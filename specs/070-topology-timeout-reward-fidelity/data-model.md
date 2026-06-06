# Data Model: Feature 070

## EvidenceProvenance

Represents where a recovered blocker-resolution fact came from.

Fields:

- `category`: topology, timeout_drop, or reward.
- `source_reference`: paper section, table, figure, repository file, or user extraction note.
- `extraction_method`: manual, OCR, code-derived, runtime-derived, or unknown.
- `confidence`: verified, assumption-backed, or blocked.
- `reviewer_note`: reason this evidence is accepted or rejected.

Validation:

- Manual evidence must never be silently treated as runtime truth.
- Any verified claim must include a source reference and reviewer note.

## ManualTopologyEvidence

Represents user- or paper-extracted topology evidence.

Fields:

- `edge_agent_ids`
- `cloud_id`
- `adjacency_edges`
- `adjacency_matrix`
- `row_labels`
- `column_labels`
- `provenance`

Validation:

- At least one of `adjacency_edges` or `adjacency_matrix` must be present.
- Self-edges must be rejected unless explicitly documented as non-offloading placeholders.
- Matrix labels must match edge agent IDs.
- Neighbor map must be derived from this evidence, not invented.

## TopologyEvidenceReport

Represents structured topology and neighbor graph evidence.

Fields:

- `source_agent_id`
- `edge_agent_ids`
- `cloud_id`
- `adjacency_matrix_source`
- `neighbor_map`
- `cloud_reachability`
- `evidence_status`
- `provenance`
- `blockers`

Validation:

- Must not invent adjacency.
- Neighbor legality must be derived from structured evidence.
- If manual topology evidence is supplied, the report must label it as manual paper extraction.

## NeighborLegalityEvidence

Represents whether a horizontal offload destination is legal.

Fields:

- `source_agent_id`
- `destination_agent_id`
- `is_neighbor`
- `is_self_destination`
- `legal_under_topology`
- `legal_under_action_mask`
- `final_legal`
- `provenance`

Validation:

- Self-destination must be illegal.
- Final legality requires both topology and mask legality.

## TimeoutDropRuleEvidence

Represents the recovered or unresolved timeout/drop rule.

Fields:

- `rule_text`
- `source_reference`
- `timeout_relation`
- `drop_condition`
- `provenance`
- `paper_semantics_status`

Validation:

- A rule cannot be marked verified without source-backed text.
- Runtime-derived behavior can support compatibility evidence, but not paper-faithful evidence by itself.

## TimeoutDropAccountingEvidence

Represents per-task timeout/drop accounting.

Fields:

- `task_id`
- `arrival_slot`
- `timeout_length`
- `absolute_deadline_slot`
- `completion_slot`
- `terminal_slot`
- `terminal_status`
- `drop_reason`
- `paper_semantics_status`
- `rule_evidence`

Validation:

- Dropped tasks must have terminal evidence.
- Completed tasks must not be counted as dropped.
- Deadline and timeout semantics must be explicit.

## RewardEquationEvidence

Represents reward equation recovery state.

Fields:

- `equation_id`
- `equation_text`
- `source_reference`
- `terms`
- `recovered_status`
- `assumption_status`
- `provenance`
- `blockers`

Validation:

- Must separate recovered equation text from inferred or assumption-backed terms.
- A verified reward equation must include source-backed equation text and term definitions.

## TerminalRewardEvidence

Represents terminal reward emission.

Fields:

- `task_id`
- `selected_action`
- `terminal_status`
- `terminal_slot`
- `reward_slot`
- `reward_value`
- `reward_equation_id`
- `timing_valid`
- `provenance`

Validation:

- Reward slot must be at or after terminal slot.
- Reward must reference a known equation evidence record or an explicit blocker.

## Feature070Blocker

Represents unresolved topology, timeout/drop, or reward issues.

Fields:

- `category`
- `severity`
- `description`
- `evidence_source`
- `next_action`

## Feature070FidelityReport

Final Feature 070 report.

Fields:

- `feature_name`
- `status`
- `passed`
- `changed_files`
- `topology_evidence`
- `neighbor_legality_evidence`
- `timeout_drop_rule_evidence`
- `timeout_drop_accounting_evidence`
- `reward_equation_evidence`
- `terminal_reward_evidence`
- `blockers`
- `feature_068r_regression_status`
- `feature_069_regression_status`
- `paper_claim_boundary`
- `recommended_next_feature`

Validation:

- Must report each of the three blocker categories separately.
- Must not claim full paper reproduction unless all blocker categories are resolved with structured evidence.
- `passed=True` requires no blockers and valid terminal reward timing.
