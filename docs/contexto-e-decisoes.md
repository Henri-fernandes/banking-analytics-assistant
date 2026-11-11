# Contexto e decisões da conversa

Registro de continuidade preparado em 30/10/2026 e atualizado em 10/11/2026. Fonte das decisões: conversa com o autor. As referências técnicas de terceiros estão na pesquisa vinculada e têm validade temporal.

## Estado que orienta a retomada

Em 10/11/2026, o autor pediu remover a implementação anterior e recomeçar por partes. A versão atual contém documentação; o painel e seu código, dados e testes foram retirados. O histórico do Git preserva a prova anterior em `afc1077`. Os registros datados abaixo descrevem a situação da época, não capacidades atuais. Consulte [próximos passos](proximos-passos.md) e [registro do recomeço](reinicio.md).

## Por que o projeto existe

O autor quer fortalecer seu portfólio em Dados/BI, SQL, Databricks, Python/PySpark e AI Engineering, aplicado principalmente a finanças e crédito. Já concluiu projetos de Airflow e webscraping; possui um BI de crédito inacabado. Este projeto será independente desses trabalhos. Projetos futuros de modelagem de crédito podem se integrar entre si se houver uma dependência justificada.

## Produto que o autor quer

Um assistente interno que permita ao analista perguntar sobre os dados da própria instituição, consultar resultados e investigar variações. O cenário de referência é:

1. "Como está a inadimplência da filial X?"
2. Resposta com definição do indicador, período, evolução, comparação e gráfico.
3. "O que contribuiu para esse crescimento?"
4. Novas consultas por segmento, produto, safra e demais recortes, preservando o contexto e apresentando evidências.

Os percentuais citados na conversa eram exemplos de interação, não dados reais nem metas. O autor destacou expressamente o cuidado com causalidade: o sistema precisa sustentar o que afirma.

A proposta inicial do assistente de analisar empresas abertas e produzir pareceres de crédito PJ foi corrigida pelo autor. Esse não é o produto escolhido. A comparação de provedores também não muda o objetivo para um simples chatbot de PDFs.

## Decisões confirmadas

| ID | Decisão | Consequência |
|---|---|---|
| D01 | Desenvolvimento pelo autor no VS Code com Codex | Documentação portátil e continuidade fora desta conversa |
| D02 | Banco/instituição financeira com PF e PJ | Ambos fazem parte do domínio; detalhar diferenças por produto e público |
| D03 | Aplicação própria como entrega principal | [ADR-0001](adr/0001-aplicacao-propria.md); Genie foi avaliado como alternativa |
| D04 | Código destinado ao GitHub e aplicação acessível a terceiros na nuvem | Planejar publicação e reprodução |
| D05 | Nenhum custo adicional além do Codex já contratado | Validar planos gratuitos e comportamento ao atingir cotas |
| D06 | Atendimento independente do computador pessoal | Dados, recuperação, ferramentas e inferência necessários aos visitantes na nuvem |
| D07 | Desenvolvimento e treinamento local podem ser utilizados | Publicar os artefatos necessários; escolher hospedagem junto com o alvo do treinamento |
| D08 | Prever alternativas às ferramentas principais | Comparar compatibilidade, cotas e condições de migração/fallback |
| D09 | Entidades centrais indicadas pelo autor | Clientes, filiais, propostas, contratos, parcelas, pagamentos e renegociações |
| D10 | Começar com crédito pessoal parcelado PF e capital de giro parcelado PJ | Confirmado em 04/11/2026; adicionar outros produtos posteriormente |
| D11 | Recorte inicial para analista de carteira/crédito: saldo, evolução da inadimplência, contribuição por segmento e comparação de safras em mesma idade | Aceite da proposta inicial em 04/11/2026; fórmulas e critérios de cálculo ainda dependem de revisão |
| D12 | Combinar dados sintéticos, públicos e reais | Confirmado em 04/11/2026; preservar origem e granularidade; integração de base real depende de disponibilidade e condições de utilização |
| D13 | Over90 inclui atrasos a partir de 90 dias, inclusive | Confirmado pelo autor em 04/11/2026: `dias_atraso >= 90`; 89 dias fica fora, 90 e 91 dias entram. Demais componentes da métrica continuam em revisão |
| D14 | Todos os indicadores Over usam limiar inclusivo | Confirmado em 04/11/2026: OverN enquadra `dias_atraso >= N`; aplicar a mesma convenção aos demais limiares, preservando as definições originais de fontes externas |
| D15 | Repositório `banking-analytics-assistant` público | Destino confirmado pelo autor: `Henri-fernandes/banking-analytics-assistant`; código enviado e verificado na `main` em 05/11/2026; deploy da aplicação ainda pendente |
| D16 | Remover a implementação anterior e recomeçar por partes | Confirmado em 10/11/2026; preservar decisões/pesquisa e histórico do Git. A próxima parte é especificar fontes e perguntas do recorte, antes de nova implementação |

## Escopo desejado, com detalhamento pendente

Os domínios de concessão, safras/MOB/bads, carteira, saldo devedor, inadimplência/overs/WO, PD, provisão/PDD, renegociação, reestruturação, DRE, RAROC e liquidez pertencem ao escopo desejado. O [escopo de negócio](escopo-negocio.md) descreve as dependências propostas e as definições ainda necessárias. Nenhuma fórmula ou regra de produto foi aprovada apenas por mencionar esses termos.

O autor deseja contexto, RAG, embeddings, banco vetorial, ferramentas, agente, saída estruturada, streaming, guardrails, cache, fallback, avaliações e observabilidade. Fine-tuning é um experimento desejado com utilidade mensurável; MCP é opcional. Ele esclareceu que não é obrigatório colocar tudo na primeira entrega: a prioridade é qualidade e relevância demonstrável.

Gráficos, tabelas, SQL exibido e exportações CSV/Excel/PDF são desejados. A interface e o nível de personalização continuam abertos.

## Propostas que continuam em avaliação

- A abordagem híbrida está confirmada; fontes específicas, disponibilidade de base real, uso de Faker e regras da geração sintética continuam em definição.
- Groq/Gemini, Streamlit/Render, Hugging Face e Supabase são candidatos, não decisões.
- Databricks pode ser avaliado para preparação/orquestração ou comparação futura. Seu uso e PySpark não são dependências impostas à execução pública.
- Tipo de PD, método de provisão, simulação de capital e métricas de liquidez ainda não foram definidos. Consultá-los no assistente não aprova automaticamente novos projetos de modelagem.
- Nome do banco, volume, histórico, jurisdição e metas de qualidade seguem em aberto. Os dois produtos iniciais estão confirmados; produtos adicionais serão definidos depois.

## Retomada em 04/11/2026

O autor autorizou começar pelo recorte proposto e informou que outros produtos serão adicionados depois. Ao discutir a origem dos dados, escolheu combinar todas as fontes sugeridas: sintéticas, públicas e reais.

A [especificação da primeira entrega](superpowers/specs/2026-11-04-primeira-entrega-design.md) foi aceita como base para avançar, com a correção de que todos os Overs incluem o próprio limiar. O autor autorizou a execução do [plano](superpowers/plans/2026-11-04-prova-conversacional-nuvem.md) pelo agente principal nesta sessão.

A prova foi implementada localmente com Python 3.12.16, Streamlit 1.66.0, SQLite reconstruível, três cenários sintéticos e referência pública SGS 21114. Os adaptadores Groq/Gemini foram testados com respostas controladas; nenhuma inferência real foi realizada. A [avaliação](avaliacoes/prova-inicial.md) registra 37 testes passando e as limitações. As regras efetivamente usadas estão no [contrato versionado](metricas/carteira-v1-inclusive.md).

O autor informou que o repositório GitHub de destino ainda não existe. Nenhum repositório remoto, push ou deploy foi criado. Hospedagem, plano gratuito de inferência e prova com PC desligado permanecem pendentes. Não confundir a stack implementada na prova com uma escolha definitiva de fornecedores para todas as etapas.

## Retomada em 05/11/2026

O autor forneceu o [repositório público](https://github.com/Henri-fernandes/banking-analytics-assistant) e autorizou continuar. A criação remota foi verificada; o Git local já está inicializado na branch `main`, inicialmente sem commits e sem remote configurado. A conta disponível nas integrações de GitHub não tem permissão de escrita nesse destino. A autenticação de `Henri-fernandes` foi solicitada, sem solicitar senha ou token pela conversa. A preparação do primeiro commit pode prosseguir sem publicar por outra conta.

O `origin` foi configurado, os 37 testes passaram novamente e os 46 arquivos revisados foram registrados no commit inicial local `0a218e6`. A autoria usa o nome da conta de destino e seu email público noreply; isso não altera a autenticação. A verificação da API ainda informa ausência de permissão de escrita para a conta autenticada. Nenhum push foi executado.

Após o autor concluir o login, a API confirmou `Henri-fernandes` com permissão de escrita. O primeiro push foi executado sem force, criando `main` no remoto; a API retornou o mesmo SHA local `a4681ad3bed282e55591620e0d3f69bf9f783082`. Autenticação e envio do código estão concluídos. Hospedagem, chave de inferência e prova com PC desligado continuam pendentes.

O histórico anterior registra o estado da época; para a situação do envio, consulte [próximos passos](proximos-passos.md).

## Referências em vídeo e limite da evidência

Em 09/11/2026, o autor reafirmou que a entrega é um chat interno capaz de consultar dados, arquivos e regras, com RAG, agente e guardrails. Confirmou a prioridade de construir a base de dados e o corpus de regras/documentos antes de integrar o agente. O painel e os cenários de teste existentes não satisfazem essa entrega. O próximo foco deixa de ser apenas habilitar inferência/publicação da prova e passa a ser a preparação dessas fontes e sua validação.

O autor também forneceu a [aula de agentes RAG da Hashtag Programação](https://www.youtube.com/watch?v=XqG3RN6VzDw&t=6274s) como referência da experiência desejada, com complexidade adicional no nosso projeto. A análise e a comparação por componente estão em [estado e referência RAG](avaliacoes/estado-e-referencia-rag.md). O vídeo não impõe ferramentas ou fornecedores.

Durante a publicação, o autor enviou uma captura da aplicação no Community Cloud, mostrando o cenário de variação de 30% para 40% e aviso de IA desabilitada. Isso evidencia a interface carregada pelo autor; sem URL fornecida, não comprova acesso público independente ou atendimento completo na nuvem.

O autor forneceu os vídeos [Erick Wendel](https://www.instagram.com/p/DcqwbZ2gGHs/) e [Beer and Code](https://www.instagram.com/reel/DfFO_r1IPLB/). Foram processados com a habilidade watch e analisados visualmente. Não havia legendas disponíveis e a fala não foi transcrita.

O segundo vídeo apresenta visualmente componentes de uma aplicação/agente, incluindo contexto, recuperação, ferramentas, saída estruturada, avaliações e tracing. Os vídeos são referências conceituais, sem obrigação de copiar a arquitetura. Sua análise não comprova detalhes de fala ou de implementação não visíveis.

## Como continuar

Use [próximos passos](proximos-passos.md) para retomar a definição. Atualize este registro quando houver decisão nova; preserve nos ADRs o motivo de escolhas arquiteturais relevantes. A solicitação que gerou este pacote foi documentar contexto, regras e direção para o Codex, não implementar a aplicação inteira nesta etapa.
