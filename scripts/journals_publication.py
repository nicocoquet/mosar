"""Publication des données et de la page de l'explorateur des revues."""

from __future__ import annotations

import json
import re

import markdown

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
        "cluster_link": "Consulter la grappe « {name} »",
        "updated": "Dernière actualisation",
        "loading": "Chargement des revues…",
    },
    "en": {
        "title": "Journals",
        "cluster_link": "View the “{name}” cluster",
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
    cluster_link_label = labels["cluster_link"].format(name=cluster_name)

    assets_prefix = "../assets/" if lang == "fr" else "../../assets/"
    # Les pages anglaises sont publiées un niveau plus bas par mkdocs-static-i18n.
    intro = intro.replace("../assets/", assets_prefix)
    # Séparer les paragraphes de présentation des définitions des niveaux.
    # Les deux parties restent issues des introductions éditoriales FR/EN.
    heading = re.search(r"(?im)^#{2,4}\s+[^\n]*(?:proximité|proximity)[^\n]*$", intro)
    if heading is None:
        raise SystemExit(f"Titre des niveaux de proximité introuvable dans l'introduction {lang}.")
    intro_overview = intro[:heading.start()].strip()
    intro_levels = intro[heading.start():].strip()
    # Convertir avant insertion dans des blocs HTML imbriqués : MkDocs ne
    # traite pas systématiquement le Markdown à cet emplacement.
    overview_html = markdown.markdown(intro_overview, extensions=["extra"])
    levels_html = markdown.markdown(intro_levels, extensions=["extra"])
    colon_space = " " if lang == "fr" else ""
    # Reprendre le badge des fiches de revues sans modifier les sources Markdown.
    # La substitution est limitée aux libellés de niveau en début de définition.
    levels_html = re.sub(
        r"<strong>\s*((?:Niveau|Level)\s+[1-4])\s*[—–-]\s*(.*?)\s*:\s*</strong>",
        lambda match: (
            f'<span class="revues-level-badge">{match.group(1)}</span> '
            f'<strong class="revues-level-title">{match.group(2)}{colon_space}:</strong>'
        ),
        levels_html,
    )
    # Chaque définition occupe sa propre colonne : les retours à la ligne
    # commencent sous l'intitulé, jamais sous le badge de niveau.
    levels_html = re.sub(
        r'(<li>)(<span class="revues-level-badge">.*?</span>)\s*(.*?)(</li>)',
        lambda match: (
            f'{match.group(1)}{match.group(2)}'
            f'<div class="revues-level-description">{match.group(3)}</div>'
            f'{match.group(4)}'
        ),
        levels_html,
        flags=re.DOTALL,
    )

    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        f"""---
hide:
  - toc
---
# {labels["title"]} {{ .page-title-compact }}

<div class="revues-header">
  <div class="revues-intro">
{overview_html}
  </div>
  <aside class="revues-provenance">
    <a class="revues-source-link" href="{cluster_url}" target="_blank" rel="noopener noreferrer">
      <span>{cluster_link_label}</span>
      <img src="{assets_prefix}logos/logo_mirabel.png" alt="Mir@bel">
    </a>
    <p class="revues-updated"><span class="revues-updated-label">{labels["updated"]}{colon_space}:</span><span class="revues-updated-value"><strong>{refresh_date}</strong> (API Mir@bel)</span></p>
  </aside>
</div>

<div class="revues-levels">
{levels_html}
</div>

<link rel="stylesheet" href="{assets_prefix}stylesheets/revues-exploration.css">

<div id="revues-explorer" class="revues-explorer" lang="{lang}" data-source="{assets_prefix}data/revues-exploration.json"><p class="explorer-loading">{labels["loading"]}</p></div>

<script src="{assets_prefix}javascripts/revues-config.js" defer></script>
<script src="{assets_prefix}javascripts/revues-exploration.js" defer></script>
""",
        encoding="utf-8",
    )