# Feature 082 — HOODIE Runtime Evaluation Spec Repair

## Reference
GitHub Spec Kit: https://github.com/github/spec-kit

## Goal
- HOODIE is the only proposed method.
- Remove ORIGINAL_HOODIE_BASELINE as independent policy.
- Extract all baseline algorithms exactly from HOODIE paper evaluation section.
- Map baselines to repository adapters.
- Mark baseline adapters blocked until paper-extracted.
- Only allow LOCAL_ONLY, CLOUD_ONLY, RANDOM_POLICY as sanity-check baselines if paper supports or labels them.

## Tasks
- Extract exact baseline names from HOODIE paper (OCR or PDF).
- Map baselines to repo adapters.
- Update readiness: blocked if extraction incomplete, partial if baselines extracted but not implemented, mostly_implemented if implemented or documented unsupported, fully_implemented only if HOODIE compared to paper-derived baselines.
- Scope guard: reject evaluation comparing HOODIE against ORIGINAL_HOODIE_BASELINE unless paper-defined.

## Claim boundary
- HOODIE proposed method only
- No DCQ, thesis method, statistical superiority, or full paper reproduction.