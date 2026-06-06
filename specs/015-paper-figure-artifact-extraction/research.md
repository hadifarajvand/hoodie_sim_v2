# Research: Paper Figure Artifact Extraction and Comparison Scaffold

## Decision: Use OCR Text As The Only Paper Source

The extractor will read `resources/papers/hoodie/ocr/merged.tex` for captions, figure descriptions, and evaluation context. It will not inspect paper images or digitize plotted curves.

**Rationale**: OCR text is committed, deterministic, and auditable. Figure image digitization would introduce an unsupported measurement process and risks fabricated numeric targets.

## Decision: Treat Missing Numeric Curves As Missing Targets

When OCR text describes a plotted quantity but does not include numeric curve values, the paper numeric target is missing.

**Rationale**: Captions can name variables and axes, but they are not numeric datasets. The extractor must not invent curve values.

## Decision: Use Existing Campaign Artifacts As Reproduction Data

The extractor will load the committed campaign root, matrix summary, per-run JSON files, traces, and optional audit and sensitivity reports.

**Rationale**: These are the artifact-backed data currently available. They support partial extraction for Figure 9 action distributions and Figure 10 delay/drop-ratio baseline metrics.

## Decision: Mark Training-Only Figures Unsupported Unless Training Artifacts Exist

Figures 8 and 11 require training reward or training delay curves. Current campaign artifacts are evaluation artifacts, not DRL training logs.

**Rationale**: Treating evaluation outputs as training curves would be scientifically false.

## Decision: Preserve Repository Metric Signs

Figure 10 notes paper average delay convention may be negative. The extractor preserves repository metric values as stored and records a caveat instead of transforming signs.

**Rationale**: Metric formula changes and undocumented sign flips are forbidden.

