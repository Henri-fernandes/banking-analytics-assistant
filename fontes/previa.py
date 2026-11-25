"""Prévia local dos materiais. Não expõe diretórios ou arquivos arbitrários."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import socket
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
FILES={'/regras.pdf':(ROOT/'output/pdf/regras_credito_v1.pdf','application/pdf'),
       '/dados.xlsx':(ROOT/'outputs/base-inicial/base_credito_v1.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
PAGINA='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Materiais do projeto</title><main><h1>Materiais do projeto</h1>
<p><a href="/regras.pdf">Abrir regras de crédito em PDF</a></p>
<p><a href="/dados.xlsx">Baixar planilha de dados</a></p>
<p>Prévia local dos arquivos. A conversa desta etapa é executada pelo terminal.</p></main></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=='/': body=PAGINA.encode('utf-8');mime='text/html; charset=utf-8'
        elif path in FILES:
            file,mime=FILES[path]
            try: body=file.read_bytes()
            except OSError: self.send_error(503,'Material indisponivel');return
        else: self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
        if path=='/dados.xlsx': self.send_header('Content-Disposition','attachment; filename="base_credito_v1.xlsx"')
        self.end_headers();self.wfile.write(body)

class Servidor(ThreadingHTTPServer):
    allow_reuse_address=False
    allow_reuse_port=False

    def server_bind(self):
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

def criar_servidor(porta=8501): return Servidor(('127.0.0.1',porta),Handler)

def servir(porta=8501):
    if type(porta) is not int or not 1<=porta<=65535: raise ValueError('filtro_invalido: porta entre 1 e 65535')
    with criar_servidor(porta) as server:
        print(f'Materiais em http://127.0.0.1:{porta}/ | mantenha este terminal aberto',flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
