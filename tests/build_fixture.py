from pathlib import Path

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "fixtures" / "corpus-minimal.xlsx"

HEADERS = [
    "Identifiant",
    "Nom revue",
    "Université (ou institution)",
    "Niveau rattachement",
    "Fiche mirabel",
    "ID Mir@bel",
    "Discipline",
    "Discipline TCD",
    "Année de création",
    "Année de création (par décennie)",
    "Période de création",
    "Nombre de n°s par an",
    "Format",
    "Éditeur",
    "Type d'éditeur",
    "Diffuseur numérique",
    "Diffuseur numérique pr TCD",
    "Type de diffuseur numérique",
    "DOI",
    "Accès ouvert",
    "Modalités",
    "Licence",
    "Licence pour TCD",
    "Personnel à disposition",
    "Source de financement",
    "Relance faite le",
]

ROWS = [
    ["FIX-001", "Revue fixture 01", "Institution fictive A", 1, None, None, "Histoire", None, 1750, None, None, 0.5, "numérique", "Éditeur fictif A", "Éditeur public", None, None, None, None, "oui", None, "CC BY 4.0", None, None, None, None],
    ["FIX-002", "Revue fixture 02", "Institution fictive A", 1, None, None, "Archéologie", None, 1850, None, None, 1, "papier", "Éditeur fictif B", "Association", None, None, None, None, "non", None, "Tous droits réservés", None, None, None, None],
    ["FIX-003", "Revue fixture 03", "Institution fictive A", 1, None, None, "Économie", None, 1910, None, None, 2, "papier+numérique", "Éditeur fictif C", "Éditeur privé", None, None, None, None, "oui", None, "CC BY-NC-ND 4.0", None, None, None, None],
    ["FIX-004", "Revue fixture 04", "Institution fictive B", 2, None, None, "Droit", None, 1935, None, None, 3, "numérique", "Éditeur fictif D", "Organisme de recherche public", None, None, None, None, "non", None, "Tous droits réservés", None, None, None, None],
    ["FIX-005", "Revue fixture 05", "Institution fictive B", 2, None, None, "Science politique", None, 1955, None, None, 4, "papier", "Éditeur fictif E", "Coédition public/privé", None, None, None, None, "oui", None, "CC BY-SA 4.0", None, None, None, None],
    ["FIX-006", "Revue fixture 06", "Institution fictive B", 2, None, None, "Sociologie", None, 1965, None, None, 6, "papier+numérique", "Éditeur fictif F", "Coédition privé/Association", None, None, None, None, "non", None, "Tous droits réservés", None, None, None, None],
    ["FIX-007", "Revue fixture 07", "Institution fictive C", 3, None, None, "Anthropologie", None, 1975, None, None, "irrégulier", "numérique", "Éditeur fictif G", "Éditeur public", None, None, None, None, "oui", None, "CC BY", None, None, None, None],
    ["FIX-008", "Revue fixture 08", "Institution fictive C", 3, None, None, "Littérature", None, 1985, None, None, "parution continue", "papier", "Éditeur fictif H", "Association", None, None, None, None, "non", None, "Tous droits réservés", None, None, None, None],
    ["FIX-009", "Revue fixture 09", "Institution fictive C", 3, None, None, "Sciences économiques", None, 1995, None, None, 1, "papier+numérique", "Éditeur fictif I", "Éditeur privé", None, None, None, None, "oui", None, "CC BY NC", None, None, None, None],
    ["FIX-010", "Revue fixture 10", "Institution fictive D", 4, None, None, "Information-communication", None, 2005, None, None, 2, "numérique", "Éditeur fictif J", "Organisme de recherche public", None, None, None, None, "non", None, "tous droits réservés, avec possibilité de CC", None, None, None, None],
    ["FIX-011", "Revue fixture 11", "Institution fictive D", 4, None, None, "Histoire et archéologie", None, 2015, None, None, None, "papier+numérique", "Éditeur fictif K", "Coédition public/privé", None, None, None, None, "oui", None, None, None, None, None, None],
    ["FIX-012", "Revue fixture 12", "Institution fictive D", 4, None, None, "Mathématiques", None, None, None, None, 4, "papier+numérique", "Éditeur fictif L", "Coédition privé/Association", None, None, None, None, "non", None, "Tous droits réservés", None, None, None, None],
]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "recensement"

    ws.append(HEADERS)
    for row in ROWS:
        ws.append(row)

    wb.save(OUTPUT)

    print(f"Fixture créé : {OUTPUT.relative_to(ROOT)}")
    print(f"Revues : {len(ROWS)}")
    print(f"Colonnes : {len(HEADERS)}")


if __name__ == "__main__":
    main()
