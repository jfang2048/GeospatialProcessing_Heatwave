"""Read-only access to local Milan run outputs and verified CDS requests."""

import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from heatwave.ingest import download
from heatwave.ingest.normalize import netcdf_path


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
        label, request = download.build_request(year, 7, first_day, last_day)
        entry = download.cache_entry(cache, label, request)
        if not entry.is_dir():
            pytest.fail(f"Missing real CDS request {entry}. Set HEATWAVE_CACHE_DIR to the provider cache.", pytrace=False)
        payload = download.verify_entry(entry, request)
        manifest = json.loads((entry / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["dataset_doi"] == "10.24381/cds.e9c9c792"
        assert request["daily_statistic"] == "daily_maximum"
        assert request["frequency"] == "1_hourly"
        assert request["time_zone"] == "utc+00:00"
        assert request["area"] == [45.9, 8.6, 45.1, 10.0]
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
