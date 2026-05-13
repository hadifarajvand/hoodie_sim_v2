<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read
`specs/038-training-foundation-contract/plan.md`

Feature 038 scope: contract-only training foundation for HOODIE.
Do not add DRL training, neural-network code, replay execution, optimizer behavior,
or production training loops. Do not change runtime contracts, baseline policies,
topology, timeout/deadline, execution, transmission, capacity sharing, reward timing,
reward equation, or dependencies.
<!-- SPECKIT END -->

## External Reference Usage

- EdgeSimPy is approved only as a non-authoritative structural reference.
- SimPy is approved only as a secondary non-authoritative reference for generic simulation vocabulary and patterns.
- No code, class definition, semantics, queue behavior, timing logic, reward logic, or evaluation behavior may be copied, adapted, or adopted without explicit user approval.
- Any proposed borrowing must first be mapped to the HOODIE paper or recorded in the assumptions log.
- If uncertain, Codex must propose rather than implement.
