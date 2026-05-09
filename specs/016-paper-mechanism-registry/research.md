# Research: Paper Mechanism Registry

## OCR Source of Truth

- Decision: Use `resources/papers/hoodie/ocr/merged.tex` as the authoritative paper evidence source.
- Rationale: The feature must preserve paper traceability and avoid inventing unsupported mechanism details.
- Alternatives considered: Using derived OCR siblings or analysis artifacts as primary evidence was rejected because those are secondary and may omit or reinterpret the original paper text.

## Secondary Evidence Inputs

- Decision: Allow `merged.md`, `merged.txt`, `merged.json`, `HOODIE_paper.pdf`, figure extraction outputs, audit reports, and sensitivity reports as secondary context only.
- Rationale: These sources can help with context or cross-checking but must not override the OCR source of truth.
- Alternatives considered: Treating secondary files as equivalent evidence was rejected because that would weaken provenance and increase the chance of paper drift.

## Mechanism Status Classification

- Decision: Classify each mechanism as documented, partially documented, ambiguous, or missing on the paper side, and implemented, partially implemented, assumption-backed, not implemented, or unknown on the project side.
- Rationale: The registry must separate what the paper states from what the repository can presently prove.
- Alternatives considered: Collapsing paper and implementation state into one label was rejected because it would blur paper evidence with repository evidence.

## Evidence Snippet Strategy

- Decision: Store deterministic OCR evidence snippets with source path, section or context, figure or equation reference when available, and snippet index or character offset.
- Rationale: Deterministic evidence references support repeatable review and avoid ambiguous citations.
- Alternatives considered: Relying on line numbers alone was rejected because OCR sources can be unstable or difficult to cite precisely.

## Risk Classification

- Decision: Mark reward timing, delayed reward, timeout/drop, topology adjacency, and unit mapping issues as high-impact or blocking when evidence is incomplete.
- Rationale: These mechanisms shape correctness and fairness, so ambiguity here carries disproportionate scientific risk.
- Alternatives considered: Treating all gaps as equal was rejected because some missing details affect the validity of later analysis much more than others.

## Project Mapping Policy

- Decision: Allow known module-path mappings only as project mappings, never as paper evidence.
- Rationale: The registry must distinguish current repository coverage from paper claims.
- Alternatives considered: Mixing module mappings into the evidence field was rejected because it would incorrectly imply paper support.

## Output Determinism

- Decision: Generate JSON and Markdown outputs in a deterministic order with stable formatting.
- Rationale: The registry is meant to be audit-friendly and repeatable.
- Alternatives considered: Human-friendly but non-deterministic ordering was rejected because it would complicate diff review and reproducibility.
