# Banking Analytics Assistant

Assistente conversacional para análise de crédito de clientes PF e PJ. Consulta dados de carteira em uma planilha, recupera regras de um PDF e apresenta respostas, tabelas e gráficos na conversa.

A versão atual funciona localmente com Python e uma interface em HTML, CSS e JavaScript. A geração de respostas utiliza a API do Gemini. Autenticação e publicação da aplicação na nuvem são etapas pendentes.

## Funcionalidades

- Consultas de saldo, inadimplência, contratos, concessões, propostas, renegociações e safras por ferramentas de leitura.
- Recuperação textual de regras com identificação do documento, seção e páginas, mantida internamente para conferência.
- Continuação de perguntas por indicador, período, público e filial.
- Gráficos de linhas e colunas agrupadas, com painéis separados para PF e PJ, rótulos de dados e valores por mês.
- Histórico local de mensagens, gráficos e contexto, preservado ao atualizar a página ou reiniciar o servidor. Retenção de sete dias de inatividade.

O agente consulta somente as fontes disponibilizadas à aplicação. Não possui busca na internet nem ferramenta para executar SQL livre. As consultas são fixas e parametrizadas; a conexão analítica é somente leitura.

## Dados e regras

- [Regras de crédito e carteira](output/pdf/regras_credito_v1.pdf): concessão, saldo devedor, pagamentos, inadimplência, renegociação e safras.
- [Base de crédito](outputs/base-inicial/base_credito_v1.xlsx): clientes, produtos, propostas, contratos, parcelas, pagamentos, renegociações e posições mensais.

A amostra contém 28 clientes fictícios, 30 propostas e 26 contratos, com posições de janeiro a junho de 2026. Os produtos iniciais são crédito pessoal parcelado PF e capital de giro parcelado PJ.

Todos os indicadores Over usam limiar inclusivo: `dias_atraso >= N`. O cálculo considera o saldo principal elegível de cada posição, preservando a distinção entre principal, juros vencidos e saldo devedor. Posições mensais não são somadas como se fossem fluxos.

Os dados são sintéticos e as políticas são fictícias, preparados para estudo e demonstração. Não representam uma instituição real ou política regulatória.

## Executar localmente

Requisitos: Python 3.12 e uma chave de projeto Gemini no plano gratuito, sem faturamento habilitado. No PowerShell, a partir da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m assistente configurar
.\.venv\Scripts\python.exe -m assistente servir
```

A configuração solicita a chave com entrada oculta e a grava no `.env`, ignorado pelo Git. Execute `configurar` somente na primeira configuração. O aplicativo não verifica o plano da conta no provedor; cotas esgotadas interrompem a consulta, sem repetição automática.

Abra [http://localhost:8501](http://localhost:8501) e mantenha o processo em execução. Para iniciar novamente, basta executar o último comando. Uma porta alternativa pode ser indicada com `--porta 8502`.

Use sempre o mesmo navegador e endereço para recuperar a conversa: `localhost` e `127.0.0.1` possuem cookies separados. O botão **Nova conversa** limpa a sessão atual. O histórico fica em `.tools/chat/conversas.sqlite`, também ignorado pelo Git.

## Exemplos de perguntas

```text
Qual o Over60 PJ em junho de 2026?
E PF?
E em maio?
Explique a regra de inadimplência do PDF.
Crie gráficos de colunas dos Overs 30, 60 e 90 para todos os meses da base,
um para PF e outro para PJ.
```

Envie as continuações separadamente. Os três primeiros resultados de referência são, respectivamente, 9,05%, 71,46% e 63,54%.

A camada de dados também pode ser consultada sem chamar o modelo:

```powershell
.\.venv\Scripts\python.exe -m fontes consultar over --referencia 2026-06-30 --publico PJ --limiar 90
.\.venv\Scripts\python.exe -m fontes buscar "Como funciona a renegociação?"
```

O primeiro comando retorna numerador de R$ 28.800,00 e denominador de R$ 318.300,00, com taxa aproximada de 9,05%. Valores monetários no JSON da ferramenta estão em centavos.

## Estrutura

| Caminho | Responsabilidade |
|---|---|
| `assistente/` | Orquestração, transporte Gemini, histórico e servidor local |
| `assistente/static/` | Interface de conversa e renderização dos gráficos |
| `fontes/` | Leitura do PDF, importação da planilha e consultas parametrizadas |
| `output/pdf/` | Documento de regras |
| `outputs/base-inicial/` | Planilha da carteira |

Dependências principais: `openpyxl` e `pypdf`, com SQLite e HTTP da biblioteca padrão do Python. A busca documental padrão é textual. Os módulos opcionais de busca semântica utilizam `requirements-embeddings.txt` e pesos preparados separadamente; não são necessários para executar o chat.

## Limites da demonstração

- A prévia atende uma consulta por vez, em loopback, sem autenticação ou controle de acesso por usuário. Não é uma implantação para uso corporativo.
- O limite atual é de dez turnos concluídos por conversa. Ao atingir esse limite, inicie uma nova conversa.
- Perguntas, histórico limitado, trechos e resultados consultados são enviados ao Gemini para gerar respostas. Utilize apenas os materiais fictícios desta demonstração.
- A interpretação do recorte, a escolha das ferramentas e o texto dependem do modelo. Referências válidas e formato correto não garantem fidelidade de toda resposta; os resultados devem ser conferidos nas fontes.
- Sem chave, cota ou disponibilidade do provedor, o chat informa a limitação. As consultas diretas à camada `fontes/` continuam disponíveis.
