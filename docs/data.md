# Get the Milan data

FJ runs the command below and shares the two NetCDF files. If a teammate has already sent you both files, put them in `data/processed/milan/` and start at Events in the [case guide](workflow.md).

## Get the full case with ARCO

From the repository root, activate the project environment and set up your [CDS token](cds-setup.md).

```bash
python -m heatwave.ingest.arco
```

The command reads hourly ERA5-Land temperatures for the 9 × 15 Milan grid and takes the daily maximum in UTC. It writes both files under `data/processed/milan/`. [ERA5-Land ARCO dataset](https://doi.org/10.24381/ee82e357) · [ECMWF guide](https://confluence.ecmwf.int/pages/viewpage.action?pageId=737567208)

| File | Dates | Used for |
| --- | --- | --- |
| `baseline.nc` | May–September, 1991–2020 | The local temperature threshold |
| `target.nc` | May–September, 2022 | The summer being studied |

ARCO opens the written files before publishing them and compares every saved temperature with a separate calculation from the original hourly values. Before sharing, you can rerun the file checks with `python -m heatwave.ingest.check`. Add `--pilot path/to/payload.nc` to compare the seven July days against a separately downloaded CDS daily file. The comparison checks dates, coordinates, missing cells and temperatures to 0.001 °C.

If you use `uv`, the equivalent command installs the library and its ARCO dependencies in an isolated environment.

```bash
uv run --isolated --no-project --python 3.12 --with '.[arco]' python -m heatwave.ingest.arco
```

## Seven-day pilot and existing CDS files

Run `python -m heatwave.ingest.download --profile pilot` to get 15–21 July 2022 for the [pilot notebook](../notebooks/00_pilot.ipynb). To import a pilot file from the CDS website, use `python -m heatwave.ingest.download --import-pilot /path/to/file.nc`. The repository also includes the seven daily maxima at 45.5°N, 9.2°E in Celsius, rounded to 0.001 °C. [Sample CSV](../data/examples/pilot_milan_cell.csv) · [CDS daily dataset](https://doi.org/10.24381/cds.e9c9c792)

If you have all the monthly CDS downloads in `data/raw/cds/`, you can turn them into the same pair of input files.

```bash
python -m heatwave.ingest.normalize --cache-dir data/raw/cds \
  --baseline-out data/processed/cds/baseline.nc --target-out data/processed/cds/target.nc
```
