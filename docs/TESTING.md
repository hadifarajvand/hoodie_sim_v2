# Testing Policy

Before claiming a coding task is complete, run the narrowest useful validation first.

Preferred order:
1. targeted test
2. unit tests
3. typecheck
4. lint
5. build
6. integration/e2e tests if available and safe

Always report:
- exact command
- result
- failure reason
- whether failure appears pre-existing
- whether current change is safe

Do not fake passing tests.
