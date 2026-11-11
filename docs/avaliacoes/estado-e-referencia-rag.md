> Histórico: a implementação descrita foi retirada em 10/11/2026. Este documento não descreve a versão atual; consulte o [recomeço](../reinicio.md).

# Estado do projeto e referência de experiência

Data: 09/11/2026. Inspeção do código em `afc1077`, dos documentos e das capturas fornecidas pelo autor. Nenhum teste da aplicação ou chamada de LLM foi reexecutado nesta análise.

## Objetivo confirmado

O produto é um assistente interno em formato de chat que consulta dados, arquivos e regras da instituição, combina evidências e mantém o contexto dos aprofundamentos. O painel atual é uma prova de ferramentas analíticas. O autor confirmou a prioridade de preparar dados e documentos antes de integrar RAG e agente; guardrails fazem parte do resultado desejado.

## Onde estamos

| Parte | Evidência atual | O que falta |
|---|---|---|
| Dados | Três cenários independentes, 13 contratos de teste e reconstrução em SQLite; 24 observações públicas separadas | Base coerente com maior histórico e variedade, cadastros e eventos; ingestão reproduzível e dicionário; base real depende de disponibilidade |
| Regras | Documento versionado das quatro análises e convenção OverN inclusiva | Corpus de políticas, procedimentos e produtos, com origem, versão, vigência e casos esperados; políticas fictícias devem ser identificadas |
| Ferramentas | Saldo, evolução, contribuição e safras em SQL definido pela aplicação | Ampliação conforme perguntas e dados; combinação de resultados com evidências documentais |
| Recuperação | Seleção fixa de seção do documento conforme a análise | Ingestão e busca documental por pergunta, associação às fontes e avaliação; embeddings e índice vetorial não existem no código |
| Conversa | Intenção estruturada, filtros por sessão e respostas por modelos de texto fixos | Chat principal, busca e consultas coordenadas, resposta fundamentada nas duas fontes e esclarecimentos contextualizados |
| LLM | Adaptadores Groq/Gemini testados com respostas controladas | Chamada real, elegibilidade gratuita e comportamento na conta ainda sem evidência |
| Guardrails | Validação de filtros, SQL parametrizado e somente leitura, limites de chamadas, tempo e linhas, separação de sessões e erros | Autorização por identidade, filtragem de documentos/dados por acesso, testes de injeção, verificação de evidências e integração dos controles ao agente |
| Publicação | Código no GitHub e captura do autor mostrando a interface após o deploy no Community Cloud | URL não fornecida; acesso público independente, inferência, reinício e prova com PC desligado não verificados |

Os 37 testes são evidência histórica das ferramentas e da prova local, registrada na avaliação inicial e na preparação do GitHub; não significam que o assistente completo foi testado.

## Referência fornecida pelo autor

[Aula Completaça de Agentes RAG com tudo o que você precisa — Hashtag Programação](https://www.youtube.com/watch?v=XqG3RN6VzDw), duração de aproximadamente 1h56min32s.

Análise com a habilidade watch, em modo local: metadados/capítulos, legendas automáticas em português de proveniência não certificada e dez quadros entre 1h44min34s e 1h54min34s. Foram lidos trechos das legendas da apresentação, explicação do RAG, recuperação e teste final. Não houve revisão visual contínua das quase duas horas nem uso de inferência paga. Artefatos temporários ficaram fora do versionamento em `.superpowers/watch/`.

- [00:33–02:11](https://www.youtube.com/watch?v=XqG3RN6VzDw&t=33s): apresenta um chat que responde sobre políticas internas de RH.
- [1:44:34 em diante](https://www.youtube.com/watch?v=XqG3RN6VzDw&t=6274s): explica recuperação de trechos. Nas telas amostradas aparecem carregamento de PDF, divisão em blocos, embeddings, FAISS, retriever, prompt e modelo.
- [1:49:33–1:52:21](https://www.youtube.com/watch?v=XqG3RN6VzDw&t=6573s): as legendas descrevem o teste; uma continuação curta não encontra resposta. Histórico exibido na interface não comprova resolução correta do contexto pela recuperação.
- [1:53 aproximadamente](https://www.youtube.com/watch?v=XqG3RN6VzDw&t=6780s): discussão de aplicações e riscos, incluindo injeção de instruções. Isso não comprova controles implementados ou testados.

A experiência do vídeo esclarece o objetivo; não aprova sua stack nem certifica produção. O fluxo observado é principalmente uma cadeia de recuperação documental e geração. Nosso objetivo acrescenta ferramentas analíticas, combinação das duas fontes e controles verificáveis. RAG busca evidências documentais; cálculos continuam nas ferramentas determinísticas; o agente coordena as etapas permitidas.

## Sequência de continuidade

Prioridade confirmada: dados e regras/documentos antes da integração do agente. Proposta de execução por recortes:

1. Definir perguntas de aceitação do primeiro recorte PF/PJ e seus resultados/fontes esperados.
2. Estruturar e gerar uma base sintética coerente; manter referências públicas separadas e não depender de uma base privada inexistente.
3. Preparar corpus e contratos das métricas, distinguindo decisões do autor, propostas e políticas fictícias.
4. Validar consultas e recuperação documental separadamente.
5. Integrar chat, ferramentas e recuperação; aplicar guardrails desde o acesso às fontes e ferramentas, antes da resposta.
6. Avaliar respostas, contexto, acesso, falhas e consumo; verificar execução integral na nuvem.

Essa sequência não constitui uma nova implementação concluída. Volume, período, regras financeiras adicionais e metas de qualidade ainda precisam de especificação.
