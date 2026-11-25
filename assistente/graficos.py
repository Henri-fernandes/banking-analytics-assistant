"""Projeção visual calculada exclusivamente a partir de uma consulta de série."""
from decimal import Decimal

def grafico_over(evidence,tipo='linhas'):
    if tipo not in ('linhas','colunas'):
        raise ValueError('resposta_nao_fundamentada: tipo de gráfico não suportado')
    output=evidence['resultado']
    if evidence['ferramenta']!='consultar_carteira' or evidence['argumentos'].get('ferramenta')!='serie_over' or output['status']!='ok':
        raise ValueError('resposta_nao_fundamentada: gráfico exige série consultada')
    rows=output['linhas']
    if not rows or len(rows)>180: raise ValueError('resposta_nao_fundamentada: série vazia ou excessiva')
    series=[]
    for limit in sorted({r['limiar'] for r in rows}):
        points=[]
        for row in rows:
            if row['limiar']!=limit: continue
            den=row['denominador_centavos'];num=row['numerador_centavos']
            if type(den) is not int or type(num) is not int or not 0<=num<=den:
                raise ValueError('resposta_nao_fundamentada: componentes da série inválidos')
            points.append({'referencia':row['referencia'],'valor':float(Decimal(num)*100/Decimal(den)) if den else None})
        series.append({'nome':f'Over{limit}','pontos':points})
    filters=output['filtros']
    return {'tipo':tipo,'titulo':'Evolução dos indicadores Over','series':series,
            'publico':filters.get('publico') or 'PF e PJ','filial':filters.get('filial')}
