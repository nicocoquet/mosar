# Données source

Le dépôt ne doit contenir que le classeur expurgé `Recensement-revues-stat.xlsx`.

Le fichier versionné doit contenir uniquement l’onglet `recensement` et ne doit jamais contenir les colonnes suivantes :

- `Contacts`
- `Divers`
- `Questionnaire envoyé le`
- `Réponse reçue le`
- `Relance faite le`

Ne jamais déposer le classeur de travail original dans GitHub, même temporairement : les données supprimées resteraient dans l’historique Git.

Pour produire la version publiable :

```bash
python scripts/sanitize_xlsx.py /chemin/vers/le/classeur-source.xlsx
```

Pour vérifier le classeur publiable sans le modifier, exécuter :

```bash
python scripts/sanitize_xlsx.py --check
```

La liste des colonnes interdites et le nom de l’onglet attendu sont définis dans `config/project.yml`. Le contrôle est également exécuté automatiquement par GitHub Actions avant la génération du site.

Le script crée `data/Recensement-revues-stat.xlsx`, puis le workflow contrôle à nouveau l’absence des colonnes interdites avant de générer les statistiques.