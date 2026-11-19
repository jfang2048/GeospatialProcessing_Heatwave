# Proposed work plan

Each owner delivers Python functions, a command or usage example, tests, and documentation for their module.

| Owner | Work directory | Deliverable | Acceptance criteria |
| --- | --- | --- | --- |
| FJ | `heatwave/ingest/` | Provider retrieval, NetCDF normalization, exact date and grid validation, and input provenance. Also owns shared integration on a separate branch. | Seven day CDS pilot and normalized cube; verified checksums; K to °C and invalid input tests; fully hydrated baseline and target or an explicit data availability report. |
| YY | `heatwave/events/` | Calendar P90, strict consecutive run detector and `events.nc`. | Independent tests for known percentile, missing values, gaps, equality, three day inclusion and summer boundary; output conforms to v1. |
| FY | `heatwave/footprints/` | Daily component labelling, latitude dependent cell areas, per component summary and `footprints.nc` plus CSV. | Synthetic edge/diagonal checks, deterministic IDs, consistent areas and a known peak excess; output conforms to v1. |

## Milestones

| Target | Who can work independently | Exit criterion |
| --- | --- | --- |
| 23 Nov 2026 project work session | All | Show the proposal and decide the geographic scope and whether this processing chain is sufficient. Confirm owners and freeze v1 together. |
| 26 Nov | FJ runs the pilot. YY and FY use fixtures. | Verify that the pilot file opens and check its dates and grid. Prepare independent fixtures for Events and Footprints. |
| 3 Dec | FJ finalizes the normalized handoff. YY and FY submit their PRs. | Each module's tests pass. Use synthetic inputs if the provider queue delays integration. |
| 10 Dec | FJ integrates. All review outputs and compare their hand calculations with the notebook. | Clean install, synthetic end to end run, then full real case with verified input manifest when available. |
| 14 Dec project work session | All | Each member explains the path from raw input to P90, duration and footprint area. Check contributions and complete the submission. |

Use the [contribution rules](../AGENTS.md) for handoff changes and PRs. Check every outgoing commit against the [public repository checklist](../AGENTS.md#public-repository-checklist).

## Integration commands

From the repository root:

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
python -m pip install -e . --no-deps
python -m pytest -q -p no:cacheprovider
jupyter nbconvert --to notebook --execute --stdout notebooks/00_fixture.ipynb > /tmp/gprocessing-heatwave-fixture.ipynb
```

Use the [synthetic NetCDF handoffs](fixtures/README.md) until the real-case interfaces are ready. Write outputs under `runs/<name>/`.

For submission, provide the repository, source and environment, documentation, a sample, and tests. Enter the team details, tentative title, and repository URL in the course spreadsheet. Confirm the exam call in WeBeep and count back nine calendar days to the last eligible repository change.
