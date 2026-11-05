import unittest

from financeiro.analytics import Intent
from financeiro.conversation import answer, resolve_intent
from financeiro.data import build_database
from financeiro.llm import ProviderError
from tests.test_data import FIXTURE
from tests.test_llm import config, groq_response, payload


class TestConversation(unittest.TestCase):
    def setUp(self):
        self.previous = Intent("evolucao", "2025-01-31", "2025-02-28", "F01", "PF", 30, "variacao")
        self.conn = build_database(FIXTURE, "variacao")
        self.addCleanup(self.conn.close)

    def test_followup_keeps_threshold_and_period(self):
        current = resolve_intent(payload(action=None, date_from=None, date_to=None, branch=None,
                                         person="PJ", threshold=None), self.previous)
        self.assertEqual((current.person, current.branch, current.threshold), ("PJ", "F01", 30))
        self.assertEqual((current.date_from, current.date_to), ("2025-01-31", "2025-02-28"))
        self.assertEqual(self.previous.person, "PF")

    def test_all_clears_only_requested_filter_and_first_question_requires_period(self):
        current = resolve_intent(payload(branch="ALL", person=None), self.previous)
        self.assertIsNone(current.branch)
        self.assertEqual(current.person, "PF")
        first = resolve_intent(payload(date_from=None, date_to=None), None)
        self.assertEqual(first.action, "clarificar")

    def test_extra_sql_bad_date_threshold_and_public_rejected(self):
        for raw in (payload(sql="DROP TABLE positions"), payload(date_to="2025-02-30"),
                    payload(threshold=True), payload(threshold=-1), payload(person="invalid")):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                resolve_intent(raw, self.previous)

    def test_answer_uses_validated_result_and_causal_limit(self):
        raw = payload(action="contribuicao", threshold=90, person="ALL")
        response = answer("O que causou o aumento?", self.previous, self.conn, config(),
                          lambda *a, **k: groq_response(raw))
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["result"]["variation_pp"], "10")
        self.assertIn("causa", response["text"])
        self.assertIn("10", response["text"])

    def test_provider_failure_is_not_business_result(self):
        def fail(*args, **kwargs):
            raise ProviderError("quota")
        response = answer("Consulta", self.previous, self.conn, config(), fail)
        self.assertEqual(response["status"], "quota")
        self.assertIsNone(response["result"])
        self.assertEqual(response["context"], self.previous)
        self.assertEqual(response["metadata"]["error"], "quota")
        self.assertIn("request_id", response["metadata"])
        self.assertNotIn("test-key", str(response["metadata"]))

    def test_unknown_branch_is_clarified_before_sql(self):
        response = answer("Consulta", self.previous, self.conn, config(),
                          lambda *a, **k: groq_response(payload(branch="F99")))
        self.assertEqual(response["status"], "esclarecimento")
        self.assertIsNone(response["result"])


if __name__ == "__main__":
    unittest.main()
