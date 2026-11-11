# Escopo de negócio — assistente interno de um banco

Atualizado em 10/11/2026. Este documento registra o recorte informado pelo autor e identifica decisões pendentes. A implementação anterior foi removida a pedido do autor; referências à prova abaixo são históricas. O novo modelo, regras adicionais e plano de construção serão especificados por partes; consulte [próximos passos](proximos-passos.md).

## Definições confirmadas

- Instituição representada: banco/instituição financeira, com foco em crédito e temas financeiros relacionados.
- Públicos atendidos: **pessoas físicas (PF) e pessoas jurídicas (PJ)**, conforme confirmação do autor em 30/10/2026.
- Produtos iniciais: **crédito pessoal parcelado PF** e **capital de giro parcelado PJ**, confirmados em 04/11/2026, com inclusão de mais produtos posteriormente.
- Origem dos dados: abordagem **híbrida**, combinando fontes sintéticas, públicas e reais, confirmada em 04/11/2026. A disponibilidade de uma base real ainda não foi comprovada.
- Recorte inicial: analista de carteira/crédito consultando saldo, evolução da inadimplência, contribuição para a variação e safras em idades equivalentes. As fórmulas continuam propostas.
- Limiar de todos os Overs: **OverN inclui atraso a partir de N dias, inclusive** (`dias_atraso >= N`), confirmado em 04/11/2026. Over90 inclui 90 dias; Over30 inclui 30 dias. Numerador, denominador e demais componentes devem constar do contrato de cada métrica.
- Desenvolvimento: VS Code com Codex, conduzido pelo autor.
- Entrega: aplicação própria acessível na nuvem, sem dependência da máquina pessoal durante o uso e sem custo adicional.
- Dados centrais: clientes, filiais, propostas, contratos, parcelas, pagamentos e renegociações.
- Finalidade: permitir consultas e aprofundamentos analíticos por linguagem natural, com resultados verificáveis, tabelas, gráficos e exportações.

Ainda estão em aberto: identidade/nome do banco, fontes específicas, histórico, escala, jurisdição normativa e regras operacionais. Produtos posteriores serão detalhados em novas entregas.

O detalhamento dos cadastros, produtos, políticas e parâmetros de risco deve contemplar as diferenças entre PF e PJ. As regras de comparação e consolidação serão definidas na especificação dos indicadores.

## Primeira prova implementada localmente

As quatro perguntas iniciais já têm ferramentas SQL e interface local, com três cenários sintéticos manuais e referência pública separada. Consulte a [especificação](superpowers/specs/2026-11-04-primeira-entrega-design.md), as [regras implementadas na amostra](metricas/carteira-v1-inclusive.md) e as [evidências](avaliacoes/prova-inicial.md). Dados reais, geração em escala, inferência real e atendimento publicado ainda não foram verificados.

A composição de fontes preservará o nível de cada informação. Séries públicas agregadas servem como contexto ou referência de mercado; não serão convertidas em contratos individuais observados nem somadas ao saldo do banco fictício. A combinação com uma base real dependerá de sua disponibilidade, significado dos campos e condições de utilização. O núcleo sintético permitirá testar cenários conhecidos sem depender dessa disponibilidade.

## Domínios desejados e dependências

| Domínio | Assuntos informados pelo autor | Dados adicionais propostos para detalhar |
|---|---|---|
| Concessão e qualidade de originação | Propostas, aprovações, concessões, safras, MOB e bads | Produto, canal, decisão, data de originação, limites, perfil e classificação de risco no momento da proposta |
| Carteira e comportamento | Saldo devedor, carteira, inadimplência, overs e write-off | Posições históricas por contrato e data, alocação de pagamentos, dias de atraso, eventos de baixa e recuperação |
| Risco e provisão | PD, PDD/provisão e perda de crédito | Parâmetros de risco versionados, exposição, critérios de classificação e movimentos da provisão; LGD/EAD quando exigidos pelo método escolhido |
| Renegociação e reestruturação | Alteração de condições, recuperação e desempenho após alteração | Eventos e motivos, vínculo entre operações originais e novas, condições antes/depois e histórico de pagamentos |
| Resultado e rentabilidade | DRE e RAROC | Contas e lançamentos, competência, receitas, custos de captação, despesas, perdas, critérios de alocação e capital |
| Liquidez | Entradas/saídas, disponibilidade e descasamento de prazos | Caixa, ativos líquidos, captações/passivos, vencimentos, fluxos previstos/realizados e hipóteses de estresse |

As fontes adicionais são uma proposta de dependências, não um esquema de banco de dados aprovado. Os sete grupos centrais são a base do crédito; os demais temas requerem ampliar as informações disponíveis para que as análises tenham significado.

## Decisões de regra a formalizar

### Concessão, safra, MOB e bad

- Separar solicitação, aprovação e contratação efetiva, inclusive propostas rejeitadas ou não convertidas.
- Definir a data que determina a safra e a convenção de contagem do MOB.
- Definir evento bad, limite de atraso, horizonte de desempenho e unidade de cálculo.
- Comparar safras em idades equivalentes e identificar operações ainda sem janela completa de observação.
- Definir como tratar cancelamentos, antecipações, renegociações e propostas repetidas.

### Carteira, saldo, overs e write-off

- Definir quais componentes formam cada saldo: principal, juros, encargos, parcelas vencidas e a vencer.
- Distinguir posições em uma data de referência de fluxos acumulados no período.
- Especificar cada Over: fronteira de dias, contagem ou saldo, numerador, denominador e população elegível.
- Definir atraso de parcela e de contrato, pagamentos parciais, alocações e eventos de baixa/recuperação.
- Evitar somar saldos de várias datas como se fossem uma posição única da carteira.

### PD e provisão

- Distinguir probabilidade estimada (PD) de desfechos observados (bads).
- Definir horizonte da PD, população, data da estimativa e versão do parâmetro/modelo.
- Decidir se o assistente consumirá parâmetros disponibilizados, simulados ou produzidos em um experimento específico. Construir um novo modelo de crédito não é consequência automática de consultar PD.
- Definir método de provisão, exposição, parâmetros, cenários e classificações necessários ao cálculo.
- Distinguir o saldo da provisão em uma data de seus movimentos e do efeito no resultado.
- Formalizar o significado de PDD no projeto e as referências normativas adotadas.

### Renegociação e reestruturação

- Definir os critérios que distinguem as duas categorias.
- Preservar o vínculo entre operações e o histórico anterior à alteração.
- Definir tratamento de múltiplos contratos em um acordo, descontos, novos prazos, pagamentos e reincidência de atraso.

### DRE e RAROC

- Definir plano de contas, competência, apropriações, despesas e critérios de alocação.
- Conciliar o resultado com seus lançamentos e com os movimentos da provisão pertinentes.
- Para RAROC, definir resultado ajustado ao risco, capital, período, anualização e nível de agregação.
- Recebimento de parcelas, amortização de principal e receita contábil precisam de representações distintas.

### Liquidez

- Definir fluxo contratual e fluxo esperado, disponibilidade, captações, vencimentos e hipóteses de estresse.
- Distinguir análise gerencial de caixa e descasamento de indicadores regulatórios completos.
- Confirmar quais métricas de liquidez serão demonstradas e se os dados sustentam seus cálculos.

## Proposta de sequência das entregas

1. Base de crédito e regras: clientes, filiais, propostas, contratos, parcelas, pagamentos, posições e eventos de alteração.
2. Consultas de concessão, safras/MOB/bads, carteira, saldo, overs e comportamento após renegociação.
3. Parâmetros de risco e provisão, com reconciliação e histórico de versões.
4. Dados de resultado e capital para DRE e RAROC.
5. Dados de tesouraria/captação e fluxos para liquidez.

A sequência é uma proposta a validar. Os temas informados permanecem no escopo desejado; cada entrega deve ter perguntas, dados e critérios de aceitação próprios.

## Contexto documental para o RAG

O corpus poderá conter políticas de crédito, dicionário de indicadores, regras de classificação, regras contábeis, procedimentos de cobrança, documentos de produtos e descrições dos cenários de liquidez. Cada documento deve ter autoria/origem, vigência, versão e ligação com as métricas pertinentes.

O sistema deve distinguir regra institucional, referência externa, hipótese de simulação, parâmetro estimado e dado observado. Em respostas históricas, precisamos recuperar os dados e as regras aplicáveis à data consultada.

## Referências iniciais, sujeitas ao recorte adotado

Se o projeto adotar referência brasileira, a [Resolução CMN 4.966](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=4966&tipo=RESOLU%C3%87%C3%83O+CMN) é uma das fontes a avaliar para perdas esperadas e tratamento de instrumentos renegociados/reestruturados. Sua aplicabilidade e os critérios operacionais ainda não foram definidos neste projeto.

O [Basel Framework — LCR](https://www.bis.org/committees/bcbs/basel-framework/standard/lcr?allChapters=true) relaciona ativos líquidos e fluxos líquidos de saída sob estresse, ilustrando a necessidade de dados além da carteira de crédito para métricas regulatórias de liquidez. Nenhum LCR foi aprovado ou calculado neste momento.

O [glossário do BCE](https://www.ecb.europa.eu/services/glossary/html/act2r.et.html) identifica RAROC como retorno sobre capital ajustado ao risco. A fórmula, os ajustes e o capital utilizados serão documentados separadamente.

Estas fontes orientam a especificação; ainda não representam um compromisso de implementação regulatória completa.
