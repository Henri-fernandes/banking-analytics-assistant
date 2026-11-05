import copy
import json
import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from financeiro.analytics import Intent, run_query
from financeiro.data import build_database
from tests.test_data import FIXTURE


class TestAnalytics(unittest.TestCase):
    def query(self, scenario="fronteira", action="evolucao", start="2025-01-31", end="2025-01-31", **filters):
        conn = build_database(FIXTURE, scenario)
        self.addCleanup(conn.close)
        return run_query(conn, Intent(action, start, end, filters.get("branch"), filters.get("person"),
                                      filters.get("threshold", 90), scenario))

    def test_boundary_total_and_balance(self):
        row = self.query()["rows"][0]
        self.assertEqual((row["denominator_centavos"], row["numerator_centavos"], row["rate_percent"]),
                         (1000000, 900000, "90"))
        result = self.query(action="saldo")
        self.assertEqual(sum(r["principal_centavos"] for r in result["rows"]), 1000000)
        self.assertEqual(result["rule_evidence"]["section"], "saldo")
        self.assertEqual(result["rule_evidence"]["version"], result["rule_version"])
        self.assertTrue(result["rule_evidence"]["text"])

    def test_every_over_includes_its_boundary(self):
        for threshold in (1, 15, 30, 60, 90, 180):
            raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
            data = raw["scenarios"]["fronteira"]
            for i, item in enumerate(data["installments"]):
                data["contracts"][i]["originated_at"] = "2020-01-01"
                item["due_at"] = (date(2025, 1, 31) - timedelta(days=threshold + (-1, 0, 1, 1)[i])).isoformat()
            with self.subTest(threshold=threshold), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "test.json"
                path.write_text(json.dumps(raw), encoding="utf-8")
                conn = build_database(path, "fronteira")
                self.addCleanup(conn.close)
                intent = Intent("evolucao", "2025-01-31", "2025-01-31", None, None, threshold, "fronteira")
                self.assertEqual(run_query(conn, intent)["rows"][0]["numerator_centavos"], 900000)
        self.assertEqual(self.query(threshold=0)["rows"][0]["rate_percent"], "100")

    def test_variation_reconciles(self):
        rows = self.query("variacao", "evolucao", end="2025-02-28")["rows"]
        self.assertEqual([r["rate_percent"] for r in rows], ["30", "40"])
        result = self.query("variacao", "contribuicao", end="2025-02-28")
        self.assertEqual(sorted(Decimal(r["contribution_pp"]) for r in result["rows"]), [Decimal(5), Decimal(5)])
        self.assertEqual(result["variation_pp"], "10")

    def test_mob_observed_only(self):
        result = self.query("safras", "safras", end="2025-02-28")
        self.assertEqual([(r["cohort"], r["mob"]) for r in result["rows"]],
                         [("2025-01", 0), ("2025-01", 1), ("2025-02", 0)])

    def test_absent_period_different_from_empty_population(self):
        self.assertEqual(self.query(branch="F02")["status"], "populacao_vazia")
        self.assertEqual(self.query(end="2025-02-28")["status"], "dados_indisponiveis")
        self.assertEqual(self.query("safras", end="2025-02-28")["rows"][0]["rate_percent"], "0")
        self.assertEqual(self.query("variacao", "contribuicao", end="2025-02-28", branch="F02")["status"], "populacao_vazia")

    def test_invalid_filters_never_become_sql(self):
        for kwargs in ({"branch": "F01' OR 1=1 --"}, {"person": "PF OR 1=1"}, {"threshold": True},
                       {"threshold": -1}, {"threshold": 1.5}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.query(**kwargs)

    def test_missing_overdue_excludes_same_population_from_rate(self):
        raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        raw["scenarios"]["fronteira"]["installments"][1]["interest_centavos"] = None
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            conn = build_database(path, "fronteira")
            self.addCleanup(conn.close)
            intent = Intent("evolucao", "2025-01-31", "2025-01-31", None, None, 90, "fronteira")
            result = run_query(conn, intent)
            self.assertEqual(result["excluded_rows"], 1)
            self.assertEqual(result["rows"][0]["denominator_centavos"], 800000)
            self.assertEqual(result["rows"][0]["numerator_centavos"], 700000)

    def test_limit_never_presents_partial_total_or_contribution(self):
        raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data = raw["scenarios"]["fronteira"]
        data["references"].append("2025-02-28")
        for index in range(501):
            product = f"PF_EXTRA{index}"
            raw["products"].append({"id": product, "person": "PF"})
            data["contracts"].append({"id": product, "person": "PF", "product": product,
                                      "branch": "F01", "originated_at": "2024-09-01", "principal_centavos": 100})
            data["installments"].append({"id": product, "contract_id": product, "due_at": "2024-11-01",
                                         "principal_centavos": 100, "interest_centavos": 0})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wide.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            conn = build_database(path, "fronteira")
            self.addCleanup(conn.close)
            for action in ("saldo", "contribuicao"):
                result = run_query(conn, Intent(action, "2025-01-31", "2025-02-28", None, None, 90, "fronteira"))
                self.assertEqual(result["status"], "limite_excedido")
                self.assertEqual(result["rows"], [])

    def test_balance_keeps_branch_and_product_breakdown(self):
        raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data = raw["scenarios"]["fronteira"]
        extra = dict(data["contracts"][0], id="S:OTHER", branch="F02")
        item = dict(data["installments"][0], id="S:OTHER:I1", contract_id="S:OTHER")
        data["contracts"].append(extra)
        data["installments"].append(item)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "branches.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            conn = build_database(path, "fronteira")
            self.addCleanup(conn.close)
            result = run_query(conn, Intent("saldo", "2025-01-31", "2025-01-31", None, None, 90, "fronteira"))
            self.assertEqual(len(result["rows"]), 3)
            second_branch = [r for r in result["rows"] if r["branch"] == "F02"]
            self.assertEqual(second_branch[0]["principal_centavos"], 100000)


if __name__ == "__main__":
    unittest.main()
