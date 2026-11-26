"""Check ARCO's UTC day grouping without making a network request."""

import numpy as np
import pytest
import xarray as xr

from heatwave.ingest.arco import daily_maximum, season_hours


def test_daily_maximum_groups_utc_days_and_keeps_missing_cells():
    hours = season_hours(2022)[:48]
    values = np.column_stack((np.arange(48, dtype=float), np.full(48, np.nan)))
    hourly = xr.DataArray(values, coords={"time": hours}, dims=("time", "cell"))

    daily = daily_maximum(hourly)

    np.testing.assert_array_equal(daily.time, hours[::24])
    np.testing.assert_array_equal(daily[:, 0], [23, 47])
    assert np.isnan(daily[:, 1]).all()


def test_daily_maximum_rejects_gap_in_hours():
    hours = season_hours(2022)[:24] + np.arange(24) // 4
    hourly = xr.DataArray(np.ones(24), coords={"time": hours}, dims="time")
    with pytest.raises(ValueError, match="consecutive hourly UTC"):
        daily_maximum(hourly)
