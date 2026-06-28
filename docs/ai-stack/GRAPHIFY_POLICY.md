# Graphify Policy

Graphify is structural memory.

Use Graphify for:
- unfamiliar codebase exploration
- cross-module features
- refactors
- impact analysis
- dependency path questions
- PR/change risk
- paper/code alignment
- architecture audits

Do not force Graphify for:
- one-file typo fixes
- obvious local bugs
- simple copy changes
- trivial config edits

Expected queries:
- Which files implement this feature?
- What depends on this module?
- What path connects frontend component X to backend service Y?
- What files are impacted by this change?
- What tests cover this area?

Graphify output should be committed for important repos unless the project policy says otherwise.

Graphify hooks may keep AST/code graph fresh after commits.
