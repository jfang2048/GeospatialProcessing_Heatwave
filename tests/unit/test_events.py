"""Exercise Events using synthetic grids with known thresholds and flags."""

from pathlib import Path

import numpy as np
import xarray as xr

from heatwave.events.detect import detect_events, run

EXAMPLES = Path(__file__).resolve().parents[2] / "data/examples/synthetic"


def test_events_matches_hand_labelled_fixture(tmp_path):
    result = tmp_path / "events.nc"
    run(EXAMPLES / "baseline_fixture.nc", EXAMPLES / "target_fixture.nc", result)

    with xr.open_dataset(result) as actual, xr.open_dataset(EXAMPLES / "events_fixture.nc") as expected:
        for name in ("tx_c", "p90_c", "excess_c", "heatwave_flag"):
            xr.testing.assert_allclose(actual[name], expected[name])


def test_events_uses_the_full_reference_window_and_requires_405_samples():
    season_starts = np.array([f"{year}-05-01" for year in range(1991, 2021)], dtype="datetime64[D]")
    season_days = np.arange(153, dtype="timedelta64[D]")
    baseline_dates = (season_starts[:, None] + season_days).ravel()
    month_days = np.array([day[5:] for day in np.datetime_as_string(baseline_dates, unit="D")])
    june_first_window = (month_days >= "05-25") & (month_days <= "06-08")
    baseline_tx = np.full((baseline_dates.size, 2, 2), 20.0, dtype=np.float32)

    # Adjacent out-of-window days would raise P90 if included.
    baseline_tx[(month_days == "05-24") | (month_days == "06-09")] = 50.0
    # Of the 450 samples, 45 are missing, 364 equal 20°C and 41 equal 30°C.
    window_samples = np.repeat([np.nan, 20.0, 30.0], [45, 364, 41])
    baseline_tx[june_first_window, 0, :] = window_samples[:, None]
    # Remove one more sample from the second cell, leaving 404 valid values.
    baseline_tx[np.flatnonzero(june_first_window)[45], 0, 1] = np.nan

    dims = ("time", "lat", "lon")
    grid = {"lat": [45.4, 45.5], "lon": [9.1, 9.2]}
    baseline = xr.Dataset({"tx_c": (dims, baseline_tx)}, coords={"time": baseline_dates, **grid})
    target_dates = np.arange("2022-06-01", "2022-06-04", dtype="datetime64[D]")
    target_tx = np.full((target_dates.size, 2, 2), 45.0, dtype=np.float32)
    target = xr.Dataset({"tx_c": (dims, target_tx)}, coords={"time": target_dates, **grid})

    first_days = detect_events(baseline, target).sel(time=slice("2022-06-01", "2022-06-03"))
    row = first_days.isel(lat=0)
    june_first = row.isel(time=0)

    # The zero-based linear P90 rank is 0.9 * (405 - 1) = 363.6.
    np.testing.assert_allclose(june_first.p90_c.values, [26.0, np.nan])
    np.testing.assert_allclose(june_first.excess_c.values, [19.0, np.nan])
    np.testing.assert_array_equal(row.heatwave_flag.values, [[1, -1], [1, 0], [1, 0]])
