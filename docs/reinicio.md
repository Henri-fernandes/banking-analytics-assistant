# Recomeço solicitado pelo autor

Data: 10/11/2026.

## Motivo e autorização

O autor rejeitou a interface de painel como direção do produto e solicitou: “Apague isso no rep, e vamos começar do zero... Por partes”. A remoção corresponde à implementação daquela prova; o objetivo, as decisões e as pesquisas são preservados para não perder o contexto.

## Escopo da remoção

- `app.py` e configuração visual/exemplo de secrets do Streamlit.
- Módulos `financeiro/`, script de referência pública e testes da prova.
- Requisitos Python e lock da implementação retirada.
- Amostras sintéticas e snapshot público que alimentavam o painel.

Arquivos locais ignorados, como ambientes e ferramentas de desenvolvimento, não fazem parte do repositório e não foram apagados. O histórico do Git foi preservado; `afc1077` identifica a última versão publicada da prova antes deste recomeço. A remoção ocorre por novo commit, sem reescrever commits anteriores ou excluir o repositório GitHub.

## Documentos preservados

Contexto, escopo, glossário, restrições, ADR da aplicação própria e pesquisa permanecem como referências. Os relatórios de avaliação, plano/especificação, regras da amostra e guia operacional anteriores são registros históricos, marcados como tal. Regras particulares da amostra não passam automaticamente a políticas da nova base.

Overs inclusivos, produtos iniciais, abordagem híbrida, custo adicional zero e execução na nuvem continuam confirmados. O recomeço não aprova uma nova stack, volume, histórico ou regra financeira adicional.

## Operação e verificação

Não existe comando de execução ou suíte ativa nesta versão. A verificação da remoção confere o diff, ausência dos arquivos retirados e links da documentação; não reutiliza os 37 testes históricos como prova de uma nova aplicação.

A configuração antiga do Community Cloud aponta para `app.py`, agora removido. A instância remota não foi administrada/excluída nesta operação; seu estado após a atualização precisa ser observado no serviço. Uma cópia ainda carregada no navegador pode corresponder à versão anterior.

## Próxima conversa

Confirmar o entendimento do produto e discutir apenas a primeira parte: perguntas representativas, fontes necessárias, modelo dos dados e inventário dos documentos. A construção seguinte depende da especificação desse recorte.
