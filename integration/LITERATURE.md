# Reading notes and design choices

## Heatwave threshold and duration

Perkins and Alexander (2013) use a cell-specific calendar-day P90 from a centred 15-day window and require at least three consecutive hot days. The Milan case applies that method to June–August with a defined coverage threshold and summer boundary. A 30-year baseline supplies up to 450 samples per date and cell. [Paper, §2](https://doi.org/10.1175/JCLI-D-12-00383.1) · [ClimPACT2 guide](https://gerinberg.com/climpact/user_guide/html/appendixD.htm)

## Milan in 2022

Falasca, Di Bernardino and Salata (2023) study Milan's summer 2022 in the context of the 1991–2020 climate. Their thermal comfort analysis motivates the case year. The heatwave mask is validated using the synthetic fixture and internal consistency checks. [Paper](https://doi.org/10.1016/j.uclim.2023.101728)

## Temperature and grid scale

Puche, Vavassori and Brovelli (2023) distinguish the effects of built form on land surface and air temperature. This project uses 2 m air temperature and interprets results at the regional grid scale. [Paper](https://doi.org/10.3390/rs15030733)

Muñoz‑Sabater et al. (2021) describe ERA5‑Land's nominal 9 km grid. This project uses the CDS product's native 0.1° grid and the maximum of hourly samples for each UTC day. Cell area varies with latitude. [Technical paper](https://doi.org/10.5194/essd-13-4349-2021) · [Dataset](https://doi.org/10.24381/cds.e9c9c792) · [Daily statistics methods](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505382218)

## Daily footprints

Mandonnet et al. (2026) label persistent hot cells in space and time. This project applies the persistence test per cell, then groups cells sharing a raster edge within each day. Identifiers are local to each date. [Paper, §2.2](https://doi.org/10.1007/s10584-026-04234-0)
