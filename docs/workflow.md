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
python -m heatwave.report
```

Open `data/processed/milan/footprints.csv` for the area and peak excess of each footprint. The report command saves `temperature.png`, `area.png` and `footprints.png` under `reports/milan/`. Open [the case notebook](../notebooks/01_case.ipynb) to see the same figures in Jupyter. The environment file includes Matplotlib. For a pip installation, use `python -m pip install -e '.[report]'`. [How to read the figures](geography.md)

## Tests

Run your check after writing your stage's files. Use the same `HEATWAVE_RUN_DIR` when checking a case outside the default directory.

| Stage | Offline check | Check your Milan outputs |
| --- | --- | --- |
| FJ · Ingest | `python -m pytest -q tests/unit/test_arco.py tests/unit/test_normalize.py tests/unit/test_ingest_check.py` | `python -m heatwave.ingest.check`. Add `--pilot` and the raw CDS pilot path for a second-source comparison. |
| YY · Events | `python -m pytest -q tests/unit/test_events.py` | `python -m pytest -q tests/real/test_case.py -k events_against` |
| FY · Footprints | `python -m pytest -q tests/unit/test_footprints.py` | `python -m pytest -q tests/real/test_case.py -k footprint_labels` |
| Report | `python -m pytest -q tests/unit/test_report.py` | `python -m heatwave.report` checks that the inputs agree and writes the figures. |

Run `python -m pytest -q` for all offline tests. Run `python -m pytest -q tests/real/test_case.py` for the completed case. The [CDS pilot test](../tests/real/test_pilot.py) needs the raw seven-day file in `data/raw/cds/`.

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
