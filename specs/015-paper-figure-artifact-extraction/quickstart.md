# Quickstart: Paper Figure Artifact Extraction

## Run Validation

```sh
src/.venvmac/bin/python -m unittest tests.unit.test_paper_figure_extraction tests.integration.test_paper_figure_extraction_flow
```

## Run Extraction

```sh
src/.venvmac/bin/python - <<'PY'
from pathlib import Path
from src.analysis.paper_figure_extraction import PaperFigureExtractor

extractor = PaperFigureExtractor(
    paper_path=Path("resources/papers/hoodie/ocr/merged.tex"),
    artifact_root=Path("artifacts/campaigns/paper-baseline-reproduction"),
    output_dir=Path("artifacts/analysis/paper-figure-extraction"),
)
outputs = extractor.write_outputs()
print(outputs)
PY
```

## Expected Outputs

- `artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json`
- `artifacts/analysis/paper-figure-extraction/paper-figure-extraction.md`

## Guardrails

- No dependency changes.
- No simulator execution.
- No training execution.
- No policy, metric, or environment lifecycle changes.
- No mutation of existing paper or campaign artifacts.
- Unsupported paper figures remain explicitly unsupported.

