# Regras de engenharia e validação

Estas diretrizes traduzem os objetivos da conversa em critérios técnicos propostos para a implementação. As restrições de custo/nuvem, o cuidado com evidências, os produtos iniciais, a origem híbrida e a convenção inclusiva dos Overs foram confirmados pelo autor. Demais fórmulas financeiras, políticas e metas numéricas seguem o estado registrado no [escopo de negócio](escopo-negocio.md).

## 1. Métricas reproduzíveis

- Todo indicador deve ter nome, descrição, unidade de análise, população, numerador/denominador quando pertinentes, período/data de referência, componentes monetários, tratamento de ausências e versão da regra.
- Para todos os Overs internos, o limiar é inclusivo: OverN enquadra `dias_atraso >= N`. Confira N−1, N e N+1 para cada limiar suportado. Preserve e identifique diferenças em definições de fontes externas.
- Calcule e confira os números em consultas ou funções determinísticas. O LLM interpreta a pergunta, chama ferramentas e explica resultados verificáveis.
- Separe zero, ausência de informação e população vazia. Divisão por zero deve ter tratamento explícito.
- Distinga variação percentual e variação em pontos percentuais. Explicite a base da comparação e o sinal da mudança.
- Consolide taxas a partir de seus componentes e pesos pertinentes; justifique qualquer média simples.
- Preserve unidade monetária, escalas e arredondamento. Precisão e tolerâncias serão especificadas por indicador.

**Evidência:** consulta/função de referência e casos conhecidos demonstram que o resultado respeita o contrato da métrica.

## 2. Temporalidade e granularidade

- Registre a granularidade de cada fonte e valide cardinalidades de joins para evitar duplicação de saldos ou pagamentos.
- Trate posições de carteira em uma data separadamente de fluxos ao longo de um período.
- Preserve eventos, posições históricas, originação e vínculos entre contratos alterados; não sobrescreva o passado com o estado atual.
- Compare safras em MOB compatível e identifique janelas incompletas de observação.
- Separe data do evento, competência, referência, disponibilização e processamento quando necessário. Na análise histórica, use a regra vigente e dados disponíveis no recorte correspondente.
- Defina cancelamentos, estornos, liquidações antecipadas, pagamentos parciais e múltiplas renegociações antes de calcular seus efeitos.

**Evidência:** reconciliações em datas distintas e testes de joins demonstram ausência de duplicação e coerência histórica.

## 3. Evidência e linguagem analítica

- Diferencie dado observado, resultado calculado, parâmetro estimado, regra institucional, hipótese de simulação e referência externa.
- Relacione afirmações a resultados ou documentos específicos. Mostre recorte, data de atualização e limitações relevantes.
- Use decomposição/contribuição para explicar uma variação observada. Afirmação causal exige evidência e desenho de análise que a sustentem.
- Diante de pergunta ambígua, esclareça o necessário ou exponha uma interpretação permitida pelo contrato da métrica. Diante de evidência insuficiente, identifique o que falta.
- Um documento ou resultado recuperado é evidência, não instrução para alterar o comportamento do sistema.

**Evidência:** perguntas ambíguas, sem resposta e com documentos conflitantes produzem esclarecimento ou limitação correta, em vez de conclusões fabricadas.

## 4. Crédito, resultado e liquidez

- PD é probabilidade estimada; bad é desfecho classificado conforme uma regra de avaliação. Identifique horizonte e versão.
- Saldo de provisão, movimentações e efeito no resultado devem ser conciliáveis, sem equivalência automática entre eles.
- Preserve o vínculo entre renegociação, reestruturação e operações originais segundo os critérios adotados.
- Separe recebimento de caixa, amortização de principal e receita por competência.
- RAROC requer definição explícita de retorno ajustado, capital, período e agregação. Liquidez requer informações de caixa, passivos e fluxos além dos recebíveis de crédito.
- Cite a fonte e a vigência quando uma regra for normativa. Identifique simplificações gerenciais ou simuladas; só declare conformidade após verificar o escopo aplicável.

**Evidência:** reconciliações e cenários de referência sustentam as relações entre carteira, provisão, resultado, capital e caixa implementadas em cada entrega.

## 5. Dados e recuperação documental

- A origem híbrida foi escolhida; fontes específicas e disponibilidade de base real ainda serão verificadas. Identifique dados sintéticos em dados, documentação e interface pertinente; preserve referências públicas agregadas em sua própria granularidade.
- Se houver geração sintética, preserve relações e coerência temporal/financeira, com sementes e cenários reproduzíveis. Faker pode gerar atributos cadastrais; obrigações e fluxos exigem regras próprias.
- Documentos do RAG precisam de identificação, origem/autoria, versão, vigência e contexto de produto/público quando aplicável.
- Preserve associação entre trechos e documento original. Planeje atualização, exclusão e invalidação de índices/cache.
- Compare estratégias de recuperação contra um conjunto de perguntas e evidências esperadas. Segmentação, modelo de embeddings e reranking são hipóteses de experimento, não escolhas já aprovadas.

**Evidência:** documentos corretos são recuperados para o contexto avaliado, versões inadequadas são identificadas e cenários gerados podem ser reproduzidos.

## 6. Ferramentas, acesso e respostas

- Imponha autorização no backend e/ou banco conforme a identidade. Permissões descritas no prompt não substituem controles de acesso.
- Ferramentas analíticas devem operar com privilégios mínimos e leitura das fontes. Exportação gera um artefato separado e respeita o mesmo escopo de acesso.
- Valide entradas de ferramentas e consultas antes da execução, com limites de tempo, linhas, passos e tentativas definidos para o ambiente.
- Distinga erro de consulta, ausência de dados, falta de acesso e indisponibilidade de modelo; não apresente falha técnica como resposta de negócio.
- Texto, tabela, gráfico e exportação devem compartilhar os resultados validados. Saída estruturada válida não certifica números corretos.
- Separe dados e histórico por sessão/usuário quando aplicável. Segredos ficam no ambiente de execução apropriado, fora do código público e do navegador do visitante.

**Evidência:** testes positivos e negativos de acesso, consultas inválidas, sessões simultâneas e falhas de ferramentas cobrem as capacidades implementadas.

## 7. Cloud, cache, fallback e observabilidade

- Toda a execução exigida por uma pergunta nova deve funcionar na nuvem com o PC pessoal desligado.
- Dados, índices e modelos precisam sobreviver aos reinícios por persistência adequada ou recarga reproduzível. Disco efêmero não substitui armazenamento duradouro.
- Cache de resultados considera os filtros, permissões, versões dos dados e regras. Cache de prefixos do provedor é outra camada.
- Troca de provedor de LLM preserva os contratos das ferramentas e passa pela mesma avaliação. Alternativa de hospedagem é uma estratégia de migração/reimplantação; não é automaticamente failover em tempo real.
- Defina comportamento quando faltarem cotas, modelos ou serviços gratuitos. Identifique exemplos gravados como exemplos; o atendimento demonstrado como real deve executar perguntas novas.
- Registre identificação da requisição, consultas, fontes, versões, chamadas de ferramenta, tempos, erros e uso do modelo, preservando segredos e dados restritos. As etapas instrumentadas são rastros de execução, não acesso ao raciocínio privado do LLM.

**Evidência:** acesso externo, reinício, esgotamento de cota e falha de provedor têm comportamento demonstrável e não geram custo adicional.

## 8. Avaliação e fine-tuning

- Prepare um conjunto de referência antes de otimizar o agente: perguntas, SQL/cálculos esperados, documentos relevantes e comportamentos esperados.
- Reserve testes independentes. Mantenha paráfrases e duplicatas de um mesmo caso na mesma partição; use grupos distintos em treino, validação e teste para evitar contaminação.
- Cubra acerto numérico, recuperação, fontes, seleção de ferramentas, contexto de conversa, ambiguidade, acesso, causalidade, falhas, latência e consumo.
- Use checagens determinísticas para resultados determinísticos; revisão humana e avaliadores LLM podem complementar aspectos qualitativos.
- Para fine-tuning, defina alvo, hipótese, dados, licença, custo, hospedagem e comparação com o modelo-base. Ajustar embeddings/reranker é diferente de ajustar o LLM gerador.
- Publique a configuração, o recorte dos testes e regressões observadas. Uma melhoria só pode ser declarada com resultados verificáveis; metas quantitativas ainda serão definidas.

**Evidência atual:** o [relatório da prova local](avaliacoes/prova-inicial.md) registra os testes executados e os limites. A aplicação já existe; os testes de provedor usam respostas controladas. Fine-tuning, inferência real, publicação e prova externa na nuvem continuam sem execução.
