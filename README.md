# Banking Analytics Assistant

Base inicial de regras e dados para um projeto de análise de crédito de clientes PF e PJ.

## Arquivos

- [Regras de crédito e carteira](output/pdf/regras_credito_v1.pdf): documento com políticas de concessão, saldo devedor, pagamentos, inadimplência, renegociação e safras.
- [Base de crédito](outputs/base-inicial/base_credito_v1.xlsx): planilha com tabelas de clientes, produtos, propostas, contratos, parcelas, pagamentos, renegociações e posições mensais.

A amostra reúne 28 clientes fictícios, 30 propostas e 26 contratos, com posições de janeiro a junho de 2026. Os produtos são crédito pessoal parcelado PF e capital de giro parcelado PJ.

Os indicadores Over usam limiar inclusivo: `dias_atraso >= N`. O documento distingue saldo principal, juros vencidos e saldo devedor e descreve o tratamento dos pagamentos e das renegociações.

## Escopo

Os dados são sintéticos e as políticas são fictícias, preparados para estudo e demonstração. Não representam uma instituição real ou política regulatória.

Esta primeira entrega contém apenas o documento de regras e a base de dados. O assistente conversacional será incorporado em uma entrega posterior.
