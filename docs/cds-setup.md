# Set up your CDS token

Sign in to the Climate Data Store and copy the URL and token shown on your account's API setup page into `~/.cdsapirc`. [CDS API setup](https://cds.climate.copernicus.eu/how-to-api)

```text
url: https://cds.climate.copernicus.eu/api
key: <personal-access-token>
```

Run `chmod 600 ~/.cdsapirc` to keep the token file private. Activate the [project environment](../README.md#quick-start) and follow the [data guide](data.md). To update an existing environment, run `conda env update -n gprocessing-heatwave -f environment.yml` and reinstall the checkout with `python -m pip install -e .`.

The seven-day pilot has its own CDS daily-product terms. Accept them once on the [pilot dataset page](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=download).
