# Referência pública — SGS 21114

Fonte: Banco Central do Brasil / Departamento de Estatísticas. [Ficha do conjunto](https://dadosabertos.bcb.gov.br/dataset/21114-inadimplencia-da-carteira-de-credito-com-recursos-livres---pessoas-fisicas---credito-pessoal-). O catálogo declara licença Open Data Commons Open Database License (ODbL): [texto da licença](https://opendatacommons.org/licenses/odbl/1-0/). Preserve atribuição e condições da fonte ao redistribuir os dados; essa licença da base é distinta do código do projeto.

A série mensal é percentual de inadimplência de crédito pessoal não consignado PF com recursos livres. O conceito publicado usa atraso **superior a 90 dias**. O indicador interno do banco fictício usa **a partir de 90 dias**, conforme decisão do autor. Os indicadores ficam em contextos separados; não são equivalentes por definição.

`sgs21114.json`, quando presente, contém a resposta original, valores normalizados, origem, período solicitado, data real de obtenção e SHA-256. Uma falha de atualização não substitui um arquivo válido por dados inventados. A ausência do arquivo deve ser apresentada como referência indisponível.

Atualização explícita, com Python configurado:

```powershell
.\.venv\Scripts\python.exe -m scripts.update_public_reference --start 2024-01-01 --end 2025-12-31
```

Nenhum registro desta fonte representa cliente, contrato ou filial do banco fictício. A referência não é somada à carteira sintética.
