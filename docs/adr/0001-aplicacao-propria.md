---
status: accepted
date: 2026-10-30
---

# ADR-0001 — Desenvolver uma aplicação própria como entrega principal

Decidimos desenvolver o assistente interno de dados como aplicação própria, aproveitando bibliotecas, APIs e serviços existentes. A decisão foi aprovada pelo autor do projeto em 30/10/2026 após a comparação com Databricks Genie Agents. O objetivo é combinar demonstração pública na nuvem, custo adicional zero e controle dos componentes de engenharia de IA que o portfólio pretende evidenciar.

## Alternativas consideradas

**Databricks Genie Agents:** fornece analytics conversacional, SQL, gráficos, governança, avaliação e recursos de exportação. Reduz o trabalho de aplicação e evidencia competências no ecossistema Databricks. Entretanto, a interface incorporada exige autenticação Databricks, Apps não aceita acesso anônimo e a integração pública via API precisa ter sua viabilidade gratuita comprovada na edição utilizada. A configuração documentada também não expõe os mesmos controles de treinamento e recuperação de uma implementação própria.

**Aplicação própria — escolhida:** permite definir a experiência de acesso, recuperação documental, ferramentas, validações, contratos de saída, cache, fallback, avaliações e instrumentação. A maior liberdade traz trabalho adicional de integração, segurança, testes e manutenção. Gratuidade e disponibilidade dependem de cotas e capacidades que ainda precisam ser testadas.

Os fatos, fontes e limites da pesquisa estão na [análise comparativa](../pesquisas/comparacao-genie-agents-aplicacao-propria.md), consultada em 30/10/2026. A escolha não pressupõe maior acurácia nem preferência de recrutadores por uma das arquiteturas.

## Consequências

- O atendimento será executado integralmente na nuvem, sem dependência da máquina do autor.
- A stack continua em aberto. Groq, Gemini, Streamlit, Render, Hugging Face e outras opções citadas na pesquisa são candidatas, não decisões aprovadas.
- Regras de negócio e ferramentas terão limites definidos; a compatibilidade de modelos e fornecedores será verificada com os mesmos casos de avaliação.
- Controle de acesso, validação de consultas e resultados, persistência, tratamento de falhas e observabilidade passam a ser responsabilidades da implementação.
- Fine-tuning exige uma decisão conjunta de alvo e hospedagem. Possibilidade de treinamento local não comprova viabilidade gratuita de inferência na nuvem.
- O Databricks pode ser avaliado para preparação de dados ou comparação futura, sem tornar o Genie uma dependência do atendimento por esta decisão.
- A implementação será precedida pelas definições de domínio, dados, regras e avaliação e por uma prova mínima de publicação gratuita.

Revisitar esta decisão se as restrições de acesso ou orçamento mudarem, ou se testes demonstrarem que outra arquitetura atende melhor aos requisitos.
