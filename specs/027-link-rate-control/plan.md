# Implementation Plan: Link-Rate Control and Transmission Delay Contract

**Branch**: `[027-link-rate-control-transmission-delay-contract]` | **Date**: 2026-05-11 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/027-link-rate-control/spec.md`

## Summary

Deliver a public, config-backed link-rate control contract for horizontal and vertical defaults and an explicit transmission-delay contract that is deterministic, unit-safe, and testable. The feature must preserve the unrecoverable status of cloud rate and Figure 7 adjacency, avoid curve fitting or topology fabrication, and clearly mark per-edge/offload link-rate control unsupported unless a runtime-backed non-paper hook exists.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules, standard library, recovered paper registry artifacts, analysis/report helpers  
**Storage**: JSON, Markdown, and optional CSV artifacts under `artifacts/analysis/link-rate-transmission-delay-contract/` and `specs/027-link-rate-control/`  
**Testing**: `unittest`-based unit and integration tests for conversion, delay monotonicity, environment reachability, and scope guards  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal environment contract and analysis feature  
**Performance Goals**: Deterministic contract evaluation with stable artifact generation; no extra runtime sweep cost  
**Constraints**: No simulator behavior changes unless a failing test proves a real bug and the repair is documented; no policy redesign; no metric redesign except explicit delay reporting if already part of accounting; no training; no neural-network code; no TorchRL; no Gymnasium; no ns-3; no ns-3-gym; no dependency or lockfile changes; no campaign reruns; no paper-validity claim  
**Scale/Scope**: A narrow environment-control contract covering horizontal and vertical defaults, unsupported per-edge requests, and validation artifacts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitution Gate

- [x] Dependency impact checked
- [x] Environment impact checked
- [x] Assumption impact checked
- [x] Fidelity impact checked
- [x] Test impact checked
- [x] Reproducibility impact checked
- [x] Config/schema impact checked
- [x] Public interface impact checked
- [x] Artifact impact checked
- [x] Security/secret impact checked
- [x] Performance budget impact checked
- [x] Baseline fairness impact checked
- [x] Paper-to-code mapping impact checked
- [x] Definition-of-done impact checked

This feature is only valid if it preserves the hard boundary between paper-backed horizontal/vertical defaults and unsupported per-edge/offload requests. It may not infer cloud rate or adjacency from simulator behavior.

## Project Structure

### Documentation (this feature)

```text
specs/027-link-rate-control/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── transmission-delay-contract.md
```

### Source / Artifacts (repository root)

```text
src/environment/
├── compute_config.py
├── environment.py
├── gym_adapter.py
├── offload_trace_ledger.py
├── offload_trace_schema.py
├── runtime_model.py
└── topology.py

src/analysis/structured_paper_topology_linkrate_registry/
├── recovery.py
├── registry.py
└── report.py

src/audits/
└── differential_environment/
    ├── audit.py
    ├── classify.py
    ├── report.py
    └── runner.py

tests/unit/
├── test_compute_config.py
├── test_structured_paper_topology_linkrate_registry.py
├── test_offload_trace_schema.py
└── test_link_rate_transmission_delay_contract.py

tests/integration/
├── test_structured_paper_topology_linkrate_registry_no_fabrication.py
├── test_offload_instrumentation_scope_guard.py
├── test_link_rate_control_horizontal.py
├── test_link_rate_control_vertical.py
├── test_link_rate_control_monotonicity.py
└── test_link_rate_control_scope_guard.py

artifacts/analysis/link-rate-transmission-delay-contract/
├── link-rate-contract-report.json
├── link-rate-contract-report.md
└── link-rate-contract-report.csv (optional if consistent with project style)
```

**Structure Decision**: Keep link-rate contract logic inside the environment and analysis layers already used by HOODIE. Reuse the structured paper registry as the source of paper-backed horizontal and vertical defaults. Keep unsupported per-edge/offload controls out of the code path unless a runtime-backed non-paper hook can prove legality.

## Phase 0: Research

1. Confirm the recovered registry exposes horizontal = 30 Mbps and vertical = 10 Mbps while leaving cloud rate and Figure 7 adjacency unrecoverable.
2. Inspect the environment boundary for a public configuration path that can carry horizontal and vertical rate overrides without changing policy, metrics, or training code.
3. Define deterministic unit conversion rules for bits, Mbits, bps, Mbps, seconds, and simulator slots.
4. Determine how transmission delay should be reported without altering metric formulas or topology legality.
5. Confirm the correct failure mode for zero or negative rates and ambiguous unit inputs.

## Phase 1: Design & Contracts

1. Define the link-rate config model and conversion rules in `data-model.md`.
2. Define the exact transmission-delay contract and rounding policy in `contracts/transmission-delay-contract.md`.
3. Define the validation and reproduction steps in `quickstart.md`.
4. Record the default paper-backed values and unsupported scope boundaries in the research notes.
5. Update `AGENTS.md` to point at this plan file for Feature 027.
6. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Read the recovered topology and parameter registry first.
2. Add a public configuration contract for horizontal and vertical rate control only.
3. Implement explicit, deterministic unit conversion helpers for rates, payload sizes, and slot/time conversion.
4. Define the transmission-delay contract in a way tests can exercise directly and environment integration can observe without curve fitting.
5. Mark per-edge/offload link-rate control unsupported unless a runtime-backed non-paper hook exists.
6. Emit validation artifacts that separate schema support from actually controllable rate effects.

## Validation Strategy

1. Unit tests validate conversion rules, rate bounds, zero/negative handling, and delay formula behavior.
2. Integration tests validate public environment reachability for horizontal and vertical rate control.
3. Monotonicity tests confirm higher controllable rates do not increase delay for the same payload.
4. Regression tests ensure Feature 026 observability remains intact.
5. Scope-guard tests reject policy, metric, training, dependency, lockfile, campaign, and topology fabrication drift.

## Risks and Constraints

- Per-edge/offload link-rate control may remain unsupported because topology legality is unrecoverable; it must not be invented.
- Transmission delay may exist only as an explicit contract/reporting layer if the environment accounting path cannot expose it without metric redesign.
- Unit conversion bugs are easy to hide; every conversion rule needs a direct test, not just a derived integration check.

## Deliverables

- `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json`
- `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.md`
- optional `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.csv`
- `specs/027-link-rate-control/research.md`
- `specs/027-link-rate-control/data-model.md`
- `specs/027-link-rate-control/quickstart.md`
- `specs/027-link-rate-control/contracts/transmission-delay-contract.md`
