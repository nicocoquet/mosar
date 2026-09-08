from argparse import ArgumentParser
from pathlib import Path

from openpyxl import Workbook, load_workbook

SHEET = "recencement"
FORBIDDEN_COLUMNS = {
    "Contacts",
    "Divers",
    "Questionnaire envoyé le",
    "Réponse reçue le",
}


def normalize_header(value):
    return str(value).strip() if value is not None else ""


def get_headers(ws):
    return [normalize_header(cell.value) for cell in ws[1]]


def validate_sanitized(path: Path):
    wb = load_workbook(path, read_only=True, data_only=True)
    if wb.sheetnames != [SHEET]:
        raise SystemExit(
            f"Le fichier versionné doit contenir uniquement l’onglet '{SHEET}'. "
            f"Onglets trouvés : {', '.join(wb.sheetnames)}"
        )
    headers = set(get_headers(wb[SHEET]))
    remaining = sorted(FORBIDDEN_COLUMNS & headers)
    if remaining:
        raise SystemExit(
            "Colonnes interdites encore présentes : " + ", ".join(remaining)
        )
    print("Contrôle d’expurgation réussi.")


def sanitize(source: Path, output: Path):
    wb = load_workbook(source, read_only=True, data_only=False)
    if SHEET not in wb.sheetnames:
        raise SystemExit(f"Onglet attendu introuvable : {SHEET}")

    ws = wb[SHEET]
    headers = get_headers(ws)
    missing = sorted(FORBIDDEN_COLUMNS - set(headers))
    if missing:
        raise SystemExit(
            "Expurgation interrompue : colonnes attendues introuvables : "
            + ", ".join(missing)
        )

    keep_indexes = [
        index for index, header in enumerate(headers)
        if header not in FORBIDDEN_COLUMNS
    ]

    clean_wb = Workbook()
    clean_ws = clean_wb.active
    clean_ws.title = SHEET

    for row in ws.iter_rows(values_only=True):
        clean_ws.append([row[index] for index in keep_indexes])

    output.parent.mkdir(parents=True, exist_ok=True)
    clean_wb.save(output)
    validate_sanitized(output)
    print(f"Fichier expurgé créé : {output}")


def main():
    parser = ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/Recensement-revues-stat.xlsx"),
    )
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()

    if args.check:
        validate_sanitized(args.check)
        return
    if not args.source:
        parser.error("un fichier source est requis sauf avec --check")
    sanitize(args.source, args.output)


if __name__ == "__main__":
    main()
