# SRC-001 Independent Review — Attempt 1

Verdict: REWORK

The branch is one commit ahead of the authorized control commit and changes only the seven permitted G1 evidence files. The BLOCKED_EXTERNAL disposition is internally consistent: no source snapshot, verifier, test, or 69-row audit is claimed.

Evidence-integrity failures:

1. `git_diff.patch` is not the exact branch diff. It contains only a short fragment for `report.md` and omits the remaining changed files and most changed lines.
2. `hashes.json` verifies five evidence files but omits `git_diff.patch`. A self-hash for `hashes.json` is not required, but every other G1 file must be covered.

The listed hashes for `report.md`, `status.json`, `commands.txt`, `test_output.txt`, and `changed_files.json` match their committed contents. `changed_files.json` exactly matches the seven changed paths.

No implementation or source-lock work is requested in rework attempt 2. The executor must regenerate a complete `git_diff.patch`, add its SHA-256 to `hashes.json`, retain BLOCKED_EXTERNAL, commit the corrected seven-file G1 package, and stop.
