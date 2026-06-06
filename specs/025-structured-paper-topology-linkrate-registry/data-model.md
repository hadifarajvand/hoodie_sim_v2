# Data Model: Structured Paper Topology and Link-Rate Registry

## Entities

### Topology Registry
- **Purpose**: Frozen paper-backed record of Figure 7 topology facts.
- **Fields**:
  - `schema_version`
  - `paper_figure_id`
  - `node_count`
  - `node_ids`
  - `adjacency_matrix`
  - `adjacency_matrix_status`
  - `legal_horizontal_destinations`
  - `edge_cloud_connectivity`
  - `source_evidence`
  - `unrecoverable_items`
  - `recovery_confidence`
  - `no_fabrication_disclaimer`
- **Validation rules**:
  - `adjacency_matrix_status` must be `recovered`, `unrecoverable`, or `partially_recovered`.
  - If any Figure 7 edge is unsupported, the topology artifact must not invent it.
  - If the full Figure 7 topology cannot be reconstructed without gaps, the artifact should be marked unrecoverable.

### Parameter Registry
- **Purpose**: Frozen paper-backed record of link rates, CPU capacities, and scenario parameters.
- **Fields**:
  - `schema_version`
  - `entries`
  - `source_evidence`
  - `unrecoverable_items`
  - `no_fabrication_disclaimer`
- **Entry fields**:
  - `name`
  - `value`
  - `unit`
  - `recovery_status`
  - `source_evidence`
  - `notes`
- **Validation rules**:
  - Every recovered value must include evidence and recovery status.
  - Learning/training-related values may be recorded only as paper evidence, not executable config.
  - Unsupported values must be explicitly unrecoverable.

### Recovery Report
- **Purpose**: Human-readable and machine-readable summary of what was recovered and what remains missing.
- **Fields**:
  - `schema_version`
  - `inputs`
  - `outputs`
  - `summary_counts`
  - `recovery_statuses`
  - `source_evidence`
  - `disclaimers`

## Relationships

- The `Topology Registry` is a subset of the broader paper recovery output.
- The `Parameter Registry` may reference topology facts when a parameter is topology-dependent, but it must not invent topology to support a parameter.
- The `Recovery Report` summarizes both registries and records unrecoverable items.

## Status Taxonomy

- **recovered**: The value is directly supported by paper evidence.
- **partially_recovered**: The value is only partially recoverable and the partial result is still evidence-backed.
- **unrecoverable**: The value cannot be supported reliably and must not be inferred.

## Notes

- Figure 7 topology is stricter than parameter recovery: if Figure 7 cannot be fully reconstructed, the topology artifact is not partially recovered.
- Deterministic JSON ordering is required for all registry and report outputs.
