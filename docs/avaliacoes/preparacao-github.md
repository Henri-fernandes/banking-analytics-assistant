# Preparação do primeiro envio ao GitHub

Data: 05/11/2026. Destino confirmado: [Henri-fernandes/banking-analytics-assistant](https://github.com/Henri-fernandes/banking-analytics-assistant), público. O primeiro envio ainda não foi confirmado.

## Verificações locais

- Git inicializado na branch `main`; `origin` configurado para o destino fornecido pelo autor.
- Autor local configurado como `Henri-fernandes`, usando o endereço público noreply associado ao identificador público da conta. Isso configura autoria de commit, não autenticação ou permissão de envio.
- Suite executada novamente em 05/11/2026 com `.venv/Scripts/python.exe -m unittest discover -s tests -q`: 37 testes, sem falhas ou erros.
- `.gitattributes` estabelece normalização de texto em LF. `.gitignore` exclui ambiente virtual, ferramentas locais, credenciais de execução e dados privados.
- Os arquivos destinados ao primeiro commit serão enumerados em [arquivos-primeiro-commit.txt](arquivos-primeiro-commit.txt) e conferidos antes do commit. A checagem de credenciais procura padrões reconhecíveis; não substitui revisão de conteúdo ou auditoria de segurança.

## Autenticação pendente

A conta atualmente disponível não tem permissão de escrita nesse repositório. Foi solicitado ao autor autenticar `Henri-fernandes` pelo GitHub CLI, sem enviar senha ou token na conversa. Nenhum envio por uma conta diferente, fork ou mudança de permissões foi realizado como alternativa.

Depois da autenticação, conferir a conta ativa e a permissão no destino antes de executar `git push -u origin main`. Revalidar o estado remoto; se houver conteúdo novo, não usar force push. A publicação da aplicação e a inferência real continuam etapas separadas.

## Observação do ambiente

O diretório Git foi criado pela conta de sandbox. As operações autorizadas fora do sandbox usam uma exceção de diretório confiável restrita a esse diretório em cada comando, sem adicionar configuração global. Isso permite preparar o Git local sem trocar a propriedade dos arquivos ou alterar a confiança de outros repositórios.
