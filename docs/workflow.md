# Run the Milan case

Run the commands from the repository root after [installing the library](../README.md#quick-start). The first line needs a [CDS token](cds-setup.md). If `baseline.nc` and `target.nc` are already in `data/processed/milan/`, start at the Events command.

```bash
python -m heatwave.ingest.arco
python -m heatwave.events.detect \
  --baseline data/processed/milan/baseline.nc --target data/processed/milan/target.nc \
  --out data/processed/milan/events.nc
python -m heatwave.footprints.summarize \
  --events data/processed/milan/events.nc --labels-out data/processed/milan/footprints.nc \
  --summary-out data/processed/milan/footprints.csv
python -m nbconvert --to notebook --execute notebooks/01_case.ipynb --output-dir reports/milan
```

Open `data/processed/milan/footprints.csv` for the area and peak excess of each footprint. Open `reports/milan/01_case.ipynb` for the daily area series, a single-cell temperature series and the map of the peak day. [Output fields](v1.md) · [How to read the figures](geography.md)

## Tests

| Command | What it needs |
| --- | --- |
| `python -m pytest -q` | The installed project |
| `python -m pytest -q tests/real/test_pilot.py` | The seven-day CDS file in `data/raw/cds/` |
| `python -m pytest -q tests/real/test_case.py` | The completed Milan case |
| `python -m pytest -q tests/real` | The completed case, pilot and raw July 1991 and July 2022 files from the CDS daily route |

## Common problems

| What you see | What to do |
| --- | --- |
| `No module named heatwave` | Activate the project environment and run `python -m pip install -e .` from the checkout. |
| ARCO reports an unexpected `zarr_format` argument | [Update the project environment](cds-setup.md) to install Zarr 3. |
| ARCO cannot read your CDS key | Follow [CDS token setup](cds-setup.md) and try again. |
| A CDS pilot request stays on `accepted` | Check the request in [CDS Your Requests](https://cds.climate.copernicus.eu/requests). For the full Milan case, use the ARCO command above. |
| An output file already exists | To keep both runs, give ARCO a new `--run-dir` and use those paths for Events and Footprints. |
| A test or Notebook cannot find its inputs | For another run folder set `HEATWAVE_RUN_DIR`. For another raw cache set `HEATWAVE_CACHE_DIR`. |

## Synthetic fixtures

The [worked example](../notebooks/00_fixture.ipynb) uses the 2 × 3 grid in `data/examples/synthetic/`. For Events, start with `baseline_fixture.nc` and `target_fixture.nc`. For Footprints, start with `events_fixture.nc`. See `worked_example.csv` for the expected flags and IDs on the first five days. Regenerate the files with `python tests/build_fixtures.py`.

## Course submission

Submit the code, environment file, README, sample data, executed Milan notebook and tests. Each team member contributes their own code and explains the workflow. Register the team, title and repository in the course spreadsheet. Confirm your exam call and the nine-calendar-day submission deadline in WeBeep.
