#!/usr/bin/env python3
"""Génère une page de test Revues à partir de la grappe Mir@bel Mosar (146).

Le générateur de production reste inchangé : cette surcouche redirige seulement
ses sorties vers des fichiers de test et adapte le texte généré.
"""
from pathlib import Path

import generate_revues_exploration as generator


def main():
    generator.GRAPPE_ID = 146
    generator.OUT_JSON = Path("docs/assets/data/revues-test.json")
    generator.OUT_REPORT = Path("data/revues/join-report-test.json")
    generator.OUT_MD = Path("docs/revues-test.md")

    generator.main()

    page = generator.OUT_MD.read_text(encoding="utf-8")
    page = page.replace(
        "grappe Mir@bel n° 15 « PCP Sciences de l’Antiquité et Archéologie »",
        "grappe Mir@bel n° 146 « Mosar »",
    )
    page = page.replace(
        "https://reseau-mirabel.info/grappe/15/PCP-Sciences-de-l-Antiquite-et-Archeologie",
        "https://reseau-mirabel.info/grappe/146",
    )
    page = page.replace(
        "../assets/data/revues-exploration.json",
        "../assets/data/revues-test.json",
    )
    page = page.replace(
        "# Revues { .page-title-compact }",
        "# Revues — test grappe 146 { .page-title-compact }",
    )
    generator.OUT_MD.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
