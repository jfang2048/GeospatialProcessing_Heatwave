"""Read-only access to local Milan run outputs and CDS inputs."""

import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from heatwave.ingest.cache import cache_entry, cached_payload, netcdf_path
from heatwave.ingest.requests import build_request


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def run_dir():
    return Path(os.getenv("HEATWAVE_RUN_DIR", ROOT / "runs" / "milan"))


@pytest.fixture(scope="session")
def load_output(run_dir):
    @lru_cache(maxsize=None)
    def load(name):
        path = run_dir / name
        if not path.is_file():
            pytest.fail(f"Missing real-case output {path}. Set HEATWAVE_RUN_DIR to the completed run.", pytrace=False)
        return xr.load_dataset(path)

    return load


@pytest.fixture(scope="session")
def load_raw_kelvin():
    cache = Path(os.getenv("HEATWAVE_CACHE_DIR", ROOT / "data" / "raw" / "cds"))

    def load(year, first_day, last_day):
        label, _ = build_request(year, 7, first_day, last_day)
        payload = cached_payload(cache_entry(cache, label))
        with netcdf_path(payload) as path, xr.open_dataset(path) as raw:
            temp = raw["t2m"].load()
        assert temp.attrs["units"].strip().lower() in {"k", "kelvin"}
        assert temp.latitude.attrs["units"] == "degrees_north"
        assert temp.longitude.attrs["units"] == "degrees_east"
        time_name, = [name for name in ("valid_time", "time") if name in temp.dims]
        temp = temp.rename({"latitude": "lat", "longitude": "lon", time_name: "time"})
        temp = temp.transpose("time", "lat", "lon").sortby(["time", "lat", "lon"])
        dates = np.arange(last_day - first_day + 1) + np.datetime64(f"{year}-07-{first_day:02}")
        np.testing.assert_array_equal(temp.time.values, dates)
        np.testing.assert_allclose(temp.lat, np.arange(451, 460) / 10, atol=5e-6, rtol=0)
        np.testing.assert_allclose(temp.lon, np.arange(86, 101) / 10, atol=5e-6, rtol=0)
        assert np.isfinite(temp.values).any(), "No observed temperature anywhere in this Milan request"
        assert not np.isinf(temp.values).any()
        return temp

    return load
