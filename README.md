# Daily heatwave footprints around Milan

This Python project maps persistent summer heat around Milan in June–August 2022. It compares ERA5-Land daily maximum 2 m air temperatures against a 1991–2020 local reference, then measures the area and peak temperature exceedance of each daily footprint. The seven-day real-data pilot has been verified. The full Milan case requires the reference and target data.

## Quick start

From the repository root, create the environment and open the worked example.

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
python -m pip install -e .
jupyter lab notebooks/00_fixture.ipynb
```

The editable install makes the `heatwave` package importable from any directory and uses the code under `src/` as you edit it.

For the real case, set up CDS access, read the ERA5-Land ARCO archive, then follow the run commands to produce `events.nc`, `footprints.nc`, `footprints.csv` and the case notebook. If you have the team's `baseline.nc` and `target.nc`, start at Events. [CDS setup](docs/cds-setup.md) · [Download and share data](docs/data.md) · [Run and test the case](docs/workflow.md)

## Repository layout

```text
README.md                       Project overview, setup and navigation
AGENTS.md                       Ownership, local releases and privacy checks
environment.yml / pyproject.toml Environment and Python package settings
docs/
  cds-setup.md                  CDS account, token and first download
  data.md                       Download data and share the two NetCDF inputs
  workflow.md                   Run commands, tests and submission
  v1.md                         File formats and validation at each handoff
  geography.md                  Study area, method references and map specifications
src/heatwave/                   Installable Python library
  ingest/                       ARCO download and conversion to Celsius (FJ)
  events/                       P90 and heatwave days (YY)
  footprints/                   Connected areas and daily CSV (FY)
tests/
  unit/                         Offline tests, run with python -m pytest
  real/                         Tests using downloaded data and analysis outputs
  build_fixtures.py             Regenerate the small synthetic sample files
data/
  examples/                     Small committed datasets for the notebooks
  raw/cds/                      Original CDS downloads, stored locally
  processed/milan/              Local files from the Milan pipeline
    baseline.nc / target.nc     Celsius input cubes for Events
    events.nc                   Daily heatwave flags for Footprints
    footprints.nc / .csv        Footprint labels and area summaries
notebooks/                      Notebook templates and worked examples
reports/                        Executed notebooks and figures, stored locally
.github/                        Tests and release checks
```

- Get data or share the two input files with the team. [Data guide](docs/data.md)
- Check file dimensions, units, flags and outputs. [File contract](docs/v1.md)
- Find test commands and requirements for the final demonstration. [Workflow](docs/workflow.md) · [Notebook examples](notebooks/) · [Map specifications](docs/geography.md)
- Find ownership and publication rules before contributing. [Contribution rules](AGENTS.md)
