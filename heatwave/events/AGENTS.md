# Events ownership · YY

Edit files under `heatwave/events/` on `events/<task>` branches. Read the [v1 contract](../../contracts/v1.md), use synthetic temperature inputs, and implement P90 by calendar date plus the run detector without relying on a CDS login.

Own the planned `thresholds.py` and `detect.py`, tests and module usage notes. Consume canonical `baseline.nc` and `target.nc`; write `events.nc`. Demonstrate a hand trace for a three day run and a known percentile. Check equality, a missing cell value, an absent date, two day runs, and the summer boundary. Any required upstream format change belongs in a request to the Ingest owner.

Start with the shared [baseline and target fixtures](../../integration/fixtures/README.md).
