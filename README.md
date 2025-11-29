# Assessment Processing Pipeline

This project processes assessment/test data end-to-end: it loads data, sanitizes and validates inputs, computes raw and derived scores, optionally standardizes scores against norms, and finally exports results to CSV/JSON or renders PDF report(s).

The pipeline is orchestrated by `processor.process` and uses the following components:

- `DataProvider` — Locates and provides raw inputs (responses, roster, norms, metadata).
- `DataContainer` — In-memory model for all working data and results; provides persistence.
- `Sanitizer` — Validates inputs, fixes data issues where safe, flags/raises errors otherwise.
- `Scorer` — Computes raw-related metrics (raw score, corrected raw, means, subscores).
- `Standardizer` — Converts raw metrics to standard scores using age/grade norms (optional).
- `Reporter` — Renders PDF report(s); supports single combined or split-per-subject output.
- `TracebackNotifier` — Sends notifications when unexpected exceptions occur.

