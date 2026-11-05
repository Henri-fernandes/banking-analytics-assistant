"""Assistente de carteira: consultas verificáveis sobre um banco fictício."""

import json
import os
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from financeiro.analytics import Intent, run_query
from financeiro.conversation import answer, format_result
from financeiro.data import build_database
from financeiro.llm import CallLimiter
from scripts.update_public_reference import load_snapshot

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "data/synthetic/fixtures.json"
ACTIONS = {"Evolução da inadimplência": "evolucao", "Saldo da carteira": "saldo",
           "Contribuição para a variação": "contribuicao", "Comparação de safras": "safras"}
SCENARIOS = {"variacao": "Variação da carteira", "fronteira": "Fronteiras de atraso", "safras": "Safras em mesma idade"}


@st.cache_resource
def shared_limiter():
    return CallLimiter()


def read_config():
    try:
        secrets = dict(st.secrets)
    except FileNotFoundError:
        secrets = {}
    names = ("PROVIDER", "GROQ_API_KEY", "GEMINI_API_KEY", "GROQ_FREE_VERIFIED", "GEMINI_FREE_VERIFIED", "ALLOW_FALLBACK")
    return {key: os.environ.get(key, secrets.get(key)) for key in names if key in os.environ or key in secrets}


def display_result(result):
    st.markdown(format_result(result))
    rows = result["rows"]
    if rows:
        frame = pd.DataFrame(rows)
        for field in list(frame.columns):
            if field.endswith("_centavos"):
                frame[field] = frame[field].map(lambda v: float(Decimal(int(v)) / 100) if pd.notna(v) else None)
            elif field in ("rate_percent", "contribution_pp"):
                frame[field] = pd.to_numeric(frame[field])
        labels = {"reference": "Data", "branch": "Filial", "product": "Produto", "principal_centavos": "Saldo principal (R$)",
                  "numerator_centavos": "Saldo no Over (R$)", "denominator_centavos": "Saldo elegível (R$)",
                  "rate_percent": "Taxa (%)", "contribution_pp": "Contribuição (p.p.)", "mob": "MOB", "cohort": "Safra",
                  "start_numerator_centavos": "Saldo no Over inicial (R$)", "end_numerator_centavos": "Saldo no Over final (R$)"}
        frame = frame.rename(columns=labels)
        action = result["filters"]["action"]
        if result["status"] == "ok":
            if action == "evolucao":
                st.line_chart(frame, x="Data", y="Taxa (%)", color="#16645c", height=260)
            elif action == "saldo":
                st.bar_chart(frame, x="Produto", y="Saldo principal (R$)", color="Filial", height=260)
            elif action == "contribuicao":
                st.bar_chart(frame, x="Produto", y="Contribuição (p.p.)", color="#16645c", height=260)
            elif action == "safras":
                st.line_chart(frame, x="MOB", y="Taxa (%)", color="Safra", height=260)
        st.dataframe(frame, hide_index=True, width="stretch")
    if result["status"] != "ok":
        st.info("Ajuste o recorte nos controles de consulta para investigar outra população ou período.")
    if result["truncated"]:
        st.warning("O resultado atingiu o limite de 500 linhas. Reduza o recorte.")
    with st.expander("Consulta e evidências"):
        evidence = result["rule_evidence"]
        st.markdown(evidence["text"])
        st.caption(f"Fonte da regra: {evidence['document']} / {evidence['section']} / {evidence['version']}")
        for sql in result["sql"]:
            st.code(sql, language="sql")
        st.json({"parâmetros": result["parameters"], "filtros": result["filters"],
                 "regra": result["rule_version"], "fontes": result["source_versions"],
                 "excluídos": result["excluded_rows"], "id": result["request_id"]})


st.set_page_config(page_title="Assistente de carteira", page_icon="▤", layout="wide")
st.title("Assistente de carteira")
st.caption("Dados sintéticos — banco fictício. Crédito pessoal PF e capital de giro PJ.")
st.markdown("Consulte a carteira, compare períodos e acompanhe as evidências de cada resposta.")

source = json.loads(FIXTURE.read_text(encoding="utf-8"))
st.session_state.setdefault("session_id", str(uuid4()))
st.session_state.setdefault("messages", [])
with st.sidebar:
    st.header("Recorte da consulta")
    scenario = st.selectbox("Cenário", list(SCENARIOS), format_func=SCENARIOS.get, key="scenario")
    refs = sorted(source["scenarios"][scenario]["references"])
    if st.session_state.get("loaded_scenario") != scenario:
        for key, value in {"date_from": refs[0], "date_to": refs[-1], "branch": "ALL", "person": "ALL",
                           "threshold": 90, "action": "Evolução da inadimplência"}.items():
            st.session_state[key] = value
        st.session_state.update(loaded_scenario=scenario, messages=[], selected_key=None)
        st.session_state.pop("pending_intent", None)
    pending = st.session_state.pop("pending_intent", None)
    if pending:
        for field in ("branch", "person", "threshold"):
            st.session_state[field] = getattr(pending, field) if getattr(pending, field) is not None else "ALL"
        for field in ("date_from", "date_to"):
            if getattr(pending, field) in refs:
                st.session_state[field] = getattr(pending, field)
        if pending.action in ACTIONS.values():
            st.session_state["action"] = next(k for k, v in ACTIONS.items() if v == pending.action)
    action = st.selectbox("Análise", list(ACTIONS), key="action")
    date_from = st.selectbox("Posição inicial", refs, key="date_from")
    date_to = st.selectbox("Posição final", refs, key="date_to")
    branch = st.selectbox("Filial", ["ALL", *source["branches"]],
                          format_func=lambda v: "Todas as filiais" if v == "ALL" else v, key="branch")
    person = st.selectbox("Público", ["ALL", "PF", "PJ"],
                          format_func=lambda v: "PF e PJ" if v == "ALL" else v, key="person")
    threshold = int(st.number_input("Dias de atraso do Over", min_value=0, max_value=3650000, step=1, key="threshold"))
    st.caption(f"Over{threshold} inclui o próprio dia {threshold}. Saldo principal em reais.")
    consult = st.button("Consultar", type="primary", width="stretch")
    if st.button("Limpar conversa", key="clear_chat", width="stretch"):
        st.session_state.messages = []
        st.session_state.pop("context", None)
        st.session_state.selected_key = None
    st.divider()
    st.caption("Amostras controladas para verificar os cálculos. Não representam desempenho de mercado.")

selected = Intent(ACTIONS[action], date_from, date_to, None if branch == "ALL" else branch,
                  None if person == "ALL" else person, threshold, scenario)
selected_key = tuple(asdict(selected).values())
config = {**read_config(), "limiter": shared_limiter(), "session_id": st.session_state.session_id}
provider = config.get("PROVIDER", "groq").upper()
enabled = bool(config.get(f"{provider}_API_KEY")) and config.get(f"{provider}_FREE_VERIFIED") in (True, "true")

conn = build_database(FIXTURE, scenario)
try:
    if selected_key != st.session_state.get("selected_key") or consult:
        st.session_state.context = selected
        try:
            st.session_state.last_result = run_query(conn, selected)
        except ValueError as exc:
            st.session_state.last_result = None
            st.session_state.manual_error = str(exc)
        else:
            st.session_state.pop("manual_error", None)
        st.session_state.selected_key = selected_key
    analysis_tab, public_tab = st.tabs(["Carteira e conversa", "Referência de mercado"])
    with analysis_tab:
        if not enabled:
            st.warning("A interpretação por IA ainda não está habilitada. Use os controles para consultar os dados.")
        if st.session_state.get("manual_error"):
            st.error(st.session_state.manual_error)
        if st.session_state.get("last_result"):
            display_result(st.session_state.last_result)
        st.divider()
        st.subheader("Aprofundar a análise")
        st.caption("Exemplos: “e em PJ?”, “compare as safras” ou “quais produtos contribuíram para a variação?”.")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["text"])
        question = st.chat_input("Pergunte sobre esta carteira", max_chars=2000, disabled=not enabled)
        if question:
            with st.spinner("Consultando a carteira…"):
                response = answer(question, st.session_state.get("context"), conn, config)
            st.session_state.messages.extend([{"role": "user", "text": question},
                                              {"role": "assistant", "text": response["text"]}])
            st.session_state.messages = st.session_state.messages[-40:]
            if response["result"] is not None:
                st.session_state.last_result = response["result"]
                st.session_state.context = response["context"]
                st.session_state.pending_intent = response["context"]
                st.session_state.selected_key = tuple(asdict(response["context"]).values())
            st.session_state.last_metadata = response["metadata"]
            st.rerun()
        if st.session_state.get("last_metadata"):
            with st.expander("Execução da pergunta"):
                st.json(st.session_state.last_metadata)
    with public_tab:
        st.subheader("Crédito pessoal PF no mercado")
        st.markdown("Referência pública do Banco Central, separada da carteira do banco fictício.")
        st.info("A série SGS 21114 usa atraso superior a 90 dias. O Over90 desta aplicação inclui 90 dias. As definições diferem.")
        try:
            snapshot = load_snapshot(ROOT / "data/public/sgs21114.json")
            public_frame = pd.DataFrame(snapshot["rows"])[["period", "value_percent"]]
            public_frame["value_percent"] = pd.to_numeric(public_frame["value_percent"])
            public_frame = public_frame.rename(columns={"period": "Mês", "value_percent": "Taxa publicada (%)"})
            st.line_chart(public_frame, x="Mês", y="Taxa publicada (%)", color="#527d93", height=240)
            st.dataframe(public_frame, hide_index=True, width="stretch")
            info = snapshot["metadata"]
            st.caption(f"Banco Central do Brasil. Série mensal 21114. Obtida em {info.get('fetched_at', 'data não informada')}. Licença ODbL.")
            st.markdown(f"[Fonte e metodologia]({info['catalog_url']})")
        except FileNotFoundError:
            st.info("A referência pública ainda não está disponível. A consulta da carteira sintética continua funcionando.")
        except (ValueError, KeyError):
            st.error("A integridade da referência pública não foi confirmada. Seus valores não serão exibidos.")
finally:
    conn.close()
