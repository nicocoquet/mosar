#!/usr/bin/env python3
"""Contrôles structurels du JSON produit pour l'explorateur Revues."""
from __future__ import annotations

import json
from pathlib import Path

from mosar_model import PROXIMITY_LEVELS


SOURCE = Path("docs/assets/data/revues-exploration.json")
REQUIRED_RECORD_KEYS = {
    "mirabel_id",
    "title",
    "sigle",
    "issn",
    "languages",
    "publishers",
    "country",
    "periodicity",
    "publication_format",
    "publication_fees",
    "labels",
    "ddh",
    "themes",
    "journal_url",
    "mirabel_url",
    "mosar",
}
REQUIRED_MOSAR_KEYS = {
    "proximity_level",
    "open_access",
    "discipline",
    "editorial_structure",
    "licence",
}


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert isinstance(payload.get("meta"), dict), "Bloc meta absent ou invalide"
    records = payload.get("records")
    assert isinstance(records, list), "Bloc records absent ou invalide"

    ids = []
    previous_key = None
    for index, record in enumerate(records, start=1):
        missing = REQUIRED_RECORD_KEYS - record.keys()
        assert not missing, f"Revue {index}: clés absentes {sorted(missing)}"
        assert isinstance(record["mirabel_id"], int), (
            f"Revue {index}: identifiant Mir@bel invalide"
        )
        assert record["title"], f"Revue {index}: titre vide"
        ids.append(record["mirabel_id"])

        mosar = record["mosar"]
        if mosar is not None:
            missing_mosar = REQUIRED_MOSAR_KEYS - mosar.keys()
            assert not missing_mosar, (
                f"Revue {record['mirabel_id']}: clés Mosar absentes "
                f"{sorted(missing_mosar)}"
            )

        raw_level = ((mosar or {}).get("proximity_level") or "").strip()
        try:
            level = int(raw_level)
            if level not in PROXIMITY_LEVELS:
                level = 99
        except (TypeError, ValueError):
            level = 99
        current_key = (level, record["title"].casefold())
        if previous_key is not None:
            assert previous_key <= current_key, (
                "Ordre des revues invalide autour de "
                f"{record['mirabel_id']} ({record['title']})"
            )
        previous_key = current_key

    assert len(ids) == len(set(ids)), "Identifiants Mir@bel dupliqués"
    assert payload["meta"].get("mirabel_unique_reviews") == len(records), (
        "Le total meta.mirabel_unique_reviews ne correspond pas aux records"
    )

    print(
        "Contrôle structurel Revues : OK "
        f"({len(records)} enregistrements, identifiants uniques)"
    )


if __name__ == "__main__":
    main()
