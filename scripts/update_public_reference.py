"""Snapshot contextual da série pública SGS 21114; nunca contratos individuais."""

import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlencode

CATALOG = "https://dadosabertos.bcb.gov.br/dataset/21114-inadimplencia-da-carteira-de-credito-com-recursos-livres---pessoas-fisicas---credito-pessoal-"
TITLE = "Inadimplência — recursos livres — PF — crédito pessoal não consignado"
TARGET = Path(__file__).resolve().parents[1] / "data/public/sgs21114.json"


def normalize_reference(raw: bytes) -> list[dict]:
    if len(raw) > 2_000_000:
        raise ValueError("Referência pública excede 2 MB.")
    try:
        values = json.loads(raw)
        if not isinstance(values, list) or not values:
            raise ValueError("Série vazia ou formato inválido.")
        rows, periods = [], set()
        for item in values:
            if not isinstance(item["valor"], str):
                raise ValueError("Percentual publicado deve ser uma string decimal.")
            parsed = datetime.strptime(item["data"], "%d/%m/%Y").date()
            period = parsed.strftime("%Y-%m")
            value = Decimal(item["valor"])
            if not value.is_finite() or not 0 <= value <= 100 or period in periods:
                raise ValueError("Valor público inválido ou período duplicado.")
            periods.add(period)
            text = format(value, "f")
            rows.append({"period": period, "published_date": parsed.isoformat(),
                         "value_percent": text.rstrip("0").rstrip(".") if "." in text else text,
                         "threshold_operator": ">", "threshold_days": 90, "origin_kind": "publica"})
        return sorted(rows, key=lambda row: row["period"])
    except (KeyError, TypeError, InvalidOperation, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Resposta pública não contém uma série mensal válida.") from None


def write_snapshot(raw: bytes, target: Path, metadata: dict) -> None:
    rows = normalize_reference(raw)
    info = {**metadata, "series": 21114, "title": TITLE, "catalog_url": CATALOG,
            "license": "ODbL-1.0", "attribution": "Banco Central do Brasil — Departamento de Estatísticas",
            "unit": "percentual", "frequency": "mensal", "sha256_raw": hashlib.sha256(raw).hexdigest()}
    snapshot = {"metadata": info, "raw_utf8": raw.decode("utf-8"), "rows": rows}
    content = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                         prefix=".sgs-", suffix=".tmp", delete=False) as output:
            temporary = Path(output.name)
            output.write(content)
        os.replace(temporary, target)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def load_snapshot(path: Path) -> dict:
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    try:
        raw = snapshot["raw_utf8"].encode("utf-8")
        if (snapshot["metadata"]["series"] != 21114
                or hashlib.sha256(raw).hexdigest() != snapshot["metadata"]["sha256_raw"]
                or normalize_reference(raw) != snapshot["rows"]):
            raise ValueError("Snapshot público não confere com sua origem.")
    except (KeyError, TypeError, AttributeError):
        raise ValueError("Snapshot público inválido.") from None
    return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2025-12-31")
    args = parser.parse_args()
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    if start > end:
        parser.error("Período invertido.")
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.21114/dados?" + urlencode({
        "formato": "json", "dataInicial": start.strftime("%d/%m/%Y"), "dataFinal": end.strftime("%d/%m/%Y")})
    request = urllib.request.Request(url, headers={"User-Agent": "FinanceiroPortfolio/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(2_000_001)
        write_snapshot(raw, TARGET, {"source_url": url, "fetched_at": datetime.now(timezone.utc).isoformat(),
                                     "requested_start": start.isoformat(), "requested_end": end.isoformat()})
        snapshot = load_snapshot(TARGET)
        print(f"SGS 21114: {len(snapshot['rows'])} observações públicas; SHA-256 {snapshot['metadata']['sha256_raw']}")
    except (OSError, ValueError) as exc:
        print(f"Atualização não concluída ({type(exc).__name__}). Snapshot anterior preservado, se existente.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
