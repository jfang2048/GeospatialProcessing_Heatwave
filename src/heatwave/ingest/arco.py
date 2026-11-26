"""Read ERA5-Land ARCO hourly temperatures and write the two Milan inputs."""

import argparse
import os
from pathlib import Path

import numpy as np
import xarray as xr

from heatwave._handoff import publish_outputs
from heatwave.ingest.provider import temperature_cube
from heatwave.ingest.requests import AREA, BASELINE, TARGET

ARCO_URL = (
    "https://arco.datastores.ecmwf.int/cadl-arco-geo-007/arco/"
    "reanalysis_era5_land/sfc-2m-temperature/geoChunked.zarr"
)
ARCO_SOURCE = "ERA5-Land hourly ARCO, daily maximum of 24 UTC hours"
ARCO_DOI = "10.24381/ee82e357"


def cds_token():
    token = os.environ.get("CDSAPI_KEY")
    if token:
        return token
    config = Path.home() / ".cdsapirc"
    if config.is_file():
        for line in config.read_text(encoding="utf-8").splitlines():
            name, _, value = line.partition(":")
            if name.strip() == "key" and value.strip():
                return value.strip()
    raise ValueError("Set the CDS key in ~/.cdsapirc or CDSAPI_KEY.")


def season_hours(year):
    return np.arange(f"{year}-05-01", f"{year}-10-01", dtype="datetime64[h]")


def daily_maximum(hourly):
    """Aggregate complete UTC days and preserve masked cells."""
    times = hourly.time.values
    if (
        not len(times) or len(times) % 24
        or times[0] != times[0].astype("datetime64[D]")
        or not np.all(np.diff(times) == np.timedelta64(1, "h"))
    ):
        raise ValueError("Expected consecutive hourly UTC records in complete days.")
    return hourly.coarsen(time=24).max().assign_coords(time=times[::24])


def read_hourly(hourly, hours):
    north, west, south, east = AREA
    lat = np.arange(round(10 * south), round(10 * north) + 1) / 10
    lon = np.arange(round(10 * west), round(10 * east) + 1) / 10
    return (
        hourly.sel(time=hours)
        .sel(latitude=lat, longitude=lon, method="nearest", tolerance=5e-6)
        .transpose("time", "latitude", "longitude")
        .load()
    )


def run(run_dir, token):
    with publish_outputs((run_dir / "baseline.nc", run_dir / "target.nc")) as outputs:
        with xr.open_zarr(
            ARCO_URL, consolidated=True, chunks=None,
            storage_options={"headers": {"Authorization": f"Bearer {token}"}},
        ) as data:
            # Select all requested hours together so each storage chunk is fetched once.
            hours = np.concatenate([season_hours(year) for year in (*BASELINE, TARGET)])
            print("Reading the Milan grid from ERA5-Land ARCO…", flush=True)
            hourly = read_hourly(data.t2m, hours)
        if hourly.attrs.get("units", "").lower() not in {"k", "kelvin"}:
            raise ValueError("Expected Kelvin 2 m temperatures from ERA5-Land ARCO.")
        if np.isinf(hourly.values).any():
            raise ValueError("ERA5-Land ARCO returned infinite temperatures.")
        for years, output in zip((BASELINE, (TARGET,)), outputs, strict=True):
            seasons = [
                daily_maximum(hourly.sel(time=slice(f"{year}-05-01", f"{year}-09-30")))
                for year in years
            ]
            daily = xr.concat(seasons, dim="time")
            temperature_cube(
                daily.time.values, daily.latitude.values, daily.longitude.values,
                (daily.values.astype("float64") - 273.15).astype("float32"),
                source=ARCO_SOURCE, doi=ARCO_DOI,
            ).to_netcdf(output)
    print(run_dir / "baseline.nc")
    print(run_dir / "target.nc")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=Path("data/processed/milan"))
    args = parser.parse_args(argv)
    token = ""
    try:
        token = cds_token()
        run(args.run_dir, token)
    except Exception as error:  # noqa: BLE001 — redact the key from HTTP errors at the CLI boundary.
        message = str(error)
        parser.exit(1, f"ARCO: {message.replace(token, '[redacted]') if token else message}\n")


if __name__ == "__main__":
    main()
