# Prompt — Continue HOODIE After Local Kernel Milestone

The first real implementation milestone already exists locally:

- Commit: `0d5fa65`
- Message: `HOODIE: add kernel foundation`
- Focused tests: `python -m pytest tests/test_hoodie_kernel.py tests/test_phase1.py`
- Result: `11 passed`

This is progress, not a stopping point.

## 1. Push failure is not an implementation blocker

The failed `git fetch origin --prune` SSH negotiation does not invalidate the local commit and does not authorize stopping the implementation.

Do not reset, amend away, recreate, or abandon commit `0d5fa65`.

Continue implementation locally while repairing remote authentication in parallel.

## 2. Diagnose remote authentication safely

From the isolated implementation worktree, record:

```bash
git status --short --branch
git log --oneline --decorate -5
git remote -v
git branch --show-current
```

Do not print credentials, tokens, private keys, or full credential-helper contents.

Check available authentication paths:

```bash
command -v gh || true
gh auth status || true
ssh -T git@github.com || true
```

If `gh auth status` confirms an authenticated GitHub account with repository write access, prefer HTTPS and GitHub CLI credential setup:

```bash
gh auth setup-git
git remote set-url origin https://github.com/hadifarajvand/hoodie_sim_v2.git
git fetch origin --prune
```

If HTTPS already works through the system credential manager, use:

```bash
git remote set-url origin https://github.com/hadifarajvand/hoodie_sim_v2.git
git fetch origin --prune
```

If SSH is intentionally required, inspect the SSH agent without exposing key material:

```bash
ssh-add -l || true
ssh -vT git@github.com 2>&1 | tail -n 80
```

Repair the agent/key selection through the user's existing SSH setup only. Do not generate, overwrite, upload, or replace SSH keys without explicit authorization.

Do not request or paste a personal-access token into source files, shell history, logs, or chat.

## 3. Push the existing local branch when authentication works

Preserve the current unique implementation branch. Determine it with:

```bash
BRANCH="$(git branch --show-current)"
printf '%s\n' "$BRANCH"
```

Then push exactly that branch:

```bash
git push -u origin "$BRANCH"
```

Verify the remote contains the kernel milestone:

```bash
git ls-remote --heads origin "$BRANCH"
git log -1 --oneline
```

The local commit `0d5fa65` must remain in the pushed branch history.

Never force-push. Never push to or merge into `main`.

## 4. Do not pause implementation while push is unavailable

Remote push failure is an operational issue, not a reason to stop coding because local commits work.

Continue immediately with the next implementation milestone:

```text
HOODIE: implement observation forecasting and DDQN learner
```

Implement and test:

1. source-contracted observation schema and deterministic feature ordering;
2. real causal load/history buffers with no zero placeholders;
3. LSTM forecasting with explicit training target, reset semantics, serialization, and a clean no-LSTM bypass;
4. Dueling Q-network with separate value and advantage streams;
5. one online/target network pair;
6. topology-aware legal-action masking;
7. masked epsilon-greedy action selection;
8. Double-DQN target calculation;
9. replay buffer and transition types;
10. optimizer step with configurable gamma and learning rate;
11. target-network update with source-contracted units;
12. tensor-safe checkpoint save/load;
13. deterministic checkpoint resume;
14. focused unit, property, and integration tests.

Commit locally even when the remote remains unavailable.

After that, continue through all remaining milestones defined by:

- `docs/plans/HOODIE_FAST_TRACK_FULL_IMPLEMENTATION_OVERRIDE.md`
- `docs/plans/HOODIE_AUTONOMOUS_FULL_IMPLEMENTATION_RUNBOOK.md`
- `docs/plans/HOODIE_MODULAR_REDESIGN_IMPLEMENTATION_PLAN.md`

Required later milestones remain:

1. distributed training, baselines, and paired evaluation;
2. ECHO removal from active implementation;
3. Figures 8–11 experiment and rendering pipeline;
4. full campaign and reproducibility closure.

## 5. Retry policy

Retry remote authentication after each local milestone and before the final campaign.

Do not repeatedly spend the whole invocation on SSH diagnostics. Use a bounded diagnostic attempt, continue coding locally, and retry later.

If authentication remains unavailable, retain all work as sequential local commits on the isolated implementation branch. The final blocker report is allowed only after the implementation itself has continued as far as the local environment permits and must include:

- branch name;
- all local commit SHAs;
- exact non-secret error output;
- HTTPS, GitHub CLI, and SSH-agent checks attempted;
- confirmation that no credentials were exposed;
- exact push command to run after authentication is restored.

## 6. Output policy

Do not return another Phase 0 or inventory report.

Do not report completion after only the kernel milestone.

Do not stop merely because push is temporarily unavailable.

Return only after:

- full HOODIE implementation and full Figures 8–11 campaign are complete; or
- a genuine hard blocker prevents further local implementation, not merely remote push.

Begin the observation, forecasting, and DDQN milestone now while authentication recovery is attempted in parallel.
