# Feature Specification: Topology, Timeout/Drop, and Reward Fidelity

**Feature Branch**: `070-topology-timeout-reward-fidelity`  
**Spec Branch**: `070-topology-timeout-reward-fidelity-spec-kit`  
**Implementation Branch**: `070-topology-timeout-reward-fidelity-implementation`  
**Created**: 2026-05-31  
**Updated**: 2026-05-31  
**Status**: Implementation branch under review; blocker-resolution refinement required before any merge  
**Input**: Feature 070 resolves the three blockers recorded by Feature 069: structured topology/neighbor graph evidence, timeout/drop paper-faithful accounting, and reward equation / terminal reward fidelity.

## Dependency

Feature 070 depends on Feature 069 being merged into `main` at or after merge commit `8e3aaf7a691917a473f2ccc89d89d0d4b5689ced`.

Feature 069 established mechanism-fidelity readiness but explicitly recorded these blockers:

1. Structured topology adjacency is unavailable as a structured artifact.
2. Timeout/drop paper-faithful semantics remain unresolved.
3. Reward-equation fidelity remains assumption-backed.

Feature 070 is allowed to address all three, but only through a phased contract. It must not collapse them into one vague implementation blob.

## Goal

Create a defensible, paper-grounded fidelity layer that converts the three Feature 069 blockers into structured contracts, targeted tests, source evidence, and explicit claim boundaries.

## Blocker-Resolution Upgrade

The first implementation pass correctly prevented false `passed=True` reports, but it still preserved all three blockers. The next pass must try to actually resolve them where evidence exists.

Resolution means:

- **Topology**: convert paper-backed or user-extracted adjacency into a structured topology artifact and validate neighbor legality from that artifact.
- **Timeout/drop**: recover the terminal accounting rule from existing runtime/paper evidence and distinguish verified semantics from blocker-backed semantics.
- **Reward**: recover the reward equation or explicitly encode the exact missing terms; terminal reward timing alone is not reward-equation fidelity.

## Evidence Intake Rule

Feature 070 may accept user-provided evidence only when it is explicitly marked as manual paper extraction. User-provided topology adjacency, timeout/drop semantics, or reward equation text must include:

- evidence category: `topology`, `timeout_drop`, or `reward`
- source reference: paper figure/table/section or user extraction note
- extraction method: manual, OCR, code-derived, or runtime-derived
- confidence: verified, assumption-backed, or blocked
- reviewer note explaining why the evidence is accepted

Manual evidence is allowed as structured evidence only if tests can validate its shape and the final report clearly marks its provenance. Do not hide manual evidence as runtime truth.

## User Stories

### US1 - Structured topology and neighbor graph evidence
As a researcher, I need topology adjacency and neighbor legality to exist as structured evidence so horizontal offloading and coordination claims are not built on informal assumptions.

### US2 - Timeout and drop accounting
As a researcher, I need task timeout, deadline, completion, and drop accounting to be explicitly tied to terminal task state so delay/drop metrics are not hand-waved.

### US3 - Reward equation and terminal reward fidelity
As a researcher, I need the reward equation and terminal reward emission path to be recovered, encoded, or explicitly blocked so the DRL objective is not fake-paper-faithful.

### US4 - Integrated blocker-resolution report
As a reviewer, I need a final report that says exactly what was verified, what remained assumption-backed, and what still blocks full paper reproduction.

## Acceptance Criteria

- A structured topology/neighbor graph contract exists and is tested.
- Horizontal neighbor legality is validated against structured topology evidence.
- If user-extracted topology evidence is supplied, it is parsed, validated, provenance-tagged, and used instead of the current blocked empty topology.
- Timeout/drop accounting is represented with task-level terminal-state evidence and tests.
- Completed tasks cannot be counted as dropped; dropped tasks must have terminal evidence.
- Reward equation recovery is represented with source/equation evidence and terminal reward tests.
- `passed=True` is impossible while topology, timeout/drop, or reward blockers remain unresolved.
- Feature 068R and Feature 069 targeted validations remain green.
- The final report separates verified behavior, paper-backed behavior, user-provided evidence, assumption-backed behavior, compatibility fallback, and unresolved blockers.
- The feature does not claim full paper reproduction unless all three blockers are actually resolved with evidence.

## Out of Scope

- Training a DRL agent.
- Running or regenerating campaign outputs.
- Broad full-suite cleanup.
- Dependency or lock-file changes.
- New baseline policy semantics unrelated to topology, timeout/drop, or reward fidelity.
- Feature 071 or later scope.

## Regression Guard

Feature 070 must not weaken:

- Feature 068R baseline placement fidelity.
- Feature 069 mechanism report and scope guard behavior.
- Existing legal-mask authority.
- Existing family-level compatibility fallback.
- Existing delayed reward timing tests.

## Claim Boundary

Feature 070 may claim blocker-resolution readiness only for the blocker categories that have structured evidence and passing targeted tests. If any of topology, timeout/drop, or reward remains incomplete, the final report must say so plainly.
