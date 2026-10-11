# Installation du lot Admin Mosar

Copier `docs/` et `tests/` à la racine du dépôt Mosar, puis ajouter à `mkdocs.yml` :

Dans `nav` (après Contacts) :

    - Admin: admin.md

Dans `plugins.i18n.languages[0].nav_translations` :

    Admin: Admin

Dans `extra_javascript` :

    - javascripts/admin.js

Dans `extra_css` :

    - stylesheets/admin.css

Ne pas renseigner `data-api-url` tant que Render et l'OAuth GitHub ne sont pas configurés et testés.

Contrôles :

    python tests/check_admin_static.py
    node --check docs/javascripts/admin.js
    mkdocs build --strict
    git status --short

Pour tester en local : `mkdocs serve`.

IMPORTANT : ce lot ajoute une interface statique inactive par défaut. La connexion ne sera activée qu'après configuration du service HTTPS et des autorisations GitHub. Ne pas considérer la visibilité de la page comme un mécanisme de contrôle d'accès.
