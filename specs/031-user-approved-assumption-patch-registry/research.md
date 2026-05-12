# Research: User-Approved Assumption Patch Registry

## Decision 1: Registry scope is analysis-only
- **Decision**: The feature will generate a registry and report only; it will not mutate simulator runtime behavior.
- **Rationale**: Feature 030 established that the paper evidence is exhausted. This feature must only record user-approved assumptions, not reclassify paper gaps.
- **Alternatives considered**: Immediate runtime config patching was rejected because it would conflate registry creation with behavioral change.

## Decision 2: Runtime approval is a hard gate
- **Decision**: `runtime_use_allowed` can be true only when `assumption_status = approved`.
- **Rationale**: Proposed assumptions are audit artifacts, not operational inputs.
- **Alternatives considered**: Allowing proposed assumptions to be used at runtime was rejected because it weakens the approval boundary.

## Decision 3: Paper status remains immutable
- **Decision**: Registry entries preserve `paper_status` separately from `assumption_status`.
- **Rationale**: This prevents any assumption record from being mistaken for recovered paper evidence.
- **Alternatives considered**: Overwriting paper status with assumption status was rejected as scientifically misleading.

## Decision 4: Manual values are required where no safe default exists
- **Decision**: `Figure_7_adjacency`, `legal_horizontal_destinations`, and `timeout_value` remain blocked without explicit user values.
- **Rationale**: Those items would require topology or deadline invention if auto-filled.
- **Alternatives considered**: Auto-generating topology or deadlines was rejected because it would fabricate unsupported inputs.

## Decision 5: Safe proposed defaults are allowed for selected runtime assumptions
- **Decision**: CPU capacity assumptions, cloud data-rate assumption, and reward aggregation order may be proposed with explicit values and risk notes.
- **Rationale**: The project already has runtime defaults and validation semantics that can be surfaced as assumptions without claiming paper recovery.
- **Alternatives considered**: Marking all unresolved items blocked was rejected because some values can be responsibly proposed for approval.

## Decision 6: Feature 030 closure report is the source gate
- **Decision**: The registry is built only from the Feature 030 closure report and the named in-scope unresolved items.
- **Rationale**: This keeps the registry tied to evidence exhaustion rather than ad hoc additions.
- **Alternatives considered**: Allowing arbitrary new candidates was rejected because it would bypass the closure gate.
