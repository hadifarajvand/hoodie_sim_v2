# Next Step Decision

**Date:** 2026-06-23  
**Status:** Baselines complete; awaiting user decision

---

## Current State

✓ **Baseline campaigns completed:**
- Shared-agent: 5000 episodes, 11 checkpoints, final completion 25.45%
- Per-EA distributed: 5000 episodes, 11 checkpoints, final completion 22.14%
- Both campaigns reconciled (delta=0.0, coverage=100%)
- All metrics extracted and formatted

✓ **Figures generated:**
- Figures 1–7: Diagnostic plots (shared vs distributed, rewards, actions, etc.)
- Figure 8a/8b: Single-config reward curves
- Figure 9a: Real action distribution
- Figure 10a/10b: Delay and drop ratio vs baselines (COMPLETE)
- Figure 11a: With-LSTM delay curve
- Papers figures 8/9/11 sweep/ablation panels: Not generated (marked as missing)

✓ **Paper-output report assembled:**
- paper-output-report.md (comprehensive overview)
- paper-output-report.json (structured metadata)
- paper-figure-status-matrix.md/json (detailed status per figure)
- baseline-results-summary.md/json (comparison of both baselines)
- remaining-gaps.md (detailed list of optional work)
- claim-safety.json (verification that no claims were violated)

✗ **NOT done:**
- Parameter sweeps for Fig 8 (lr/gamma)
- System parameter sweeps for Fig 9
- LSTM ablation for Fig 11
- Proposed method (not started, pending approval)

---

## Decision Options

### Option A: Submit Baselines with Partial Figures

**What you get:**
- Paper with Figures 8, 9, 11 marked as "single-configuration results"
- Honest captions: "sweep panels require additional hyperparameter tuning (future work)"
- Figure 10: Complete (delay and drop ratio)
- Reviewers see real data, not fabricated sweeps
- Ready to submit now

**Timeline:** Ready today

**Pros:**
- Fast publication path
- Honest about what was/wasn't done
- Figure 10 is complete and strong
- Real baseline results are publishable as-is

**Cons:**
- Reviewers might request sweeps during revision
- Less comprehensive sensitivity analysis in print

**Recommendation:** Low risk; acceptable for many venues

---

### Option B: Run Optional Improvements First

**What you do:**
1. Run LSTM ablation (Fig 11b) — 1 run, 4–8 hours
2. Run lr/gamma sweep (Fig 8 panels) — 5–10 runs, 50–100 hours
3. Run system parameter sweep (Fig 9 panels) — 20–40 runs, 200–400 hours
4. Regenerate Figures 8, 9, 11 with complete panels
5. Submit complete paper

**Timeline:** 1–3 weeks (depending on parallelization)

**Pros:**
- More comprehensive manuscript
- Fewer reviewer questions about robustness/generalization
- Sweep data valuable for appendix

**Cons:**
- Significant additional compute time
- Delays publication
- May not change conclusions

**Recommendation:** High effort; medium value

---

### Option C: Hybrid (Incremental Approach)

**Phase 1 (Now): Submit with partial figures**
- Baseline results, Figure 10 complete
- Figures 8, 9, 11 marked as single-config

**Phase 2 (If reviewer feedback): Run requested sweeps**
- Only after reviewer comments come back
- Prioritize based on feedback
- Resubmit revised version

**Timeline:** 2 phases; review cycle between

**Pros:**
- Parallel with review process
- Only do sweeps if reviewers actually ask
- Reduces speculative work

**Cons:**
- Lengthens publication timeline
- Requires more revisions

**Recommendation:** Practical balance

---

## Proposed Method Decision

### Current Status
- NOT implemented (fully out of scope for baseline report)
- Awaiting user approval to start
- Will go on separate branch when approved

### What it would include
- Deadline-aware routing logic
- Optional EDF/LSTF queue discipline
- Reward shaping for deadline incentives
- Full 5000-episode training
- Comparison against baselines

### Timeline if Approved
- Implementation: 3–5 days
- Training: 1–2 days
- Evaluation and figures: 1 day
- Total: ~1 week

### Recommendation
- Decide on this independently from baseline publication
- Once baseline is finalized, can move forward on proposed method
- Will be on separate branch (clean separation)

---

## Recommended Path Forward

### My Recommendation: **Option A (Submit Baselines with Partial Figures)**

**Reasoning:**
1. **Baselines are solid:** Both campaigns complete, metrics reconciled, results honest
2. **Figure 10 is complete:** Delay and drop ratio comparison ready to publish
3. **Figures 8, 9, 11 are real:** Single-config curves are genuine data, not placeholders
4. **Honest about gaps:** Captions transparently mark missing sweeps as future work
5. **Fast path to publication:** Can submit baseline results within days
6. **Separate from proposed method:** Baselines are independent contribution
7. **Review feedback can guide future work:** If reviewers care about specific sweeps, run them then

**Next steps if you choose this:**
1. Review paper-output-report.md for tone/clarity
2. Export baseline results and figures to manuscript format
3. Draft Methods/Results sections summarizing both campaigns
4. Submit (with honest figure captions)
5. After reviewer feedback (or in parallel), decide on proposed method

**Alternative if you prefer thoroughness:**
- Run only LSTM ablation (1 run, ~6 hours) to complete Figure 11
- Run only ~5 lr/gamma configs (50 hours) to show robustness for Figure 8
- Delay system parameter sweeps (Fig 9) to future work or appendix
- This is a reasonable middle ground (1–2 days of compute)

---

## Final Checklist Before Committing

- [ ] Baseline results summaries accurate? (shared-agent, per-EA distributed)
- [ ] Baseline comparison table accurate? (all 7 policies, final metrics)
- [ ] Figure status honest? (10=complete, 8/9/11=partial)
- [ ] Remaining gaps document complete? (lists all optional work)
- [ ] Claim safety verified? (no superiority/reproduction/proposed-method claims)
- [ ] Proposed method decision clear? (not in scope for baseline report)
- [ ] Timeline expectations set? (Option A now, Option B 1–3 weeks, Option C review cycle)

---

## What's Ready to Commit

✓ All baseline artifacts (metrics, reconciliation, figures)  
✓ Paper-output-report directory with all analysis  
✓ No training reruns needed  
✓ No code changes needed  
✓ Only documentation/analysis in this commit

---

## Your Decision

1. **Proceed with baseline report commit?** (Yes/No)
2. **Which path:** Option A (now), Option B (complete), or Option C (hybrid)?
3. **Proposed method approval:** Approve to start after baseline finalized? (Yes/No/Later)

Once you decide, we commit the paper-output-report branch and move to the next phase.

