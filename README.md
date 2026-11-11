# Banking Analytics Assistant

Projeto de um assistente interno para um banco com clientes PF e PJ. A experiência principal será um chat que consulta dados, arquivos e regras da instituição e responde com fontes verificáveis, tabelas e gráficos quando necessários.

## Estado em 10/11/2026

O autor solicitou remover a implementação anterior e recomeçar por partes. O painel Streamlit, seus módulos, amostras, testes e configurações foram retirados da versão atual. O código anterior continua no histórico do Git, no commit `afc1077`.

Esta versão contém documentação de contexto, decisões, pesquisa e registros históricos. Não há aplicação executável, base de dados ativa, corpus de produção, agente ou RAG implementados nesta etapa do recomeço. Os resultados de testes da prova anterior são históricos.

Repositório: [Henri-fernandes/banking-analytics-assistant](https://github.com/Henri-fernandes/banking-analytics-assistant).

## Objetivo preservado

- Conversar sobre dados, arquivos e regras da própria instituição, preservando o contexto dos aprofundamentos.
- Combinar recuperação documental e consultas a dados, com cálculos determinísticos e fontes identificadas.
- Aplicar controles de acesso, validação, limites e tratamento de falhas; documentos recuperados são evidência, não instruções.
- Servir visitantes integralmente na nuvem com o computador do autor desligado e custo adicional zero.
- Começar com crédito pessoal parcelado PF e capital de giro parcelado PJ; adicionar outros produtos depois.
- Combinar fontes sintéticas, públicas e reais conforme disponibilidade e condições de uso. Todos os Overs internos incluem o próprio limiar: `dias_atraso >= N`.

O vídeo fornecido pelo autor é referência de experiência. Frameworks, hospedagem e provedores serão escolhidos conforme o recorte e o orçamento; a stack da prova removida não é obrigatória.

## Continuidade

1. [Contexto e decisões](docs/contexto-e-decisoes.md): escolhas confirmadas e histórico.
2. [Próximos passos](docs/proximos-passos.md): primeira parte do recomeço e pontos a definir.
3. [Escopo de negócio](docs/escopo-negocio.md), [glossário](GLOSSARY.md) e [regras de engenharia](docs/regras-e-validacao.md): referências para discutir dados e documentos.
4. [Registro do recomeço](docs/reinicio.md): remoção realizada, arquivos preservados e situação da publicação anterior.

Os documentos da prova anterior em `docs/avaliacoes/`, `docs/operacao/`, `docs/metricas/` e `docs/superpowers/` ficam como histórico identificado. Seus comandos e entregas não descrevem a versão atual.
