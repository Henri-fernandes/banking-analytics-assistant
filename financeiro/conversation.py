"""Contexto por conversa e respostas baseadas em resultados determinísticos."""

import logging
import sqlite3
import time
from dataclasses import asdict
from decimal import Decimal
from uuid import uuid4

from financeiro.analytics import Intent, run_query
from financeiro.data import parse_date
from financeiro.llm import ProviderError, SCHEMA, interpret, request_json

LOGGER = logging.getLogger(__name__)


def resolve_intent(payload, previous):
    if set(payload) != set(SCHEMA["required"]):
        raise ValueError("Intenção deve conter apenas os campos analíticos permitidos.")
    values = asdict(previous) if previous else asdict(Intent("clarificar", None, None))
    for field, value in payload.items():
        if value is not None:
            values[field] = None if value == "ALL" and field in ("person", "branch") else value
    if values["action"] not in ("saldo", "evolucao", "contribuicao", "safras", "clarificar"):
        raise ValueError("Informe uma pergunta analítica suportada.")
    for field in ("date_from", "date_to"):
        if values[field] is not None:
            parse_date(values[field])
    if values["date_from"] and values["date_to"] and values["date_from"] > values["date_to"]:
        raise ValueError("Período invertido.")
    if (type(values["threshold"]) is not int or not 0 <= values["threshold"] <= 3650000
            or values["person"] not in (None, "PF", "PJ")
            or (values["branch"] is not None and not isinstance(values["branch"], str))):
        raise ValueError("Filtro ou limiar inválido.")
    if not values["date_to"] or (values["action"] != "saldo" and not values["date_from"]):
        values["action"] = "clarificar"
    return Intent(**values)


def _br_decimal(value, places=2):
    return f"{Decimal(value):,.{places}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def format_result(result):
    status = result["status"]
    if status == "limite_excedido":
        return "A consulta excedeu 500 linhas. Reduza o recorte; nenhum total parcial foi apresentado como resultado completo."
    if status == "dados_indisponiveis":
        return "Não há posição completa para: " + ", ".join(result["missing_references"]) + "."
    if status == "esclarecimento":
        return "Informe a análise desejada e o período das posições mensais."
    if status == "populacao_vazia":
        return "Não há saldo elegível neste recorte. A taxa fica sem resultado; isso não significa taxa de 0%."
    filters = result["filters"]
    prefix = f"Dados sintéticos. Filial: {filters['branch'] or 'todas'}; público: {filters['person'] or 'PF e PJ'}. "
    if filters["action"] == "saldo":
        total = sum(row["principal_centavos"] for row in result["rows"])
        body = f"Saldo principal em {filters['date_to']}: R$ {_br_decimal(Decimal(total) / 100)}. Juros e encargos estão separados."
    elif filters["action"] == "contribuicao":
        body = (f"Variação entre {filters['date_from']} e {filters['date_to']}: {_br_decimal(result['variation_pp'])} p.p. "
                "As contribuições por produto reconciliam essa variação e combinam saldo e composição; não demonstram causa econômica.")
    elif filters["action"] == "safras":
        body = "Comparação de safras nos MOBs observados. Janelas futuras permanecem ausentes; esta taxa não é PD nem bad acumulado."
    else:
        points = [f"{r['reference']}: {_br_decimal(r['rate_percent'])}%" if r["rate_percent"] is not None
                  else f"{r['reference']}: sem saldo elegível" for r in result["rows"]]
        body = "; ".join(points) + "."
    rule = f" Over{filters['threshold']}: atraso maior ou igual a {filters['threshold']} dias, por saldo principal elegível."
    if filters["action"] == "saldo":
        rule = ""
    exclusions = f" {result['excluded_rows']} posição(ões) excluída(s) por informação ausente." if result["excluded_rows"] else ""
    return prefix + body + rule + exclusions + f" Regra: {result['rule_version']}."


def answer(question, previous, conn, config, transport=None):
    started = time.monotonic()
    request_id = str(uuid4())

    def failure(code, text):
        metadata = {"error": code, "request_id": request_id,
                    "duration_ms": round((time.monotonic() - started) * 1000)}
        LOGGER.info("Consulta não concluída: %s", metadata)
        return {"status": code, "text": text, "result": None, "context": previous, "metadata": metadata}

    try:
        parsed = interpret(question, previous, config, transport or request_json)
        intent = resolve_intent(parsed["payload"], previous)
        result = run_query(conn, intent)
        result["request_id"] = request_id
        metadata = {"provider": parsed["provider"], "model": parsed["model"], "usage": parsed["usage"],
                    "duration_ms": round((time.monotonic() - started) * 1000), "request_id": result["request_id"]}
        LOGGER.info("Consulta concluída: %s", {**metadata, "action": intent.action, "status": result["status"]})
        return {"status": result["status"], "text": format_result(result), "result": result,
                "context": intent, "metadata": metadata}
    except ProviderError as exc:
        messages = {
            "missing_key": "A interpretação por IA não está configurada. As consultas pelos controles continuam disponíveis.",
            "free_unverified": "O plano gratuito do provedor precisa ser verificado antes de habilitar a interpretação.",
            "quota": "A cota de inferência está esgotada. Tente mais tarde ou use os controles analíticos.",
            "budget": "O limite de chamadas desta demonstração foi atingido. Aguarde um minuto.",
            "invalid_output": "O provedor não retornou uma intenção válida. Reformule a pergunta.",
            "auth": "A autenticação do provedor precisa ser corrigida na configuração do servidor.",
            "invalid_question": "Escreva uma pergunta de até 2.000 caracteres.",
        }
        return failure(exc.code, messages.get(exc.code, "Provedor indisponível. Tente mais tarde."))
    except ValueError as exc:
        return failure("esclarecimento", f"Confira o recorte: {exc}")
    except sqlite3.Error:
        return failure("query_error", "A consulta falhou. Nenhuma conclusão de negócio foi produzida.")
