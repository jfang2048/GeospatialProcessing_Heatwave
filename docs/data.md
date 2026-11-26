# Get and share the data

From the repository root, activate the project environment and [set up your CDS token](cds-setup.md).

```bash
python -m heatwave.ingest.arco
```

With `uv`, you can run the same command in an isolated environment.

```bash
uv run --isolated --no-project --python 3.12 --with '.[arco]' python -m heatwave.ingest.arco
```

The command reads hourly 2 m temperatures from ECMWF's ERA5-Land ARCO Zarr store and takes the maximum over each UTC day. It writes `runs/milan/baseline.nc` and `runs/milan/target.nc` for May–September 1991–2020 and 2022. The grid is 9 × 15. Use `--run-dir runs/milan-2` to run again in a fresh directory. [ARCO dataset and licence](https://doi.org/10.24381/ee82e357) · [ECMWF guide](https://confluence.ecmwf.int/pages/viewpage.action?pageId=737567208)

Give the team the two NetCDF files through the shared folder. Teammates put them in `runs/milan/` and [start at Events](workflow.md).

## CDS daily product

Use this route for the [pilot notebook](../notebooks/00_pilot.ipynb) or to reuse files already downloaded to `data/raw/cds/`.

```bash
python -m heatwave.ingest.download --profile pilot
# For a full archive already downloaded from CDS
python -m heatwave.ingest.normalize --cache-dir data/raw/cds --baseline-out runs/cds/baseline.nc --target-out runs/cds/target.nc
```

Import a seven-day file already downloaded through the CDS website with `python -m heatwave.ingest.download --import-pilot /path/to/file.nc`. For a pending CDS request, check its ID on [Your Requests](https://cds.climate.copernicus.eu/requests). The [seven-row CSV](../notebooks/data/pilot_milan_cell.csv) contains the daily maxima for 15–21 July 2022 at 45.5°N, 9.2°E in Celsius, rounded to 0.001 °C. [CDS daily dataset and licence](https://doi.org/10.24381/cds.e9c9c792)
