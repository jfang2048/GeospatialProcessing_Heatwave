"""Normalize the verified CDS monthly cache into two v1 temperature cubes."""

import argparse
from contextlib import contextmanager
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
import xarray as xr

from heatwave._handoff import publish_outputs, validate_grid
from heatwave.ingest import download


@contextmanager
def netcdf_path(payload):
    """Expose one NetCDF member to xarray, including NetCDF4/HDF5 ZIP members."""
    if payload.suffix == ".nc":
        yield payload
        return
    with ZipFile(payload) as archive, TemporaryDirectory() as scratch:
        members = [info for info in archive.infolist() if info.filename.lower().endswith(".nc")]
        if len(members) != 1:
            raise ValueError(f"expected one NetCDF member in ZIP, found {len(members)}")
        path = Path(scratch) / "month.nc"
        with archive.open(members[0]) as source, path.open("wb") as dest:
            shutil.copyfileobj(source, dest)
        yield path


def check_axis(coord, name, units, first, last):
    if coord.dims != (name,) or coord.attrs.get("units") != units:
        raise ValueError(f"{name} must be one-dimensional with units {units}")
    expected = np.arange(round(10 * first), round(10 * last) + 1) / 10
    # Allow representational error of float32 provider coordinates. Return the
    # provider's actual centres so mismatches across months cannot be rounded away.
    if coord.size != expected.size or not np.allclose(coord.values, expected, rtol=0, atol=5e-6):
        raise ValueError(f"{name} differs from the requested 0.1-degree Milan grid")


def read_month(raw, request):
    """Validate one requested UTC month and convert CF-decoded Kelvin to float32 Celsius."""
    if "t2m" not in raw.data_vars:
        raise ValueError("missing provider temperature variable t2m")
    temp = raw["t2m"]
    if temp.attrs.get("units", "").strip().lower() not in {"k", "kelvin"}:
        raise ValueError(f"expected Kelvin for t2m, got {temp.attrs.get('units')!r}")
    times = [name for name in ("valid_time", "time") if name in temp.dims]
    if len(times) != 1 or set(temp.dims) != {times[0], "latitude", "longitude"}:
        raise ValueError(f"unexpected temperature dimensions {temp.dims}")
    time_name = times[0]
    time = raw.coords[time_name]
    if time.dims != (time_name,) or time.dtype.kind != "M":
        raise ValueError("expected a CF-decodable Gregorian time coordinate")
    temp = temp.transpose(time_name, "latitude", "longitude").sortby(
        [time_name, "latitude", "longitude"]
    )
    dates = temp.coords[time_name].values
    expected = np.array([
        f"{request['year']}-{request['month']}-{day}" for day in request["day"]
    ], dtype="datetime64[D]")
    if not np.array_equal(dates, expected):
        raise ValueError("expected exactly one UTC midnight record on each requested date")

    north, west, south, east = request["area"]
    lat, lon = temp.coords["latitude"], temp.coords["longitude"]
    check_axis(lat, "latitude", "degrees_north", south, north)
    check_axis(lon, "longitude", "degrees_east", west, east)
    if temp.dtype.kind not in "iuf":
        raise ValueError("t2m must contain numeric temperatures")
    with np.errstate(over="ignore"):
        tx_c = (temp.values.astype("float64") - 273.15).astype("float32")
    if np.isinf(tx_c).any():
        raise ValueError("t2m contains infinite or out-of-range temperatures")
    return dates, lat.values, lon.values, tx_c


def normalize(cache_dir, baseline_out, target_out):
    """Publish baseline and target cubes from the complete cache specified in contracts/v1.md.

    Reject unverified, incomplete or misaligned partitions before publishing either cube.
    Both outputs preserve the WGS 84 grid, UTC dates and provider mask.
    """
    cache = cache_dir.resolve()
    for path in (baseline_out, target_out):
        if path.resolve().is_relative_to(cache):
            raise ValueError(f"output must be outside the provider cache: {path}")
    grid = None
    with publish_outputs((baseline_out, target_out)) as (baseline_stage, target_stage):
        for profile, output in (("target", target_stage), ("baseline", baseline_stage)):
            all_dates, all_values = [], []
            for label, request in download.request_plan(profile):
                entry = download.cache_entry(cache, label, request)
                payload = download.verify_entry(entry, request)
                try:
                    with netcdf_path(payload) as path, xr.open_dataset(path) as raw:
                        dates, lat, lon, tx_c = read_month(raw, request)
                    if grid is None:
                        grid = lat, lon
                    elif not np.array_equal(lat, grid[0]) or not np.array_equal(lon, grid[1]):
                        raise ValueError("latitude or longitude differs from other partitions")
                except Exception as error:
                    raise ValueError(f"{payload}: {error}") from error
                all_dates.append(dates)
                all_values.append(tx_c)
            dates = np.concatenate(all_dates)
            first_day, last_day = dates[[0, -1]].astype("datetime64[D]")
            cube = xr.Dataset(
                data_vars={"tx_c": (("time", "lat", "lon"), np.concatenate(all_values), {"units": "degC"})},
                coords={
                    "time": dates,
                    "lat": ("lat", grid[0], {"units": "degrees_north"}),
                    "lon": ("lon", grid[1], {"units": "degrees_east"}),
                },
                attrs={
                    "contract_version": "1",
                    "source": download.DATASET,
                    "source_doi": download.DATASET_DOI,
                    "requested_bounds": ", ".join(map(str, download.AREA)),
                    "requested_period": f"{first_day} to {last_day}, May-September",
                    "day_timezone": "UTC",
                },
            )
            validate_grid(cube)
            cube.to_netcdf(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--baseline-out", type=Path, required=True)
    parser.add_argument("--target-out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        normalize(args.cache_dir, args.baseline_out, args.target_out)
    except Exception as error:
        print(f"Normalization failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
