# Mapping daily heatwave footprints around Milan

**Politecnico di Milano · Geospatial Processing · Proposal for approval**

Team members FJ, FY and YY study when sustained daytime heat occurred around Milan from June through August 2022 and which contiguous grid cells experienced it each day.

The proposed Python library takes daily maximum temperature cubes for a reference period and a target summer. It produces a heatwave mask, daily connected footprints, and a table of footprint areas and peak temperature exceedances. The demonstration notebook will show a cell-level temperature series, daily affected area, and a map of the day with the largest total footprint area.

## Study design

| Item | Specification |
| --- | --- |
| Study area | Milan and the western Po Valley. WGS 84 grid centre bounds of 8.6–10.0°E and 45.1–45.9°N. |
| Temperature | Copernicus ERA5‑Land daily statistics. Daily maximum of hourly 2 m air temperature on a 0.1° grid, with days in UTC. |
| Reference and target | 1991–2020 reference summers and June–August 2022 target. Fetch May–September for each year to cover the threshold window at the summer boundaries. |
| Threshold | At each cell and calendar date, calculate P90 from a centred 15-day window pooled across 30 reference years, up to 450 samples. |
| Heatwave days | Mark each day in a run of at least three consecutive days strictly above P90. Missing inputs break a run. Evaluate June through August. |
| Footprints | Group cells sharing an edge on each day. Sum latitude-dependent cell areas and report each component's peak exceedance above P90. |
| Outputs | Labelled NetCDF, footprint CSV, and demonstration notebook. Footprint IDs are local to each date. |

The analysis describes regional daytime air temperature at the native ERA5‑Land scale of about 9 km. The [reading notes](integration/LITERATURE.md) explain the choices behind the case and method.

## Validation and approval

1. Hand-check synthetic cases for P90 equality, run length, missing inputs, edge and diagonal contacts, and component area.
2. Run a seven-day CDS pilot in July 2022 and verify dates, units and grid coordinates before requesting the full reference period.
3. For the full case, check date coverage and grid consistency. Compare the summed footprint areas with the heatwave mask area and report reference coverage and unknown cells. Use the map and time series to explain the day with the largest total affected area.
4. Run the demonstration from a clean environment. Each member contributes code and tests and can explain the workflow.

**Approval requested.** Is one Milan case at the ERA5‑Land grid scale suitable for the course, with a custom percentile and run detector followed by daily connected footprint analysis?

## Run the starter

```bash
conda env create -f environment.yml
conda activate gprocessing-heatwave
jupyter lab
```

Open the [synthetic notebook](notebooks/00_fixture.ipynb) for a worked example. See the [data acquisition guide](heatwave/ingest/README.md) for CDS requests and the [file contract](contracts/v1.md) for module handoffs. The [work plan](integration/WORKPLAN.md) lists owners and milestones.

## Contribute

This repository is public. Use team initials and review every outgoing commit for private information before pushing. Set your repository-local Git identity and follow the [public repository checklist](AGENTS.md#public-repository-checklist).
