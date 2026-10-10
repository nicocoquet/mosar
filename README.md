# Mosar
**Modèle ouvert de soutien et d’accompagnement des revues**

**Mosar** est un projet financé par le **Fonds national pour la science ouverte (FNSO)** pour la période **2026-2028**. Il prolonge l’expérience de la clinique éditoriale inaugurée par la **MSH Mondes** en novembre 2023 et vise à proposer aux revues du périmètre des universités **Paris 1 Panthéon-Sorbonne** et **Paris Nanterre** un accompagnement individualisé, notamment vers les standards de l’accès ouvert diamant.

Le projet est porté par la **MSH Mondes**, avec l’**EDCH (OPERAS)**, l’**université Paris Nanterre** et l’**université Paris 1 Panthéon-Sorbonne**.

Mosar poursuit trois objectifs complémentaires :

- **observer** le paysage éditorial du site à partir d’un recensement qualitatif et quantitatif ;
- **accompagner** les revues selon leurs besoins et leur degré de proximité avec les établissements partenaires ;
- **modéliser** l’offre de services et les outils produits afin de préparer leur réutilisation dans d’autres contextes institutionnels.

Ce dépôt contient le site web du projet, ses sources de données publiables et les traitements qui produisent les pages de données.

## Enjeux et choix d’architecture

Le dispositif technique a été conçu autour de quelques choix structurants.

**Conserver des sources de travail identifiables**
Le recensement des revues reste un tableur XLSX, format adapté au travail quotidien de collecte et d’enquête. Les données externes utilisées pour décrire les revues proviennent de Mir@bel. Les traitements ne masquent pas ces provenances : ils les contrôlent, les normalisent et les combinent pour la publication.

**Contribuer à un référentiel partagé plutôt que dupliquer les métadonnées descriptives**
Mosar participe à l'enrichissement de Mir@bel en y ajoutant des revues et en complétant ou corrigeant leurs métadonnées. Le projet réutilise ensuite ces informations par API pour alimenter ses propres outils. Ce circuit favorise la mutualisation, la qualité et la pérennité des données descriptives, tout en préservant l'autonomie du recensement analytique Mosar.

**Fonder les rapprochements sur des identifiants**
L’ID numérique Mir@bel constitue la clé de jointure entre le recensement Mosar et les métadonnées récupérées par API.

**Séparer données, règles métier et publication**
Les règles d’analyse et de normalisation sont portées par des scripts Python ; les contenus éditoriaux rédigés en Markdown sont séparés des fichiers générés ; MkDocs et Material for MkDocs interviennent dans la couche finale de publication.

**Produire un site statique**
Les transformations sont effectuées au moment du build. Le site publié ne nécessite ni serveur applicatif Mosar ni base de données pour être consulté.

**Rendre les traitements contrôlables et reproductibles**
Les transformations sont versionnées, les sorties intermédiaires peuvent être examinées, des fixtures déterministes testent les principaux contrats métier et la CI reconstruit le site avant publication.

**Préparer la réutilisation sans prétendre à une généricité achevée**
La configuration d’instance et les moteurs de traitement sont progressivement dissociés, mais certaines règles analytiques, catégories, textes et choix graphiques restent propres à Mosar. Le dépôt documente ce qui est effectivement réutilisable aujourd’hui.

## Architecture actuelle

```text

                  Travail documentaire Mosar
                            |
                Recensement et vérification
                       des revues
                            |
                 Ajouts et corrections
                            |
                            v
                      Référentiel
                        Mir@bel
                            |
                            v
                    Grappe n° 146
                            |
                            v
                       API Mir@bel
                            |
                            v
                   Acquisition Revues
                            |
                            |
Recensement Mosar (XLSX)    |
          |                 |
          |                 |
          +-----------------+ 
          |                 |
          v                 v
 Pipeline Statistiques   Jointure Revues
          |                 |
          v                 v
  Indicateurs et       Modèle normalisé
     graphiques              |
          |                  v
          |            JSON + rapport
          |                  |
          v                  v
     Pages Statistiques  Pages Revues
          |                  |
          +--------+---------+
                   |
                   v
        Contenus éditoriaux + CSS/JS
                   |
                   v
            MkDocs / Material
                   |
                   v
              GitHub Pages

Configuration commune : config/project.yml
```

La logique de données et les règles métier ne dépendent donc pas directement de MkDocs. Le générateur de site assemble des contenus déjà préparés et les composants de présentation.


## Sources de données

### Recensement Mosar

Le fichier `data/Recensement-revues-stat.xlsx` constitue la source analytique interne publiée avec le projet. Le traitement utilise l’onglet `recensement`.

Le tableur est conservé comme **format pivot collaboratif**. Avant publication, `scripts/sanitize_xlsx.py` vérifie que les colonnes définies comme privées ne sont pas présentes dans la version destinée au dépôt.

### Mir@bel

Le projet Mosar s'appuie sur [Mir@bel](https://reseau-mirabel.info/) comme référentiel partagé pour l'identification et la description des revues de son périmètre.

Cette articulation repose sur une démarche à double sens.

**Enrichissement du référentiel Mir@bel**

Le travail de recensement conduit dans le cadre de Mosar contribue à l'enrichissement de Mir@bel : ajout de revues absentes du référentiel, complétion ou correction de métadonnées descriptives, amélioration de la qualité des informations disponibles.

Ces contributions bénéficient ainsi au réseau Mir@bel et à ses autres utilisateurs, au-delà des seuls besoins du projet Mosar.

**Réutilisation des données Mir@bel**

En retour, Mosar récupère automatiquement, par l'API de Mir@bel, les métadonnées des revues appartenant à la **grappe n° 146 « Mosar »**, qui définit le périmètre de référence du projet.

Les données récupérées sont rapprochées de celles du recensement XLSX Mosar à partir de l'identifiant Mir@bel de chaque revue.

Les deux sources remplissent des fonctions complémentaires :

- **Mir@bel** fournit les métadonnées descriptives et référentielles des revues, enrichies notamment par les contributions de Mosar ;
- **Mosar** conserve dans son propre recensement les informations analytiques nécessaires à l'observation du paysage éditorial et à l'accompagnement des revues.

Ce fonctionnement permet de mutualiser les métadonnées descriptives dans un référentiel partagé, tout en conservant les données analytiques spécifiques au projet.

L'enrichissement de Mir@bel relève du travail documentaire réalisé dans le cadre de Mosar (pôle éditorial de la MSH Mondes). Le pipeline décrit dans ce dépôt intervient en aval : il récupère les données par API, les rapproche du recensement Mosar et prépare leur publication (pôle DHUNE de la MSH Mondes).

Les paramètres de connexion à l'API et l'identifiant de la grappe sont centralisés dans `config/project.yml`.


## Deux pipelines complémentaires

### Statistiques

Le pipeline Statistiques part du XLSX et produit les indicateurs, graphiques et pages française et anglaise.

Ses responsabilités sont réparties entre plusieurs modules :

```text
statistics_project.py
    adaptation de la configuration à la source statistique

statistics_data.py
    lecture, validation, normalisation et agrégation

mosar_model.py
    règles analytiques propres à Mosar

mosar_dashboard.py
    définition éditoriale du tableau de bord

statistics_build.py
    construction des pages statistiques

statistics_render.py
    rendu et exports des graphiques

statistics_publication.py
    destinations et paramètres de publication

generate_statistics.py
    orchestration de la génération
```

Les graphiques du tableau de bord disposent également d’exports CSV et XLSX (données), JPEG et SVG (graphiques). `prepare_reusable_charts.py` prépare les fragments graphiques réutilisés lors de la construction du site.

Les pages `docs/statistiques.md` et `docs/statistiques.en.md` sont des **sorties générées**. Les textes introductifs sont conservés hors de `docs/` :

```text
content/statistiques-intro.fr.md
content/statistiques-intro.en.md
```

### Revues

Le pipeline Revues combine Mir@bel et le recensement Mosar. Ses responsabilités sont volontairement séparées :

```text
journals_sources.py
    acquisition des données Mir@bel et Mosar

journals_model.py
    normalisation d'une revue

journals_pipeline.py
    jointure, dédoublonnage, tri et rapport

journals_publication.py
    production du JSON, du rapport et de la page

generate_journals_exploration.py
    orchestration
```

Le générateur produit actuellement :

```text
docs/assets/data/revues-exploration.json
data/revues/join-report.json
docs/revues.md
docs/revues.en.md
```

Le rapport de jointure permet de contrôler les identifiants communs aux deux sources, les revues présentes dans une seule source et les éventuels doublons de titres actifs renvoyés par Mir@bel.

L’interface de consultation est exécutée dans le navigateur. Elle repose principalement sur :

```text
docs/assets/javascripts/revues-exploration.js
docs/assets/javascripts/revues-config.js
docs/assets/stylesheets/revues-exploration.css
```

Elle fournit notamment recherche, facettes, filtres actifs, tri et cartes de revues. Les composants propres à cet explorateur utilisent le préfixe `.rx-` afin de limiter les collisions avec le thème du site.

Les introductions éditoriales française et anglaise sont conservées séparément des pages générées :

```text
content/revues-intro.fr.md
content/revues-intro.en.md
```

## Configuration et portabilité

`config/project.yml` centralise les principaux paramètres propres à l’instance Mosar :

- identité et URL du projet ;
- fichier XLSX et feuille de travail ;
- correspondance entre noms logiques et colonnes du tableur ;
- API et grappe Mir@bel ;
- chemins des contenus éditoriaux et des sorties ;
- configuration du fallback éventuel ;
- colonnes interdites dans le XLSX publiable.

`scripts/config.py` charge et valide ce contrat de configuration.

Cette organisation évite que les moteurs de données aient à connaître les chemins du dépôt ou les destinations MkDocs. Elle permet également de distinguer ce qui relève d’un **moteur réutilisable**, de la **configuration d’une instance** et des **règles scientifiques ou éditoriales propres à Mosar**.

## Contenus éditoriaux et contenus générés

La distinction entre les deux est importante pour la maintenance.

Les introductions des pages générées sont rédigées dans `content/`. Les pages, données et fragments produits par les scripts sont reconstruits lors du build et ne constituent pas la source éditoriale à modifier directement.

Exemples :

```text
content/
    revues-intro.fr.md
    revues-intro.en.md
    statistiques-intro.fr.md
    statistiques-intro.en.md

docs/
    statistiques.md          généré
    statistiques.en.md       généré
    revues.md                généré
    revues.en.md             généré

generated/charts/            généré
```

Lorsqu’une correction porte sur une donnée ou une règle, elle doit être effectuée dans la source, la configuration ou le module concerné, et non uniquement dans la sortie générée.

## Tests et reproductibilité

La reproductibilité ne repose pas uniquement sur la capacité à relancer les scripts sur les données de production.

Le moteur statistique dispose d’un corpus fictif autonome :

```text
tests/fixtures/minimal-corpus.xlsx
tests/check_fixture.py
```

Il permet de vérifier les principales dimensions analytiques sans dépendre du XLSX de production.

Le pipeline Revues dispose également d’une fixture déterministe :

```text
tests/check_journals_fixture.py
```

Elle teste en mémoire la jointure, le dédoublonnage, les normalisations, le tri et le rapport sans appel à l’API Mir@bel, sans XLSX de production et sans MkDocs.

Des contrôles complémentaires vérifient la non-régression statistique, la structure des données Revues, le comportement JavaScript de l’explorateur et les traductions de son interface (`tests/check_journals_translations.js`).

Cette séparation permet de distinguer les **tests métier déterministes** des **tests d’intégration utilisant les sources réelles**.

## Internationalisation

Le site utilise `mkdocs-static-i18n` et une convention par suffixe :

```text
page.md       français
page.en.md    anglais
```

Le français est la langue par défaut. Les pipelines Statistiques et Revues produisent chacun leurs pages française et anglaise. L’explorateur Revues dispose également d’une interface bilingue, notamment pour les douze facettes de filtrage. Une troisième langue pourra être ajoutée à l’avenir.

## Couche de publication

Le site est actuellement publié avec **MkDocs**, **Material for MkDocs** et **GitHub Pages**.

Le couplage au générateur de site est volontairement maintenu dans la couche de publication et dans les styles qui lui sont propres. Les moteurs de données, la jointure Mir@bel/Mosar et les règles analytiques ne doivent pas dépendre de la structure HTML du thème.

Ce choix est important pour la pérennité du projet : une évolution future de la couche de publication doit pouvoir être envisagée sans réécrire les traitements de données.

## Développement local

Les dépendances Python sont déclarées dans `requirements.txt`.

```bash
python -m pip install -r requirements.txt
```

Les principaux contrôles et générations peuvent être reproduits localement :

```bash
python scripts/sanitize_xlsx.py --check
python tests/check_fixture.py
python tests/check_journals_fixture.py

python scripts/generate_statistics.py
python scripts/check_regression.py
python scripts/prepare_reusable_charts.py

python scripts/generate_journals_exploration.py
python scripts/check_journals_output.py

node --check scripts/check_journals_js.js
node scripts/check_journals_js.js
node tests/check_journals_translations.js

mkdocs build --strict
```

La génération à partir des données réelles de Mir@bel nécessite un accès réseau. Le test `check_journals_fixture.py`, en revanche, est entièrement local.

Pour consulter le site localement après génération :

```bash
mkdocs serve
```

## Intégration continue et déploiement

Le workflow `.github/workflows/deploy.yml` contrôle et reconstruit le projet.

Il vérifie notamment :

1. le caractère publiable du XLSX ;
2. la fixture statistique ;
3. la fixture Revues ;
4. la génération et la non-régression statistiques ;
5. la génération Revues à partir des sources réelles ;
6. la structure des données produites, les interactions JavaScript et les traductions de l’explorateur ;
7. le build strict de MkDocs.

La publication sur GitHub Pages intervient après validation du build selon les conditions définies dans le workflow.

Les fichiers générés ne sont donc pas considérés comme une vérité autonome : ils doivent pouvoir être reconstruits depuis les sources versionnées et les sources externes prévues.

## Arborescence fonctionnelle

```text
.github/workflows/       intégration continue et déploiement
config/                  configuration de l'instance
content/                 fragments éditoriaux des pages générées
data/                    données sources publiables et rapports
docs/                    contenus et ressources du site
generated/               sorties intermédiaires du build
scripts/                 modèles, traitements, publication et contrôles
tests/                   fixtures et tests déterministes
mkdocs.yml               configuration du site
requirements.txt         dépendances Python
```

## À propos du développement du code

Les scripts de ce dépôt ont été **essentiellement développés par vibe coding**, dans le cadre d’un travail itératif associant définition des besoins, génération de code avec assistance d’IA, tests sur les données réelles, revue des résultats et refactorisations successives.

Cette origine est indiquée explicitement par souci de transparence. Elle ne dispense pas le code des exigences appliquées au projet : les règles métier doivent rester explicites, les responsabilités séparées, les transformations testables et les résultats reproductibles. Les fixtures, contrôles de non-régression et validations de CI ont précisément pour fonction de rendre ces exigences vérifiables indépendamment de la manière dont le code a été initialement produit.

## État actuel et limites

L’architecture est aujourd’hui suffisamment séparée pour distinguer :

```text
sources de données
        ↓
acquisition / lecture
        ↓
règles métier et normalisation
        ↓
traitements et agrégations
        ↓
publication
        ↓
MkDocs / interface web
```

Cette organisation constitue le socle actuel du projet. Elle ne signifie pas que le site Mosar et ses pipelines de traitements soient déjà génériques et prêts à être déployés tel quel dans n’importe quel contexte.

Restent notamment spécifiques à Mosar : les règles analytiques, certaines catégories statistiques, les textes éditoriaux et l’identité visuelle.

## Licence et réutilisation

Les conditions de licence du code, des contenus et des ressources graphiques doivent encore être précisées explicitement avant de présenter le dépôt comme un paquet réutilisable autonome. Les métadonnées provenant de services externes restent soumises aux conditions de leurs sources respectives.