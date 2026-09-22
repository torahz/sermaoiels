(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const records = JSON.parse($('sermoes-data').textContent).sermons;
  const elements = {q: $('search'), ano: $('filterAno'), mes: $('filterMes'), preletor: $('filterPreletor'), serie: $('filterSerie'), estacao: $('filterEstacao'), ordem: $('sort')};
  const colors = {'Advento':'#877097','Natal':'#af8530','Epifania':'#526b87','Quaresma':'#756580','Páscoa':'#a44549','Pentecostes':'#b77642','Trindade':'#937b4d','Após Pentecostes':'#527750','Tempo Comum':'#46694e','Criação':'#668f9e','Estação da Criação':'#668f9e','Cristo Rei':'#af8530'};
  const escape = s => String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const dateLabel = d => d.split('-').reverse().join('/');
  const list = $('sermonList');
  const initialCards = new Map([...list.querySelectorAll('.sermon-card')].map(c => [c.dataset.id, c]));
  let toastTimeout;
  function toast(message) {
    $('toast').textContent = message; $('toast').hidden = false;
    clearTimeout(toastTimeout); toastTimeout = setTimeout(() => $('toast').hidden = true, 5000);
  }
  function populate(select, values, reverse = false) {
    [...new Set(values.filter(Boolean))].sort((a,b) => reverse ? b.localeCompare(a) : a.localeCompare(b,'pt-BR')).forEach(v => select.add(new Option(v,v)));
  }
  populate(elements.ano, records.map(r => r.date.slice(0,4)), true);
  populate(elements.preletor, records.map(r => r.preacher));
  // Unifica apenas a seleção de variantes de caixa/acentuação; os textos originais ficam intactos.
  const seriesChoices = new Map();
  records.forEach(r => {if (r.series && !seriesChoices.has(SermonsCore.normalize(r.series))) seriesChoices.set(SermonsCore.normalize(r.series), r.series);});
  populate(elements.serie, [...seriesChoices.values()]);
  populate(elements.estacao, records.map(r => r.season));
  ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'].forEach((m,i) => elements.mes.add(new Option(m,String(i+1).padStart(2,'0'))));
  for (const r of records) initialCards.get(r.id)?.style.setProperty('--season-color',colors[r.season] || '#46694e');
  function readURL() {
    const params = new URLSearchParams(location.search);
    Object.entries(elements).forEach(([key, el]) => {
      const value = params.get(key) || (key === 'ordem' ? 'recent' : '');
      if (el.tagName === 'SELECT' && ![...el.options].some(o => o.value === value)) el.add(new Option(value,value));
      el.value = value;
    });
  }
  function render(writeURL = true) {
    const filters = Object.fromEntries(Object.entries(elements).map(([k,el]) => [k,el.value]));
    const found = SermonsCore.query(records,filters);
    const fragment = document.createDocumentFragment();
    found.forEach(r => fragment.append(initialCards.get(r.id)));
    list.replaceChildren(fragment);
    $('resultCount').textContent = `${found.length} ${found.length === 1 ? 'sermão encontrado' : 'sermões encontrados'}`;
    $('emptyState').hidden = found.length !== 0;
    $('publicationNotice').hidden = filters.ordem !== 'published';
    const count = Object.entries(filters).filter(([k,v]) => k !== 'ordem' && v).length;
    $('activeFilters').textContent = count ? `(${count} ${count === 1 ? 'ativo' : 'ativos'})` : '';
    if (writeURL) {
      const url = new URL(location.href);
      Object.entries(filters).forEach(([k,v]) => v && !(k === 'ordem' && v === 'recent') ? url.searchParams.set(k,v) : url.searchParams.delete(k));
      history.replaceState(null,'',url);
    }
  }
  function clear() {
    Object.entries(elements).forEach(([k,el]) => el.value = k === 'ordem' ? 'recent' : '');
    render();
  }
  $('filters').addEventListener('submit',e => e.preventDefault());
  Object.values(elements).forEach(el => el.addEventListener(el.type === 'search' ? 'input' : 'change',() => render()));
  $('clearFilters').addEventListener('click',clear);
  $('emptyClear').addEventListener('click',clear);
  window.addEventListener('popstate',() => {readURL();render(false);showSelected();});
  const latest = SermonsCore.query(records)[0];
  if (latest) {
    $('featured').innerHTML = `<p class="eyebrow">ÚLTIMO SERMÃO</p><time datetime="${escape(latest.date)}">${dateLabel(latest.date)}</time><h2>${escape(latest.title)}</h2><p class="series">${escape(latest.series)}</p><p class="preacher">${escape(latest.preacher)}</p><p class="celebration">${escape(latest.celebration)}</p><a class="listen" href="${escape(latest.url)}" target="_blank" rel="noopener">Abrir gravação ↗</a>`;
    $('featured').hidden = false;
  }
  async function share(url,title) {
    if (navigator.share) {
      try {await navigator.share({title,url});return;} catch(e) {if(e.name === 'AbortError')return;}
    }
    try {await navigator.clipboard.writeText(url);toast('Link copiado. Agora é só compartilhar.');}
    catch {window.prompt('Copie este link para compartilhar:',url);}
  }
  $('sharePage').addEventListener('click',() => share(location.href,document.title));
  document.addEventListener('click',e => {
    const button = e.target.closest('[data-share]');
    if (!button) return;
    const r = records.find(r => r.id === button.dataset.share);
    if (!r) return;
    const url = new URL(location.href);url.search='';url.hash='';url.searchParams.set('sermao',r.id);
    share(url.href,`${r.title} · Igreja Esperança`);
  });
  function showSelected() {
    const id = new URLSearchParams(location.search).get('sermao');
    const box = $('selectedSermon'); box.replaceChildren();box.hidden = true;
    if (!id) return;
    const card = initialCards.get(id);
    if (!card) {toast('O sermão compartilhado não foi encontrado neste acervo.');return;}
    const p = document.createElement('p');p.textContent='Sermão compartilhado';
    const clone = card.cloneNode(true);clone.removeAttribute('id');
    box.append(p,clone);box.hidden=false;
    box.scrollIntoView({behavior:'instant',block:'start'});
  }
  readURL();render(false);showSelected();
  if (matchMedia('(max-width:650px)').matches && !Object.entries(elements).some(([k,el]) => k !== 'ordem' && el.value)) $('filterDetails').open=false;
  const offline = () => $('offlineNotice').hidden = navigator.onLine;
  window.addEventListener('online',offline);window.addEventListener('offline',offline);offline();
  let installPrompt;
  window.addEventListener('beforeinstallprompt',e => {e.preventDefault();installPrompt=e;});
  $('installBtn').addEventListener('click',async () => {
    if (installPrompt) {await installPrompt.prompt();installPrompt=null;} else $('installDialog').showModal();
  });
  window.addEventListener('appinstalled',() => {installPrompt=null;toast('Aplicativo instalado.');});
  if ('serviceWorker' in navigator && ['https:','http:'].includes(location.protocol)) {
    navigator.serviceWorker.register('./sw.js',{updateViaCache:'none'}).then(reg => {
      const notify = () => {
        if (reg.waiting && navigator.serviceWorker.controller) toast('Uma atualização está pronta. Feche e reabra o aplicativo para utilizá-la.');
      };
      notify();reg.addEventListener('updatefound',() => reg.installing?.addEventListener('statechange',notify));
      reg.update().catch(() => {});
    }).catch(() => {});
  }
})();
