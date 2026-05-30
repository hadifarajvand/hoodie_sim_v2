# Quickstart: Feature 070

## Purpose

This quickstart explains how to validate the Feature 070 Spec Kit branch and how future implementation must start after the Spec Kit is merged.

## Spec-Only Validation

This branch must not contain implementation code.

Required scope check:

```bash
git diff --name-only origin/main...HEAD
```

Allowed output must be limited to the Feature 070 Spec Kit directory only.

Whitespace check:

```bash
git diff --check
```

## Future Implementation Start

After this Spec Kit PR is merged into `main`, future implementation must start from updated `origin/main`.

The implementation branch must read the Feature 070 Spec Kit files first and must preserve Feature 068R and Feature 069 regression behavior.

## Future Targeted Validation Families

Future implementation should run targeted validation for:

- Feature 068R policy regression.
- Feature 069 mechanism report regression.
- Structured topology evidence.
- Neighbor legality evidence.
- Timeout/drop terminal accounting.
- Reward equation evidence.
- Terminal reward timing.
- Integrated Feature 070 report schema.

## Warning

Do not implement Feature 070 before this Spec Kit is merged into `main`.
