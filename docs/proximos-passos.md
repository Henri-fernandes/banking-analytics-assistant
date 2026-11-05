# Estado atual e próximos passos

Atualizado em 05/11/2026. Este é um roteiro proposto de continuidade, não um plano técnico fechado. As decisões confirmadas estão em [contexto e decisões](contexto-e-decisoes.md).

## Estado verificável

- Documentação inicial, comparação com Genie e ADR-0001 preparados.
- Banco, atendimento PF/PJ, aplicação própria, custo adicional zero e atendimento na nuvem confirmados.
- Crédito pessoal parcelado PF e capital de giro parcelado PJ confirmados; novos produtos serão adicionados depois.
- Recorte inicial confirmado: analista de carteira/crédito; saldo, evolução da inadimplência, contribuição para a variação e safras em mesma idade.
- Abordagem híbrida confirmada: dados sintéticos, públicos e reais. A prova já tem amostras sintéticas e referência pública; nenhuma base real privada foi disponibilizada.
- Regra geral dos Overs confirmada: OverN inclui atraso a partir de N dias, inclusive (`dias_atraso >= N`); vale para Over90 e os demais limiares.
- Plano autorizado e implementado localmente: Python 3.12.16, Streamlit 1.66.0 e SQLite reconstruível; comandos reais no README.
- Três cenários sintéticos manuais e 24 observações públicas SGS 21114 carregados; base real e gerador em escala não implementados.
- 37 testes passando, incluindo interface e duas sessões com provedor controlado; servidor local respondeu HTTP 200.
- Repositório público [Henri-fernandes/banking-analytics-assistant](https://github.com/Henri-fernandes/banking-analytics-assistant) criado e verificado. Git local inicializado na `main`, com `origin` configurado; primeiro commit em preparação. Envio depende de autenticação com permissão no destino. Nenhum push/deploy ou chave de inferência configurados até esta atualização.
- Nenhuma inferência real, teste das cotas da conta ou acesso por terceiro com PC desligado. A revisão visual de navegador foi interrompida pelo Computer Use por falta de verificação segura da URL.

## Próximo trabalho: publicar e verificar a prova na nuvem

O autor autorizou a execução do [plano da prova funcional](superpowers/plans/2026-11-04-prova-conversacional-nuvem.md). A implementação local e suas evidências estão no [relatório](avaliacoes/prova-inicial.md). Retome a etapa externa do [guia operacional](operacao/prova-nuvem.md); não refaça o núcleo já testado.

Concluir a revisão do primeiro commit e o envio ao repositório de destino. A autenticação disponível pertence a outra conta e não tem permissão de escrita nesse repositório; o autor precisa autenticar `Henri-fernandes` pelo GitHub CLI ou conectar a conta correspondente. Depois, configurar hospedagem e provedor sem custo. Não solicitar segredos na conversa; usar configuração privada na hospedagem. A revisão visual deverá ser retomada quando houver acesso seguro ao navegador.

A [preparação do primeiro envio](avaliacoes/preparacao-github.md) registra o estado do Git e a verificação local de 05/11/2026. Não refazer a implementação para resolver a autenticação.

**Concluído quando:** o plano estiver revisado e a prova executar perguntas novas com dados conhecidos, SQL rastreável e inferência na nuvem; evidência de acesso por terceiro, reinício e limites de cota deve ser registrada. Código local ou plano escrito não satisfazem, por si só, esse critério.

## Pendências por dependência

| Prioridade | Decisão em aberto | Resultado necessário |
|---|---|---|
| P0 | Repositório, hospedagem e inferência | Revisar arquivos, criar/identificar destino e configurar contas Free para a prova externa |
| P0 | Fontes da abordagem híbrida | Selecionar fontes públicas e identificar disponibilidade de base real, condições de uso e limitações |
| P0 | Histórico e volume | Períodos, granularidades e cobertura suficiente das janelas de análise |
| P0 | Indicadores e políticas | Contratos das métricas e casos numéricos de referência |
| P0 | Viabilidade gratuita da nuvem | Pequena consulta e resposta novas acessíveis por terceiro |
| P1 | Stack principal e alternativas | Candidatos revalidados documentalmente em 04/11/2026; faltam compatibilidade funcional e teste nas contas do autor |
| P1 | Modelo de dados e camadas | Entidades, eventos, posições, qualidade e atualização |
| P1 | Corpus e recuperação | Documentos, vigências, métodos candidatos e avaliação |
| P1 | Interface e exportações | Formato das respostas, interações e arquivos |
| P2 | Alvo do fine-tuning | Hipótese, dataset, avaliação e hospedagem compatível |
| P2 | MCP | Uso concreto e benefício frente às ferramentas já implementadas |

P0/P1/P2 indica ordem de resolução proposta, não obrigação de implementar todos os itens de uma vez. Identidade visual e nome do banco podem ser escolhidos sem bloquear a definição dos dados.

## Sequência de entregas proposta

| Etapa | Trabalho | Evidência de conclusão |
|---|---|---|
| 1. Produto e regras | Produtos, perguntas, métricas e limites | Recorte definido e casos de referência verificáveis |
| 2. Prova na nuvem | Aplicação mínima, consulta e inferência | Visitante executa pergunta nova com PC do autor desligado, dentro do plano gratuito |
| 3. Dados e corpus | Ingestão/geração, qualidade, camadas e documentos | Recarga reproduzível, integridade e reconciliações aprovadas para o recorte |
| 4. Backend analítico | Métricas, ferramentas, contexto, recuperação e agente | Perguntas de referência corretas com consultas e fontes rastreáveis |
| 5. Interface | Gráficos, tabelas, streaming e arquivos priorizados | Mesmos dados validados em resposta, visualização e exportação |
| 6. Robustez | Avaliação, acesso, observabilidade, cache e fallback | Casos de erro e de acesso cobertos; relatório de qualidade e consumo |
| 7. Experimentos | Recuperação, modelos e fine-tuning relevante | Comparação reproduzível e artefato executável no ambiente previsto |
| 8. Publicação | Documentação, demonstração e reprodução | Link acessível, instalação descrita e limites identificados |

Avaliação e observabilidade acompanham as etapas; a etapa 6 consolida os testes. A sequência dos módulos financeiros está no [escopo de negócio](escopo-negocio.md). Esboçar o contrato da interface antes do backend completo ajuda a definir a saída de tabelas e gráficos.

## Decisão de stack: como comparar

Para cada dependência crítica, registrar função, candidato principal, alternativa, limites gratuitos, autenticação exigida do visitante, recursos necessários, persistência, suporte ao modelo ajustado quando aplicável e resultado do teste. Registrar data e fontes oficiais, pois condições de provedores mudam.

A [pesquisa inicial](pesquisas/comparacao-genie-agents-aplicacao-propria.md) contém as evidências já coletadas. Entre os pontos a rever estão acesso público no Databricks, cotas de APIs, restrições de LoRA na Groq, compatibilidade de saída estruturada/streaming/ferramentas, elegibilidade ZeroGPU e hibernação/persistência das hospedagens. A presença de um serviço na pesquisa não autoriza concluir que ele atende o projeto.

## Atualização de estado

Após uma decisão, atualizar seu documento de origem e este estado/roteiro quando houver mudança de prioridade. Registrar escolhas arquiteturais relevantes em ADRs curtos. Ao implementar, documentar os comandos reais de execução e teste e os resultados obtidos. Quando um teste falhar, preservar a evidência e revisar a hipótese sem marcar a etapa como concluída.
