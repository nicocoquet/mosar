/* Mosar Admin — no tokens or XLSX content are written to persistent browser storage. */
(() => {
  'use strict';
  const root = document.getElementById('mosar-admin');
  if (!root) return;
  const $ = id => document.getElementById(id);
  const en = root.dataset.lang === 'en';
  const t = (fr, english) => en ? english : fr;
  // Set data-api-url to the actual HTTPS Render origin when deploying the service.
  const api = (root.dataset.apiUrl || '').trim().replace(/\/$/, '');
  const configured = /^https:\/\/[^/]+$/i.test(api);
  const state = {session: null, file: null, encoded: null, previewToken: null, jobToken: null, busy: false};
  // Noms d'affichage uniquement ; les autorisations restent fondées sur le login GitHub.
  const displayNames = Object.freeze({
    nicocoquet: 'Nicolas Coquet (MSH Mondes)',
    'gaelle-david': 'Gaëlle David (MSH Mondes)',
  });
  function displayName(login) { return displayNames[String(login || '').toLowerCase()] || login; }
  const MAX_BYTES = 15 * 1024 * 1024;
  const POLL_MS = 8000;
  let pollTimer = null;
  function stopPolling() { if (pollTimer !== null) { clearTimeout(pollTimer); pollTimer = null; } }
  function schedulePolling() {
    stopPolling();
    if (state.session && state.jobToken) pollTimer = setTimeout(refresh, POLL_MS);
  }
  function error(message) { $('admin-error').textContent = message || ''; $('admin-error').hidden = !message; }
  function busy(value) { state.busy = value; sync(); }
  function sync() {
    const connected = !!state.session;
    $('admin-login').disabled = !configured || state.busy || connected;
    $('admin-logout').hidden = !connected;
    $('admin-logout').disabled = state.busy;
    $('admin-file').disabled = !connected || state.busy || !!state.jobToken;
    $('admin-preview').disabled = !connected || !state.file || state.busy || !!state.jobToken;
    $('admin-publish').disabled = !connected || !state.previewToken || !$('admin-confirm').checked || state.busy;
    $('admin-reset').disabled = state.busy;
    $('admin-refresh').disabled = !connected || !state.jobToken || state.busy;
  }
  function resetPreview() {
    state.previewToken = null; state.encoded = null;
    $('admin-confirm').checked = false;
    $('admin-report-panel').hidden = true;
    $('admin-report').replaceChildren();
    sync();
  }
  async function request(path, options = {}) {
    const headers = {'Authorization': `Bearer ${state.session}`, ...(options.body ? {'Content-Type': 'application/json'} : {})};
    let response;
    try { response = await fetch(api + path, {...options, headers, cache: 'no-store'}); }
    catch { throw new Error(t('Service inaccessible. Réessayez ultérieurement.', 'Service unavailable. Please try again later.')); }
    let payload = {};
    try { payload = await response.json(); } catch { /* empty response */ }
    if (!response.ok) {
      if (response.status === 401) { state.session = null; stopPolling(); resetPreview(); $('admin-user').textContent = ''; sync(); }
      throw new Error(typeof payload.detail === 'string' ? payload.detail : t('Erreur du service.', 'Service error.'));
    }
    return payload;
  }
  function encodeFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(new Error(t('Lecture du fichier impossible.', 'Could not read file.')));
      reader.onload = () => {
        const result = reader.result;
        if (typeof result !== 'string') { reject(new Error('Invalid file data')); return; }
        resolve(result.slice(result.indexOf(',') + 1));
      };
      reader.readAsDataURL(file);
    });
  }
  function renderReport(report) {
    const pairs = [
      [t('Revues conservées', 'Journals retained'), report.rows_retained],
      [t('Colonnes conservées', 'Columns retained'), report.columns_retained],
      [t('Lignes sans ID exclues', 'Rows without ID removed'), report.rows_without_id_removed],
      [t('Colonnes confidentielles supprimées', 'Private columns removed'), report.private_columns_removed],
      [t('Autres colonnes supprimées', 'Other columns removed'), report.unknown_columns_removed],
      [t('Onglets exclus', 'Worksheets removed'), report.sheets_removed],
    ];
    const list = document.createElement('dl'); list.className = 'admin-report-list';
    for (const [label, value] of pairs) {
      const dt = document.createElement('dt'); dt.textContent = label;
      const dd = document.createElement('dd'); dd.textContent = Array.isArray(value) ? (value.join(', ') || '—') : String(value ?? '—');
      list.append(dt, dd);
    }
    $('admin-report').replaceChildren(list);
  }
  function safeLink(url, label) {
    if (!/^https:\/\//i.test(url || '')) return null;
    const a = document.createElement('a'); a.href = url; a.textContent = label; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a;
  }
  async function refresh() {
    if (!state.jobToken) return;
    busy(true); error('');
    try {
      const job = await request('/api/jobs/' + encodeURIComponent(state.jobToken));
      const labels = {queued: t('En attente de GitHub Actions…', 'Waiting for GitHub Actions…'), processing: t('Génération en cours…', 'Building site…'), failed: t('La publication a échoué. Consultez le workflow.', 'Publication failed. Check the workflow.'), completed: t('Workflow terminé avec succès.', 'Workflow completed successfully.')};
      $('admin-job-status').textContent = labels[job.status] || job.status;
      const resultStatus = $('admin-result-status');
      resultStatus.className = job.status === 'completed' ? 'admin-result-success' : job.status === 'failed' ? 'admin-result-failure' : '';
      resultStatus.textContent = job.status === 'completed'
        ? t('Publication terminée avec succès.', 'Publication completed successfully.')
        : job.status === 'failed'
          ? t('Échec de la publication. Consultez le suivi détaillé.', 'Publication failed. See detailed status.')
          : t('Traitement en cours. Résultat en attente…', 'Processing. Outcome pending…');
      const links = $('admin-job-links'); links.replaceChildren();
      if (job.workflow_url) { const a = safeLink(job.workflow_url, t('Consulter le workflow', 'View workflow')); if (a) links.append(a); }
      if (job.status === 'completed' && job.site_url) {
        const a = safeLink(job.site_url, t('Voir le site Mosar', 'Visit Mosar site'));
        if (a) { if (links.childNodes.length) links.append(' · '); links.append(a); }
      }
      if (job.status === 'queued' || job.status === 'processing') schedulePolling();
      else stopPolling();
    } catch (e) {
      if (!state.session) {
        error(t('Session expirée. Reconnectez-vous à GitHub. La publication déjà transmise continue sur GitHub Actions ; vous pouvez en consulter le résultat depuis le dépôt.', 'Session expired. Sign in to GitHub again. The submitted publication continues on GitHub Actions; you can check its result in the repository.'));
      } else {
        error(e.message);
        schedulePolling();
      }
    }
    finally { busy(false); }
  }
  $('admin-login').addEventListener('click', () => {
    if (!configured) return;
    const destination = new URL(window.location.href); destination.hash = '';
    window.location.assign(api + '/auth/github?returnTo=' + encodeURIComponent(destination.href));
  });
  $('admin-logout').addEventListener('click', async () => {
    busy(true);
    try { await request('/auth/logout', {method: 'POST'}); } catch { /* local logout still proceeds */ }
    stopPolling(); $('admin-processing-grid').hidden = true; state.session = null; state.file = null; state.jobToken = null; $('admin-file').value = ''; resetPreview(); $('admin-user').textContent = ''; error(''); busy(false);
  });
  $('admin-file').addEventListener('change', () => {
    state.file = $('admin-file').files?.[0] || null; resetPreview(); error('');
    if (state.file && (!/\.xlsx$/i.test(state.file.name) || !state.file.size || state.file.size > MAX_BYTES)) {
      error(t('Choisissez un fichier .xlsx non vide de 15 Mo maximum.', 'Choose a non-empty .xlsx file up to 15 MB.'));
      state.file = null;
    }
    sync();
  });
  $('admin-preview').addEventListener('click', async () => {
    if (!state.file) return;
    busy(true); error(''); resetPreview();
    try {
      state.encoded = await encodeFile(state.file);
      const result = await request('/api/preview', {method:'POST', body: JSON.stringify({filename:state.file.name, content:state.encoded})});
      state.previewToken = result.preview_token;
      renderReport(result.report);
      $('admin-report-panel').hidden = false;
    } catch (e) { state.encoded = null; error(e.message); }
    finally { busy(false); }
  });
  $('admin-confirm').addEventListener('change', sync);
  $('admin-reset').addEventListener('click', () => { resetPreview(); state.file = null; $('admin-file').value = ''; error(''); sync(); });
  $('admin-publish').addEventListener('click', async () => {
    if (!state.previewToken || !state.encoded || !$('admin-confirm').checked || !state.file) return;
    busy(true); error('');
    try {
      const result = await request('/api/publish', {method:'POST', body:JSON.stringify({filename:state.file.name, content:state.encoded, preview_token:state.previewToken})});
      state.jobToken = result.job_token; state.encoded = null; state.file = null; resetPreview(); $('admin-file').value = '';
      $('admin-processing-grid').hidden = false;
      $('admin-job-panel').hidden = false;
      $('admin-result-status').className = '';
      $('admin-result-status').textContent = t('Traitement en cours. Résultat en attente…', 'Processing. Outcome pending…');
      $('admin-job-status').textContent = t('Classeur transmis à GitHub. Suivi automatique du déploiement…', 'Workbook submitted to GitHub. Tracking deployment automatically…');
      schedulePolling();
    } catch (e) { error(e.message); }
    finally { busy(false); }
  });
  $('admin-refresh').addEventListener('click', refresh);
  async function init() {
    if (!configured) { $('admin-config-notice').hidden = false; sync(); return; }
    $('admin-config-notice').hidden = true;
    const hash = new URLSearchParams(window.location.hash.slice(1));
    const candidate = hash.get('session');
    if (candidate) { history.replaceState(null, '', window.location.pathname + window.location.search); state.session = candidate; }
    if (state.session) {
      try { const info = await request('/auth/session'); $('admin-user').textContent = t('Connexion : ', 'Account: ') + displayName(info.user.login); }
      catch (e) { state.session = null; error(e.message); }
    }
    sync();
  }
  init();
})();
