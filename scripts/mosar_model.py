"""Règles analytiques propres à l'instance Mosar.

Ce module décrit le modèle d'analyse du corpus. Il est volontairement séparé
du moteur de lecture, de contrôle et d'agrégation de statistics_data.py.
Modifier ces règles peut modifier les résultats statistiques publiés.
"""

PROX_DEFS = {
    "fr": {
        1: "revues publiées par la MSH Mondes, les Presses universitaires de Nanterre et les Éditions de la Sorbonne",
        2: "revues portées ou hébergées par un laboratoire des universités Paris 1 ou Paris Nanterre",
        3: "revues dont le.a rédacteur.rice en chef est membre des universités Paris 1 ou Paris Nanterre, qui comprennent au moins un.e membre du comité de rédaction restreint (≤ 8) de Paris 1 ou Paris Nanterre ou si la revue est soutenue financièrement par une UR",
        4: "revues dont au moins un.e membre appartient à l’université Paris 1 ou Paris Nanterre (comité de rédaction ou comité scientifique)",
    },
    "en": {
        1: "journals published by MSH Mondes, Presses universitaires de Nanterre or Éditions de la Sorbonne",
        2: "journals hosted or supported by a research unit affiliated with Paris 1 or Paris Nanterre University",
        3: "journals whose editor-in-chief is affiliated with Paris 1 or Paris Nanterre University, with at least one Paris 1 or Paris Nanterre member on a small editorial board (≤ 8), or with financial support from a research unit",
        4: "journals with at least one member affiliated with Paris 1 or Paris Nanterre University on the editorial or scientific board",
    },
}

PROXIMITY_LEVELS = tuple(PROX_DEFS["fr"])


def proximity_sort_key(record):
    """Trie les revues selon le niveau de proximité Mosar puis le titre."""
    raw = ((record.get("mosar") or {}).get("proximity_level") or "").strip()
    try:
        level = int(raw)
        if level not in PROXIMITY_LEVELS:
            level = 99
    except (TypeError, ValueError):
        level = 99
    return level, record["title"].casefold()

DISCIPLINE_MAP = {
    "Histoire": "Histoire", "Pluridisciplinaire": "Pluridisciplinaire", "Archéologie": "Archéologie", "Droit": "Droit", "Science politique": "Sciences politiques",
    "Économie": "Économie, gestion, finance, marketing", "Littérature": "Littérature", "Philosophie": "Philosophie", "Géographie": "Géographie", "Études des aires culturelles": "Études des aires culturelles",
    "Anthropologie": "Anthropologie", "Sociologie": "Sociologie", "Économie, gestion": "Économie, gestion, finance, marketing", "Arts": "Arts", "Psychologie": "Psychologie",
    "Sciences de l'éducation": "Pluridisciplinaire", "Information-communication": "Information-communication", "Histoire et archéologie": "Archéologie", "Sciences économiques": "Économie, gestion, finance, marketing",
    "Ingénierie": "STM (sciences, technologie, médecine)", "Muséologie": "Arts", "Arts visuels": "Arts", "Gestion": "Économie, gestion, finance, marketing", "Psychiatrie": "STM (sciences, technologie, médecine)",
    "Linguistique": "Linguistique", "Arts vivants": "Arts", "Ergonomie": "STM (sciences, technologie, médecine)", "Histoire, Architecture": "Histoire", "Travail social": "Sociologie",
    "Littérature, Arts visuels": "Littérature", "Neurosciences": "STM (sciences, technologie, médecine)", "Etude des aires culturelles": "Études des aires culturelles", "Psychiatrie, éducation": "STM (sciences, technologie, médecine)",
    "Anthropologie et histoire du droit": "Droit", "Histoire des sciences": "Histoire", "Finance": "Économie, gestion, finance, marketing", "Communication": "Information-communication",
    "Langues et cultures étrangères": "Études des aires culturelles", "Relations internationales": "Histoire", "Marketing": "Économie, gestion, finance, marketing", "Linguistique, Neurosciences": "STM (sciences, technologie, médecine)",
    "Architecture": "Pluridisciplinaire", "Logistique": "Économie, gestion, finance, marketing", "Mécanique": "STM (sciences, technologie, médecine)", "Droit (histoire et anthropologie)": "Droit",
    "Mathématiques": "STM (sciences, technologie, médecine)", "Informatique": "STM (sciences, technologie, médecine)", "Histoire de l'art": "Arts", "Étude de genre": "Sociologie",
    "Histoire et sociologie des sciences": "Pluridisciplinaire", "Ethnologie": "Anthropologie",
}

LICENCE_MAP = {
    "Tous droits réservés": "Tous droits réservés", "tous droits réservés": "Tous droits réservés", "CC BY": "Licence Creative Commons", "CC BY NC ND": "Licence Creative Commons",
    "CC BY NC ND 4.0": "Licence Creative Commons", "CC BY-NC-ND 4.0": "Licence Creative Commons", "CC BY SA 4.0": "Licence Creative Commons", "Pas de mention, tous droits réservés": "Tous droits réservés",
    "CC BY NC": "Licence Creative Commons", "CC BY NC SA 4.0": "Licence Creative Commons", "CC BY 4.0": "Licence Creative Commons", "tous droits réservés, avec possibilité de CC": "Licence CC ou DR variable pour une même publication",
    "CC BY-SA 4.0": "Licence Creative Commons", "Tous droits réservés, CC-BY": "Licence CC ou DR variable pour une même publication", "CC BY SA": "Licence Creative Commons",
    "tous droits réservés (18 mois), puis CC BY-NC-ND 4.0": "Licence CC ou DR variable pour une même publication", "CC BY-NC-SA": "Licence Creative Commons", "pas d'indication, tous droits réservés": "Tous droits réservés",
    "CC BY-NC-ND": "Licence Creative Commons", "tous droits réservés et CC variable selon les articles": "Licence CC ou DR variable pour une même publication", "CC BY-SA": "Licence Creative Commons",
    "Pas mentionné": "Tous droits réservés", "non": "Tous droits réservés", "CC BY-NC-SA 4.0": "Licence Creative Commons", "Licence OpenEdition Books": "Licence Creative Commons",
    "Tous droits réservés, aucune mention": "Tous droits réservés", "CC-BY-NC-ND": "Licence Creative Commons", "CC BY NC ND 4.0 ou tous droits réservés": "Licence CC ou DR variable pour une même publication",
    "CC-BY-NC-ND 4.0": "Licence Creative Commons", "Tous droits réservés (sur Cairn) et CC BY NC ND sur OpenEdition": "Licence CC ou DR variable pour une même publication", "CC BY 3.0": "Licence Creative Commons",
}

FORMAT_MAP = {
    "numérique": "Numérique",
    "papier": "Papier",
    "papier+numérique": "Papier et numérique",
}

ALLOWED_STRUCTURES = {
    "Éditeur privé",
    "Organisme de recherche public",
    "Éditeur public",
    "Association",
    "Coédition public/privé",
    "Coédition privé/Association",
}

DATE_ACCESS_GROUPS = (
    ("Avant 1960", None, 1959),
    ("1960–1999", 1960, 1999),
    ("À partir de 2000", 2000, None),
)

PERIODICITY_LABELS = {
    0.5: "Un numéro tous les deux ans",
    1: "Annuel (1 nᵒ/an)",
    2: "Semestriel (2 nᵒˢ/an)",
    3: "Quadrimestriel (3 nᵒˢ/an)",
    4: "Trimestriel (4 nᵒˢ/an)",
}


PERIODICITY_SPECIAL_LABELS = {
    "irrégulier": "Parution irrégulière",
    "parution continue": "Parution continue",
}
PERIODICITY_ABOVE_FOUR_LABEL = "Plus de 4 nᵒˢ/an"


def creation_period(year):
    """Classe une année de création selon les périodes analytiques Mosar."""
    if year < 1800:
        return f"{(year // 100) + 1}e siècle"
    if year <= 1899:
        return "XIXe siècle"
    if year <= 1924:
        return "1900–1924"
    if year <= 1949:
        return "1925–1949"
    if year <= 1959:
        return "Années 1950"
    if year <= 1969:
        return "Années 1960"
    if year <= 1979:
        return "Années 1970"
    if year <= 1989:
        return "Années 1980"
    if year <= 1999:
        return "Années 1990"
    if year <= 2009:
        return "Années 2000"
    if year <= 2019:
        return "Années 2010"
    return "Années 2020"


def date_access_group(year):
    """Classe une année dans les groupes utilisés pour l'analyse de l'accès."""
    return next(
        label
        for label, minimum, maximum in DATE_ACCESS_GROUPS
        if (minimum is None or year >= minimum)
        and (maximum is None or year <= maximum)
    )


def normalize_structure(structure):
    """Normalise le libellé de structure pour la distribution éditoriale."""
    if structure == "Coédition privé/Association":
        return "Coédition privé/association"
    return structure


def group_structure_for_access(structure):
    """Regroupe les structures selon le modèle Mosar d'analyse de l'accès."""
    if structure.startswith("Coédition"):
        return "Coédition éditeur privé & structure publique ou associative"
    if structure == "Organisme de recherche public":
        return "Organisme public de recherche"
    return structure


def periodicity_label(value):
    """Retourne la catégorie Mosar d'une périodicité déjà normalisée."""
    if value in PERIODICITY_SPECIAL_LABELS:
        return PERIODICITY_SPECIAL_LABELS[value]
    number = float(value.replace(",", "."))
    if number in PERIODICITY_LABELS:
        return PERIODICITY_LABELS[number]
    if number > 4:
        return PERIODICITY_ABOVE_FOUR_LABEL
    raise ValueError(value)
