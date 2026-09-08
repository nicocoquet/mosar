# mosar

Modèle ouvert de soutien et d’accompagnement des revues - FNSO.

## Principe

- `data/Recensement-revues-stat.xlsx` est la source de données.
- `scripts/generate_statistics.py` lit uniquement l’onglet `recencement` et régénère les pages **Statistiques** française et anglaise.
- `docs/index*.md` et `docs/a-propos*.md` sont des pages éditoriales : elles ne sont pas régénérées par le script statistique.
- GitHub Actions reconstruit puis publie le site MkDocs sur GitHub Pages.

## Développement local

```bash
python -m pip install -r requirements.txt
python scripts/generate_statistics.py
mkdocs serve
```
