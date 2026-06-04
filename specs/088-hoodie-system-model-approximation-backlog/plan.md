# Plan: Feature 088 HOODIE System-Model Approximation Backlog

## Branch

`088-hoodie-system-model-approximation-backlog`

## Goal

Record approximation repair candidates without implementing them yet.

## Plan

1. Preserve the approximation inventory from Feature 086.
2. Distinguish exact mechanisms from approximate documented mechanisms.
3. Define future repair directions.
4. Do not modify simulator code.
5. Continue output analysis from Feature 087.

## Activation Criteria

Activate this feature only if:

- paper-output comparison diverges significantly;
- the user wants stricter HOODIE reproduction;
- a reviewer requires exact system-model implementation rather than documented approximation.

## Non-Goals

- No code changes now.
- No new tests now.
- No artifact generation now.
- No thesis/DCQ/proposed-method work.
