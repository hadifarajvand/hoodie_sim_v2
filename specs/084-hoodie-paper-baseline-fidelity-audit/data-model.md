# Data Model: Feature 084 HOODIE Paper Baseline and Formula Fidelity Audit

## Entity: PaperMethod

Fields:
- `method_id`: canonical method identifier.
- `role`: `proposed` or `baseline`.
- `paper_name`: name from HOODIE paper.
- `active`: whether the method is active in final paper-fidelity artifacts.
- `historical_defect`: optional note for invalid previous labels.

Required active methods:

| method_id | role | paper_name | active |
|---|---|---|---|
| HOODIE | proposed | HOODIE | true |
| RO | baseline | Random Offloader | true |
| FLC | baseline | Full Local Computing | true |
| VO | baseline | Vertical Offloader | true |
| HO | baseline | Horizontal Offloader | true |
| BCO | baseline | Balanced Cyclic Offloader | true |
| MLEO | baseline | Minimum Latency Estimation Offloader | true |

Invalid active methods:

| method_id | reason |
|---|---|
| MQO | Not a HOODIE paper baseline; historical Feature 083 defect only. |
| ORIGINAL_HOODIE_BASELINE | Conceptually wrong; HOODIE is the proposed paper method, not a separate baseline. |
| HOODIE_PROPOSED | Redundant/unstable label; active method ID must be `HOODIE`. |

## Entity: FormulaMappingRow

Fields:
- `paper_item`: equation, algorithm, figure, model, or textual obligation from the HOODIE paper.
- `meaning`: interpretation of the paper item.
- `expected_simulation_logic`: required runtime behavior.
- `current_code_location`: file/function/class path if implemented.
- `status`: `exact`, `approximate`, `missing`, `wrong`, or `out_of_scope`.
- `required_fix`: required implementation or documentation repair.
- `evidence`: paper/code/artifact evidence.

## Entity: EvaluationArtifact

Fields:
- `artifact_path`: generated file path.
- `policy_ids`: active policy IDs included in artifact.
- `metrics`: metrics included.
- `contains_invalid_policy`: boolean validation result.
- `readiness_level`: declared fidelity readiness.

## Entity: Metric

Required metrics:
- `task_completion_delay`
- `task_drop_ratio`
- `completion_rate`
- `total_reward`

Secondary/repository-specific metrics must be labeled as repository-specific and must not be presented as paper metrics unless explicitly supported by the paper.
