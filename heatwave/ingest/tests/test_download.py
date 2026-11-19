"""Download tests exercise caching without provider access."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from heatwave.ingest import download


# A signature with dummy content exercises transport detection only.
NETCDF_STUB = b"CDF\x02transport fixture"


class FakeCDS:
    def __init__(self, content=NETCDF_STUB, zipped=False):
        self.calls = []
        self.content = content
        self.zipped = zipped

    def retrieve(self, dataset, request):
        self.calls.append((dataset, request))
        return self

    def download(self, destination):
        if self.zipped:
            with ZipFile(destination, "w") as archive:
                archive.writestr("data.nc", self.content)
        else:
            Path(destination).write_bytes(self.content)


class DownloadTests(unittest.TestCase):
    def test_plan_has_valid_months_and_separate_pilot(self):
        (pilot_label, pilot), = download.request_plan("pilot")
        self.assertEqual(pilot["day"], ["15", "16", "17", "18", "19", "20", "21"])
        self.assertEqual(pilot["area"], [45.9, 8.6, 45.1, 10.0])
        self.assertEqual(pilot["time_zone"], "utc+00:00")
        self.assertEqual(len(list(download.request_plan("full"))), 155)
        requests = list(download.request_plan("baseline", 1991))
        self.assertEqual(len(requests), 5)
        self.assertEqual([len(request["day"]) for _, request in requests], [31, 30, 31, 31, 30])
        self.assertEqual(len({label for label, _ in requests}), 5)
        self.assertEqual(pilot_label, "2022-07-15_to_21")

    def test_direct_and_zipped_downloads_are_cached_and_verified(self):
        for zipped in (False, True):
            with self.subTest(zipped=zipped), TemporaryDirectory() as temp:
                (label, request), = download.request_plan("pilot")
                entry = download.cache_entry(Path(temp), label, request)
                provider = FakeCDS(zipped=zipped)
                payload = download.retrieve_entry(provider, entry, request)
                self.assertEqual(payload.suffix, ".zip" if zipped else ".nc")
                self.assertEqual(download.verify_entry(entry, request), payload)
                self.assertEqual(download.retrieve_entry(provider, entry, request), payload)
                self.assertEqual(provider.calls, [(download.DATASET, request)])
                metadata = json.loads((entry / "manifest.json").read_text())
                self.assertEqual(metadata["dataset_doi"], download.DATASET_DOI)
                payload.write_bytes(b"x" * metadata["bytes"])
                with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
                    download.verify_entry(entry, request)

    def test_failed_download_leaves_no_cache_and_can_retry(self):
        for zipped in (False, True):
            with self.subTest(zipped=zipped), TemporaryDirectory() as temp:
                (label, request), = download.request_plan("pilot")
                root = Path(temp)
                entry = download.cache_entry(root, label, request)
                with self.assertRaisesRegex(ValueError, "NetCDF"):
                    download.retrieve_entry(FakeCDS(b"provider error", zipped), entry, request)
                self.assertEqual(list(root.iterdir()), [])
                self.assertEqual(download.retrieve_entry(FakeCDS(), entry, request).name, "payload.nc")
