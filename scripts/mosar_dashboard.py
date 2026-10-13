"""Définition éditoriale du tableau de bord statistique Mosar.

Ce module décrit les textes, l'ordre et les catégories d'affichage des
graphiques. Il ne contient ni lecture de données ni code de rendu SVG/JPEG.
"""

TITLES = {
    "proximite-revues": {"fr": "Ventilation des revues selon le degré de proximité", "en": "Breakdown of journals by degree of proximity"},
    "acces-ouvert-rattachement": {"fr": "Ouverture selon le degré de proximité", "en": "Open access by degree of proximity"},
    "format-publication": {"fr": "Ventilation des revues selon leur format de publication", "en": "Breakdown of journals by publication format"},
    "acces-format-publication": {"fr": "Ouverture selon le format de publication", "en": "Open access by publication format"},
    "annee-creation": {"fr": "Répartition des revues selon leur année de création", "en": "Distribution of journals by year of creation"},
    "periode-creation": {"fr": "Répartition des revues selon leur période de création", "en": "Distribution of journals by period of creation"},
    "acces-date-creation": {"fr": "Nombre de revues en accès ouvert ou restreint selon la date de création", "en": "Number of open- or restricted-access journals by date of creation"},
    "periodicite-revues": {"fr": "Périodicité de publication", "en": "Publication frequency"},
    "disciplines-revues": {"fr": "Répartition des revues du périmètre selon la discipline", "en": "Distribution of journals in the corpus by discipline"},
    "structures-editoriales": {"fr": "Types de structures éditoriales des revues du périmètre", "en": "Types of editorial structures of journals in the corpus"},
    "acces-structure-editoriale": {"fr": "Ouverture selon le type de structure éditoriale", "en": "Open access by editorial structure type"},
    "droits-reutilisation": {"fr": "Droits de réutilisation", "en": "Reuse rights"},
}

CHART_ORDER = tuple(TITLES)

FORMAT_CATEGORIES = ("Numérique", "Papier", "Papier et numérique")

PERIOD_ORDER = (
    "XIXe siècle", "1900–1924", "1925–1949", "Années 1950",
    "Années 1960", "Années 1970", "Années 1980", "Années 1990",
    "Années 2000", "Années 2010", "Années 2020",
)

DATE_ACCESS_CATEGORIES = ("Avant 1960", "1960–1999", "À partir de 2000")

PERIODICITY_CATEGORIES = (
    "Un numéro tous les deux ans",
    "Annuel (1 nᵒ/an)",
    "Semestriel (2 nᵒˢ/an)",
    "Quadrimestriel (3 nᵒˢ/an)",
    "Trimestriel (4 nᵒˢ/an)",
    "Plus de 4 nᵒˢ/an",
    "Parution irrégulière",
    "Parution continue",
)

STRUCTURE_ACCESS_ORDER = (
    "Éditeur privé",
    "Éditeur public",
    "Organisme public de recherche",
    "Association",
    "Coédition éditeur privé & structure publique ou associative",
)

RIGHTS_CATEGORIES = (
    "Licence Creative Commons",
    "Tous droits réservés",
    "Licence CC ou DR variable pour une même publication",
)

PAGE_TITLES = {"fr": "Statistiques", "en": "Statistics"}
