"""Tests de non-régression du traitement statistique Mosar."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts"),
)

from statistics_data import (
    ALLOWED_STRUCTURES, DISCIPLINE_MAP, FORMAT_MAP, PROXIMITY_LEVELS,
    derive, periodicity, year, creation_quantiles,
)


class StatisticsDataTests(unittest.TestCase):

    def test_quantiles_preserve_same_year_and_totals(self):
        from collections import Counter
        years = {
            1900: Counter(open=3, restricted=1),
            1901: Counter(open=2),
            1950: Counter(restricted=5),
            1980: Counter(open=4),
            2000: Counter(restricted=3),
            2020: Counter(open=2),
        }
        groups = creation_quantiles(years, groups=4)
        self.assertEqual(len(groups), 4)
        self.assertEqual(sum(sum(v.values()) for _, _, v in groups), 20)
        self.assertEqual(groups[0][0], 1900)
        self.assertEqual(groups[-1][1], 2020)
        self.assertTrue(all(groups[i][1] < groups[i+1][0] for i in range(3)))

    def test_quantiles_with_fewer_distinct_years(self):
        from collections import Counter
        groups = creation_quantiles({1990: Counter(open=3), 2000: Counter(restricted=2)})
        self.assertEqual(len(groups), 2)

    def test_year_unknown(self):
        """Les années absentes ou inconnues ne sont pas bloquantes."""
        for value in (None, "", "?"):
            with self.subTest(value=value):
                self.assertIsNone(year(value, 93))

    def test_year_valid(self):
        """Les années connues sont correctement interprétées."""
        self.assertEqual(year(2012, 90), 2012)
        self.assertEqual(year("1978", 95), 1978)

    def test_year_invalid(self):
        """Les autres valeurs incorrectes restent rejetées."""
        with self.assertRaisesRegex(SystemExit, "Année de création invalide"):
            year("inconnue", 93)

        with self.assertRaisesRegex(SystemExit, "Année de création hors plage"):
            year(1499, 93)

    def test_periodicity_invalid(self):
        """Une périodicité incorrecte reste rejetée."""
        with self.assertRaisesRegex(SystemExit, "Périodicité invalide"):
            periodicity("inconnue", 93)

    def test_unknown_year_and_periodicity_in_derive(self):
        """Une revue avec deux valeurs inconnues reste comptabilisée.

        Test autonome : aucune dépendance au classeur publié ni à /tmp.
        """
        columns = {
            "open_access": "Accès ouvert",
            "proximity": "Rattachement",
            "format": "Format",
            "creation_year": "Année de création",
            "periodicity": "Périodicité",
            "discipline": "Discipline",
            "publisher_type": "Type d'éditeur",
            "licence": "Licence",
        }
        source = SimpleNamespace(columns=columns)
        row = {
            "_row": 93,
            columns["open_access"]: "oui",
            columns["proximity"]: next(iter(PROXIMITY_LEVELS)),
            columns["format"]: next(iter(FORMAT_MAP)),
            columns["creation_year"]: "?",
            columns["periodicity"]: "?",
            columns["discipline"]: next(iter(DISCIPLINE_MAP)),
            columns["publisher_type"]: sorted(ALLOWED_STRUCTURES)[0],
            columns["licence"]: None,
        }

        data = derive([row], source)

        self.assertEqual(data["total"], 1)
        self.assertEqual(sum(data["years"].values()), 0)
        self.assertEqual(sum(data["periodicities"].values()), 0)
        for key in ("levels", "formats", "disciplines", "structures"):
            with self.subTest(counter=key):
                self.assertEqual(sum(data[key].values()), 1)


if __name__ == "__main__":
    unittest.main()