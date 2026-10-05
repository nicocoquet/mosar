#!/usr/bin/env python3
"""Explorateur des revues : métadonnées Mir@bel + enrichissements analytiques Mosar."""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GRAPPE_ID = 15
API = "https://reseau-mirabel.info/api"
XLSX = Path("data/Recensement-revues-stat.xlsx")
FALLBACK = Path("data/mirabel/mosar-test-enrichment.csv")
OUT_JSON = Path("docs/assets/data/revues-exploration.json")
OUT_REPORT = Path("data/revues/join-report.json")
OUT_MD = Path("docs/revues-exploration.md")


def api_json(path: str):
    req = Request(f"{API}{path}", headers={"User-Agent": "Mosar/1.0 (+https://nicocoquet.github.io/mosar/)"})
    with urlopen(req, timeout=45) as response:
        return json.load(response)


def fetch_titles() -> list[dict]:
    records, offset = [], 0
    while True:
        q = urlencode({"grappeid": GRAPPE_ID, "actif": 1, "offset": offset})
        batch = api_json(f"/titres?{q}")
        if not isinstance(batch, list):
            raise RuntimeError("Réponse inattendue de /titres")
        records.extend(batch)
        if len(batch) < 1000:
            return records
        offset += 1000


def load_mosar() -> tuple[dict[int, dict], str]:
    try:
        from openpyxl import load_workbook
        ws = load_workbook(XLSX, data_only=True, read_only=True)["recencement"]
        rows = ws.iter_rows(values_only=True)
        headers = [str(v).strip() if v is not None else "" for v in next(rows)]
        if "ID Mir@bel" in headers:
            pos = {h: i for i, h in enumerate(headers)}
            fields = {
                "nom_revue": "Nom revue", "niveau_rattachement": "Niveau rattachement",
                "acces_ouvert": "Accès ouvert", "discipline": "Discipline",
                "periodicite": "Nombre de n°s par an", "format": "Format",
                "type_editeur": "Type d'éditeur", "licence": "Licence",
            }
            out = {}
            for row in rows:
                raw = row[pos["ID Mir@bel"]]
                if raw in (None, ""):
                    continue
                rid = int(raw)
                out[rid] = {key: row[pos[col]] if col in pos else None for key, col in fields.items()}
            return out, "XLSX Mosar"
    except Exception as exc:
        print(f"Lecture XLSX impossible pour la jointure ({exc}); recours au CSV de prototype.")

    out = {}
    with FALLBACK.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rid = int(row.pop("mirabel_id"))
            out[rid] = row
    return out, "CSV de prototype (extrait du XLSX fourni)"


def normalize_periodicity(value):
    if value is None or value == "": return "Non renseignée"
    s = str(value).strip().lower().replace(",", ".")
    if s == "parution continue": return "Parution continue"
    if s == "parution irrégulière": return "Parution irrégulière"
    try:
        n = float(s)
        if n == .5: return "Un numéro tous les deux ans"
        if n == 1: return "Annuel"
        if n == 2: return "Semestriel"
        if n == 3: return "Quadrimestriel"
        if n == 4: return "Trimestriel"
        if n > 4: return "Plus de 4 numéros/an"
    except ValueError:
        pass
    return str(value).strip()


def normalize_open(value):
    if value is None: return None
    s = str(value).strip().casefold()
    if s == "oui": return "Accès ouvert"
    if s == "non": return "Accès restreint"
    return str(value).strip()


def publication_format(issns):
    supports = {str(x.get("support") or "").strip().casefold() for x in (issns or []) if isinstance(x, dict)}
    supports.discard("")
    has_paper = "papier" in supports
    has_digital = "electronique" in supports or "électronique" in supports
    if has_paper and has_digital: return "Papier et numérique"
    if has_digital: return "Numérique"
    if has_paper: return "Papier"
    return None


def external_links(t):
    out = []
    for item in t.get("liensext") or []:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            out.append({"url": item[0], "label": item[1]})
    return out


def title_label(t: dict) -> str:
    prefix = (t.get("prefixe") or "").strip()
    name = (t.get("titre") or "Titre sans nom").strip()
    return f"{prefix} {name}".strip()


def main():
    titles = fetch_titles()
    themes_payload = api_json(f"/themes/grappe/{GRAPPE_ID}")
    themes_by_revue = {int(x["revueid"]): [t.get("nom") for t in x.get("themes", []) if t.get("nom")] for x in themes_payload}
    mosar, mosar_source = load_mosar()

    by_revue: dict[int, dict] = {}
    duplicate_active_titles = Counter()
    for t in titles:
        rid = t.get("revueid")
        if not rid:
            continue
        rid = int(rid)
        duplicate_active_titles[rid] += 1
        if rid in by_revue:
            continue
        issn_objects = t.get("issns") or []
        issns = [x["issn"] for x in issn_objects if isinstance(x, dict) and x.get("issn")]
        links = external_links(t)
        ddh = next((x for x in links if str(x["label"]).strip().casefold() == "ddh"), None)
        labels = [str(x).strip() for x in (t.get("labellisation") or []) if str(x).strip()]
        m = mosar.get(rid)
        by_revue[rid] = {
            "mirabel_id": rid,
            "title": title_label(t),
            "sigle": t.get("sigle") or "",
            "issn": list(dict.fromkeys(issns)),
            "languages": t.get("langues") or [],
            "publishers": t.get("editeurs") or [],
            "periodicity": (t.get("periodicite") or "").strip() or None,
            "publication_format": publication_format(issn_objects),
            # L'API Mir@bel 1.6.3 n'expose pas encore le champ visible « Frais de publication ».
            # Le modèle est néanmoins prêt : la facette apparaîtra dès qu'une valeur API sera disponible.
            "publication_fees": t.get("fraispublication") or t.get("frais_publication") or None,
            "labels": labels,
            "ddh": ddh,
            "themes": themes_by_revue.get(rid, []),
            "journal_url": t.get("url") or "",
            "mirabel_url": t.get("url_revue_mirabel") or f"https://reseau-mirabel.info/revue/{rid}",
            "illustration": "../assets/images/revues/gallia-card.jpg" if rid == 853 else None,
            "mosar": None if not m else {
                "proximity_level": str(m.get("niveau_rattachement") or "").strip(),
                "open_access": normalize_open(m.get("acces_ouvert")),
                "discipline": str(m.get("discipline") or "").strip(),
                "editorial_structure": str(m.get("type_editeur") or "").strip(),
                "licence": str(m.get("licence") or "").strip(),
            },
        }

    records = sorted(by_revue.values(), key=lambda r: r["title"].casefold())
    cluster_ids = set(by_revue)
    mosar_ids = set(mosar)
    matched = sorted(cluster_ids & mosar_ids)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cluster_id": GRAPPE_ID,
        "mirabel_active_titles": len(titles),
        "mirabel_unique_reviews": len(records),
        "mosar_source": mosar_source,
        "mosar_ids": len(mosar_ids),
        "matched_ids": matched,
        "matched_count": len(matched),
        "mirabel_without_mosar_count": len(cluster_ids - mosar_ids),
        "mosar_outside_cluster_ids": sorted(mosar_ids - cluster_ids),
        "duplicate_active_title_review_ids": sorted(rid for rid, n in duplicate_active_titles.items() if n > 1),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"meta": report, "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text('''---\nhide:\n  - toc\n---\n# Revues — exploration\n\nCette page est un **prototype hors navigation**. Elle teste l’articulation entre les métadonnées de la grappe Mir@bel n° 15 et les données analytiques propres au projet Mosar. La page **Revues** actuelle n’est pas modifiée.\n\n<link rel="stylesheet" href="../assets/stylesheets/revues-exploration.css">\n\n<div id="revues-explorer" class="revues-explorer" data-source="../assets/data/revues-exploration.json">\n  <p class="explorer-loading">Chargement des revues…</p>\n</div>\n\n<script src="../assets/javascripts/revues-exploration.js" defer></script>\n''', encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
