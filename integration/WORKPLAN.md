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

## Integration commands

Activate the [project environment](../README.md#run-the-starter), then run these commands from the repository root.

```bash
python -m pytest -q -p no:cacheprovider
mkdir -p runs/fixture
jupyter nbconvert --to notebook --execute --stdout notebooks/00_fixture.ipynb > runs/fixture/00_fixture.ipynb
```

Use the [synthetic NetCDF handoffs](fixtures/README.md) until the real-case interfaces are ready. Write outputs under `runs/<name>/`.

## End-to-end acceptance

FJ runs the following checks from a clean checkout after the three planned [stage commands](../contracts/v1.md#proposed-command-interfaces) land. Record the commit, environment versions, input identifiers and hashes, commands, results, and any unavailable real data in the integration PR.

1. Start offline with a small synthetic provider cache and matching request manifests. FJ supplies the cache in the integration test. Exercise the production normalizer on the requested periods and pass its actual outputs to Events, then pass the resulting event file to Footprints. Run the stages as separate CLI processes in order and stop on the first failure.
2. Independently exercise the two downstream commands with the [committed fixtures](fixtures/README.md). Compare Events with the reference event cube, then compare Footprints with the hand-labelled CSV for every listed date and cell. Check dimensions, dates, integer flags and IDs exactly. Compare floating values with the v1 fixture tolerances and matching NaN positions. Check daily area conservation and all CSV/raster keys across the full summer.
3. Repeat with identical inputs in a fresh directory. Compare decoded arrays and CSV values, and verify input hashes remain stable. Inject a corrupt input and an incompatible grid in separate runs. Verify that each fails at the consuming stage and that later stages do not start.
4. For the Milan run, verify the versioned snapshot hashes, 1991–2020 baseline, 2022 target, and grid coverage. Execute the demonstration notebook against the generated files and report reference coverage, unknown cells and the peak-area day. Record synthetic and real-case results separately. The current fixture notebook checks hand-worked values.

For submission, provide the repository, source and environment, documentation, a sample, and tests. Enter the team details, tentative title, and repository URL in the course spreadsheet. Confirm the exam call in WeBeep and count back nine calendar days to the last eligible repository change.
