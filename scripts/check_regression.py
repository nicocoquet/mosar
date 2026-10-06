#!/usr/bin/env python3
"""Contrôles de non-régression sur le corpus Mosar publié.

Ces assertions portent sur des invariants métier du corpus de référence.
Elles doivent être mises à jour explicitement lorsqu'une évolution des
données source est volontaire.
"""
from statistics_data import derive, read_rows


EXPECTED = {
    "total": 186,
    "open_access": 101,
    "formats": {
        "Papier et numérique": 130,
        "Numérique": 51,
        "Papier": 5,
    },
}


def main():
    data = derive(read_rows())

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

    assert sum(data["levels"].values()) == EXPECTED["total"]
    assert sum(data["periodicities"].values()) == EXPECTED["total"]
    assert sum(data["disciplines"].values()) == EXPECTED["total"]
    assert sum(data["structures"].values()) == EXPECTED["total"]
    assert sum(data["rights"].values()) == EXPECTED["total"]

    print(
        "Non-régression statistiques : OK "
        f"({EXPECTED['total']} revues, {EXPECTED['open_access']} en accès ouvert)"
    )


if __name__ == "__main__":
    main()
