"use strict";
const app=document.getElementById('aplicacao');
const log=document.getElementById('mensagens');
const input=document.getElementById('pergunta');
const send=document.getElementById('enviar');
const fresh=document.getElementById('nova');
const error=document.getElementById('erro');
let csrf='',busy=false;
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');

function habilitar(){send.disabled=busy||!csrf||!input.value.trim();fresh.disabled=busy||!csrf;input.disabled=busy;}
function ajustar(){input.style.height='auto';input.style.height=Math.min(input.scrollHeight,168)+'px';habilitar();}
function falha(text){error.textContent=text;error.hidden=!text;}
function mostrar(papel,texto,grafico,graficos){
  app.classList.add('em-conversa');
  const article=document.createElement('article');article.className='mensagem '+papel;
  const label=document.createElement('div');label.className='rotulo';label.textContent=papel==='usuario'?'Você':'Assistente';
  const content=document.createElement('div');content.className='texto';
  if(papel==='assistente')content.append(renderizarMensagem(document,texto));
  else content.textContent=texto;
  article.append(label,content);
  if(papel==='assistente')for(const data of graficos||(grafico?[grafico]:[])){
    const chart=renderizarGrafico(document,data);if(chart)article.append(chart);
  }
  log.append(article);return article;
}
function rolar(){log.lastElementChild?.scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'end'});}
function esperando(){
  const node=document.createElement('div');node.className='aguardando';node.setAttribute('role','status');
  const dot=document.createElement('span');dot.className='indicador';dot.setAttribute('aria-hidden','true');
  const text=document.createElement('span');text.textContent='Preparando resposta…';node.append(dot,text);log.append(node);rolar();return node;
}
async function chamar(path,body){
  const options=body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(body)};
  const response=await fetch(path,options);
  const data=await response.json();
  if(!response.ok)throw new Error(data.erro||'Não foi possível concluir a solicitação.');
  return data;
}
async function iniciar(){
  try{const state=await chamar('/api/conversa');csrf=state.csrf;state.mensagens.forEach(m=>mostrar(m.papel,m.texto,m.grafico,m.graficos));habilitar();if(state.mensagens.length)rolar();}
  catch{falha('Não foi possível conectar. Atualize a página ou confira se o servidor local está ativo.');}
}
document.getElementById('formulario').addEventListener('submit',async event=>{
  event.preventDefault();const question=input.value.trim();if(busy||!csrf||!question)return;
  busy=true;falha('');const sent=mostrar('usuario',question);input.value='';ajustar();const wait=esperando();
  try{const answer=await chamar('/api/mensagem',{mensagem:question});wait.remove();mostrar('assistente',answer.mensagem,answer.grafico,answer.graficos);rolar();}
  catch(e){wait.remove();sent.remove();falha(e instanceof TypeError?'A conexão foi interrompida. Confira o servidor local antes de tentar novamente.':e.message);input.value=question;}
  finally{busy=false;ajustar();if(window.matchMedia('(hover:hover)').matches)input.focus();}
});
input.addEventListener('input',ajustar);
input.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();if(!send.disabled)document.getElementById('formulario').requestSubmit();}});
fresh.addEventListener('click',async()=>{
  if(busy||!csrf)return;busy=true;habilitar();falha('');
  try{await chamar('/api/nova',{});log.replaceChildren();app.classList.remove('em-conversa');input.value='';window.scrollTo({top:0,behavior:'instant'});}
  catch(e){falha(e.message);}
  finally{busy=false;ajustar();}
});
document.querySelectorAll('[data-pergunta]').forEach(button=>button.addEventListener('click',()=>{if(busy)return;input.value=button.dataset.pergunta;ajustar();input.focus();}));
habilitar();iniciar();
