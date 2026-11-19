# Mapping daily heatwave footprints around Milan

**Politecnico di Milano · Geospatial Processing · Proposal for approval**

FJ, FY and YY study daily heatwave footprints around Milan and the western Po Valley in June–August 2022, using 1991–2020 as the reference period. The study bounds are 8.6–10.0°E and 45.1–45.9°N on the native 0.1° ERA5‑Land grid.

The pipeline turns daily maximum 2 m air temperature into a heatwave mask, then groups edge-connected cells and reports their area and peak exceedance. The [v1 file contract](contracts/v1.md) defines each stage's inputs, outputs, and acceptance checks. The planned demonstration shows a cell-level time series, daily affected area, and a map of the day with the largest total affected area.

## Run the starter

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
jupyter lab
```

Open the [synthetic notebook](notebooks/00_fixture.ipynb) for a worked example. Use the [synthetic fixtures](integration/fixtures/README.md) to develop and test each stage independently. Follow the [ingest guide](heatwave/ingest/README.md) for the CDS pilot and real data. The [work plan](integration/WORKPLAN.md) covers integration and submission.

## Method references

- Perkins and Alexander define the calendar-day P90 and three-day run used in this study. [Journal of Climate](https://doi.org/10.1175/JCLI-D-12-00383.1) · [ClimPACT2 guide](https://gerinberg.com/climpact/user_guide/html/appendixD.htm)
- Falasca et al. motivate the Milan 2022 case. Puche et al. distinguish air and surface temperature in the same area. [Urban Climate](https://doi.org/10.1016/j.uclim.2023.101728) · [Remote Sensing](https://doi.org/10.3390/rs15030733)
- The ERA5‑Land paper and CDS documentation describe the grid and daily statistics. [ERA5‑Land paper](https://doi.org/10.5194/essd-13-4349-2021) · [Dataset](https://doi.org/10.24381/cds.e9c9c792) · [Daily statistics methods](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505382218)
- Mandonnet et al. describe grouping persistent hot cells. This project applies spatial grouping separately for each day. [Climatic Change](https://doi.org/10.1007/s10584-026-04234-0)

**Approval requested.** Is a single Milan case at the ERA5‑Land grid scale suitable for the course, using a custom percentile and run detector followed by daily connected footprint analysis?

## Contribute

Follow the [public repository checklist](AGENTS.md#public-repository-checklist) before every push.
