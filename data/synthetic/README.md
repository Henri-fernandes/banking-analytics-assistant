# Cenários sintéticos

Os contratos deste diretório são exemplos construídos para teste, sem clientes ou instituições reais. Valores monetários estão em centavos; juros contratuais são informados separadamente de principal. Parcelas únicas dos gabaritos de fronteira e variação têm juros explicitamente zero; isso não representa precificação de mercado.

`fixtures.json` contém cenários independentes, selecionados explicitamente: `fronteira`, `variacao` e `safras`. Não some cenários. A lista de referências declara cobertura completa da respectiva amostra; ausência de referência significa dado indisponível.

Posições são reconstruídas de contratos, parcelas e alocações. Atraso preserva o vencimento do resíduo após pagamento parcial; eventos posteriores à referência não alteram o passado. Este arquivo não é um gerador financeiro em escala. OverN inclui o próprio limiar N.
