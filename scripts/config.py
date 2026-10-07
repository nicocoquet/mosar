"""Chargement et validation de la configuration de l'instance Mosar."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "project.yml"

_REQUIRED = {
    "project": ("id", "name", "site_url"),
    "data": ("file", "sheet"),
    "columns": (
        "journal_name",
        "mirabel_id",
        "proximity",
        "open_access",
        "format",
        "creation_year",
        "periodicity",
        "discipline",
        "publisher_type",
        "licence",
    ),
    "mirabel": ("api", "cluster_id", "cluster_name", "cluster_url"),
    "privacy": ("forbidden_columns",),
}


def _validate(config: dict[str, Any]) -> None:
    for section, keys in _REQUIRED.items():
        values = config.get(section)
        if not isinstance(values, dict):
            raise SystemExit(f"Section de configuration manquante ou invalide : {section}")
        missing = [key for key in keys if values.get(key) in (None, "")]
        if missing:
            raise SystemExit(
                f"Clés de configuration manquantes dans {section} : "
                + ", ".join(missing)
            )

    publication = config.get("publication")
    if not isinstance(publication, dict):
        raise SystemExit(
            "Section de configuration manquante ou invalide : publication"
        )

    statistics = publication.get("statistics")
    if not isinstance(statistics, dict):
        raise SystemExit(
            "Section de configuration manquante ou invalide : "
            "publication.statistics"
        )

    if statistics.get("downloads") in (None, ""):
        raise SystemExit(
            "Clé de configuration manquante : publication.statistics.downloads"
        )

    statistics_pages = statistics.get("pages")
    if not isinstance(statistics_pages, dict) or not statistics_pages:
        raise SystemExit(
            "Section de configuration manquante ou invalide : "
            "publication.statistics.pages"
        )

    for lang, page in statistics_pages.items():
        if not isinstance(page, dict):
            raise SystemExit(
                f"Configuration invalide : publication.statistics.pages.{lang}"
            )
        missing = [
            key for key in ("intro", "output")
            if page.get(key) in (None, "")
        ]
        if missing:
            raise SystemExit(
                f"Clés de configuration manquantes dans "
                f"publication.statistics.pages.{lang} : "
                + ", ".join(missing)
            )

    journals = publication.get("journals")
    if not isinstance(journals, dict):
        raise SystemExit(
            "Section de configuration manquante ou invalide : "
            "publication.journals"
        )

    missing = [
        key for key in ("data_file", "report_file")
        if journals.get(key) in (None, "")
    ]
    if missing:
        raise SystemExit(
            "Clés de configuration manquantes dans publication.journals : "
            + ", ".join(missing)
        )

    journal_pages = journals.get("pages")
    if not isinstance(journal_pages, dict) or not journal_pages:
        raise SystemExit(
            "Section de configuration manquante ou invalide : "
            "publication.journals.pages"
        )

    for lang, page in journal_pages.items():
        if not isinstance(page, dict):
            raise SystemExit(
                f"Configuration invalide : publication.journals.pages.{lang}"
            )
        missing = [
            key for key in ("intro", "output")
            if page.get(key) in (None, "")
        ]
        if missing:
            raise SystemExit(
                f"Clés de configuration manquantes dans "
                f"publication.journals.pages.{lang} : "
                + ", ".join(missing)
            )

    fallback = journals.get("fallback")
    if not isinstance(fallback, dict):
        raise SystemExit(
            "Section de configuration manquante ou invalide : "
            "publication.journals.fallback"
        )

    if not isinstance(fallback.get("enabled"), bool):
        raise SystemExit(
            "publication.journals.fallback.enabled doit être un booléen."
        )

    if fallback.get("file") in (None, ""):
        raise SystemExit(
            "Clé de configuration manquante : "
            "publication.journals.fallback.file"
        )

    if not isinstance(config["privacy"]["forbidden_columns"], list):
        raise SystemExit("privacy.forbidden_columns doit être une liste.")

    try:
        config["mirabel"]["cluster_id"] = int(config["mirabel"]["cluster_id"])
    except (TypeError, ValueError):
        raise SystemExit("mirabel.cluster_id doit être un entier.")


@lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Fichier de configuration introuvable : {CONFIG_PATH}")

    with CONFIG_PATH.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    if not isinstance(config, dict):
        raise SystemExit(f"Configuration YAML invalide : {CONFIG_PATH}")

    _validate(config)
    return config


def project_path(value: str) -> Path:
    """Résout un chemin de configuration relativement à la racine du dépôt."""
    path = Path(value)
    return path if path.is_absolute() else ROOT / path
