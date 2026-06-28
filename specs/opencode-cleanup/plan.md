# Implementation Plan: OpenCode/ECC Configuration Cleanup

## Overview
This plan outlines a safe cleanup of the OpenCode/ECC configuration in the hoodie_sim_v2 repository. The approach follows a phased validation-then-execution model to ensure no destructive changes are made without proper verification.

## Requirements
- Validate current OpenCode configuration loading
- Document provider strategy (keep global, no secrets in repo)
- Organize skills appropriately 
- Review plugin installations
- Document tool usage
- Verify ECC wiring
- Make only safe, validated changes

## Architecture Changes
- Update .opencode/opencode.json skills path from "../skills" to correct location
- Potentially create .opencode/skills/ directory and move skills
- Create/update .opencode/README.md with provider documentation
- Possibly pin @tarquinen/opencode-dcp@latest to specific version

## Implementation Plan

### Phase 1: Validate OpenCode Config Loading
1. Check if .opencode/opencode.json is actually loaded by OpenCode installation
2. Look for root-level opencode.json or opencode.jsonc files
3. Verify OpenCode recognizes project agents, commands, plugins, and skills from current config
4. If .opencode/opencode.json is not loaded, stop and recommend correct config location

### Phase 2: Provider Strategy
1. Confirm provider definitions and auth should remain global by default
2. Verify no provider secrets are copied into repository
3. Create/update .opencode/README.md to document:
   - Dependency on global OpenCode provider definitions
   - Requirement for user to configure provider auth
   - No secrets should be committed
   - Any needed environment variables (without exposing values)

### Phase 3: Skills Strategy
1. Inspect ../skills directory (if exists) to determine content and ownership
2. Validate every SKILL.md frontmatter (name, description, folder name match)
3. Determine if skills are project-specific or shared
4. If project-specific: propose moving/copying to .opencode/skills/
5. If shared: propose installing globally under ~/.config/opencode/skills/
6. Show exact plan before any moves/copies
7. Update .opencode/opencode.json skills path if moving to project-local

### Phase 4: Plugin Strategy
1. Check for duplicate plugins (global vs local)
2. Determine current version of @tarquinen/opencode-dcp@latest if possible
3. Keep ecc-universal, opencode-parser, pdf, and ./plugins project-local unless clear reason to move globally
4. Do not remove pdf plugin without explicit approval
5. Pin @tarquinen/opencode-dcp@latest to specific version only if version can be determined safely

### Phase 5: Tools Strategy
1. Inspect .opencode/tools/ directory
2. Determine if commands, agents, plugins, or config reference anything in tools/
3. If unused, document as dormant
4. Do not delete unless separately approved

### Phase 6: ECC Strategy
1. Confirm ECC is fully wired:
   - ecc-universal plugin present
   - ECC commands present
   - ECC agents present
   - ECC instructions present
   - ECC plugins/hooks present if expected
   - Skills available if ECC expects them
2. Classify ECC as: plugin only, partial project install, full project install, or unclear
3. If incomplete, propose exact missing pieces

### Phase 7: Safe Changes (Only After Validation)
1. Create/update .opencode/README.md with provider documentation
2. Update skills path in .opencode/opencode.json if correct stable path verified
3. Create .opencode/skills/ and move skills if confirmed project-specific and safe
4. Pin plugin versions only if exact versions known and change is non-breaking

## Dependencies
- OpenCode CLI (v1.17.10)
- Valid .opencode/opencode.json configuration
- Access to global OpenCode config (~/.config/opencode/)
- Read access to ../skills directory (if exists)

## Risks
- HIGH: Mistakenly removing or moving critical configuration that breaks OpenCode functionality
- MEDIUM: Incorrectly identifying skill ownership leading to misplaced skills
- LOW: Documentation updates that are inaccurate but not harmful

## Estimated Complexity: MEDIUM
Estimated time: 2-3 hours for validation and planning, minimal time for actual safe changes

## Validation Approach
- Show exact files to be changed before making changes
- Show exact intended changes
- Validate configuration loading before modifications
- Confirm skill ownership before moving
- Verify plugin versions before pinning
- Document all validation steps

## Success Criteria
- Validation results documented before any changes
- Exact patch plan created showing proposed changes
- Provider strategy clearly documented
- Skills strategy defined with ownership determination
- Plugin strategy defined with version information
- ECC wiring status determined
- Remaining risks identified and documented
- Validation commands and their results shown
- Clear next recommended action provided
