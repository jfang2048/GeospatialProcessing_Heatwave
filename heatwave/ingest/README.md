# Obtain the two temperature input cubes

## Run the pilot

From the repository root, preview the request and cache path.

```bash
python -m heatwave.ingest.download --profile pilot --dry-run
```

For the download, activate the [Conda environment](../../README.md#run-the-starter), accept the CDS dataset terms, and store the API URL and token in your local `~/.cdsapirc`. [CDS API setup](https://cds.climate.copernicus.eu/how-to-api) · [Dataset terms](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=download)

```bash
python -m heatwave.ingest.download --profile pilot
python -m heatwave.ingest.download --profile pilot --verify-only
```

The pilot requests July 15–21, 2022 for the full study area. Find `payload.zip` or `payload.nc` and a checksummed request manifest under `data/raw/cds/<date-range>_<request-hash>/`. List ZIP members with `python -m zipfile -l <payload.zip>`, then open the embedded NetCDF separately. Check the variable name, Kelvin units, coordinates and seven dates with xarray before requesting the baseline.

## Download the full case

```bash
python -m heatwave.ingest.download --profile target
python -m heatwave.ingest.download --profile baseline --year 1991
python -m heatwave.ingest.download --profile baseline
python -m heatwave.ingest.download --profile full --verify-only
```

The full case uses 155 monthly requests for May–September. Reruns reuse verified downloads. Move a corrupt cache entry aside before rerunning its profile. For authentication or terms errors, check the token and dataset terms and compare the pilot with **Show API request code** in the CDS form.

## Share a snapshot

1. The Ingest owner normalizes `baseline.nc` and `target.nc` and assigns a versioned snapshot ID such as `milan-jja-2022-v1`. Record the request manifests, code commit, normalization choices, hashes, sizes, period, grid and units.
2. Store the two cubes in the team's shared folder. Run `sha256sum baseline.nc target.nc > SHA256SUMS` there. Commit a sanitized [snapshot manifest](snapshot.example.json) with attribution and expected hashes. Share restricted URLs privately and follow the [public repository checklist](../../AGENTS.md#public-repository-checklist).
3. Download into ignored `data/snapshots/milan-jja-2022-v1/` and run `sha256sum -c SHA256SUMS` from that directory. For changed data, publish a new snapshot ID and update the manifest in the same PR. Keep earlier versions for reproducibility. [Copernicus catalogue, licence and citation](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics)
