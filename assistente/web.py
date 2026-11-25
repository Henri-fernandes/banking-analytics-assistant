"""Prévia de chat em loopback, com histórico local e projeção pública das respostas."""
from http.cookies import SimpleCookie,CookieError
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import logging
from pathlib import Path
import re
import secrets
import socket
import time
from datetime import datetime,timezone
from urllib.parse import urlsplit

from assistente.conversa import Conversa
from assistente.historico import HistoricoLocal,RETENCAO
from fontes.previa import FILES

STATIC=Path(__file__).resolve().parent/'static'
HISTORICO=STATIC.parents[1]/'.tools/chat/conversas.sqlite'
ASSETS={'/':('chat.html','text/html; charset=utf-8'),'/chat.css':('chat.css','text/css; charset=utf-8'),
        '/chat.js':('chat.js','text/javascript; charset=utf-8'),'/formatacao.js':('formatacao.js','text/javascript; charset=utf-8'),
        '/graficos.js':('graficos.js','text/javascript; charset=utf-8')}
ERROS={
    'modelo_nao_configurado':'A conexão com o assistente ainda não foi configurada neste computador.',
    'plano_nao_confirmado':'A configuração da conta gratuita precisa ser confirmada neste computador.',
    'cota_esgotada':'A cota gratuita foi atingida. Aguarde a renovação para continuar.',
    'credencial_invalida':'Não foi possível autenticar a conexão com o assistente.',
    'acesso_modelo_negado':'A conta não tem acesso ao modelo configurado.',
    'fonte_alterada':'Os arquivos da base mudaram. Inicie uma nova conversa.',
    'limite_sessao':'Esta conversa atingiu o limite de mensagens. Inicie uma nova conversa.',
    'limite_contexto':'A conversa ficou extensa. Inicie uma nova conversa com um recorte mais específico.',
    'resposta_nao_fundamentada':'Não consegui conferir a resposta com os dados disponíveis. Reformule a pergunta.',
    'modelo_indisponivel':'A conexão com o assistente falhou ou demorou demais. Sua pergunta permanece no campo para tentar novamente.',
    'resposta_modelo_invalida':'O assistente não devolveu uma resposta completa no formato esperado. Sua pergunta permanece no campo para tentar novamente.',
    'limite_execucao':'Não consegui concluir a análise dentro do limite desta consulta. Tente uma pergunta mais específica.',
    'erro_interno':'Não foi possível concluir esta consulta.',
    'historico_indisponivel':'Não foi possível acessar o histórico salvo. Confira o armazenamento local antes de continuar.',
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass

    def _falha_consulta(self,status,code,execution=None):
        # Registrar somente metadados permitidos, sem pergunta, resposta, chave ou exceção.
        code=code if code in ERROS else 'erro_interno'
        entry={'evento':'falha_consulta','referencia':secrets.token_hex(8),'status':code,
               'instante':datetime.now(timezone.utc).isoformat()}
        if isinstance(execution,dict):
            for key in ('chamadas_modelo','ferramentas'):
                value=execution.get(key)
                if type(value) is int and 0<=value<=100: entry[key]=value
            duration=execution.get('duracao_segundos')
            if type(duration) in (int,float) and 0<=duration<=3600: entry['duracao_segundos']=round(duration,3)
        logging.getLogger(__name__).warning(json.dumps(entry,ensure_ascii=False))
        self._enviar(status,{'erro':ERROS[code],'referencia':entry['referencia']})

    def setup(self):
        super().setup();self.connection.settimeout(10)

    def _permitido(self):
        port=self.server.server_port
        allowed={f'127.0.0.1:{port}',f'localhost:{port}'}
        return self.headers.get('Host') in allowed and self.headers.get('Sec-Fetch-Site')!='cross-site'

    def _enviar(self,status,body,mime='application/json; charset=utf-8',cookie=None):
        if not isinstance(body,bytes): body=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        for key,value in {'Content-Type':mime,'Content-Length':str(len(body)),'Cache-Control':'no-store',
                          'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY',
                          'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"}.items():
            self.send_header(key,value)
        if cookie: self.send_header('Set-Cookie',f'credito_sid={cookie}; HttpOnly; SameSite=Strict; Path=/; Max-Age={RETENCAO}')
        self.end_headers();self.wfile.write(body)

    def _sessao(self,criar=False):
        now=time.monotonic()
        for key in list(self.server.sessions):
            if now-self.server.sessions[key]['acesso']>1800: del self.server.sessions[key]
        try:
            cookie=SimpleCookie(self.headers.get('Cookie',''))
            sid=cookie['credito_sid'].value if 'credito_sid' in cookie else None
        except CookieError: sid=None
        if sid is not None and not re.fullmatch(r'[A-Za-z0-9_-]{43}',sid): sid=None
        if sid in self.server.sessions:
            session=self.server.sessions[sid];session['acesso']=now
            return sid,session
        if len(self.server.sessions)>=16: return None,None
        if sid and self.server.store:
            saved=self.server.store.carregar(sid)
            if saved is not None:
                self.server.sessions[sid]={**saved,'csrf':secrets.token_urlsafe(32),'conversa':None,'acesso':now}
                return sid,self.server.sessions[sid]
        if not criar: return None,None
        sid=secrets.token_urlsafe(32)
        self.server.sessions[sid]={'csrf':secrets.token_urlsafe(32),'mensagens':[],'conversa':None,'estado_agente':None,'acesso':now}
        return sid,self.server.sessions[sid]

    def _salvar(self,sid,session):
        if self.server.store:
            self.server.store.salvar(sid,{'mensagens':session['mensagens'],'estado_agente':session['estado_agente']})

    def do_GET(self):
        if not self._permitido(): self._enviar(403,{'erro':'Endereço não permitido.'});return
        path=urlsplit(self.path).path
        if path=='/api/conversa':
            try:
                sid,s=self._sessao(criar=True)
                if s is not None: self._salvar(sid,s)
            except ValueError:
                self._falha_consulta(503,'historico_indisponivel');return
            if s is None: self._enviar(503,{'erro':'Há muitas sessões locais abertas. Tente novamente mais tarde.'});return
            self._enviar(200,{'csrf':s['csrf'],'mensagens':s['mensagens']},cookie=sid);return
        if path in ASSETS:
            name,mime=ASSETS[path]
            self._enviar(200,(STATIC/name).read_bytes(),mime);return
        if path in FILES:
            file,mime=FILES[path]
            try: body=file.read_bytes()
            except OSError: self._enviar(503,{'erro':'Material indisponível.'});return
            self._enviar(200,body,mime);return
        self._enviar(404,{'erro':'Página não encontrada.'})

    def do_POST(self):
        if not self._permitido(): self._enviar(403,{'erro':'Endereço não permitido.'});return
        path=urlsplit(self.path).path
        if path not in ('/api/mensagem','/api/nova'): self._enviar(404,{'erro':'Página não encontrada.'});return
        origins={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
        try: sid,s=self._sessao()
        except ValueError: self._falha_consulta(503,'historico_indisponivel');return
        token=self.headers.get('X-CSRF-Token','')
        if s is None or self.headers.get('Origin') not in origins or not secrets.compare_digest(token,s['csrf']):
            self._enviar(403,{'erro':'A sessão expirou. Atualize a página para continuar.'});return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=12_000 or self.headers.get_content_type()!='application/json': raise ValueError()
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict): raise ValueError()
            if path=='/api/nova':
                if body: raise ValueError()
            elif set(body)!={'mensagem'} or not isinstance(body['mensagem'],str) or not 1<=len(body['mensagem'].strip())<=2000:
                raise ValueError()
        except (ValueError,UnicodeError,OSError):
            self._enviar(400,{'erro':'Escreva uma mensagem de até 2.000 caracteres.'});return
        if path=='/api/nova':
            cleared={**s,'conversa':None,'mensagens':[],'estado_agente':None}
            try: self._salvar(sid,cleared)
            except ValueError: self._falha_consulta(503,'historico_indisponivel');return
            s.update(cleared);self._enviar(200,{'mensagens':[]});return
        question=body['mensagem'].strip()
        try:
            if s['conversa'] is None:
                conversation=self.server.factory()
                if s['estado_agente'] is not None: conversation.restaurar_estado(s['estado_agente'])
                s['conversa']=conversation
            result=s['conversa'].perguntar(question)
            if result['status']!='ok':
                code=result['status'];status=429 if code=='cota_esgotada' else 422
                self._falha_consulta(status,code,result.get('execucao'));return
            answer=result['resposta']
            # Projeção explícita: nunca enviar evidências, SQL ou rastros ao navegador.
            message=re.sub(r'\[T\d+E\d+\]','',answer['mensagem']).strip()
            graph={key:result[key] for key in ('grafico','graficos') if key in result}
            updated={**s,'mensagens':s['mensagens']+[{'papel':'usuario','texto':question},{'papel':'assistente','texto':message,**graph}],
                     'estado_agente':s['conversa'].exportar_estado() if self.server.store else None}
            self._salvar(sid,updated)
            s.update(updated)
            self._enviar(200,{'mensagem':message,'tipo':answer['tipo'],**graph})
        except ValueError as exc:
            if str(exc).startswith('historico_indisponivel:'): s['conversa']=None
            self._falha_consulta(503,str(exc).split(':')[0])
        except Exception:
            self._falha_consulta(500,'erro_interno')

class Servidor(HTTPServer):
    # Prévia local: uma requisição por vez mantém cada conexão SQLite na mesma thread.
    # Atendimento concorrente exige outra gestão de conexões e avaliação antes do deploy.
    allow_reuse_address=False
    allow_reuse_port=False
    def server_bind(self):
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'): self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

def criar_servidor(porta=8501,factory=Conversa,armazenamento=None):
    store=HistoricoLocal(armazenamento) if armazenamento else None
    server=Servidor(('127.0.0.1',porta),Handler)
    server.sessions={};server.factory=factory
    server.store=store
    return server

def servir(porta=8501):
    if type(porta) is not int or not 1<=porta<=65535: raise ValueError('Porta inválida.')
    with criar_servidor(porta,armazenamento=HISTORICO) as server:
        print(f'Conversa em http://127.0.0.1:{porta}/',flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
