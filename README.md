# Daily heatwave footprints around Milan

This Python project maps persistent summer heat around Milan in June–August 2022. It compares ERA5-Land daily maximum 2 m air temperatures against a 1991–2020 local reference, then measures the area and peak temperature exceedance of each daily footprint. The seven-day real-data pilot has been verified. The full Milan case requires the reference and target data.

## Quick start

From the repository root, create the environment and open the worked example.

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
jupyter lab notebooks/00_fixture.ipynb
```

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
heatwave/
  ingest/                       Prepare the two NetCDF inputs (FJ)
    arco.py                     Read hourly ARCO and write the two input cubes
    download.py                 Download or import the CDS daily product
    normalize.py                Convert cached CDS daily files to the two cubes
    requests.py / cache.py      Request plan and on-disk cache
    provider.py                 Decode provider dates, coordinates and values
  events/detect.py              Calculate percentiles and detect heatwave days (YY)
  footprints/summarize.py       Label daily footprints and write the CSV (FY)
  _handoff.py                   Shared grid and output file conventions
tests/real/                     Tests that use CDS inputs and case outputs
notebooks/                      Worked example, real pilot and full case
  data/                         Synthetic examples and the seven-day cell CSV
.github/                        CI, PR template and public-release check
data/ and runs/                 Local data and outputs, ignored by Git
```

- Get data or share the two input files with the team. [Data guide](docs/data.md)
- Check file dimensions, units, flags and outputs. [File contract](docs/v1.md)
- Find test commands and requirements for the final demonstration. [Workflow](docs/workflow.md) · [Notebook examples](notebooks/) · [Map specifications](docs/geography.md)
- Find ownership and publication rules before contributing. [Contribution rules](AGENTS.md)
