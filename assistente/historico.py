"""Histórico da prévia local, separado por sessão e fora do pacote público."""
import hashlib
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import time

RETENCAO=7*86400

class HistoricoLocal:
    def __init__(self,path):
        self.path=Path(path)
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with closing(sqlite3.connect(self.path)) as conn,conn:
                conn.execute('CREATE TABLE IF NOT EXISTS sessoes (chave TEXT PRIMARY KEY, atualizado REAL NOT NULL, conteudo TEXT NOT NULL)')
        except (sqlite3.Error,OSError):
            raise ValueError('historico_indisponivel: não foi possível abrir o histórico local') from None

    def carregar(self,sid):
        key=hashlib.sha256(sid.encode()).hexdigest()
        try:
            with closing(sqlite3.connect(self.path)) as conn,conn:
                conn.execute('DELETE FROM sessoes WHERE atualizado < ?',(time.time()-RETENCAO,))
                row=conn.execute('SELECT conteudo FROM sessoes WHERE chave=?',(key,)).fetchone()
            if row is None: return None
            if len(row[0])>2_000_000: raise ValueError()
            data=json.loads(row[0])
            if not isinstance(data,dict) or set(data)!={'mensagens','estado_agente'} or not isinstance(data['mensagens'],list) or len(data['mensagens'])>20:
                raise ValueError()
            if any(not isinstance(m,dict) or m.get('papel') not in ('usuario','assistente') or not isinstance(m.get('texto'),str) for m in data['mensagens']):
                raise ValueError()
            return data
        except (sqlite3.Error,OSError,ValueError,TypeError):
            raise ValueError('historico_indisponivel: não foi possível ler o histórico local') from None

    def salvar(self,sid,data):
        try:
            raw=json.dumps(data,ensure_ascii=False,allow_nan=False)
            if len(raw)>2_000_000: raise ValueError()
            key=hashlib.sha256(sid.encode()).hexdigest()
            with closing(sqlite3.connect(self.path)) as conn,conn:
                conn.execute('DELETE FROM sessoes WHERE atualizado < ?',(time.time()-RETENCAO,))
                conn.execute('INSERT INTO sessoes VALUES (?,?,?) ON CONFLICT(chave) DO UPDATE SET atualizado=excluded.atualizado,conteudo=excluded.conteudo',
                             (key,time.time(),raw))
        except (sqlite3.Error,OSError,ValueError,TypeError):
            raise ValueError('historico_indisponivel: não foi possível salvar o histórico local') from None
