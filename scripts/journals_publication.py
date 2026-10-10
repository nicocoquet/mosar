"""Publication des données et de la page de l'explorateur des revues."""

from __future__ import annotations

import json

from config import load_config, project_path


CONFIG = load_config()
JOURNALS_PUBLICATION = CONFIG["publication"]["journals"]
JOURNALS_PAGES = JOURNALS_PUBLICATION["pages"]

DATA_FILE = project_path(JOURNALS_PUBLICATION["data_file"])
REPORT_FILE = project_path(JOURNALS_PUBLICATION["report_file"])

INTRO_FILES = {
    lang: project_path(page["intro"])
    for lang, page in JOURNALS_PAGES.items()
}

OUTPUTS = {
    lang: project_path(page["output"])
    for lang, page in JOURNALS_PAGES.items()
}


def load_intro(lang: str) -> str:
    """Charger l'introduction éditoriale d'une page Revues."""

    intro_file = INTRO_FILES[lang]

    if not intro_file.is_file():
        raise SystemExit(
            f"Introduction éditoriale de la page Revues introuvable : "
            f"{intro_file}"
        )

    return intro_file.read_text(encoding="utf-8").strip()


def write_data(
    records: list[dict],
    report: dict,
    *,
    proximity_levels,
) -> None:
    """Publier les données de l'explorateur et le rapport de jointure."""

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    DATA_FILE.write_text(
        json.dumps(
            {
                "meta": report,
                "model": {
                     "proximity_levels": list(proximity_levels),
                },
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    REPORT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

PAGE_LABELS = {
    "fr": {
        "title": "Revues",
        "cluster": "Grappe Mir@bel n°",
        "cluster_link": "Consulter la grappe sur Mir@bel",
        "updated": "Dernière actualisation",
        "loading": "Chargement des revues…",
    },
    "en": {
        "title": "Journals",
        "cluster": "Mir@bel cluster no.",
        "cluster_link": "View the cluster on Mir@bel",
        "updated": "Last updated",
        "loading": "Loading journals…",
    },
}

def write_page(
    report: dict,
    *,
    cluster_id: int,
    cluster_name: str,
    cluster_url: str,
    lang: str = "fr",
) -> None:
    """Publier la page Markdown de l'explorateur des revues."""

    intro = load_intro(lang)
    output = OUTPUTS[lang]
    refresh_date = report["generated_at"][:10]
    labels = PAGE_LABELS[lang]

    assets_prefix = "../assets/" if lang == "fr" else "../../assets/"
    # Les pages anglaises sont publiées un niveau plus bas par mkdocs-static-i18n.
    intro = intro.replace("../assets/", assets_prefix)

    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        f"""---
hide:
  - toc
---
# {labels["title"]} {{ .page-title-compact }}

<div class="revues-intro" markdown="1">

{intro}

</div>

<p class="revues-source">{labels["cluster"]} {cluster_id} « {cluster_name} ».</p>
<p class="revues-source-link"><a href="{cluster_url}" target="_blank" rel="noopener">{labels["cluster_link"]}</a></p>
<p class="revues-updated">{labels["updated"]} : <strong>{refresh_date}</strong> (API Mir@bel).</p>

<link rel="stylesheet" href="{assets_prefix}stylesheets/revues-exploration.css">

<div id="revues-explorer" class="revues-explorer" lang="{lang}" data-source="{assets_prefix}data/revues-exploration.json"><p class="explorer-loading">{labels["loading"]}</p></div>

<script src="{assets_prefix}javascripts/revues-config.js" defer></script>
<script src="{assets_prefix}javascripts/revues-exploration.js" defer></script>
""",
        encoding="utf-8",
    )