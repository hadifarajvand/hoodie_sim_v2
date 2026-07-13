# ECHO Topology PNG Export Authorization

## Status

**Author-approved implementation clarification**

This document resolves the topology PNG export blocker caused by the unavailable optional `cairosvg` dependency.

The scientific requirement is to export:

- a publication-quality vector topology figure; and
- a 300-dpi PNG topology figure.

The scientific specification does not require the PNG to be produced by rasterizing the SVG with CairoSVG.

## Approved implementation

Generate the SVG and PNG independently from the same canonical graph data and the same deterministic node coordinates.

Use the repository's existing plotting stack, preferably Matplotlib with the non-interactive `Agg` backend.

Required behavior:

1. Build the canonical graph once from the approved adjacency matrix.
2. Compute or load deterministic node coordinates once.
3. Store the coordinates in the topology metadata.
4. Render the vector output directly as SVG.
5. Render the raster output directly as PNG with `dpi=300`.
6. Use identical:
   - node ordering;
   - edge ordering;
   - node coordinates;
   - labels;
   - sizes;
   - line widths;
   - margins;
   - figure dimensions.
7. Do not derive scientific topology data from either rendered image.
8. Do not emit a placeholder PNG.
9. Do not silently reduce resolution.
10. Do not require CairoSVG for the paper-evaluation path.

## Preferred code change

Replace the hard dependency path:

```python
_svg_to_png(svg_markup)
```

with a renderer interface that can export both formats from graph data, for example:

```python
render_topology(
    adjacency=adjacency,
    positions=positions,
    svg_path=svg_path,
    png_path=png_path,
    dpi=300,
)
```

The implementation may retain CairoSVG as an optional renderer, but it must not be required when direct PNG rendering is available.

## Determinism and lineage

The topology metadata must record:

- renderer name and version;
- plotting backend;
- figure size;
- PNG dpi;
- node coordinates;
- adjacency hash;
- SVG hash;
- PNG hash.

The SVG and PNG must be traceable to the same adjacency matrix and coordinate manifest.

## Required validation

Tests must verify:

1. SVG and PNG files both exist.
2. PNG is a valid PNG file.
3. PNG export uses 300 dpi or the equivalent pixel dimensions for the declared physical figure size.
4. Both formats use the same stored node-coordinate manifest.
5. Repeated rendering with the same inputs produces identical topology geometry.
6. Node and edge counts match the canonical adjacency matrix.
7. Missing CairoSVG does not fail the paper topology export.
8. A renderer failure raises a clear error and never creates a misleading empty or placeholder artifact.

## Dependency policy

Do not install a new system-level Cairo dependency solely for this export unless the environment owner explicitly chooses to do so.

A pure-Python or already-installed plotting path is preferred for reproducibility.

## Authorization

This clarification authorizes direct 300-dpi PNG rendering from canonical graph data and removes CairoSVG as a mandatory runtime dependency for ECHO topology artifacts.
