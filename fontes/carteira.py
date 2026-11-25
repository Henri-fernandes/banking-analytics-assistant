"""Importação da planilha de valores e consultas analíticas somente leitura."""
import calendar
import hashlib
import math
import sqlite3
import time
from datetime import date,datetime
from decimal import Decimal
from pathlib import Path

import openpyxl

SCHEMA={
 'clientes':'cliente_id nome_ficticio publico filial_id',
 'produtos':'produto_id nome publico taxa_mensal limite_principal parcelas',
 'propostas':'proposta_id cliente_id produto_id data_proposta valor_solicitado cadastro_validado capacidade_validada parecer_favoravel aceite_cliente situacao origem',
 'contratos':'contrato_id proposta_id cliente_id produto_id filial_id publico data_originacao principal_contratado taxa_mensal numero_parcelas primeiro_vencimento tipo_origem contrato_anterior desembolso_novo',
 'parcelas':'parcela_id contrato_id numero vencimento principal_previsto juros_previstos total_previsto',
 'pagamentos':'alocacao_id evento_id contrato_id parcela_id data_pagamento principal_pago juros_pagos total_pago natureza juros_dispensados',
 'renegociacoes':'renegociacao_id contrato_anterior contrato_novo data_efetivacao principal_transferido desconto_principal juros_vencidos_perdoados dinheiro_novo motivo',
 'posicoes':'referencia contrato_id cliente_id produto_id publico filial_id safra_contrato safra_relacionamento mob principal_contratado principal_amortizado principal_transferido saldo_principal juros_vencidos_pendentes saldo_devedor vencimento_mais_antigo dias_atraso situacao tipo_origem',
}
MONEY=set('limite_principal valor_solicitado principal_contratado desembolso_novo principal_previsto juros_previstos total_previsto principal_pago juros_pagos total_pago juros_dispensados principal_transferido desconto_principal juros_vencidos_perdoados dinheiro_novo principal_amortizado saldo_principal juros_vencidos_pendentes saldo_devedor'.split())
INTEGERS={'parcelas','numero_parcelas','numero','mob','dias_atraso'}
DATES={'data_proposta','data_originacao','primeiro_vencimento','vencimento','data_pagamento','data_efetivacao','referencia','safra_contrato','safra_relacionamento','vencimento_mais_antigo'}

def iso(value):
    if isinstance(value,(date,datetime)): return value.strftime('%Y-%m-%d')
    if not isinstance(value,str) or len(value)!=10 or date.fromisoformat(value).isoformat()!=value: raise ValueError('Data inválida')
    return value

class Carteira:
    def __init__(self,path):
        self.path=Path(path)
        self.assinatura=hashlib.sha256(self.path.read_bytes()).hexdigest()
        self._conn=sqlite3.connect(':memory:');self._conn.row_factory=sqlite3.Row
        self.contagens={};self._tables={}
        book=None
        try:
            if self.path.stat().st_size>10_000_000: raise ValueError('Planilha excede 10 MB')
            book=openpyxl.load_workbook(self.path,read_only=True,data_only=False)
            if {s.lower() for s in book.sheetnames}!=set(SCHEMA): raise ValueError('Abas diferentes do contrato de dados')
            for sheet in book:
                name=sheet.title.lower();keys=SCHEMA[name].split();rows=sheet.iter_rows(values_only=True)
                if list(next(rows))!=keys: raise ValueError(f'Cabeçalhos inválidos: {name}')
                cols=[k+'_centavos' if k in MONEY else k for k in keys]
                types=['INTEGER' if k in MONEY|INTEGERS else 'REAL' if k=='taxa_mensal' else 'TEXT' for k in keys]
                self._conn.execute(f'CREATE TABLE {name} ('+', '.join(f'{k} {t}' for k,t in zip(cols,types))+')')
                records=[];seen=set()
                for row in rows:
                    if all(v is None for v in row): continue
                    if len(records)>=100_000: raise ValueError('Limite de registros por aba')
                    result={}
                    for k,v in zip(keys,row):
                        if v is None:
                            if k not in ('contrato_anterior','vencimento_mais_antigo'): raise ValueError(f'Campo ausente: {name}.{k}')
                        elif k in MONEY:
                            if type(v) not in (int,float) or not math.isfinite(v): raise ValueError('Valor monetário inválido')
                            cents=Decimal(str(v))*100
                            if cents<0 or cents!=cents.to_integral_value(): raise ValueError('Centavos inválidos')
                            v=int(cents)
                        elif k in DATES: v=iso(v)
                        elif k in INTEGERS:
                            if type(v) not in (int,float) or not math.isfinite(v) or v<0 or int(v)!=v: raise ValueError('Inteiro inválido')
                            v=int(v)
                        elif k=='taxa_mensal':
                            if type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1: raise ValueError('Taxa inválida')
                        elif not isinstance(v,str) or not v.strip() or v.startswith('='): raise ValueError(f'Texto inválido: {k}')
                        result[k+'_centavos' if k in MONEY else k]=v
                    pk=(result['referencia'],result['contrato_id']) if name=='posicoes' else result[cols[0]]
                    if pk in seen: raise ValueError(f'Chave duplicada: {name}')
                    seen.add(pk);records.append(result)
                if not records: raise ValueError(f'Aba vazia: {name}')
                self._conn.executemany(f'INSERT INTO {name} VALUES('+','.join('?' for _ in cols)+')',[[r[k] for k in cols] for r in records])
                self._tables[name]=records;self.contagens[name]=len(records)
            self._validar()
            self._conn.commit();self._conn.execute('PRAGMA query_only=ON')
        except Exception as exc:
            self._conn.close()
            raise ValueError(f'fonte_invalida: {exc}') from exc
        finally:
            if book is not None: book.close()
        self.referencias={r['referencia'] for r in self._tables['posicoes']}
        self.publicos={'PF','PJ'}
        self.filiais={r['filial_id'] for r in self._tables['clientes']}
        self.ids={r['contrato_id'] for r in self._tables['contratos']}

    def _validar(self):
        t=self._tables
        clients={r['cliente_id']:r for r in t['clientes']};products={r['produto_id']:r for r in t['produtos']}
        proposals={r['proposta_id']:r for r in t['propostas']};contracts={r['contrato_id']:r for r in t['contratos']}
        installments={r['parcela_id']:r for r in t['parcelas']}
        for r in t['propostas']:
            if r['cliente_id'] not in clients or r['produto_id'] not in products: raise ValueError('Proposta com chave órfã')
        for r in t['contratos']:
            p=proposals.get(r['proposta_id']);c=clients.get(r['cliente_id']);prod=products.get(r['produto_id'])
            if not p or not c or not prod or p['situacao']!='CONTRATADA' or p['cliente_id']!=r['cliente_id'] or p['produto_id']!=r['produto_id']: raise ValueError('Vínculo de contrato inválido')
            if r['publico']!=c['publico'] or r['publico']!=prod['publico'] or r['filial_id']!=c['filial_id']: raise ValueError('Público/filial incompatível')
            if r['data_originacao']<p['data_proposta'] or r['primeiro_vencimento']<r['data_originacao']: raise ValueError('Cronologia de contrato inválida')
        for r in t['parcelas']:
            if r['contrato_id'] not in contracts: raise ValueError('Parcela órfã')
            if r['total_previsto_centavos']!=r['principal_previsto_centavos']+r['juros_previstos_centavos']: raise ValueError('Total da parcela divergente')
        for c in t['contratos']:
            rows=[r for r in t['parcelas'] if r['contrato_id']==c['contrato_id']]
            if len(rows)!=c['numero_parcelas'] or sum(r['principal_previsto_centavos'] for r in rows)!=c['principal_contratado_centavos']: raise ValueError('Parcelamento não reconcilia com contrato')
        for r in t['pagamentos']:
            p=installments.get(r['parcela_id'])
            if not p or p['contrato_id']!=r['contrato_id']: raise ValueError('Alocação órfã')
            if r['total_pago_centavos']!=r['principal_pago_centavos']+r['juros_pagos_centavos']: raise ValueError('Total recebido divergente')
            if r['data_pagamento']<contracts[r['contrato_id']]['data_originacao']: raise ValueError('Pagamento antes da originação')
        for p in t['parcelas']:
            rows=[r for r in t['pagamentos'] if r['parcela_id']==p['parcela_id']]
            if sum(r['principal_pago_centavos'] for r in rows)>p['principal_previsto_centavos'] or sum(r['juros_pagos_centavos']+r['juros_dispensados_centavos'] for r in rows)>p['juros_previstos_centavos']: raise ValueError('Alocação excede obrigação')
        for r in t['renegociacoes']:
            old=contracts.get(r['contrato_anterior']);new=contracts.get(r['contrato_novo'])
            if not old or not new or old['cliente_id']!=new['cliente_id'] or new['contrato_anterior']!=old['contrato_id']: raise ValueError('Renegociação órfã')
            if r['principal_transferido_centavos']!=new['principal_contratado_centavos']: raise ValueError('Transferência divergente')
            if r['data_efetivacao']!=new['data_originacao'] or r['data_efetivacao']<old['data_originacao']: raise ValueError('Cronologia do acordo divergente')
        for r in t['posicoes']:
            c=contracts.get(r['contrato_id'])
            if not c or any(r[k]!=c[k] for k in ['cliente_id','produto_id','publico','filial_id','tipo_origem']): raise ValueError('Posição com vínculo divergente')
            if r['principal_contratado_centavos']!=c['principal_contratado_centavos']: raise ValueError('Principal da posição difere do contrato')
            if r['referencia']<c['data_originacao']: raise ValueError('Posição antes da originação')
            d=date.fromisoformat(r['referencia'])
            if d.day!=calendar.monthrange(d.year,d.month)[1]: raise ValueError('Referência não mensal')
            if r['principal_contratado_centavos']-r['principal_amortizado_centavos']-r['principal_transferido_centavos']!=r['saldo_principal_centavos']: raise ValueError('Principal não reconcilia')
            if r['saldo_principal_centavos']+r['juros_vencidos_pendentes_centavos']!=r['saldo_devedor_centavos']: raise ValueError('Saldo devedor não reconcilia')
            paid=sum(a['principal_pago_centavos'] for a in t['pagamentos'] if a['contrato_id']==r['contrato_id'] and a['data_pagamento']<=r['referencia'])
            transferred=sum(a['principal_transferido_centavos'] for a in t['renegociacoes'] if a['contrato_anterior']==r['contrato_id'] and a['data_efetivacao']<=r['referencia'])
            if paid!=r['principal_amortizado_centavos'] or transferred!=r['principal_transferido_centavos']: raise ValueError('Posição diverge dos eventos de principal')
            if r['vencimento_mais_antigo'] and r['vencimento_mais_antigo']>r['referencia']: raise ValueError('Vencimento pendente posterior à referência')
            delay=max(0,(d-date.fromisoformat(r['vencimento_mais_antigo'])).days) if r['vencimento_mais_antigo'] else 0
            if delay!=r['dias_atraso']: raise ValueError('Atraso não reconcilia')

    def __enter__(self): return self
    def __exit__(self,*args): self._conn.close()

    def consultar(self,ferramenta,**filtros):
        if hashlib.sha256(self.path.read_bytes()).hexdigest()!=self.assinatura: raise ValueError('fonte_alterada: reconstrua a carga')
        result={'status':'filtro_invalido','linhas':[],'filtros':filtros,'unidade_monetaria':'centavos de BRL','fonte':self.path.name,'fonte_sha256':self.assinatura,'sql':None,'parametros':{}}
        def finish(status): result['status']=status;return result
        p={};where='referencia=:referencia AND (:publico IS NULL OR publico=:publico) AND (:filial IS NULL OR filial_id=:filial)'
        try:
            if ferramenta not in ('saldo','over','serie_over','contratos','renegociacoes','concessoes','propostas','safras'): return result
            allowed={'inicio','fim','publico','filial','limiares'} if ferramenta=='serie_over' else {'referencia','publico','filial','limiar'} if ferramenta in ('saldo','over') else {'referencia','ids'} if ferramenta=='contratos' else {'inicio','fim'} if ferramenta in ('renegociacoes','concessoes') else {'situacao'} if ferramenta=='propostas' else {'safras','mob','limiar'}
            if set(filtros)-allowed: return result
            if ferramenta in ('saldo','over','contratos'):
                p['referencia']=iso(filtros.get('referencia'))
                if p['referencia'] not in self.referencias: return finish('sem_cobertura')
            if ferramenta in ('saldo','over','serie_over'):
                p.update(publico=filtros.get('publico'),filial=filtros.get('filial'))
                if p['publico'] not in self.publicos|{None} or p['filial'] not in self.filiais|{None}: return result
            if ferramenta in ('over','safras'):
                if type(filtros.get('limiar')) is not int or not 0<=filtros['limiar']<=3650000: return result
                p['limiar']=filtros['limiar']
            if ferramenta=='serie_over':
                p['inicio']=iso(filtros.get('inicio'));p['fim']=iso(filtros.get('fim',max(self.referencias)))
                limits=filtros.get('limiares')
                if p['inicio']>p['fim'] or not isinstance(limits,list) or not 1<=len(limits)<=5:
                    return result
                if any(type(n) is not int or not 0<=n<=3650000 for n in limits) or len(set(limits))!=len(limits): return result
                if p['inicio']<min(self.referencias)[:7]+'-01' or p['fim']>max(self.referencias): return finish('sem_cobertura')
                refs=sorted(ref for ref in self.referencias if p['inicio']<=ref<=p['fim'])
                if not refs: return finish('sem_cobertura')
                if len(refs)>36: return finish('limite_excedido')
                first=date.fromisoformat(p['inicio']);last=date.fromisoformat(p['fim'])
                for month in range(first.year*12+first.month-1,last.year*12+last.month):
                    year,m=divmod(month,12);ref=date(year,m+1,calendar.monthrange(year,m+1)[1]).isoformat()
                    if p['inicio']<=ref<=p['fim'] and ref not in self.referencias: return finish('sem_cobertura')
                p.update({f'lim{i}':n for i,n in enumerate(sorted(limits))})
                values=','.join(f'(:lim{i})' for i in range(len(limits)))
                sql=f'''WITH limiares(limiar) AS (VALUES {values})
SELECT referencia,limiar,COUNT(CASE WHEN saldo_principal_centavos>0 THEN 1 END) AS contratos_elegiveis,
SUM(saldo_principal_centavos) AS denominador_centavos,
SUM(CASE WHEN dias_atraso>=limiar THEN saldo_principal_centavos ELSE 0 END) AS numerador_centavos
FROM posicoes CROSS JOIN limiares WHERE referencia BETWEEN :inicio AND :fim
AND (:publico IS NULL OR publico=:publico) AND (:filial IS NULL OR filial_id=:filial)
GROUP BY referencia,limiar ORDER BY referencia,limiar'''
            elif ferramenta=='saldo':
                sql=f'SELECT SUM(saldo_principal_centavos) AS saldo_principal_centavos, SUM(juros_vencidos_pendentes_centavos) AS juros_vencidos_pendentes_centavos, SUM(saldo_devedor_centavos) AS saldo_devedor_centavos FROM posicoes WHERE {where}'
            elif ferramenta=='over':
                sql=f'SELECT COUNT(*) AS contratos_elegiveis, SUM(saldo_principal_centavos) AS denominador_centavos, SUM(CASE WHEN dias_atraso >= :limiar THEN saldo_principal_centavos ELSE 0 END) AS numerador_centavos FROM posicoes WHERE {where} AND saldo_principal_centavos>0'
            elif ferramenta=='contratos':
                ids=filtros.get('ids')
                if not isinstance(ids,list) or not ids or len(ids)>500 or any(not isinstance(i,str) or i not in self.ids for i in ids): return result
                p.update({f'id{i}':v for i,v in enumerate(dict.fromkeys(ids))})
                sql='SELECT * FROM posicoes WHERE referencia=:referencia AND contrato_id IN ('+','.join(':'+k for k in p if k.startswith('id'))+') ORDER BY contrato_id'
            elif ferramenta in ('renegociacoes','concessoes'):
                p['inicio']=iso(filtros.get('inicio') or min(c['data_originacao'] for c in self._tables['contratos'])[:7]+'-01')
                p['fim']=iso(filtros.get('fim') or max(self.referencias))
                if p['inicio']>p['fim']: return result
                lower=min(c['data_originacao'] for c in self._tables['contratos'])[:7]+'-01'
                if p['inicio']<lower or p['fim']>max(self.referencias): return finish('sem_cobertura')
                sql='SELECT * FROM renegociacoes WHERE data_efetivacao BETWEEN :inicio AND :fim ORDER BY data_efetivacao' if ferramenta=='renegociacoes' else 'SELECT tipo_origem, COUNT(*) AS contratos, SUM(principal_contratado_centavos) AS principal_contratado_centavos, SUM(desembolso_novo_centavos) AS desembolso_novo_centavos FROM contratos WHERE data_originacao BETWEEN :inicio AND :fim GROUP BY tipo_origem ORDER BY tipo_origem'
            elif ferramenta=='propostas':
                p['situacao']=filtros.get('situacao')
                if p['situacao'] not in {None,'CONTRATADA','APROVADA_NAO_CONTRATADA','RECUSADA','EM_ANALISE'}: return result
                sql='SELECT * FROM propostas WHERE :situacao IS NULL OR situacao=:situacao ORDER BY proposta_id'
            else:
                saf=filtros.get('safras');mob=filtros.get('mob')
                if not isinstance(saf,list) or not saf or len(saf)>24 or type(mob) is not int or not 0<=mob<=120: return result
                for value in saf:
                    d=date.fromisoformat(iso(value))
                    if d.day!=1 or value not in {c['data_originacao'][:7]+'-01' for c in self._tables['contratos'] if c['tipo_origem']=='NOVA'}: return result
                    year,month=divmod(d.year*12+d.month-1+mob,12);ref=date(year,month+1,calendar.monthrange(year,month+1)[1]).isoformat()
                    if ref not in self.referencias: return finish('sem_cobertura')
                p.update(mob=mob,**{f'saf{i}':v for i,v in enumerate(dict.fromkeys(saf))})
                sql="SELECT safra_contrato,referencia,mob,COUNT(*) AS contratos_elegiveis,SUM(saldo_principal_centavos) AS denominador_centavos,SUM(CASE WHEN dias_atraso>=:limiar THEN saldo_principal_centavos ELSE 0 END) AS numerador_centavos FROM posicoes WHERE tipo_origem='NOVA' AND saldo_principal_centavos>0 AND mob=:mob AND safra_contrato IN ("+','.join(':'+k for k in p if k.startswith('saf'))+') GROUP BY safra_contrato,referencia,mob ORDER BY safra_contrato'
            result.update(sql=sql+' LIMIT 501',parametros=p)
            deadline=time.monotonic()+2
            self._conn.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
            try: rows=[dict(r) for r in self._conn.execute(result['sql'],p)]
            finally: self._conn.set_progress_handler(None,0)
            if len(rows)>500: return finish('limite_excedido')
            if not rows or (ferramenta=='saldo' and rows[0]['saldo_principal_centavos'] is None) or (ferramenta=='over' and not rows[0]['denominador_centavos']): return finish('sem_populacao')
            for row in rows:
                if 'denominador_centavos' in row:
                    row['taxa_percentual']=str(Decimal(row['numerador_centavos'])*100/Decimal(row['denominador_centavos'])) if row['denominador_centavos'] else None
            result['linhas']=rows;return finish('ok')
        except (ValueError,TypeError,OverflowError): return result
        except sqlite3.Error: return finish('erro_consulta')
