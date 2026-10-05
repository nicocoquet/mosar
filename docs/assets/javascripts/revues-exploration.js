(() => {
  const root = document.getElementById('revues-explorer');
  if (!root) return;
  const source = root.dataset.source;
  const esc = (s='') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const LANG = {fre:'Français',fra:'Français',eng:'Anglais',deu:'Allemand',ger:'Allemand',ita:'Italien',spa:'Espagnol',por:'Portugais',dut:'Néerlandais',nld:'Néerlandais',cat:'Catalan',pol:'Polonais',rus:'Russe',ara:'Arabe',gre:'Grec moderne',ell:'Grec moderne',lat:'Latin',tur:'Turc',rum:'Roumain',ron:'Roumain',hun:'Hongrois',cze:'Tchèque',ces:'Tchèque',slo:'Slovaque',slk:'Slovaque',hrv:'Croate',srp:'Serbe',slv:'Slovène',bul:'Bulgare',ukr:'Ukrainien',heb:'Hébreu',jpn:'Japonais',chi:'Chinois',zho:'Chinois'};
  const langLabel = code => LANG[String(code).toLowerCase()] || String(code).toUpperCase();
  const state = {q:'', proximity:new Set(), access:new Set(), fees:new Set(), periodicity:new Set(), format:new Set(), themes:new Set(), languages:new Set()};

  fetch(source).then(r => { if(!r.ok) throw new Error(r.status); return r.json(); }).then(data => init(data)).catch(err => { root.innerHTML = `<p>Impossible de charger les données (${esc(err.message)}).</p>`; });

  function init(data){
    const records = data.records || [];
    root.innerHTML = `<div class="rx-toolbar"><input class="rx-search" type="search" placeholder="Rechercher une revue, un ISSN, un éditeur…" aria-label="Rechercher"><div class="rx-summary"></div></div><div class="rx-layout"><aside class="rx-facets"><div class="rx-facets-head"><h2>Affiner</h2><button class="rx-reset" type="button" disabled>Réinitialiser</button></div><div class="rx-facet-list"></div></aside><section class="rx-cards" aria-live="polite"></section></div>`;
    root.querySelector('.rx-search').addEventListener('input', e => { state.q=e.target.value.trim().toLocaleLowerCase('fr'); render(records); });
    root.querySelector('.rx-reset').addEventListener('click', () => { Object.keys(state).forEach(k => k==='q' ? state.q='' : state[k].clear()); root.querySelector('.rx-search').value=''; root.querySelectorAll('input[type=checkbox]').forEach(i=>i.checked=false); render(records); });
    buildFacets(records); render(records);
  }

  function values(records, getter){ const c=new Map(); records.flatMap(getter).filter(Boolean).forEach(v=>c.set(v,(c.get(v)||0)+1)); return [...c.entries()].sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0],'fr')); }
  function buildFacets(records){
    const specs = [
      ['proximity','Niveau de proximité', r => r.mosar?.proximity_level ? [`Niveau ${r.mosar.proximity_level}`] : []],
      ['access','Accès', r => r.mosar?.open_access ? [r.mosar.open_access] : []],
      ['fees','Frais de publication', r => r.publication_fees ? [r.publication_fees] : []],
      ['periodicity','Périodicité', r => r.periodicity ? [r.periodicity] : []],
      ['format','Format de publication', r => r.publication_format ? [r.publication_format] : []],
      ['themes','Thématiques', r => r.themes || []],
      ['languages','Langues', r => (r.languages || []).map(langLabel)]
    ];
    const box=root.querySelector('.rx-facet-list');
    specs.forEach(([key,title,getter])=>{
      const vals=values(records,getter); if(!vals.length) return;
      const section=document.createElement('section'); section.className='rx-facet';
      const scroll = vals.length > 8 ? ' rx-facet-options--scroll' : '';
      section.innerHTML=`<h3>${esc(title)}</h3><div class="rx-facet-options${scroll}">${vals.map(([v,n])=>`<label class="rx-option"><input type="checkbox" data-facet="${key}" value="${esc(v)}"><span>${esc(v)}</span><span class="rx-count">${n}</span></label>`).join('')}</div>`;
      box.appendChild(section);
    });
    box.addEventListener('change', e=>{ const i=e.target.closest('input[data-facet]'); if(!i)return; const set=state[i.dataset.facet]; i.checked?set.add(i.value):set.delete(i.value); render(records); });
  }

  function matchesSet(selected, vals){ return !selected.size || vals.some(v=>selected.has(v)); }
  function filtered(records){ return records.filter(r=>{
    const hay=[r.title,r.sigle,...(r.issn||[]),...(r.publishers||[])].join(' ').toLocaleLowerCase('fr');
    if(state.q && !hay.includes(state.q)) return false;
    if(!matchesSet(state.proximity,r.mosar?.proximity_level?[`Niveau ${r.mosar.proximity_level}`]:[])) return false;
    if(!matchesSet(state.access,r.mosar?.open_access?[r.mosar.open_access]:[])) return false;
    if(!matchesSet(state.fees,r.publication_fees?[r.publication_fees]:[])) return false;
    if(!matchesSet(state.periodicity,r.periodicity?[r.periodicity]:[])) return false;
    if(!matchesSet(state.format,r.publication_format?[r.publication_format]:[])) return false;
    if(!matchesSet(state.themes,r.themes||[])) return false;
    if(!matchesSet(state.languages,(r.languages||[]).map(langLabel))) return false;
    return true;
  }); }

  function activeFilters(){ return state.q || Object.entries(state).some(([k,v]) => k!=='q' && v.size); }
  function icon(type){
    if(type==='open') return '<span class="rx-icon" aria-hidden="true">↗</span>';
    if(type==='paper') return '<span class="rx-icon" aria-hidden="true">▤</span>';
    if(type==='digital') return '<span class="rx-icon" aria-hidden="true">▣</span>';
    return '';
  }
  function formatMark(format){
    if(!format) return '';
    const marks = format==='Papier et numérique' ? `${icon('paper')}${icon('digital')}` : format==='Papier' ? icon('paper') : icon('digital');
    return `<span class="rx-signal" title="Format de publication : ${esc(format)}">${marks}<span>${esc(format)}</span></span>`;
  }
  function labelMarks(r){
    const out=[];
    (r.labels||[]).forEach(label=>{
      if(label.toLowerCase().includes('ddh diamond journal')) out.push(`<span class="rx-label rx-label--diamond" title="Labellisation : Diamond journal"><span aria-hidden="true">◆</span> Diamond journal</span>`);
      else out.push(`<span class="rx-label">${esc(label)}</span>`);
    });
    if(r.ddh?.url) out.push(`<a class="rx-label rx-label--ddh" href="${esc(r.ddh.url)}" target="_blank" rel="noopener" title="Voir la revue dans le Directory of Diamond Journals"><span aria-hidden="true">◇</span> DDH</a>`);
    return out.join('');
  }

  function render(records){
    const rows=filtered(records); root.querySelector('.rx-summary').textContent=`${rows.length} revue${rows.length>1?'s':''} sur ${records.length}`;
    root.querySelector('.rx-reset').disabled=!activeFilters();
    const cards=root.querySelector('.rx-cards');
    if(!rows.length){ cards.innerHTML='<div class="rx-empty">Aucune revue ne correspond aux filtres sélectionnés.</div>'; return; }
    cards.innerHTML=rows.map(r=>{
      const illustration = r.illustration ? `<div class="rx-card-visual"><img src="${esc(r.illustration)}" alt="" loading="lazy"></div>` : `<div class="rx-card-visual rx-card-visual--empty" aria-hidden="true"></div>`;
      const top=[]; if(r.mosar?.proximity_level) top.push(`<span class="rx-proximity">Niveau ${esc(r.mosar.proximity_level)}</span>`);
      const details=[];
      if(r.publishers?.length) details.push(`<span>${esc(r.publishers.join(', '))}</span>`);
      if(r.languages?.length) details.push(`<span>${esc(r.languages.map(langLabel).join(', '))}</span>`);
      if(r.periodicity) details.push(`<span>${esc(r.periodicity)}</span>`);
      const signals=[];
      if(r.mosar?.open_access) signals.push(`<span class="rx-signal rx-signal--access">${icon('open')}<span>${esc(r.mosar.open_access)}</span></span>`);
      if(r.publication_format) signals.push(formatMark(r.publication_format));
      const labels=labelMarks(r);
      const links=[`<a href="${esc(r.mirabel_url)}" target="_blank" rel="noopener">Mir@bel ↗</a>`]; if(r.journal_url) links.unshift(`<a href="${esc(r.journal_url)}" target="_blank" rel="noopener">Site web ↗</a>`);
      return `<article class="rx-card">${illustration}<div class="rx-card-body"><div class="rx-card-top">${top.join('')}</div><h2>${esc(r.title)}</h2><div class="rx-card-details">${details.join('<span class="rx-dot">·</span>')}</div><div class="rx-signals">${signals.join('')}</div>${labels?`<div class="rx-labels">${labels}</div>`:''}<div class="rx-card-foot"><span class="rx-issn">${r.issn?.length?`ISSN ${esc(r.issn.join(', '))}`:''}</span><span class="rx-links">${links.join('')}</span></div></div></article>`;
    }).join('');
  }
})();
