#!/usr/bin/env python3
"""Génère une page statique Mosar à partir d'une grappe publique Mir@bel."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GRAPPE_ID = 15
API_URL = "https://reseau-mirabel.info/api/titres"
GRAPPE_URL = "https://reseau-mirabel.info/grappe/15/PCP-Sciences-de-l-Antiquite-et-Archeologie"
CACHE = Path("data/mirabel/grappe-15.json")
DOC_FR = Path("docs/mirabel.md")
DOC_EN = Path("docs/mirabel.en.md")
PAGE_SIZE = 1000


def fetch_page(offset: int) -> list[dict]:
    query = urlencode({"grappeid": GRAPPE_ID, "actif": 1, "offset": offset})
    request = Request(f"{API_URL}?{query}", headers={"User-Agent": "Mosar/1.0 (+https://nicocoquet.github.io/mosar/)"})
    with urlopen(request, timeout=45) as response:
        payload = json.load(response)
    if not isinstance(payload, list):
        raise RuntimeError("Réponse Mir@bel inattendue : une liste JSON était attendue.")
    return payload


def fetch_all() -> list[dict]:
    records, offset = [], 0
    while True:
        batch = fetch_page(offset)
        records.extend(batch)
        if len(batch) < PAGE_SIZE:
            return records
        offset += PAGE_SIZE


def load_data() -> tuple[list[dict], str, bool]:
    try:
        records = fetch_all()
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({"fetched_at": fetched_at, "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
        return records, fetched_at, False
    except Exception:
        if not CACHE.exists():
            raise
        cached = json.loads(CACHE.read_text(encoding="utf-8"))
        return cached["records"], cached.get("fetched_at", "date inconnue"), True


def first(record: dict, *keys: str, default=""):
    for key in keys:
        value = record.get(key)
        if value not in (None, "", []):
            return value
    return default


def title_name(record: dict) -> str:
    return str(first(record, "titre", "nom", "nomtitre", default="Titre sans nom"))


def revue_id(record: dict):
    value = first(record, "revueid", "revue_id")
    if value:
        return value
    revue = record.get("revue")
    return first(revue, "id", "revueid") if isinstance(revue, dict) else ""


def issns(record: dict) -> str:
    values = []
    for key in ("issn", "issne", "issnl", "issn_e", "issn_l"):
        value = record.get(key)
        if isinstance(value, list):
            values.extend(str(v) for v in value if v)
        elif value:
            values.append(str(value))
    return ", ".join(dict.fromkeys(values)) or "—"


def build_rows(records: list[dict]) -> str:
    rows = []
    for record in sorted(records, key=lambda r: title_name(r).casefold()):
        name = title_name(record).replace("|", "\\|")
        rid = revue_id(record)
        if rid:
            name = f"[{name}](https://reseau-mirabel.info/revue/{rid})"
        rows.append(f"| {name} | {issns(record)} |")
    return "\n".join(rows)


def render(records: list[dict], fetched_at: str, fallback: bool, lang: str) -> str:
    count, date, rows = len(records), fetched_at[:10], build_rows(records)
    if lang == "fr":
        status = "cache local de secours" if fallback else "API Mir@bel"
        return f'''# Grappe Mir@bel

## PCP Sciences de l’Antiquité et Archéologie

Cette page est un **prototype d’intégration de données Mir@bel dans Mosar**. Elle est générée automatiquement à partir de la grappe publique n° {GRAPPE_ID} « PCP Sciences de l’Antiquité et Archéologie ».

**{count} titres actifs** ont été récupérés. Dernière actualisation : **{date}** ({status}).

[Consulter la grappe originale sur Mir@bel]({GRAPPE_URL}){{ target="_blank" }}

Les données Mir@bel sont réutilisées sous Licence Ouverte ; Mir@bel demeure la source de référence.

### Revues et titres

| Titre | ISSN |
| --- | --- |
{rows}
'''
    status = "local fallback cache" if fallback else "Mir@bel API"
    return f'''# Mir@bel cluster

## PCP Ancient Studies and Archaeology

This page is a **prototype integration of Mir@bel data into Mosar**. It is generated automatically from public cluster no. {GRAPPE_ID}, “PCP Sciences de l’Antiquité et Archéologie”.

**{count} active titles** were retrieved. Last refresh: **{date}** ({status}).

[View the original cluster on Mir@bel]({GRAPPE_URL}){{ target="_blank" }}

Mir@bel data are reused under the French Open Licence; Mir@bel remains the reference source.

### Journals and titles

| Title | ISSN |
| --- | --- |
{rows}
'''


def main() -> None:
    records, fetched_at, fallback = load_data()
    if not records:
        raise RuntimeError("La grappe Mir@bel n'a renvoyé aucun titre actif.")
    DOC_FR.write_text(render(records, fetched_at, fallback, "fr"), encoding="utf-8")
    DOC_EN.write_text(render(records, fetched_at, fallback, "en"), encoding="utf-8")
    print(f"Grappe Mir@bel {GRAPPE_ID}: {len(records)} titres actifs.")

if __name__ == "__main__":
    main()
