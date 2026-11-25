"""Transporte REST do Gemini. Sem retries, ferramentas remotas ou segredo no URL."""
import getpass
import json
import os
from pathlib import Path
import socket
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'.env'
MODELO='gemini-3.5-flash-lite'

def validar_chave(chave,minimo=1):
    # A chave é opaca: aceitar formatos novos sem assumir prefixo ou alfabeto antigo.
    # Limitar tamanho e recusar caracteres que não podem compor um cabeçalho HTTP.
    if not isinstance(chave,str) or not minimo<=len(chave)<=4096 or any(not 33<=ord(c)<=126 for c in chave):
        raise ValueError('credencial_invalida: formato de chave inválido')

def configurar(path=CONFIG):
    path=Path(path)
    if path.exists(): raise ValueError('configuracao_existente: edite o .env local; ele não será sobrescrito')
    key=getpass.getpass('Chave Gemini do projeto Free (entrada oculta): ').strip()
    validar_chave(key,minimo=20)
    # A conta Free foi informada pelo autor; isso não verifica faturamento na API.
    with path.open('x',encoding='utf-8') as stream:
        stream.write('GEMINI_API_KEY='+key+'\nGEMINI_FREE_TIER_CONFIRMED=1\n')

class SemRedirecionamento(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ValueError('modelo_indisponivel: redirecionamento HTTP recusado')

class Gemini:
    def __init__(self,chave=None,gratuito=None,config=CONFIG):
        values={}
        if chave is None:
            try:
                for line in Path(config).read_text(encoding='utf-8-sig').splitlines():
                    if '=' in line and not line.lstrip().startswith('#'):
                        k,v=line.split('=',1);values[k.strip()]=v.strip()
            except FileNotFoundError: pass
            chave=os.environ.get('GEMINI_API_KEY') or values.get('GEMINI_API_KEY')
            if gratuito is None:
                gratuito=(os.environ.get('GEMINI_FREE_TIER_CONFIRMED') or values.get('GEMINI_FREE_TIER_CONFIRMED'))=='1'
        if not chave: raise ValueError('modelo_nao_configurado: execute python -m assistente configurar no seu terminal')
        validar_chave(chave)
        if not gratuito: raise ValueError('plano_nao_confirmado: use chave de projeto Free sem faturamento; consulte o README')
        self.chave=chave;self.uso={};self.modelo_efetivo=MODELO

    def gerar(self,contents,declaracoes,instrucao):
        payload={'systemInstruction':{'parts':[{'text':instrucao}]},'contents':contents,
                 'tools':[{'functionDeclarations':declaracoes}],
                 'generationConfig':{'temperature':0,'maxOutputTokens':2048}}
        data=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8')
        request=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent',
                data=data,headers={'Content-Type':'application/json','x-goog-api-key':self.chave},method='POST')
        try:
            # urlopen mantém o contexto TLS padrão. O handler bloqueia envio da chave a outro host.
            opener=urllib.request.build_opener(SemRedirecionamento())
            with opener.open(request,timeout=20) as response: raw=response.read(1_000_001)
        except urllib.error.HTTPError as exc:
            status={400:'requisicao_modelo_invalida',401:'credencial_invalida',403:'acesso_modelo_negado',429:'cota_esgotada'}.get(exc.code,'modelo_indisponivel')
            raise ValueError(status+': chamada interrompida; sem repetição automática') from None
        except (urllib.error.URLError,TimeoutError,socket.timeout,OSError):
            raise ValueError('modelo_indisponivel: falha de rede ou tempo excedido') from None
        try:
            if len(raw)>1_000_000: raise ValueError('Resposta excessiva')
            result=json.loads(raw)
            candidate=result['candidates'][0]
            if candidate.get('finishReason')!='STOP': raise ValueError('Resposta não concluída')
            content=candidate['content']
            if content.get('role')!='model' or not isinstance(content.get('parts'),list) or not content['parts']:
                raise ValueError('Conteúdo ausente')
            self.uso=result.get('usageMetadata',{})
            self.modelo_efetivo=result.get('modelVersion',MODELO)
            return content
        except (ValueError,KeyError,IndexError,TypeError,UnicodeError):
            raise ValueError('resposta_modelo_invalida: resposta ausente, incompleta ou fora do formato') from None
