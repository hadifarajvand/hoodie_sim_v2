# Plan — Feature 083 HOODIE Paper Baseline Fidelity

## Steps
1. Inspect HOODIE paper evaluation section and OCR text.
2. Extract baseline algorithms and their reported metrics.
3. Map baselines to repository adapters: RO, FLC, VO, HO, BCO, MQO.
4. Remove any legacy policy proxies (ORIGINAL_HOODIE_BASELINE).
5. Update Spec Kit tasks, readiness, and scope.
6. Implement adapters for paper-defined baselines.
7. Regenerate Feature 083 artifact bundle.
8. Validate artifacts: HOODIE vs each baseline, highlight core metrics (completion delay, task drop ratio).
9. Update report and manifest with explicit metric comparison.
10. Run unit and integration tests for all adapters and artifacts.