# Banking Analytics Assistant

Projeto de portfólio de um assistente conversacional para analistas consultarem dados empresariais, com foco financeiro e de crédito. A experiência prevista combina respostas fundamentadas, consultas, tabelas, gráficos e aprofundamentos ao longo da conversa.

Repositório público: [Henri-fernandes/banking-analytics-assistant](https://github.com/Henri-fernandes/banking-analytics-assistant). A criação foi confirmada; o primeiro envio do código está em preparação.

**Estado em 04/11/2026:** primeira prova implementada e testada localmente em Python/Streamlit e SQLite. Há três cenários sintéticos, referência pública do Banco Central e 37 testes passando. Inferência real, repositório remoto e deploy ainda estão pendentes. Começamos com crédito pessoal parcelado PF e capital de giro parcelado PJ, com mais produtos posteriormente. Todos os Overs usam `dias_atraso >= N`.

O desenvolvimento será conduzido pelo autor no **VS Code com Codex**, utilizando esta documentação como referência. A aplicação publicada continuará sendo executada na nuvem.

Para retomar em outro diretório ou sessão, comece por [Início no Codex](INICIO_NO_CODEX.md). As instruções permanentes do agente estão em [AGENTS.md](AGENTS.md).

## Documentação de continuidade

- [Contexto e decisões](docs/contexto-e-decisoes.md): intenção do autor, escolhas confirmadas, sugestões e histórico relevante.
- [Regras e validação](docs/regras-e-validacao.md): diretrizes analíticas e técnicas para as entregas.
- [Próximos passos](docs/proximos-passos.md): estado verificável, pendências e roteiro proposto.
- [Especificação da primeira entrega](docs/superpowers/specs/2026-11-04-primeira-entrega-design.md): base para planejamento, com perguntas, dados e exemplos numéricos.
- [Plano da prova funcional](docs/superpowers/plans/2026-11-04-prova-conversacional-nuvem.md): entregas, arquivos e verificações da implementação.
- [Execução e publicação](docs/operacao/prova-nuvem.md): ambiente, segredos, candidatos de hospedagem e critérios de nuvem.
- [Evidências da prova](docs/avaliacoes/prova-inicial.md): testes executados, resultados e pendências reais.
- [Regras da carteira](docs/metricas/carteira-v1-inclusive.md): definições versionadas utilizadas nos cálculos.

## Executar localmente

Na pasta atual, com o ambiente preparado:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --browser.gatherUsageStats false
```

Abra `http://localhost:8501`. As consultas pelos controles funcionam sem chave de LLM. O chat depende de configurar um provedor Free verificado; veja o guia de operação. A demonstração identifica os dados sintéticos e mantém a referência pública separada.

Para testar:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Para outro ambiente com Python 3.12, crie `.venv` e instale `requirements.lock.txt`. As instruções completas estão no guia vinculado. O Git local está inicializado; a publicação do código depende de autenticação com permissão nesse repositório.

## Capacidades implementadas na prova

Saldo por produto/filial, evolução dos Overs, contribuição para a variação e safras/MOB; tabela, gráfico e SQL com parâmetros; reconstrução histórica por eventos; regras documentais versionadas; adaptadores de interpretação Groq/Gemini com limites; contexto separado por sessão. A interface e os adaptadores foram testados com respostas controladas; isso não comprova inferência real ou publicação na nuvem.

## Decisão de arquitetura

O backend e a interface serão desenvolvidos como aplicação própria, aproveitando bibliotecas, APIs e serviços existentes. Essa abordagem prioriza acesso público, controle dos componentes de engenharia de IA e alternativas de fornecedores compatíveis com o orçamento.

O Databricks Genie Agents foi avaliado como alternativa gerenciada. Poderá ser reconsiderado ou utilizado em um experimento comparativo futuro. Seu uso não é uma dependência aprovada do atendimento da aplicação.

- [ADR-0001 — Aplicação própria como entrega principal](docs/adr/0001-aplicacao-propria.md)
- [Pesquisa — Genie Agents versus aplicação própria](docs/pesquisas/comparacao-genie-agents-aplicacao-propria.md)
- [Escopo de negócio e dependências dos dados](docs/escopo-negocio.md)
- [Glossário inicial](GLOSSARY.md)

## Instituição e domínios confirmados

Banco/instituição financeira com atendimento a **pessoas físicas (PF) e pessoas jurídicas (PJ)**, confirmado pelo autor em 30/10/2026, e dados de clientes, filiais, propostas, contratos, parcelas, pagamentos e renegociações. Os temas desejados incluem concessão, safras/MOB/bads, carteira e saldo devedor, inadimplência/overs/write-off, PD, provisão/PDD, renegociações e reestruturações, RAROC, risco de liquidez e DRE.

O [escopo de negócio](docs/escopo-negocio.md) diferencia as entidades confirmadas das fontes adicionais propostas para sustentar esses temas. A lista de temas não define, por si só, uma fórmula, um modelo de risco ou conformidade regulatória.

## Restrições confirmadas

- Nenhum custo adicional além do uso do Codex já contratado para desenvolver o projeto.
- Código destinado ao GitHub e aplicação acessível por terceiros na nuvem.
- Atendimento completo funcionando com o computador do autor desligado.
- Desenvolvimento, preparação de dados e treinamento podem ocorrer localmente; os artefatos necessários ao atendimento devem estar disponíveis na nuvem.
- Provedores, cotas, persistência e alternativas gratuitas precisam ser validados antes de fechar a stack.
- Ao esgotar os recursos gratuitos, o sistema deve informar a limitação e respeitar o orçamento.
- Projeto independente dos trabalhos existentes de Airflow, webscraping e BI.

## Experiência de referência

1. O analista pergunta como está a inadimplência de uma filial.
2. O assistente resolve a definição do indicador e os filtros, consulta os dados e apresenta evolução, comparação, tabela e gráfico.
3. O analista pede um aprofundamento por segmento ou pergunta o que contribuiu para a variação.
4. O assistente preserva o contexto e apresenta resultados verificáveis, distinguindo decomposição da variação, hipóteses e conclusões causais.

O indicador, a definição de inadimplência e as regras desse exemplo ainda serão formalizados.

## Capacidades desejadas

Contexto de conversa, RAG documental, embeddings, índice vetorial, ferramentas de consulta e cálculo, agente com limites de execução, saída estruturada, streaming, guardrails, cache, fallback, avaliações e observabilidade.

Fine-tuning é um experimento desejado, com alvo, conjunto de avaliação e hospedagem a definir. MCP é uma extensão possível para ferramentas internas. Gráficos, consultas exibidas e exportações CSV/Excel/PDF fazem parte das funcionalidades a detalhar. Essas capacidades serão priorizadas em entregas; a lista não significa que todas precisam estar na primeira versão.

## Próximas definições

O próximo trabalho é concluir o envio ao repositório já criado, configurar os provedores gratuitos e executar a prova externa. Os serviços candidatos foram reavaliados documentalmente; gratuidade nas contas e atendimento com o PC desligado ainda precisam de teste. O estado das decisões e os critérios seguintes estão em [próximos passos](docs/proximos-passos.md).

A escolha arquitetural original não fixou fornecedores. A prova local utiliza a stack descrita acima; hospedagem e inferência real continuam sem validação funcional nas contas do autor.
