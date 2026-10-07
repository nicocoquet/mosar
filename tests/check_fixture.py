from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from statistics_data import StatisticsSource, derive, read_rows


FIXTURE = ROOT / "tests" / "fixtures" / "minimal-corpus.xlsx"

FIXTURE_COLUMNS = {
    "journal_name": "Nom revue",
    "proximity": "Niveau rattachement",
    "open_access": "Accès ouvert",
    "format": "Format",
    "creation_year": "Année de création",
    "periodicity": "Nombre de n°s par an",
    "discipline": "Discipline",
    "publisher_type": "Type d'éditeur",
    "licence": "Licence",
}

FIXTURE_SOURCE = StatisticsSource(
    xlsx=FIXTURE,
    sheet="recensement",
    columns=FIXTURE_COLUMNS,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(
            f"{label}\n"
            f"  attendu : {expected!r}\n"
            f"  obtenu  : {actual!r}"
        )


def nested_dict(value):
    return {key: dict(counter) for key, counter in value.items()}


def main():
    rows = read_rows(FIXTURE_SOURCE)
    data = derive(rows, FIXTURE_SOURCE)

    assert_equal(
        data["total"],
        12,
        "Nombre total de revues",
    )

    assert_equal(
        dict(data["levels"]),
        {1: 3, 2: 3, 3: 3, 4: 3},
        "Niveaux de rattachement",
    )

    assert_equal(
        nested_dict(data["level_access"]),
        {
            1: {"open": 2, "restricted": 1},
            2: {"restricted": 2, "open": 1},
            3: {"open": 2, "restricted": 1},
            4: {"restricted": 2, "open": 1},
        },
        "Accès ouvert par niveau de rattachement",
    )

    assert_equal(
        dict(data["formats"]),
        {
            "Numérique": 4,
            "Papier": 3,
            "Papier et numérique": 5,
        },
        "Formats",
    )

    assert_equal(
        nested_dict(data["format_access"]),
        {
            "Numérique": {"open": 2, "restricted": 2},
            "Papier": {"restricted": 2, "open": 1},
            "Papier et numérique": {"open": 3, "restricted": 2},
        },
        "Accès ouvert par format",
    )

    assert_equal(
        sum(data["years"].values()),
        11,
        "Années de création renseignées",
    )

    assert_equal(
        dict(data["periods"]),
        {
            "18e siècle": 1,
            "XIXe siècle": 1,
            "1900–1924": 1,
            "1925–1949": 1,
            "Années 1950": 1,
            "Années 1960": 1,
            "Années 1970": 1,
            "Années 1980": 1,
            "Années 1990": 1,
            "Années 2000": 1,
            "Années 2010": 1,
        },
        "Périodes de création",
    )

    assert_equal(
        nested_dict(data["date_access"]),
        {
            "Avant 1960": {"open": 3, "restricted": 2},
            "1960–1999": {"restricted": 2, "open": 2},
            "À partir de 2000": {"restricted": 1, "open": 1},
        },
        "Accès ouvert par période de création",
    )

    assert_equal(
        sum(data["periodicities"].values()),
        11,
        "Périodicités renseignées",
    )

    assert_equal(
        dict(data["periodicities"]),
        {
            "Un numéro tous les deux ans": 1,
            "Annuel (1 nᵒ/an)": 2,
            "Semestriel (2 nᵒˢ/an)": 2,
            "Quadrimestriel (3 nᵒˢ/an)": 1,
            "Trimestriel (4 nᵒˢ/an)": 2,
            "Plus de 4 nᵒˢ/an": 1,
            "Parution irrégulière": 1,
            "Parution continue": 1,
        },
        "Périodicités",
    )

    assert_equal(
        dict(data["disciplines"]),
        {
            "Histoire": 1,
            "Archéologie": 2,
            "Économie, gestion, finance, marketing": 2,
            "Droit": 1,
            "Sciences politiques": 1,
            "Sociologie": 1,
            "Anthropologie": 1,
            "Littérature": 1,
            "Information-communication": 1,
            "STM (sciences, technologie, médecine)": 1,
        },
        "Disciplines normalisées",
    )

    assert_equal(
        dict(data["structures"]),
        {
            "Éditeur public": 2,
            "Association": 2,
            "Éditeur privé": 2,
            "Organisme de recherche public": 2,
            "Coédition public/privé": 2,
            "Coédition privé/association": 2,
        },
        "Structures éditoriales",
    )

    assert_equal(
        nested_dict(data["struct_access"]),
        {
            "Éditeur public": {"open": 2},
            "Association": {"restricted": 2},
            "Éditeur privé": {"open": 2},
            "Organisme public de recherche": {"restricted": 2},
            "Coédition éditeur privé & structure publique ou associative": {
                "open": 2,
                "restricted": 2,
            },
        },
        "Accès ouvert par structure éditoriale",
    )

    assert_equal(
        sum(data["rights"].values()),
        11,
        "Droits renseignés",
    )

    assert_equal(
        dict(data["rights"]),
        {
            "Licence Creative Commons": 5,
            "Tous droits réservés": 5,
            "Licence CC ou DR variable pour une même publication": 1,
        },
        "Droits normalisés",
    )

    print("Fixture statistique : OK")
    print("12 revues fictives contrôlées.")
    print("Toutes les dimensions du tableau de bord sont conformes.")


if __name__ == "__main__":
    main()