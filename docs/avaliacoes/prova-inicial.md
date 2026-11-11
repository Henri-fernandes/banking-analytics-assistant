> Histórico: a implementação descrita foi retirada em 10/11/2026. Este documento não descreve a versão atual; consulte o [recomeço](../reinicio.md).

# Evidências da prova inicial

Data: 04/11/2026. Escopo: implementação local da primeira prova, sem implantação externa. A [execução e suas decisões](execucao-inicial.md) e o [plano](../superpowers/plans/2026-11-04-prova-conversacional-nuvem.md) permitem retomar o trabalho.

## Resultado observado

- Python 3.12.16 e Streamlit 1.66.0 instalados em ambiente isolado da pasta, sem alterar o PATH global.
- Suite `python -m unittest discover -s tests -v`: **37 testes passaram**. O [resultado estruturado](resultado-testes.json) registra a execução final com contagem e duração reais. Os avisos `missing ScriptRunContext` são emitidos pelo ambiente de testes Streamlit fora de uma sessão de navegador; não houve exceção da aplicação nos AppTests.
- Servidor local iniciado em `127.0.0.1:8501`; rota `/_stcore/health` respondeu HTTP 200, corpo `ok`.
- Três cenários sintéticos, com 13 contratos no total dos cenários independentes, recompõem as posições de teste. Não são uma carteira observada nem um gerador financeiro em escala.
- Referência pública SGS 21114: 24 observações, janeiro/2024 a dezembro/2025, obtidas pelo script deste projeto usando o endpoint oficial do Banco Central. Metadados e resposta original estão em `data/public/sgs21114.json`. SHA-256 da resposta original: `5a69845b54b781dc20ca93113bd86e69cd4c11efdebf74ee50512073afbea7eb`.

## O que os testes cobrem

| Capacidade | Evidência local |
|---|---|
| Overs inclusivos | N−1, N, N+1 para 1, 15, 30, 60, 90 e 180; Over0 inclui dia zero |
| Fronteira Over90 | Atrasos 89/90/91/120; saldo R$ 10.000, numerador R$ 9.000, taxa 90% |
| Saldo e histórico | Pagamento parcial, liquidação, juros residuais, vencimento na referência e evento futuro sem alteração do passado |
| Variação | Taxas 30% e 40%; contribuições PF +5 p.p. e PJ +5 p.p.; soma +10 p.p. |
| Safra/MOB | Mesma idade, MOB 0 na originação e ausência de desempenho futuro |
| Qualidade e SQL | Duplicata, chave órfã, dinheiro inválido, componentes ausentes, filtro inválido, SQLite somente leitura, limite sem total parcial |
| Conversa e provedor | Continuação preserva filtros; intenção extra/SQL, datas inválidas, recusa, truncamento, resposta malformada, ausência de chave, Free não verificado, cota e fallback limitado |
| Sessões | Dois AppTests isolados; “e em PJ?” conserva Over30 e período; limpeza de mensagens da própria sessão |
| Referência pública | Definição externa preservada, HTML/percentual inválidos rejeitados, integridade verificada e atualização inválida preservando snapshot anterior |

As respostas dos provedores foram controladas nos testes. Contadores de tokens dessas respostas são exemplos de teste, não consumo real de inferência ou benchmark de latência. A coleta do Banco Central foi real e identificada como fonte pública separada.

## Revisão de código

Revisão local pelo próprio implementador, sem subagentes, conforme a execução escolhida. Foram corrigidos com testes de regressão que falharam antes da correção: total parcial quando a consulta excedia o limite, estrutura aninhada malformada do provedor, ausência de metadados de erro e percentual público booleano interpretado como número. A seleção do trecho da regra versionada também foi verificada no resultado analítico. Não houve revisão independente nem commit, pois a pasta não é repositório Git.

## Não executado e limitações

- Nenhuma chamada real de Groq ou Gemini, nenhuma chave configurada e nenhuma cota da conta verificada.
- Nenhum repositório GitHub de destino criado, nenhum push ou deploy. O autor informou que o repositório ainda não existe.
- Nenhuma visita com o computador do autor desligado ou reinício de hospedagem remota. A prova de nuvem permanece pendente.
- Conferência visual de navegador pendente: o acesso ao navegador integrado estava indisponível; Computer Use interrompeu o acesso ao Chrome porque não conseguiu verificar com segurança a URL atual. Nenhuma nova ação de UI foi executada após essa interrupção.
- Não há dados privados/reais integrados, autenticação por perfis, persistência durável de conversa/telemetria, geração em escala, embeddings, fine-tuning ou módulos posteriores. Os três cenários sintéticos têm regras explícitas, com eventos suportados delimitados.

Próximo passo operacional: criar/identificar o repositório e configurar as contas gratuitas para executar os critérios de nuvem descritos no [guia](../operacao/prova-nuvem.md).
