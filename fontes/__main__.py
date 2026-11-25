"""Interface local para consultar fontes com filtros explícitos."""
import argparse
import json
import sys
from pathlib import Path

from fontes.carteira import Carteira
from fontes.documentos import Documento

ROOT=Path(__file__).resolve().parents[1]

def main(argv=None):
    parser=argparse.ArgumentParser(description='Busca documental e consultas locais de leitura. Sem modelo gerador.')
    parser.add_argument('--pdf',type=Path,default=ROOT/'output/pdf/regras_credito_v1.pdf')
    parser.add_argument('--planilha',type=Path,default=ROOT/'outputs/base-inicial/base_credito_v1.xlsx')
    actions=parser.add_subparsers(dest='acao',required=True)
    search=actions.add_parser('buscar',help='Localiza trechos do PDF')
    search.add_argument('pergunta');search.add_argument('--limite',type=int,default=5)
    search.add_argument('--metodo',choices=['textual','semantica','hibrida'],default='textual')
    actions.add_parser('preparar-modelo',help='Baixa os pesos públicos do modelo opcional de embeddings')
    preview=actions.add_parser('servir',help='Abre prévia local do PDF e da planilha')
    preview.add_argument('--porta',type=int,default=8501)
    tools=actions.add_parser('consultar',help='Executa uma ferramenta fixa de leitura').add_subparsers(dest='ferramenta',required=True)
    for tool in ['saldo','over','contratos','renegociacoes','concessoes','propostas','safras']:
        sub=tools.add_parser(tool)
        if tool in ('saldo','over','contratos'): sub.add_argument('--referencia',required=True)
        if tool in ('saldo','over'):
            sub.add_argument('--publico',choices=['PF','PJ']);sub.add_argument('--filial')
        if tool in ('over','safras'): sub.add_argument('--limiar',type=int,default=90)
        if tool=='contratos': sub.add_argument('--id',dest='ids',action='append',required=True)
        if tool in ('renegociacoes','concessoes'):
            sub.add_argument('--inicio');sub.add_argument('--fim')
        if tool=='propostas': sub.add_argument('--situacao',choices=['CONTRATADA','APROVADA_NAO_CONTRATADA','RECUSADA','EM_ANALISE'])
        if tool=='safras':
            sub.add_argument('--safra',dest='safras',action='append',required=True);sub.add_argument('--mob',type=int,required=True)
    args=vars(parser.parse_args(argv));action=args.pop('acao');pdf=args.pop('pdf');planilha=args.pop('planilha')
    try:
        if action=='servir':
            from fontes.previa import servir
            servir(**args);return 0
        elif action=='preparar-modelo':
            from fontes.embeddings import preparar_modelo
            result={'status':'ok',**preparar_modelo()}
        elif action=='buscar':
            method=args.pop('metodo')
            if method=='textual': result=Documento(pdf).buscar(**args)
            else:
                from fontes.semantica import BuscaSemantica
                result=BuscaSemantica(pdf).buscar(**args,metodo=method)
        else:
            tool=args.pop('ferramenta')
            with Carteira(planilha) as source: result=source.consultar(tool,**{k:v for k,v in args.items() if v is not None})
    except (OSError,ValueError) as exc:
        result={'status':'fonte_invalida' if not str(exc).startswith(('filtro_invalido','fonte_alterada','modelo_indisponivel','vetor_invalido')) else str(exc).split(':')[0],'erro':str(exc)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status'] in ('ok','sem_resultado','sem_populacao','sem_cobertura') else 2

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
