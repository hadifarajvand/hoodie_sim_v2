# Data Model: Campaign Result Sanity Audit

## Entities

### CampaignArtifactSet

- `campaign_dir`: directory containing campaign-level outputs
- `matrix_dir`: directory containing per-run matrix outputs
- `bundle_dir`: directory containing bundle outputs
- `trace_dir`: directory containing trace files
- `run_json_files`: discovered per-run result files
- `matrix_summary_csv`: aggregate matrix summary file
- `campaign_summary_json`: campaign summary artifact
- `determinism_check_json`: audit of deterministic reporting inputs

### AuditFinding

- `category`: type of anomaly or consistency issue
- `severity`: informational, warning, or critical
- `description`: human-readable explanation
- `evidence`: artifact paths or summary fields supporting the finding

### AuditReport

- `artifact_inventory`: discovered artifact list
- `findings`: ordered set of audit findings
- `scenario_differentiation`: summary of scenario separation signals
- `policy_differentiation`: summary of policy separation signals
- `accounting_consistency`: reconciliation results for totals and finalized tasks
- `passed`: whether the audit found blocking inconsistencies

## Relationships

- `CampaignArtifactSet` is the source input to the audit.
- `AuditFinding` records are grouped into `AuditReport`.
- `AuditReport` references artifact paths and summary values but does not mutate any input.

## Validation Rules

- Artifact paths must be treated as read-only references.
- Findings must be deterministic for the same artifact set.
- Scenario and policy differentiation checks must be derived from existing artifact content only.
- Accounting consistency must reconcile aggregate totals with underlying per-run records when available.

