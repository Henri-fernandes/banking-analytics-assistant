"""Ferramentas de leitura: somente SQL definido pela aplicação."""

import calendar
import json
import sqlite3
import time
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from financeiro.data import parse_date


@dataclass(frozen=True)
class Intent:
    action: str
    date_from: str | None
    date_to: str | None
    branch: str | None = None
    person: str | None = None
    threshold: int = 90
    scenario: str = "variacao"


def decimal_text(value):
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _rate(numerator, denominator):
    return None if not denominator else decimal_text(Decimal(numerator) * 100 / Decimal(denominator))


def _references(start, end):
    year, month = start.year, start.month
    result = []
    while (year, month) <= (end.year, end.month):
        result.append(f"{year:04d}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result


def _rule_evidence(action, version):
    section = {"saldo": "saldo", "contribuicao": "contribuicao", "safras": "safras"}.get(action, "over")
    document = "docs/metricas/carteira-v1-inclusive.md"
    text = (Path(__file__).resolve().parents[1] / document).read_text(encoding="utf-8")
    if f"Regra: {version}\n" not in text:
        raise ValueError("Documento de regras não corresponde à versão do cálculo.")
    excerpt = text.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0].strip()
    return {"document": document, "version": version, "section": section, "text": excerpt}


def run_query(conn: sqlite3.Connection, intent: Intent) -> dict:
    meta = dict(conn.execute("SELECT name, value FROM metadata"))
    if intent.action not in ("saldo", "evolucao", "contribuicao", "safras", "clarificar"):
        raise ValueError("Ferramenta desconhecida.")
    if (intent.person not in (None, "PF", "PJ") or intent.branch not in [None, *json.loads(meta["branches"])]
            or type(intent.threshold) is not int or not 0 <= intent.threshold <= 3_650_000
            or intent.scenario != meta["scenario"]):
        raise ValueError("Filtro, cenário ou limiar inválido.")
    result = {"request_id": str(uuid4()), "status": "esclarecimento", "rows": [], "sql": [],
              "parameters": {}, "filters": asdict(intent), "rule_version": meta["rule_version"],
              "source_versions": {"synthetic": meta["source_version"], "sha256": meta["checksum"]},
              "excluded_rows": 0, "truncated": False}
    result["rule_evidence"] = _rule_evidence(intent.action, meta["rule_version"])
    if intent.action == "clarificar" or not intent.date_to or (intent.action != "saldo" and not intent.date_from):
        return result
    end = parse_date(intent.date_to)
    start = parse_date(intent.date_from or intent.date_to)
    if start > end:
        raise ValueError("Período invertido.")
    if any(d.day != calendar.monthrange(d.year, d.month)[1] for d in (start, end)):
        raise ValueError("Use posições no último dia de cada mês.")
    if (end.year - start.year) * 12 + end.month - start.month > 120:
        raise ValueError("Limite de 120 meses por consulta.")
    expected = ([end.isoformat()] if intent.action == "saldo" else
                [start.isoformat(), end.isoformat()] if intent.action == "contribuicao" else _references(start, end))
    available = {r[0] for r in conn.execute("SELECT reference FROM coverage")}
    if not set(expected) <= available:
        result.update(status="dados_indisponiveis", missing_references=sorted(set(expected) - available))
        return result
    params = {"start": end.isoformat() if intent.action == "saldo" else start.isoformat(),
              "end": end.isoformat(), "branch": intent.branch, "person": intent.person,
              "threshold": intent.threshold}
    where = "reference BETWEEN :start AND :end AND (:branch IS NULL OR branch=:branch) AND (:person IS NULL OR person=:person)"
    required = "principal_centavos IS NOT NULL" + (" AND days_overdue IS NOT NULL" if intent.action != "saldo" else "")
    eligible = f"{where} AND principal_centavos > 0 AND {required}"
    sums = "SUM(CASE WHEN days_overdue >= :threshold THEN principal_centavos ELSE 0 END) AS numerator_centavos, SUM(principal_centavos) AS denominator_centavos"
    if intent.action == "saldo":
        sql = f"SELECT reference, branch, product, SUM(principal_centavos) AS principal_centavos FROM positions WHERE {eligible} GROUP BY reference, branch, product ORDER BY branch, product LIMIT 501"
    elif intent.action in ("evolucao", "contribuicao"):
        group = "reference, product" if intent.action == "contribuicao" else "reference"
        sql = f"SELECT {group}, {sums} FROM positions WHERE {eligible} GROUP BY {group} ORDER BY {group} LIMIT 501"
    else:
        mob = "(CAST(substr(reference,1,4) AS INTEGER)-CAST(substr(originated_at,1,4) AS INTEGER))*12+CAST(substr(reference,6,2) AS INTEGER)-CAST(substr(originated_at,6,2) AS INTEGER)"
        sql = f"SELECT substr(originated_at,1,7) AS cohort, {mob} AS mob, reference, {sums} FROM positions WHERE {eligible} GROUP BY cohort, mob, reference ORDER BY cohort, mob LIMIT 501"
    exclusions_sql = f"SELECT count(*) FROM positions WHERE {where} AND NOT ({required})"
    result.update(sql=[sql, exclusions_sql], parameters=params)
    deadline = time.monotonic() + 2
    conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
    try:
        rows = [dict(r) for r in conn.execute(sql, params)]
        result["excluded_rows"] = conn.execute(exclusions_sql, params).fetchone()[0]
    finally:
        conn.set_progress_handler(None, 0)
    result["truncated"] = len(rows) > 500
    if result["truncated"]:
        result.update(status="limite_excedido")
        return result
    if intent.action == "contribuicao":
        endpoints = (start.isoformat(), end.isoformat())
        totals = {ref: sum(r["denominator_centavos"] for r in rows if r["reference"] == ref) for ref in endpoints}
        if not all(totals.values()):
            result.update(status="populacao_vazia")
            return result
        grouped = {(r["product"], r["reference"]): r["numerator_centavos"] for r in rows}
        contributions = []
        for product in sorted({r["product"] for r in rows}):
            initial = grouped.get((product, endpoints[0]), 0)
            final = grouped.get((product, endpoints[1]), 0)
            value = Decimal(100) * (Decimal(final) / totals[endpoints[1]] - Decimal(initial) / totals[endpoints[0]])
            contributions.append({"product": product, "start_numerator_centavos": initial,
                                  "end_numerator_centavos": final, "contribution_pp": decimal_text(value)})
        variation = sum(Decimal(row["contribution_pp"]) for row in contributions)
        result.update(rows=contributions, variation_pp=decimal_text(variation), status="ok",
                      denominators_centavos=totals)
        return result
    if intent.action != "saldo":
        for row in rows:
            row["rate_percent"] = _rate(row["numerator_centavos"], row["denominator_centavos"])
        if intent.action == "evolucao":
            by_ref = {r["reference"]: r for r in rows}
            rows = [by_ref.get(ref, {"reference": ref, "numerator_centavos": 0, "denominator_centavos": 0,
                                     "rate_percent": None}) for ref in expected]
    nonempty = any(r.get("principal_centavos", r.get("denominator_centavos", 0)) > 0 for r in rows)
    result.update(rows=rows, status="ok" if nonempty else "populacao_vazia")
    return result
