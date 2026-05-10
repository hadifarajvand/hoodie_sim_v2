# Quickstart: Structured Paper Topology and Link-Rate Registry

## Purpose

Recover paper-backed topology and parameter evidence into frozen registry artifacts without fabricating missing values.

## Required Inputs

- `resources/papers/hoodie/ocr/merged.tex`
- `resources/papers/hoodie/ocr/merged.md`
- `resources/papers/hoodie/ocr/merged.txt`
- `resources/papers/hoodie/ocr/merged.json`
- `resources/papers/hoodie/HOODIE_paper.pdf` if locally available
- `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`
- `artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json`

## Expected Outputs

- `resources/papers/hoodie/recovered/topology-g.json`
- `resources/papers/hoodie/recovered/paper-parameter-registry.json`
- `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json`
- `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.md`

## Validation Guidance

- Use the approved project interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Run schema validation tests for both recovered JSON artifacts
- Run determinism tests to verify stable JSON ordering and stable conclusions
- Run no-fabrication tests to ensure every recovered topology edge or parameter value has evidence or is explicitly unrecoverable
- Run scope-guard tests to ensure no simulator, policy, metric, training, dependency, or lockfile changes occur
- Run an integration test to verify Figure 7 recovery does not silently use simulator defaults

## Recovery Rules

- Do not infer topology edges from node count or trace file count.
- Do not use existing simulator topology as paper truth.
- Do not claim paper reproduction readiness.
- If Figure 7 is not fully recoverable, mark the topology artifact unrecoverable rather than partially recovered.
- Parameter entries may be partially recovered only when paper evidence supports a partial value.

## Output Rules

- Write deterministic JSON with explicit `schema_version` fields.
- Include `source_evidence` for every recovered item.
- Record `recovery_status` for every item.
- Include a `no_fabrication_disclaimer` in both registry artifacts and the recovery report.
