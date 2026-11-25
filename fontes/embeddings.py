"""Modelo opcional de embeddings em CPU. Somente preparar_modelo acessa a rede."""
import hashlib
import json
import math
import re
from importlib.metadata import version
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODELO='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
REPOSITORIO='Qdrant/paraphrase-multilingual-MiniLM-L12-v2-onnx-Q'
REVISAO='faf4aa4225822f3bc6376869cb1164e8e3feedd0'
CACHE=ROOT/'.tools/modelos/minilm'
ARQUIVOS=['model_optimized.onnx','config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json']

def assinatura(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()

def normalizar_vetor(vetor,dimensao=None):
    try:
        values=[float(x) for x in vetor]
        norma=math.sqrt(sum(x*x for x in values))
        if not values or (dimensao is not None and len(values)!=dimensao) or not math.isfinite(norma) or norma==0:
            raise ValueError()
        return [x/norma for x in values]
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError('vetor_invalido: dimensão, norma ou valores inválidos') from exc

def preparar_modelo(cache_dir=CACHE):
    """Baixa pesos públicos, fixa revisão e registra hashes; não recebe documentos."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise ValueError('modelo_indisponivel: instale requirements-embeddings.txt') from exc
    cache_dir=Path(cache_dir);cache_dir.mkdir(parents=True,exist_ok=True)
    try:
        path=Path(snapshot_download(REPOSITORIO,revision=REVISAO,allow_patterns=ARQUIVOS,
                                   local_dir=cache_dir,token=False))
    except Exception as exc:
        raise ValueError('modelo_indisponivel: falha no download; use busca textual. '+str(exc)) from exc
    manifest={'modelo':MODELO,'repositorio':REPOSITORIO,'revisao':REVISAO,
              'arquivos':{name:assinatura(path/name) for name in ARQUIVOS}}
    (cache_dir/'manifesto.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest

class ModeloLocal:
    def __init__(self,cache_dir=CACHE):
        try:
            from fastembed import TextEmbedding
            from tokenizers import Tokenizer
            path=Path(cache_dir)
            manifest=json.loads((path/'manifesto.json').read_text(encoding='utf-8'))
            if manifest['modelo']!=MODELO or manifest['repositorio']!=REPOSITORIO or manifest['revisao']!=REVISAO:
                raise ValueError('Modelo/revisão diferente')
            if set(manifest['arquivos'])!=set(ARQUIVOS): raise ValueError('Manifesto incompleto')
            for name in ARQUIVOS:
                if assinatura(path/name)!=manifest['arquivos'][name]: raise ValueError('Pesos/configuração alterados')
            self.tokenizer=Tokenizer.from_file(str(path/'tokenizer.json'))
            self.tokenizer.no_padding();self.tokenizer.no_truncation()
            self.model=TextEmbedding(MODELO,specific_model_path=str(path.resolve()),local_files_only=True,
                                     threads=2,providers=['CPUExecutionProvider'])
            self.config={'modelo':MODELO,'revisao':manifest['revisao'],'arquivos':manifest['arquivos'],
                         'fastembed':version('fastembed'),'onnxruntime':version('onnxruntime'),
                         'tokenizers':version('tokenizers'),'limite_tokens':128,'threads':2,
                         'agregacao':'media_janelas_sem_sobreposicao_v1','prefixos':False}
            self.identidade=json.dumps(self.config,sort_keys=True)
        except Exception as exc:
            raise ValueError('modelo_indisponivel: prepare o modelo ou use --metodo textual; '+str(exc)) from exc

    def janelas(self,texto):
        """Preserva todas as palavras; audita cada janela incluindo tokens especiais."""
        parts=[];current=''
        for word in re.findall(r'\S+\s*',texto):
            if len(self.tokenizer.encode(current+word).ids)>128:
                if not current or len(self.tokenizer.encode(word).ids)>128:
                    raise ValueError('fonte_invalida: palavra excede o contexto do modelo')
                parts.append(current);current=word
            else: current+=word
        if current: parts.append(current)
        return parts

    def documentos(self,textos):
        result=[]
        for texto in textos:
            windows=self.janelas(texto)
            vectors=self._codificar(windows)
            if len(vectors)!=len(windows) or not vectors: raise ValueError('vetor_invalido: resposta incompleta')
            result.append(normalizar_vetor([sum(v[i] for v in vectors)/len(vectors) for i in range(384)],384))
        return result

    def pergunta(self,texto):
        if len(self.tokenizer.encode(texto).ids)>128:
            raise ValueError('filtro_invalido: pergunta excede 128 tokens do modelo; reformule ou use busca textual')
        return self._codificar([texto])[0]

    def _codificar(self,textos):
        try:
            vectors=[normalizar_vetor(v,384) for v in self.model.embed(textos,batch_size=8)]
            if len(vectors)!=len(textos): raise ValueError('vetor_invalido: resposta incompleta')
            return vectors
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError('modelo_indisponivel: falha na inferência local; '+str(exc)) from exc
