"""Pipeline de traitement des données de l'explorateur des revues."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from journals_model import build_record
from mosar_model import proximity_sort_key


def build_journals_dataset(
    titles: list[dict],
    themes_by_journal: dict[int, list[str]],
    mosar: dict[int, dict],
    *,
    cluster_id: int,
    mosar_source: str,
    generated_at: datetime | None = None,
) -> tuple[list[dict], dict]:
    """Construire les enregistrements publiables et le rapport de jointure.

    Les données Mir@bel et Mosar sont supposées déjà chargées. Ce traitement
    ne connaît ni leurs modalités d'acquisition ni leur destination de
    publication.
    """

    if generated_at is None:
        generated_at = datetime.now(timezone.utc)

    by_journal: dict[int, dict] = {}
    duplicate_active_titles = Counter()

    for title in titles:
        journal_id = title.get("revueid")

        if not journal_id:
            continue

        journal_id = int(journal_id)
        duplicate_active_titles[journal_id] += 1

        if journal_id in by_journal:
            continue

        by_journal[journal_id] = build_record(
            title,
            themes_by_journal.get(journal_id, []),
            mosar.get(journal_id),
        )

    records = sorted(
        by_journal.values(),
        key=proximity_sort_key,
    )

    cluster_ids = set(by_journal)
    mosar_ids = set(mosar)
    matched_ids = sorted(cluster_ids & mosar_ids)

    report = {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "cluster_id": cluster_id,
        "mirabel_active_titles": len(titles),
        "mirabel_unique_reviews": len(records),
        "mosar_source": mosar_source,
        "mosar_ids": len(mosar_ids),
        "matched_ids": matched_ids,
        "matched_count": len(matched_ids),
        "mirabel_without_mosar_count": len(cluster_ids - mosar_ids),
        "mosar_outside_cluster_ids": sorted(mosar_ids - cluster_ids),
        "duplicate_active_title_review_ids": sorted(
            journal_id
            for journal_id, count in duplicate_active_titles.items()
            if count > 1
        ),
    }

    return records, report