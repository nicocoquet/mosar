from argparse import ArgumentParser
from pathlib import Path

from openpyxl import Workbook, load_workbook

from config import load_config, project_path

CONFIG = load_config()
SHEET = CONFIG["data"]["sheet"]
FORBIDDEN_COLUMNS = set(CONFIG["privacy"]["forbidden_columns"])
ALLOWED_COLUMNS = set(CONFIG["privacy"]["allowed_columns"])
DEFAULT_OUTPUT = project_path(CONFIG["data"]["file"])

if not ALLOWED_COLUMNS:
    raise SystemExit("La liste des colonnes autorisées est vide.")

overlap = FORBIDDEN_COLUMNS & ALLOWED_COLUMNS
if overlap:
    raise SystemExit(
        "Colonnes à la fois autorisées et interdites : "
        + ", ".join(sorted(overlap))
    )

if "ID_Mosar" not in ALLOWED_COLUMNS:
    raise SystemExit("ID_Mosar doit figurer parmi les colonnes autorisées.")


def normalize_header(value):
    return str(value).strip() if value is not None else ""


def get_headers(ws):
    return [normalize_header(cell.value) for cell in ws[1]]


def require_id_column(headers):
    if "ID_Mosar" not in headers:
        raise SystemExit("Colonne obligatoire introuvable : ID_Mosar.")
    if headers.count("ID_Mosar") != 1:
        raise SystemExit("La colonne ID_Mosar apparaît plusieurs fois.")
    return headers.index("ID_Mosar")


def validate_sanitized(path: Path):
    try:
        wb = load_workbook(path, read_only=True, data_only=False)
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit(
            f"Impossible de lire le classeur : {error}"
        ) from error

    try:
        if wb.sheetnames != [SHEET]:
            raise SystemExit(
                f"Le fichier versionné doit contenir uniquement "
                f"l’onglet '{SHEET}'. "
                f"Onglets trouvés : {', '.join(wb.sheetnames)}"
            )

        ws = wb[SHEET]
        headers = get_headers(ws)

        if len(headers) != len(set(headers)):
            raise SystemExit(
                "Contrôle échoué : en-têtes de colonnes dupliqués."
            )

        remaining = sorted(FORBIDDEN_COLUMNS & set(headers))
        if remaining:
            raise SystemExit(
                "Colonnes interdites encore présentes : "
                + ", ".join(remaining)
            )

        unknown = sorted(set(headers) - ALLOWED_COLUMNS)
        if unknown:
            raise SystemExit(
                "Colonnes non autorisées : "
                + ", ".join(unknown)
            )

        id_column = require_id_column(headers)

        for row_number, row in enumerate(
            ws.iter_rows(min_row=2),
            start=2
        ):
            identifier = row[id_column].value

            if identifier is None or not str(identifier).strip():
                raise SystemExit(
                    f"Contrôle échoué : ID_Mosar vide "
                    f"à la ligne {row_number}."
                )

            for cell in row:
                if cell.data_type == "f":
                    raise SystemExit(
                        f"Formule Excel interdite : "
                        f"{SHEET}!{cell.coordinate}"
                    )

    finally:
        wb.close()

    print("Contrôle d’expurgation réussi.")


def sanitize(source: Path, output: Path):
    if source.resolve() == output.resolve():
        raise SystemExit("Le fichier source et le fichier de sortie doivent être différents.")
    try:
        wb = load_workbook(source, read_only=True, data_only=False)
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit(f"Impossible de lire le classeur source : {error}") from error
    try:
        if SHEET not in wb.sheetnames:
            raise SystemExit(f"Onglet attendu introuvable : {SHEET}")
        ws = wb[SHEET]
        headers = get_headers(ws)
        if len(headers) != len(set(headers)):
            raise SystemExit("En-têtes de colonnes dupliqués dans le classeur source.")
        id_column = require_id_column(headers)
        removed_columns = sorted(FORBIDDEN_COLUMNS & set(headers))
        unknown_columns = sorted(set(headers) - ALLOWED_COLUMNS - FORBIDDEN_COLUMNS)
        keep_indexes = [i for i, header in enumerate(headers) if header in ALLOWED_COLUMNS]
        removed_sheets = [name for name in wb.sheetnames if name != SHEET]

        clean_wb = Workbook()
        clean_ws = clean_wb.active
        clean_ws.title = SHEET
        excluded_rows = 0
        retained_rows = 0
        for row_number, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if row_number > 1:
                identifier = row[id_column]
                if identifier is None or not str(identifier).strip():
                    excluded_rows += 1
                    continue
                retained_rows += 1
            values = []
            for index in keep_indexes:
                value = row[index]
                if row_number > 1 and isinstance(value, str) and value.startswith("="):
                    raise SystemExit(
                        f"Formule Excel interdite : {SHEET}, ligne {row_number}, "
                        f"colonne '{headers[index]}'."
                    )
                values.append(value)
            clean_ws.append(values)
    finally:
        wb.close()

    # Valider le résultat en mémoire avant de remplacer le fichier de destination.
    if clean_ws.max_row < 2:
        raise SystemExit("Aucune revue avec ID_Mosar : fichier de sortie non créé.")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp.xlsx")
    try:
        clean_wb.save(temporary)
        validate_sanitized(temporary)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
        clean_wb.close()

    print(f"Onglets exclus ({len(removed_sheets)}) : {', '.join(removed_sheets) or 'aucun'}")
    print(f"Colonnes confidentielles supprimées ({len(removed_columns)}) : {', '.join(removed_columns) or 'aucune'}")
    print(f"Colonnes non autorisées supprimées ({len(unknown_columns)}) : {', '.join(unknown_columns) or 'aucune'}")
    print(f"Lignes sans ID_Mosar exclues : {excluded_rows}")
    print(f"Lignes de données conservées : {retained_rows}")
    print(f"Fichier expurgé créé : {output}")


def main():
    parser = ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", nargs="?", type=Path, const=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.check:
        validate_sanitized(args.check)
        return
    if not args.source:
        parser.error("un fichier source est requis sauf avec --check")
    sanitize(args.source, args.output)


if __name__ == "__main__":
    main()
