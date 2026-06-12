Phase 6.15 hardens the HOODIE paper-scenario action-distribution wiring path.

It runs Phase 6.14 only under a temporary output directory, writes and validates canonical action-distribution files, and requires explicit action category fields.

It blocks numeric-only unmapped actions, validates local/horizontal/vertical/unknown counts and ratios, and blocks unknown actions by default for paper-scenario wiring.

It preserves non-official metadata guards and does not claim official Figure 9, official Figure 10, paper reproduction, or paper-performance validation.

It does not run official Figure 9.
It does not run official Figure 10.
It does not run 200-episode validation.
It does not run full or 5000-episode training.
It does not evaluate all official policies.
It does not create official paper results.

Official Figure 9 remains blocked until real paper-scenario action-distribution validation exists.
Official Figure 10 remains blocked.
Figure 11 remains blocked until LSTM ablation protocol and run exist.

The next phase should harden action mapping from real HOODIE paper-scenario traces or evaluation aggregation, not official reproduction.
