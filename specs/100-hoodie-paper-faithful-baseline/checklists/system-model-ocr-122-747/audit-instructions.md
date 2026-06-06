# Audit Instructions

Use this checklist as a contract, not as a vibe check.

## How To Use

1. Read the OCR source sections in `resources/papers/hoodie/ocr/merged.md` for the relevant lines.
2. Read the current repository code paths that implement or approximate the mechanism.
3. Compare the mechanism against the paper requirement.
4. Mark the row with the strictest accurate status:
   - `COMPLETE` only if the mechanism is actually present and auditable
   - `PARTIAL` if the mechanism exists but is proxy-based, incomplete, or not yet paper-grade
   - `MISSING` if the mechanism is not present
   - `UNCLEAR` if the evidence is insufficient
   - `NOT_APPLICABLE_YET` if the mechanism belongs to a later phase
5. Write the gap or risk in blunt language. If it is trash, say it is trash.

## Rules For Avoiding False Completes

- Do not mark something `COMPLETE` because the code path exists. The question is whether it matches the paper contract.
- Do not mark something `COMPLETE` if it is reconstructed from traces but not natively emitted by the runtime.
- Do not mark the state model `COMPLETE` if the summary still reports proxy dimensions like `state_dim=2`.
- Do not mark the action model `COMPLETE` if the action count is a reduced proxy instead of the paper state/action contract.
- Do not mark reward `COMPLETE` if the reward is only recovered after the fact from task traces.

## Evidence Hierarchy

Prefer this order:

1. Paper text in the OCR source.
2. Repository code.
3. Trace outputs and audit artifacts.
4. Summary reports.

If the evidence conflicts, the paper text wins and the repository gets the gap.

## Required Audit Questions

- Does the repository expose the mechanism in code?
- Does the mechanism behave as the paper says?
- Is the mechanism auditable in trace outputs?
- Is the mechanism paper-grade or just a proxy?
- What phase should fix it?

## Output Standard

Every audit result should be actionable. If you cannot point to the file, line, trace, or artifact that proves the claim, do not call it complete.

