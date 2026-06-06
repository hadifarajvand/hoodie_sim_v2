# System Model OCR Fidelity Checklist

This checklist audits simulator fidelity against OCR lines 122-747 of the HOODIE paper, focused on the System Model and the immediately related modelling sections.

## Experimental Results / Output Contract Coverage

This checklist now also covers OCR lines 758-1050, which define the paper's experimental output contract.

- Lines 122-747 define the system-model mechanism contract.
- Lines 758-1050 define the required simulator outputs, metrics, validation runs, training curves, baseline comparisons, and figure artifacts.
- The purpose is to specify what the simulator must later generate honestly.
- The purpose is not to match paper numbers or invent figure-ready outputs now.
- Final Figures 8-11 must not be generated until the reward, LSTM, validation, and baseline fidelity gaps are closed or explicitly waived.
- The simulator must generate its own training curves, validation metrics, baseline comparisons, and figure datasets.

This is a specification and audit package only.

- It does not change simulator runtime behavior.
- It does not change training behavior.
- It does not claim paper-faithful completion.
- It exists to let an engineer map each paper mechanism to current repository evidence.

Use the companion checklist file to record whether each paper element is `COMPLETE`, `PARTIAL`, `MISSING`, `UNCLEAR`, or `NOT_APPLICABLE_YET`.
