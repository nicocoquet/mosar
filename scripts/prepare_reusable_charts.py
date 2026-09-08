from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FRAGMENTS = ROOT / "generated" / "charts"

# Registre minimal des graphiques réutilisables.
# L'identifiant stable sert aux fragments, aux exports et aux futures insertions
# dans des bilans ou d'autres pages éditoriales.
CHARTS = {
    "proximite-revues": {
        "title": {
            "fr": "Répartition des revues selon le degré de proximité avec les universités Paris Nanterre, Paris 1 et la MSH Mondes",
            "en": "Distribution of journals by degree of proximity to Paris Nanterre University, Paris 1 University and MSH Mondes",
        },
        "source": "recencement:Niveau rattachement",
        "type": "pie",
        "pages": {
            "fr": DOCS / "statistiques.md",
            "en": DOCS / "statistiques.en.md",
        },
        "fragments": {
            "fr": FRAGMENTS / "proximite-revues.fr.md",
            "en": FRAGMENTS / "proximite-revues.en.md",
        },
    }
}

START = "## "
END_MARKERS = ("## Graphique 2", "## Chart 2")


def extract_first_chart(page_text: str) -> tuple[str, str, str]:
    start = page_text.index(START, page_text.index("statistics-intro"))
    end = min(
        page_text.index(marker, start)
        for marker in END_MARKERS
        if marker in page_text[start:]
    )
    before = page_text[:start].rstrip()
    chart = page_text[start:end].strip()
    after = page_text[end:].lstrip()
    return before, chart, after


def snippet_path(chart_id: str, lang: str) -> str:
    return f'--8<-- "generated/charts/{chart_id}.{lang}.md"'


def main():
    FRAGMENTS.mkdir(parents=True, exist_ok=True)

    for chart_id, chart in CHARTS.items():
        for lang, page_path in chart["pages"].items():
            text = page_path.read_text(encoding="utf-8")
            before, fragment, after = extract_first_chart(text)
            chart["fragments"][lang].write_text(fragment + "\n", encoding="utf-8")
            page_path.write_text(
                f"{before}\n\n{snippet_path(chart_id, lang)}\n\n{after}",
                encoding="utf-8",
            )

    print("Composants graphiques générés : " + ", ".join(CHARTS))


if __name__ == "__main__":
    main()
