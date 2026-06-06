# Quickstart

## Verify the Spec Package Exists

Run:

```bash
find specs/100-hoodie-paper-faithful-baseline -maxdepth 2 -type f | sort
```

You should see all required spec files and contracts.

## Confirm No Simulator Code Was Modified

Run:

```bash
git status --short
git diff --name-only
```

The expected result is that only files under `specs/100-hoodie-paper-faithful-baseline/` are changed.

## What This Package Is

This package defines the paper-faithful target. It does not modify runtime behavior and does not claim the simulator is already compliant.

