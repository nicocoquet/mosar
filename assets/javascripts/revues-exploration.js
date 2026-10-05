(() => {
  const root = document.getElementById('revues-explorer');
  if (!root) return;
  const source = root.dataset.source;
  const esc = (s='') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const langLabel = code => ({fre:'Français',fra:'Français',eng:'Anglais',deu:'Allemand',ger:'Allemand',ita:'Italien',spa:'Espagnol',por:'Portugais'}[code] || code);
  const state = {q:'', proximity:new Set(), access:new Set(), themes:new Set(), languages:new Set()};

  fetch(source).then(r => { if(!r.ok) throw new Error(r.status); return r.json(); }).then(data => init(data)).catch(err => { root.innerHTML = `<p>Impossible de charger les données (${esc(err.message)}).</p>`; });

  function init(data){
    const records = data.records || [];
    root.innerHTML = `<div class="rx-toolbar"><input class="rx-search" type="search" placeholder="Rechercher une revue, un ISSN, un éditeur…" aria-label="Rechercher"><div class="rx-summary"></div></div><div class="rx-layout"><aside class="rx-facets"><h2>Affiner</h2><div class="rx-facet-list"></div><button class="rx-reset" type="button">Réinitialiser</button></aside><section class="rx-cards" aria-live="polite"></section></div>`;
    root.querySelector('.rx-search').addEventListener('input', e => { state.q=e.target.value.trim().toLocaleLowerCase('fr'); render(records); });
    root.querySelector('.rx-reset').addEventListener('click', () => { Object.keys(state).forEach(k => k==='q' ? state.q='' : state[k].clear()); root.querySelector('.rx-search').value=''; root.querySelectorAll('input[type=checkbox]').forEach(i=>i.checked=false); render(records); });
    buildFacets(records); render(records);
  }

  function values(records, getter){ const c=new Map(); records.flatMap(getter).filter(Boolean).forEach(v=>c.set(v,(c.get(v)||0)+1)); return [...c.entries()].sort((a,b)=>a[0].localeCompare(b[0],'fr')); }
  function buildFacets(records){
    const specs = [
      ['proximity','Niveau de proximité', r => r.mosar?.proximity_level ? [`Niveau ${r.mosar.proximity_level}`] : []],
      ['access','Accès', r => r.mosar?.open_access ? [r.mosar.open_access] : []],
      ['themes','Thématiques Mir@bel', r => r.themes || []],
      ['languages','Langues', r => (r.languages || []).map(langLabel)]
    ];
    const box=root.querySelector('.rx-facet-list');
    specs.forEach(([key,title,getter])=>{
      const vals=values(records,getter); if(!vals.length) return;
      const section=document.createElement('section'); section.className='rx-facet';
      section.innerHTML=`<h3>${esc(title)}</h3><div class="rx-facet-options">${vals.map(([v,n])=>`<label class="rx-option"><input type="checkbox" data-facet="${key}" value="${esc(v)}"><span>${esc(v)}</span><span class="rx-count">${n}</span></label>`).join('')}</div>`;
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
    if(!matchesSet(state.themes,r.themes||[])) return false;
    if(!matchesSet(state.languages,(r.languages||[]).map(langLabel))) return false;
    return true;
  }); }

  function render(records){
    const rows=filtered(records); root.querySelector('.rx-summary').textContent=`${rows.length} revue${rows.length>1?'s':''} sur ${records.length}`;
    const cards=root.querySelector('.rx-cards');
    if(!rows.length){ cards.innerHTML='<div class="rx-empty">Aucune revue ne correspond aux filtres sélectionnés.</div>'; return; }
    cards.innerHTML=rows.map(r=>{
      const meta=[]; if(r.publishers?.length) meta.push(r.publishers.join(', ')); if(r.languages?.length) meta.push(r.languages.map(langLabel).join(', ')); if(r.issn?.length) meta.push(`ISSN ${r.issn.join(', ')}`);
      const badges=[]; (r.themes||[]).slice(0,3).forEach(v=>badges.push(`<span class="rx-badge">${esc(v)}</span>`));
      if(r.mosar){ if(r.mosar.proximity_level) badges.unshift(`<span class="rx-badge rx-badge--mosar">Niveau ${esc(r.mosar.proximity_level)}</span>`); if(r.mosar.open_access) badges.push(`<span class="rx-badge rx-badge--mosar">${esc(r.mosar.open_access)}</span>`); }
      const links=[`<a href="${esc(r.mirabel_url)}" target="_blank" rel="noopener">Notice Mir@bel ↗</a>`]; if(r.journal_url) links.unshift(`<a href="${esc(r.journal_url)}" target="_blank" rel="noopener">Site de la revue ↗</a>`);
      return `<article class="rx-card"><h2>${esc(r.title)}</h2><div class="rx-meta">${meta.map(x=>`<span>${esc(x)}</span>`).join('')}</div><div class="rx-badges">${badges.join('')}</div><div class="rx-links">${links.join('')}</div></article>`;
    }).join('');
  }
})();
