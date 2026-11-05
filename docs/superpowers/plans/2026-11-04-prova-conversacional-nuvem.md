# Prova conversacional de carteira na nuvem — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execução proposta: pelo agente principal nesta sessão; sem subagentes, salvo escolha explícita do autor.

**Goal:** implementar e verificar uma aplicação que responda às quatro perguntas iniciais sobre PF/PJ, execute SQL rastreável e inferência na nuvem, e respeite a regra `dias_atraso >= N` para todos os Overs.

**Architecture:** arquivos sintéticos pequenos e versionados recompõem posições históricas em SQLite; ferramentas executam SQL fixo parametrizado. Uma API interpreta a intenção; o backend valida os filtros e produz texto, tabela e gráfico a partir do mesmo resultado. Referência pública fica separada da carteira; nenhuma integração real é presumida disponível.

**Tech Stack:** proposta para esta prova: Python 3.12, biblioteca padrão (`sqlite3`, `decimal`, `unittest`, `urllib`, `json`), Streamlit 1.66.0; hospedagem Community Cloud, alternativa Render Free; Groq Free, alternativa Gemini Free. [Pesquisa atualizada e condições](../../pesquisas/comparacao-genie-agents-aplicacao-propria.md#revalidação-dos-candidatos-em-04112026).

**Spec:** [primeira entrega, com correção inclusiva de todos os Overs](../specs/2026-11-04-primeira-entrega-design.md).

Data: 04/11/2026. Estado: plano escrito para revisão; nenhuma tarefa executada. A autorização para avançar à etapa de planejamento não é evidência de aplicação funcional.

## Global Constraints

- “sem custo adicional”; “com o computador do autor desligado” durante o atendimento publicado.
- “OverN inclui atraso a partir de N dias, inclusive”. Dados externos mantêm suas próprias definições.
- “BRL; valores de referência em centavos inteiros; taxas calculadas antes do arredondamento de exibição”.
- “Uma linha por contrato e data de referência”; posições mensais não são somadas entre datas.
- “taxas e contribuições conferidas antes da formatação, com tolerância de 0,000001 ponto percentual”.
- “Texto, tabela e gráfico usam o mesmo resultado validado, com regra, fontes, data e consulta.”
- “Nenhum serviço externo foi criado, dependência instalada ou dado ingerido” na preparação deste plano.
- Demonstração aberta somente com dados sintéticos e referências públicas verificadas. Base real depende de disponibilidade e condições próprias; nenhum registro privado será publicado por este plano.

## Review Focus

1. Origem incompleta ou posição inexistente deve produzir indisponibilidade, sem virar carteira vazia ou taxa zero — testes da tarefa 1 e 2.
2. Pagamento parcial e pagamento posterior à referência devem preservar atraso e história corretos — testes da tarefa 1.
3. Mudança de público em continuação deve preservar data, filial e limiar; duas sessões devem permanecer independentes — testes da tarefa 3 e 5.
4. Resposta de modelo malformada, filtro desconhecido e tentativa de SQL devem ser rejeitados antes da consulta — testes da tarefa 3.
5. Erro de provedor, ausência de chave e cota esgotada devem limitar a inferência sem fabricar resposta ou iniciar serviço pago — testes da tarefa 3 e prova da tarefa 5.

## Limite desta entrega e ambiente

Esta é a prova pequena que antecede geração em escala. Usará cenários manuais, não o gerador de até 1.000 contratos e 24 meses sugerido na especificação. Parcelas têm componentes financeiros explicitamente informados; não escolher um sistema de amortização por inferência. Vetores, embeddings, fine-tuning, autenticação com perfis, XLSX/PDF e módulos financeiros posteriores ficam fora desta prova, sem alegação de implementação.

Nesta sessão, `Get-Command python,py` não encontrou runtime no PATH; Node e Git foram encontrados. A pasta ainda não é repositório Git. Não instalar Python globalmente nem publicar para resolver isso silenciosamente. No início da execução, procurar runtime em instalações conhecidas do ambiente; se não houver, preparar instalação isolada na pasta do projeto, com download oficial e permissões de rede aplicáveis. Não usar Codespaces ou outra conta com cobrança como substituição automática.

Quando Python 3.12 estiver disponível, executar na raiz em PowerShell, uma linha por operação:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install streamlit==1.66.0
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Esses são comandos planejados, não comandos já existentes ou executados. Dependências transitivas efetivamente resolvidas deverão ser registradas após o smoke test. Nenhum teste automatizado desta prova fará chamada externa paga ou dependerá de chave real.

## Arquivos e responsabilidades

| Criar | Responsabilidade |
|---|---|
| `.gitignore`, `requirements.txt` | Excluir `.venv/`, `.tools/`, `__pycache__/`, `.streamlit/secrets.toml`, `.env`, `data/private/` e artefatos locais; fixar `streamlit==1.66.0` |
| `financeiro/__init__.py`, `tests/__init__.py` | Pacotes Python, sem efeitos colaterais na importação |
| `financeiro/data.py` | Validar dados sintéticos, calcular posições por eventos e montar SQLite em memória |
| `financeiro/analytics.py` | Tipos da consulta, validação do recorte, consultas parametrizadas e resultados |
| `financeiro/llm.py` | Dois adaptadores HTTP pequenos, esquema de intenção, limites e erros de provedor |
| `financeiro/conversation.py` | Resolver intenção com contexto, selecionar ferramenta e formatar resposta com fontes |
| `app.py` | Chat, controles, tabelas, gráficos e histórico por sessão em Streamlit |
| `data/synthetic/fixtures.json`, `data/synthetic/README.md` | Cenários construídos com gabaritos, componentes e cobertura declarados |
| `scripts/update_public_reference.py`, `data/public/README.md` | Atualizar somente a referência pública oficial, com metadados e integridade |
| `tests/test_data.py`, `tests/test_analytics.py`, `tests/test_llm.py`, `tests/test_conversation.py`, `tests/test_public_reference.py`, `tests/test_app.py` | Casos de referência, limites e integração local |
| `.streamlit/secrets.example.toml`, `.streamlit/config.toml` | Nomes de configuração sem segredos e configuração de interface |
| `docs/operacao/prova-nuvem.md`, `docs/avaliacoes/prova-inicial.md` | Como executar/publicar e evidências reais coletadas, com resultado por caso |

Modificar também README, AGENTS, guia de retomada e estado ao implementar, para apontarem aos comandos reais e distinguirem funcionamento local de nuvem verificada.

## Tarefa 1: dados de referência e posições históricas

**Files:** criar estrutura mínima, `financeiro/data.py`, arquivos sintéticos e `tests/test_data.py`.

**Interfaces:** `position_at(contract: dict, installments: list[dict], allocations: list[dict], reference: str) -> dict`; `build_database(path: Path, scenario: str) -> sqlite3.Connection`. Data ISO, dinheiro em centavos; `ValueError` em arquivo inconsistente. A conexão retornada recebe `PRAGMA query_only = ON` depois da carga e não é compartilhada entre threads.

- [x] **1. Escrever o primeiro teste de fronteira e história.** Usar `unittest`, `datetime.date` e `timedelta` para construir vencimentos, sem números de dias digitados e datas incompatíveis. Incluir este caso em uma classe `TestData`:

```python
def test_partial_payment_preserves_over90(self):
    contract = {"id": "S:C1", "originated_at": "2024-09-01", "principal_centavos": 100000}
    installments = [{"id": "S:I1", "contract_id": "S:C1", "due_at": "2024-11-02",
                     "principal_centavos": 100000, "interest_centavos": 1000}]
    allocations = [{"installment_id": "S:I1", "effective_at": "2025-01-30",
                    "principal_centavos": 40000, "interest_centavos": 1000}]
    before = position_at(contract, installments, allocations, "2025-01-31")
    self.assertEqual(before["principal_centavos"], 60000)
    self.assertEqual(before["days_overdue"], 90)
    allocations.append({"installment_id": "S:I1", "effective_at": "2025-02-01",
                        "principal_centavos": 60000, "interest_centavos": 0})
    self.assertEqual(position_at(contract, installments, allocations, "2025-01-31"), before)
```

- [x] **2. Executar o teste antes da implementação.** Com runtime disponível: `python -m unittest tests.test_data -v`. Esperar falha de importação da função, não falha de dependência de teste.
- [x] **3. Implementar a posição determinística.** Filtrar eventos por `effective_at <= reference`; principal = concessão menos amortizações. Para cada parcela, conferir saldo de principal e juros separados; vencimento mais antigo com resíduo contratual determina atraso, limitado inferiormente a zero. Validar IDs, relações, datas, tipos inteiros sem booleanos, componentes não negativos, totais das parcelas e ausência de alocação excessiva. Rejeitar eventos financeiros não suportados em vez de ignorá-los. Calcular apenas contratos já originados na referência.
- [x] **4. Criar três cenários manuais no mesmo JSON, selecionáveis por `scenario`.** Cada um tem ID de origem sintética, versão, referências completas, contratos, parcelas e alocações. Não consolidar cenários entre si:

Todos os contratos do arquivo usam filial fictícia `F01`, código de produto `PF_CP` ou `PJ_CG` e público coerente com o produto. Cada parcela recebe ID único e o vínculo com o contrato; as datas de origem e os componentes constam de cada registro. O exemplo de teste de `position_at` acima omite atributos cadastrais que essa função de cálculo não consome; `build_database` exige o cadastro completo. A regra da posição só exige campos financeiros não negativos quando informados; ausências permitidas são sinalizadas e excluídas das métricas afetadas, sem coerção para zero.

| Cenário | Conteúdo e gabarito |
|---|---|
| `fronteira` | Referência 31/01/2025; quatro contratos de 100000, 200000, 300000 e 400000 centavos, originados em 01/09/2024, parcelas únicas sem juros, vencimentos em 03/11, 02/11, 01/11 e 03/10 de 2024. Total 1000000, Over90 900000, taxa 90% |
| `variacao` | Referências 31/01 e 28/02/2025. PF: 20000 vencidos em 01/11/2024, 10000 vencidos em 30/11/2024, 30000 a vencer em 31/12/2025; PJ: 10000, 8000 e 22000 centavos com os mesmos três vencimentos. Esses seis contratos originam em 01/09/2024. Acrescentar PF de 20000 centavos originado em 01/02/2025, com vencimento 31/12/2025. Parcelas únicas sem juros e sem pagamentos: taxas 30% e 40%; contribuições PF +5 p.p., PJ +5 p.p. |
| `safras` | Contratos PF de 100000 centavos cada, originados em 15/01 e 15/02/2025, vencimento em 31/12/2025, sem pagamentos e juros. Posições 31/01 e 28/02: primeira safra tem MOB 0 e 1; segunda somente MOB 0 |

- [x] **5. Montar tabela de posições com chave `(scenario, contract_id, reference)` e catálogo de cobertura.** Saldo/atraso ausente permanece ausente com motivo; duplicatas ou inconsistência estrutural rejeitam a carga. Campo financeiro ausente afeta apenas as métricas que o exigem, com contagem de exclusões. Data sem cobertura completa gera indisponibilidade; grupo conhecido sem contratos em data coberta gera população vazia.
- [x] **6. Rodar os testes ampliados.** Acrescentar duplicata, chave órfã, liquidação, juros residuais, componente ausente, valor negativo e cobertura inexistente. Executar `python -m unittest tests.test_data -v`; registrar contagem real e o checksum SHA-256 dos fixtures. Entrega: dados reconstruíveis, sem gerador financeiro em escala.

## Tarefa 2: quatro ferramentas SQL com Overs inclusivos

**Files:** criar `financeiro/analytics.py` e `tests/test_analytics.py`.

**Interfaces:** dataclass `Intent(action, date_from, date_to, branch, person, threshold, scenario)`, sendo `action` um de `saldo`, `evolucao`, `contribuicao`, `safras`, `clarificar`; datas ISO; filtros nulos significam todos após resolução do contexto; limiar é inteiro não negativo. `run_query(conn: sqlite3.Connection, intent: Intent) -> dict` retorna `status`, `rows`, `sql`, `parameters`, `filters`, `rule_version`, `source_versions`, `excluded_rows` e `request_id`. Status: `ok`, `populacao_vazia`, `dados_indisponiveis` ou `esclarecimento`.

- [x] **1. Escrever os testes de referência.** Classe `TestAnalytics`, utilizando a conexão da tarefa 1:

```python
def test_boundary_total(self):
    result = run_query(self.conn, Intent("evolucao", "2025-01-31", "2025-01-31",
                                       None, None, 90, "fronteira"))
    row = result["rows"][0]
    self.assertEqual(row["denominator_centavos"], 1000000)
    self.assertEqual(row["numerator_centavos"], 900000)
    self.assertEqual(row["rate_percent"], "90")
```

Acrescentar laço com N = 1, 15, 30, 60, 90 e 180, construindo posições aos N−1, N e N+1 dias; com saldos iguais, dois de três entram. Incluir N=0 com dia zero dentro e rejeitar limiar negativo, fracionário ou booleano. Strings decimais de saída serão canônicas, sem zeros finais desnecessários.
- [x] **2. Executar `python -m unittest tests.test_analytics -v` e confirmar falha antes do código.**
- [x] **3. Implementar SQL fixo por ação, com parâmetros de valores.** O fragmento central do numerador deve ser:

```sql
SUM(CASE WHEN days_overdue >= :threshold THEN principal_centavos ELSE 0 END)
```

Aplicar elegibilidade por principal positivo e referência, filtros por público/filial e agrupamento permitido. Saldo usa a data final; evolução usa referências mensais; contribuição usa somente as duas datas completas; safras agrupa originação/MOB, sem preencher desempenho futuro com zero. Usar `Decimal` para taxas e contribuições depois de obter somas inteiras; denominador zero produz `None`, jamais divisão SQLite inteira.
- [x] **4. Escrever gabaritos de contribuição e granularidade.** No cenário `variacao`, verificar taxas 30 e 40 e contribuições 5 e 5 com soma 10 p.p.; testar grupo que só aparece na segunda data, denominador zero, posição ausente e duas parcelas sem duplicação do saldo. No cenário `safras`, verificar MOBs observados e ausência de MOB futuro.
- [x] **5. Executar `python -m unittest tests.test_data tests.test_analytics -v`.** Conferir também que a conexão rejeita `DELETE` e que um filtro de filial como `F01' OR 1=1 --` é rejeitado por validação, antes de executar SQL. Entrega: quatro ferramentas úteis sem qualquer chave de LLM.

## Tarefa 3: interpretação, continuidade e limites de execução

**Files:** criar `financeiro/llm.py`, `financeiro/conversation.py`, testes correspondentes e configuração sem segredos.

**Interfaces:** `request_json(url, payload, headers, timeout=20) -> dict`; `interpret(question, previous, config, transport=request_json) -> dict`; `resolve_intent(payload: dict, previous: Intent | None) -> Intent`; `answer(question, previous, conn, config, transport=request_json) -> dict` retorna estado, texto, resultado analítico, contexto atualizado e metadados de consumo. `ProviderError(code: str)` distingue `missing_key`, `quota`, `timeout`, `unavailable`, `invalid_output` e `budget` sem carregar credencial ou corpo bruto no erro público.

- [x] **1. Escrever testes de contexto, interpretação inválida e cota com transportes falsos.** Eles retornam um corpo JSON construído ou lançam `ProviderError`, sem rede. Caso central:

```python
def test_followup_keeps_threshold(self):
    previous = Intent("evolucao", "2025-01-31", "2025-02-28", "F01", "PF", 30, "variacao")
    payload = {"action": None, "date_from": None, "date_to": None,
               "branch": None, "person": "PJ", "threshold": None}
    current = resolve_intent(payload, previous)
    self.assertEqual(current.person, "PJ")
    self.assertEqual((current.branch, current.threshold), ("F01", 30))
    self.assertEqual((current.date_from, current.date_to), ("2025-01-31", "2025-02-28"))
```

Nos payloads, `null` significa manter o contexto; `"ALL"` limpa público/filial. Sem contexto, `threshold=null` usa Over90, público/filial nulos significam todos e ausência de período exige esclarecimento. Ação ausente sem ação anterior também exige esclarecimento. Para saldo com data final informada, usar essa única posição; para demais ações exigir o intervalo pertinente. Cenário pertence ao controle do aplicativo, nunca é escolhido pelo modelo.
- [x] **2. Executar os testes e confirmar falha antes da implementação.** `python -m unittest tests.test_llm tests.test_conversation -v`.
- [x] **3. Implementar o schema da intenção.** Exigir seis campos (`action`, `date_from`, `date_to`, `branch`, `person`, `threshold`), todos presentes e anuláveis; `additionalProperties: false`. Validar tipos, datas existentes, período em ordem, público, filial e ação em listas permitidas. Rejeitar campos como `sql`, comandos ou filtros desconhecidos. O prompt inclui somente catálogo, versão das regras e contexto mínimo; documentos recuperados são evidência, não comandos. O modelo retorna intenção, sem valores financeiros ou SQL.
- [ ] **4. Implementar os dois transportes REST com o mesmo contrato local.** Groq: `POST https://api.groq.com/openai/v1/chat/completions`, `model=openai/gpt-oss-20b`, `stream=false`, `max_completion_tokens=1024`, mensagens e `response_format` com `type=json_schema`, `strict=true`. Gemini alternativo: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent`, chave no header `x-goog-api-key`, conteúdo e `generationConfig` com `responseMimeType=application/json`, `responseJsonSchema` e `maxOutputTokens=1024`. Testar a disponibilidade efetiva dos modelos no Free antes de habilitar chamada real; falha não permite mudar para modelo pago. Normalizar ambos os resultados e validar novamente no backend.
- [x] **5. Impor limites no backend.** Pergunta até 2000 caracteres; no máximo duas chamadas por pergunta (uma principal e uma alternativa); timeout HTTP de 20 segundos; sem loop de retry. Alternativa só quando configurada e seu plano gratuito tiver sido verificado. JSON inválido pede reformulação; 429/503/timeout permitem a tentativa alternativa; autenticação inválida exige corrigir configuração. Limite compartilhado em memória, protegido por lock, de 10 chamadas por minuto/processo e 6 por sessão/minuto, contado também nas falhas. Restringir SQL a 500 linhas e 2 segundos usando progress handler; resultado truncado deve ser identificado. Limites locais não são prova do plano de cobrança do provedor.
- [x] **6. Formatar a explicação sem nova inferência.** Usar templates a partir de `run_query`, regra inclusiva, datas, filtros e fontes; contribuição não vira afirmação causal. Selecionar a seção pertinente da regra documentada por ID/versão, sem serviço vetorial nesta prova. Rastrear ID, ferramenta, SQL, tempo e tokens reportados; logs operacionais efêmeros e exportação de evidência sem chaves ou dados privados.
- [x] **7. Rodar os testes ampliados.** Incluir JSON truncado, campo extra, recusa do provedor, intervalo impossível, filial desconhecida, pedido causal sem evidência, cota de ambos esgotada e mensagem com instrução para gerar SQL. `python -m unittest tests.test_llm tests.test_conversation -v`. Entrega: respostas testáveis com provedor falso e limites verificáveis; não declarar inferência real antes do teste externo.

## Tarefa 4: referência pública identificada e reproduzível

**Files:** criar `scripts/update_public_reference.py`, `tests/test_public_reference.py`, `data/public/README.md`; arquivos baixados somente após validar o conteúdo.

**Interfaces:** `normalize_reference(raw: bytes) -> list[dict]`; `write_snapshot(raw: bytes, target: Path, metadata: dict) -> None`. O script aceita período por argumentos `--start` e `--end`, exige datas e série fixa 21114; não aceita URL arbitrária. Rede ocorre só na atualização, nunca em cada pergunta.

- [x] **1. Escrever testes de normalização com dados construídos.** Em classe `TestPublicReference`:

```python
def test_percentage_preserves_external_definition(self):
    rows = normalize_reference(b'[{"data":"01/01/2025","valor":"5.25"}]')
    self.assertEqual(rows[0]["value_percent"], "5.25")
    self.assertEqual(rows[0]["threshold_operator"], ">")
    self.assertEqual(rows[0]["threshold_days"], 90)
    self.assertEqual(rows[0]["origin_kind"], "publica")
```

- [x] **2. Rodar o teste para confirmar falha e implementar parse com `json`, `Decimal` e datas.** Rejeitar HTML, duplicata de período, percentual fora de 0–100 e estrutura inesperada. Download limitado a 2 MB e timeout de 20 segundos. Falha não substitui o último snapshot válido; escrita via arquivo temporário no mesmo diretório e substituição após validação.
- [x] **3. Atualizar somente a série pública identificada.** Após confirmar o recurso na ficha oficial, usar o endpoint `https://api.bcb.gov.br/dados/serie/bcdata.sgs.21114/dados?formato=json&dataInicial=01/01/2024&dataFinal=31/12/2025`. Registrar resposta bruta, normalizada, data de obtenção real, SHA-256, título, fonte e licença ODbL com atribuição; manter os arquivos públicos separados do dataset sintético e do licenciamento do código. Não inventar valores se o serviço estiver indisponível. Nessa situação, publicar indisponibilidade da referência e manter esta etapa pendente de coleta.
- [x] **4. Rodar `python -m unittest tests.test_public_reference -v`**, incluindo HTML, duplicata, falha sem snapshot e falha com snapshot anterior íntegro. Entrega: referência contextual pública separada, com diferença explícita entre `>90` externo e `>=90` interno; nenhuma comparação de equivalência ou enriquecimento de contratos individuais.

## Tarefa 5: interface, publicação e evidência ponta a ponta

**Files:** criar `app.py`, configuração Streamlit e `tests/test_app.py`; criar os dois documentos operacionais e atualizar documentação de continuidade.

**Interfaces:** `app.py` usa `answer` e `build_database`; guarda somente contexto e mensagens da sessão em `st.session_state`. Conexão SQLite por execução/thread, nunca um singleton global. Compartilhar somente o limitador sem mensagens ou resultados privados. Configuração de API vem do ambiente/secrets, nunca de campo de chave no navegador.

- [x] **1. Escrever smoke test de interface sem rede.** Usar a API oficial `AppTest` no `unittest`, sem adicionar dependência de teste:

```python
def test_without_key_app_remains_usable(self):
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file("app.py").run()
    self.assertEqual(len(app.exception), 0)
    self.assertIn("Dados sintéticos", app.caption[0].value)
    self.assertGreater(len(app.warning), 0)
```

Limpar configuração de chaves no processo do teste, preservando/restaurando o ambiente original. A falta de chave produz aviso e permite os controles analíticos; não apresenta interpretação por LLM como funcional.
- [x] **2. Rodar o teste antes da implementação e criar a página.** Título “Assistente de carteira”; aviso “Dados sintéticos — banco fictício”; seletor do cenário, período, filial, público e limiar default 90; chat; botão “Limpar conversa”; tabela, gráfico e SQL com parâmetros em expansor. Sobreposição de períodos sem dados mostra lacunas. A referência pública aparece em área própria com atualização e definição. Não exibir instruções internas de implementação no fluxo do analista.
- [ ] **3. Conferir duas sessões e integração com provedor falso.** Testar que alterar pessoa em uma sessão não modifica outra; “e em PJ?” preserva Over30 e período; limpar conversa apaga o contexto apenas daquela sessão. Verificar que tabela e gráfico recebem o mesmo `rows` e o SQL exibido é o realmente executado. `python -m unittest discover -s tests -v` e inspeção visual local com filtros e uma falha de inferência.
- [x] **4. Preparar deploy reproduzível.** Documentar Python 3.12, `requirements.txt`, `app.py` e configuração de segredos; registrar versões transitivas de um ambiente que passou nos testes. Community Cloud como primeira opção. Alternativa Render: build `pip install -r requirements.txt` e start `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT`, instância Free sem pagamento cadastrado. Não criar banco de expiração curta ou serviço pago. Documentar que conversa e logs são efêmeros, enquanto dados/regras são recompostos de arquivos versionados.
- [ ] **5. Verificar os pré-requisitos de conta antes de chamar API ou publicar.** Identificar repositório GitHub de destino, conta de hospedagem e chave de provedor Free; inspecionar plano e cotas da conta sem revelar segredos. Se não estiverem acessíveis por ferramentas/sessões autorizadas, concluir código, testes locais e instruções e pedir apenas a ação necessária para configurar acesso. Não solicitar chave em mensagem nem tratar a falta dela como teste de gratuidade concluído. Publicação externa ocorre somente após resultado local concreto e revisão da ação de publicar.
- [ ] **6. Executar prova externa e registrar resultado por caso.** Um visitante faz pergunta nova com o computador do autor desligado; filtrar PF e PJ, alterar Over30 para Over90 e confirmar fronteiras; pedir contribuição e safra; reiniciar e repetir consulta verificando versões. Simular 429 e timeout com transporte controlado; identificar simulação no relatório. Registrar URL, commit/versão, data, duração e resultado sem segredo. Caso não se possa desligar a máquina ou obter participação do visitante nesta sessão, deixar esse critério explicitamente “não executado”, sem substituir por resposta gravada.
- [x] **7. Atualizar README, AGENTS, guia de retomada e próximos passos com evidência real.** Distinguir testes automatizados locais, inferência real, referência pública coletada e prova por terceiro. No relatório, incluir consumo, falhas, limitações de sessão/hibernação e o que permanece pendente. Não marcar etapa de nuvem concluída enquanto um critério obrigatório não foi executado.

## Cobertura e revisão do plano

| Requisito da especificação | Onde será verificado |
|---|---|
| P01–P04, taxa e contribuição reconciliáveis | Tarefas 1 e 2; integração na 5 |
| Todos os Overs inclusivos, exemplos numéricos e precisão | Tarefa 2, incluindo fronteiras gerais e Over90 |
| Tempo, pagamentos, granularidade e recarga | Tarefa 1 e reinício na 5 |
| Continuidade, ambiguidade, fontes e linguagem causal | Tarefa 3 e duas sessões na 5 |
| Público versus sintético e metadados | Tarefa 4 e apresentação na 5 |
| Nuvem sem PC, cotas e alternativas | Tarefa 5; pesquisa atualizada vinculada |
| Contexto documental | Seleção de regra versionada na tarefa 3; recuperação vetorial não é alegada |
| Base real e simulação em escala | Dependências explicitamente identificadas, fora da prova pequena; não são critérios falsamente concluídos |

Não há comandos de build/test existentes para reutilizar. Este plano define os primeiros comandos; a sua presença não significa que já rodaram. Como ainda não há Git inicializado, nenhum commit foi criado. Versionar as entregas após existir um repositório e revisar os arquivos a incluir; nunca executar `git add .` sem conferir segredos e dados.

Recomendação de execução para revisão: o agente principal implementa nesta sessão, tarefa a tarefa, sem delegação. Ao fim, revisão do diff, dos casos de referência e das evidências disponíveis. A alternativa com subagentes só será usada se o autor a escolher explicitamente. O plano precisa ser revisado antes do início da implementação, conforme o fluxo de planejamento aplicado.

## Estado da execu??o

A implementa??o local est? conclu?da e testada. Permanecem abertos: tarefa 3, passo 4 (ativa??o real dos modelos no Free); tarefa 5, passo 3 (confer?ncia visual bloqueada pelo Computer Use; parte automatizada passou); tarefa 5, passos 5?6 (contas, reposit?rio e prova externa). Nenhum desses itens deve ser marcado conclu?do por uma resposta de teste ou um servidor apenas local.
