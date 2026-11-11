# Estado atual e próximos passos

Atualizado em 10/11/2026.

## Decisão atual

O autor solicitou remover a implementação anterior do repositório e recomeçar por partes. A versão atual preserva documentação, decisões e pesquisa. O painel, os módulos Python, dados de demonstração, testes e configurações da prova foram retirados. O histórico do Git permite consultar o código anterior em `afc1077`.

Não há uma nova aplicação executável, base ativa, corpus, agente ou RAG nesta versão. Os relatórios de testes anteriores são históricos. Consulte o [registro do recomeço](reinicio.md).

## Objetivo confirmado

Assistente interno em formato de chat para um banco PF/PJ: consultar dados, arquivos e regras; combinar fontes verificáveis; manter contexto; apresentar tabelas e gráficos quando necessários. Aplicar controles de acesso, validação, limites, avaliação e tratamento de falhas. Atendimento na nuvem, com o PC desligado e custo adicional zero.

Produtos iniciais: crédito pessoal parcelado PF e capital de giro parcelado PJ. Origem híbrida das fontes e Overs inclusivos permanecem confirmados. Não há base privada fornecida. Novos produtos, regras financeiras e fornecedores dependem do recorte discutido com o autor.

## Primeira parte proposta

Alinhar um pequeno conjunto de perguntas que represente a experiência desejada. Para cada uma, identificar dados, documentos e evidências necessárias. A partir disso, especificar o modelo dos dados e o inventário documental antes de iniciar a construção.

Resultado esperado desta parte: uma especificação revisável do primeiro recorte, distinguindo decisões confirmadas, políticas fictícias propostas e escolhas em aberto. A referência em vídeo orienta a experiência; sua stack não está aprovada por associação.

## Partes seguintes, ainda a detalhar

1. Construir e validar dados coerentes e documentos versionados do recorte escolhido.
2. Validar consultas e recuperação documental separadamente, com gabaritos e fontes esperadas.
3. Integrar agente e interface de chat, combinando dados e documentos e mantendo o contexto.
4. Avaliar guardrails, respostas, acesso, falhas e consumo; verificar operação na nuvem.

Essas partes são um roteiro, não autorização para implementar tudo de uma vez. O autor pediu avançar por partes. Os controles acompanham dados, ferramentas e recuperação desde sua criação.

## Publicação anterior

A captura do autor mostrou o painel no Community Cloud, mas nenhuma URL foi fornecida e não houve prova independente de acesso/inferência. A remoção de `app.py` torna a configuração antiga de deploy incompatível com a versão atual. A instância hospedada não foi excluída por esta alteração no Git; qualquer cópia ainda servida corresponde à prova retirada.
