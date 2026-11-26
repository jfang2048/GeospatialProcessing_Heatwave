# Set up the CDS token

1. Sign in to CDS. Copy your API URL and token into your local `~/.cdsapirc`. [CDS API setup](https://cds.climate.copernicus.eu/how-to-api)

   ```text
   url: https://cds.climate.copernicus.eu/api
   key: <personal-access-token>
   ```

   ```bash
   chmod 600 ~/.cdsapirc
   ```

2. Activate the [project environment](../README.md#quick-start). If you already have the environment, update it with `conda env update -n gprocessing-heatwave -f environment.yml`. Install this checkout with `python -m pip install -e .` after updating the environment. Then follow the [data guide](data.md).

For the separate seven-day pilot downloaded from the CDS daily statistics product, accept its terms once on the [dataset page](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=download).
