# The Milan grid and figures

## Study area

The case covers Milan and its surroundings on a 9 × 15 ERA5-Land grid. Cell centres span 8.6–10.0°E and 45.1–45.9°N at 0.1° spacing. Maps use the full cell edges, from 8.55–10.05°E and 45.05–45.95°N. A cell near 45.5°N covers about 86.66 km² using the project's spherical area formula. Areas vary with latitude. [File guide](v1.md) · [ERA5-Land ARCO](https://doi.org/10.24381/ee82e357)

The inputs cover May–September because the P90 window uses dates on either side of each summer day. The report covers the 92 days from 1 June to 31 August 2022. Each value is the daily maximum 2 m temperature in Celsius for one UTC date and grid cell.

## Three submission figures

1. **Cell time series.** Plot daily temperature and its P90 threshold on the same °C axis. Give the cell coordinates, highlight heatwave days and show gaps for missing values.
2. **Daily affected area.** Show the observed area in km² and the share of cells with data. A fully observed day with zero qualifying cells has area zero. Mark days with partial coverage and leave a gap when the whole grid is unknown.
3. **Peak-day map.** Use the earliest date with the largest positive observed area, based on unrounded totals. Give the UTC date, area, coverage and data source. Show each component, background and unknown cells on the full grid. Keep the geographic aspect and draw the actual cells. If every observed daily area is zero, report that in the area summary.

Use a sequential °C palette for temperature and P90 and a diverging palette centred on zero for temperature excess. Use distinct colours or outlines for footprint IDs. IDs identify components on a single day and restart the next day.

The reported area measures the qualifying cells inside the study rectangle. Components at the edge can continue beyond it.

## Method references

- Perkins and Alexander define the calendar-day P90 and three-day run used in this study. [Journal of Climate](https://doi.org/10.1175/JCLI-D-12-00383.1) · [ClimPACT2 guide](https://gerinberg.com/climpact/user_guide/html/appendixD.htm)
- Falasca et al. motivate the Milan 2022 case. Puche et al. distinguish air and surface temperature in the same area. [Urban Climate](https://doi.org/10.1016/j.uclim.2023.101728) · [Remote Sensing](https://doi.org/10.3390/rs15030733)
- The ERA5‑Land paper and CDS documentation describe the grid and daily statistics. [ERA5‑Land paper](https://doi.org/10.5194/essd-13-4349-2021) · [Dataset](https://doi.org/10.24381/cds.e9c9c792) · [Daily statistics methods](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505382218)
- Mandonnet et al. describe grouping persistent hot cells. This project applies spatial grouping separately for each day. [Climatic Change](https://doi.org/10.1007/s10584-026-04234-0)
