# Orientações para o Codex

## Objetivo e estado

Construir uma aplicação própria de análise conversacional interna para um banco com clientes **PF e PJ**. Analistas devem consultar dados, receber respostas verificáveis, tabelas e gráficos e aprofundar a conversa. O desenvolvimento será no VS Code com Codex; o atendimento publicado funcionará integralmente na nuvem.

A prova local usa Python/Streamlit, SQLite reconstruível, três cenários sintéticos e uma referência pública do Banco Central. Há testes unittest e adaptadores Groq/Gemini; inferência real e deploy ainda não foram verificados. O código foi enviado ao repositório público `Henri-fernandes/banking-analytics-assistant`, na `main`; confira commit, remote e autenticação ao retomar.

## Leitura por tarefa

- **Retomada ou mudança de direção:** leia [contexto e decisões](docs/contexto-e-decisoes.md) e [próximos passos](docs/proximos-passos.md). Continue do estado registrado, sem refazer perguntas resolvidas.
- **Execução e testes:** leia [README](README.md), [operação da prova](docs/operacao/prova-nuvem.md) e [evidências](docs/avaliacoes/prova-inicial.md) antes de repetir instalações ou verificações.
- **Dados, produtos, indicadores ou políticas:** leia [escopo de negócio](docs/escopo-negocio.md), [glossário](GLOSSARY.md) e [regras e validação](docs/regras-e-validacao.md).
- **LLM, RAG, ferramentas, interface ou deploy:** leia [regras e validação](docs/regras-e-validacao.md). Consulte a [pesquisa de provedores](docs/pesquisas/comparacao-genie-agents-aplicacao-propria.md) antes de reutilizar suas conclusões e confira limites atuais em fontes oficiais.
- **Reavaliar Genie:** leia o [ADR-0001](docs/adr/0001-aplicacao-propria.md). A entrega principal escolhida é aplicação própria.

## Restrições de execução

- Custo adicional zero além do Codex já contratado. Cotas esgotadas devem resultar em limitação informada, preservando o orçamento.
- Aplicação acessível a terceiros com o computador do autor desligado. Treinamento local é permitido; inferência, consultas e recuperação para visitantes precisam estar na nuvem.
- Registre uma alternativa viável para cada dependência externa crítica. Provedor candidato não é stack aprovada.
- Todos os Overs internos usam limiar inclusivo: `dias_atraso >= N`. Preserve e identifique diferenças nas definições de fontes externas.
- Decisões novas do usuário atualizam os documentos correspondentes. Diferencie decisão confirmada, proposta e hipótese em aberto.
- Execute o trabalho autorizado. Resolva escolhas reversíveis com pressupostos explícitos; pergunte quando faltar uma decisão de produto, regra financeira ou custo que altere o resultado.

## Entrega e evidência

Implemente por entregas verificáveis, com métricas e dados de referência. Os comandos reais de execução e unittest estão no README. Ao concluir, informe mudanças, verificações realizadas e limitações reais. Uma previsão de arquitetura não conta como funcionalidade implementada, e um resultado gravado deve ser identificado como exemplo.

Mantenha instruções permanentes neste arquivo curtas; detalhes ficam nos documentos vinculados. Preserve caminhos relativos para que a pasta possa ser movida para outro computador ou repositório.
