# Repository Tracking Policy

This repository is intentionally split into tracked source, tracked reference
material, and ignored generated output. If a file does not clearly belong in
one of the tracked categories below, do not add it to git.

## Track In Git

- `src/`
- `tests/`
- `configs/`
- `specs/`
- `docs/`
- `AGENTS.md`
- repository governance files such as `.gitignore`
- reference artifacts that are explicitly part of the project record, such as
  paper OCR exports and approved source PDFs under `resources/papers/`
- vendored reference code under `resources/references/` only when it is being
  used as a read-only internal module and its upstream repo metadata has been
  removed

## Do Not Track

- `outputs/`
- `.DS_Store`
- `__pycache__/`
- `*.pyc`
- `*.pyo`
- virtual environments, including `resources/references/simpy/venv_mac/`
- notebook checkpoints
- coverage output
- build artifacts
- transient logs, temp files, editor swap files, and cache directories

## Special Rules For Vendored References

- Reference code may be copied into `resources/references/` only if it is
  treated as part of this repository, not as a nested git repository.
- Before staging vendored code, remove any nested `.git/` directory so git does
  not interpret the path as a submodule or embedded repository.
- Do not commit the vendored reference's local virtual environment, caches, or
  generated build output.
- Keep external reference code read-only unless the project explicitly needs a
  local adaptation.

## Review Rule

Before any large staging operation, verify `git status` and confirm that:

- no ignored junk is staged
- no nested repositories remain embedded
- only intended source, docs, configs, and approved reference artifacts are
  present

If the staging set contains outputs or cache files, stop and fix the ignore
rules before committing.
