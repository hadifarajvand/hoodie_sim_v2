# Implementation Plan: Feature 068

**Branch**: `068-paper-baseline-policy-fidelity-batch`  
**Date**: 2026-05-30  
**Spec**: `spec.md`  
**Status**: Ready for implementation handoff

## Summary

Feature 068 is a bounded baseline-policy fidelity batch. Feature 068R extends it and does not replace it. The branch constrains the implementation of RO, FLC, VO, HO, BCO, and MLEO so those baselines can be compared through one registry, one policy interface, one action-mask contract, and one testable behavior set. The main implementation risk is MLEO: it must rank available candidates by total estimated delay, keep the legal mask authoritative, and expose a documented fallback when observations are incomplete.

## Technical Context

- Language: Python.
- Dependencies: existing repository dependencies only.
- Test style: existing unit and integration conventions.
- Primary runtime boundary: policy layer and policy registry.
- Primary files expected during implementation: `src/policies/`, `src/evaluation/policy_registry.py`, `tests/unit/`, and `tests/integration/`.
- Forbidden implementation areas: `src/environment/`, `src/training/`, `src/agents/`, generated artifacts, dependency files, and campaign outputs.

## Constitution Check

- Dependency control: PASS. No new dependency is allowed.
- Environment fidelity: PASS with constraint. No simulator lifecycle, traffic, or reward behavior may change.
- Policy interface: IMPACTED. Baseline policies and registry are the intended interface.
- Testing standard: REQUIRED. Test-first implementation is required for every behavior repair.
- Artifact lifecycle: PASS. No generated artifacts are refreshed.
- Assumption discipline: REQUIRED. MLEO fallback behavior must be documented if observation fields are incomplete.
- Hardening discipline: REQUIRED. Feature 068R must preserve the prior Feature 068 registry coverage, mask compliance, fallback behavior, seeded RO behavior, BCO balance_hint behavior, and MLEO metadata contracts.
- Test integrity: REQUIRED. Feature 068R must not pass by deleting, weakening, or replacing prior Feature 068 tests.
- Mask authority: REQUIRED. A placement payload may describe a candidate, but the legal-action mask remains the final authority on availability.
- Claim safety: REQUIRED. This feature may claim baseline-policy fidelity only, not paper reproduction.

## Project Structure

```text
specs/068-paper-baseline-policy-fidelity-batch/
  spec.md
  plan.md
  research.md
  data-model.md
  quickstart.md
  tasks.md
  checklists/requirements.md

src/policies/
  common.py
  flc.py
  vo.py
  ho.py
  ro.py
  bco.py
  mleo.py
  policy_interface.py

src/evaluation/
  policy_registry.py

tests/unit/
  test_policy_registry.py
  test_baseline_policy_fidelity.py
  test_mleo_policy.py

tests/integration/
  test_baseline_policy_fidelity_flow.py
```

## Phase 0: Research Decisions

### Decision 1: Baseline repair stays in the policy layer

Rationale: Changing environment behavior while repairing baselines would mix two concerns and make fairness claims impossible to audit.

### Decision 2: Registry coverage is the first gate

Rationale: If a baseline cannot be requested by name, later tests and campaigns cannot use it consistently.

### Decision 3: Action mask is applied before preference

Rationale: Policy preference cannot override topology, current state, or action availability.

### Decision 4: MLEO ranks candidates by total delay

Rationale: A minimum-latency baseline must compare candidate totals, not fixed preferences.

### Decision 5: Fallbacks are visible

Rationale: Missing fields are expected while simulator exposure evolves. A visible fallback is honest; a hidden fallback creates fake fidelity.

## Phase 1: Design and Contracts

### BaselinePolicy contract

Every baseline must accept shared policy input and return a selected action or documented no-choice result. Behavior must be deterministic unless the policy is explicitly seeded random.

### PolicyContext contract

PolicyContext is the input boundary. It provides observation, action mask, optional trace history, and optional seed or RNG information. Baselines must not inspect environment internals directly.

### DelayCandidate contract

MLEO candidate fields: action family, action id or alias, availability, queue delay, transmission delay, compute delay, total delay, tie-break key, and fallback notes.

### Fallback contract

Fallback is allowed only when the preferred action is unavailable, required MLEO estimate fields are incomplete, or no candidate is comparable. Fallback must be documented and tested.

### Compatibility contract

Placement-level repair is additive. If only family-level actions are exposed, baselines may keep the documented family-level fallback behavior, but that compatibility path must not be described as paper-exact placement fidelity.

### Mask authority contract

For placement candidates, `legal_action_mask` is authoritative. A candidate payload cannot override a false mask entry by marking itself available.

## Validation Gates

- Registry coverage gate.
- Action-mask compliance gate.
- RO seeding gate.
- BCO balancing gate.
- MLEO ranking gate.
- MLEO fallback gate.
- Controlled differentiation gate.
- Scope audit gate.

## Complexity Tracking

No additional complexity is approved. If implementation requires new simulator fields, new config schema, or generated artifacts, stop and report the blocker instead of expanding scope.

## Implementation Boundary

Allowed: policy modules, policy registry, unit tests, integration tests, and feature documentation notes.

Forbidden: simulator lifecycle behavior, traffic generation, reward timing, HOODIE training logic, generated artifact refresh, and dependency changes.

## Validation Commands

Use the approved interpreter when available:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests/unit
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests/integration
```

If that interpreter is unavailable, use the project interpreter and record the exact command.

## Done Criteria

- Required baselines resolve.
- Tests prove mask compliance.
- MLEO ranks available candidates by total delay.
- MLEO fallback behavior is explicit.
- Placement-level behavior is additive and keeps family-level compatibility intact.
- The legal-action mask always wins over payload availability metadata.
- Controlled differentiation tests exist.
- No forbidden paths changed.
- Implementation report lists commands, results, changed files, and risks.
