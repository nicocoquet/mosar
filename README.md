# Mosar

**Modèle ouvert de soutien et d’accompagnement des revues**

Mosar est un projet financé par le **Fonds national pour la science ouverte (FNSO)** pour la période **2026-2028**. Il prolonge l’expérience de la clinique éditoriale inaugurée par la **MSH Mondes** en novembre 2023 pour proposer aux revues du périmètre des universités **Paris 1 Panthéon-Sorbonne** et **Paris Nanterre** un accompagnement individualisé pour les revues, notamment vers les standards de l’accès ouvert diamant.
Ce projet porté par la MSH Mondes,  co-corté par OPERAS, l'université Paris Nanterre et l'université Paris 1 Panthéon-Sorbonne.

Le projet poursuit trois objectifs complémentaires :

- **observer** le paysage éditorial du site à partir d’une enquête qualitative et quantitative ;
- **accompagner** les revues selon leurs besoins et leur degré de proximité avec les établissements partenaires ;
- **modéliser** l’offre de services et les outils produits afin de préparer leur réutilisation dans d’autres contextes institutionnels.

Ce dépôt contient le site web du projet et les traitements qui permettent de produire ses pages de données à partir du recensement Mosar et de sources externes.

> **État de la documentation.** Ce README décrit l’architecture effectivement utilisée par Mosar à ce jour. La transformation de cette architecture en dispositif générique et configurable, réutilisable par d’autres organismes, constitue une étape ultérieure du projet et sera documentée lorsqu’elle sera opérationnelle.

## Architecture générale

Le site est statique. Les données sont transformées lors de la construction du site ; aucun serveur applicatif ni base de données ne sont nécessaires pour sa consultation.

```text
Recensement Mosar (XLSX) ───────┬──> scripts statistiques ──> pages et graphiques
                                │
                                └──> jointure par ID Mir@bel ───────┐
                                                                    │
API Mir@bel ──> métadonnées des revues ────────────────────────────┤
                                                                    v
                                                          JSON normalisé
                                                                    │
                                                                    v
                                                     explorateur Revues (JS)

Markdown éditorial + données générées + CSS/JS
                         │
                         v
                  MkDocs / Material
                         │
                         v
                    GitHub Pages
```

La logique métier est volontairement placée principalement dans les scripts Python et dans des données intermédiaires explicites. MkDocs assemble ensuite les contenus et les composants du site.

## Sources de données

### Recensement Mosar

Le fichier [`data/Recensement-revues-stat.xlsx`](data/Recensement-revues-stat.xlsx) constitue actuellement la source analytique interne du projet. Le traitement principal utilise l’onglet `recencement`.

Il contient notamment les informations propres à l’analyse Mosar : niveau de rattachement ou de proximité, accès ouvert, format de publication, année de création, périodicité, discipline, type de structure éditoriale et licence.

Le tableur reste un format de travail collaboratif : les scripts contrôlent et transforment ses données pour la publication, sans en faire un format de diffusion web.

### Mir@bel

La page **Revues** combine le recensement Mosar avec des métadonnées récupérées depuis l’API de [Mir@bel](https://reseau-mirabel.info/).

À l’état actuel du projet, le générateur interroge encore la **grappe Mir@bel n° 15 « PCP Sciences de l’Antiquité et Archéologie »**, utilisée pendant le développement du prototype. La grappe propre au projet Mosar, **n° 146**, a été créée mais n’est pas encore utilisée par le pipeline de production tant que ses métadonnées ne sont pas accessibles dans les conditions attendues via l’API.

L’**ID numérique Mir@bel de la revue** sert de clé de jointure entre les données récupérées par API et le recensement Mosar. Cette clé évite une jointure fragile sur les titres de revues.

## Pipeline Statistiques

La production des statistiques est répartie entre plusieurs scripts afin de séparer lecture des données, normalisation, construction des pages et préparation des composants réutilisables.

### `scripts/statistics_data.py`

Ce module :

- lit `data/Recensement-revues-stat.xlsx` avec `openpyxl` ;
- vérifie la présence des colonnes attendues ;
- normalise plusieurs catégories utilisées dans les analyses ;
- calcule les données nécessaires aux graphiques et indicateurs ;
- définit les sorties française et anglaise.

Les règles de regroupement utilisées pour les disciplines, licences et autres catégories analytiques sont donc explicites et versionnées avec le code.

### `scripts/generate_statistics.py`

Ce script construit les pages :

- `docs/statistiques.md` ;
- `docs/statistiques.en.md`.

Les pages sont régénérées à partir du XLSX : elles ne doivent donc pas être considérées comme des contenus éditoriaux indépendants de leur source.

### `scripts/prepare_reusable_charts.py`

Après génération des pages statistiques, ce script extrait les graphiques identifiés dans des fragments Markdown placés dans `generated/charts/`. Les pages utilisent ensuite ces fragments au moyen de `pymdownx.snippets`.

Cette organisation permet de conserver des graphiques identifiés et réutilisables sans dupliquer leur balisage.

## Pipeline Revues

La page **Revues** est produite par `scripts/generate_revues_exploration.py`.

Le script :

1. interroge l’API Mir@bel pour les titres actifs de la grappe configurée ;
2. récupère les métadonnées utiles à l’explorateur ;
3. lit le recensement Mosar et indexe les lignes possédant un `ID Mir@bel` ;
4. joint les deux sources sur cet identifiant ;
5. normalise les données au niveau de la revue ;
6. produit un JSON destiné à l’interface ;
7. produit un rapport de jointure ;
8. génère `docs/revues.md`.

Les principales sorties sont :

```text
docs/assets/data/revues-exploration.json   données consommées par l'interface
data/revues/join-report.json               contrôle de la jointure
docs/revues.md                             page MkDocs générée
```

Le rapport permet notamment de repérer les identifiants présents dans une seule des deux sources et les éventuels doublons de titres actifs renvoyés par Mir@bel.

### Interface de consultation

L’interactivité est réalisée côté navigateur par :

```text
docs/assets/javascripts/revues-exploration.js
docs/assets/stylesheets/revues-exploration.css
```

Le JavaScript assure notamment :

- la recherche libre ;
- les facettes ;
- l’affichage des filtres sélectionnés ;
- le tri des revues par niveau de proximité puis par ordre alphabétique ;
- la construction des cartes de revues ;
- le recours à une image générique lorsqu’aucune illustration spécifique n’est disponible.

Les images spécifiques sont nommées à partir de l’ID Mir@bel de la revue et placées dans :

```text
docs/assets/images/revues/
```

L’interface peut également afficher les liens vers Mir@bel, le **Diamond Discovery Hub (DDH)** et le site de la revue, ainsi que les informations de labellisation et de diffusion disponibles.

## Contenus éditoriaux et contenus générés

Une distinction importante doit être conservée entre les fichiers rédigés directement et ceux reconstruits par les scripts.

**Contenus éditoriaux**, par exemple :

```text
docs/index.md
docs/index.en.md
docs/partenaires.md
docs/partenaires.en.md
```

**Contenus générés**, notamment :

```text
docs/statistiques.md
docs/statistiques.en.md
docs/revues.md
docs/assets/data/revues-exploration.json
generated/charts/
```

Lorsqu’une correction concerne une donnée ou une règle de génération, il faut intervenir sur la source ou sur le script correspondant plutôt que modifier uniquement le fichier généré.

## Styles et interface

Les styles sont répartis selon leur responsabilité :

```text
docs/stylesheets/extra.css                 identité globale et composants transversaux
docs/stylesheets/header.css                adaptations spécifiques à Material for MkDocs
docs/stylesheets/home.css                  page d'accueil
docs/assets/stylesheets/revues-exploration.css
                                           explorateur de revues
```

Les composants propres à l’explorateur utilisent le préfixe `.rx-` afin de limiter les collisions avec le thème et de faciliter leur identification.

`header.css` concentre volontairement la majeure partie du couplage à la structure HTML de **Material for MkDocs**. Cette séparation doit faciliter l’identification des adaptations nécessaires lors d’une future évolution ou migration du générateur de site.

## Internationalisation

Le site utilise `mkdocs-static-i18n` avec une structure par suffixe :

```text
page.md       français
page.en.md    anglais
```

Le français est la langue par défaut. Toutes les pages générées ne disposent pas encore nécessairement du même niveau de traduction ; il faut donc distinguer l’infrastructure bilingue de la couverture éditoriale effective.

## Développement local

Le projet nécessite Python. Les dépendances sont déclarées dans `requirements.txt` :

- Material for MkDocs ;
- `mkdocs-static-i18n` ;
- `openpyxl` ;
- `matplotlib`.

Installation :

```bash
python -m pip install -r requirements.txt
```

Pour reproduire localement les principales étapes du build :

```bash
python scripts/sanitize_xlsx.py --check data/Recensement-revues-stat.xlsx
python scripts/generate_statistics.py
python scripts/prepare_reusable_charts.py
python scripts/generate_revues_exploration.py
mkdocs build --strict
```

Pour travailler avec le serveur local MkDocs :

```bash
mkdocs serve
```

Le générateur de la page Revues interroge l’API Mir@bel : cette étape nécessite donc un accès réseau.

## Déploiement

Le workflow `.github/workflows/deploy.yml` s’exécute sur les `push` et les pull requests visant `main`, ainsi que manuellement.

Il :

1. installe Python 3.12 et les dépendances ;
2. vérifie que le XLSX peut être publié dans le dépôt dans son état prévu ;
3. régénère les statistiques ;
4. prépare les fragments graphiques ;
5. régénère la page Revues depuis les sources ;
6. exécute `mkdocs build --strict` ;
7. publie sur GitHub Pages lors des exécutions qui ne proviennent pas d’une pull request.

Le build strict constitue un contrôle important : une référence invalide ou une erreur détectée par MkDocs bloque la publication plutôt que de produire silencieusement un site incohérent.

## Arborescence fonctionnelle

```text
.github/workflows/     automatisation du build et du déploiement
data/                  données sources et rapports de contrôle
docs/                  contenus publiés par MkDocs
docs/assets/           données web, images, pictogrammes, JavaScript et CSS spécifiques
 docs/stylesheets/      styles globaux du site
generated/charts/      fragments statistiques produits lors du build
scripts/                traitements Python
mkdocs.yml              configuration du site
requirements.txt        dépendances Python
```

## Principes techniques

L’architecture actuelle suit plusieurs principes qui orientent le développement du projet :

- **sources explicites** : le XLSX Mosar et les données Mir@bel restent identifiables comme sources des informations publiées ;
- **jointures sur identifiants** : l’ID Mir@bel est préféré à une correspondance textuelle sur les titres ;
- **traitements versionnés** : les normalisations et transformations sont exprimées dans le code ;
- **sorties contrôlables** : JSON intermédiaire et rapport de jointure permettent d’examiner ce qui est produit ;
- **site statique** : l’interface publiée ne dépend pas d’un backend Mosar ;
- **séparation des responsabilités** : données, traitements, contenu éditorial, présentation et déploiement sont distingués autant que possible ;
- **maintenabilité** : le CSS spécifique à Material est isolé du CSS des composants métier ;
- **reproductibilité comme objectif** : le projet doit pouvoir servir de base à des dispositifs analogues, sans prétendre que l’architecture actuelle est déjà entièrement générique.

## Reproductibilité : état actuel et perspective

Mosar porte dès l’origine une ambition de réutilisation au-delà du périmètre de la MSH Mondes. Le dépôt constitue déjà une base documentée et versionnée, mais plusieurs paramètres propres à l’instance Mosar sont encore codés directement dans les scripts ou les contenus : identifiant de grappe Mir@bel, chemins, critères analytiques, textes et identité visuelle.

La prochaine étape architecturale consistera donc à distinguer plus nettement :

```text
code générique
configuration d'une instance
sources de données
contenus éditoriaux
présentation graphique
```

Cette évolution fera l’objet d’un chantier et d’une documentation propres. Le présent README doit rester la description fidèle de l’état opérationnel du projet, et non anticiper une généricité qui n’est pas encore implémentée.

## Licence et réutilisation

Les conditions de licence du code, des contenus et des ressources graphiques doivent être précisées explicitement avant de considérer le dépôt comme un paquet réutilisable autonome. Les métadonnées provenant de services externes restent soumises aux conditions de leurs sources respectives.
