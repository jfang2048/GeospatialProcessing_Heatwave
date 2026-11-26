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

## Files you get after a run

Each stage writes a file the next stage can read. The paths below are relative to your checkout. GitHub carries the source and example files. Your downloaded data and generated results live locally.

| File | What it contains |
| --- | --- |
| `data/processed/milan/baseline.nc` | Daily maximum temperatures for May–September 1991–2020. Events uses them to calculate P90. |
| `data/processed/milan/target.nc` | Daily maximum temperatures for May–September 2022. Events looks for heatwaves in June–August. |
| `data/processed/milan/events.nc` | Temperature, P90, excess above P90 and a heatwave flag for each cell and summer day. |
| `data/processed/milan/footprints.nc` | A raster of connected footprint IDs for each day. |
| `data/processed/milan/footprints.csv` | One row per daily footprint, with its cell count, area and peak temperature excess. |
| `reports/milan/temperature.png` | Temperature and P90 at one grid cell, with heatwave days marked. |
| `reports/milan/area.png` | Observed heatwave area and data coverage for every summer day. |
| `reports/milan/footprints.png` | Footprint map for the day with the largest observed area. |
| `reports/milan/01_case.ipynb` | Executed case notebook with the three figures, produced by the notebook command in the case guide. |
| `reports/pilot/temperature_2022-07-15.png` | First-day temperature map produced by the pilot notebook. |

The original CDS downloads, if you use them, go under `data/raw/cds/`. Each request gets its own folder with a NetCDF or ZIP file. [File formats](docs/v1.md) · [Run and troubleshoot the case](docs/workflow.md)

## Where to look

### Guides and project setup

| File | What it does |
| --- | --- |
| [README.md](README.md) | Start here for installation, the example and this file index. |
| [AGENTS.md](AGENTS.md) | Records who owns each stage, how the team works and how to push from the local checkout. |
| [LICENSE](LICENSE) | Gives the project’s GNU GPL version 3 licence text. |
| [environment.yml](environment.yml) | Defines the Conda environment used for the library, tests and notebooks. |
| [pyproject.toml](pyproject.toml) | Defines the installable package, dependencies, optional extras and pytest defaults. |
| [.gitignore](.gitignore) | Keeps local downloads, outputs, credentials and build files out of Git. |
| [docs/cds-setup.md](docs/cds-setup.md) | Shows where to put your CDS token and how to update the environment. |
| [docs/data.md](docs/data.md) | Explains how to get the Milan inputs with ARCO, use the CDS pilot and share the two NetCDF files. |
| [docs/workflow.md](docs/workflow.md) | Gives the case commands in order, the tests for each stage and fixes for common errors. |
| [docs/v1.md](docs/v1.md) | Defines the files passed between stages, including fields, units, flags and calculations. |
| [docs/geography.md](docs/geography.md) | Describes the Milan grid, the three figures and the sources behind the method. |

### Python library

The files below are in `src/heatwave/`. After installation, import them under the package name `heatwave`.

| File | What it does |
| --- | --- |
| [`__init__.py`](src/heatwave/__init__.py) | Marks the top-level `heatwave` package. |
| [`_handoff.py`](src/heatwave/_handoff.py) | Checks the common NetCDF grid and stages output files before publishing them. |
| [`ingest/__init__.py`](src/heatwave/ingest/__init__.py) | Marks FJ’s data-preparation package. |
| [`ingest/arco.py`](src/heatwave/ingest/arco.py) | Reads hourly ERA5-Land data, takes each UTC day’s maximum and writes the two Celsius input cubes. |
| [`ingest/cache.py`](src/heatwave/ingest/cache.py) | Finds local CDS files and opens NetCDF files inside ZIP archives. |
| [`ingest/check.py`](src/heatwave/ingest/check.py) | Checks saved Milan inputs and can compare the target with a separate CDS daily pilot. |
| [`ingest/download.py`](src/heatwave/ingest/download.py) | Downloads the CDS daily product or imports a seven-day pilot file downloaded in the browser. |
| [`ingest/normalize.py`](src/heatwave/ingest/normalize.py) | Converts an existing cache of monthly CDS files into the same input format as ARCO. |
| [`ingest/provider.py`](src/heatwave/ingest/provider.py) | Decodes CDS dates, coordinates and temperatures and builds the common Celsius dataset. |
| [`ingest/requests.py`](src/heatwave/ingest/requests.py) | Defines the Milan bounds, date ranges and monthly requests for the CDS daily route. |
| [`events/__init__.py`](src/heatwave/events/__init__.py) | Marks YY’s heatwave detection package. |
| [`events/detect.py`](src/heatwave/events/detect.py) | Calculates P90 for each cell and summer day, then marks runs of at least three days above it. |
| [`footprints/__init__.py`](src/heatwave/footprints/__init__.py) | Marks FY’s footprint analysis package. |
| [`footprints/summarize.py`](src/heatwave/footprints/summarize.py) | Groups heatwave cells that share an edge and writes the labelled raster and area CSV. |
| [`report.py`](src/heatwave/report.py) | Reads a completed case and makes the three figures used by the report command and the notebook. |

### Notebooks and sample data

| File | What it shows |
| --- | --- |
| [notebooks/00_fixture.ipynb](notebooks/00_fixture.ipynb) | Works through heatwave flags and footprint areas on a tiny synthetic grid. |
| [notebooks/00_pilot.ipynb](notebooks/00_pilot.ipynb) | Opens the seven-day CDS pilot and shows its temperatures and a map. |
| [notebooks/01_case.ipynb](notebooks/01_case.ipynb) | Shows the finished Milan case using the library’s report figures. |
| [pilot_milan_cell.csv](data/examples/pilot_milan_cell.csv) | Seven real July 2022 daily maximum temperatures at one Milan grid cell. |
| [baseline_fixture.nc](data/examples/synthetic/baseline_fixture.nc) | A small synthetic reference cube used to calculate a known threshold. |
| [target_fixture.nc](data/examples/synthetic/target_fixture.nc) | A synthetic target cube with short hot spells, qualifying runs and a missing cell. |
| [events_fixture.nc](data/examples/synthetic/events_fixture.nc) | Expected synthetic event layers and flags. Footprints can start from this file. |
| [worked_example.csv](data/examples/synthetic/worked_example.csv) | Expected flags and footprint IDs for individual cells on the first five days. |

### Tests and GitHub

Run `python -m pytest -q` for the offline tests. Use the case guide for commands that check a specific stage or the full Milan result. [Stage tests](docs/workflow.md#tests)

| File | What it does |
| --- | --- |
| [tests/build_fixtures.py](tests/build_fixtures.py) | Regenerates the synthetic NetCDFs and CSV under `data/examples/synthetic/`. |
| [tests/unit/test_arco.py](tests/unit/test_arco.py) | Checks UTC day grouping, daily maximum values and missing hourly records. |
| [tests/unit/test_download.py](tests/unit/test_download.py) | Exercises request planning, cache reuse, ZIP handling and failed downloads with a fake CDS client. |
| [tests/unit/test_events.py](tests/unit/test_events.py) | Compares Events output with the expected synthetic event cube. |
| [tests/unit/test_footprints.py](tests/unit/test_footprints.py) | Compares footprint labels and summary values with the worked example. |
| [tests/unit/test_ingest_check.py](tests/unit/test_ingest_check.py) | Checks that the input checker catches a missing date in a saved NetCDF. |
| [tests/unit/test_normalize.py](tests/unit/test_normalize.py) | Builds a synthetic monthly cache and tests the resulting Celsius files, masks and failure paths. |
| [tests/unit/test_report.py](tests/unit/test_report.py) | Checks the values plotted, missing-data coverage, peak-day ties, CSV consistency and PNG exports. |
| [tests/real/conftest.py](tests/real/conftest.py) | Gives the real-data tests access to the chosen case directory and original CDS files. |
| [tests/real/test_case.py](tests/real/test_case.py) | Checks the Milan cubes and independently recomputes thresholds, heatwave runs, component IDs and areas. |
| [tests/real/test_pilot.py](tests/real/test_pilot.py) | Compares the seven-day CDS pilot at one grid cell with the included sample CSV. |
| [tests/real/test_raw_handoff.py](tests/real/test_raw_handoff.py) | Compares July 1991 and July 2022 normalized temperatures with the original CDS monthly files. |
| [.github/workflows/tests.yml](.github/workflows/tests.yml) | Runs offline tests on pull requests and pushes to `main`, with a manually triggered job for the real case. |
| [.github/scripts/check_publication.py](.github/scripts/check_publication.py) | Checks outgoing commit identities and looks for tracked files that should stay local. |
| [.github/pull_request_template.md](.github/pull_request_template.md) | Prompts contributors to describe their change and the tests they ran. |

## Use from Python

Import the stage you need. For example, `heatwave.events.detect.detect_events(baseline, target)` takes two xarray datasets and returns the event layers as a dataset. Install `.[report]` to use `heatwave.report.figures(run_dir)` and get Matplotlib figures from a completed run. [File formats](docs/v1.md)
