# Set up CDS access

1. Sign in to CDS and accept the terms on the ERA5-Land daily statistics download page. [Dataset page](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=download)
2. Copy your API URL and personal access token from the signed-in setup page to `~/.cdsapirc`. Keep the token in this local file. [CDS API setup](https://cds.climate.copernicus.eu/how-to-api)

   ```text
   url: https://cds.climate.copernicus.eu/api
   key: <personal-access-token>
   ```

   ```bash
   chmod 600 ~/.cdsapirc
   ```

3. Activate the [project environment](../README.md#quick-start). Run the seven-day download and verify it.

   ```bash
   python -m heatwave.ingest.download --profile pilot
   python -m heatwave.ingest.download --profile pilot --verify-only
   ```

   For a local terminal with `uv`, this is the equivalent download command.

   ```bash
   uv run --isolated --no-project --python 3.12 --with 'cdsapi>=0.7.7' \
     python -m heatwave.ingest.download --profile pilot
   ```

See the [data guide](data.md) for pilot import, the full download and snapshot sharing.
