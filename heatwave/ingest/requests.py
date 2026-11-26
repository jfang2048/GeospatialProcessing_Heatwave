"""Plan CDS requests for the pilot and Milan study."""

import calendar

DATASET = "derived-era5-land-daily-statistics"
DATASET_DOI = "10.24381/cds.e9c9c792"
AREA = (45.9, 8.6, 45.1, 10.0)  # North, west, south, east.
BASELINE = range(1991, 2021)
TARGET = 2022


def build_request(year, month, first_day, last_day):
    """Describe an inclusive UTC date range in one month on the Milan CDS grid."""
    request = {
        "variable": ["2m_temperature"],
        "year": str(year),
        "month": f"{month:02d}",
        "day": [f"{day:02d}" for day in range(first_day, last_day + 1)],
        "daily_statistic": "daily_maximum",
        "time_zone": "utc+00:00",
        "frequency": "1_hourly",
        "area": list(AREA),
    }
    label = f"{year}-{month:02d}-{first_day:02d}_to_{last_day:02d}"
    return label, request


def request_plan(profile, year=None):
    """Plan the pilot or partition the proposed study by calendar month."""
    if profile == "pilot":
        yield build_request(TARGET, 7, 15, 21)
        return
    years = {
        "baseline": BASELINE,
        "target": (TARGET,),
        "full": (*BASELINE, TARGET),
    }[profile]
    for selected_year in (years if year is None else (year,)):
        for month in range(5, 10):
            last_day = calendar.monthrange(selected_year, month)[1]
            yield build_request(selected_year, month, 1, last_day)
