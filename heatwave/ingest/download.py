"""Retrieve the exact CDS inputs specified in the Milan heatwave proposal."""

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from heatwave.ingest.cache import (
    cache_entry,
    payload_kind,
    publish_entry,
    sha256,
    verify_entry,
)
from heatwave.ingest.requests import (
    BASELINE,
    DATASET,
    DATASET_DOI,
    build_request,
    request_plan,
)

# Keep the request and cache helpers available to the raw-data tests.
__all__ = [
    "DATASET", "DATASET_DOI", "build_request", "cache_entry", "main",
    "request_plan", "retrieve_entry", "sha256", "verify_entry",
]


def retrieve_entry(client, entry, request, *, pilot_file=None):
    """Publish one fetched payload or a validated local pilot together with its provenance."""
    if pilot_file is None and entry.exists():
        return verify_entry(entry, request)
    if pilot_file is not None and request != next(request_plan("pilot"))[1]:
        raise ValueError("local import requires the pilot request")
    entry.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".partial-", dir=entry.parent) as tempdir:
        staging = Path(tempdir) / "ready"
        staging.mkdir()
        received = staging / "response"
        if pilot_file is None:
            client.retrieve(DATASET, request).download(str(received))
        else:
            shutil.copyfile(pilot_file, received)
        payload = received.rename(staging / f"payload.{payload_kind(received)}")
        now = datetime.now(UTC).isoformat()
        if pilot_file is None:
            provenance = {"acquisition_method": "cds_api", "retrieved_at_utc": now}
        else:
            from heatwave.ingest.provider import validate_pilot

            validate_pilot(payload, request)
            provenance = {
                "acquisition_method": "user_supplied_local_pilot",
                "source_filename": pilot_file.name,
                "imported_at_utc": now,
            }
        return publish_entry(
            entry, request, payload, provenance, match_bytes=pilot_file is not None
        )


def main(argv=None):
    """Plan, fetch or verify UTC daily maxima for a selected CDS profile.

    The cache contains one payload and request manifest per partition. A
    verification or retrieval error returns a nonzero status. The accepted
    bounds and date ranges are documented in docs/geography.md.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile", choices=("pilot", "target", "baseline", "full"), default="pilot"
    )
    parser.add_argument("--year", type=int, help="one year in the baseline profile")
    parser.add_argument("--cache-dir", type=Path, default=Path("data/raw/cds"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print exact request JSON")
    mode.add_argument("--verify-only", action="store_true", help="verify local cache")
    mode.add_argument("--import-pilot", type=Path, metavar="FILE",
                      help="validate and cache a local CDS web-form pilot download")
    args = parser.parse_args(argv)
    if args.import_pilot is not None and args.profile != "pilot":
        parser.error("--import-pilot requires the pilot profile")
    if args.year is not None and (args.profile != "baseline" or args.year not in BASELINE):
        parser.error("--year requires the baseline profile and a year in 1991–2020")

    client = None
    for label, request in request_plan(args.profile, args.year):
        entry = cache_entry(args.cache_dir, label, request)
        if args.dry_run:
            print(json.dumps({"cache_dir": str(entry), "dataset": DATASET, "request": request}))
            continue
        try:
            if args.import_pilot is not None:
                payload = retrieve_entry(None, entry, request, pilot_file=args.import_pilot)
            elif entry.exists():
                payload = verify_entry(entry, request)
            elif args.verify_only:
                raise ValueError(f"no cached download at {entry}. Run without --verify-only first.")
            else:
                if client is None:
                    import cdsapi

                    client = cdsapi.Client()
                print(f"Requesting {label} from CDS", file=sys.stderr)
                payload = retrieve_entry(client, entry, request)
        except Exception as error:  # noqa: BLE001 — CDS also raises plain Exception.
            message = str(error)
            if message.startswith("Missing/incomplete configuration file:"):
                message += ". See https://cds.climate.copernicus.eu/how-to-api for CDS credentials."
            print(f"{label}: {message}", file=sys.stderr)
            return 1
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
