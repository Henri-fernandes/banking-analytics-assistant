"""Extração de seções e recuperação textual com evidências de origem."""
import hashlib
import re
import sqlite3
import unicodedata
from pathlib import Path

from pypdf import PdfReader

STOPWORDS=set('a o as os um uma uns umas de da do das dos e em no na nos nas ao aos por para com que qual quais como quando quanto quantos era eram esta este esse essa isso se ser sao tem ter fica depois antes exatamente documento regra regras funciona funcionar'.split())

def normalizar(text):
    return ''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if not unicodedata.combining(c))

class Documento:
    def __init__(self,path):
        self.path=Path(path)
        raw=self.path.read_bytes()
        if len(raw)>10_000_000: raise ValueError('fonte_invalida: PDF excede 10 MB')
        self.assinatura=hashlib.sha256(raw).hexdigest()
        self.secoes=[];self.trechos=[]
        try:
            reader=PdfReader(self.path)
            if len(reader.pages)>100: raise ValueError('PDF excede 100 páginas')
            current=None;intro=[]
            for page_number,page in enumerate(reader.pages,1):
                if len(page.get_contents().get_data())>8_000_000: raise ValueError('Conteúdo de página excessivo')
                lines=page.extract_text(extraction_mode='layout').splitlines()
                nonempty=[i for i,line in enumerate(lines) if line.strip()]
                if nonempty and lines[nonempty[-1]].strip()==str(page_number): lines[nonempty[-1]]=''
                buffer=[]
                def flush():
                    if buffer:
                        text=' '.join(buffer).strip()
                        if current is not None:
                            current['blocos'].append((page_number,text))
                            if page_number not in current['paginas']: current['paginas'].append(page_number)
                        else: intro.append(text)
                        buffer.clear()
                for line in lines:
                    line=line.strip()
                    match=re.fullmatch(r'\d{1,2}\.\s+[^.]+',line)
                    if match:
                        flush()
                        current={'titulo':line,'paginas':[page_number],'blocos':[]}
                        self.secoes.append(current)
                    elif line: buffer.append(line)
                    else: flush()
                flush()
            if not self.secoes or not any(s['blocos'] for s in self.secoes): raise ValueError('PDF sem seções/texto extraível')
            found=re.search(r'Versão\s+([0-9.]+)', ' '.join(intro))
            self.versao=found.group(1).rstrip('.') if found else 'nao_identificada'
        except Exception as exc:
            raise ValueError(f'fonte_invalida: leitura do PDF: {exc}') from exc
        for section in self.secoes:
            groups=[];parts=[];pages=[]
            for page,text in section['blocos']:
                for segment in (text[i:i+1600] for i in range(0,len(text),1600)):
                    if sum(len(p) for p in parts)+len(segment)>1600 and parts:
                        groups.append((parts,pages));parts=[];pages=[]
                    parts.append(segment.strip())
                    if page not in pages: pages.append(page)
            if parts: groups.append((parts,pages))
            for parts,pages in groups:
                self.trechos.append({'id':f'{self.assinatura[:12]}-{len(self.trechos)+1}', 'documento':self.path.name,
                    'versao':self.versao,'fonte_sha256':self.assinatura,'secao':section['titulo'],
                    'paginas':pages,'texto':'\n\n'.join(parts)})
        self._conn=sqlite3.connect(':memory:')
        try:
            self._conn.execute('CREATE VIRTUAL TABLE trechos USING fts5(titulo,texto,tokenize="unicode61 remove_diacritics 2")')
            self._conn.executemany('INSERT INTO trechos(rowid,titulo,texto) VALUES(?,?,?)',
                [(i+1,normalizar(t['secao']),normalizar(t['texto'])) for i,t in enumerate(self.trechos)])
            self._conn.commit();self._conn.execute('PRAGMA query_only=ON')
            self.metodo='sqlite_fts5'
        except sqlite3.OperationalError:
            self._conn.close();self._conn=None;self.metodo='lexical_memoria'

    def buscar(self,pergunta,limite=5):
        if not isinstance(pergunta,str) or not pergunta.strip() or len(pergunta)>2000:
            raise ValueError('filtro_invalido: pergunta deve ter de 1 a 2.000 caracteres')
        if type(limite) is not int or not 1<=limite<=5: raise ValueError('filtro_invalido: limite de 1 a 5')
        if hashlib.sha256(self.path.read_bytes()).hexdigest()!=self.assinatura: raise ValueError('fonte_alterada: reconstrua o índice')
        terms=list(dict.fromkeys(t for t in re.findall(r'[a-z0-9]+',normalizar(pergunta)) if t not in STOPWORDS and len(t)>1))
        ranked=[]
        if terms and self._conn:
            query=' OR '.join('"'+term+'"'+('*' if len(term)>=4 else '') for term in terms)
            ranked=list(self._conn.execute('SELECT rowid,bm25(trechos,4.0,1.0) AS score FROM trechos WHERE trechos MATCH ? ORDER BY score,rowid LIMIT ?', (query,limite)))
        elif terms:
            for i,chunk in enumerate(self.trechos):
                words=re.findall(r'[a-z0-9]+',normalizar(chunk['secao']+' '+chunk['texto']))
                score=sum(any(w.startswith(t) if len(t)>=4 else w==t for w in words) for t in terms)
                if score: ranked.append((i+1,-score))
            ranked=sorted(ranked,key=lambda item:(item[1],item[0]))[:limite]
        return {'status':'ok' if ranked else 'sem_resultado','metodo':self.metodo,
            'trechos':[{**self.trechos[i-1],'pontuacao_lexical':score} for i,score in ranked],
            'fonte_sha256':self.assinatura}
