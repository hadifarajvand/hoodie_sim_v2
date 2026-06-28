# OpenCode/ECC Configuration Cleanup Plan

## Problem Statement
The hoodie_sim_v2 repository has accumulated OpenCode/ECC configuration over time that needs cleanup and organization. The current state includes:
- Global provider definitions in ~/.config/opencode/opencode.jsonc
- Project-specific configuration in .opencode/opencode.json
- Skills referenced from ../skills (which doesn't exist)
- Various plugins installed
- ECC components that need verification
- Potential cleanup opportunities in .opencode/tools/

## Goal
Create a safe cleanup plan that:
1. Validates current configuration loading
2. Documents provider strategy (keep global, no secrets in repo)
3. Organizes skills appropriately (move project-specific skills to .opencode/skills/)
4. Reviews plugin installations for duplication and version pinning
5. Documents tool usage in .opencode/tools/
6. Verifies ECC is properly wired
7. Makes only safe, non-destructive changes after validation

## Requirements
- Do not commit, push, or alter Git history
- Do not remove .opencode/tools/ without separate approval
- Do not remove plugins without confirming duplication and getting separate approval
- Do not copy provider secrets into repository
- Show exact files to be changed and intended changes before editing
- Stop if .opencode/opencode.json is not loaded and recommend correct location

## Success Criteria
- Validation results documented
- Exact patch plan created showing files to change
- Provider strategy defined and documented
- Skills strategy defined and documented
- Plugin strategy defined and documented
- ECC status determined
- Remaining risks identified
- Validation commands and results shown
- Next recommended action provided

## Constraints
- No destructive changes without explicit approval
- No committing/pushing/pulling
- No package installation
- No copying of raw provider secrets
- Must show exact changes before making them
