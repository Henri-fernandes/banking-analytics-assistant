import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from financeiro.data import build_database, position_at

FIXTURE = Path(__file__).resolve().parents[1] / "data/synthetic/fixtures.json"


class TestData(unittest.TestCase):
    def setUp(self):
        self.contract = {"id": "S:C1", "originated_at": "2024-09-01", "principal_centavos": 100000}
        self.installments = [{"id": "S:I1", "contract_id": "S:C1", "due_at": "2024-11-02",
                              "principal_centavos": 100000, "interest_centavos": 1000}]
        self.allocations = [{"installment_id": "S:I1", "effective_at": "2025-01-30",
                             "principal_centavos": 40000, "interest_centavos": 1000}]

    def test_partial_and_future_payment_preserve_history(self):
        before = position_at(self.contract, self.installments, self.allocations, "2025-01-31")
        self.assertEqual(before["principal_centavos"], 60000)
        self.assertEqual(before["days_overdue"], 90)
        self.allocations.append({"installment_id": "S:I1", "effective_at": "2025-02-01",
                                 "principal_centavos": 60000, "interest_centavos": 0})
        self.assertEqual(position_at(self.contract, self.installments, self.allocations, "2025-01-31"), before)
        after = position_at(self.contract, self.installments, self.allocations, "2025-02-28")
        self.assertEqual((after["principal_centavos"], after["days_overdue"]), (0, 0))

    def test_unpaid_interest_preserves_due_date(self):
        self.allocations[0].update(principal_centavos=100000, interest_centavos=0)
        result = position_at(self.contract, self.installments, self.allocations, "2025-01-31")
        self.assertEqual((result["principal_centavos"], result["days_overdue"]), (0, 90))

    def test_due_today_is_zero(self):
        self.assertEqual(position_at(self.contract, self.installments, [], "2024-11-02")["days_overdue"], 0)

    def test_multiple_installments_do_not_duplicate_principal(self):
        self.installments[0]["principal_centavos"] = 50000
        self.installments.append({"id": "S:I2", "contract_id": "S:C1", "due_at": "2025-02-28",
                                  "principal_centavos": 50000, "interest_centavos": 0})
        result = position_at(self.contract, self.installments, self.allocations, "2025-01-31")
        self.assertEqual((result["principal_centavos"], result["days_overdue"]), (60000, 90))

    def test_negative_boolean_and_excess_payment_rejected(self):
        for value in (-1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                position_at(dict(self.contract, principal_centavos=value), self.installments, [], "2025-01-31")
        self.allocations[0]["principal_centavos"] = 100001
        with self.assertRaises(ValueError):
            position_at(self.contract, self.installments, self.allocations, "2025-01-31")

    def test_missing_amount_is_not_zero(self):
        result = position_at(dict(self.contract, principal_centavos=None), self.installments, [], "2025-01-31")
        self.assertIsNone(result["principal_centavos"])
        self.assertIn("principal", result["excluded_reason"])

    def test_fixture_is_read_only_and_has_exact_boundary_positions(self):
        with build_database(FIXTURE, "fronteira") as conn:
            rows = conn.execute("SELECT principal_centavos, days_overdue FROM positions ORDER BY contract_id").fetchall()
            self.assertEqual([tuple(r) for r in rows], [(100000, 89), (200000, 90), (300000, 91), (400000, 120)])
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("DELETE FROM positions")
            self.assertEqual(conn.execute("SELECT count(*) FROM coverage").fetchone()[0], 1)

    def test_duplicate_or_orphan_rejected(self):
        source = json.loads(FIXTURE.read_text(encoding="utf-8"))
        for kind in ("duplicate", "orphan", "product", "duplicate_reference"):
            raw = copy.deepcopy(source)
            data = raw["scenarios"]["fronteira"]
            if kind == "duplicate":
                data["contracts"].append(copy.deepcopy(data["contracts"][0]))
            elif kind == "orphan":
                data["installments"][0]["contract_id"] = "MISSING"
            elif kind == "product":
                data["contracts"][0]["person"] = "PJ"
            else:
                data["references"].append(data["references"][0])
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "bad.json"
                path.write_text(json.dumps(raw), encoding="utf-8")
                with self.assertRaises(ValueError):
                    build_database(path, "fronteira")


if __name__ == "__main__":
    unittest.main()
