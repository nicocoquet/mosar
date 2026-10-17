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
    value === 'diamond'
      ? config.diamondFacetLabel
      : (config.values?.[String(value)] ?? String(value));
  const esc = (s='') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  const periodicityCount = value => {
    const known = {annuel:1, semestriel:2, quadrimestriel:3, trimestriel:4,
      bimestriel:6, mensuel:12, bimensuel:24};
    const v = String(value).trim().toLocaleLowerCase('fr');
    if (Object.hasOwn(known, v)) return known[v];
    const match = v.match(/^(\d+)\s+(?:numéros? par an|n(?:os|ᵒˢ)\/an)$/);
    return match ? Number(match[1]) : null;
  };
  const periodicityRank = value => {
    const count = periodicityCount(value);
    if (count !== null) return count;
    return ({bisannuel:25, 'parution continue':26, irrégulier:27})[String(value).toLocaleLowerCase('fr')] ?? 100;
  };
  const periodicityLabel = value => {
    const count = periodicityCount(value);
    if (/^\d+\s+(?:numéros? par an|n(?:os|ᵒˢ)\/an)$/.test(String(value).trim().toLocaleLowerCase('fr'))) {
      return config.locale === 'en' ? count + ' issues/year' : count + ' nos/an';
    }
    return config.periodicityLabels?.[value] ?? displayValue(value);
  };
  const periodicityHtml = value => esc(value)
    .replace(/n(?:os|ᵒˢ)\/an/g, 'n<sup>os</sup>/an')
    .replace(/n°/g, 'n<sup>o</sup>');
  const issnLine = record => {
    const details = record.issn_details || [];
    if (!details.length) return (record.issn || []).length ? 'ISSN ' + esc(record.issn.join(', ')) : '';
    const seen = new Set();
    const entries = [];
    details.forEach(item => {
      const value = String(item.issn || '').trim();
      if (!value || seen.has(value)) return;
      seen.add(value);
      const support = String(item.support || '').trim().toLocaleLowerCase('fr');
      const label = support === 'electronique' || support === 'électronique' ? 'ISSN-E' : 'ISSN';
      entries.push({label, value});
    });
    return entries.map(({label, value}) => label + ' ' + esc(value)).join(' · ');
  };
  const langLabel = code => config.languages[String(code).toLowerCase()] || String(code).toUpperCase();
  const valueOrUnknown = value => value === null || value === undefined || String(value).trim()==='' ? config.unknownLabel : String(value).trim();
  const listOrUnknown = values => Array.isArray(values) && values.length ? values.filter(Boolean).map(String) : [config.unknownLabel];
  const state = {q:''};
  config.facets.forEach(({key}) => { state[key] = new Set(); });
  const FACET_LABELS = Object.fromEntries(config.facets.map(({key,label}) => [key,label]));
  const ASSET_BASE = new URL('../', document.currentScript.src).href;
  const ICON_BASE = `${ASSET_BASE}assets/icons/`;
  const REVUE_IMAGE_BASE = `${ASSET_BASE}assets/journals/`;
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
  function buildFacets(records, proximityLevels) {
    const box = root.querySelector('.rx-facet-list');

    config.facets.forEach(({key, label}) => {
      if (key === 'licence_mentioned') return; // Groupe intégré à la facette licence.
      let vals = values(records, r => recordValues(r)[key]);

      if (key === 'proximity') {
        vals.sort((a, b) => {
          const na = parseInt(a[0].match(/\d+/)?.[0] || 99);
          const nb = parseInt(b[0].match(/\d+/)?.[0] || 99);
          return na - nb;
        });
      }

      if (key === 'perimetre') {
        const order = config.perimetreOrder;
        vals.sort((a, b) => {
          const ia = order.indexOf(a[0]);
          const ib = order.indexOf(b[0]);
          return (ia < 0 ? order.length : ia) - (ib < 0 ? order.length : ib)
            || a[0].localeCompare(b[0], config.locale);
        });
      }

      if (key === 'periodicity') {
        vals.sort((a, b) => periodicityRank(a[0]) - periodicityRank(b[0])
          || a[0].localeCompare(b[0], config.locale));
      }

      if (key === 'indexing') {
        const order = ['DDH', 'DOAJ', 'ROAD', 'Wikidata', 'Wikipédia'];
        vals.sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]));
      }

      const section = document.createElement('details');
      section.className = 'rx-facet';
      section.dataset.facet = key;

      const scroll = key !== 'periodicity' && vals.length > config.facetScrollThreshold
        ? ' rx-facet-options--scroll'
        : '';

      const options = vals.map(([value, count], index) => {
        const isIndexing = key === 'indexing';
        const group = ['DDH', 'DOAJ', 'ROAD'].includes(value) ? 'open' : 'wiki';
        const previous = index ? vals[index - 1][0] : null;
        const previousGroup = ['DDH', 'DOAJ', 'ROAD'].includes(previous) ? 'open' : 'wiki';
        const groupHeading = isIndexing && (index === 0 || group !== previousGroup)
          ? `<div class="rx-indexing-heading${index ? ' rx-indexing-heading--separated' : ''}">${esc(config.indexingGroups[group])}</div>`
          : '';
        const infoText = isIndexing ? config.indexingInfo?.[value]
          : key === 'periodicity' ? config.periodicityInfo?.[value]
          : key === 'licence' && value === 'Licence CC ou DR variable pour une même publication'
            ? config.licenceHybridInfo : null;
        const info = infoText
          ? key === 'periodicity'
            ? `<button type="button" class="rx-indexing-info rx-indexing-info--html" aria-label="${esc(value)} : ${esc(infoText)}">i<span class="rx-indexing-tooltip">${periodicityHtml(infoText)}</span></button>`
            : `<button type="button" class="rx-indexing-info" data-tooltip="${esc(infoText)}" aria-label="${esc(value)} : ${esc(infoText)}">i</button>`
          : '';

        const isDiamondOption = key === 'labelling' && value === 'diamond';

        const labelText = isDiamondOption
          ? config.diamondFacetLabel
          : key === 'periodicity'
            ? periodicityLabel(value)
            : displayValue(value);

        const pictogram = isDiamondOption
          ? `<img class="rx-facet-diamond-icon"
                   src="${ICON_BASE}picto_diamond-access.png"
                   alt="">`
          : '';

        if (isIndexing || key === 'periodicity' || key === 'licence') return `${groupHeading}
          <div class="rx-indexing-option">
            <label class="rx-option">
              <input type="checkbox" data-facet="${esc(key)}" value="${esc(value)}">
              <span>${key === 'periodicity' ? periodicityHtml(labelText) : esc(labelText)}</span>
            </label>
            ${info}
            <span class="rx-count">${count}</span>
          </div>`;

        return `
          <label class="rx-option">
            <input type="checkbox"
                   data-facet="${esc(key)}"
                   value="${esc(value)}">
            ${pictogram}
            <span>${esc(labelText)}</span>
            <span class="rx-count">${count}</span>
          </label>`;
      }).join('');

      const licenceMentionedOptions = key === 'licence'
        ? ['oui', 'non'].map(value => {
          const count = records.filter(r => r.mosar?.licence_mentioned === value).length;
          return `<label class="rx-option">
            <input type="checkbox" data-facet="licence_mentioned" value="${value}">
            <span>${esc(config.licenceMentionedLabels[value])}</span>
            <span class="rx-count">${count}</span>
          </label>`;
        }).join('')
        : '';
      const licenceMentionedGroup = key === 'licence'
        ? `<div class="rx-indexing-heading rx-indexing-heading--separated">${esc(config.licenceMentionedHeading)}</div>${licenceMentionedOptions}`
        : '';

      section.innerHTML = `
        <summary>
          <span>${esc(label)}</span>
          <span class="rx-chevron" aria-hidden="true"></span>
        </summary>
        <div class="rx-facet-options${scroll}">
          ${options}
          ${licenceMentionedGroup}
        </div>`;

      box.appendChild(section);
    });

    box.addEventListener('change', e => {
      const input = e.target.closest('input[data-facet]');
      if (!input) return;

      const selected = state[input.dataset.facet];

      if (input.checked) {
        selected.add(input.value);
        input.closest('details').open = true;
      } else {
        selected.delete(input.value);
      }

      render(records, proximityLevels);
    });
  }

  function matchesSet(selected,vals){return !selected.size||vals.some(v=>selected.has(v));}
  function recordValues(r) {
    return {
      proximity: [
        r.mosar?.proximity_level
          ? config.levelLabel(r.mosar.proximity_level)
          : config.unknownLabel
      ],
      access: [valueOrUnknown(r.mosar?.open_access)],
      format: [valueOrUnknown(r.publication_format)],
      labelling: r.is_diamond ? ['diamond'] : [],
      discipline: [valueOrUnknown(r.mosar?.discipline_normalized)],
      themes: listOrUnknown(r.themes),
      languages: r.languages?.length
        ? r.languages.map(langLabel)
        : [config.unknownLabel],
      periodicity: [valueOrUnknown(r.periodicity)],
      licence: [valueOrUnknown(r.mosar?.licence_normalized)],
      licence_mentioned: r.mosar?.licence_mentioned ? [r.mosar.licence_mentioned] : [],
      editorial_structure: [
        valueOrUnknown(r.mosar?.editorial_structure_normalized)
      ],
      publishers: listOrUnknown(r.publishers),
      perimetre: Array.isArray(r.mosar?.perimetre) && r.mosar.perimetre.length
        ? r.mosar.perimetre
        : ['Non renseigné'],
      laboratoires: Array.isArray(r.mosar?.laboratoires)
        ? r.mosar.laboratoires.filter(Boolean)
        : [],
      associations: Array.isArray(r.mosar?.associations) ? r.mosar.associations.filter(Boolean) : [],
      diffuseurs_numeriques: Array.isArray(r.mosar?.diffuseurs_numeriques) ? r.mosar.diffuseurs_numeriques.filter(Boolean) : [],
      indexing: ['DDH', 'DOAJ', 'ROAD', 'Wikidata', 'Wikipédia'].filter(
        name => name === 'Wikipédia' ? Boolean(r.references?.[name]) : Boolean(r.references?.[name]?.url)
      )
    };
  }
  function filtered(records){return records.filter(r=>{const hay=[r.title,r.sigle,...(r.issn||[]),...(r.publishers||[])].join(' ').toLocaleLowerCase('fr');if(state.q&&!hay.includes(state.q))return false;const v=recordValues(r);return Object.keys(v).every(k=>matchesSet(state[k],v[k]));});}
  function sortRecords(rows, proximityLevels){return [...rows].sort((a,b)=>{const parse=r=>{const n=parseInt(r.mosar?.proximity_level,10);return [Number.isInteger(n)&&proximityLevels.includes(n)?n:99,(r.title||'').toLocaleLowerCase('fr')];};const ka=parse(a),kb=parse(b);return ka[0]-kb[0]||ka[1].localeCompare(kb[1],'fr');});}
  function activeFilters(){return state.q||Object.entries(state).some(([k,v])=>k!=='q'&&v.size);}
  function renderActiveFilters(){const box=root.querySelector('.rx-active-filters');if(!box)return;const tags=[];Object.entries(state).forEach(([key,selected])=>{if(key==='q'||!selected.size)return;selected.forEach(value=>tags.push(`<span class="rx-active-filter"><span class="rx-active-filter-label">${esc(FACET_LABELS[key])} :</span> ${esc(key === 'licence_mentioned' ? config.licenceMentionedLabels[value] : displayValue(value))}</span>`));});box.innerHTML=tags.length?`<div class="rx-active-filters-title">${esc(config.selectedFiltersLabel)}</div><div class="rx-active-filters-list">${tags.join('')}</div>`:'';}
  function formatMark(format){if(!format)return'';const marks=format==='Papier et numérique'?`${icons.paper}${icons.digital}`:format==='Papier'?icons.paper:icons.digital;return `<span class="rx-signal" title="${esc(config.formatTitle)} : ${esc(displayValue(format))}"><span class="rx-format-icons">${marks}</span><span>${esc(displayValue(format))}</span></span>`;}
  function accessMark(access){if(!access)return'';const restricted=/restreint|fermé|ferme/i.test(access);return `<span class="rx-signal ${restricted?'rx-signal--restricted':'rx-signal--open'}" title="${esc(displayValue(access))}">${restricted?icons.closed:icons.open}<span>${esc(displayValue(access))}</span></span>`;}
  function isDiamond(r) {
    return r.is_diamond === true;
  }
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
    const rows=sortRecords(filtered(records), proximityLevels);
    const [shown, total] = config.resultsLabel(rows.length, records.length);
    const summary = root.querySelector('.rx-summary');
    const highlighted = document.createElement('strong');
    highlighted.textContent = shown;
    summary.replaceChildren(highlighted, document.createTextNode(` ${total}`));
    root.querySelector('.rx-reset').disabled=!activeFilters();renderActiveFilters();
    const cards=root.querySelector('.rx-cards');if(!rows.length){cards.innerHTML=`<div class="rx-empty">${esc(config.emptyLabel)}</div>`;return;}
    cards.innerHTML=rows.map(r=>{const specific=`${REVUE_IMAGE_BASE}${encodeURIComponent(r.mirabel_id)}.jpg`,fallback=`${REVUE_IMAGE_BASE}default.jpg`;const diamond=isDiamond(r)?`<span class="rx-diamond-medal" title="${esc(config.diamondTitle)}" aria-label="${esc(config.diamondTitle)}"><img src="${ICON_BASE}picto_diamond-access.png" alt=""></span>`:'';const illustration=`<div class="rx-card-visual"><img src="${specific}" data-fallback="${fallback}" alt="" loading="lazy">${diamond}</div>`;const subtitle=r.subtitle?`<div class="rx-subtitle">${esc(r.subtitle)}</div>`:'';const publisher=r.publishers?.length?`<div class="rx-publisher">${r.publishers.map(name=>`<div>${esc(name)}</div>`).join('')}</div>`:'';const signals=[];if(r.mosar?.open_access)signals.push(accessMark(r.mosar.open_access));if(r.publication_format)signals.push(formatMark(r.publication_format));const actions=[];if(r.ddh?.url)actions.push(`<a class="rx-action" href="${esc(r.ddh.url)}" target="_blank" rel="noopener" title="${esc(config.ddhTitle)}"><img class="rx-brand-icon" src="${ICON_BASE}picto_ddh.png" alt="">DDH</a>`);actions.push(`<a class="rx-action" href="${esc(r.mirabel_url)}" target="_blank" rel="noopener" title="${esc(config.mirabelTitle)}"><img class="rx-brand-icon" src="${ICON_BASE}picto_mirabel.png" alt="">Mir@bel</a>`);if(r.journal_url)actions.push(`<a class="rx-action rx-action--website" href="${esc(r.journal_url)}" target="_blank" rel="noopener" title="${esc(config.websiteTitle)}">${icons.world}<span>${esc(config.websiteLabel)}</span></a>`);const tags=metaTags(r);return `<article class="rx-card">${illustration}<div class="rx-card-body"><h2>${esc(r.title)}</h2>${subtitle}${publisher}<div class="rx-signals">${signals.join('')}</div><div class="rx-actions">${actions.join('')}</div><div class="rx-issn">${issnLine(r)}</div>${tags?`<div class="rx-meta-tags">${tags}</div>`:''}</div></article>`;}).join('');
    cards.querySelectorAll('.rx-card-visual img[data-fallback]').forEach(img=>{img.addEventListener('error',()=>{const fallback=img.dataset.fallback;if(fallback&&img.getAttribute('src')!==fallback)img.setAttribute('src',fallback);},{once:true});});
  }
})();
