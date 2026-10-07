#!/usr/bin/env python3
"""Explorateur des revues : métadonnées Mir@bel + enrichissements analytiques Mosar."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone

from config import load_config, project_path
from journals_model import build_record
from journals_sources import (
    MirabelSource,
    MosarJournalSource,
    fetch_mirabel_themes,
    fetch_mirabel_titles,
    load_mosar_journals,
)
from mosar_model import PROXIMITY_LEVELS, proximity_sort_key

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
JOURNALS_PAGE = JOURNALS_PUBLICATION["pages"]["fr"]
FALLBACK_CONFIG = JOURNALS_PUBLICATION["fallback"]

MOSAR_SOURCE = MosarJournalSource(
    xlsx=project_path(CONFIG["data"]["file"]),
    sheet=CONFIG["data"]["sheet"],
    columns=CONFIG["columns"],
    project_name=PROJECT_NAME,
    fallback_enabled=FALLBACK_CONFIG["enabled"],
    fallback=project_path(FALLBACK_CONFIG["file"]),
)

OUT_JSON = project_path(JOURNALS_PUBLICATION["data_file"])
OUT_REPORT = project_path(JOURNALS_PUBLICATION["report_file"])
INTRO_FILE = project_path(JOURNALS_PAGE["intro"])
OUT_MD = project_path(JOURNALS_PAGE["output"])


def load_intro() -> str:
    if not INTRO_FILE.is_file():
        raise SystemExit(
            f"Introduction éditoriale de la page Revues introuvable : {INTRO_FILE}"
        )
    return INTRO_FILE.read_text(encoding="utf-8").strip()


def main():
    titles = fetch_mirabel_titles(MIRABEL_SOURCE)
    themes_by_revue = fetch_mirabel_themes(MIRABEL_SOURCE)
    mosar, mosar_source = load_mosar_journals(MOSAR_SOURCE)
    by_revue = {}; duplicate_active_titles = Counter()
    for t in titles:
        rid = t.get("revueid")
        if not rid: continue
        rid = int(rid); duplicate_active_titles[rid] += 1
        if rid in by_revue: continue
        by_revue[rid] = build_record(
            t,
            themes_by_revue.get(rid, []),
            mosar.get(rid),
        )
    records = sorted(by_revue.values(), key=proximity_sort_key)
    cluster_ids=set(by_revue); mosar_ids=set(mosar); matched=sorted(cluster_ids & mosar_ids)
    report={"generated_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),"cluster_id":GRAPPE_ID,"mirabel_active_titles":len(titles),"mirabel_unique_reviews":len(records),"mosar_source":mosar_source,"mosar_ids":len(mosar_ids),"matched_ids":matched,"matched_count":len(matched),"mirabel_without_mosar_count":len(cluster_ids-mosar_ids),"mosar_outside_cluster_ids":sorted(mosar_ids-cluster_ids),"duplicate_active_title_review_ids":sorted(rid for rid,n in duplicate_active_titles.items() if n>1)}
    OUT_JSON.parent.mkdir(parents=True,exist_ok=True); OUT_REPORT.parent.mkdir(parents=True,exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(
            {
                "meta": report,
                "model": {"proximity_levels": list(PROXIMITY_LEVELS)},
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    OUT_REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    refresh_date = report["generated_at"][:10]
    intro = load_intro()
    OUT_MD.write_text(
        f'''---
hide:
  - toc
---
# Revues {{ .page-title-compact }}

<div class="revues-intro" markdown="1">

{intro}

</div>

<p class="revues-source">Grappe Mir@bel n° {GRAPPE_ID} « {GRAPPE_NAME} ».</p>
<p class="revues-source-link"><a href="{GRAPPE_URL}" target="_blank" rel="noopener">Consulter la grappe sur Mir@bel</a></p>
<p class="revues-updated">Dernière actualisation : <strong>{refresh_date}</strong> (API Mir@bel).</p>

<link rel="stylesheet" href="../assets/stylesheets/revues-exploration.css">

<div id="revues-explorer" class="revues-explorer" data-source="../assets/data/revues-exploration.json"><p class="explorer-loading">Chargement des revues…</p></div>

<script src="../assets/javascripts/revues-config.js" defer></script>
<script src="../assets/javascripts/revues-exploration.js" defer></script>
''',
        encoding="utf-8",
    )
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__": main()