# Regras da carteira de demonstração

Regra: carteira-v1-inclusive

Autoria: projeto Financeiro. Origem: definições gerenciais da amostra e convenção de Overs confirmada pelo autor em 04/11/2026. Aplicabilidade: todos os cenários sintéticos desta versão. As datas de observação dos cenários são fictícias; este documento define sua interpretação para a demonstração, sem alegar política histórica de um banco real ou conformidade regulatória.

## saldo

Saldo principal é a concessão menos amortizações de principal efetivadas até a referência. Inclui principal vencido e a vencer; juros e encargos ficam separados. Posição mensal: último dia do mês, uma linha por contrato. Contratos ainda não originados ficam fora. Saldo nulo significa informação ausente; saldo zero não participa da população de crédito com principal positivo. Posições de meses diferentes não são somadas.

## over

Todos os Overs usam `dias_atraso >= N`. Over30 inclui 30 dias; Over90 inclui 90 dias. O atraso é contado em dias corridos desde o vencimento da parcela mais antiga que ainda tem obrigação contratual pendente na referência. Pagamento parcial mantém o vencimento do resíduo. Parcela com vencimento na própria referência tem zero dias de atraso.

Nesta amostra, a taxa é o principal dos contratos enquadrados no Over dividido pelo principal elegível do mesmo recorte e data. Numerador e denominador usam a mesma população com principal positivo e atraso conhecido. Componentes ausentes são identificados e excluídos das métricas afetadas. População vazia produz taxa sem resultado, diferente de zero por cento. O indicador não é PD.

## contribuicao

Para cada produto g e data t, N(g,t) é o principal inadimplente e D(t) é o principal elegível consolidado. A contribuição é `100 × [N(g,t1)/D(t1) − N(g,t0)/D(t0)]`, em pontos percentuais. A soma das contribuições reconcilia a variação consolidada. Denominador zero ou referência indisponível impede a decomposição. Contribuição observada combina saldo e composição; não demonstra causa econômica.

## safras

Safra é o mês de originação. MOB é a diferença entre os meses-calendário da posição e da originação; o mês de originação é MOB 0. Comparar apenas idades observadas. Meses futuros permanecem ausentes. A curva mostra o Over na posição de cada MOB, não bad acumulado nem PD.

## limites

Os cenários iniciais não simulam renegociação, reestruturação, provisão, baixa para prejuízo, DRE, RAROC ou liquidez. Dados com eventos financeiros não suportados devem ser revisados antes de uso. A referência pública SGS 21114 preserva seu conceito externo de atraso superior a 90 dias e não é equivalente ao Over90 interno inclusivo.
