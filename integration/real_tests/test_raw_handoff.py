"""Check the Kelvin conversion and mask against two original monthly CDS payloads."""

import numpy as np
import pytest


@pytest.mark.parametrize(("year", "name"), [(1991, "baseline.nc"), (2022, "target.nc")])
def test_month_matches_cds(year, name, load_raw_kelvin, load_output):
    raw = load_raw_kelvin(year, 1, 31)
    normalized = load_output(name).tx_c.sel(time=raw.time)
    assert normalized.dims == ("time", "lat", "lon")
    np.testing.assert_array_equal(normalized.lat, raw.lat)
    np.testing.assert_array_equal(normalized.lon, raw.lon)
    np.testing.assert_allclose(normalized, raw.values.astype("float64") - 273.15,
                               rtol=0, atol=1e-5, equal_nan=True)
