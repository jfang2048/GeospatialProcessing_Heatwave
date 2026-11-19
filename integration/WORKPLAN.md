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

For submission, provide the repository, source and environment, documentation, a sample, and tests. Enter the team details, tentative title, and repository URL in the course spreadsheet. Confirm the exam call in WeBeep and count back nine calendar days to the last eligible repository change.
