# Continuar o projeto no VS Code com Codex

## Preparação

Abra no VS Code a pasta deste projeto, que contém `AGENTS.md`, `README.md`, `GLOSSARY.md` e `docs/`. Ela pode ser movida para o diretório em que você pretende desenvolver e versionar o código. Preserve a estrutura e os caminhos relativos.

Inicie uma nova sessão do Codex nessa pasta. O Codex descobre instruções em `AGENTS.md` de acordo com a raiz e o diretório de trabalho; se estiver em um repositório maior, instruções ancestrais também podem se aplicar. [Documentação oficial](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Mensagem inicial sugerida

Copie a mensagem abaixo para iniciar a continuidade:

```text
Continue a definição deste projeto a partir da documentação existente.

Leia AGENTS.md, docs/contexto-e-decisoes.md e docs/proximos-passos.md.
Para discutir dados e métricas, consulte também docs/escopo-negocio.md,
GLOSSARY.md e docs/regras-e-validacao.md.

O projeto é uma aplicação própria de análise conversacional interna para
um banco com clientes PF e PJ. A entrega precisa funcionar na nuvem,
acessível a terceiros, com meu computador desligado e custo adicional zero.
Vou desenvolver no VS Code com Codex.

Os produtos iniciais confirmados são crédito pessoal parcelado PF e
capital de giro parcelado PJ; vamos adicionar outros depois. A origem
dos dados será híbrida: sintética, pública e real. As perguntas iniciais
tratam de saldo, inadimplência, contribuição para variações e safras.

Leia docs/superpowers/specs/2026-11-04-primeira-entrega-design.md e retome
do estado registrado em docs/proximos-passos.md. O plano da prova está em
docs/superpowers/plans/2026-11-04-prova-conversacional-nuvem.md e já foi
autorizado e executado localmente. Leia também docs/avaliacoes/prova-inicial.md
e docs/operacao/prova-nuvem.md antes de repetir o que já foi testado.
Para todos os Overs, preserve dias_atraso >= N, já confirmado.
Diferencie propostas de decisões confirmadas. Continue o trabalho útil e pergunte
somente pelo que alterar produto, regra financeira ou custo.

A prova local usa Python/Streamlit, SQLite, cenários sintéticos e uma
referência pública do Banco Central. Há comandos reais de execução e testes
no README. Inferência real e deploy ainda estão pendentes;
o repositório público de destino agora é Henri-fernandes/banking-analytics-assistant.
Confira o estado do Git e a autenticação antes de enviar. Retome a publicação e os testes
externos, preservando o que já foi implementado. Fine-tuning segue futuro.
```

## Mapa dos arquivos

| Arquivo | Papel |
|---|---|
| [AGENTS.md](AGENTS.md) | Instruções curtas e rotas de leitura para o agente |
| [README.md](README.md) | Apresentação e navegação do projeto |
| [Contexto e decisões](docs/contexto-e-decisoes.md) | Intenção, decisões, preferências e limites da conversa |
| [Escopo de negócio](docs/escopo-negocio.md) | Domínios bancários, dados necessários e regras pendentes |
| [Regras e validação](docs/regras-e-validacao.md) | Diretrizes técnicas e evidências esperadas |
| [Próximos passos](docs/proximos-passos.md) | Estado, pendências e roteiro de entregas proposto |
| [Especificação inicial](docs/superpowers/specs/2026-11-04-primeira-entrega-design.md) | Proposta de regras, dados e casos de referência para revisão |
| [Plano da prova](docs/superpowers/plans/2026-11-04-prova-conversacional-nuvem.md) | Tarefas, interfaces e critérios de teste da primeira implementação |
| [Glossário](GLOSSARY.md) | Vocabulário inicial do domínio |
| [ADR-0001](docs/adr/0001-aplicacao-propria.md) | Motivo da escolha por aplicação própria |
| [Pesquisa de alternativas](docs/pesquisas/comparacao-genie-agents-aplicacao-propria.md) | Comparação datada e fontes oficiais |

Esta pasta contém documentação, aplicação, amostras e testes da prova local. Modelos ajustados e publicação ainda não foram implementados. Consulte o relatório para distinguir verificações locais das pendências externas.
