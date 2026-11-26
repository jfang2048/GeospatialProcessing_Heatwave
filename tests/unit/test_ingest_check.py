"""Saved input checks should catch mistakes before the Events handoff."""

import numpy as np
import pytest

from heatwave.ingest.check import milan_cube
from heatwave.ingest.provider import temperature_cube


def test_saved_cube_with_a_missing_date_is_rejected(tmp_path):
    dates = np.arange("2022-05-01", "2022-10-01", dtype="datetime64[D]")
    lat, lon = np.arange(451, 460) / 10, np.arange(86, 101) / 10
    cube = temperature_cube(
        dates, lat, lon, np.full((153, 9, 15), 24.0, dtype="float32"),
        source="Synthetic test", doi="synthetic",
    )
    path = tmp_path / "target.nc"
    cube.to_netcdf(path)
    assert milan_cube(path, (2022,)).sizes["time"] == 153

    cube.isel(time=slice(1, None)).to_netcdf(path)
    with pytest.raises(ValueError, match="expected all May–September dates"):
        milan_cube(path, (2022,))
