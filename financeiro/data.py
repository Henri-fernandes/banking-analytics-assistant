"""Cenários sintéticos e posições financeiras reconstruíveis."""

import calendar
import hashlib
import json
import sqlite3
from datetime import date
from pathlib import Path

RULE_VERSION = "carteira-v1-inclusive"


def parse_date(value):
    if not isinstance(value, str):
        raise ValueError("Data deve ser ISO YYYY-MM-DD.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise ValueError("Data inválida.") from None
    if parsed.isoformat() != value:
        raise ValueError("Data deve ser ISO YYYY-MM-DD.")
    return parsed


def _money(value):
    if value is not None and (type(value) is not int or not 0 <= value <= 10**14):
        raise ValueError("Componente monetário inválido: use centavos inteiros não negativos.")
    return value


def _unique(rows, key):
    result = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str) or not value or value in result:
            raise ValueError(f"Identificador ausente ou duplicado: {key}.")
        result[value] = row
    return result


def position_at(contract, installments, allocations, reference):
    ref = parse_date(reference)
    origin = parse_date(contract["originated_at"])
    if ref < origin:
        raise ValueError("Referência anterior à originação.")
    if contract.get("status", "active") != "active":
        raise ValueError("Evento de status não suportado por esta amostra.")
    granted = _money(contract.get("principal_centavos"))
    items = _unique(installments, "id")
    for item in items.values():
        if item["contract_id"] != contract["id"] or parse_date(item["due_at"]) < origin:
            raise ValueError("Parcela sem vínculo ou com vencimento anterior à originação.")
        _money(item.get("principal_centavos"))
        _money(item.get("interest_centavos"))
    principals = [i.get("principal_centavos") for i in items.values()]
    if not items or (granted is not None and None not in principals and sum(principals) != granted):
        raise ValueError("Parcelas não reconciliam com principal concedido.")
    paid = {key: {"principal_centavos": 0, "interest_centavos": 0} for key in items}
    totals = {key: {"principal_centavos": 0, "interest_centavos": 0} for key in items}
    for event in allocations:
        key = event["installment_id"]
        when = parse_date(event["effective_at"])
        if key not in items or when < origin:
            raise ValueError("Alocação órfã ou anterior à originação.")
        for component in ("principal_centavos", "interest_centavos"):
            value = _money(event.get(component))
            for bucket in ([totals[key], paid[key]] if when <= ref else [totals[key]]):
                bucket[component] = None if value is None or bucket[component] is None else bucket[component] + value
    for key, item in items.items():
        for component in ("principal_centavos", "interest_centavos"):
            expected, actual = item.get(component), totals[key][component]
            if expected is not None and actual is not None and actual > expected:
                raise ValueError("Alocação excede o componente da parcela.")
    amortizations = [p["principal_centavos"] for p in paid.values()]
    principal = None if granted is None or None in amortizations else granted - sum(amortizations)
    days, unknown = 0, False
    for key, item in items.items():
        due = parse_date(item["due_at"])
        if due > ref:
            continue
        residues = []
        for component in ("principal_centavos", "interest_centavos"):
            expected, actual = item.get(component), paid[key][component]
            residues.append(None if expected is None or actual is None else expected - actual)
        if None in residues:
            unknown = True
        elif sum(residues) > 0:
            days = max(days, (ref - due).days)
    reasons = []
    if principal is None:
        reasons.append("principal ausente")
    if unknown:
        reasons.append("componentes de atraso ausentes")
    return {"principal_centavos": principal, "days_overdue": None if unknown else days,
            "excluded_reason": "; ".join(reasons) or None}


def build_database(path: Path, scenario: str) -> sqlite3.Connection:
    raw = Path(path).read_bytes()
    if len(raw) > 5_000_000:
        raise ValueError("Amostra excede o tamanho suportado.")
    source = json.loads(raw)
    if source["origin"]["kind"] != "sintetica":
        raise ValueError("Esta carga aceita somente cenários sintéticos identificados.")
    if scenario not in source["scenarios"]:
        raise ValueError("Cenário desconhecido.")
    data = source["scenarios"][scenario]
    contracts = _unique(data["contracts"], "id")
    items = _unique(data["installments"], "id")
    products = _unique(source["products"], "id")
    _unique(data["allocations"], "id")
    refs = data["references"]
    if not refs or len(set(refs)) != len(refs) or len(contracts) > 10000:
        raise ValueError("Cobertura ausente, duplicada ou amostra excessiva.")
    for ref in refs:
        parsed = parse_date(ref)
        if parsed.day != calendar.monthrange(parsed.year, parsed.month)[1]:
            raise ValueError("Posição deve referir-se ao último dia do mês.")
    grouped_items = {key: [] for key in contracts}
    grouped_events = {key: [] for key in contracts}
    for item in items.values():
        if item["contract_id"] not in contracts:
            raise ValueError("Parcela órfã.")
        grouped_items[item["contract_id"]].append(item)
    for event in data["allocations"]:
        if event["installment_id"] not in items:
            raise ValueError("Alocação órfã.")
        grouped_events[items[event["installment_id"]]["contract_id"]].append(event)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript("""
            CREATE TABLE metadata (name TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE coverage (reference TEXT PRIMARY KEY);
            CREATE TABLE positions (
                contract_id TEXT NOT NULL, reference TEXT NOT NULL, person TEXT NOT NULL,
                product TEXT NOT NULL, branch TEXT NOT NULL, originated_at TEXT NOT NULL,
                principal_centavos INTEGER, days_overdue INTEGER, excluded_reason TEXT,
                PRIMARY KEY (contract_id, reference));
        """)
        metadata = {"scenario": scenario, "source_version": source["version"],
                    "checksum": hashlib.sha256(raw).hexdigest(), "rule_version": RULE_VERSION,
                    "branches": json.dumps(source["branches"]), "origin_kind": "sintetica"}
        conn.executemany("INSERT INTO metadata VALUES (?, ?)", metadata.items())
        conn.executemany("INSERT INTO coverage VALUES (?)", [(ref,) for ref in refs])
        for key, contract in contracts.items():
            if (contract["product"] not in products or contract["person"] not in ("PF", "PJ")
                    or products[contract["product"]]["person"] != contract["person"]
                    or contract["branch"] not in source["branches"]):
                raise ValueError("Cadastro de produto, público ou filial incompatível.")
            for ref in refs:
                if parse_date(ref) < parse_date(contract["originated_at"]):
                    continue
                pos = position_at(contract, grouped_items[key], grouped_events[key], ref)
                conn.execute("INSERT INTO positions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (key, ref, contract["person"], contract["product"], contract["branch"],
                              contract["originated_at"], pos["principal_centavos"],
                              pos["days_overdue"], pos["excluded_reason"]))
        conn.commit()
        conn.execute("PRAGMA query_only = ON")
        return conn
    except Exception:
        conn.close()
        raise
