# Proposed work plan

## Milestones

| Target | Who can work independently | Exit criterion |
| --- | --- | --- |
| 23 Nov 2026 project work session | All | Show the proposal and decide the geographic scope and whether this processing chain is sufficient. Confirm owners and freeze v1 together. |
| 26 Nov | FJ runs the pilot. YY and FY use fixtures. | Verify that the pilot file opens and check its dates and grid. Prepare independent fixtures for Events and Footprints. |
| 3 Dec | FJ finalizes the normalized handoff. YY and FY submit their PRs. | Each module's tests pass. Use synthetic inputs if the provider queue delays integration. |
| 10 Dec | FJ integrates. All review outputs and compare their hand calculations with the notebook. | Clean install, synthetic end to end run, then full real case with verified input manifest when available. |
| 14 Dec project work session | All | Each member explains the path from raw input to P90, duration and footprint area. Check contributions and complete the submission. |

See the [v1 contract](../contracts/v1.md) for acceptance checks and the [contribution rules](../AGENTS.md) for module ownership and push checks.

## Starter checks

Activate the [project environment](../README.md#run-the-starter), then run these commands from the repository root.

```bash
python -m pytest -q -p no:cacheprovider
mkdir -p runs/fixture
jupyter nbconvert --to notebook --execute --stdout notebooks/00_fixture.ipynb > runs/fixture/00_fixture.ipynb
```

Use the [synthetic NetCDF handoffs](fixtures/README.md) until the real-case interfaces are ready. Write outputs under `runs/<name>/`.

## Automated pipeline

FJ owns the planned integration entry point. Once the stage CLIs are available, one non-interactive command must take a run from data acquisition to a validated report. Each module owner maintains their stage CLI. The runner supplies paths, invokes those CLIs, checks their results and runs the report notebook headlessly.

```bash
# Planned offline integration run
python integration/run_pipeline.py --profile fixture --run-dir runs/fixture-01
# Planned Milan run after CDS access is configured
python integration/run_pipeline.py --profile milan --cache-dir data/raw/cds --run-dir runs/milan-01
```

| Step | Runner responsibility | Output passed forward |
| --- | --- | --- |
| Acquire | For `fixture`, build a deterministic synthetic provider cache in the run directory. For `milan`, use the configured CDS client to retrieve missing full-profile requests and verify every cached payload against its request manifest. | Verified provider cache |
| Normalize | Call the Ingest CLI on that cache. Check both cubes against v1. | `baseline.nc`, `target.nc` |
| Detect | Pass both produced cubes to Events and validate the daily grid and flags. | `events.nc` |
| Summarize | Pass the produced event file to Footprints. Cross-check labels, CSV keys and area totals. | `footprints.nc`, `footprints.csv` |
| Report | Execute the case notebook with paths to this run's products. Record coverage, unknown cells, the peak-area day and its map and time series. Handle a summer with zero qualifying cells explicitly. | Executed notebook and run manifest |

Claim a new run directory before starting work. Record profile, code revision, input hashes, stage status and output paths relative to that directory in `run.json`. Write diagnostics to stderr. Stop at the first failing command or validation, mark the run failed and return nonzero. An interrupted run remains incomplete. Mark success and return zero only after the report and its inputs pass validation. Retry in a fresh run directory, reusing verified Milan downloads. Keep manifests and diagnostics free of credentials, private URLs and personal paths.

## End-to-end acceptance

After the [stage CLIs](../contracts/v1.md#proposed-command-interfaces) land, CI must run the module tests and the fixture profile from a clean checkout on pull requests and pushes to `main`. Run offline with no CDS credentials. FJ runs the Milan profile separately with configured access. Record the commit, environment versions, input identifiers and hashes, commands, results, and any unavailable real data in the integration PR.

1. Invoke the fixture command above as a subprocess. Assert exit status 0, successful stage records in order, and a readable executed notebook. Check that every recorded output exists under the new run directory and that the report uses those outputs.
2. Independently exercise the two downstream commands with the [committed fixtures](fixtures/README.md). Compare Events with the reference event cube, then compare Footprints with the hand-labelled CSV for every listed date and cell. Check dimensions, dates, integer flags and IDs exactly. Compare floating values with the v1 fixture tolerances and matching NaN positions. Check daily area conservation and all CSV/raster keys across the full summer.
3. Repeat with identical inputs in a fresh directory. Compare decoded arrays and CSV values, and verify input hashes remain stable. Inject a corrupt payload and an incompatible grid in separate runs. Verify a nonzero exit status, a diagnostic naming the failed check, and no downstream products or success record. Retry with corrected inputs and verify the earlier successful run is intact.
4. For the Milan run, verify the versioned snapshot hashes, 1991–2020 baseline, 2022 target, and grid coverage. Execute the demonstration notebook against the generated files and report reference coverage, unknown cells and the peak-area day. Record synthetic and real-case results separately. The current fixture notebook checks hand-worked values.

For submission, provide the repository, source and environment, documentation, a sample, and tests. Enter the team details, tentative title, and repository URL in the course spreadsheet. Confirm the exam call in WeBeep and count back nine calendar days to the last eligible repository change.
