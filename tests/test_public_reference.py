import json
import tempfile
import unittest
from pathlib import Path

from scripts.update_public_reference import load_snapshot, normalize_reference, write_snapshot

RAW = b'[{"data":"01/01/2025","valor":"5.25"}]'


class TestPublicReference(unittest.TestCase):
    def test_percent_preserves_external_definition(self):
        row = normalize_reference(RAW)[0]
        self.assertEqual((row["value_percent"], row["period"]), ("5.25", "2025-01"))
        self.assertEqual((row["threshold_operator"], row["threshold_days"], row["origin_kind"]), (">", 90, "publica"))

    def test_invalid_public_data_rejected(self):
        for raw in (b'<html>Error</html>', b'[]', b'[{"data":"01/01/2025","valor":"NaN"}]',
                    b'[{"data":"01/01/2025","valor":"101"}]',
                    b'[{"data":"01/01/2025","valor":true}]',
                    b'[{"data":"01/01/2025","valor":"5"},{"data":"01/01/2025","valor":"6"}]'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                normalize_reference(raw)

    def test_failed_update_preserves_snapshot_and_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "reference.json"
            write_snapshot(RAW, target, {"fetched_at": "2026-11-04T00:00:00+00:00"})
            original = target.read_bytes()
            with self.assertRaises(ValueError):
                write_snapshot(b'bad', target, {})
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(load_snapshot(target)["rows"][0]["value_percent"], "5.25")
            bad = json.loads(original)
            bad["rows"][0]["value_percent"] = "99"
            target.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_snapshot(target)

    def test_missing_file_is_not_fake_data(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(FileNotFoundError):
            load_snapshot(Path(tmp) / "absent.json")


if __name__ == "__main__":
    unittest.main()
