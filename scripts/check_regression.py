#!/usr/bin/env python3
"""Contrôler les invariants statistiques sans figer le contenu du recensement.

Les effectifs et répartitions sont libres d'évoluer avec le classeur XLSX.
Les tests sur valeurs attendues restent dans tests/check_fixture.py.
"""
from statistics_data import derive, read_rows
from statistics_project import DEFAULT_SOURCE


def check(condition, message):
    if not condition:
        raise SystemExit(f"Non-régression statistiques : {message}")


def main():
    rows = read_rows(DEFAULT_SOURCE)
    data = derive(rows, DEFAULT_SOURCE)
    total = data["total"]
    check(total > 0, "corpus vide")

    for label, counter in (
        ("niveaux", data["levels"]),
        ("formats", data["formats"]),
    ):
        actual = sum(counter.values())
        check(actual == total, f"{label} : {actual}/{total} revues")

    for label, counter in (
        ("années", data["years"]),
        ("périodicités", data["periodicities"]),
        ("disciplines", data["disciplines"]),
        ("structures", data["structures"]),
        ("droits", data["rights"]),
        ("secteurs", data["sectors"]),
    ):
        actual = sum(counter.values())
        check(actual <= total, f"{label} : {actual}/{total} revues")

    for label, counter, breakdown in (
        ("rattachement", data["levels"], data["level_access"]),
        ("format", data["formats"], data["format_access"]),
        ("structure", data["structures"], data["struct_access"]),
    ):
        # Les catégories de structure sont regroupées différemment pour
        # les croisements ; seul le total est comparable dans ce cas.
        actual = sum(sum(values.values()) for values in breakdown.values())
        expected = sum(counter.values())
        check(actual == expected, f"croisement {label} : {actual}/{expected}")

    for label, counter, breakdown in (
        ("année de création", data["years"], data["year_access"]),
    ):
        actual = sum(sum(values.values()) for values in breakdown.values())
        expected = sum(counter.values())
        check(actual == expected, f"croisement {label} : {actual}/{expected}")

    for label, breakdown in (
        ("rattachement", data["level_access"]),
        ("format", data["format_access"]),
        ("structure", data["struct_access"]),
        ("année de création", data["year_access"]),
        ("période de création", data["date_access"]),
    ):
        for category, counts in breakdown.items():
            unexpected = set(counts) - {"open", "restricted"}
            check(not unexpected, f"{label}/{category} : statuts inconnus {unexpected}")

    open_access = sum(values["open"] for values in data["level_access"].values())
    restricted = sum(values["restricted"] for values in data["level_access"].values())
    check(open_access + restricted == total, "répartition de l'accès ouvert incomplète")

    years = sum(data["years"].values())
    check(sum(data["periods"].values()) == years, "périodes de création incohérentes")
    check(
        sum(sum(values.values()) for values in data["date_access"].values()) == years,
        "accès ouvert par période de création incohérent",
    )
    check(
        sum(sum(values.values()) for _, _, values in data["creation_quantiles"]) == years,
        "quantiles chronologiques incohérents",
    )

    print(
        f"Non-régression statistiques : OK "
        f"({total} revues, {open_access} en accès ouvert)"
    )


if __name__ == "__main__":
    main()
