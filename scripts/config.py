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
