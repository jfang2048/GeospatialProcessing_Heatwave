# Get and share the data

Activate the project environment and [set up CDS](cds-setup.md). Run commands from the repository root.

```bash
python -m heatwave.ingest.download --profile pilot
python -m heatwave.ingest.download --profile full
```

The pilot is 15–21 July 2022. It provides the grid used by [the pilot notebook](../notebooks/00_pilot.ipynb). The [seven-row CSV](../notebooks/data/pilot_milan_cell.csv) contains UTC daily maximum 2 m air temperatures at 45.5°N, 9.2°E, converted to Celsius and rounded to 0.001 °C. [Copernicus C3S / ECMWF dataset, DOI and licence](https://doi.org/10.24381/cds.e9c9c792)

For a pilot file already downloaded through the CDS website, run `python -m heatwave.ingest.download --import-pilot /path/to/file.nc`.

The full download covers May–September in 1991–2020 and 2022. Files land in `data/raw/cds/`. The script downloads one month at a time and reuses existing files. With `accepted` on the terminal, follow the request ID on [CDS Your Requests](https://cds.climate.copernicus.eu/requests).

## Share the two input files

After [normalization](workflow.md), give the team `baseline.nc` and `target.nc` through the shared folder. Teammates place both files in `runs/milan/` and start at Events. The original CDS downloads stay with FJ.
