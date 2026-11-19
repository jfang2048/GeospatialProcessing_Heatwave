# Reading notes and design choices

## 1. When is a hot day part of a heatwave?

Perkins and Alexander (2013), *On the Measurement of Heat Waves*, §2 uses calendar day P90 of daily maximum temperature from a centred 15 day window, computed separately for each grid cell. Their minimum duration is three consecutive days. The window provides up to 450 values per threshold in a 30 year baseline, and the three day rule captures persistence. The Australia study uses a different analysis season. The Milan proposal applies its TX90 method to June through August, with an explicit boundary rule and a stated coverage threshold. Studies with other thresholds and durations measure a different set of days. See §2 and ClimPACT2 Appendix D. [Paper](https://doi.org/10.1175/JCLI-D-12-00383.1) · [ClimPACT2 guide](https://gerinberg.com/climpact/user_guide/html/appendixD.htm)

## 2. Why Milan and why 2022?

Falasca, Di Bernardino and Salata (2023) use Milan summer 2022 as a case for their Mediterranean Outdoor Thermal Comfort Index. They place that summer in the context of the 1991–2020 reference climate and analyze thermal stress with variables beyond maximum air temperature. This motivates the case year. Thermal comfort episodes describe a different physical quantity, so they provide no reference labels for the grid cell mask. See the abstract and case study methods. [Paper](https://doi.org/10.1016/j.uclim.2023.101728)

## 3. Why choose only air temperature?

Puche, Vavassori and Brovelli (2023) used both remote sensing and in situ air temperature in metropolitan Milan. In their analysis built form could affect the two temperature measures differently even when their temporal series correlate. A heatwave definition based on 2 m air temperature therefore uses the corresponding reanalysis variable directly. Local climate zone and neighbourhood inference would require a separate input and evaluation design. See §2 and the discussion. [Paper](https://doi.org/10.3390/rs15030733)

## 4. What do the grid cells represent?

Muñoz‑Sabater et al. (2021) describe a physically based land reanalysis forced by ERA5, with nominal 9 km resolution. The CDS daily product aggregates hourly values and serves a 0.1° geographic grid. The project uses the maximum of those hourly samples for each UTC day on the native grid. That definition supports repeatability and leaves possible date boundary differences when comparing to a local time series. Reanalysis cells are regional estimates and their footprint area depends on the cell grid and domain. [Technical paper](https://doi.org/10.5194/essd-13-4349-2021) · [Dataset](https://doi.org/10.24381/cds.e9c9c792) · [CDS daily statistics methods](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505382218)

## 5. What does a spatial footprint mean?

Mandonnet et al. (2026), §2.2 first select persistent hot cells and then group adjacent cells across space and time with 26‑neighbour 3D connectivity. The course project keeps cellwise persistence, then runs shared edge connectivity in each daily raster. That makes component membership hand checkable and keeps a single spatial operation in scope. An identifier is valid for one date. Tracking movement, splits and mergers across dates is a separate analysis. [Paper](https://doi.org/10.1007/s10584-026-04234-0)
