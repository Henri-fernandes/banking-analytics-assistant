"use strict";

// Subconjunto de Markdown: parágrafos, listas e negrito. HTML sempre permanece texto.
function renderizarMensagem(doc,texto){
  const root=doc.createDocumentFragment();
  let paragraph=[],list=null,listType='';
  function inline(node,text){
    const pattern=/\*\*([^*\n]+)\*\*/g;let last=0;
    for(const match of text.matchAll(pattern)){
      if(match.index>last)node.append(doc.createTextNode(text.slice(last,match.index)));
      const strong=doc.createElement('strong');strong.textContent=match[1];node.append(strong);
      last=match.index+match[0].length;
    }
    if(last<text.length)node.append(doc.createTextNode(text.slice(last)));
  }
  function flush(){
    if(!paragraph.length)return;
    const p=doc.createElement('p');inline(p,paragraph.join('\n'));root.append(p);paragraph=[];
  }
  const normalized=texto.replace(/\r\n?/g,'\n').replace(/([^\n])[ \t]+-[ \t]+(?=\*\*[^*\n]+\*\*\s*:)/g,'$1\n- ');
  for(const line of normalized.split('\n')){
    if(!line.trim()){flush();list=null;continue;}
    const unordered=line.match(/^\s*[-*]\s+(.+)$/);
    const ordered=line.match(/^\s*\d+[.)]\s+(.+)$/);
    const item=unordered||ordered;
    if(item){
      flush();const type=unordered?'ul':'ol';
      if(!list||listType!==type){list=doc.createElement(type);listType=type;root.append(list);}
      const li=doc.createElement('li');inline(li,item[1]);list.append(li);
    }else{list=null;paragraph.push(line);}
  }
  flush();return root;
}

if(typeof module!=='undefined'&&module.exports)module.exports={renderizarMensagem};
else globalThis.renderizarMensagem=renderizarMensagem;
