# Feature 082 Plan — Policy Adapter Repair

## Objective
Repair compatibility-mode policies in Feature 082 runtime evaluation so that all baseline and proposed policies are distinct.

## Phases
1. Inspect current adapter logic
2. Repair HOODIE_PROPOSED adapter
3. Repair ORIGINAL_HOODIE_BASELINE adapter
4. Add policy identity guard tests
5. Regenerate artifacts
6. Update report and execution manifest with identity proof

## Validation
- Artifact verification
- Unit and integration tests
- Metrics distinguish HOODIE_PROPOSED from LOCAL_ONLY and ORIGINAL_HOODIE_BASELINE from CLOUD_ONLY