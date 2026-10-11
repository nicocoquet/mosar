---
hide:
  - toc
---

# Mise à jour des données Mosar

Cette page permet aux personnes autorisées de mettre à jour le recensement des revues. Le classeur est contrôlé et expurgé **avant toute publication**.

<div id="mosar-admin" class="mosar-admin" data-lang="fr" data-api-url="" data-site-url="https://nicocoquet.github.io/mosar/">
  <div class="admin-notice" role="status" id="admin-config-notice">L'interface sera activée après la configuration du service d'administration.</div>
  <section class="admin-panel" aria-labelledby="admin-login-title">
    <span class="admin-step">01 · Connexion</span>
    <h2 id="admin-login-title">Accès réservé</h2>
    <p>Connectez-vous avec un compte GitHub autorisé pour déposer un nouveau classeur.</p>
    <div class="admin-actions"><button type="button" class="md-button md-button--primary" id="admin-login">Se connecter avec GitHub</button><button type="button" class="md-button" id="admin-logout" hidden>Se déconnecter</button></div>
    <p id="admin-user" class="admin-muted" aria-live="polite"></p>
  </section>
  <section class="admin-panel" aria-labelledby="admin-upload-title">
    <span class="admin-step">02 · Fichier</span>
    <h2 id="admin-upload-title">Déposer le recensement</h2>
    <p>Sélectionnez un fichier Excel (.xlsx), de 15 Mo maximum. Aucun fichier n'est publié à cette étape.</p>
    <label for="admin-file">Classeur XLSX</label>
    <input type="file" id="admin-file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" disabled>
    <div class="admin-actions"><button type="button" class="md-button md-button--primary" id="admin-preview" disabled>Contrôler le fichier</button></div>
  </section>
  <section class="admin-panel" id="admin-report-panel" aria-labelledby="admin-report-title" hidden>
    <span class="admin-step">03 · Vérification</span>
    <h2 id="admin-report-title">Rapport de contrôle</h2>
    <div id="admin-report" aria-live="polite"></div>
    <p class="admin-warning">Seul le classeur expurgé sera enregistré dans GitHub. Vérifiez le rapport avant de confirmer.</p>
    <label class="admin-check"><input type="checkbox" id="admin-confirm"> Je confirme la publication de ce classeur expurgé.</label>
    <div class="admin-actions"><button type="button" class="md-button md-button--primary" id="admin-publish" disabled>Confirmer et publier</button><button type="button" class="md-button" id="admin-reset">Choisir un autre fichier</button></div>
  </section>
  <section class="admin-panel" id="admin-job-panel" aria-labelledby="admin-job-title" hidden>
    <span class="admin-step">04 · Publication</span>
    <h2 id="admin-job-title">Suivi de la publication</h2>
    <p id="admin-job-status" role="status" aria-live="polite"></p>
    <p id="admin-job-links"></p>
    <button type="button" class="md-button" id="admin-refresh">Actualiser le statut</button>
  </section>
  <p class="admin-error" id="admin-error" role="alert" hidden></p>
</div>

