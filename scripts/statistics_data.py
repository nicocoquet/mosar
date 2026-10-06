from collections import Counter, defaultdict
from pathlib import Path
import math
import re

from openpyxl import load_workbook

from config import load_config, project_path
from mosar_model import (
    ALLOWED_STRUCTURES,
    DATE_ACCESS_GROUPS,
    DISCIPLINE_MAP,
    FORMAT_MAP,
    LICENCE_MAP,
    PERIODICITY_LABELS,
    PROXIMITY_LEVELS,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config()
COLUMNS = CONFIG["columns"]
XLSX = project_path(CONFIG["data"]["file"])
SHEET = CONFIG["data"]["sheet"]
OUTPUTS = {"fr": ROOT / "docs/statistiques.md", "en": ROOT / "docs/statistiques.en.md"}
DOWNLOADS = ROOT / "docs/downloads"

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
    required = [
        COLUMNS["journal_name"], COLUMNS["proximity"], COLUMNS["open_access"],
        COLUMNS["format"], COLUMNS["creation_year"], COLUMNS["periodicity"],
        COLUMNS["discipline"], COLUMNS["publisher_type"], COLUMNS["licence"],
    ]
    missing = [x for x in required if x not in headers]
    if missing:
        raise SystemExit("Colonnes manquantes : " + ", ".join(missing))
    rows = []
    for row_number, values in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        row = dict(zip(headers, values))
        if norm(row[COLUMNS["journal_name"]]):
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
    if n in PERIODICITY_LABELS:
        return PERIODICITY_LABELS[n]
    if n > 4:
        return "Plus de 4 nᵒˢ/an"
    raise SystemExit(f"Périodicité invalide ligne {row_number}: {v!r}")


def derive(rows):
    total = len(rows)
    levels, formats, years, periods = Counter(), Counter(), Counter(), Counter()
    periodicities, disciplines, structures, rights = Counter(), Counter(), Counter(), Counter()
    level_access, format_access, date_access, structure_access = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for row in rows:
        rn = row["_row"]
        a = access(row[COLUMNS["open_access"]], rn)
        try:
            level = int(row[COLUMNS["proximity"]])
        except (TypeError, ValueError):
            raise SystemExit(f"Niveau de rattachement invalide ligne {rn}")
        if level not in PROXIMITY_LEVELS:
            raise SystemExit(f"Niveau de rattachement invalide ligne {rn}: {level}")
        levels[level] += 1
        level_access[level][a] += 1

        f = norm(row[COLUMNS["format"]])
        if f not in FORMAT_MAP:
            raise SystemExit(f"Format inattendu ligne {rn}: {f!r}")
        f = FORMAT_MAP[f]
        formats[f] += 1
        format_access[f][a] += 1

        y = year(row[COLUMNS["creation_year"]], rn)
        years[y] += 1
        periods[creation_period(y)] += 1
        date_group = next(
            label
            for label, minimum, maximum in DATE_ACCESS_GROUPS
            if (minimum is None or y >= minimum) and (maximum is None or y <= maximum)
        )
        date_access[date_group][a] += 1

        periodicities[periodicity(row[COLUMNS["periodicity"]], rn)] += 1

        discipline = norm(row[COLUMNS["discipline"]])
        if discipline not in DISCIPLINE_MAP:
            raise SystemExit(f"Discipline non référencée ligne {rn}: {discipline!r}")
        disciplines[DISCIPLINE_MAP[discipline]] += 1

        structure = norm(row[COLUMNS["publisher_type"]])
        if structure not in ALLOWED_STRUCTURES:
            raise SystemExit(f"Type d'éditeur inattendu ligne {rn}: {structure!r}")
        structures["Coédition privé/association" if structure == "Coédition privé/Association" else structure] += 1
        grouped_structure = "Coédition éditeur privé & structure publique ou associative" if structure.startswith("Coédition") else ("Organisme public de recherche" if structure == "Organisme de recherche public" else structure)
        structure_access[grouped_structure][a] += 1

        licence = norm(row[COLUMNS["licence"]])
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
