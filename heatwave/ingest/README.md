# Obtain the two temperature input cubes

## Download a pilot first

From the repository root, preview the exact request and its cache path without any dependencies or credentials:

```bash
python -m heatwave.ingest.download --profile pilot --dry-run
```

For a real download, create a CDS account, accept the dataset terms in the CDS web form, and put the current API URL and personal access token in your home directory's `.cdsapirc` according to the official instructions. Use the Conda environment in the root README. [CDS API setup](https://cds.climate.copernicus.eu/how-to-api) · [Dataset terms and download](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=download)

```bash
python -m heatwave.ingest.download --profile pilot
python -m heatwave.ingest.download --profile pilot --verify-only
```

The pilot is July 15–21, 2022. It makes a single CDS request for the whole study box. The download is stored under `data/raw/cds/<date-range>_<request-hash>/` as `payload.zip` or `payload.nc` with `manifest.json`. A manifest pins the exact parameters, provider citation and byte checksum. ZIP products are kept as returned and can be listed with `python -m zipfile -l <payload.zip>`. The data normalizer is planned for the Ingest module. Before requesting the baseline, use xarray to confirm the pilot's variable name, Kelvin units, coordinates and all seven days. A ZIP's embedded NetCDF must be opened separately by the normalizer.

## Hydrate the real case

```bash
python -m heatwave.ingest.download --profile target
python -m heatwave.ingest.download --profile baseline --year 1991
python -m heatwave.ingest.download --profile baseline
python -m heatwave.ingest.download --profile full --verify-only
```

The real case uses one request per calendar month from May to September. The full run consists of 155 requests. Known good requests are reused and interrupted downloads can be rerun. The full variable array is roughly 2.6 MB in float32 (31 × 153 × 135 × 4 bytes, assuming both endpoints of the box), before container and coordinate overhead. CDS queue and packaging latency drive the download time. If verification reports a corrupt cache entry, move that request directory aside and rerun the same profile. If authentication or terms fail, compare the pilot with “Show API request code” in the official form, confirm the personal token and dataset terms, and retry. The downloader does not use a live CDS credential in its tests.

## Share one snapshot with the group

1. The Ingest owner retrieves and normalizes the provider files once. Give the resulting `baseline.nc` and `target.nc` a fixed snapshot ID such as `milan-jja-2022-v1`. Record the exact input request manifests, code commit, normalization choices, file SHA‑256 hashes, byte counts, period, grid and units.
2. Store two versioned files or a small archive in one project shared drive folder with immutable versioned filenames and stable read links for the whole team. Put the links, release notes, attribution and expected hashes in a small tracked snapshot manifest under `heatwave/ingest/`. Use [snapshot.example.json](snapshot.example.json) as the starting schema. Inside the snapshot folder run `sha256sum baseline.nc target.nc > SHA256SUMS` and share the checksum file alongside both cubes. With a private drive, give the professor and tutor access before using the snapshot to assess the real case. Keep tokenized links and credentials outside Git.
3. Each teammate downloads that exact snapshot into ignored `data/snapshots/milan-jja-2022-v1/`, verifies it using `sha256sum -c SHA256SUMS` from the snapshot directory, and runs code locally. Release a new snapshot ID for any data change and update the manifest in one PR. Preserve the previous snapshot to reproduce earlier outputs. If the link fails or access changes, the tracked request specifications and checksummed manifests identify how to recover it.
4. Git stores the source, request recipe, manifests, and synthetic tests. A GitHub release asset is an alternative host for a small distributable snapshot. DVC with a remote is useful when regular dataset revisions and automated fetches justify the shared storage and account setup. For this case, one shared versioned snapshot plus a simple tracked manifest is sufficient. Confirm distribution terms and include Copernicus attribution based on the [catalogue licence and citation](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics).
