"""Offline coverage from a provider-shaped request cache to the two v1 files."""

from zipfile import ZipFile

import numpy as np
import pytest
import xarray as xr

from heatwave.ingest.normalize import normalize
from heatwave.ingest.provider import read_month
from heatwave.ingest.requests import build_request, request_plan


def provider_month(request):
    dates = np.array(
        [f"{request['year']}-{request['month']}-{day}" for day in request["day"]],
        dtype="datetime64[D]",
    )
    values = np.full((len(dates), 9, 15), 300, dtype="float32")
    values[:, 0, 0] = np.nan
    return xr.Dataset(
        {"t2m": (("valid_time", "latitude", "longitude"), values, {"units": "K"})},
        coords={
            "valid_time": dates,
            "latitude": ("latitude", np.arange(459, 450, -1) / 10, {"units": "degrees_north"}),
            "longitude": ("longitude", np.arange(86, 101) / 10, {"units": "degrees_east"}),
        },
    )


def test_full_cache_normalizes_both_cubes(tmp_path):
    cache = tmp_path / "cache"
    for label, request in request_plan("full"):
        entry = cache / label
        entry.mkdir(parents=True)
        payload = entry / "payload.nc"
        provider_month(request).to_netcdf(payload, engine="scipy")
        if label == "2022-05-01_to_31":
            zipped = entry / "payload.zip"
            with ZipFile(zipped, "w") as archive:
                archive.write(payload, "month.nc")
            payload.unlink()

    baseline = tmp_path / "baseline.nc"
    target = tmp_path / "target.nc"
    normalize(cache, baseline, target)
    for path, count in ((baseline, 4590), (target, 153)):
        with xr.open_dataset(path) as cube:
            assert cube.tx_c.dims == ("time", "lat", "lon")
            assert cube.tx_c.shape == (count, 9, 15)
            assert cube.tx_c.dtype == np.float32
            assert cube.tx_c.attrs["units"] == "degC"
            np.testing.assert_allclose(cube.lat, np.arange(451, 460) / 10)
            np.testing.assert_allclose(cube.tx_c[:, 0, 0], 26.85, atol=1e-5)
            assert np.isnan(cube.tx_c[:, -1, 0]).all()

    label, _ = next(request_plan("baseline"))
    (cache / label / "payload.nc").unlink()
    with pytest.raises(FileNotFoundError):
        normalize(cache, tmp_path / "retry-baseline.nc", tmp_path / "retry-target.nc")
    assert not (tmp_path / "retry-baseline.nc").exists()
    assert not (tmp_path / "retry-target.nc").exists()


def test_provider_month_rejects_wrong_dates_and_units():
    _, request = build_request(2022, 7, 15, 21)
    raw = provider_month(request)
    with pytest.raises(ValueError, match="requested date"):
        read_month(raw.isel(valid_time=slice(1, None)), request)
    raw.t2m.attrs["units"] = "degC"
    with pytest.raises(ValueError, match="expected Kelvin"):
        read_month(raw, request)
