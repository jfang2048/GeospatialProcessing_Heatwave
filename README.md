# Daily heatwave footprints around Milan

`heatwave` is a small Python library for tracking how much of the Milan area was affected by heatwaves in summer 2022. It compares ERA5-Land daily maximum temperatures with a local 1991–2020 reference. When a grid cell stays above its threshold for at least three days, the library marks those days and groups neighbouring hot cells into daily footprints. The result is a map of each footprint and a table of its area and peak temperature excess.

## Quick start

Run these commands from the repository root to install the library and open the worked example.

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
python -m pip install -e .
jupyter lab notebooks/00_fixture.ipynb
```

The example uses a tiny grid included with the repository. For the Milan case, use your CDS token to get the data, or get `baseline.nc` and `target.nc` from a teammate. Follow the case guide to turn those inputs into `events.nc`, `footprints.nc` and `footprints.csv`. Run `python -m heatwave.report` to save the case figures in `reports/milan/`. [CDS token](docs/cds-setup.md) · [Get the data](docs/data.md) · [Run the Milan case](docs/workflow.md)

## Where to look

```text
src/heatwave/
  ingest/arco.py          Get hourly temperatures and write daily Celsius inputs
  events/detect.py        Calculate thresholds and mark heatwave days
  footprints/summarize.py Label connected areas and write the daily summary
  report.py               Draw temperature, area and footprint figures
data/
  examples/               Sample data included in the repository
  raw/cds/                Original CDS downloads
  processed/milan/        baseline.nc, target.nc, events.nc and footprint results
tests/
  unit/                   Tests you can run offline
  real/                   Tests that use the CDS pilot or full Milan results
notebooks/                Worked example, seven-day pilot and Milan case
reports/                  Executed notebooks and figures
docs/                     Setup, commands, file formats and map notes
```

Run `python -m pytest -q` for the offline tests. The case guide shows how to check your own stage and fixes for common errors. For development, use the file guide to see what each module reads and writes. [Cases and troubleshooting](docs/workflow.md) · [File formats](docs/v1.md) · [Study grid and maps](docs/geography.md) · [Team roles and releases](AGENTS.md)

## Use from Python

Import the stage you need. For example, `heatwave.events.detect.detect_events(baseline, target)` takes two xarray datasets and returns the event layers as a dataset. Install `.[report]` to use `heatwave.report.figures(run_dir)` and get Matplotlib figures from a completed run. [File formats](docs/v1.md)
