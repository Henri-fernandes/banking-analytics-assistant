**Databricks Genie Agents ou aplicação própria: análise para o portfólio**

> Cópia histórica da pesquisa de 30/10/2026. Para decisões atuais, consulte a [versão mantida em docs/pesquisas, com revalidação de 04/11/2026](docs/pesquisas/comparacao-genie-agents-aplicacao-propria.md#revalidação-dos-candidatos-em-04112026).

Pesquisa documental verificada em 30/10/2026. Fontes primárias oficiais. Nenhum workspace, provedor ou modelo foi submetido a benchmark nesta análise. Recursos podem variar por edição, região, modelo e configuração da conta. Opiniões de adequação estão identificadas como avaliação.

**Conclusão para este projeto:** a aplicação própria é a candidata mais alinhada à combinação de acesso público, controle do backend de IA e custo adicional zero. O Genie oferece uma solução pronta de analytics conversacional com governança, mas a viabilidade de uma demonstração pública e gratuita por tempo indeterminado ainda exige confirmação. Esta recomendação é uma avaliação arquitetural; não comprova maior acurácia ou preferência de recrutadores.

Comparamos o produto gerenciado Genie Agents com uma aplicação cujo fluxo, recuperação, ferramentas e interface seriam desenvolvidos por nós. Construir um agente personalizado usando Model Serving do Databricks é outra arquitetura, que não herda automaticamente todas as características do Genie.

O usuário quer um assistente interno simulado, capaz de responder sobre carteira, filiais, inadimplência e seus desdobramentos, com gráficos, tabelas, evidências e exportações. O sistema publicado deve funcionar com o computador pessoal desligado. Desenvolvimento e treinamento podem ocorrer localmente.

| Critério | Genie Agents | Aplicação própria |
|---|---|---|
| Primeira experiência funcional | Interface, consultas, contexto e visualizações já fornecidos | Precisamos integrar esses componentes |
| Trabalho que fica mais visível | SQL, semântica, curadoria, governança e avaliação no Databricks | Engenharia de dados, recuperação, ferramentas, agente, avaliação e operação |
| Link aberto para visitantes | Interface nativa/incorporada exige identidade e permissões Databricks | Pode ser publicado sem conta do provedor para o visitante |
| Interface própria | Possível via API; autenticação e condições de uso continuam necessárias | Controle sobre a experiência dentro das capacidades do framework escolhido |
| Modelos | Sistema gerenciado pelo produto | Escolha entre modelos e provedores compatíveis |
| Fine-tuning | Não é um controle documentado de configuração do Genie | Pode integrar modelos ajustados se houver hospedagem viável |
| Recuperação documental | Recursos gerenciados; fontes e modos têm requisitos | Escolha explícita de segmentação, embeddings, índice e reranking |
| Segurança por usuário | Integração com Unity Catalog | Implementação e validação sob nossa responsabilidade |
| Avaliação | Benchmarks e monitoramento nativos | Avaliação personalizada, que precisamos construir |
| Versionamento | API e configuração serializada | Código, dados e configurações versionáveis; execução depende de serviços |
| Custo zero | Free Edition com cotas; acesso público via API ainda a confirmar | Viável como candidata com serviços gratuitos, sujeito a cotas e testes |
| Operação | Menos componentes de aplicação sob nossa gestão | Mais controle e mais trabalho de manutenção |

As implicações arquiteturais da tabela são explicadas e fundamentadas abaixo.

**O que o Genie já entrega e por que isso é uma vantagem real**

Genie Agents gera SQL, tabelas e visualizações sobre fontes selecionadas do Unity Catalog. A configuração usa semântica e exemplos fornecidos pelos autores. O Chat mode atende perguntas estruturadas; o Agent mode permite investigações com múltiplas consultas e fontes adicionais. Portanto, uma pergunta sobre a evolução da inadimplência e seu aprofundamento são compatíveis com a proposta do produto, sujeitos à qualidade da base e da configuração. [Conceitos oficiais](https://docs.databricks.com/aws/en/genie-agents/concepts).

O benefício prático é aproveitar componentes já entregues e dedicar trabalho a indicadores, relacionamentos, regras e exemplos corretos. A expectativa de reduzir código de aplicação decorre desse escopo pronto; não estimamos dias de desenvolvimento nem garantimos qualidade superior.

O agente usa fontes explicitamente anexadas e respeita as permissões dos usuários sobre os dados. Preparar uma base com descrições, instruções e exemplos continua sendo responsabilidade do autor. Isso é especialmente útil para demonstrar modelagem e governança. Recursos empresariais não devem ser presumidos disponíveis na Free Edition. [Configuração e permissões](https://docs.databricks.com/aws/en/genie-agents/set-up).

O Genie também já oferece exportação CSV de resultados, PNG de visualizações e PDF de relatórios do Agent mode. Não encontramos confirmação de exportação nativa de workbook XLSX formatado nas páginas consultadas; isso não prova impossibilidade por outras integrações. [Uso e exportações](https://docs.databricks.com/aws/en/genie-agents/talk-to-genie), [ações sobre resultados](https://docs.databricks.com/aws/en/genie-agents/monitor).

**Acesso público: a diferença mais importante para a demonstração**

Incorporar o Genie por iframe em um site preserva a necessidade de login Databricks e de acesso explícito ao agente e aos dados. Hospedar esse iframe em um site público não elimina tais condições. [Requisitos de incorporação](https://docs.databricks.com/aws/en/genie-agents/embed).

Databricks Apps declara que acesso anônimo não é suportado. Externos podem receber identidades e permissões, o que constitui outra experiência de distribuição. [Permissões de Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/permissions).

É possível construir uma interface externa sobre a API do Genie. A documentação prevê autenticação de usuário e de service principal, além de APIs de Chat, Agent mode e gerenciamento. Isso demonstra possibilidade de integração; não demonstra que um backend público com credencial de serviço terá todas as capacidades disponíveis gratuitamente na Free Edition. Uma credencial compartilhada também não preserva automaticamente as identidades individuais dos visitantes. [API e autenticação](https://docs.databricks.com/aws/en/genie-agents/conversation-api).

Na aplicação própria, a política de acesso da demonstração fica sob nosso controle. Streamlit Community Cloud permite publicar um aplicativo público acessível por URL. Podemos ainda representar perfis de analistas fictícios; qualquer regra de acesso precisa ser implementada no backend. [Compartilhamento público no Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

OpenSharing oferece outra forma de distribuição de Genie Agents, mas trabalha com snapshots e destinatários que montam um agente; não equivale a publicar um chat anônimo. [OpenSharing](https://docs.databricks.com/aws/en/opensharing/share-genie-agent).

**Gratuidade: separar Free Edition, promoção e serviços externos**

A Free Edition é uma oferta sem custo e sujeita a cotas. O excesso pode interromper compute até a reposição da cota. Não há SLA. Databricks Apps nessa edição para após até 24 horas de início, atualização ou implantação e pode ser reiniciado. São limitações concretas para uma demonstração acessada espontaneamente. A parada dos Apps não deve ser extrapolada para afirmar que todo endpoint Genie para a cada 24 horas. [Limitações da Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).

Em outro contexto, a documentação comercial informa promoção de uso de Genie One e Agents por usuários até 31/01/2027, excluindo service principals. Em contas comerciais, compute de SQL e uso de LLM são cobranças separadas; budgets são aproximados, sem garantia de teto absoluto. Essas regras não estabelecem cobrança automática futura na Free Edition. [Genie e promoção](https://docs.databricks.com/aws/en/genie/), [budgets e compute](https://docs.databricks.com/aws/en/genie/budgets).

A aplicação própria também tem limites. Groq possui cotas por requisições e tokens compartilhadas pela organização, que podem ser consumidas por várias chamadas de uma única pergunta. Gemini oferece camada gratuita para modelos elegíveis. Ter duas opções exige testes de compatibilidade e controle de consumo; não garante disponibilidade contínua. [Cotas Groq](https://console.groq.com/docs/rate-limits), [preços Gemini](https://ai.google.dev/gemini-api/docs/pricing).

Streamlit hiberna após 12 horas sem tráfego; qualquer visitante autorizado pode solicitar sua reativação. Seus recursos de memória e CPU são limitados. [Hospedagem e hibernação](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app).

Render Free suspende o processo após 15 minutos sem tráfego e o reativa no acesso seguinte. Arquivos modificados no disco do serviço são efêmeros; seu PostgreSQL gratuito expira em 30 dias. Uma implantação nessa opção precisa recuperar seus artefatos e escolher persistência adequada. [Limites Render](https://render.com/docs/free).

Conclusão factual: as duas rotas podem operar sem o computador pessoal ligado. Nenhuma das ofertas gratuitas consultadas sustenta promessa de uso público ilimitado ou disponibilidade garantida.

**Fine-tuning: a etapa de treinamento precisa incluir uma decisão de hospedagem**

As configurações documentadas de Genie expõem fontes, descrições, sinônimos, relacionamentos, regras, exemplos e testes. Não encontramos controles para treinar os pesos do modelo gerenciado ou selecionar livremente embeddings, chunking e mecanismo vetorial. Configurar o contexto não deve ser apresentado no portfólio como fine-tuning. [Configuração do Genie](https://docs.databricks.com/aws/en/genie-agents/set-up).

Em uma aplicação própria podemos integrar modelos ajustados, respeitando capacidade e compatibilidade do serviço. Um fato que limita a proposta inicial: hospedar adapters LoRA próprios na Groq é um recurso Enterprise; o Free Plan não resolve esse requisito. O treinamento também é realizado fora da Groq. [LoRA na Groq](https://console.groq.com/docs/lora).

Hugging Face ZeroGPU é uma possibilidade gratuita para modelos próprios, condicionada a elegibilidade da conta e compatibilidade Gradio. A documentação informa cotas diárias de 2 minutos para visitantes sem autenticação e 5 minutos para contas gratuitas, além de filas. Isso pode limitar conversas analíticas longas. [ZeroGPU](https://huggingface.co/docs/hub/main/spaces-zerogpu).

A alternativa de ajustar um embedding ou reranker menor pode ser estudada separadamente. É treinamento de um componente de recuperação, não fine-tuning do LLM de geração. A documentação do Sentence Transformers descreve treinamento e avaliações de recuperação. Hospedar o artefato no orçamento e na memória da aplicação ainda exige teste. [Treinamento de embeddings](https://www.sbert.net/docs/sentence_transformer/training_overview.html).

**Controle técnico: vantagem e responsabilidade da aplicação própria**

Na aplicação própria controlamos os componentes que implementamos: seleção de contexto, segmentação documental, embeddings, filtros, recuperação, reranking, ferramentas, limites de passos, validação de consultas, formato de resposta, cache de resultados e política de fallback. A infraestrutura e o comportamento interno de um LLM de terceiros continuam fora do nosso controle. Usar bibliotecas e APIs prontas é compatível com essa arquitetura.

Esse controle permite experimentos comparáveis: recuperação lexical versus vetorial versus híbrida; modelos diferentes; configuração de contexto; treinamento antes/depois. Não garante melhorias. É necessário preservar perguntas de teste independentes e avaliar regressões.

Uma restrição de integração concreta: a documentação atual da Groq informa que Structured Outputs não suporta streaming nem tool use na mesma chamada. Podemos organizar etapas separadas, mas isso acrescenta desenho e testes. JSON válido também não certifica a correção dos valores financeiros. [Structured Outputs](https://console.groq.com/docs/structured-outputs).

Prompt caching do provedor e cache de resultados da aplicação são coisas diferentes. O primeiro reutiliza processamento de prefixos em modelos suportados. O segundo precisa considerar dados, permissões, filtros e validade temporal; será responsabilidade nossa. [Prompt caching Groq](https://console.groq.com/docs/prompt-caching).

**Avaliação, observabilidade e versionamento**

Genie fornece benchmarks, monitoramento e feedback. Seus benchmarks iniciam conversas novas; portanto, não comprovam por si só a continuidade das conversas de aprofundamento. Precisamos testar interações como "e nas outras filiais?" em qualquer uma das rotas. [Avaliação do Genie](https://docs.databricks.com/aws/en/genie-agents/monitor).

Genie também possui configuração serializada e APIs de gerenciamento para CI/CD. Seria incorreto afirmar que não pode ser versionado. O motor de execução continua pertencendo à plataforma. [Management APIs](https://docs.databricks.com/aws/en/genie-agents/conversation-api).

Na aplicação própria podemos instrumentar as etapas que implementamos. MLflow Tracing, por exemplo, registra entradas, saídas, metadados, latência e uso de tokens e é compatível com OpenTelemetry. Hospedagem e persistência dessa telemetria precisam entrar no desenho de custo zero. [MLflow Tracing](https://mlflow.org/docs/latest/genai/tracing/).

Segurança tem o mesmo sentido de responsabilidade: permissões Unity Catalog são uma vantagem concreta do caminho nativo; na aplicação própria, filtros por usuário, acesso de leitura, validação e limites de ferramentas precisam ser impostos no backend/banco e testados. Instruções de prompt não substituem autorização. Não presumimos que todos os controles comerciais estejam disponíveis na conta gratuita.

**O que cada opção evidencia no portfólio — avaliação, não estatística de contratação**

Genie favorece uma demonstração centrada em Databricks, modelagem, SQL, semântica, governança, preparação de dados e curadoria de analytics conversacional. Pode ser um excelente projeto se esse for o objetivo e a forma de acesso for adequada.

A aplicação própria favorece evidências de engenharia de IA: código de recuperação e orquestração, decisões sobre modelos, ferramentas, contratos de saída, experimentos, fallback, instrumentação e experiência web. Também oferece um caminho mais direto para uma demonstração pública. Exige mais integração e manutenção, e isso pode atrasar uma entrega se o escopo for grande.

Não encontramos evidência para afirmar que recrutadores preferem uma arquitetura, nem que Genie ou um backend próprio terá maior acurácia ou menor latência nessa base. Qualidade precisa de comparação com o mesmo conjunto de perguntas, dados e métricas.

**Recomendação para os requisitos declarados**

Priorizar uma aplicação própria como entrega principal. Os motivos são acesso por terceiros, controle dos componentes que o usuário deseja demonstrar e possibilidade de escolher serviços gratuitos substituíveis. O fine-tuning permanece um experimento com alvo e hospedagem a comprovar, não uma capacidade gratuita garantida.

Genie pode ser uma alternativa muito adequada para uso com identidades Databricks ou uma implementação comparativa posterior sobre a mesma amostra e os mesmos indicadores. Não é necessário construir duas aplicações completas de início.

Antes de fechar a arquitetura, comprovar:

1. Acesso de um visitante real sem depender do PC do autor.
2. Consulta e resposta sobre pergunta nova, não apenas resultados gravados.
3. Correção numérica e temporal contra SQL de referência.
4. Continuidade em conversas, ambiguidade e insuficiência de informação.
5. Negação de acesso fora do perfil quando esse recurso for demonstrado.
6. Recuperação após reinício e identificação de dados desatualizados.
7. Limites gratuitos e comportamento quando as cotas acabam.
8. Se houver fine-tuning, execução do artefato ajustado na nuvem e comparação com o modelo-base.

Esses itens são critérios propostos. Nenhum foi executado nesta pesquisa documental.
