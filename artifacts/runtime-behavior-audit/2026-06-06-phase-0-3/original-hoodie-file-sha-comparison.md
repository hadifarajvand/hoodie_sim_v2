# Original HOODIE File SHA Comparison

## Method

I compared the current branch files against the baseline snapshot available in Git history at commit `419e48f` for promoted root-level runtime files.

## Exact Hash Matches

The following files are byte-for-byte identical to the baseline snapshot:

| File | Current SHA-256 | Baseline SHA-256 | Match |
| --- | --- | --- | --- |
| `main.py` | `495df77f95892aa9f17b45770f21666ce1ec24dc057f318df2d969fc0baae3e3` | `495df77f95892aa9f17b45770f21666ce1ec24dc057f318df2d969fc0baae3e3` | Yes |
| `environment/environment.py` | `c06312a4c4b906cb4d592b5883219bd5187873cf5230f3898a59a513a7d7e85f` | `c06312a4c4b906cb4d592b5883219bd5187873cf5230f3898a59a513a7d7e85f` | Yes |
| `utils/__init__.py` | `83c7c0eaad9b24601a3e6ffb3603712d43519c3ab66f66b34546267ea06a0714` | `83c7c0eaad9b24601a3e6ffb3603712d43519c3ab66f66b34546267ea06a0714` | Yes |
| `hyperparameters/hyperparameters.json` | `7c10a0e1b05fe572f650d53acce0cb9d58705e73974f08537c4827d1f486dd10` | `7c10a0e1b05fe572f650d53acce0cb9d58705e73974f08537c4827d1f486dd10` | Yes |

## Interpretation

The branch's core runtime entrypoint and environment files are identical to the promoted HOODIE runtime baseline snapshot.

That is strong evidence that the runtime implementation itself is still the legacy HOODIE simulator baseline, not a rewritten paper-faithful Phase 0.3 runtime.

## Caveat

This comparison does **not** prove equivalence to the external `Ilias-Paralikas/HOODIE` repository byte-for-byte because that repository is not vendored here for direct diffing. It does prove equivalence to the promoted baseline snapshot that this branch is built from.

