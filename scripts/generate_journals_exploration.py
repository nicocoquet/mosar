#!/usr/bin/env python3
"""Explorateur des revues : métadonnées Mir@bel + enrichissements analytiques Mosar."""
from __future__ import annotations

import json

from config import load_config, project_path
from mosar_model import PROXIMITY_LEVELS
from journals_pipeline import build_journals_dataset
from journals_publication import write_data, write_page
from journals_sources import (
    MirabelSource,
    MosarJournalSource,
    fetch_mirabel_themes,
    fetch_mirabel_titles,
    load_mosar_journals,
)

CONFIG = load_config()

PROJECT_NAME = CONFIG["project"]["name"]
SITE_URL = CONFIG["project"]["site_url"]

GRAPPE_ID = CONFIG["mirabel"]["cluster_id"]
GRAPPE_NAME = CONFIG["mirabel"]["cluster_name"]
GRAPPE_URL = CONFIG["mirabel"]["cluster_url"]

MIRABEL_SOURCE = MirabelSource(
    api=CONFIG["mirabel"]["api"],
    cluster_id=GRAPPE_ID,
    project_name=PROJECT_NAME,
    site_url=SITE_URL,
)

JOURNALS_PUBLICATION = CONFIG["publication"]["journals"]
FALLBACK_CONFIG = JOURNALS_PUBLICATION["fallback"]

MOSAR_SOURCE = MosarJournalSource(
    xlsx=project_path(CONFIG["data"]["file"]),
    sheet=CONFIG["data"]["sheet"],
    columns=CONFIG["columns"],
    project_name=PROJECT_NAME,
    fallback_enabled=FALLBACK_CONFIG["enabled"],
    fallback=project_path(FALLBACK_CONFIG["file"]),
)


def main() -> None:
    titles = fetch_mirabel_titles(MIRABEL_SOURCE)
    themes_by_journal = fetch_mirabel_themes(MIRABEL_SOURCE)
    mosar, mosar_source = load_mosar_journals(MOSAR_SOURCE)

    records, report = build_journals_dataset(
        titles,
        themes_by_journal,
        mosar,
        cluster_id=GRAPPE_ID,
        mosar_source=mosar_source,
    )

    write_data(
        records,
        report,
        proximity_levels=PROXIMITY_LEVELS,
    )
    write_page(
        report,
        cluster_id=GRAPPE_ID,
        cluster_name=GRAPPE_NAME,
        cluster_url=GRAPPE_URL,
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
