"use strict";

function renderizarGrafico(doc,data){
  if(!data||!['linhas','colunas'].includes(data.tipo)||typeof data.titulo!=='string'||!Array.isArray(data.series)||!data.series.length||data.series.length>5)return null;
  const columns=data.tipo==='colunas';
  let dates=null;
  for(const serie of data.series){
    if(!serie||!/^Over\d+$/.test(serie.nome)||!Array.isArray(serie.pontos)||!serie.pontos.length||serie.pontos.length>36)return null;
    const refs=[];
    for(const point of serie.pontos){
      if(!point||typeof point.referencia!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(point.referencia))return null;
      const date=new Date(point.referencia+'T00:00:00Z');
      if(!Number.isFinite(date.getTime())||date.toISOString().slice(0,10)!==point.referencia)return null;
      if(point.valor!==null&&(typeof point.valor!=='number'||!Number.isFinite(point.valor)||point.valor<0||point.valor>100))return null;
      refs.push(point.referencia);
    }
    if(refs.some((ref,i)=>i>0&&ref<=refs[i-1]))return null;
    if(dates&&JSON.stringify(dates)!==JSON.stringify(refs))return null;
    dates=refs;
  }
  const el=(tag,text)=>{const node=doc.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
  const svgEl=(tag,attrs={},text)=>{
    const node=doc.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [key,value] of Object.entries(attrs))node.setAttribute(key,value);
    if(text!==undefined)node.textContent=text;return node;
  };
  const percent=value=>value===null?'Sem população':value.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%';
  const month=ref=>ref.slice(5,7)+'/'+ref.slice(0,4);
  const colors=['#214b68','#187566','#a55528','#73528b','#596873'];
  const dashes=['','8 4','2 4','10 3 2 3','5 3'];
  const figure=el('figure');figure.className='grafico tipo-'+data.tipo;
  const caption=el('figcaption',data.titulo);caption.className='grafico-titulo';figure.append(caption);
  const context=el('p',`${month(dates[0])} a ${month(dates.at(-1))} · ${data.publico||'PF e PJ'}${data.filial?' · '+data.filial:''}`);
  context.className='grafico-contexto';figure.append(context);
  const legend=el('div');legend.className='grafico-legenda';
  data.series.forEach((serie,index)=>{
    const item=el('span');const mark=el('span');mark.className='grafico-amostra serie'+index;
    mark.setAttribute('aria-hidden','true');item.append(mark,el('span',serie.nome));legend.append(item);
  });
  figure.append(legend);
  const controls=el('label');controls.className='grafico-controles';
  const toggle=el('input');toggle.type='checkbox';toggle.checked=dates.length<=12;
  controls.append(toggle,el('span','Rótulos de dados'));figure.append(controls);
  const viewport=el('div');viewport.className='grafico-janela';viewport.setAttribute('tabindex','0');
  viewport.setAttribute('aria-label','Gráfico mensal. Em telas pequenas, role horizontalmente. Valores disponíveis na tabela abaixo.');
  const svg=svgEl('svg',{viewBox:'0 0 760 320',role:'group','aria-label':data.titulo});
  svg.append(svgEl('title',{},`${data.titulo}. Taxas em porcentagem de zero a cem. Consulte os valores na tabela abaixo.`));
  const slot=686/dates.length;
  const x=index=>columns?50+slot*(index+.5):dates.length===1?393:50+686*index/(dates.length-1);
  const y=value=>274-value*2.54;
  const groupWidth=slot*.76;
  const barWidth=Math.min(30,groupWidth/data.series.length*.82);
  const barCenter=(index,serie)=>x(index)-groupWidth/2+groupWidth/data.series.length*(serie+.5);
  for(const tick of [0,25,50,75,100]){
    svg.append(svgEl('line',{x1:50,y1:y(tick),x2:736,y2:y(tick),class:'grafico-grade'}),
      svgEl('text',{x:40,y:y(tick)+4,'text-anchor':'end',class:'grafico-eixo'},tick+'%'));
  }
  const every=Math.max(1,Math.ceil(dates.length/12));
  dates.forEach((ref,index)=>{
    if(index%every===0||index===dates.length-1)svg.append(svgEl('text',{
      x:x(index),y:302,'text-anchor':'middle',class:'grafico-eixo'},ref.slice(5,7)+'/'+ref.slice(2,4)));
  });
  data.series.forEach((serie,index)=>{
    if(columns){
      serie.pontos.forEach((point,i)=>{
        if(point.valor===null)return;
        svg.append(svgEl('rect',{x:barCenter(i,index)-barWidth/2,y:y(point.valor),width:barWidth,
          height:point.valor*2.54,fill:colors[index],class:'grafico-coluna','aria-hidden':'true'}));
      });
      return;
    }
    let path='';const paths=[];
    serie.pontos.forEach((point,i)=>{
      if(point.valor===null){if(path)paths.push(path);path='';return;}
      const coords=`${Number(x(i).toFixed(2))},${Number(y(point.valor).toFixed(2))}`;
      path+=(path?' L':'M')+coords;
    });
    if(path)paths.push(path);
    for(const d of paths)svg.append(svgEl('path',{d,fill:'none',stroke:colors[index],
      'stroke-width':2.5,'stroke-dasharray':dashes[index],class:'grafico-linha'}));
    serie.pontos.forEach((point,i)=>{
      if(point.valor===null)return;
      const label=`${serie.nome}, ${month(point.referencia)}: ${percent(point.valor)}`;
      const circle=svgEl('circle',{cx:x(i),cy:y(point.valor),r:4,fill:colors[index],stroke:'#fff',
        'stroke-width':1.5,'aria-hidden':'true'});
      circle.append(svgEl('title',{},label));svg.append(circle);
    });
  });
  const labels=svgEl('g',{class:'grafico-rotulos',visibility:toggle.checked?'visible':'hidden','aria-hidden':'true'});
  dates.forEach((ref,i)=>{
    const items=data.series.map((serie,index)=>({value:serie.pontos[i].valor,index}))
      .filter(item=>item.value!==null).map(item=>({...item,y:Math.max(34,y(item.value)-10)})).sort((a,b)=>a.y-b.y);
    for(let j=1;j<items.length;j++)items[j].y=Math.max(items[j].y,items[j-1].y+16);
    if(items.length){items.at(-1).y=Math.min(items.at(-1).y,266);
      for(let j=items.length-2;j>=0;j--)items[j].y=Math.min(items[j].y,items[j+1].y-16);}
    for(const item of items)labels.append(svgEl('text',{x:columns?barCenter(i,item.index):x(i)+(i===dates.length-1&&dates.length>1?-7:7),y:item.y,
      'text-anchor':columns?'middle':i===dates.length-1&&dates.length>1?'end':'start',fill:colors[item.index],class:'grafico-rotulo'},percent(item.value)));
  });
  svg.append(labels);
  toggle.addEventListener('change',()=>labels.setAttribute('visibility',toggle.checked?'visible':'hidden'));

  const guide=svgEl('line',{y1:20,y2:274,class:'grafico-guia',visibility:'hidden','aria-hidden':'true'});
  const tooltip=svgEl('g',{class:'grafico-tooltip',visibility:'hidden','aria-hidden':'true','pointer-events':'none'});
  const hide=()=>{tooltip.setAttribute('visibility','hidden');guide.setAttribute('visibility','hidden');};
  const show=index=>{
    const left=Math.max(50,Math.min(548,x(index)+14));
    tooltip.setAttribute('transform',`translate(${left} 28)`);tooltip.textContent='';
    tooltip.append(svgEl('rect',{width:188,height:36+data.series.length*20,rx:6,class:'grafico-tooltip-fundo'}),
      svgEl('text',{x:12,y:23,class:'grafico-tooltip-mes'},month(dates[index])));
    data.series.forEach((serie,j)=>tooltip.append(svgEl('text',{x:12,y:46+j*20,fill:colors[j],class:'grafico-tooltip-valor'},
      `${serie.nome}: ${percent(serie.pontos[index].valor)}`)));
    guide.setAttribute('x1',x(index));guide.setAttribute('x2',x(index));guide.setAttribute('visibility','visible');
    tooltip.setAttribute('visibility','visible');
  };
  svg.append(guide);
  const regions=[];
  dates.forEach((ref,index)=>{
    const step=columns?slot:dates.length===1?1372:686/(dates.length-1);
    const left=Math.max(50,x(index)-step/2);const right=Math.min(736,x(index)+step/2);
    const region=svgEl('rect',{x:left,y:20,width:right-left,height:254,fill:'transparent',
      class:'grafico-interacao',tabindex:0,role:'img',
      'aria-label':`${month(ref)}. `+data.series.map(s=>`${s.nome}: ${percent(s.pontos[index].valor)}`).join('. ')});
    for(const event of ['pointerenter','focus','click'])region.addEventListener(event,()=>show(index));
    for(const event of ['pointerleave','blur'])region.addEventListener(event,hide);
    region.addEventListener('keydown',event=>{
      if(event.key==='Escape')hide();
      if(event.key==='ArrowRight'||event.key==='ArrowLeft'){
        event.preventDefault();regions[(index+(event.key==='ArrowRight'?1:-1)+dates.length)%dates.length].focus();
      }
    });
    regions.push(region);svg.append(region);
  });
  svg.append(tooltip);
  viewport.append(svg);figure.append(viewport);
  const details=el('details');const summary=el('summary','Ver valores por mês');details.append(summary);
  const scroll=el('div');scroll.className='grafico-tabela';
  const table=el('table');table.append(el('caption','Taxas mensais dos indicadores Over'));
  const head=el('thead');const header=el('tr');
  for(const title of ['Mês',...data.series.map(s=>s.nome)]){
    const th=el('th',title);th.setAttribute('scope','col');header.append(th);
  }
  head.append(header);table.append(head);const body=el('tbody');
  dates.forEach((ref,i)=>{
    const row=el('tr');const th=el('th',month(ref));th.setAttribute('scope','row');row.append(th);
    data.series.forEach(serie=>row.append(el('td',percent(serie.pontos[i].valor))));body.append(row);
  });
  table.append(body);scroll.append(table);details.append(scroll);figure.append(details);
  return figure;
}

if(typeof module!=='undefined')module.exports={renderizarGrafico};
