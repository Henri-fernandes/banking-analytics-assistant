import os
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from tests.test_llm import groq_response, payload

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class TestApp(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"GROQ_API_KEY": "", "GEMINI_API_KEY": "",
                                          "GROQ_FREE_VERIFIED": "false", "GEMINI_FREE_VERIFIED": "false"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_without_key_is_usable_and_manual_over_updates(self):
        app = AppTest.from_file(APP).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Dados sintéticos", app.caption[0].value)
        self.assertGreater(len(app.warning), 0)
        self.assertEqual(list(app.dataframe[0].value["Taxa (%)"]), [30.0, 40.0])
        app.number_input(key="threshold").set_value(0).run()
        self.assertEqual(list(app.dataframe[0].value["Taxa (%)"]), [100.0, 100.0])
        app.selectbox(key="branch").select("F02").run()
        self.assertEqual(app.session_state["last_result"]["status"], "populacao_vazia")
        self.assertEqual(len(app.exception), 0)

    def test_followup_and_two_sessions_remain_independent(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GROQ_FREE_VERIFIED": "true"}), \
                patch("financeiro.conversation.request_json", lambda *a, **k: groq_response(
                    payload(action=None, date_from=None, date_to=None, branch=None, person="PJ", threshold=None))):
            first = AppTest.from_file(APP).run(timeout=20)
            second = AppTest.from_file(APP).run(timeout=20)
            first.number_input(key="threshold").set_value(30).run()
            first.chat_input[0].set_value("e em PJ?").run()
            self.assertEqual(len(first.exception), 0)
            self.assertEqual((first.session_state["context"].person, first.session_state["context"].threshold), ("PJ", 30))
            self.assertIsNone(second.session_state["context"].person)
            self.assertEqual(second.session_state["context"].threshold, 90)
            first.button(key="clear_chat").click().run()
            self.assertEqual(first.session_state["messages"], [])

    def test_all_four_analytical_views_render(self):
        app = AppTest.from_file(APP).run(timeout=20)
        for action in ("Saldo da carteira", "Contribuição para a variação", "Comparação de safras"):
            with self.subTest(action=action):
                app.selectbox(key="action").select(action).run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(app.session_state["last_result"]["status"], "ok")
                self.assertGreater(len(app.dataframe[0].value), 0)


if __name__ == "__main__":
    unittest.main()
