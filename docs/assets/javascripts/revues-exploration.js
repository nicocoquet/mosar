(() => {
  const root = document.getElementById('revues-explorer');
  if (!root) return;
  const source = root.dataset.source;
  const esc = (s='') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const LANG = {fre:'Français',fra:'Français',eng:'Anglais',deu:'Allemand',ger:'Allemand',ita:'Italien',spa:'Espagnol',por:'Portugais',dut:'Néerlandais',nld:'Néerlandais',cat:'Catalan',pol:'Polonais',rus:'Russe',ara:'Arabe',gre:'Grec moderne',ell:'Grec moderne',lat:'Latin',tur:'Turc',rum:'Roumain',ron:'Roumain',hun:'Hongrois',cze:'Tchèque',ces:'Tchèque',slo:'Slovaque',slk:'Slovaque',hrv:'Croate',srp:'Serbe',slv:'Slovène',bul:'Bulgare',ukr:'Ukrainien',heb:'Hébreu',jpn:'Japonais',chi:'Chinois',zho:'Chinois'};
  const langLabel = code => LANG[String(code).toLowerCase()] || String(code).toUpperCase();
  const state = {q:'', proximity:new Set(), access:new Set(), fees:new Set(), periodicity:new Set(), format:new Set(), themes:new Set(), languages:new Set()};
  const ICON_BASE = '../assets/images/icons/';
  const REVUE_IMAGE_BASE = '../assets/images/revues/';

  const icons = {
    open: '<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 11m0 2a7 7 0 0 0 14 0v-3"/><path d="M8 11v-4a4 4 0 0 1 8 0v4"/></svg>',
    closed: '<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11v-4a4 4 0 0 1 8 0v4"/></svg>',
    paper: '<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5a2.5 2.5 0 0 1 2.5-2.5h13.5"/><path d="M6.5 2h13.5v20h-13.5a2.5 2.5 0 0 1-2.5-2.5v-15a2.5 2.5 0 0 1 2.5-2.5z"/></svg>',
    digital: '<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4m0 2a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-14a2 2 0 0 1-2-2z"/><path d="M8 20h8"/><path d="M12 18v2"/></svg>',
    world: '<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8"/><path d="M3.6 15h16.8"/><path d="M11.5 3a17 17 0 0 0 0 18"/><path d="M12.5 3a17 17 0 0 1 0 18"/></svg>',
    medal: '<svg class="rx-medal-icon" viewBox="0 0 512 512" aria-hidden="true"><path d="M223.75 130.75L154.62 15.54A31.997 31.997 0 0 0 127.18 0H16.03C3.08 0-4.5 14.57 2.92 25.18l111.27 158.96c29.72-27.77 67.52-46.83 109.56-53.39zM495.97 0H384.82c-11.24 0-21.66 5.9-27.44 15.54l-69.13 115.21c42.04 6.56 79.84 25.62 109.56 53.38L509.08 25.18C516.5 14.57 508.92 0 495.97 0zM256 160c-97.2 0-176 78.8-176 176s78.8 176 176 176 176-78.8 176-176-176zm92.52 157.26l-37.93 36.96 8.97 52.22c1.6 9.36-8.26 16.51-16.65 12.09L256 393.88l-46.9 24.65c-8.4 4.45-18.25-2.74-16.65-12.09l8.97-52.22-37.93-36.96c-6.82-6.64-3.05-18.23 6.35-19.59l52.43-7.64 23.43-47.52c2.11-4.28 6.19-6.39 10.28-6.39 4.11 0 8.22 2.14 10.33 6.39l23.43 47.52 52.43 7.64c9.4 1.36 13.17 12.95 6.35 19.59z"/></svg>'
  };

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
  function formatMark(format){
    if(!format) return '';
    const marks = format==='Papier et numérique' ? `${icons.paper}${icons.digital}` : format==='Papier' ? icons.paper : icons.digital;
    return `<span class="rx-signal" title="Format de publication : ${esc(format)}"><span class="rx-format-icons">${marks}</span><span>${esc(format)}</span></span>`;
  }
  function accessMark(access){
    if(!access) return '';
    const restricted = /restreint|fermé|ferme/i.test(access);
    return `<span class="rx-signal ${restricted?'rx-signal--restricted':'rx-signal--open'}" title="${esc(access)}">${restricted?icons.closed:icons.open}<span>${esc(access)}</span></span>`;
  }
  function isDiamond(r){ return (r.labels||[]).some(label => label.toLowerCase().includes('ddh diamond journal')); }
  function metaTags(r){
    const tags=[];
    if(r.mosar?.proximity_level) tags.push(`<span class="rx-meta-tag rx-meta-tag--proximity">Niveau ${esc(r.mosar.proximity_level)}</span>`);
    const country = r.country || r.publication_country || r.country_name;
    if(country) tags.push(`<span class="rx-meta-tag">${esc(country)}</span>`);
    (r.languages||[]).map(langLabel).forEach(v => tags.push(`<span class="rx-meta-tag">${esc(v)}</span>`));
    if(r.periodicity) tags.push(`<span class="rx-meta-tag">${esc(r.periodicity)}</span>`);
    return tags.join('<span class="rx-meta-sep">·</span>');
  }

  function render(records){
    const rows=filtered(records); root.querySelector('.rx-summary').textContent=`${rows.length} revue${rows.length>1?'s':''} sur ${records.length}`;
    root.querySelector('.rx-reset').disabled=!activeFilters();
    const cards=root.querySelector('.rx-cards');
    if(!rows.length){ cards.innerHTML='<div class="rx-empty">Aucune revue ne correspond aux filtres sélectionnés.</div>'; return; }
    cards.innerHTML=rows.map(r=>{
      const specific = `${REVUE_IMAGE_BASE}${encodeURIComponent(r.mirabel_id)}.jpg`;
      const fallback = `${REVUE_IMAGE_BASE}default.jpg`;
      const diamond = isDiamond(r) ? `<span class="rx-diamond-medal" title="Labellisation : Diamond journal" aria-label="Diamond journal">${icons.medal}</span>` : '';
      const illustration = `<div class="rx-card-visual"><img src="${specific}" data-fallback="${fallback}" alt="" loading="lazy">${diamond}</div>`;
      const publisher = r.publishers?.length ? `<div class="rx-publisher">${esc(r.publishers.join(', '))}</div>` : '';
      const signals=[];
      if(r.mosar?.open_access) signals.push(accessMark(r.mosar.open_access));
      if(r.publication_format) signals.push(formatMark(r.publication_format));
      const actions=[];
      if(r.ddh?.url) actions.push(`<a class="rx-action" href="${esc(r.ddh.url)}" target="_blank" rel="noopener" title="Voir la revue dans le Diamond Discovery Hub"><img class="rx-brand-icon" src="${ICON_BASE}picto_ddh.png" alt="">DDH</a>`);
      actions.push(`<a class="rx-action" href="${esc(r.mirabel_url)}" target="_blank" rel="noopener" title="Voir la revue dans Mir@bel"><img class="rx-brand-icon" src="${ICON_BASE}picto_mirabel.png" alt="">Mir@bel</a>`);
      if(r.journal_url) actions.push(`<a class="rx-action rx-action--website" href="${esc(r.journal_url)}" target="_blank" rel="noopener" title="Site web de la revue">${icons.world}<span>Site web ↗</span></a>`);
      const tags=metaTags(r);
      return `<article class="rx-card">${illustration}<div class="rx-card-body"><h2>${esc(r.title)}</h2>${publisher}<div class="rx-signals">${signals.join('')}</div><div class="rx-actions">${actions.join('')}</div><div class="rx-issn">${r.issn?.length?`ISSN ${esc(r.issn.join(', '))}`:''}</div>${tags?`<div class="rx-meta-tags">${tags}</div>`:''}</div></article>`;
    }).join('');
    cards.querySelectorAll('.rx-card-visual img[data-fallback]').forEach(img => {
      img.addEventListener('error', () => {
        const fallback = img.dataset.fallback;
        if (fallback && img.getAttribute('src') !== fallback) img.setAttribute('src', fallback);
      }, {once:true});
    });
  }
})();
