from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FRAGMENTS = ROOT / "generated" / "charts"
CHART_IDS = [
    "proximite-revues",
    "acces-ouvert-rattachement",
    "format-publication",
    "acces-format-publication",
    "annee-creation",
    "periode-creation",
    "acces-date-creation",
    "periodicite-revues",
    "disciplines-revues",
    "structures-editoriales",
    "acces-structure-editoriale",
    "droits-reutilisation",
]
PAGES = {"fr": DOCS / "statistiques.md", "en": DOCS / "statistiques.en.md"}


def snippet(chart_id, lang):
    return f'--8<-- "generated/charts/{chart_id}.{lang}.md"'


def main():
    FRAGMENTS.mkdir(parents=True, exist_ok=True)
    for lang, page in PAGES.items():
        text = page.read_text(encoding="utf-8")
        for chart_id in CHART_IDS:
            pattern = re.compile(
                rf"<!-- CHART:{re.escape(chart_id)}:START -->\n(.*?)\n<!-- CHART:{re.escape(chart_id)}:END -->",
                re.S,
            )
            match = pattern.search(text)
            if not match:
                raise SystemExit(f"Bloc graphique introuvable : {chart_id} ({lang})")
            fragment = match.group(1).strip() + "\n"
            (FRAGMENTS / f"{chart_id}.{lang}.md").write_text(fragment, encoding="utf-8")
            text = text[: match.start()] + snippet(chart_id, lang) + text[match.end() :]
        page.write_text(text, encoding="utf-8")
    print("Composants graphiques générés : " + ", ".join(CHART_IDS))


if __name__ == "__main__":
    main()
