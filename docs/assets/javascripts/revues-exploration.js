(() => {
  const root = document.getElementById('revues-explorer');
  if (!root) return;
  const source = root.dataset.source;
  const config = window.MOSAR_REVUES_CONFIG;
  if (!config) {
    root.innerHTML = `<p>${root.getAttribute('lang') === 'en'
      ? 'Explorer configuration not found.'
      : 'Configuration de l’explorateur introuvable.'}</p>`;
    return;
  }
  const displayValue = value =>
  config.values?.[String(value)] ?? String(value);
  const esc = (s='') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const langLabel = code => config.languages[String(code).toLowerCase()] || String(code).toUpperCase();
  const valueOrUnknown = value => value === null || value === undefined || String(value).trim()==='' ? config.unknownLabel : String(value).trim();
  const listOrUnknown = values => Array.isArray(values) && values.length ? values.filter(Boolean).map(String) : [config.unknownLabel];
  const state = {q:''};
  config.facets.forEach(({key}) => { state[key] = new Set(); });
  const FACET_LABELS = Object.fromEntries(config.facets.map(({key,label}) => [key,label]));
  const ASSET_BASE = new URL('../', document.currentScript.src).href;
  const ICON_BASE = `${ASSET_BASE}images/icons/`;
  const REVUE_IMAGE_BASE = `${ASSET_BASE}images/revues/`;
  const icons={open:'<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11v-4a4 4 0 0 1 7.8-1.25"/></svg>',closed:'<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11v-4a4 4 0 0 1 8 0v4"/></svg>',paper:'<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5a2.5 2.5 0 0 1 2.5-2.5h13.5"/><path d="M6.5 2h13.5v20h-13.5a2.5 2.5 0 0 1-2.5-2.5v-15a2.5 2.5 0 0 1 2.5-2.5z"/></svg>',digital:'<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4m0 2a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-14a2 2 0 0 1-2-2z"/><path d="M8 20h8"/><path d="M12 18v2"/></svg>',world:'<svg class="rx-ui-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8"/><path d="M3.6 15h16.8"/><path d="M11.5 3a17 17 0 0 0 0 18"/><path d="M12.5 3a17 17 0 0 1 0 18"/></svg>'};

  fetch(source).then(r=>{if(!r.ok)throw new Error(r.status);return r.json();}).then(data=>init(data)).catch(err=>{root.innerHTML=`<p>${esc(config.loadError)} (${esc(err.message)}).</p>`;});

  function init(data){
    const records=data.records||[];
    const proximityLevels=data.model?.proximity_levels||[];
    root.innerHTML=`<div class="rx-layout"><aside class="rx-facets"><div class="rx-facets-head"><h2>${esc(config.facetsTitle)}</h2><div class="rx-active-filters" aria-live="polite"></div><button class="rx-reset" type="button" disabled>${esc(config.resetLabel)}</button></div><div class="rx-facet-list"></div></aside><div class="rx-results"><div class="rx-toolbar"><input class="rx-search" type="search" placeholder="${esc(config.searchPlaceholder)}" aria-label="${esc(config.searchAriaLabel)}"><div class="rx-summary"></div></div><section class="rx-cards" aria-live="polite"></section></div></div>`;
    root.querySelector('.rx-search').addEventListener('input',e=>{state.q=e.target.value.trim().toLocaleLowerCase(config.locale);render(records, proximityLevels);});
    root.querySelector('.rx-reset').addEventListener('click',()=>{Object.keys(state).forEach(k=>k==='q'?state.q='':state[k].clear());root.querySelector('.rx-search').value='';root.querySelectorAll('input[type=checkbox]').forEach(i=>i.checked=false);render(records, proximityLevels);});
    buildFacets(records, proximityLevels); render(records, proximityLevels);
  }

  function values(records,getter){const c=new Map();records.flatMap(getter).filter(Boolean).forEach(v=>c.set(v,(c.get(v)||0)+1));return [...c.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'fr'));}
  function buildFacets(records, proximityLevels){
    const getters={
      proximity:r=>[r.mosar?.proximity_level?config.levelLabel(r.mosar.proximity_level):config.unknownLabel],
      access:r=>[valueOrUnknown(r.mosar?.open_access)],
      format:r=>[valueOrUnknown(r.publication_format)],
      periodicity:r=>[valueOrUnknown(r.periodicity)],
      themes:r=>listOrUnknown(r.themes),
      languages:r=>(r.languages?.length?r.languages.map(langLabel):[config.unknownLabel]),
      publishers:r=>listOrUnknown(r.publishers)
    };
    const specs=config.facets.map(({key,label})=>[key,label,getters[key]]);
    const box=root.querySelector('.rx-facet-list');
    specs.forEach(([key,title,getter])=>{
      let vals=values(records,getter);
      if(key==='proximity') vals.sort((a,b)=>{const na=parseInt(a[0].match(/\d+/)?.[0]||99),nb=parseInt(b[0].match(/\d+/)?.[0]||99);return na-nb;});
      const section=document.createElement('details'); section.className='rx-facet'; section.dataset.facet=key;
      const scroll=vals.length>config.facetScrollThreshold?' rx-facet-options--scroll':'';
      section.innerHTML=`<summary><span>${esc(title)}</span><span class="rx-chevron" aria-hidden="true"></span></summary><div class="rx-facet-options${scroll}">${vals.map(([v,n])=>`<label class="rx-option"><input type="checkbox" data-facet="${key}" value="${esc(v)}"><span>${esc(displayValue(v))}</span><span class="rx-count">${n}</span></label>`).join('')}</div>`;
      box.appendChild(section);
    });
    box.addEventListener('change',e=>{const i=e.target.closest('input[data-facet]');if(!i)return;const set=state[i.dataset.facet];i.checked?set.add(i.value):set.delete(i.value);if(i.checked)i.closest('details').open=true;render(records, proximityLevels);});
  }

  function matchesSet(selected,vals){return !selected.size||vals.some(v=>selected.has(v));}
  function recordValues(r){return {proximity:[r.mosar?.proximity_level?config.levelLabel(r.mosar.proximity_level):config.unknownLabel],access:[valueOrUnknown(r.mosar?.open_access)],format:[valueOrUnknown(r.publication_format)],periodicity:[valueOrUnknown(r.periodicity)],themes:listOrUnknown(r.themes),languages:r.languages?.length?r.languages.map(langLabel):[config.unknownLabel],publishers:listOrUnknown(r.publishers)};}
  function filtered(records){return records.filter(r=>{const hay=[r.title,r.sigle,...(r.issn||[]),...(r.publishers||[])].join(' ').toLocaleLowerCase('fr');if(state.q&&!hay.includes(state.q))return false;const v=recordValues(r);return Object.keys(v).every(k=>matchesSet(state[k],v[k]));});}
  function sortRecords(rows, proximityLevels){return [...rows].sort((a,b)=>{const parse=r=>{const n=parseInt(r.mosar?.proximity_level,10);return [Number.isInteger(n)&&proximityLevels.includes(n)?n:99,(r.title||'').toLocaleLowerCase('fr')];};const ka=parse(a),kb=parse(b);return ka[0]-kb[0]||ka[1].localeCompare(kb[1],'fr');});}
  function activeFilters(){return state.q||Object.entries(state).some(([k,v])=>k!=='q'&&v.size);}
  function renderActiveFilters(){const box=root.querySelector('.rx-active-filters');if(!box)return;const tags=[];Object.entries(state).forEach(([key,selected])=>{if(key==='q'||!selected.size)return;selected.forEach(value=>tags.push(`<span class="rx-active-filter"><span class="rx-active-filter-label">${esc(FACET_LABELS[key])} :</span> ${esc(displayValue(value))}</span>`));});box.innerHTML=tags.length?`<div class="rx-active-filters-title">${esc(config.selectedFiltersLabel)}</div><div class="rx-active-filters-list">${tags.join('')}</div>`:'';}
  function formatMark(format){if(!format)return'';const marks=format==='Papier et numérique'?`${icons.paper}${icons.digital}`:format==='Papier'?icons.paper:icons.digital;return `<span class="rx-signal" title="${esc(config.formatTitle)} : ${esc(displayValue(format))}"><span class="rx-format-icons">${marks}</span><span>${esc(displayValue(format))}</span></span>`;}
  function accessMark(access){if(!access)return'';const restricted=/restreint|fermé|ferme/i.test(access);return `<span class="rx-signal ${restricted?'rx-signal--restricted':'rx-signal--open'}" title="${esc(access)}">${restricted?icons.closed:icons.open}<span>${esc(displayValue(access))}</span></span>`;}
  function isDiamond(r){return(r.labels||[]).some(label=>label.toLowerCase().includes('ddh diamond journal'));}
    function metaTags(r) {
    const tags = [];

    if (r.mosar?.proximity_level) {
      tags.push(
        `<span class="rx-meta-tag rx-meta-tag--proximity">${esc(config.levelLabel(r.mosar.proximity_level))}</span>`
      );
    }

    const country = r.country || r.publication_country || r.country_name;
    if (country) {
      tags.push(`<span class="rx-meta-tag">${esc(country)}</span>`);
    }

    (r.languages || [])
      .map(langLabel)
      .forEach(v => tags.push(`<span class="rx-meta-tag">${esc(v)}</span>`));

    if (r.periodicity) {
      tags.push(
        `<span class="rx-meta-tag">${esc(displayValue(r.periodicity))}</span>`
      );
    }

    return tags.join('<span class="rx-meta-sep">·</span>');
  }

  function render(records, proximityLevels){
    const rows=sortRecords(filtered(records), proximityLevels);root.querySelector('.rx-summary').textContent =
      config.resultsLabel(rows.length, records.length);root.querySelector('.rx-reset').disabled=!activeFilters();renderActiveFilters();
    const cards=root.querySelector('.rx-cards');if(!rows.length){cards.innerHTML=`<div class="rx-empty">${esc(config.emptyLabel)}</div>`;return;}
    cards.innerHTML=rows.map(r=>{const specific=`${REVUE_IMAGE_BASE}${encodeURIComponent(r.mirabel_id)}.jpg`,fallback=`${REVUE_IMAGE_BASE}default.jpg`;const diamond=isDiamond(r)?`<span class="rx-diamond-medal" title="${esc(config.diamondTitle)}" aria-label="Diamond journal"><img src="${ICON_BASE}picto_diamond-access.png" alt=""></span>`:'';const illustration=`<div class="rx-card-visual"><img src="${specific}" data-fallback="${fallback}" alt="" loading="lazy">${diamond}</div>`;const publisher=r.publishers?.length?`<div class="rx-publisher">${esc(r.publishers.join(', '))}</div>`:'';const signals=[];if(r.mosar?.open_access)signals.push(accessMark(r.mosar.open_access));if(r.publication_format)signals.push(formatMark(r.publication_format));const actions=[];if(r.ddh?.url)actions.push(`<a class="rx-action" href="${esc(r.ddh.url)}" target="_blank" rel="noopener" title="${esc(config.ddhTitle)}"><img class="rx-brand-icon" src="${ICON_BASE}picto_ddh.png" alt="">DDH</a>`);actions.push(`<a class="rx-action" href="${esc(r.mirabel_url)}" target="_blank" rel="noopener" title="${esc(config.mirabelTitle)}"><img class="rx-brand-icon" src="${ICON_BASE}picto_mirabel.png" alt="">Mir@bel</a>`);if(r.journal_url)actions.push(`<a class="rx-action rx-action--website" href="${esc(r.journal_url)}" target="_blank" rel="noopener" title="${esc(config.websiteTitle)}">${icons.world}<span>${esc(config.websiteLabel)}</span></a>`);const tags=metaTags(r);return `<article class="rx-card">${illustration}<div class="rx-card-body"><h2>${esc(r.title)}</h2>${publisher}<div class="rx-signals">${signals.join('')}</div><div class="rx-actions">${actions.join('')}</div><div class="rx-issn">${r.issn?.length?`ISSN ${esc(r.issn.join(', '))}`:''}</div>${tags?`<div class="rx-meta-tags">${tags}</div>`:''}</div></article>`;}).join('');
    cards.querySelectorAll('.rx-card-visual img[data-fallback]').forEach(img=>{img.addEventListener('error',()=>{const fallback=img.dataset.fallback;if(fallback&&img.getAttribute('src')!==fallback)img.setAttribute('src',fallback);},{once:true});});
  }
})();
