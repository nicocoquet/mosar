"""Modèle de données et normalisations de l'explorateur de revues.

Ce module ne connaît ni l'API Mir@bel ni le XLSX : il transforme les
métadonnées déjà chargées en enregistrements publiables par l'explorateur.
"""
from __future__ import annotations

from mosar_model import PROXIMITY_LEVELS


def normalize_open(value):
    if value is None:
        return None
    text = str(value).strip().casefold()
    if text == "oui":
        return "Accès ouvert"
    if text == "non":
        return "Accès restreint"
    return str(value).strip()


def publication_format(issns):
    supports = {
        str(item.get("support") or "").strip().casefold()
        for item in (issns or [])
        if isinstance(item, dict)
    }
    supports.discard("")
    paper = "papier" in supports
    digital = "electronique" in supports or "électronique" in supports
    if paper and digital:
        return "Papier et numérique"
    if digital:
        return "Numérique"
    if paper:
        return "Papier"
    return None


def external_links(title):
    links = []
    for item in title.get("liensext") or []:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            links.append({"url": item[0], "label": item[1]})
    return links


def title_label(title):
    return (
        f"{(title.get('prefixe') or '').strip()} "
        f"{(title.get('titre') or 'Titre sans nom').strip()}"
    ).strip()


def country_value(title):
    value = (
        title.get("pays")
        or title.get("payspublication")
        or title.get("pays_publication")
        or title.get("country")
    )
    if isinstance(value, dict):
        return value.get("nom") or value.get("name") or value.get("libelle")
    if isinstance(value, list):
        values = []
        for item in value:
            if isinstance(item, dict):
                values.append(item.get("nom") or item.get("name") or item.get("libelle"))
            elif item:
                values.append(str(item))
        return ", ".join(item for item in values if item) or None
    return str(value).strip() if value not in (None, "") else None


def proximity_sort_key(record):
    raw = ((record.get("mosar") or {}).get("proximity_level") or "").strip()
    try:
        level = int(raw)
        if level not in PROXIMITY_LEVELS:
            level = 99
    except (TypeError, ValueError):
        level = 99
    return level, record["title"].casefold()


def build_record(title, themes, mosar_data):
    rid = int(title["revueid"])
    issn_objects = title.get("issns") or []
    issns = [
        item["issn"]
        for item in issn_objects
        if isinstance(item, dict) and item.get("issn")
    ]
    links = external_links(title)
    ddh = next(
        (
            item
            for item in links
            if str(item["label"]).strip().casefold() == "ddh"
        ),
        None,
    )
    labels = [
        str(item).strip()
        for item in (title.get("labellisation") or [])
        if str(item).strip()
    ]

    return {
        "mirabel_id": rid,
        "title": title_label(title),
        "sigle": title.get("sigle") or "",
        "issn": list(dict.fromkeys(issns)),
        "languages": title.get("langues") or [],
        "publishers": title.get("editeurs") or [],
        "country": country_value(title),
        "periodicity": (title.get("periodicite") or "").strip() or None,
        "publication_format": publication_format(issn_objects),
        "publication_fees": title.get("fraispublication")
        or title.get("frais_publication")
        or None,
        "labels": labels,
        "ddh": ddh,
        "themes": themes,
        "journal_url": title.get("url") or "",
        "mirabel_url": title.get("url_revue_mirabel")
        or f"https://reseau-mirabel.info/revue/{rid}",
        "mosar": None
        if not mosar_data
        else {
            "proximity_level": str(
                mosar_data.get("niveau_rattachement") or ""
            ).strip(),
            "open_access": normalize_open(mosar_data.get("acces_ouvert")),
            "discipline": str(mosar_data.get("discipline") or "").strip(),
            "editorial_structure": str(
                mosar_data.get("type_editeur") or ""
            ).strip(),
            "licence": str(mosar_data.get("licence") or "").strip(),
        },
    }
