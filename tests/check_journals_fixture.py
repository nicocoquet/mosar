from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from journals_pipeline import build_journals_dataset


GENERATED_AT = datetime(
    2026,
    10,
    7,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


TITLES = [
    {
        "revueid": 101,
        "prefixe": "La",
        "titre": "Revue Alpha",
        "sigle": "RA",
        "issns": [
            {"issn": "1111-1111", "support": "papier"},
            {"issn": "2222-2222", "support": "électronique"},
        ],
        "langues": ["Français", "Anglais"],
        "editeurs": ["Éditeur Alpha"],
        "pays": {"nom": "France"},
        "periodicite": "Semestriel",
        "fraispublication": "Non",
        "labellisation": ["DOAJ"],
        "liensext": [
            ["https://example.org/alpha", "Site de la revue"],
            ["https://example.org/alpha-ddh", "DDH"],
        ],
        "url": "https://example.org/alpha",
        "url_revue_mirabel": "https://reseau-mirabel.info/revue/101",
    },
    {
        "revueid": 102,
        "titre": "Revue Bêta",
        "issns": [
            {"issn": "3333-3333", "support": "electronique"},
        ],
        "langues": ["Français"],
        "editeurs": ["Éditeur Bêta"],
        "payspublication": "Belgique",
        "periodicite": "Annuel",
        "labellisation": [],
        "liensext": [],
        "url": "https://example.org/beta",
    },
    {
        "revueid": 103,
        "titre": "Revue Gamma",
        "issns": [
            {"issn": "4444-4444", "support": "papier"},
        ],
        "langues": ["Anglais"],
        "editeurs": ["Éditeur Gamma"],
        "country": "Italie",
        "periodicite": "",
        "labellisation": ["ERIH PLUS"],
        "liensext": [],
    },
    {
        "revueid": 104,
        "titre": "Revue Delta",
        "issns": [],
        "langues": [],
        "editeurs": [],
        "pays": [{"nom": "France"}, {"nom": "Suisse"}],
        "labellisation": [],
        "liensext": [],
    },
    # Doublon Mir@bel volontaire : le pipeline doit conserver
    # uniquement la première occurrence du revueid 102.
    {
        "revueid": 102,
        "titre": "Revue Bêta — doublon",
        "issns": [],
    },
]


THEMES_BY_JOURNAL = {
    101: ["Archéologie", "Histoire"],
    102: ["Linguistique"],
    103: ["Anthropologie"],
    104: [],
}


MOSAR = {
    101: {
        "niveau_rattachement": "1",
        "acces_ouvert": "Oui",
        "discipline": "Archéologie",
        "type_editeur": "Éditeur public",
        "licence": "CC BY",
    },
    102: {
        "niveau_rattachement": "3",
        "acces_ouvert": "Non",
        "discipline": "Linguistique",
        "type_editeur": "Association",
        "licence": "Tous droits réservés",
    },
    103: {
        "niveau_rattachement": "2",
        "acces_ouvert": "Oui",
        "discipline": "Anthropologie",
        "type_editeur": "Organisme de recherche public",
        "licence": "CC BY-NC",
    },
    # Identifiant Mosar volontairement absent de la grappe Mir@bel.
    999: {
        "niveau_rattachement": "4",
        "acces_ouvert": "Non",
        "discipline": "Histoire",
        "type_editeur": "Éditeur privé",
        "licence": "Tous droits réservés",
    },
}


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(
            f"{label}\n"
            f"  attendu : {expected!r}\n"
            f"  obtenu  : {actual!r}"
        )


def main():
    records, report = build_journals_dataset(
        TITLES,
        THEMES_BY_JOURNAL,
        MOSAR,
        cluster_id=15,
        mosar_source="Fixture Mosar",
        generated_at=GENERATED_AT,
    )

    assert_equal(
        len(records),
        4,
        "Nombre de revues uniques",
    )

    assert_equal(
        [record["mirabel_id"] for record in records],
        [101, 103, 102, 104],
        "Tri des revues par niveau de rattachement Mosar",
    )

    by_id = {
        record["mirabel_id"]: record
        for record in records
    }

    alpha = by_id[101]

    assert_equal(
        alpha["title"],
        "La Revue Alpha",
        "Construction du titre avec préfixe",
    )

    assert_equal(
        alpha["publication_format"],
        "Papier et numérique",
        "Format papier et numérique",
    )

    assert_equal(
        alpha["themes"],
        ["Archéologie", "Histoire"],
        "Thèmes Mir@bel",
    )

    assert_equal(
        alpha["country"],
        "France",
        "Pays sous forme d'objet Mir@bel",
    )

    assert_equal(
        alpha["ddh"],
        {
            "url": "https://example.org/alpha-ddh",
            "label": "DDH",
        },
        "Lien DDH",
    )

    assert_equal(
        alpha["mosar"],
        {
            "proximity_level": "1",
            "open_access": "Accès ouvert",
            "discipline": "Archéologie",
            "editorial_structure": "Éditeur public",
            "licence": "CC BY",
        },
        "Enrichissement Mosar",
    )

    beta = by_id[102]

    assert_equal(
        beta["title"],
        "Revue Bêta",
        "Conservation de la première occurrence d'un revueid dupliqué",
    )

    assert_equal(
        beta["publication_format"],
        "Numérique",
        "Format numérique",
    )

    assert_equal(
        beta["country"],
        "Belgique",
        "Pays via payspublication",
    )

    assert_equal(
        beta["mosar"]["open_access"],
        "Accès restreint",
        "Normalisation de l'accès restreint",
    )

    gamma = by_id[103]

    assert_equal(
        gamma["publication_format"],
        "Papier",
        "Format papier",
    )

    assert_equal(
        gamma["periodicity"],
        None,
        "Périodicité vide",
    )

    assert_equal(
        gamma["mirabel_url"],
        "https://reseau-mirabel.info/revue/103",
        "URL Mir@bel par défaut",
    )

    delta = by_id[104]

    assert_equal(
        delta["country"],
        "France, Suisse",
        "Pays multiples",
    )

    assert_equal(
        delta["publication_format"],
        None,
        "Format inconnu",
    )

    assert_equal(
        delta["mosar"],
        None,
        "Revue Mir@bel sans enrichissement Mosar",
    )

    assert_equal(
        report,
        {
            "generated_at": "2026-10-07T12:00:00+00:00",
            "cluster_id": 15,
            "mirabel_active_titles": 5,
            "mirabel_unique_reviews": 4,
            "mosar_source": "Fixture Mosar",
            "mosar_ids": 4,
            "matched_ids": [101, 102, 103],
            "matched_count": 3,
            "mirabel_without_mosar_count": 1,
            "mosar_outside_cluster_ids": [999],
            "duplicate_active_title_review_ids": [102],
        },
        "Rapport de jointure",
    )

    print("Fixture Revues : OK")
    print("5 titres Mir@bel fictifs, 4 revues uniques contrôlées.")
    print("Jointure, dédoublonnage, normalisations et tri conformes.")


if __name__ == "__main__":
    main()