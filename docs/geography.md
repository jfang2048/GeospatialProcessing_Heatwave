# Study grid and map interpretation

## Spatial and temporal support

| Property | Milan case | How to verify |
| --- | --- | --- |
| Geographic extent | Centre coordinates from 8.6 to 10.0°E and 45.1 to 45.9°N, both inclusive. The rectangular domain includes Milan and surrounding territory. | The CDS request uses north, west, south, east: `[45.9, 8.6, 45.1, 10.0]`. Inspect the seven-day pilot before accepting the real grid. |
| Grid and coordinates | CDS distributes a regular geographic grid at 0.1° × 0.1°. The underlying ERA5-Land model has approximately 9 km native resolution. The project uses the delivered grid throughout. | Expect 9 latitude rows × 15 longitude columns = 135 centres before masking. Verify spacing, endpoints and ordering. Report discrepancies before normalizing the real case. |
| Spatial reference and axis order | Interpret centres as geographic WGS 84 latitude and longitude in degrees. NetCDF arrays use `(time, lat, lon)`. Maps have longitude increasing to the right and latitude increasing upwards. | Preserve the coordinates. Check the southwest and northeast cells against their array indices. Draw cell boundaries at half steps around the centres. |
| Raster footprint | Expected outer edges are **8.55–10.05°E, 45.05–45.95°N**. Footprint areas include full qualifying cells inside these edges. | Derive edges from the actual coordinates. With the project's spherical approximation, a cell at 45.5°N covers about 86.66 km². Latitude changes cell area. |
| Measurement and time | Reanalysis of air temperature 2 m above ground. Each input value is the maximum of hourly samples on one UTC date. Reference input covers May–September of 1991–2020. Target input covers May–September 2022. | Expect 4,590 and 153 daily slices respectively. The reported interval is 1 June–31 August 2022 inclusive (92 dates). May and September supply reference-window context. |

These dimensions describe the requested real case. The [committed example](workflow.md#synthetic-fixtures) uses a 2 × 3 grid. Its smaller extent lets a reviewer check every cell. The CDS catalogue distinguishes the delivered grid spacing from the model resolution. [Product documentation](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=overview)

## Raster layers

All layers share the input grid. Each value refers to one cell and one UTC date. The ranges below describe the meaning of each variable. Report the actual finite minimum and maximum from the selected data when displaying a continuous layer.

| Layer | Measurement and value range | Map convention |
| --- | --- | --- |
| `tx_c` | Daily maximum air temperature, continuous °C. Values may fall below zero. | Sequential colour scale with °C legend. For side-by-side dates or thresholds, use common limits. |
| `p90_c` | Local 90th-percentile reference temperature for the same month/day, continuous °C. | Use the temperature scale and identify the reference period and 15-day window. |
| `excess_c` | Signed temperature difference, `tx_c − p90_c`, in °C. Zero means equality, positive means above threshold. | Diverging colours centred on zero. Persistence is encoded separately by the event flag. |
| `heatwave_flag` | Categorical raster. `1` is a day in a qualifying run, `0` is observed without a qualifying run, `-1` is unknown. | Three distinct legend entries. Use an explicit unknown symbol or hatch. |
| `footprint_id` | Nominal raster. Positive integers identify edge-connected components on that date, `0` is background, `-1` is unknown. | Discrete colours or component outlines. IDs restart each day and carry no intensity or rank. |

## Three submission figures

1. **Cell time series.** Identify the selected grid centre by longitude and latitude. Plot daily `tx_c` and `p90_c` in °C against UTC dates, highlight qualifying days and leave gaps where a series is missing.
2. **Daily affected area.** Keep all 92 UTC dates on the axis. Sum the nominal spherical areas of cells with flag `1` in km². Report the number or fraction of known cells alongside the series. A fully observed day without a component is zero. For partial coverage, show the observed area and mark the day incomplete. For a wholly unknown day, show a gap. Use the flag raster to distinguish these cases because the summary CSV has no row for an empty day.
3. **Peak-day footprint map.** Select the earliest date tied for the greatest positive observed area, comparing unrounded daily totals. Give the UTC date, observed area, coverage and data source. Show component boundaries or colours, background and unknown cells. Use the full cell-edge extent, label axes in degrees, show north upwards and preserve the approximate local aspect at the domain's mid-latitude. Render categorical cells without smoothing. With no positive area, report whether observations were available and omit the peak-day map.

A component touching the edge may continue outside the study domain. The area represents qualifying grid cells inside the rectangle. Municipal land area, neighbourhood-scale temperature, population exposure and heatwave motion would each require additional data or analysis. The [file contract](v1.md) gives the cell-area formula, connectivity and missing-value rules.

## Method references

- Perkins and Alexander define the calendar-day P90 and three-day run used in this study. [Journal of Climate](https://doi.org/10.1175/JCLI-D-12-00383.1) · [ClimPACT2 guide](https://gerinberg.com/climpact/user_guide/html/appendixD.htm)
- Falasca et al. motivate the Milan 2022 case. Puche et al. distinguish air and surface temperature in the same area. [Urban Climate](https://doi.org/10.1016/j.uclim.2023.101728) · [Remote Sensing](https://doi.org/10.3390/rs15030733)
- The ERA5‑Land paper and CDS documentation describe the grid and daily statistics. [ERA5‑Land paper](https://doi.org/10.5194/essd-13-4349-2021) · [Dataset](https://doi.org/10.24381/cds.e9c9c792) · [Daily statistics methods](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505382218)
- Mandonnet et al. describe grouping persistent hot cells. This project applies spatial grouping separately for each day. [Climatic Change](https://doi.org/10.1007/s10584-026-04234-0)
