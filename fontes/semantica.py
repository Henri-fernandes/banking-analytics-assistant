"""Recuperação semântica e fusão por posição, com cache reconstruível."""
import hashlib
import json
import tempfile
from pathlib import Path

from fontes.documentos import Documento
from fontes.embeddings import ModeloLocal,normalizar_vetor

class BuscaSemantica:
    def __init__(self,pdf,backend=None,cache_dir=None):
        self.documento=Documento(pdf)
        self.backend=backend if backend is not None else ModeloLocal()
        chunks=self.documento.trechos
        payload={'algoritmo':'coseno_rrf60_v1','fonte':self.documento.assinatura,
                 'trechos':chunks,'backend':self.backend.identidade}
        self.chave=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        directory=Path(cache_dir) if cache_dir is not None else Path(__file__).resolve().parents[1]/'.tools/indices'
        directory.mkdir(parents=True,exist_ok=True)
        cache=directory/(self.chave+'.json')
        def validar(vectors):
            if not isinstance(vectors,list) or len(vectors)!=len(chunks): raise ValueError('vetor_invalido: quantidade')
            result=[normalizar_vetor(v) for v in vectors]
            if len({len(v) for v in result})!=1: raise ValueError('vetor_invalido: dimensões diferentes')
            return result
        try:
            stored=json.loads(cache.read_text(encoding='utf-8'))
            if stored['chave']!=self.chave: raise ValueError('cache incompatível')
            self.vetores=validar(stored['vetores'])
        except (OSError,ValueError,KeyError,TypeError):
            self.vetores=validar(self.backend.documentos([t['secao']+'\n'+t['texto'] for t in chunks]))
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=directory,delete=False) as f:
                json.dump({'chave':self.chave,'vetores':self.vetores},f,allow_nan=False)
                temporary=Path(f.name)
            temporary.replace(cache)

    def buscar(self,pergunta,limite=5,metodo='semantica'):
        if metodo not in ('semantica','hibrida'): raise ValueError('filtro_invalido: método desconhecido')
        # A busca textual aplica os mesmos limites e verifica a assinatura da fonte.
        lexical=self.documento.buscar(pergunta,limite=limite)
        vector=normalizar_vetor(self.backend.pergunta(pergunta),len(self.vetores[0]))
        scores=[sum(a*b for a,b in zip(vector,v)) for v in self.vetores]
        ranking=sorted(range(len(scores)),key=lambda i:(-scores[i],i))[:limite]
        semantic=[{**self.documento.trechos[i],'similaridade_cosseno':scores[i]} for i in ranking]
        result=semantic
        if metodo=='hibrida':
            merged={};fusion={}
            for lista in (semantic,lexical['trechos']):
                for rank,chunk in enumerate(lista,1):
                    id_=chunk['id'];merged[id_]={**merged.get(id_,{}),**chunk}
                    fusion[id_]=fusion.get(id_,0)+1/(60+rank)
            result=[{**merged[id_],'pontuacao_fusao':fusion[id_]} for id_ in
                    sorted(merged,key=lambda id_:(-fusion[id_],id_))[:limite]]
        return {'status':'ok' if result else 'sem_resultado','metodo':metodo,'trechos':result,
                'fonte_sha256':self.documento.assinatura,'indice_sha256':self.chave,
                'aviso':'Ranking de recuperação; pontuações não medem confiança na resposta.'}
