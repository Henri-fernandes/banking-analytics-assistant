import json
import unittest
import urllib.error
from unittest.mock import patch

from financeiro.llm import CallLimiter, ProviderError, interpret, request_json


def payload(**changes):
    return {"action": "evolucao", "date_from": "2025-01-31", "date_to": "2025-02-28",
            "branch": None, "person": None, "threshold": 90, **changes}


def config(**changes):
    return {"PROVIDER": "groq", "GROQ_API_KEY": "test-key", "GROQ_FREE_VERIFIED": True,
            "limiter": CallLimiter(), "session_id": "test", **changes}


def groq_response(value=None):
    return {"choices": [{"message": {"content": json.dumps(payload() if value is None else value),
                                       "refusal": None}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50}}


class TestLLM(unittest.TestCase):
    def test_structured_request_has_no_sql_or_financial_data(self):
        def transport(url, body, headers, timeout=20):
            self.assertEqual(url, "https://api.groq.com/openai/v1/chat/completions")
            self.assertFalse(body["stream"])
            self.assertTrue(body["response_format"]["json_schema"]["strict"])
            self.assertNotIn("tools", body)
            return groq_response()
        result = interpret("Como evoluiu?", None, config(), transport)
        self.assertEqual(result["payload"]["threshold"], 90)
        self.assertEqual(result["usage"]["total_tokens"], 50)

    def test_missing_key_or_unverified_free_never_calls_network(self):
        def forbidden(*args, **kwargs):
            self.fail("Rede não deveria ser acessada")
        for fields in ({"GROQ_API_KEY": ""}, {"GROQ_FREE_VERIFIED": False}):
            with self.subTest(fields=fields), self.assertRaises(ProviderError):
                interpret("Consulta", None, config(**fields), forbidden)

    def test_bad_json_refusal_and_truncation(self):
        for kind in ("json", "refusal", "truncated"):
            raw = groq_response()
            if kind == "json":
                raw["choices"][0]["message"]["content"] = "{"
            elif kind == "refusal":
                raw["choices"][0]["message"]["refusal"] = "refused"
            else:
                raw["choices"][0]["finish_reason"] = "length"
            with self.subTest(kind=kind), self.assertRaises(ProviderError) as caught:
                interpret("Consulta", None, config(), lambda *a, **k: raw)
            self.assertEqual(caught.exception.code, "invalid_output")

    def test_fallback_is_bounded_and_normalized(self):
        calls = []
        def transport(url, body, headers, timeout=20):
            calls.append(url)
            if "groq" in url:
                raise ProviderError("quota")
            return {"candidates": [{"content": {"parts": [{"text": json.dumps(payload(person="PJ"))}]},
                                     "finishReason": "STOP"}],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 15, "totalTokenCount": 25}}
        result = interpret("e PJ?", None, config(ALLOW_FALLBACK=True, GEMINI_API_KEY="test-alt",
                                                GEMINI_FREE_VERIFIED=True), transport)
        self.assertEqual((result["provider"], result["payload"]["person"]), ("gemini", "PJ"))
        self.assertEqual(len(calls), 2)

    def test_shared_and_session_budgets_count_failures(self):
        now = [0]
        limiter = CallLimiter(clock=lambda: now[0])
        for _ in range(6):
            limiter.admit("first")
        with self.assertRaises(ProviderError):
            limiter.admit("first")
        for _ in range(4):
            limiter.admit("second")
        with self.assertRaises(ProviderError):
            limiter.admit("third")
        now[0] = 61
        limiter.admit("first")

    def test_malformed_nested_response_is_a_provider_error(self):
        for raw in ({"choices": [{"message": [], "finish_reason": "stop"}]},
                    {**groq_response(), "usage": None}):
            with self.subTest(raw=raw):
                if raw.get("usage", "present") is None:
                    result = interpret("Consulta", None, config(), lambda *a, **k: raw)
                    self.assertEqual(result["usage"], {})
                else:
                    with self.assertRaises(ProviderError) as caught:
                        interpret("Consulta", None, config(), lambda *a, **k: raw)
                    self.assertEqual(caught.exception.code, "invalid_output")

    def test_http_errors_and_wrapped_timeout_are_distinct(self):
        errors = [(urllib.error.HTTPError("https://example.invalid", 429, "quota", {}, None), "quota"),
                  (urllib.error.HTTPError("https://example.invalid", 401, "auth", {}, None), "auth"),
                  (urllib.error.HTTPError("https://example.invalid", 503, "down", {}, None), "unavailable"),
                  (urllib.error.URLError(TimeoutError()), "timeout")]
        for error, expected in errors:
            with self.subTest(expected=expected), patch("urllib.request.urlopen", side_effect=error):
                with self.assertRaises(ProviderError) as caught:
                    request_json("https://example.invalid", {}, {"Authorization": "Bearer private-test-token"})
                self.assertEqual(caught.exception.code, expected)
                self.assertNotIn("private-test-token", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
