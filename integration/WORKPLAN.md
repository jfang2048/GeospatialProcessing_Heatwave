# Proposed work plan

The module assignments below are proposed. Each owner implements Python functions, a command entry point or usage example, module tests and module documentation inside their directory. The first PR for each module must contain code its owner can explain.

| Owner | Work directory | Deliverable | Acceptance criteria |
| --- | --- | --- | --- |
| FJ | `heatwave/ingest/` | Provider retrieval, NetCDF normalization, exact date and grid validation, and input provenance. Also owns shared integration on a separate branch. | Seven day CDS pilot and normalized cube; verified checksums; K to °C and invalid input tests; fully hydrated baseline and target or an explicit data availability report. |
| YY | `heatwave/events/` | Calendar P90, strict consecutive run detector and `events.nc`. | Independent tests for known percentile, missing values, gaps, equality, three day inclusion and summer boundary; output conforms to v1. |
| FY | `heatwave/footprints/` | Daily component labelling, latitude dependent cell areas, per component summary and `footprints.nc` plus CSV. | Synthetic edge/diagonal checks, deterministic IDs, consistent areas and a known peak excess; output conforms to v1. |

## Milestones

| Target | Who can work independently | Exit criterion |
| --- | --- | --- |
| 23 Nov 2026 project work session | All | Show the proposal and decide the geographic scope and whether this processing chain is sufficient. Confirm owners and freeze v1 together. |
| 26 Nov | A runs and records the provider pilot. B and C use fixtures. | A representative raw file opens, time and coordinates are understood, and both algorithm owners have independent unit fixtures. |
| 3 Dec | A finalizes the normalized handoff. B and C complete and submit their own PRs. | Three independent module tests pass. Integration uses synthetic stage inputs if the provider queue takes longer. |
| 10 Dec | FJ integrates. All review outputs and compare their hand calculations with the notebook. | Clean install, synthetic end to end run, then full real case with verified input manifest when available. |
| 14 Dec project work session | All | Each member traces raw input, P90, duration and spatial area without relying on the notebook output. Verify balance of source code contributions and finish course submission requirements. |

Use one PR per task. When the contract changes, the integration owner updates and versions it after agreement from the affected owners. A teammate reviews each module PR. Resolve a dependency by using an agreed fixture or asking the path owner for a change. The full notebook and shared environment have a single editor.

## Integration commands

From the repository root:

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
python -m pip install -e . --no-deps
python -m pytest -q -p no:cacheprovider
jupyter nbconvert --to notebook --execute --stdout notebooks/00_fixture.ipynb > /tmp/gprocessing-heatwave-fixture.ipynb
```

The fixture notebook and [independent NetCDF handoffs](fixtures/README.md) are available immediately. Add the real case notebook after the three module interfaces land. Use `runs/<name>/` for outputs. The course requires an online repository, source and environment settings, documentation, a sample, and tests. Enter names, tentative title and repository URL in the course spreadsheet. Give both professor and tutor access if private. Confirm the chosen exam call in WeBeep and count back nine calendar days from it for the last eligible repository change, as stated in the Project Assignment. The dates above are internal work targets.
