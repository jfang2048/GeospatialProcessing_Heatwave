# Mapping daily heatwave footprints around Milan

**Politecnico di Milano · Geospatial Processing**

**Research question.** Where did unusually hot days persist for at least three consecutive days around Milan during June–August 2022, and how much of the study grid did they cover each day? FJ, FY and YY compare the 2022 daily maximum 2 m air temperature at each cell with its local 1991–2020 calendar-day threshold.

The requested cell centres span **8.6–10.0°E and 45.1–45.9°N** in the western Po Valley. The CDS product supplies a regular **0.1° × 0.1°** grid. At 45.5°N this is about **7.8 km east–west by 11.1 km north–south**. The rectangle includes Milan and surrounding territory. The analysis describes persistent heat at this regional scale. See the [grid, time coverage and map specifications](contracts/geography.md) and the [CDS product description](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=overview).

The pipeline turns daily maximum 2 m air temperature into a heatwave mask, then groups edge-connected cells and reports their area and peak exceedance. The [v1 file contract](contracts/v1.md) defines each stage's inputs, outputs and acceptance checks. The [case notebook](notebooks/01_case.ipynb) reads the resulting files to show a cell-level time series, daily affected area and a map of the day with the largest observed footprint.

**Implementation status.** The seven-day CDS pilot has been downloaded and checked. All 945 temperatures on the 9 × 15 grid are present. The three processing commands and full-case notebook are implemented. Verification of summer heatwave dates and areas awaits the full 1991–2020 reference and 2022 target.

## Run the starter

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
```

Start with the **real seven-day sample** (15–21 July 2022). Configure your personal CDS account and accept the dataset terms as described in the [ingest guide](heatwave/ingest/README.md). These commands download the requested Milan area, verify the cache and inspect the actual provider data. The sample tests input format and coverage. The long reference period is needed for the heatwave thresholds.

```bash
python -m heatwave.ingest.download --profile pilot
python -m heatwave.ingest.download --profile pilot --verify-only
python -m pytest -q integration/real_tests/test_pilot.py
```

The [seven-row sample](integration/pilot_milan_cell.csv) is a real extract from the official Copernicus Climate Change Service / ECMWF ERA5-Land daily statistics product. At 45.5°N, 9.2°E, the maximum on 15 July was **36.662 °C**. The CSV gives UTC dates and temperatures converted from Kelvin and rounded to 0.001 °C. The [pilot notebook](notebooks/00_pilot.ipynb) reads the verified full grid. The cell values and map describe daily temperatures; classifying a heatwave also requires the reference distribution. [Dataset and CC-BY licence](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=overview) · [Pilot file provenance](heatwave/ingest/README.md#verified-pilot)

For the **full Milan case**, use a fresh output directory. Run from the repository root after the pilot passes.

```bash
python -m heatwave.ingest.download --profile full
python -m heatwave.ingest.download --profile full --verify-only
python -m heatwave.ingest.normalize --cache-dir data/raw/cds --baseline-out runs/milan/baseline.nc --target-out runs/milan/target.nc
python -m heatwave.events.detect --baseline runs/milan/baseline.nc --target runs/milan/target.nc --out runs/milan/events.nc
python -m heatwave.footprints.summarize --events runs/milan/events.nc --labels-out runs/milan/footprints.nc --summary-out runs/milan/footprints.csv
python -m pytest -q
python -m nbconvert --to notebook --execute notebooks/01_case.ipynb --output-dir runs/milan
```

With verified real normalized cubes from a teammate, start at Events and run `python -m pytest -q integration/real_tests/test_case.py` after Footprints. Record the snapshot identifier and SHA-256 checksums. The full suite also needs the raw pilot and monthly inputs. [Source and snapshot preparation](heatwave/ingest/README.md) · [Work plan](integration/WORKPLAN.md)

## Method references

- Perkins and Alexander define the calendar-day P90 and three-day run used in this study. [Journal of Climate](https://doi.org/10.1175/JCLI-D-12-00383.1) · [ClimPACT2 guide](https://gerinberg.com/climpact/user_guide/html/appendixD.htm)
- Falasca et al. motivate the Milan 2022 case. Puche et al. distinguish air and surface temperature in the same area. [Urban Climate](https://doi.org/10.1016/j.uclim.2023.101728) · [Remote Sensing](https://doi.org/10.3390/rs15030733)
- The ERA5‑Land paper and CDS documentation describe the grid and daily statistics. [ERA5‑Land paper](https://doi.org/10.5194/essd-13-4349-2021) · [Dataset](https://doi.org/10.24381/cds.e9c9c792) · [Daily statistics methods](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505382218)
- Mandonnet et al. describe grouping persistent hot cells. This project applies spatial grouping separately for each day. [Climatic Change](https://doi.org/10.1007/s10584-026-04234-0)

## Contribute

The team is developing one regional heatwave-footprint module. Its three stages prepare inputs, detect persistent heat at each cell and measure connected areas on each date. Each member contributes through their own commits and pushes and should be able to explain the full path from daily temperatures to mapped areas. See the [course deliverables](integration/WORKPLAN.md#course-deliverables) and [public repository checklist](AGENTS.md#public-repository-checklist).
