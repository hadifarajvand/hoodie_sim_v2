# 9router model alias rewrite fix

## Goal
Fix `cx/gpt-5.4-mini[1m]` handling in running 9router so requests never forward raw alias to backend.

## Steps
1. Inspect live router process and current alias path.
2. Patch router rewrite to canonical `cx/gpt-5.4-mini-review` or `cx/gpt-5.4-mini`.
3. Restart router.
4. Verify `/v1/models` and `/v1/messages` behavior.
5. Record commands, results, and any failures in run log.
