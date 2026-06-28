# Project Decisions

## OpenCode Project-Local Workflow

- Ruflo remains the shared orchestration layer for this project.
- Project-local OpenCode assets are wrappers, guards, templates, and HOODIE-specific skills.
- Do not copy the full Ruflo repository into this project.
- Keep hooks conservative and non-mutating by default.
- Keep MCP definitions templated and secret-free.
- Use Safe Implementation permissions as the default profile.
