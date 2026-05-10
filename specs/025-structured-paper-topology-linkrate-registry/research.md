# Research: Structured Paper Topology and Link-Rate Registry

## Decisions

### Figure 7 topology recovery
- **Decision**: Treat Figure 7 as recoverable only if the full adjacency can be reconstructed from paper/OCR/PDF evidence without gaps.
- **Rationale**: The spec forbids fabricated edges, and simulator topology is not authoritative paper evidence.
- **Alternatives considered**:
  - Partially recovered topology artifact
  - Inferred adjacency from node count or existing environment structures
- **Why rejected**: Both alternatives risk fabricating a topology that the paper does not explicitly support.

### Topology artifact status
- **Decision**: Use an all-or-nothing topology artifact policy for Figure 7.
- **Rationale**: Partial graph recovery is too easy to misread as authoritative topology.
- **Alternatives considered**:
  - `partially_recovered` topology status
  - Mixed artifact with recovered and inferred edges
- **Why rejected**: The feature requires a strict recovery boundary and a clear unrecoverable outcome.

### Parameter registry recovery
- **Decision**: Recover only paper-backed values and mark all unsupported values unrecoverable or partially recovered.
- **Rationale**: The registry is meant to preserve evidence, not reconstruct plausible missing numbers.
- **Alternatives considered**:
  - Use simulator defaults as fallback
  - Fit missing values from related paper tables
- **Why rejected**: Both methods would blur the line between evidence and invention.

### Provenance and determinism
- **Decision**: Every registry item must carry evidence metadata and the JSON output must be deterministic.
- **Rationale**: The artifacts need to be auditable and reproducible.
- **Alternatives considered**:
  - Human-readable notes without source structure
  - Non-deterministic reporting
- **Why rejected**: Both make later audits fragile.

## Evidence Summary

- `resources/papers/hoodie/ocr/merged.tex` contains the primary OCR text used for recovery.
- `resources/papers/hoodie/ocr/merged.md`, `merged.txt`, and `merged.json` are supplementary OCR formats.
- `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json` indicates topology adjacency is blocking and not present as a structured artifact.
- `artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json` indicates Figure 7 has no fully recoverable adjacency edges and should not be inferred from node count or trace count.

## Constraints Confirmed

- No simulator behavior changes are allowed.
- No policy, metric, training, or campaign mutation is allowed.
- No paper-validity claim is allowed.
- The topology artifact must not be partially recovered if Figure 7 cannot be fully reconstructed.
