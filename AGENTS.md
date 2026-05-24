<!-- SPECKIT START -->
Use `docs/spec-kit-workflow/` as the repository-level SpecKit operating contract.

Feature-specific scope belongs in `specs/<feature-id>/`.
Do not write feature-specific plan/spec pointers into AGENTS.md.
Do not use AGENTS.md as an active feature pointer.
`.specify/feature.json` is local-only and must not be committed.
<!-- SPECKIT END -->

## External Reference Usage

- EdgeSimPy is approved only as a non-authoritative structural reference.
- SimPy is approved only as a secondary non-authoritative reference for generic simulation vocabulary and patterns.
- No code, class definition, semantics, queue behavior, timing logic, reward logic, or evaluation behavior may be copied, adapted, or adopted without explicit user approval.
- Any proposed borrowing must first be mapped to the HOODIE paper or recorded in the assumptions log.
- If uncertain, Codex must propose rather than implement.
