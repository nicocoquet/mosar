"""Définition éditoriale du tableau de bord statistique Mosar.

Ce module décrit les textes, l'ordre et les catégories d'affichage des
graphiques. Il ne contient ni lecture de données ni code de rendu SVG/JPEG.
"""

TITLES = {
    "proximite-revues": {"fr": "Ventilation des revues du corpus selon le degré de proximité", "en": "Breakdown of corpus journals by degree of proximity"},
    "acces-ouvert-rattachement": {"fr": "Ouverture selon le degré de proximité", "en": "Open access by degree of proximity"},
    "format-publication": {"fr": "Ventilation des revues selon leur format de publication", "en": "Breakdown of journals by publication format"},
    "acces-format-publication": {"fr": "Ouverture selon le format de publication", "en": "Open access by publication format"},
    "annee-creation": {"fr": "Année/décennie de création des revues", "en": "Journal founding year/decade"},
    "acces-date-creation": {"fr": "Ouverture selon l’ancienneté des revues", "en": "Open access by journal age"},
    "periodicite-revues": {"fr": "Périodicité de publication", "en": "Publication frequency"},
    "disciplines-revues": {"fr": "Disciplines", "en": "Disciplines"},
    "structures-editoriales": {"fr": "Types de structure éditoriale", "en": "Types of editorial structure"},
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
