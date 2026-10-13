/* Infobulles partagées des graphiques SVG Mosar : souris, clavier, tactile. */
(() => {
  const selector = '.statistics-card .chart-tooltip-target';
  const tooltip = document.createElement('div');
  tooltip.className = 'mosar-chart-tooltip';
  tooltip.id = 'mosar-chart-tooltip';
  tooltip.setAttribute('role', 'tooltip');
  tooltip.hidden = true;
  document.body.appendChild(tooltip);
  let active = null;
  let pinned = false;

  function language(target) {
    return target.closest('[lang]')?.getAttribute('lang') || document.documentElement.lang || 'fr';
  }

  function show(target) {
    if (!target || !target.matches(selector)) return;
    if (active && active !== target) active.removeAttribute('aria-describedby');
    active = target;
    const en = language(target).toLowerCase().startsWith('en');
    const count = Number(target.dataset.tooltipCount || 0);
    tooltip.replaceChildren();
    const heading = document.createElement('strong');
    heading.textContent = target.dataset.tooltipLabel || '';
    const info = document.createElement('span');
    info.textContent = (en ? 'Count: ' : 'Effectif : ') + count.toLocaleString(en ? 'en' : 'fr') +
      (en ? ' journals' : ' revues') + ' · ' + (target.dataset.tooltipPercent || '0') + ' %';
    tooltip.append(heading, info);
    tooltip.hidden = false;
    target.setAttribute('aria-describedby', tooltip.id);
    position(target);
  }

  function position(target) {
    if (!target || tooltip.hidden) return;
    const rect = target.getBoundingClientRect();
    const bounds = tooltip.getBoundingClientRect();
    const left = Math.max(8, Math.min(window.innerWidth - bounds.width - 8, rect.left + rect.width / 2 - bounds.width / 2));
    let top = rect.top - bounds.height - 10;
    if (top < 8) top = Math.min(window.innerHeight - bounds.height - 8, rect.bottom + 10);
    tooltip.style.left = left + 'px';
    tooltip.style.top = Math.max(8, top) + 'px';
  }

  function hide() {
    if (active) active.removeAttribute('aria-describedby');
    active = null;
    pinned = false;
    tooltip.hidden = true;
  }

  document.addEventListener('pointerover', (event) => {
    if (event.pointerType === 'touch' || pinned) return;
    const target = event.target.closest?.(selector);
    if (target) show(target);
  });
  document.addEventListener('pointerout', (event) => {
    if (pinned || !active || event.pointerType === 'touch') return;
    if (active.contains(event.relatedTarget)) return;
    if (event.target === active || active.contains(event.target)) hide();
  });
  document.addEventListener('focusin', (event) => {
    const target = event.target.closest?.(selector);
    if (target) { pinned = false; show(target); }
  });
  document.addEventListener('focusout', (event) => {
    if (active && (event.target === active || active.contains(event.target))) hide();
  });
  document.addEventListener('click', (event) => {
    const target = event.target.closest?.(selector);
    if (!target) { if (pinned) hide(); return; }
    if (pinned && active === target) hide();
    else { show(target); pinned = true; }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') hide();
    if ((event.key === 'Enter' || event.key === ' ') && event.target.matches?.(selector)) {
      event.preventDefault();
      if (pinned && active === event.target) hide();
      else { show(event.target); pinned = true; }
    }
  });
  window.addEventListener('resize', () => position(active));
  window.addEventListener('scroll', () => { if (pinned) position(active); else hide(); }, true);
})();
