# Implementation Tasks: OpenCode/ECC Configuration Cleanup

## Phase 1: Validate OpenCode Config Loading

### 1.1 Check OpenCode version and basic functionality
- Command: `opencode --version`
- Expected: Shows version 1.17.10 or similar
- Dependencies: None
- Risk: Low

### 1.2 Check for root-level opencode.json or opencode.jsonc
- Command: `ls -la | grep -E "opencode\.json"`
- Expected: No files found (based on earlier check)
- Dependencies: None
- Risk: Low

### 1.3 Verify .opencode/opencode.json is valid JSON
- Command: `cat .opencode/opencode.json | python3 -m json.tool > /dev/null && echo "Valid JSON"`
- Expected: Returns "Valid JSON"
- Dependencies: None
- Risk: Low

### 1.4 Check if OpenCode loads project config (indirect verification)
- Since we can't directly see config loading, we'll validate the config file exists and is properly formatted
- Command: `ls -la .opencode/opencode.json`
- Expected: File exists and is readable
- Dependencies: None
- Risk: Low

## Phase 2: Provider Strategy

### 2.1 Examine global OpenCode config for provider definitions
- Command: `cat ~/.config/opencode/opencode.jsonc`
- Expected: Shows provider definitions for "local" and "free"
- Dependencies: None
- Risk: Low

### 2.2 Check for any provider secrets in repository
- Command: `grep -r -i "key\|token\|secret\|password\|auth" .opencode/ --exclude-dir=.git || echo "No obvious secrets found"`
- Expected: No actual secrets found (may show parameter names but not values)
- Dependencies: None
- Risk: Low

### 2.3 Create/update .opencode/README.md with provider documentation
- File: `.opencode/README.md`
- Action: Create or update with provider strategy documentation
- Content to include:
  * This repo depends on global OpenCode provider definitions
  - Provider auth must be configured by the user globally
  - No secrets should be committed to this repository
  - Environment variables needed (if any can be determined without exposing values)
- Dependencies: None
- Risk: Low

## Phase 3: Skills Strategy

### 3.1 Check if ../skills directory exists
- Command: `ls -la ../skills/ 2>/dev/null || echo "../skills directory does not exist"`
- Expected: "../skills directory does not exist" (based on earlier check)
- Dependencies: None
- Risk: Low

### 3.2 Check .agents/skills directory (current skills location)
- Command: `ls -la .agents/skills/`
- Expected: List of speckit skills directories
- Dependencies: None
- Risk: Low

### 3.3 Validate SKILL.md frontmatter in .agents/skills/
- Command: For each skill directory, check for SKILL.md and validate name/description exist
- Example: `ls .agents/skills/speckit-plan/SKILL.md && head -5 .agents/skills/speckit-plan/SKILL.md`
- Expected: Each SKILL.md exists with name and description fields
- Dependencies: None
- Risk: Low

### 3.4 Determine if skills are project-specific or shared
- Analysis: The speckit skills in .agents/skills/ appear to be project-specific Speckit workflow skills
- Dependencies: None
- Risk: Low

### 3.5 Propose moving project-specific skills to .opencode/skills/
- Plan: Create .opencode/skills/ directory and copy speckit skills from .agents/skills/
- Note: Will not execute until validation confirmed
- Dependencies: Completion of validation steps
- Risk: Low (if done correctly)

### 3.6 Update .opencode/opencode.json skills path if moving to project-local
- File: `.opencode/opencode.json`
- Change: Update "skills.paths" from ["../skills"] to ["./skills"] if skills moved
- Dependencies: Skills moved to .opencode/skills/
- Risk: Low (if skills correctly moved)

## Phase 4: Plugin Strategy

### 4.1 List current project plugins from opencode.json
- Command: `grep -A 20 '"plugin":' .opencode/opencode.json`
- Expected: Shows plugins: ["./plugins", "ecc-universal", "opencode-parser", "pdf", "@tarquinen/opencode-dcp@latest"]
- Dependencies: None
- Risk: Low

### 4.2 Check for ./plugins directory (local plugins)
- Command: `ls -la .opencode/plugins/`
- Expected: Shows ecc-hooks.ts, index.ts, lib/ directory
- Dependencies: None
- Risk: Low

### 4.3 Check if any plugins are duplicated globally
- This requires checking global OpenCode plugins, which is complex without direct access
- We'll assume no duplication unless evidence suggests otherwise
- Dependencies: None
- Risk: Low

### 4.4 Determine version of @tarquinen/opencode-dcp@latest
- Since we can't safely install packages, we'll note that version pinning should only be done if version can be determined from lockfile or similar safe method
- Command: `grep -A 5 -B 5 "opencode-dcp" .opencode/opencode.json`
- Expected: Shows "@tarquinen/opencode-dcp@latest"
- Dependencies: None
- Risk: Low

### 4.5 Verify ecc-universal, opencode-parser, pdf, and ./plugins should remain project-local
- Analysis: These appear to be project-specific ECC and utility plugins
- Dependencies: None
- Risk: Low

### 4.6 Plan to pin @tarquinen/opencode-dcp@latest only if version can be determined safely
- Condition: Only if we can determine version without installing packages
- Action: If package-lock.json or similar shows version, pin to that version
- Dependencies: Ability to determine version safely
- Risk: Low (if version known)

## Phase 5: Tools Strategy

### 5.1 Inspect .opencode/tools/ directory
- Command: `ls -la .opencode/tools/`
- Expected: To be determined
- Dependencies: None
- Risk: Low

### 5.2 Check if any components reference tools/
- Command: `grep -r "tools" .opencode/ --include="*.json" --include="*.jsonc" || echo "No references to tools found in config"`
- Expected: To be determined
- Dependencies: None
- Risk: Low

### 5.3 Document tools/ as dormant if unused
- Condition: If no references found and no apparent use
- Action: Document in plan that tools/ appears dormant
- Dependencies: Completion of inspection
- Risk: Low

## Phase 6: ECC Strategy

### 6.1 Check for ecc-universal plugin
- Command: `grep "ecc-universal" .opencode/opencode.json`
- Expected: Should find "ecc-universal" in plugins array
- Dependencies: None
- Risk: Low

### 6.2 Check for ECC commands
- Command: `ls -la .opencode/commands/ | grep -i ecc || echo "No ECC-specific commands found"`
- Expected: To be determined
- Dependencies: None
- Risk: Low

### 6.3 Check for ECC agents
- Command: `ls -la .opencode/agent/ | grep -i ecc || echo "No ECC-specific agents found"`
- Expected: To be determined
- Dependencies: None
- Risk: Low

### 6.4 Check for ECC instructions
- Command: `ls -la .opencode/instructions/ | grep -i ecc || echo "No ECC-specific instructions found"`
- Expected: To be determined
- Dependencies: None
- Risk: Low

### 6.5 Check for ECC plugins/hooks
- Command: `ls -la .opencode/plugins/ | grep -i ecc || echo "No ECC-specific plugins found in ./plugins/"`
- Expected: We already saw ecc-hooks.ts in plugins/
- Dependencies: None
- Risk: Low

### 6.6 Check if ECC expects specific skills
- This would require checking ECC documentation or known requirements
- We'll note this as needing investigation if ECC components are found
- Dependencies: ECC components found
- Risk: Low

### 6.7 Classify ECC installation status
- Based on findings above, classify as:
  - plugin only (only ecc-universal plugin present)
  - partial project install (some ECC components present)
  - full project install (complete ECC setup)
  - unclear (insufficient information)
- Dependencies: All ECC checks completed
- Risk: Low

### 6.8 Propose missing pieces if ECC incomplete
- Condition: If ECC classified as less than "full project install"
- Action: List exactly what's missing for a complete ECC setup
- Dependencies: ECC classification
- Risk: Low

## Phase 7: Safe Changes (Only After Validation)

### 7.1 Create/update .opencode/README.md
- File: `.opencode/README.md`
- Action: Create or update with provider documentation
- Content:
  ```
  # OpenCode Configuration

  This repository relies on global OpenCode provider definitions configured in ~/.config/opencode/opencode.jsonc.

  ## Provider Configuration
  - Provider definitions and authentication must be configured globally by the user
  - No provider secrets should be committed to this repository
  - Refer to global OpenCode documentation for provider setup instructions

  ## Environment Variables
  (List any non-sensitive environment variables needed, if determinable)
  ```
- Dependencies: Validation completed
- Risk: Low

### 7.2 Create .opencode/skills/ directory (if skills are project-specific)
- Condition: After validating skills are project-specific and safe to move
- Command: `mkdir -p .opencode/skills/`
- Dependencies: Skills validation completed
- Risk: Low

### 7.3 Copy project-specific skills to .opencode/skills/ (if applicable)
- Condition: After validating skills are project-specific and safe to move
- Command: `cp -r .agents/skills/speckit-* .opencode/skills/`
- Dependencies: .opencode/skills/ directory created
- Risk: Low (preserves originals until verified)

### 7.4 Update skills path in .opencode/opencode.json (if moving skills)
- File: `.opencode/opencode.json`
- Change: Modify "skills.paths" from ["../skills"] to ["./skills"]
- Dependencies: Skills copied to .opencode/skills/
- Risk: Low (if paths correct)

### 7.5 Pin @tarquinen/opencode-dcp@latest to specific version (if version known safely)
- Condition: After validating version can be determined without package installation
- File: `.opencode/opencode.json`
- Change: Replace "@tarquinen/opencode-dcp@latest" with specific version like "@tarquinen/opencode-dcp@1.0.0"
- Dependencies: Version determined safely
- Risk: Low (if version correct)

## Validation Commands Summary

All validation commands should be run and results documented before proceeding to Phase 7.

1. `opencode --version`
2. `ls -la | grep -E "opencode\.json"`
3. `cat .opencode/opencode.json | python3 -m json.tool > /dev/null && echo "Valid JSON"`
4. `ls -la .opencode/opencode.json`
5. `cat ~/.config/opencode/opencode.jsonc`
6. `grep -r -i "key\|token\|secret\|password\|auth" .opencode/ --exclude-dir=.git || echo "No obvious secrets found"`
7. `ls -la ../skills/ 2>/dev/null || echo "../skills directory does not exist"`
8. `ls -la .agents/skills/`
9. `ls .agents/skills/speckit-plan/SKILL.md && head -5 .agents/skills/speckit-plan/SKILL.md` (repeat for each skill)
10. `grep -A 20 '"plugin":' .opencode/opencode.json`
11. `ls -la .opencode/plugins/`
12. `ls -la .opencode/tools/`
13. `grep -r "tools" .opencode/ --include="*.json" --include="*.jsonc" || echo "No references to tools found in config"`
14. `grep "ecc-universal" .opencode/opencode.json`
15. `ls -la .opencode/commands/ | grep -i ecc || echo "No ECC-specific commands found"`
16. `ls -la .opencode/agent/ | grep -i ecc || echo "No ECC-specific agents found"`
17. `ls -la .opencode/instructions/ | grep -i ecc || echo "No ECC-specific instructions found"`
18. `ls -la .opencode/plugins/ | grep -i ecc || echo "No ECC-specific plugins found in ./plugins/"`

## Expected Files Changed (if all safe actions proceed)

IF AND ONLY IF all validations pass and user approves:
1. `.opencode/README.md` - Created or updated
2. `.opencode/skills/` directory - Created (if skills are project-specific)
3. `.opencode/skills/speckit-*` - Copied from .agents/skills/ (if skills are project-specific)
4. `.opencode/opencode.json` - Skills path updated from "../skills" to "./skills" (if skills moved)
5. `.opencode/opencode.json` - @tarquinen/opencode-dcp@latest pinned to specific version (if version known safely)

## Files Intentionally Not Changed (unless separately approved)

- `.opencode/tools/` - Left unchanged unless explicit approval given for modification/deletion
- Any plugin in `.opencode/plugins/` or listed in opencode.json - Left unchanged unless duplication proven and explicit approval given for removal
- Global OpenCode configuration (`~/.config/opencode/opencode.jsonc`) - Never modified

## Provider Strategy Chosen
Keep provider definitions and authentication global by default. Document that users must configure providers globally and never commit secrets to repository.

## Skills Strategy Chosen
If skills are project-specific (as speckit skills appear to be), move them to .opencode/skills/ and update opencode.json to reference "./skills". If skills are shared, recommend installing globally to ~/.config/opencode/skills/.

## Plugin Strategy Chosen
Keep ecc-universal, opencode-parser, pdf, and ./plugins as project-local. Only pin @tarquinen/opencode-dcp@latest to specific version if version can be determined safely without package installation. Do not remove any plugins without explicit approval.

## ECC Status After Cleanup
To be determined after validation phase.

## Remaining Risks
- Misidentification of skill ownership (project-specific vs shared)
- Incorrect version pinning if version cannot be determined safely
- Overlooking subtle configuration dependencies
- Potential incompatibilities from reorganization (though we're being conservative)

## Next Recommended Action
Complete all validation phases and document results before proceeding to any changes. Review validation results with user before executing Phase 7.
