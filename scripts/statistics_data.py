from collections import Counter, defaultdict
from pathlib import Path
import math
import re

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "Recensement-revues-stat.xlsx"
SHEET = "recencement"
OUTPUTS = {"fr": ROOT / "docs/statistiques.md", "en": ROOT / "docs/statistiques.en.md"}
DOWNLOADS = ROOT / "docs/downloads"

INTRO = {
    "fr": "Cette page réunit les principaux indicateurs produits à partir du recensement des revues du projet Mosar. Les graphiques permettent d’explorer la composition du corpus, les caractéristiques éditoriales des revues et leurs modalités de diffusion.",
    "en": "This page brings together the main indicators produced from the Mosar journal survey. The charts explore the composition of the corpus, the journals’ editorial characteristics and their dissemination models.",
}

TITLES = {
    "proximite-revues": {"fr": "Répartition des revues selon le degré de proximité avec les universités Paris Nanterre, Paris 1 et la MSH Mondes", "en": "Distribution of journals by degree of proximity to Paris Nanterre University, Paris 1 University and MSH Mondes"},
    "acces-ouvert-rattachement": {"fr": "Pourcentage de revues en accès ouvert selon le degré de rattachement", "en": "Percentage of open-access journals by degree of affiliation"},
    "format-publication": {"fr": "Répartition des revues selon leur format de publication", "en": "Distribution of journals by publication format"},
    "acces-format-publication": {"fr": "Nombre de revues diffusées en accès ouvert ou restreint selon leur format de publication", "en": "Number of open- or restricted-access journals by publication format"},
    "annee-creation": {"fr": "Répartition des revues selon leur année de création", "en": "Distribution of journals by year of creation"},
    "periode-creation": {"fr": "Répartition des revues selon leur période de création", "en": "Distribution of journals by period of creation"},
    "acces-date-creation": {"fr": "Nombre de revues en accès ouvert ou restreint selon la date de création", "en": "Number of open- or restricted-access journals by date of creation"},
    "periodicite-revues": {"fr": "Périodicité des revues du périmètre", "en": "Publication frequency of journals in the corpus"},
    "disciplines-revues": {"fr": "Répartition des revues du périmètre selon la discipline", "en": "Distribution of journals in the corpus by discipline"},
    "structures-editoriales": {"fr": "Types de structures éditoriales des revues du périmètre", "en": "Types of editorial structures of journals in the corpus"},
    "acces-structure-editoriale": {"fr": "Pourcentage de revues en accès ouvert ou restreint selon le type de structure éditoriale", "en": "Percentage of open- or restricted-access journals by editorial structure type"},
    "droits-reutilisation": {"fr": "Type de droits de réutilisation", "en": "Reuse rights"},
}

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


def norm(v):
    return "" if v is None else re.sub(r"\s+", " ", str(v).strip())


def rpct(v, total):
    return math.floor(v * 100 / total + 0.5) if total else 0


def read_rows():
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    if SHEET not in wb.sheetnames:
        raise SystemExit(f"Onglet attendu introuvable : {SHEET}")
    ws = wb[SHEET]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    required = ["Nom revue", "Niveau rattachement", "Accès ouvert", "Format", "Année de création", "Nombre de n°s par an", "Discipline", "Type d'éditeur", "Licence"]
    missing = [x for x in required if x not in headers]
    if missing:
        raise SystemExit("Colonnes manquantes : " + ", ".join(missing))
    rows = []
    for row_number, values in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        row = dict(zip(headers, values))
        if norm(row["Nom revue"]):
            row["_row"] = row_number
            rows.append(row)
    return rows


def access(v, row_number):
    x = norm(v).casefold()
    if x == "oui":
        return "open"
    if x == "non":
        return "restricted"
    raise SystemExit(f"Accès ouvert invalide ligne {row_number}: {v!r}")


def year(v, row_number):
    try:
        y = int(float(v))
    except (TypeError, ValueError):
        raise SystemExit(f"Année de création invalide ligne {row_number}: {v!r}")
    if not 1500 <= y <= 2100:
        raise SystemExit(f"Année de création hors plage ligne {row_number}: {y}")
    return y


def creation_period(y):
    if y < 1800:
        return f"{(y // 100) + 1}e siècle"
    if y <= 1899: return "XIXe siècle"
    if y <= 1924: return "1900–1924"
    if y <= 1949: return "1925–1949"
    if y <= 1959: return "Années 1950"
    if y <= 1969: return "Années 1960"
    if y <= 1979: return "Années 1970"
    if y <= 1989: return "Années 1980"
    if y <= 1999: return "Années 1990"
    if y <= 2009: return "Années 2000"
    if y <= 2019: return "Années 2010"
    return "Années 2020"


def periodicity(v, row_number):
    x = norm(v).casefold()
    if x == "irrégulier": return "Parution irrégulière"
    if x == "parution continue": return "Parution continue"
    try:
        n = float(x.replace(",", "."))
    except ValueError:
        raise SystemExit(f"Périodicité invalide ligne {row_number}: {v!r}")
    known = {0.5: "Un numéro tous les deux ans", 1: "Annuel (1 nᵒ/an)", 2: "Semestriel (2 nᵒˢ/an)", 3: "Quadrimestriel (3 nᵒˢ/an)", 4: "Trimestriel (4 nᵒˢ/an)"}
    if n in known:
        return known[n]
    if n > 4:
        return "Plus de 4 nᵒˢ/an"
    raise SystemExit(f"Périodicité invalide ligne {row_number}: {v!r}")


def derive(rows):
    total = len(rows)
    levels, formats, years, periods = Counter(), Counter(), Counter(), Counter()
    periodicities, disciplines, structures, rights = Counter(), Counter(), Counter(), Counter()
    level_access, format_access, date_access, structure_access = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    format_map = {"numérique": "Numérique", "papier": "Papier", "papier+numérique": "Papier et numérique"}
    allowed_structures = {"Éditeur privé", "Organisme de recherche public", "Éditeur public", "Association", "Coédition public/privé", "Coédition privé/Association"}

    for row in rows:
        rn = row["_row"]
        a = access(row["Accès ouvert"], rn)
        try:
            level = int(row["Niveau rattachement"])
        except (TypeError, ValueError):
            raise SystemExit(f"Niveau de rattachement invalide ligne {rn}")
        if level not in (1, 2, 3, 4):
            raise SystemExit(f"Niveau de rattachement invalide ligne {rn}: {level}")
        levels[level] += 1
        level_access[level][a] += 1

        f = norm(row["Format"])
        if f not in format_map:
            raise SystemExit(f"Format inattendu ligne {rn}: {f!r}")
        f = format_map[f]
        formats[f] += 1
        format_access[f][a] += 1

        y = year(row["Année de création"], rn)
        years[y] += 1
        periods[creation_period(y)] += 1
        date_group = "Avant 1960" if y <= 1959 else ("1960–1999" if y <= 1999 else "À partir de 2000")
        date_access[date_group][a] += 1

        periodicities[periodicity(row["Nombre de n°s par an"], rn)] += 1

        discipline = norm(row["Discipline"])
        if discipline not in DISCIPLINE_MAP:
            raise SystemExit(f"Discipline non référencée ligne {rn}: {discipline!r}")
        disciplines[DISCIPLINE_MAP[discipline]] += 1

        structure = norm(row["Type d'éditeur"])
        if structure not in allowed_structures:
            raise SystemExit(f"Type d'éditeur inattendu ligne {rn}: {structure!r}")
        structures["Coédition privé/association" if structure == "Coédition privé/Association" else structure] += 1
        grouped_structure = "Coédition éditeur privé & structure publique ou associative" if structure.startswith("Coédition") else ("Organisme public de recherche" if structure == "Organisme de recherche public" else structure)
        structure_access[grouped_structure][a] += 1

        licence = norm(row["Licence"])
        if licence not in LICENCE_MAP:
            raise SystemExit(f"Licence non référencée ligne {rn}: {licence!r}")
        rights[LICENCE_MAP[licence]] += 1

    for name, counter in [("niveaux", levels), ("formats", formats), ("années", years), ("périodicités", periodicities), ("disciplines", disciplines), ("structures", structures), ("droits", rights)]:
        if sum(counter.values()) != total:
            raise SystemExit(f"Contrôle de total échoué pour {name}: {sum(counter.values())}/{total}")

    return {
        "total": total, "levels": levels, "level_access": level_access, "formats": formats, "format_access": format_access,
        "years": years, "periods": periods, "date_access": date_access, "periodicities": periodicities,
        "disciplines": disciplines, "structures": structures, "struct_access": structure_access, "rights": rights,
    }
