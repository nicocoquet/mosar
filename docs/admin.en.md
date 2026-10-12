---
hide:
  - toc
---

# Updating Mosar data { .page-title-compact }

<div id="mosar-admin" class="mosar-admin" data-lang="en" data-api-url="https://mosar-auth.onrender.com" data-site-url="https://nicocoquet.github.io/mosar/">
  <div class="admin-notice" role="status" id="admin-config-notice">The interface will become available once the administration service is configured.</div>
  <div class="admin-top-grid">
  <section class="admin-panel admin-panel--identity" aria-labelledby="admin-login-title">
    <span class="admin-step">01 · Sign in</span>
    <h2 id="admin-login-title">Data access</h2>
    <div class="admin-session-card">
      <span class="admin-session-avatar" aria-hidden="true"><svg class="admin-github-icon" aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.56.1.76-.24.76-.54v-2.13c-3.1.68-3.76-1.32-3.76-1.32-.5-1.28-1.24-1.62-1.24-1.62-1.01-.7.08-.69.08-.69 1.12.08 1.71 1.15 1.71 1.15 1 .1.77 2.61 3.22 1.87.1-.72.4-1.21.72-1.49-2.47-.28-5.07-1.24-5.07-5.5 0-1.22.44-2.22 1.15-3-.11-.28-.5-1.42.11-2.95 0 0 .94-.3 3.05 1.14A10.5 10.5 0 0 1 12 6.05c.95 0 1.89.13 2.77.38 2.11-1.44 3.05-1.14 3.05-1.14.61 1.53.22 2.67.11 2.95.72.78 1.15 1.78 1.15 3 0 4.27-2.6 5.22-5.08 5.49.4.35.76 1.02.76 2.06v3.2c0 .3.2.65.77.54A11.1 11.1 0 0 0 12 .9Z"/></svg></span>
      <div class="admin-session-copy">
        <strong class="admin-session-label">Sign-in required</strong>
        <p id="admin-user" class="admin-muted" aria-live="polite"></p>
      </div>
      <div class="admin-session-actions">
        <button type="button" class="md-button md-button--primary admin-github-button" id="admin-login"><svg class="admin-github-icon" aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.56.1.76-.24.76-.54v-2.13c-3.1.68-3.76-1.32-3.76-1.32-.5-1.28-1.24-1.62-1.24-1.62-1.01-.7.08-.69.08-.69 1.12.08 1.71 1.15 1.71 1.15 1 .1.77 2.61 3.22 1.87.1-.72.4-1.21.72-1.49-2.47-.28-5.07-1.24-5.07-5.5 0-1.22.44-2.22 1.15-3-.11-.28-.5-1.42.11-2.95 0 0 .94-.3 3.05 1.14A10.5 10.5 0 0 1 12 6.05c.95 0 1.89.13 2.77.38 2.11-1.44 3.05-1.14 3.05-1.14.61 1.53.22 2.67.11 2.95.72.78 1.15 1.78 1.15 3 0 4.27-2.6 5.22-5.08 5.49.4.35.76 1.02.76 2.06v3.2c0 .3.2.65.77.54A11.1 11.1 0 0 0 12 .9Z"/></svg><span>Sign in with GitHub</span></button>
        <span class="admin-session-authorized"><span class="admin-session-indicator" aria-hidden="true"></span>Access granted</span>
        <button type="button" class="md-button admin-logout-button" id="admin-logout" hidden>Sign out</button>
      </div>
    </div>
  </section>
  <section class="admin-panel admin-panel--upload" aria-labelledby="admin-upload-title">
    <span class="admin-step">02 · File</span>
    <h2 id="admin-upload-title">Upload the XLSX file</h2>
    <div class="admin-dropzone" id="admin-dropzone" aria-disabled="true">
      <span class="admin-file-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2h8l5 5v15H6z"/><path d="M14 2v5h5"/><path d="m10 12-2 2 2 2m5-4 2 2-2 2"/></svg></span>
      <label for="admin-file" class="admin-file-select md-button">Select a file</label>
      <input type="file" id="admin-file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" disabled>
      <p class="admin-drop-help">or drag it here · 15 MB maximum</p>
      <p class="admin-selected-file" id="admin-selected-file" aria-live="polite"></p>
      <button type="button" class="md-button md-button--primary admin-send-button" id="admin-preview" disabled>Upload and prepare data</button>
      <p class="admin-drop-status" id="admin-drop-status" aria-live="polite">Sign in with GitHub to get started.</p>
    </div>
  </section>
  <section class="admin-panel admin-panel--report" id="admin-report-panel" aria-labelledby="admin-report-title" hidden>
    <span class="admin-step">03 · Pre-publication check</span>
    <h2 id="admin-report-title">Validation report</h2>
    <div id="admin-report" aria-live="polite"></div>
    <p class="admin-warning">Only the sanitized workbook will be saved to GitHub. Review the report before confirming.</p>
    <label class="admin-check"><input type="checkbox" id="admin-confirm"> I confirm publication of this sanitized workbook.</label>
    <div class="admin-actions"><button type="button" class="md-button md-button--primary" id="admin-publish" disabled>Confirm and publish</button><button type="button" class="md-button" id="admin-reset">Choose another file</button></div>
  </section>
  </div>
  <div class="admin-processing-grid" id="admin-processing-grid" hidden>
  <section class="admin-panel admin-panel--job" id="admin-job-panel" aria-labelledby="admin-job-title" hidden>
    <span class="admin-step">04 · Processing</span>
    <h2 id="admin-job-title">Publication status</h2>
    <p id="admin-job-status" role="status" aria-live="polite"></p>
    <p id="admin-job-links"></p>
    <button type="button" class="md-button" id="admin-refresh">Refresh status</button>
  </section>
  <section class="admin-panel admin-panel--result" id="admin-result-panel" aria-labelledby="admin-result-title">
    <span class="admin-step">05 · Result</span>
    <h2 id="admin-result-title">Publication outcome</h2>
    <p id="admin-result-status" role="status" aria-live="polite">Waiting for processing…</p>
  </section>
  </div>
  <p class="admin-error" id="admin-error" role="alert" hidden></p>
</div>
