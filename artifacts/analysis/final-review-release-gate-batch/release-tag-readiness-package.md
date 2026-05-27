# Release Tag Readiness Package

- recommended_release_tag: `hoodie-mechanism-evidence-release-v1`

## Post-Merge Tag Commands
- `git tag -a hoodie-mechanism-evidence-release-v1 -m "Release tag for final reviewed HOODIE evidence"`
- `git push origin hoodie-mechanism-evidence-release-v1`

## Prerequisites
- merge Feature 064 to the release branch first
- confirm no forbidden paths are dirty
- confirm release notes are ready

## Tag Creation Boundary
- This feature does not create the tag.

## Rollback / Repair Note
If any final gate fails, repair the failing gate before tagging; do not create the tag from this feature.
