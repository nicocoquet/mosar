#!/usr/bin/env python3
"""Contrôles de non-régression sur le corpus Mosar publié.

Ces assertions portent sur des invariants métier du corpus de référence.
Elles doivent être mises à jour explicitement lorsqu'une évolution des
données source est volontaire.
"""
from statistics_data import derive, read_rows
from statistics_project import DEFAULT_SOURCE


EXPECTED = {
    "total": 193,
    "open_access": 105,
    "formats": {
        "Numérique": 54,
        "Papier et numérique": 135,
        "Papier": 4,
    },
    "coverage": {
        "levels": 193,
        "years": 192,
        "periodicities": 192,
        "disciplines": 193,
        "structures": 193,
        "rights": 192,
    },
}


def main():
    rows = read_rows(DEFAULT_SOURCE)
    data = derive(rows, DEFAULT_SOURCE)

    assert data["total"] == EXPECTED["total"], (
        f"Corpus inattendu : {data['total']} au lieu de {EXPECTED['total']}"
    )

    open_access = sum(
        values["open"] for values in data["level_access"].values()
    )
    assert open_access == EXPECTED["open_access"], (
        f"Accès ouvert inattendu : {open_access} "
        f"au lieu de {EXPECTED['open_access']}"
    )

    assert dict(data["formats"]) == EXPECTED["formats"], (
        f"Formats inattendus : {dict(data['formats'])!r}"
    )

    for name, expected in EXPECTED["coverage"].items():
        actual = sum(data[name].values())
        assert actual == expected, (
            f"Couverture inattendue pour {name} : "
            f"{actual} au lieu de {expected}"
        )

    print(
        "Non-régression statistiques : OK "
        f"({EXPECTED['total']} revues, "
        f"{EXPECTED['open_access']} en accès ouvert)"
    )


if __name__ == "__main__":
    main()
