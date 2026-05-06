# Research: Paper Result Reporting & Reproducibility Artifacts

## Decisions

### 1. Packaging layer location
- **Decision**: Implement the bundle packager in `src/analysis/reproducibility_bundle.py`.
- **Rationale**: This is reporting and artifact packaging, not evaluation execution. Keeping it separate preserves the evaluation runner boundary.
- **Alternatives considered**: `src/evaluation/` was considered, but it would blur the distinction between running experiments and packaging results.

### 2. Artifact format
- **Decision**: Emit `manifest.json`, `run-config.json`, `artifact-index.json`, `validation-summary.json`, and `README.md`.
- **Rationale**: These files cover provenance, inventory, validation, and human-readable explanation without adding plotting or external report tooling.
- **Alternatives considered**: A single monolithic JSON file was rejected because it is harder to inspect and less reviewer-friendly.

### 3. Checksums and determinism
- **Decision**: Use standard-library SHA-256 hashing and sorted artifact paths with optional timestamp override.
- **Rationale**: The repository already requires reproducibility, and stdlib hashing keeps the feature dependency-free.
- **Alternatives considered**: Third-party checksum or packaging libraries were rejected due to dependency constraints.

### 4. Validation behavior
- **Decision**: Missing expected files are reported in `validation-summary.json` and do not silently pass.
- **Rationale**: Reviewers need an explicit completeness signal; silent omission would make the bundle misleading.
- **Alternatives considered**: Hard-failing the bundle build was considered, but recording missing artifacts preserves more audit information.

### 5. Input contract
- **Decision**: The builder consumes an existing evaluation matrix output directory and writes the bundle to a separate output directory.
- **Rationale**: This keeps raw matrix outputs untouched and prevents accidental overwrites.
- **Alternatives considered**: In-place packaging was rejected because it risks corrupting evaluation artifacts.

## Unresolved Items

None. The feature scope is bounded and the required behavior is explicit in the spec.
