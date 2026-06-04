# Feature 085 Requirements Checklist

## Checklist Gate Policy

These items are intentionally incomplete before implementation. Do not mark an item complete until real code, generated artifacts, and tests prove it.

When Codex asks whether to proceed with incomplete checklists, answer yes and proceed with implementation. The incomplete state is the implementation gap, not a reason to fake completion.

## Requirements

- [ ] HOODIE represented as the only proposed method.
- [ ] MQO removed from active audit outputs and replaced by MLEO.
- [ ] RO baseline implemented and labeled correctly.
- [ ] FLC baseline implemented and labeled correctly.
- [ ] VO baseline implemented and labeled correctly.
- [ ] HO baseline implemented and labeled correctly.
- [ ] BCO baseline implemented and labeled correctly.
- [ ] MLEO baseline implemented and labeled correctly.
- [ ] Baseline mapping matrix documents canonical and legacy labels.
- [ ] Formula-to-code mapping matrix exists and covers all required rows.
- [ ] Audit report includes baseline fidelity proof and formula audit proof.
- [ ] Artifact bundle is regenerated with the canonical baseline set.

## Completion Rule

This checklist may become complete only after Feature 085 implementation produces artifacts with exactly this active policy set:

- HOODIE
- RO
- FLC
- VO
- HO
- BCO
- MLEO

`MQO` must not appear as an active policy in final artifacts.
