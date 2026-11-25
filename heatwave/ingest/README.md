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

For a pilot downloaded through the signed-in CDS web form, select the file using the import command. Use the actual path to the downloaded ZIP or NetCDF.

```bash
python -m heatwave.ingest.download --import-pilot /path/to/download
python -m pytest -q integration/real_tests/test_pilot.py
```

The pilot covers 15 to 21 July 2022. The importer decodes the file, checks the variable, Kelvin units, daily times, Milan grid and presence of finite temperatures, then stores the original bytes under `data/raw/cds/<date-range>_<request-hash>/`. Its local manifest records the original filename, import time, matching pilot request and SHA-256. The supply method identifies a user-provided file. Keep the CDS request or download receipt with the private run records to document provider provenance. An API retrieval records its retrieval time separately. The cache accepts equivalent one-month manifests written before the CDS month field was changed to a string.

## Verified pilot

The CDS web form returned a 27,089-byte NetCDF for 15–21 July 2022 with SHA-256 `1d2b8e5840bfd92250978453194679ef19494dbcfd5681d9c8c34a9f32fa323c`. The observed field was float32 `t2m(valid_time, latitude, longitude)` in K, containing seven dates, nine latitudes and fifteen longitudes. All 945 values were finite. The lowest and highest daily maxima over these grid cells and dates were 22.972 °C and 37.525 °C. This digest identifies the specific download used for the [published cell extract](../../integration/pilot_milan_cell.csv). Equivalent re-exports may have different file bytes.

## Download the full case

```bash
python -m heatwave.ingest.download --profile full
python -m heatwave.ingest.download --profile full --verify-only
```

Set up the CDS API and download the pilot successfully before running verification. An empty cache has no manifest to verify. The full case uses 155 monthly requests for May–September. Reruns reuse verified downloads. Move a corrupt cache entry aside before rerunning its profile. For authentication or terms errors, check the token and dataset terms and compare the pilot with **Show API request code** in the CDS form.

## Normalization handoff to Events

The normalizer reads the verified monthly entries of the full request plan. It checks each entry's manifest, request, byte count and SHA-256 before using its NetCDF payload. A direct NetCDF or a ZIP containing one NetCDF member is accepted. The separate seven-day pilot may coexist with the monthly entries. Missing entries stop the run.

```bash
mkdir -p runs/milan
python -m heatwave.ingest.normalize --cache-dir data/raw/cds --baseline-out runs/milan/baseline.nc --target-out runs/milan/target.nc
```

The reader expects Kelvin `t2m` on `latitude`, `longitude` and `time` or `valid_time`. It checks the decoded dates and requested grid, unpacks CF temperature values, preserves masks, and sorts both axes into increasing order. Additional dimensions require a documented mapping from the actual provider pilot.

For acceptance, Events receives two [v1 cubes](../../contracts/v1.md) with 4,590 baseline dates and 153 target dates. Once the full provider cache and normalized outputs are in place, run `python -m pytest -q integration/real_tests/test_raw_handoff.py`. This check compares original July temperatures and masks against the normalized values and coordinates in both cubes. The separate [pilot check](../../integration/real_tests/test_pilot.py) can be run as soon as the seven-day request is cached.

## Share a snapshot

FJ prepares one snapshot from the verified full run. The two float32 temperature arrays use about 2.56 MB before NetCDF metadata or compression. Measure the actual files before publishing.

1. Assign a version such as `milan-jja-2022-v1`. Copy the two cubes to an ignored staging directory, record sizes and checksums, and populate the [snapshot manifest](snapshot.example.json) with the producing commit, source and distribution licence.

   ```bash
   snapshot=data/snapshots/milan-jja-2022-v1
   mkdir -p "$snapshot"
   cp runs/milan/baseline.nc runs/milan/target.nc "$snapshot/"
   (cd "$snapshot" && sha256sum baseline.nc target.nc > SHA256SUMS)
   du -h "$snapshot/"*.nc
   tar -czf "$snapshot.tar.gz" -C "$snapshot" baseline.nc target.nc SHA256SUMS
   ```

2. Place the archive in the team's shared folder or attach it to a versioned GitHub Release for public distribution. Include source attribution to Copernicus Climate Change Service and ECMWF, DOI `10.24381/cds.e9c9c792`, licence and the Kelvin-to-Celsius transformation in the manifest or release notes. Commit the sanitized manifest. Keep original request downloads, credentials, and restricted links in private storage. [Copernicus dataset and licence](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics) · [GitHub Release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
3. Teammates extract the archive to their own ignored snapshot directory, run `sha256sum -c SHA256SUMS` there, and [start at Events](../../integration/WORKPLAN.md#integration-commands). Keep prior snapshots for reproducibility. Release a new version when the data changes.
