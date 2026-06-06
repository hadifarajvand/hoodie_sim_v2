# Smoke Run Report

## Repository State

- Branch: `100-hoodie-paper-base`
- Commit: `dfa6be1cf12931ad6238c38ee8397649bbaec4cb`
- Python environment: `.venvmac`

## Dependencies Identified

The Python imports used by the runtime path require:

- `numpy`
- `torch`
- `matplotlib`

Those are the minimal non-stdlib packages needed for one smoke run of the current code path.

## Run Command

```bash
source .venvmac/bin/activate && python main.py --epochs 1 --log_folder artifacts/runtime-audit-smoke/2026-06-06-071900/log_folder
```

## Outcome

- Exit code: `0`
- Status: success
- Log folder created: yes
- Log artifacts created: `scheduler.pth`

## Captured Files

- `artifacts/runtime-audit-smoke/2026-06-06-071900/run_command.txt`
- `artifacts/runtime-audit-smoke/2026-06-06-071900/run_stdout.txt`
- `artifacts/runtime-audit-smoke/2026-06-06-071900/run_stderr.txt`
- `artifacts/runtime-audit-smoke/2026-06-06-071900/exit_code.txt`
- `artifacts/runtime-audit-smoke/2026-06-06-071900/log_folder/scheduler.pth`
- `artifacts/runtime-audit-smoke/2026-06-06-071900/run_manifest.json`

## Notes

- `matplotlib` required a writable cache directory and emitted a font cache warning on first import.
- The run completed despite the warning.
- This is a smoke execution record only, not a paper-faithful runtime or training validation.
