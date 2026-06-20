# EULS Phase 25 - Reward Emission and Evaluation Metric Aggregation Repair

Feature 066 is a read-only evaluation repair pass over Feature 065 outputs and live evaluation stepping evidence.

Scope:
- recover raw reward events from evaluation stepping evidence
- recover terminal events from finalized task records
- reconcile raw event reward totals with canonical task-level reward totals
- preserve canonical task identity across decision, terminal, and reward records
- produce paper-aligned diagnostic metrics without superiority claims

Out of scope:
- reward redesign
- environment redesign
- policy redesign
- replay redesign
- 5000-episode training

Release gate:
- The feature is complete only if raw event reward recovery and canonical task reconciliation both pass.
- If raw reward events cannot be recovered from evaluation evidence, the feature must report a blocked verdict instead of fabricating events.
