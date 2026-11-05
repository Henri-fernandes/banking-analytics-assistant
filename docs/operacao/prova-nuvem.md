# Executar e publicar a prova inicial

Estado em 05/11/2026: aplicação implementada, testada localmente e enviada ao repositório público [Henri-fernandes/banking-analytics-assistant](https://github.com/Henri-fernandes/banking-analytics-assistant), na `main`. Hospedagem e inferência real ainda não verificadas. Nenhuma chave de inferência foi configurada ou utilizada.

## Rodar nesta pasta no Windows

O runtime preparado nesta sessão é Python 3.12.16, isolado em `.tools/`, com ambiente virtual `.venv/`. Não houve alteração global de PATH. Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --browser.gatherUsageStats false
```

Acesse `http://localhost:8501`. A demonstração analítica funciona pelos controles, mesmo sem chave. O chat fica desabilitado nessa situação e a interface informa a limitação.

Para reproduzir em outra pasta/máquina com Python 3.12 instalado:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py --browser.gatherUsageStats false
```

Recrie o ambiente virtual ao mover a pasta; ele contém caminhos locais. `.tools/` e `.venv/` não fazem parte dos arquivos a publicar. `requirements.txt` fixa a dependência direta; `requirements.lock.txt` registra também as versões transitivas utilizadas nesta sessão.

## Dados e verificações

Os três cenários sintéticos têm resultados conhecidos; a filial F01 tem operações e F02 representa um recorte conhecido sem população na amostra. A referência pública SGS 21114 é uma cópia separada de 24 observações mensais, obtida de uma fonte oficial com metadados. A definição pública usa `>90`; os Overs internos usam `>=N`.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m scripts.update_public_reference --start 2024-01-01 --end 2025-12-31
```

O segundo comando acessa a internet apenas para atualizar o snapshot. A aplicação lê o arquivo validado, sem chamar o Banco Central a cada pergunta. O SQLite é recomposto em memória; consultas recebem acesso somente leitura. Regras e dados versionados sobrevivem por recarga dos arquivos. Conversas e logs operacionais não têm persistência durável nesta prova.

## Habilitar a interpretação por IA

Copie `.streamlit/secrets.example.toml` para `.streamlit/secrets.toml` somente no ambiente privado, ou use o painel de Secrets da hospedagem. Esse arquivo real fica fora do versionamento. Os mesmos nomes podem ser definidos como variáveis de ambiente; não envie chaves pela conversa nem coloque credenciais no código.

Configuração suportada: `PROVIDER`, `GROQ_API_KEY`, `GROQ_FREE_VERIFIED`, `ALLOW_FALLBACK`, `GEMINI_API_KEY` e `GEMINI_FREE_VERIFIED`. Os nomes e modelos candidatos constam da [pesquisa atualizada](../pesquisas/comparacao-genie-agents-aplicacao-propria.md#revalidação-dos-candidatos-em-04112026).

Antes de marcar uma flag `FREE_VERIFIED` como `true`, conferir na conta que o plano e o modelo estão disponíveis gratuitamente. A flag é uma declaração de configuração do operador, não uma auditoria automática de faturamento. Não habilitar billing ou fornecer método de pagamento para contornar cotas. Se um candidato não estiver disponível no Free da conta, manter a inferência desabilitada e reavaliar a alternativa.

O modelo interpreta uma intenção estruturada; não recebe SQL livre, nem dados de contratos. O backend valida filtros e executa ferramentas fixas. Texto, tabela e gráfico derivam do mesmo resultado; uma regra documental versionada acompanha a consulta. Não há treinamento, embeddings ou RAG vetorial implementados nesta prova.

Cada pergunta permite no máximo uma chamada principal e uma alternativa configurada. Limites locais: 10 chamadas/minuto/processo, 6 por sessão, 2.000 caracteres por pergunta, 20 segundos por tentativa HTTP, 500 linhas e 2 segundos por consulta SQL. Excesso de linhas pede redução do recorte e não apresenta total parcial como consolidado. Limites em memória são reiniciados com o processo e não substituem cotas ou garantias financeiras do provedor.

## Preparar a publicação

O destino público `Henri-fernandes/banking-analytics-assistant` já contém o código. O autor concluiu o login de `Henri-fernandes` no GitHub CLI; permissão de escrita e primeiro push foram verificados. Git local acompanha `origin/main`. A licença do código ainda não foi escolhida.

1. Usar o código já enviado à `main`. Em novas alterações, conferir o diff e preservar o `.gitignore`: `.tools/`, `.venv/`, credenciais e dados privados continuam fora do repositório. Não repetir criação ou primeiro push.
2. No Community Cloud, selecionar esse repositório, arquivo `app.py` e Python 3.12. Instalar dependências a partir de `requirements.txt`; para resolução integralmente fixada, substituir seu conteúdo pelo lock após conferir instalação no Linux. Configurar segredos exclusivamente no painel do app. Não há serviço de banco externo obrigatório.
3. Publicar somente após revisar os arquivos e confirmar acesso à conta. A aplicação inicial expõe dados sintéticos e a referência pública; não há perfis de autorização para dados reais. A abordagem híbrida não autoriza inserir registros privados nessa demonstração aberta.
4. Conferir uma pergunta nova e registrar consumo/erros da chamada real. Sem chave ou sem plano gratuito verificado, a publicação pode servir a interface analítica, mas não comprova o atendimento conversacional por inferência.

Como alternativa de implantação, usar Render Free sem método de pagamento cadastrado, com build `pip install -r requirements.txt` e start `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --browser.gatherUsageStats false`. A expressão `$PORT` desse start é para o ambiente Linux do Render, não para colar no PowerShell. Não usar banco gratuito com expiração de 30 dias. As condições e a hibernação dos dois candidatos estão na pesquisa vinculada; nenhum deles foi implantado nesta sessão.

## Evidência exigida para declarar nuvem verificada

- URL publicada e versão dos arquivos, provedor/modelo, plano gratuito verificado na conta e cotas observadas.
- Visitante executa pergunta nova com o PC do autor desligado; tabela e gráfico reconciliam com o gabarito.
- Reinício recompõe os arquivos/SQLite e preserva as versões exibidas, sem confundir isso com persistência de conversa.
- Cota e falha de provedor recebem resposta correta. Simulação deve ser identificada como simulação.

O [relatório inicial](../avaliacoes/prova-inicial.md) separa o que já rodou localmente dessas verificações ainda pendentes.
