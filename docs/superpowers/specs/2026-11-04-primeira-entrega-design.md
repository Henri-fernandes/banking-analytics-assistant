> Histórico: a implementação descrita foi retirada em 10/11/2026. Este documento não descreve a versão atual; consulte o [recomeço](../../reinicio.md).

# Primeira entrega — carteira de crédito PF e PJ

Data: 04/11/2026. Estado: execução autorizada e prova implementada localmente, com limiar inclusivo para todos os Overs. Inferência real e deploy ainda pendentes; consulte as [evidências](../../avaliacoes/prova-inicial.md).

## Objetivo e decisões confirmadas

Entregar um assistente de análise para um banco fictício que responda perguntas novas com números calculados, consultas rastreáveis, tabelas e gráficos. A aplicação publicada deve funcionar integralmente na nuvem, com o computador do autor desligado e sem custo adicional. Consulte as [decisões de continuidade](../../contexto-e-decisoes.md).

Começar com crédito pessoal parcelado PF e capital de giro parcelado PJ. O usuário inicial é o analista de carteira/crédito. Novos produtos serão adicionados posteriormente. Combinar dados sintéticos, públicos e reais, preservando suas origens e níveis de agregação.

Produtos, perguntas, abordagem híbrida e limiar inclusivo de todos os Overs (`dias_atraso >= N`) estão confirmados. Os demais componentes dos contratos de métricas, os volumes, o histórico e o desenho abaixo orientam a proposta de implementação. A escolha híbrida não significa que já existe uma base real disponível.

## Alternativas de execução consideradas

| Caminho | Benefício | Limite |
|---|---|---|
| Núcleo sintético reproduzível, referência pública separada e integração real quando disponível — recomendado | Permite verificar cálculos com cenários conhecidos e incorporar as três origens sem inventar observações | Uma comparação de mercado depende de compatibilidade de definições e cobertura |
| Começar por uma base real | Preserva eventos observados de uma fonte específica | A base ainda não foi disponibilizada; campos e histórico podem não sustentar as perguntas |
| Começar apenas por agregados públicos | Oferece contexto observado do mercado | Não sustenta a cadeia individual cliente–contrato–parcela–pagamento do banco fictício |

Recomendação: desenvolver o núcleo com cenários sintéticos e manter referências públicas em tabelas próprias. Incorporar dados reais após conhecer o conteúdo e as condições de uso. Não condicionar a prova funcional inicial à entrega de uma base real.

## Perguntas e resultados esperados

| ID | Pergunta | Recorte | Entrega esperada |
|---|---|---|---|
| P01 | Qual o saldo por filial e produto? | Uma data mensal, PF/PJ, filial e produto | Total reconciliado, tabela por grupo, gráfico e consulta |
| P02 | Como evoluiu a inadimplência desta filial? | Intervalo mensal com os mesmos filtros | Numerador, denominador, taxa, evolução e variação em pontos percentuais |
| P03 | Quais segmentos contribuíram para a variação? | Duas datas e uma dimensão sem sobreposição, inicialmente produto | Contribuições aditivas reconciliadas com a variação total; descrição sem inferência causal |
| P04 | Como as safras se comparam na mesma idade? | Produto, filial, mês de originação e MOB | Curvas/tabela em MOB comum e identificação de janelas ainda não observadas |

O fluxo deve permitir perguntar P02 e depois “e em PJ?”, mantendo filial, período e regra, e registrando o filtro alterado. Sem contexto anterior suficiente, o assistente solicita o recorte necessário. Dimensões exclusivas de PF ou PJ serão usadas apenas no público compatível.

## Contratos de métricas propostos para revisão

O autor confirmou que a convenção vale para todos os Overs: OverN inclui atraso a partir de N dias, inclusive. As demais definições seguintes são simplificações gerenciais propostas para o banco fictício. Não constituem adoção de norma nem reprodução automática da metodologia de uma série pública.

| Tema | Proposta explícita |
|---|---|
| Moeda e precisão | BRL; valores de referência em centavos inteiros; taxas calculadas antes do arredondamento de exibição |
| Posição | Uma linha por contrato e data de referência; referência no último dia de cada mês; não somar posições de datas diferentes |
| Saldo principal | Principal concedido menos amortizações de principal efetivadas até a referência; incluir principal vencido e a vencer; separar juros, encargos e recebimentos não alocados |
| População | Contratos originados até a referência, com principal positivo e sem cancelamento ou baixa integral para prejuízo até aquela data |
| Atraso do contrato | Maior quantidade de dias corridos desde o vencimento entre parcelas com obrigação contratual ainda não integralmente paga na referência; vencimento na própria data conta zero dias; pagamento parcial preserva o vencimento do resíduo |
| Inadimplência inicial | Limiar confirmado: atraso maior ou igual a 90 dias (`dias_atraso >= 90`); 89 dias não entra, 90 e 91 dias entram. Proposta dos demais componentes: soma do principal dos contratos enquadrados dividida pela soma do principal elegível |
| Outros Overs | Aplicar `dias_atraso >= N` ao limiar solicitado, preservando população e componentes declarados. Over30 inclui 30 dias, Over60 inclui 60 dias; comparar indicadores com o mesmo limiar |
| População vazia | Taxa sem resultado, com explicação; nunca converter denominador zero em taxa zero |
| Safra e MOB | Safra = mês de originação; MOB = diferença entre meses-calendário; mês de originação é MOB 0; não exibir meses futuros como desempenho zero |
| Comparação de safras | Over90 na posição observada em cada MOB; não chamar esse resultado de bad acumulado ou PD |
| Variação | Taxa final menos inicial em pontos percentuais, sempre exibindo as duas bases |
| Ausências | Não inferir saldo ou atraso ausente como zero; excluir da métrica afetada, informar quantidade excluída e motivo; rejeitar duplicatas de contrato/data |

Para P03, em cada data t, definir N(g,t) como o saldo inadimplente do grupo e D(t) como o saldo elegível total do mesmo recorte. A contribuição do grupo em pontos percentuais é `100 × [N(g,t1)/D(t1) − N(g,t0)/D(t0)]`. A soma das contribuições deve ser igual à variação da taxa consolidada. Todos os grupos do recorte participam, inclusive categoria não informada; grupo comprovadamente sem operações em uma data tem numerador zero. Fonte ou posição ausente não equivale a grupo vazio. Se algum denominador for zero, não calcular a decomposição.

Essa contribuição combina mudanças do saldo inadimplente e da composição da carteira. Não identifica, por si só, causa econômica ou comportamento individual.

## Casos numéricos de referência propostos

Os números abaixo são exemplos construídos para validar regras, sem relação com dados reais ou públicos.

1. Quatro contratos elegíveis com principal de R$ 1.000, R$ 2.000, R$ 3.000 e R$ 4.000 e atrasos de 89, 90, 91 e 120 dias: saldo total R$ 10.000; numerador Over90 R$ 9.000; taxa 90%. O contrato com 89 dias fica fora do numerador; os contratos com 90, 91 e 120 dias entram, conforme o limiar inclusivo confirmado.
2. Carteira com saldo elegível e todos os contratos em dia: Over90 igual a 0%. Carteira sem saldo elegível: taxa sem resultado. Uma posição inexistente produz aviso de dado indisponível.
3. Na data inicial, saldo total R$ 1.000, inadimplente PF R$ 200 e PJ R$ 100: taxa 30%. Na data final, saldo total R$ 1.200, inadimplente PF R$ 300 e PJ R$ 180: taxa 40%. Contribuições: PF +5 p.p.; PJ +5 p.p.; total +10 p.p.
4. Originação em 15/01/2025: posição de 31/01/2025 em MOB 0 e posição de 28/02/2025 em MOB 1. Uma safra recente sem MOB 12 observado não recebe uma taxa inventada nesse MOB.
5. Duas parcelas de um contrato não podem duplicar o principal da posição ao juntar as fontes. Duplicata de contrato/data deve interromper a publicação daquela posição.
6. Para cada N suportado, verificar N−1 fora, N dentro e N+1 dentro. Exemplos: Over30 inclui 30 dias e exclui 29; Over60 inclui 60 e exclui 59. Limiar diferente deve constar da resposta e do contexto de continuação.

## Dados mínimos e rastreabilidade

| Informação | Granularidade e conteúdo mínimo |
|---|---|
| Origem | Identificador, classe sintética/pública/real, responsável, descrição, versão, obtenção, referência, condições de uso e checksum do arquivo |
| Produto | Código estável, nome, público elegível e versão das regras; dois registros iniciais |
| Cliente e filial | Identificadores internos, público PF/PJ e filial atribuída; usar somente atributos necessários às análises |
| Contrato | Identificador com namespace da origem, cliente, produto, filial, originação, principal concedido e eventos de status |
| Parcela | Contrato, identificador, vencimento, principal e demais componentes contratuais separados |
| Pagamento e alocação | Evento, data de efetivação, eventual estorno, parcela e valores separados por componente; recebimento e alocação têm granularidades distintas |
| Posição mensal | Contrato, referência, principal pendente, atraso, elegibilidade e versão do cálculo, reconciliados com eventos até a referência |
| Referência pública | Fonte/série, período, unidade, população, modalidade, definição, obtenção e valor publicado; tabela própria, sem vínculo inventado com cliente ou contrato |
| Documentação recuperável | Identificador do documento, título, origem, versão, vigência e trechos vinculados ao original |

Proposta de amostra inicial: 24 referências mensais de janeiro/2024 a dezembro/2025, cinco filiais fictícias e até 1.000 contratos no total dos dois produtos, com semente fixa. Esse tamanho é uma configuração de teste proposta, sem alegação de representatividade. Incluir contratos em dia, atrasos nas fronteiras, pagamentos parciais, liquidação e casos de população vazia. Um sistema de amortização e uma política de alocação completos ainda precisam ser definidos antes do gerador financeiro; os primeiros casos manuais devem declarar seus componentes explicitamente.

Renegociação, reestruturação, provisão, PD, baixa para prejuízo, DRE, RAROC e liquidez seguem no escopo futuro. A amostra inicial não simulará esses eventos; se uma fonte contiver contratos afetados, deverá identificar a situação e separá-los para revisão, em vez de presumir tratamento financeiro.

## Fontes híbridas e referência pública

Pesquisa inicial em fontes oficiais em 04/11/2026: o [SCR.data](https://www.bcb.gov.br/detalhenoticia/535/noticia) oferece visões de crédito por públicos e outros recortes. O [IF.data](https://www3.bcb.gov.br/ifdata/) publica relatórios com recortes PF/PJ e informações contábeis. Ambos são candidatos a referência agregada, com seleção de arquivo, período, metodologia e condições de uso ainda a verificar antes da carga.

O catálogo também identifica a [série SGS 21114](https://dadosabertos.bcb.gov.br/dataset/groups/21114-inadimplencia-da-carteira-de-credito-com-recursos-livres---pessoas-fisicas---credito-pessoal-) como inadimplência de crédito pessoal não consignado PF. É candidata, não uma equivalência aprovada com o produto fictício. A ficha da [série 21115](https://dadosabertos.bcb.gov.br/dataset/21115-inadimplencia-da-carteira-de-credito-com-recursos-livres---pessoas-fisicas---credito-pessoal-) corresponde especificamente à composição de dívidas, informa atraso superior a 90 dias e licença ODbL; não usar esse recorte como sinônimo de todo crédito pessoal nem estender sua licença a outras fontes sem checagem.

Não somar saldos públicos aos contratos fictícios. Comparação direta só deve ser habilitada após registrar compatibilidade de saldo, atraso, população, produto e período. Caso contrário, mostrar os números em contextos distintos e explicar a diferença de definição. Calibrar simulações por uma série pública não transforma contratos sintéticos em observações reais.

O limiar interno confirmado é `>= 90` dias. A descrição externa citada acima usa `> 90` dias; preservar a definição publicada da fonte e registrar essa diferença, sem apresentar as duas métricas como equivalentes.

Base real: nenhuma foi fornecida. Após identificar uma fonte, documentar campos, condições de utilização, cobertura e tratamento necessário para publicação. A demonstração pública inicial usará o núcleo sintético e apenas referências públicas cuja utilização tiver sido verificada. Não há autorização implícita para publicar registros privados.

## Fluxo técnico proposto, independente de fornecedor

1. Preparação: preservar arquivos de origem, validar chaves e datas, normalizar componentes e produzir posições e metadados reproduzíveis.
2. Consulta: receber intenção e filtros validados; executar ferramentas de leitura com consultas parametrizadas; calcular métricas de forma determinística. O modelo não calcula saldos a partir do texto.
3. Contexto documental: consultar regras da versão e da data aplicáveis. Começar com recuperação simples avaliável; embeddings e índice vetorial serão experimentos posteriores.
4. Resposta: texto, tabela e gráfico usam o mesmo resultado validado, com regra, fontes, data e consulta. Preservar filtros por sessão.
5. Operação: limitar chamadas, linhas e duração; registrar consultas, erros e consumo sem expor segredos. Esgotamento de cota deve interromper inferência e informar a limitação, sem contratar plano pago.

A stack não está aprovada. A escolha dos serviços requer atualização da pesquisa oficial e uma prova de consulta e resposta novas na nuvem. Consultas públicas devem usar snapshots versionados quando apropriado, com data de atualização visível; a ausência de API de origem não deve impedir a leitura de uma cópia já validada. Sem snapshot disponível, informar indisponibilidade da referência. Fonte real indisponível não bloqueia os casos sintéticos.

## Critérios de aceitação

- Produtos e origens identificados em cada resultado; nenhuma referência pública tratada como contrato do banco fictício.
- Casos monetários de referência exatos em centavos; taxas e contribuições conferidas antes da formatação, com tolerância de 0,000001 ponto percentual nas comparações computacionais.
- Fronteiras de todos os Overs suportados conferidas em N−1, N e N+1; no Over90: 89 dias fora, 90 e 91 dias dentro.
- Chaves, cardinalidades e posições reconciliadas; pagamentos posteriores à referência não alteram a resposta histórica anterior.
- P01 a P04 retornam consultas, filtros e versões das regras; texto, tabela e gráfico compartilham o resultado validado.
- Perguntas de continuação mantêm filtros; ambiguidade, ausência de dados, erro técnico e falta de cota produzem respostas distintas.
- Nenhum número é apresentado como PD, provisão ou resultado causal sem o contrato e a evidência correspondentes.
- Visitante executa uma pergunta nova com o computador pessoal desligado; reinício recompõe artefatos necessários e não perde sua identificação de versão.
- Planos gratuitos e alternativas de dependências críticas são documentados e testados; não declarar a prova na nuvem concluída com uma resposta gravada.

## Revisão e próximos passos

O autor autorizou executar o [plano da prova conversacional](../plans/2026-11-04-prova-conversacional-nuvem.md). A aplicação e os cenários manuais estão implementados localmente; a disponibilidade de base real continua sem comprovação e não bloqueou esses exemplos.

O próximo passo é publicar e executar a prova externa, com contas Free verificadas. A prova local usa componentes financeiros explicitamente informados; o gerador em escala virá depois da definição de amortização e alocação. Nenhuma hospedagem foi criada nesta sessão. Instalação isolada, dados ingeridos e testes reais constam do relatório vinculado.
