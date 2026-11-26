"""Decode and validate ERA5-Land UTC daily maximum temperatures."""

import numpy as np
import xarray as xr

from heatwave.ingest.cache import netcdf_path


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


def load_month(payload, request):
    """Read a cached provider file and close it before returning its arrays."""
    with netcdf_path(payload) as path, xr.open_dataset(path) as raw:
        return read_month(raw, request)


def validate_pilot(payload, request):
    _, _, _, temperatures = load_month(payload, request)
    if not np.isfinite(temperatures).any():
        raise ValueError("pilot contains no observed temperature")
