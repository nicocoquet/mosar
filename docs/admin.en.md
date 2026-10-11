---
hide:
  - toc
---

# Updating Mosar data

Authorized users can update the journal survey here. The workbook is checked and sanitized **before any publication**.

<div id="mosar-admin" class="mosar-admin" data-lang="en" data-api-url="https://mosar-auth.onrender.com" data-site-url="https://nicocoquet.github.io/mosar/">
  <div class="admin-notice" role="status" id="admin-config-notice">The interface will become available once the administration service is configured.</div>
  <section class="admin-panel" aria-labelledby="admin-login-title">
    <span class="admin-step">01 · Sign in</span>
    <h2 id="admin-login-title">Restricted access</h2>
    <p>Sign in with an authorized GitHub account to upload a new workbook.</p>
    <div class="admin-actions"><button type="button" class="md-button md-button--primary" id="admin-login">Sign in with GitHub</button><button type="button" class="md-button" id="admin-logout" hidden>Sign out</button></div>
    <p id="admin-user" class="admin-muted" aria-live="polite"></p>
  </section>
  <section class="admin-panel" aria-labelledby="admin-upload-title">
    <span class="admin-step">02 · File</span>
    <h2 id="admin-upload-title">Upload the survey</h2>
    <p>Select an Excel file (.xlsx), up to 15 MB. Nothing is published at this stage.</p>
    <label for="admin-file">XLSX workbook</label>
    <input type="file" id="admin-file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" disabled>
    <div class="admin-actions"><button type="button" class="md-button md-button--primary" id="admin-preview" disabled>Check file</button></div>
  </section>
  <section class="admin-panel" id="admin-report-panel" aria-labelledby="admin-report-title" hidden>
    <span class="admin-step">03 · Review</span>
    <h2 id="admin-report-title">Validation report</h2>
    <div id="admin-report" aria-live="polite"></div>
    <p class="admin-warning">Only the sanitized workbook will be saved to GitHub. Review the report before confirming.</p>
    <label class="admin-check"><input type="checkbox" id="admin-confirm"> I confirm publication of this sanitized workbook.</label>
    <div class="admin-actions"><button type="button" class="md-button md-button--primary" id="admin-publish" disabled>Confirm and publish</button><button type="button" class="md-button" id="admin-reset">Choose another file</button></div>
  </section>
  <section class="admin-panel" id="admin-job-panel" aria-labelledby="admin-job-title" hidden>
    <span class="admin-step">04 · Publication</span>
    <h2 id="admin-job-title">Publication status</h2>
    <p id="admin-job-status" role="status" aria-live="polite"></p>
    <p id="admin-job-links"></p>
    <button type="button" class="md-button" id="admin-refresh">Refresh status</button>
  </section>
  <p class="admin-error" id="admin-error" role="alert" hidden></p>
</div>

