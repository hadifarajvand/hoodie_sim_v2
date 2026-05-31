# Implementation Plan: Feature 070

**Feature**: Topology, Timeout/Drop, and Reward Fidelity  
**Status**: Implementation branch under review; blocker-resolution refinement required  
**Depends On**: Feature 069 merged into `main`

## Summary

Feature 070 resolves the three blockers recorded by Feature 069: structured topology evidence, timeout/drop accounting, and reward equation fidelity. These three areas are related and may be implemented in one feature, but the implementation must remain phased, contract-bound, and test-driven.

The current implementation is useful because it is honest: it records blockers and prevents false pass states. The next implementation pass must attempt evidence recovery instead of only preserving blockers.

## Implementation Boundary

Expected future implementation areas may include:

- `src/analysis/topology_timeout_reward_fidelity/` for read-only evidence models and report generation.
- Targeted topology helper modules inside the same analysis package for parsing structured topology evidence.
- Targeted timeout/drop accounting helpers inside the same analysis package for contract-level terminal accounting evidence.
- Targeted reward-equation helpers inside the same analysis package for equation provenance and terminal reward evidence.
- Targeted unit and integration tests.

Forbidden unless a later Spec Kit update approves them:

- DRL training changes.
- Campaign artifact regeneration.
- Dependency or lock-file changes.
- Feature 071 or later work.
- Baseline-policy rewrites unrelated to these three blockers.
- Silent runtime changes under `src/environment/**`.

## Evidence Recovery Order

1. **Topology first**
   - Search existing repository evidence for adjacency, topology graph, legal action mapping, Figure 7 adjacency, or paper-extracted matrix.
   - If the user has already manually extracted adjacency, request it in a structured format and ingest it as manual paper evidence.
   - Convert adjacency into `neighbor_map` and validate self-destination and non-neighbor rejection.

2. **Timeout/drop second**
   - Inspect existing timeout/drop runtime code and paper mechanism registry references.
   - Encode task-level terminal accounting evidence without claiming paper-faithful semantics unless source-backed.
   - Preserve blocker status where paper semantics remain unresolved.

3. **Reward third**
   - Inspect reward timing implementation and any reward equation contract already present in the repository.
   - Recover exact equation text only if source-backed.
   - If only timing is verified, keep equation recovery blocked or assumption-backed.

4. **Integrated report last**
   - Generate a report that can mark each category independently as verified, manual-paper-evidence, assumption-backed, or blocked.

## Manual Evidence Gate

If paper evidence cannot be recovered from committed files, the implementation agent must ask for user-provided paper extraction before inventing data.

For topology, ask the user for one of these forms:

```text
edge_agent_ids: A1,A2,A3,A4
cloud_id: cloud
adjacency_edges:
A1,A2
A1,A3
A2,A3
A3,A4
```

or a square adjacency matrix with row/column labels.

For timeout/drop, ask for the paper rule in this form:

```text
timeout_rule: drop if completion_slot > arrival_slot + timeout_length
source_reference: Section/Table/Figure ...
```

For reward, ask for the exact equation text and term definitions.

Manual input must be provenance-tagged. It must not be represented as runtime-derived truth.

## Phased Execution Order

1. Confirm Feature 069 is present in `main`.
2. Read Feature 069 report implementation and blocker list.
3. Read the paper mechanism registry and paper-to-code mapping.
4. Search existing repo for topology/adjacency evidence.
5. If topology remains missing, request user-supplied structured adjacency before keeping topology blocked.
6. Build tests for topology evidence and manual evidence parsing.
7. Build tests for timeout/drop terminal accounting.
8. Build tests for reward equation and terminal reward fidelity.
9. Implement the smallest source changes needed for each contract.
10. Produce an integrated Feature 070 report.
11. Run Feature 068R + Feature 069 regression gates.
12. Run targeted Feature 070 validations.
13. Run scope audit.

## Validation Gates

- Feature 068R regression gate.
- Feature 069 mechanism report gate.
- Structured topology contract gate.
- Manual topology evidence parsing gate when user evidence is supplied.
- Neighbor legality gate.
- Timeout/drop terminal accounting gate.
- Reward equation source gate.
- Terminal reward emission gate.
- Integrated report schema gate.
- Scope audit gate.

## Do Not Proceed Gates

Do not claim a blocker is resolved if:

- Feature 069 is not present in `main`.
- The branch is stale relative to `origin/main`.
- The paper evidence for a claimed equation or topology edge is missing.
- User-provided evidence is not provenance-tagged.
- The implementation would invent topology, timeout/drop, or reward semantics.
- The implementation would require campaign output regeneration.

## Complexity Control

This feature is deliberately larger than previous features because it combines three blockers. That is acceptable only if each blocker remains independently testable and independently reportable.

## Claim Boundary

The feature may claim resolved evidence only for blockers actually closed by tests and structured source evidence. Any unresolved item must remain in the report as a blocker or assumption-backed item.
