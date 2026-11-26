"""Exercise the Events command using the hand-labelled synthetic grid."""

from pathlib import Path

import xarray as xr

from heatwave.events.detect import run

EXAMPLES = Path(__file__).resolve().parents[2] / "data/examples/synthetic"


def test_events_matches_hand_labelled_fixture(tmp_path):
    result = tmp_path / "events.nc"
    run(EXAMPLES / "baseline_fixture.nc", EXAMPLES / "target_fixture.nc", result)

    with xr.open_dataset(result) as actual, xr.open_dataset(EXAMPLES / "events_fixture.nc") as expected:
        for name in ("tx_c", "p90_c", "excess_c", "heatwave_flag"):
            xr.testing.assert_allclose(actual[name], expected[name])
