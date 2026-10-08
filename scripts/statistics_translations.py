"""Traductions des catégories publiées par le tableau de bord Mosar.

Les clés restent les libellés français normalisés du modèle statistique.
Une catégorie inconnue provoque une erreur plutôt qu'une traduction silencieuse.
"""

from mosar_dashboard import (
    DATE_ACCESS_CATEGORIES,
    FORMAT_CATEGORIES,
    PERIODICITY_CATEGORIES,
    PERIOD_ORDER,
    RIGHTS_CATEGORIES,
    STRUCTURE_ACCESS_ORDER,
)
from mosar_model import DISCIPLINE_MAP

CATEGORY_EN = {
    # Formats
    "Numérique": "Digital",
    "Papier": "Print",
    "Papier et numérique": "Print and digital",
    # Périodes de création
    "XIXe siècle": "19th century",
    "1900–1924": "1900–1924",
    "1925–1949": "1925–1949",
    "Années 1950": "1950s",
    "Années 1960": "1960s",
    "Années 1970": "1970s",
    "Années 1980": "1980s",
    "Années 1990": "1990s",
    "Années 2000": "2000s",
    "Années 2010": "2010s",
    "Années 2020": "2020s",
    "Avant 1960": "Before 1960",
    "1960–1999": "1960–1999",
    "À partir de 2000": "2000 onwards",
    # Périodicités
    "Un numéro tous les deux ans": "One issue every two years",
    "Annuel (1 nᵒ/an)": "Annual (1 issue/year)",
    "Semestriel (2 nᵒˢ/an)": "Semiannual (2 issues/year)",
    "Quadrimestriel (3 nᵒˢ/an)": "Three issues per year",
    "Trimestriel (4 nᵒˢ/an)": "Quarterly (4 issues/year)",
    "Plus de 4 nᵒˢ/an": "More than 4 issues/year",
    "Parution irrégulière": "Irregular publication",
    "Parution continue": "Continuous publication",
    # Disciplines normalisées
    "Histoire": "History",
    "Pluridisciplinaire": "Multidisciplinary",
    "Archéologie": "Archaeology",
    "Droit": "Law",
    "Sciences politiques": "Political science",
    "Économie, gestion, finance, marketing": "Economics, management, finance and marketing",
    "Littérature": "Literature",
    "Philosophie": "Philosophy",
    "Géographie": "Geography",
    "Études des aires culturelles": "Area studies",
    "Anthropologie": "Anthropology",
    "Sociologie": "Sociology",
    "Arts": "Arts",
    "Psychologie": "Psychology",
    "Information-communication": "Information and communication studies",
    "STM (sciences, technologie, médecine)": "Science, technology and medicine (STM)",
    "Linguistique": "Linguistics",
    # Structures : catégories brutes et regroupées
    "Éditeur privé": "Private publisher",
    "Éditeur public": "Public publisher",
    "Organisme de recherche public": "Public research organisation",
    "Organisme public de recherche": "Public research organisation",
    "Association": "Association",
    "Coédition public/privé": "Public–private co-publishing",
    "Coédition privé/Association": "Private publisher–association co-publishing",
    "Coédition privé/association": "Private publisher–association co-publishing",
    "Coédition éditeur privé & structure publique ou associative": "Private publisher and public or non-profit organisation co-publishing",
    # Droits
    "Licence Creative Commons": "Creative Commons licence",
    "Tous droits réservés": "All rights reserved",
    "Licence CC ou DR variable pour une même publication": "Creative Commons licence or all rights reserved, varying within the same publication",
}

HEADERS_EN = {
    "Niveau": "Level",
    "Nombre": "Count",
    "Pourcentage": "Percentage",
    "Accès ouvert": "Open access",
    "Accès restreint": "Restricted access",
    "Format": "Format",
    "Année": "Year",
    "Période": "Period",
    "Périodicité": "Publication frequency",
    "Discipline": "Discipline",
    "Structure": "Editorial structure",
    "Droits": "Reuse rights",
}


def translate_category(value, lang):
    if lang == "fr":
        return value
    if lang != "en":
        raise ValueError(f"Langue non prise en charge : {lang}")
    try:
        return CATEGORY_EN[value]
    except KeyError as exc:
        raise ValueError(f"Catégorie statistique sans traduction anglaise : {value!r}") from exc


def translate_categories(values, lang):
    return [translate_category(value, lang) for value in values]


def translate_headers(headers, lang):
    if lang == "fr":
        return list(headers)
    if lang != "en":
        raise ValueError(f"Langue non prise en charge : {lang}")
    missing = set(headers) - HEADERS_EN.keys()
    if missing:
        raise ValueError(f"En-têtes CSV sans traduction anglaise : {sorted(missing)!r}")
    return [HEADERS_EN[header] for header in headers]


def check_reference_categories():
    """Vérifie la couverture des catégories définies par les référentiels."""
    reference = (
        set(FORMAT_CATEGORIES)
        | set(PERIOD_ORDER)
        | set(DATE_ACCESS_CATEGORIES)
        | set(PERIODICITY_CATEGORIES)
        | set(STRUCTURE_ACCESS_ORDER)
        | set(RIGHTS_CATEGORIES)
        | set(DISCIPLINE_MAP.values())
    )
    missing = reference - CATEGORY_EN.keys()
    if missing:
        raise ValueError(f"Catégories sans traduction : {sorted(missing)!r}")
    return len(reference)
