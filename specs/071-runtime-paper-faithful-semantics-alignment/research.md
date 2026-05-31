# Research: Feature 071

## Decision 1: Align runtime helpers, not training code

Decision: Feature 071 targets deadline, timeout/drop, terminal-state, and reward helper semantics.

Rationale: Feature 070 recovered paper equations and documented runtime divergence. The next defensible step is to align the helper layer before building golden traces or training flows.

Rejected alternative: Train or evaluate directly. Rejected because evaluation on divergent runtime semantics would be garbage.

## Decision 2: Paper mode must be strict by default

Decision: Feature 071 validation uses `paper` mode by default.

Rationale: HOODIE Eq. (20) uses a strict success condition. Runtime equality-at-deadline behavior must not be silently treated as paper-faithful.

Rejected alternative: Preserve legacy behavior as default. Rejected because it hides the divergence recovered by Feature 070.

## Decision 3: Compatibility mode stays explicit

Decision: Legacy behavior may exist only under `compatibility` mode.

Rationale: Existing tests or old simulator paths may depend on equality-at-deadline behavior. Keeping a named compatibility mode prevents accidental breakage while making paper-mode semantics unambiguous.

Rejected alternative: Delete compatibility behavior immediately. Rejected because this can break unrelated historical tests and obscure the migration boundary.

## Decision 4: Reward timing and reward equation are separate

Decision: Feature 071 must implement Eq. (20)-(23) and keep terminal reward timing explicit.

Rationale: Feature 070 proved the equation is recovered. Feature 071 must ensure runtime computation uses the recovered equation, not the old completion-slot approximation.

Rejected alternative: Treat terminal timing validity as reward fidelity. Rejected because this was the earlier weak point.

## Decision 5: Runtime-model modification is optional and narrow

Decision: `src/environment/runtime_model.py` may be changed only if necessary to expose terminal-state integration.

Rationale: Broad simulator lifecycle rewrites are too risky for Feature 071. Helper semantics can be aligned first; end-to-end validation belongs in Feature 072.

Rejected alternative: Rewrite the simulator lifecycle now. Rejected as scope creep.
