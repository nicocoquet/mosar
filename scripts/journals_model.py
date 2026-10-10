"""Modèle de données et normalisations de l'explorateur de revues.

Ce module ne connaît ni l'API Mir@bel ni le XLSX : il transforme les
métadonnées déjà chargées en enregistrements publiables par l'explorateur.
"""
from __future__ import annotations
from mosar_model import (
    ALLOWED_STRUCTURES,
    DISCIPLINE_MAP,
    LICENCE_MAP,
    normalize_structure,
)

def normalize_open(value):
    if value is None:
        return None
    text = str(value).strip().casefold()
    if text == "oui":
        return "Accès ouvert"
    if text == "non":
        return "Accès restreint"
    return str(value).strip()

def normalize_mosar_category(value, mapping, field, journal_id):
    """Normaliser une catégorie Mosar avec validation stricte."""
    text = str(value).strip() if value is not None else ""

    if not text:
        return None

    if text not in mapping:
        raise ValueError(
            f"Revue Mir@bel {journal_id} : "
            f"valeur inconnue pour {field} : {text!r}"
        )

    return mapping[text]


def normalize_editorial_structure(value, journal_id):
    """Normaliser la structure éditoriale selon le référentiel Mosar."""
    text = str(value).strip() if value is not None else ""

    if not text:
        return None

    canonical = text.lower()

    if canonical not in ALLOWED_STRUCTURES:
        raise ValueError(
            f"Revue Mir@bel {journal_id} : "
            f"structure éditoriale inconnue : {text!r}"
        )

    return normalize_structure(canonical)

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

def journal_references(links):
    """Extraire les référencements DDH, DOAJ et Wikidata."""
    supported = {"ddh": "DDH", "doaj": "DOAJ", "wikidata": "Wikidata"}
    references = {}

    for item in links:
        label = str(item.get("label") or "").strip().casefold()
        url = str(item.get("url") or "").strip()

        if label in supported and url:
            references[supported[label]] = {
                "label": supported[label],
                "url": url,
            }

    return references

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


def build_record(title, themes, mosar_data):
    rid = int(title["revueid"])
    issn_objects = title.get("issns") or []
    issns = [
        item["issn"]
        for item in issn_objects
        if isinstance(item, dict) and item.get("issn")
    ]
    links = external_links(title)
    references = journal_references(links)
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

    is_diamond = any(
        label.casefold() == "ddh diamond journal"
        for label in labels
    )

    mirabel_title = title_label(title)

    mosar_title = (
        str(mosar_data.get("nom_revue") or "").strip()
        if mosar_data
        else ""
    )

    mosar_subtitle = (
        str(mosar_data.get("sous_titre") or "").strip()
        if mosar_data
        else ""
    )

    return {
        "mirabel_id": rid,
        "title": mosar_title or mirabel_title,
        "subtitle": mosar_subtitle,
        "mirabel_title": mirabel_title,
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
        "is_diamond": is_diamond,
        "references": references,
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
            "discipline_normalized": normalize_mosar_category(
                mosar_data.get("discipline"),
                DISCIPLINE_MAP,
                "discipline",
                rid,
            ),
            "editorial_structure_normalized": normalize_editorial_structure(
                mosar_data.get("type_editeur"),
                rid,
            ),
            "licence_normalized": normalize_mosar_category(
                mosar_data.get("licence"),
                LICENCE_MAP,
                "licence",
                rid,
            ),
        },
    }
