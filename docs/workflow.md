# Run the Milan case

Install the [environment](../README.md#quick-start) and [set up data access](data.md). Run these commands in order from the repository root. If you already have both input files in `runs/milan/`, start with the Events command. Use a fresh output directory for a new run and update the paths together.

```bash
python -m heatwave.ingest.arco
python -m heatwave.events.detect --baseline runs/milan/baseline.nc --target runs/milan/target.nc --out runs/milan/events.nc
python -m heatwave.footprints.summarize --events runs/milan/events.nc --labels-out runs/milan/footprints.nc --summary-out runs/milan/footprints.csv
jupyter lab notebooks/01_case.ipynb
```

- **FJ** produces the two input files. The baseline has 4,590 dates and the target has 153, both on the same 9 × 15 grid.
- **YY** produces `events.nc`. Explain a cell's P90 and why its temperatures do or do not qualify.
- **FY** produces the two footprint files. Explain how neighbouring cells form a component and how their areas add up to the CSV total.

## Tests

```bash
python -m pytest -q
python -m pytest -q tests/real/test_pilot.py
python -m pytest -q tests/real/test_case.py
```

The first command uses local test data. The second needs the seven-day CDS download. The third needs the completed outputs in `runs/milan/`. For the older CDS route, run `python -m pytest -q tests/real` once both raw July downloads and outputs are available. Set `HEATWAVE_CACHE_DIR` or `HEATWAVE_RUN_DIR` for other locations.

## Synthetic fixtures

[The worked example](../notebooks/00_fixture.ipynb) uses a 2 × 3 grid in `notebooks/data/fixtures/`. Events can use `baseline_fixture.nc` and `target_fixture.nc`. Footprints can start at `events_fixture.nc`. The expected flags and IDs for the first five days are in `worked_example.csv`.

## Course submission

Use the real Milan case for the final report. Include the code, environment, README, sample data, notebook and tests. Each member contributes their own code and prepares to explain the whole workflow. Register the group, title and repository in the course spreadsheet. Confirm the chosen exam call and the nine-calendar-day submission deadline in WeBeep.
