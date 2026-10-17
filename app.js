var su=u=>/^(javascript|data|vbscript):/i.test(String(u||'').replace(/[\s\x00-\x1f]/g,''))?'#':u;
const CATS=['補助政策','補助成果發表','補助資訊'],L={'補助政策':'補助政策','補助成果發表':'補助成果發表','補助資訊':'補助資訊'},TABS=['首頁',...CATS];
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const N=[...NEWS].sort((a,b)=>(b.date||'').localeCompare(a.date||''));let cat='首頁',topic='',shown=20;
const W='日一二三四五六',d=new Date();$('#today').textContent=`${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日 星期${W[d.getDay()]}`;$('#upd').textContent='資料更新：'+UPDATED;
const ci=c=>CATS.indexOf(c)+1,tag=n=>`<span class="tag t${ci(n.category)}">${L[n.category]}</span>`+(n.topic&&n.topic!='綜合'?`<span class="topic">${esc(n.topic)}</span>`:'');
const link=(n,t)=>`<a href="${esc(su(n.url))}" target="_blank" rel="noopener">${t}</a>`;
const ttl=n=>esc(n.title_zh||n.title),orig=n=>n.title_zh?`<p class="orig">${esc(n.title)}</p>`:'';
const also=n=>n.also&&n.also.length?`<span class="also">另見：${n.also.map(a=>`<a href="${esc(su(a.url))}" target="_blank" rel="noopener">${esc(a.unit)}</a>`).join('、')}</span>`:'';
const meta=n=>`<div class="meta">${tag(n)}<span class="unit">${esc(n.unit)}</span><time>${n.date}</time></div>`;
const card=(n,cls='card')=>`<article class="${cls}">${meta(n)}<h3>${link(n,ttl(n))}</h3>${orig(n)}<p class="sum">${esc(n.summary)}</p><button class="tog">展開摘要 ▾</button><div class="foot"><a class="src" href="${esc(su(n.url))}" target="_blank" rel="noopener">原始連結 ↗</a>${also(n)}</div></article>`;
$('#tabs').innerHTML=TABS.map(c=>`<button data-c="${c}">${c=='首頁'?'首頁':L[c]}</button>`).join('')+'<a class="navsk" href="https://www.subsidyking.tw/" target="_blank" rel="noopener">補助王 ↗</a><a class="navsub" href="#subscribe">✉ 訂閱</a>';
const AD=`<div class="box ad"><div class="ad-name">仁禾管理顧問<br>劉靜渡</div><div class="ad-contact"><a href="mailto:tommyliu2009@gmail.com">tommyliu2009@gmail.com</a><br><a href="https://line.me/ti/p/~tommyliu2009" target="_blank" rel="noopener">LINE ID：tommyliu2009</a></div></div>`;
function side(){const t={};N.forEach(n=>{(t[n.category]=t[n.category]||{})[n.topic||'綜合']=((t[n.category]||{})[n.topic||'綜合']||0)+1});
 let h=AD+'<div class="box"><h4>分類</h4>'+CATS.filter(c=>t[c]).map(c=>`<p class="grp"><a data-c="${c}" data-t="">${L[c]}</a></p><ul class="units">`+Object.entries(t[c]).sort((a,b)=>b[1]-a[1]).map(([u,k])=>`<li><a data-c="${c}" data-t="${esc(u)}" class="${c==cat&&u==topic?'on':''}">${esc(u)}<em>${k}</em></a></li>`).join('')+'</ul>').join('')+'</div>';
 h+='<a class="box skside" href="https://www.subsidyking.tw/" target="_blank" rel="noopener"><b>補助王</b><span>全台政府補助查詢，開放中、即將截止一次看 ↗</span></a><a class="box subside" href="#subscribe">✉ 免費訂閱補助新聞電子報</a>';h+='<div class="box"><h4>最新新聞</h4><ol class="latest">'+N.slice(0,8).map(n=>`<li>${link(n,ttl(n))}<time>${n.date}｜${esc(n.unit)}</time></li>`).join('')+'</ol></div>';
 h+='<div class="box"><h4>相關網站</h4><ul class="units"><li><a href="https://www.subsidyking.tw/" target="_blank" rel="noopener">補助王：政府補助查詢 ↗</a></li><li><a href="https://web4.subsidyking.tw/" target="_blank" rel="noopener">標案王：政府標案查詢 ↗</a></li><li><a href="https://web5.subsidyking.tw/" target="_blank" rel="noopener">股票王：台股與全球市場 ↗</a></li></ul></div>';$$('.side').forEach(s=>s.innerHTML=h)}
function home(){const [l,...r]=N;if(!l)return;$('#lead').innerHTML=`<article class="lead">${meta(l)}<h2>${link(l,ttl(l))}</h2>${orig(l)}<p class="sum">${esc(l.summary)}</p><button class="tog">展開摘要 ▾</button><a class="src" href="${esc(su(l.url))}" target="_blank" rel="noopener">閱讀原文 ↗</a></article>`;
 const used=new Set([l]);const picks=CATS.map(c=>r.find(n=>n.category==c&&!used.has(n))).filter(Boolean);
 $('#subs').innerHTML='<h4 class="kicker">焦點新聞</h4>'+picks.map(n=>`<article class="subh">${meta(n)}<h3>${link(n,ttl(n))}</h3></article>`).join('');
 $$('.block[data-cat]').forEach(b=>{const a=N.filter(n=>n.category==b.dataset.cat&&n!==l).slice(0,6);b.hidden=!a.length;b.querySelector('.grid').innerHTML=a.map(n=>card(n)).join('')})}
function catv(){const all=N.filter(n=>n.category==cat),a=all.filter(n=>!topic||n.topic==topic),tp={};all.forEach(n=>tp[n.topic||'綜合']=(tp[n.topic||'綜合']||0)+1);
 $('#ctitle').textContent=L[cat]+(topic?'｜'+topic:'');$('#cmeta').textContent=`共 ${a.length} 則`;
 $('#topics').innerHTML=`<a data-c="${cat}" data-t="" class="${topic?'':'on'}">全部</a>`+Object.entries(tp).sort((x,y)=>y[1]-x[1]).map(([u,k])=>`<a data-c="${cat}" data-t="${esc(u)}" class="${u==topic?'on':''}">${esc(u)} ${k}</a>`).join('');
 $('#sklink').innerHTML=true?'<p class="sk">想查目前可申請的政府補助？請到 <a href="https://www.subsidyking.tw/" target="_blank" rel="noopener">補助王 ↗</a></p>':'';
 $('#clist').innerHTML=a.slice(0,shown).map(n=>card(n,'card row')).join('');$('#more').style.display=a.length>shown?'':'none'}
function go(c,t=''){cat=c;topic=t;shown=20;$$('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.c==cat));$('#home').hidden=cat!='首頁';$('#catview').hidden=cat=='首頁';cat=='首頁'?home():catv();side();folds();const h=cat=='首頁'?'':'#'+encodeURIComponent(cat);if(location.hash!=h)history.replaceState(null,'',h||location.pathname);scrollTo(0,0)}
function folds(){$$('.sum').forEach(p=>{const b=p.nextElementSibling;if(b&&b.classList.contains('tog'))b.hidden=!(p.scrollHeight>p.clientHeight+2)&&!p.classList.contains('open')})}
document.addEventListener('click',e=>{const t=e.target.closest('[data-c],[data-go],.tog');if(!t)return;
 if(t.classList.contains('tog')){const p=t.previousElementSibling,o=p.classList.toggle('open');t.textContent=o?'收合摘要 ▴':'展開摘要 ▾';return}
 if(t.tagName=='A'&&!t.dataset.c&&!t.dataset.go)return;e.preventDefault();go(t.dataset.go||t.dataset.c,t.dataset.t||'')});
$('#more').onclick=()=>{shown+=20;catv();folds()};addEventListener('resize',folds);
const h0=decodeURIComponent(location.hash.slice(1));go(CATS.includes(h0)?h0:'首頁');

function openblk(){const o=window.OPEN||[],b=$('#openblk');if(!o.length){b.hidden=true;return}
 b.querySelector('.olist').innerHTML='<ul>'+o.slice(0,15).map(x=>`<li>${x.soon?'<span class="soon">即將截止</span>':'<span class="opn">開放中</span>'}<a href="${esc(su(x.url))}" target="_blank" rel="noopener">${esc(x.name)}</a><em>${esc(x.org)}${x.end?'｜截止 '+x.end:''}</em></li>`).join('')+`</ul><p class="sk">共 ${o.length} 項，完整清單請到 <a href="https://www.subsidyking.tw/" target="_blank" rel="noopener">補助王 ↗</a></p>`}
openblk();
(function(){const f=$('#subf'),s=$('#smsg'),b=$('#sbtn'),U=(window.SUB_URL||'').trim();
 const show=(t,ok)=>{s.hidden=false;s.textContent=t;s.style.color=ok?'#2e7d32':'#c8102e'};
 if(!U){$('#semail').disabled=true;b.disabled=true;b.textContent='即將開放';show('訂閱功能即將開放，敬請期待。如需先訂閱，請寄信至 tommyliu2009@gmail.com。',true);return}
 f.onsubmit=e=>{e.preventDefault();const m=$('#semail').value.trim().toLowerCase();if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(m)){show('Email 格式不正確，請重新輸入。');return}
  b.disabled=true;show('處理中…',true);const cb='subcb'+Date.now(),sc=document.createElement('script');
  const done=()=>{b.disabled=false;sc.remove();delete window[cb];clearTimeout(t)},t=setTimeout(()=>{done();show('連線逾時，請稍後再試。')},15000);
  window[cb]=r=>{done();const st=r&&r.status;
   if(st=='subscribed')show('已訂閱！之後會把補助新聞寄到 '+m+'。',true);
   else if(st=='unsubscribed')show('已取消訂閱，不會再寄信給 '+m+'。',true);
   else if(st=='wait')show('剛剛已處理過這個 Email，請 30 秒後再試。');
   else show('Email 格式不正確，請重新輸入。')};
  sc.onerror=()=>{done();show('連線失敗，請稍後再試。')};
  sc.src=U+(U.includes('?')?'&':'?')+'email='+encodeURIComponent(m)+'&callback='+cb;document.body.appendChild(sc)}})();
