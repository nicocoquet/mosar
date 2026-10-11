# Service d'administration Mosar

Backend FastAPI indépendant du service AdlFI. Aucun fichier source XLSX n'est écrit sur le disque ou dans GitHub.

## Configuration

Variables d'environnement (ne jamais versionner les valeurs secrètes) :

- `GITHUB_CLIENT_ID` : identifiant de l'application OAuth GitHub Mosar.
- `GITHUB_CLIENT_SECRET` : secret OAuth.
- `SESSION_SECRET` : chaîne aléatoire d'au moins 32 caractères.
- `GITHUB_REPOSITORY` : `nicocoquet/mosar` par défaut.
- `PAGES_URL` : `https://nicocoquet.github.io/mosar/` par défaut.
- `ALLOWED_USERS` : identifiants GitHub séparés par des virgules.

Callback OAuth : `https://<service-render>/auth/callback`.

## API

- `GET /health` : disponibilité.
- `GET /auth/github` et `GET /auth/callback` : OAuth.
- `GET /auth/session` : session.
- `POST /api/preview` : JSON `{ "filename": "recensement.xlsx", "content": "<base64>" }`, renvoie rapport et jeton de prévisualisation.
- `POST /api/publish` : même JSON avec `preview_token`, revalide puis publie uniquement le XLSX expurgé.
- `GET /api/jobs/{job_token}` : statut du workflow GitHub.

Les endpoints métier exigent `Authorization: Bearer <session>`.

## Développement local

À la racine du dépôt :

```sh
python -m pip install -r service/requirements.txt
python -m unittest discover -s tests -p 'test_service_api.py' -v
SESSION_SECRET="une-longue-cle-aleatoire-de-plus-de-32-caracteres" uvicorn service.main:app --reload
```

Ne pas créer de service Render ni activer l'OAuth avant validation des tests et de l'interface. Les sessions sont en mémoire et disparaissent au redémarrage (une reconnexion est alors nécessaire).
