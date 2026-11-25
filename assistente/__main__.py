"""Comandos locais; a chave é configurada diretamente no terminal do autor."""
import argparse
import sys

def main(argv=None):
    parser=argparse.ArgumentParser(description='Assistente local de crédito')
    parser.add_argument('acao',choices=['configurar','conversar','servir'])
    parser.add_argument('--json',action='store_true',help='Exibe resposta estruturada, resultados e rastros de execução')
    parser.add_argument('--porta',type=int,default=8501,help='Porta da prévia de chat local')
    args=parser.parse_args(argv)
    try:
        if args.acao=='configurar':
            from assistente.gemini import configurar
            configurar();print('Chave salva no .env local, ignorado pelo Git. Nenhuma chamada foi realizada.')
        elif args.acao=='servir':
            from assistente.web import servir
            servir(args.porta)
        else:
            from assistente.conversa import terminal
            return terminal(detalhes=args.json)
    except (ValueError,OSError) as exc:
        print(str(exc));return 2
    return 0

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
