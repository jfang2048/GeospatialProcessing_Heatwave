"""Retrieve the exact CDS inputs specified in the Milan heatwave proposal."""

import argparse
import calendar
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import zipfile


DATASET = "derived-era5-land-daily-statistics"
DATASET_DOI = "10.24381/cds.e9c9c792"
AREA = (45.9, 8.6, 45.1, 10.0)  # North, west, south, east.
BASELINE = range(1991, 2021)
TARGET = 2022
NETCDF_SIGNATURES = (b"CDF\x01", b"CDF\x02", b"CDF\x05", b"\x89HDF\r\n\x1a\n")


def build_request(year, month, first_day, last_day):
    """Build one valid calendar partition and its descriptive name."""
    request = {
        "variable": ["2m_temperature"],
        "year": str(year),
        "month": [f"{month:02d}"],
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


def cache_entry(cache_dir, label, request):
    encoded = json.dumps([DATASET, request], sort_keys=True).encode("utf-8")
    version = hashlib.sha256(encoded).hexdigest()[:12]
    return cache_dir / f"{label}_{version}"


def payload_kind(path):
    with path.open("rb") as payload:
        signature = payload.read(8)
    if signature.startswith(NETCDF_SIGNATURES):
        return "nc"
    if not zipfile.is_zipfile(path):
        raise ValueError("CDS response is neither NetCDF nor a readable ZIP")
    with zipfile.ZipFile(path) as archive:
        netcdf_members = [
            name for name in archive.namelist() if name.lower().endswith(".nc")
        ]
        if not netcdf_members:
            raise ValueError("CDS ZIP has no .nc member")
        for name in netcdf_members:
            with archive.open(name) as member:
                if not member.read(8).startswith(NETCDF_SIGNATURES):
                    raise ValueError(f"ZIP member is not NetCDF: {name}")
        damaged_member = archive.testzip()
        if damaged_member is not None:
            raise ValueError(f"ZIP integrity check failed for {damaged_member}")
    return "zip"


def sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def verify_entry(entry, request):
    """Accept a cache hit only when both the request and payload match."""
    try:
        manifest = json.loads((entry / "manifest.json").read_text(encoding="utf-8"))
        if manifest["dataset"] != DATASET or manifest["request"] != request:
            raise ValueError("cached request differs")
        filename = manifest["payload"]
        if filename not in {"payload.zip", "payload.nc"}:
            raise ValueError("invalid payload filename")
        payload = entry / filename
        if payload.stat().st_size != manifest["bytes"]:
            raise ValueError("payload byte count differs")
        if sha256(payload) != manifest["sha256"]:
            raise ValueError("payload SHA-256 differs")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(f"{entry}: {error}") from error
    return payload


def retrieve_entry(client, entry, request):
    """Publish a payload and its metadata together after successful retrieval."""
    if entry.exists():
        return verify_entry(entry, request)
    entry.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".partial-", dir=entry.parent) as tempdir:
        staging = Path(tempdir) / "ready"
        staging.mkdir()
        received = staging / "response"
        client.retrieve(DATASET, request).download(str(received))
        payload = received.rename(staging / f"payload.{payload_kind(received)}")
        manifest = {
            "dataset": DATASET,
            "dataset_doi": DATASET_DOI,
            "request": request,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "payload": payload.name,
            "bytes": payload.stat().st_size,
            "sha256": sha256(payload),
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        try:
            staging.rename(entry)
        except OSError:
            # Another successful run may have published this same request first.
            if not (entry / "manifest.json").is_file():
                raise
        return verify_entry(entry, request)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile", choices=("pilot", "target", "baseline", "full"), default="pilot"
    )
    parser.add_argument("--year", type=int, help="one year in the baseline profile")
    parser.add_argument("--cache-dir", type=Path, default=Path("data/raw/cds"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print exact request JSON")
    mode.add_argument("--verify-only", action="store_true", help="verify local cache")
    args = parser.parse_args(argv)
    if args.year is not None and (args.profile != "baseline" or args.year not in BASELINE):
        parser.error("--year requires the baseline profile and a year in 1991–2020")

    client = None
    for label, request in request_plan(args.profile, args.year):
        entry = cache_entry(args.cache_dir, label, request)
        if args.dry_run:
            print(json.dumps({"cache_dir": str(entry), "dataset": DATASET, "request": request}))
            continue
        try:
            if args.verify_only or entry.exists():
                payload = verify_entry(entry, request)
            else:
                if client is None:
                    import cdsapi

                    client = cdsapi.Client()
                print(f"Requesting {label} from CDS", file=sys.stderr)
                payload = retrieve_entry(client, entry, request)
        except Exception as error:
            print(f"{label}: {error}", file=sys.stderr)
            return 1
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
