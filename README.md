# Mapping daily heatwave footprints around Milan

**Politecnico di Milano · Geospatial Processing · Proposal for approval**

Team: FJ, YY, FY. The proposed assignment to modules is in the [work plan](integration/WORKPLAN.md). This repository template includes a downloader, a synthetic example and interface specifications. The heatwave analysis library is the work proposed below.

## Research question

During June to August 2022, when did sustained extreme daytime air temperatures occur around Milan, and which contiguous parts of the model grid were affected on each day?

We propose a small Python library for processing a gridded temperature cube. Users provide daily maximum temperatures for a reference period and a target summer. The library returns a grid of heatwave days, connected footprints for each day, and a table with footprint area and peak exceedance. A notebook will show the temperature series at one grid cell, the total affected area over time, and a map on the day with the greatest total affected area. The same functions can be reused for other summer datacubes on a regular latitude and longitude grid.

## Study design

| Item | Proposed specification |
| --- | --- |
| Study area | Milan and the surrounding western Po Valley. WGS 84 grid centre bounds of 8.6–10.0°E and 45.1–45.9°N. |
| Temperature input | Copernicus ERA5‑Land daily statistics, 2 m air temperature, daily maximum of hourly samples, 0.1° grid. Every day uses UTC. |
| Reference and target | Reference summers from 1991 to 2020. Demonstration window from 1 June to 31 August 2022. Fetch May to September for every year to support the calendar window at the ends of summer. |
| Threshold | At each cell and calendar date, compute P90 from the pooled samples in the centred 15 day window from the 30 reference years. This gives up to 450 samples per cell and date. |
| Heatwave days | At each cell, mark every day in a run of at least three consecutive dates with daily maximum temperature strictly above its threshold. Missing inputs break a run. The detection period is bounded by June and August. |
| Footprints | Within each day, label heatwave cells connected through a shared raster edge. Sum latitude dependent cell areas and report peak exceedance above P90 for each component. |
| Outputs | Labelled NetCDF cube, footprint CSV, and reproducible notebook. Footprint IDs are local to a date. |

For example, three consecutive days at 33, 34 and 35 °C with a local daily threshold of 32 °C all enter the heatwave mask. On each day, a neighbouring cell belongs to the same footprint if it also qualifies that day and shares an edge. The peak exceedance for the first cell is 3 °C on the third day. The spatial area comes from the qualifying grid cells, whose widths decrease with latitude.

The processing steps developed by the group are the calendar window and run detector, the quality checked ingestion of the gridded input, and the area aware spatial footprint summaries. The module reports regional reanalysis patterns at approximately 9 km resolution. Its estimates describe daytime air temperature. Heat stress, neighbourhood scale urban heat islands, and spatial tracking of components across dates sit outside the proposed scope.

## Why this design

| Evidence | Design decision |
| --- | --- |
| Perkins and Alexander compare heatwave definitions, including at least three consecutive days above the daily maximum temperature P90. | Adapt their centred 15 day TX90 rule and document the local baseline and summer boundary convention. [Journal of Climate](https://doi.org/10.1175/JCLI-D-12-00383.1) |
| Falasca and colleagues use Milan summer 2022 to study both extreme air temperature and thermal comfort. | Choose 2022 as a motivated case. Their comfort indices address a separate question and provide qualitative context for this case. [Urban Climate](https://doi.org/10.1016/j.uclim.2023.101728) |
| Puche, Vavassori and Brovelli study both satellite surface temperature and measured air temperature in metropolitan Milan and find different relationships with building height. | Use 2 m air temperature as the sole core variable and keep the interpretation at the native regional grid scale. [Remote Sensing](https://doi.org/10.3390/rs15030733) |
| The ERA5‑Land technical paper documents the reanalysis and its grid. | Preserve native grid coordinates and cite the data product, with no downscaling in the library. [Earth System Science Data](https://doi.org/10.5194/essd-13-4349-2021) · [CDS data catalogue](https://doi.org/10.24381/cds.e9c9c792) |
| Published heatwave classification uses connected components across space and time. | Use a simpler daily 2D footprint after cellwise temporal detection. This provides spatial extent within the course scope. [Climatic Change](https://doi.org/10.1007/s10584-026-04234-0) |

## Verification and feasibility

1. Hand check a synthetic grid for exact P90 equality, two versus three hot days, missing dates and cell values, diagonal versus edge contact, and known component areas. Commit the small fixture and keep the demo runnable without portal access.
2. Request a seven day July 2022 CDS pilot for the full study area. Confirm requested days, units, grid extent and coordinates before queueing the reference years. The pilot checks data access and normalization. It does not produce a TX90 estimate.
3. For the full case, verify the date coverage and grid consistency. For each day, check that the sum of component areas equals the area of the corresponding heatwave mask. Explain the day with the greatest total affected area using its date, area, largest component, grid map and one time series. Reference coverage and unknown grid cells will be reported separately. The published 2022 Milan study is context for the choice of year. Numerical validation is based on the hand checked fixture and consistency checks.
4. Reproduce the demonstration notebook from a clean environment. Each of the three members contributes source code and tests through individual commits and can explain the complete workflow.

**Approval requested.** Is a single ERA5‑Land case study with a custom percentile/run detector and daily connected footprint analysis an appropriate scope for the course library? Is regional grid analysis around Milan suitable for the proposed research question?

## Review the starter

The [technical contract](contracts/v1.md) fixes the file handoffs. The [work plan](integration/WORKPLAN.md) lists owners, deliverables and rehearsal milestones. The [reading notes](integration/LITERATURE.md) document the choices from the literature. Read the [collaboration rules](AGENTS.md) before contributing.

Create the environment with `conda env create -f environment.yml`, activate `gprocessing-heatwave` and start the [synthetic notebook](notebooks/00_fixture.ipynb) with `jupyter lab`. The notebook currently demonstrates expected fixture results. The full case notebook will call the three library modules after implementation.

The [data acquisition guide](heatwave/ingest/README.md) provides the offline request preview, authenticated download, checksum verification, and shared snapshot procedure.
