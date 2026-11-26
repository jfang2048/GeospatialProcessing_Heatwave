"""Download daily ERA5-Land maximum temperatures to the local CDS cache."""

import argparse
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from heatwave.ingest.cache import cache_entry, cached_payload, payload_suffix
from heatwave.ingest.requests import BASELINE, DATASET, request_plan


def retrieve_entry(client, entry, request, *, pilot_file=None):
    """Download or import one file, then publish its cache directory."""
    if entry.exists():
        if pilot_file is not None:
            raise FileExistsError(f"Pilot already exists at {entry}. Use --cache-dir to import another.")
        return cached_payload(entry)

    entry.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".partial-", dir=entry.parent) as temp:
        staging = Path(temp) / "ready"
        staging.mkdir()
        received = staging / "response"
        if pilot_file is None:
            client.retrieve(DATASET, request).download(str(received))
        else:
            shutil.copyfile(pilot_file, received)
        payload = received.rename(staging / f"payload{payload_suffix(received)}")

        if pilot_file is not None:
            from heatwave.ingest.provider import validate_pilot

            validate_pilot(payload, request)
        staging.rename(entry)
    return entry / payload.name


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("pilot", "target", "baseline", "full"), default="pilot")
    parser.add_argument("--year", type=int, help="one year in the baseline profile")
    parser.add_argument("--cache-dir", type=Path, default=Path("data/raw/cds"))
    parser.add_argument("--import-pilot", type=Path, metavar="FILE", help="import a CDS web download")
    args = parser.parse_args(argv)
    if args.import_pilot is not None and args.profile != "pilot":
        parser.error("--import-pilot requires the pilot profile")
    if args.year is not None and (args.profile != "baseline" or args.year not in BASELINE):
        parser.error("--year requires the baseline profile and a year in 1991–2020")

    client = None
    for label, request in request_plan(args.profile, args.year):
        entry = cache_entry(args.cache_dir, label)
        try:
            if not entry.exists() and args.import_pilot is None:
                if client is None:
                    import cdsapi

                    client = cdsapi.Client()
                print(f"Requesting {label} from CDS", file=sys.stderr)
            print(retrieve_entry(client, entry, request, pilot_file=args.import_pilot))
        except Exception as error:  # noqa: BLE001 — CDS also raises plain Exception.
            print(f"{label}: {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
