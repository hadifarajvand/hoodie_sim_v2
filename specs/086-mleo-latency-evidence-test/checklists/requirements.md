# Requirements Checklist: Feature 086

## MLEO Numeric Behavior

- [ ] MLEO candidate delay values are directly inspectable.
- [ ] MLEO selects the candidate with minimum total estimated latency.
- [ ] A smallest-queue-but-not-smallest-latency candidate loses in a controlled test.
- [ ] Tests fail for queue-length-only behavior.

## HOODIE/MLEO Tie Evidence

- [ ] HOODIE/MLEO aggregate tie is explicitly explained.
- [ ] Evidence includes selected-action comparison or a clear reason why trace evidence is unavailable.
- [ ] Readiness level does not overclaim if tie cannot be fully explained.

## Scope Guard

- [ ] No DCQ.
- [ ] No thesis method.
- [ ] No custom queue redesign.
- [ ] No full empirical paper reproduction claim.

## Validation

- [ ] `git diff --check` passes.
- [ ] Runtime evaluation unit tests pass.
- [ ] MLEO-focused tests pass.
- [ ] Runtime evaluation integration tests pass.
- [ ] Feature 085 artifacts still validate.
