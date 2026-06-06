# Research: Runtime Adoption of Approved Assumption Registry

## Decision 1: Consume the approved registry directly

- Decision: Runtime adoption reads approved assumption data directly from `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` and the Feature 031 report artifact.
- Rationale: Direct consumption preserves provenance and avoids a copied runtime artifact that could drift from the approved snapshot.
- Alternatives considered: Copying adjacency or value data into a separate artifact; rejected because it weakens provenance and creates duplication risk.

## Decision 2: Topology legality remains neighbor-only for horizontal offload

- Decision: Enforce horizontal legality through the approved Figure 7 adjacency with self-offload and non-neighbor horizontal offload blocked.
- Rationale: This aligns runtime action legality with the approved topology assumption and keeps vertical/cloud routing separate.
- Alternatives considered: Allowing unrestricted horizontal destinations; rejected because it conflicts with the approved topology assumption.

## Decision 3: Link-rate adoption keeps a single vertical cloud-facing rate

- Decision: Use `R_V = 10 Mbps` as the cloud-facing vertical rate and keep the horizontal rate unchanged at `30 Mbps`.
- Rationale: The approved registry contains a single vertical/cloud-facing assumption; inventing a separate cloud-only rate would violate provenance.
- Alternatives considered: Introducing a distinct cloud-specific rate; rejected because it is not supported by Feature 031.

## Decision 4: Timeout adoption is a direct runtime contract

- Decision: Use `timeout_slots = 20`, `slot_duration_seconds = 0.1`, and `timeout_seconds = 2.0` as the runtime timeout contract.
- Rationale: These values are already explicit in the approved assumption registry and can be validated end-to-end.
- Alternatives considered: Recomputing timeout dynamically from campaign defaults; rejected because it would break the adoption contract.

## Decision 5: Aggregation is a shared helper/contract

- Decision: Implement reward aggregation as a shared helper/contract used by runtime and reporting code.
- Rationale: A shared helper prevents axis mismatch and keeps runtime/report semantics synchronized.
- Alternatives considered: Campaign reruns or duplicated aggregation logic; rejected because both increase drift risk.

