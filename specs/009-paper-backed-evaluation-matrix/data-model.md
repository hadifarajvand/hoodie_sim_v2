# Data Model: Paper-Backed Evaluation Matrix

## Entities

### EvaluationMatrixConfig

Defines the serial matrix execution scope.

- `policy_names: tuple[str, ...]`
- `scenario_names: tuple[str, ...]`
- `seeds: tuple[int, ...]`
- `episode_length_override: int | None`
- `output_dir: str`
- `runtime_parameters: object | None`
- `compute_config: object | None`
- `commit_ref: str | None`
- `dependency_change_note: str`

Validation rules:
- Policy and scenario names must be non-empty.
- Seeds must be deterministic and reproducible.
- Optional overrides must not alter default behavior when omitted.
- Unsupported policy or scenario names must fail fast.

### PolicyRegistry

Approved policy-name lookup for implemented policies only.

- `FLC`
- `VO`
- `HO`
- `RO`
- `BCO`
- `MLEO`
- `ADAPTIVE`

Rules:
- Returns a policy instance or fails fast for unsupported names.
- Must not auto-alias unknown names.

### ScenarioRegistry

Approved scenario-name lookup for paper-backed traffic scenarios only.

- `paper_default`
- `moderate`
- `heavy`
- `extreme`

Rules:
- Returns a traffic configuration or fails fast for unsupported names.
- Must not introduce new traffic models.

### MatrixRunRecord

One auditable record per policy/scenario/seed combination.

- `policy_name: str`
- `scenario_name: str`
- `seed: int`
- `trace_id: str`
- `config_snapshot: dict[str, object]`
- `final_metrics: dict[str, object]`
- `runtime_metadata: dict[str, object]`

### AggregateSummary

Roll-up view across all matrix run records.

- `total_runs: int`
- `completed_runs: int`
- `failed_runs: int`
- `policy_names: tuple[str, ...]`
- `scenario_names: tuple[str, ...]`
- `seeds: tuple[int, ...]`

## Relationships

- `EvaluationMatrixConfig` drives registry lookup and run ordering.
- `PolicyRegistry` and `ScenarioRegistry` are read-only lookup surfaces.
- `MatrixRunRecord` is derived from one environment execution.
- `AggregateSummary` is derived from the full matrix result set.

## Lifecycle

- Matrix records are generated after each run.
- Summary output is generated after the serial matrix completes.
- No persistent mutable state is owned by the runner.
