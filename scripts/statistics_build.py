from mosar_dashboard import (
    DATE_ACCESS_CATEGORIES,
    FORMAT_CATEGORIES,
    PAGE_TITLES,
    PERIODICITY_CATEGORIES,
    PERIOD_ORDER,
    RIGHTS_CATEGORIES,
    STRUCTURE_ACCESS_ORDER,
    TITLES,
)
from mosar_model import PROX_DEFS, PROXIMITY_LEVELS
from statistics_data import rpct
from statistics_publication import INTRO_FILES
from statistics_translations import translate_categories, translate_headers
from statistics_render import OPEN, actions, bar_svg, export_csv, export_jpg_bar, export_jpg_pie, export_jpg_stacked, export_svg, pie_svg, pie_legend, stacked_svg, stacked_legend


# Rubriques de navigation : ordre identique à celui des graphiques.
# Les libellés courts sont réservés à la table des matières.
STATISTICS_SECTIONS = (
    ("rattachement", {"fr": "Proximité des revues", "en": "Journal proximity"}, (
        ("proximite-revues", "Degrés de proximité", "Degrees of proximity"),
        ("acces-ouvert-rattachement", "Ouverture selon la proximité", "Open access by proximity"),
    )),
    ("formats", {"fr": "Formats de publication", "en": "Publication formats"}, (
        ("format-publication", "Répartition par format", "Distribution by format"),
        ("acces-format-publication", "Ouverture par format", "Open access by format"),
    )),
    ("anciennete", {"fr": "Ancienneté des revues", "en": "Journal age"}, (
        ("annee-creation", "Année de création", "Year founded"),
        ("periode-creation", "Période de création", "Founding period"),
        ("acces-date-creation", "Ouverture par période", "Open access by founding period"),
    )),
    ("edition", {"fr": "Caractéristiques éditoriales", "en": "Editorial characteristics"}, (
        ("periodicite-revues", "Périodicité", "Publication frequency"),
        ("disciplines-revues", "Disciplines", "Disciplines"),
        ("structures-editoriales", "Structures éditoriales", "Publishing organisations"),
        ("acces-structure-editoriale", "Ouverture par structure", "Open access by publishing organisation"),
        ("droits-reutilisation", "Droits de réutilisation", "Reuse rights"),
    )),
)

SHORT_TITLES = {
    chart_id: {"fr": short_fr, "en": short_en}
    for _, _, charts in STATISTICS_SECTIONS
    for chart_id, short_fr, short_en in charts
}


def block(chart_id, svg, lang, extra="", legend_html=""):
    # Markdown dans HTML (md_in_html) permet au titre h3 d'être repris par la ToC.
    short = SHORT_TITLES[chart_id][lang]
    return (
        f'<!-- CHART:{chart_id}:START -->\n'
        '<section class="statistics-card" markdown="1">\n\n'
        f'### {TITLES[chart_id][lang]} {{#{chart_id} .statistics-title data-toc-label="{short}"}}\n\n'
        f'{legend_html}<div class="chart-block"><div class="chart-layout" style="display:block;max-width:960px"><div class="chart-shell">{svg}</div>{extra}</div>{actions(chart_id, lang)}</div>\n\n'
        '</section>\n'
        f'<!-- CHART:{chart_id}:END -->'
    )


def grouped_blocks(blocks, lang):
    """Regroupe les fiches sans changer l'ordre ni les identifiants des graphiques."""
    if len(blocks) != len(SHORT_TITLES):
        raise ValueError(f"Nombre inattendu de graphiques : {len(blocks)}")
    grouped = []
    index = 0
    for section_id, titles, charts in STATISTICS_SECTIONS:
        grouped.append(f'## {titles[lang]} {{#statistiques-{section_id} .statistics-section-title}}')
        for chart_id, _, _ in charts:
            marker = f'<!-- CHART:{chart_id}:START -->'
            if marker not in blocks[index]:
                raise ValueError(f"Ordre inattendu : {chart_id} à la position {index + 1}")
            grouped.append(blocks[index])
            index += 1
    return "\n\n".join(grouped)


def load_intro(lang):
    path = INTRO_FILES[lang]
    if not path.is_file():
        raise SystemExit(
            f"Introduction éditoriale des statistiques introuvable : {path}"
        )
    return path.read_text(encoding="utf-8").strip()


def export_table(chart_id, headers, rows, lang):
    """Traduit les en-têtes CSV ; les lignes sont déjà préparées pour l'affichage."""
    export_csv(chart_id, translate_headers(headers, lang), rows, lang=lang)


def display_grouped(categories, source, lang):
    """Associe les catégories affichées aux effectifs des clés françaises."""
    labels = translate_categories(categories, lang)
    if len(labels) != len(set(labels)):
        raise ValueError(f"Catégories traduites non uniques : {labels!r}")
    return labels, {label: source[category] for category, label in zip(categories, labels)}


def build(data, lang):
    total = data["total"]
    out = []
    series = [
        ("Accès ouvert" if lang == "fr" else "Open access", "open", OPEN["open"]),
        ("Accès restreint" if lang == "fr" else "Restricted access", "restricted", OPEN["restricted"]),
    ]

    labels = [f"Niveau {n}" if lang == "fr" else f"Level {n}" for n in PROXIMITY_LEVELS]
    values = [data["levels"][n] for n in PROXIMITY_LEVELS]
    svg = pie_svg(labels, values, lang)
    export_table("proximite-revues", ["Niveau", "Nombre", "Pourcentage"], [(n, data["levels"][n], rpct(data["levels"][n], total)) for n in PROXIMITY_LEVELS], lang=lang)
    export_svg("proximite-revues", svg, lang=lang)
    export_jpg_pie("proximite-revues", labels, values, lang=lang)
    legend = '<section class="level-legend">' + "".join(
        f'<div class="legend-item"><span class="legend-dot level-{n}"></span><p><strong>{labels[n-1]} :</strong> {PROX_DEFS[lang][n]}</p></div>'
        for n in PROXIMITY_LEVELS
    ) + "</section>"
    out.append(block("proximite-revues", svg, lang, legend, pie_legend(labels, values, lang, sort_by_count=False)))

    categories = labels
    grouped = {categories[i]: data["level_access"][i + 1] for i in range(4)}
    average = sum(x["open"] for x in data["level_access"].values()) / total
    svg = stacked_svg(categories, series, grouped, lang, percent=True, average=average)
    export_table("acces-ouvert-rattachement", ["Niveau", "Accès ouvert", "Accès restreint"], [(i + 1, data["level_access"][i + 1]["open"], data["level_access"][i + 1]["restricted"]) for i in range(4)], lang=lang)
    export_svg("acces-ouvert-rattachement", svg, lang=lang)
    export_jpg_stacked("acces-ouvert-rattachement", categories, series, grouped, percent=True, average=average, lang=lang)
    out.append(block("acces-ouvert-rattachement", svg, lang, legend_html=stacked_legend(series, lang)))

    categories = list(FORMAT_CATEGORIES)
    values = [data["formats"][c] for c in categories]
    labels = translate_categories(categories, lang)
    svg = pie_svg(labels, values, lang)
    export_table("format-publication", ["Format", "Nombre", "Pourcentage"], [(label, data["formats"][c],rpct(data["formats"][c], total)) for c, label in zip(categories, labels)], lang=lang)
    export_svg("format-publication", svg, lang=lang)
    export_jpg_pie("format-publication", labels, values, lang=lang)
    out.append(block("format-publication", svg, lang, legend_html=pie_legend(labels, values, lang)))

    labels, grouped = display_grouped(categories, data["format_access"], lang)
    svg = stacked_svg(labels, series, grouped, lang)
    export_table("acces-format-publication", ["Format", "Accès ouvert", "Accès restreint"], [(label, grouped[label]["open"], grouped[label]["restricted"]) for label in labels], lang=lang)
    export_svg("acces-format-publication", svg, lang=lang)
    export_jpg_stacked("acces-format-publication", labels, series, grouped, lang=lang)
    out.append(block("acces-format-publication", svg, lang, legend_html=stacked_legend(series, lang)))

    years = sorted(data["years"])
    values = [data["years"][y] for y in years]
    svg = bar_svg([str(y) for y in years], values)
    export_table("annee-creation", ["Année", "Nombre"], zip(years, values), lang=lang)
    export_svg("annee-creation", svg, lang=lang)
    export_jpg_bar("annee-creation", [str(y) for y in years], values, lang=lang)
    out.append(block("annee-creation", svg, lang))

    categories = [c for c in [k for k in data["periods"] if k not in PERIOD_ORDER] + list(PERIOD_ORDER) if data["periods"][c]]
    values = [data["periods"][c] for c in categories]
    labels = translate_categories(categories, lang)
    svg = bar_svg(labels, values)
    export_table("periode-creation", ["Période", "Nombre"], zip(labels, values), lang=lang)
    export_svg("periode-creation", svg, lang=lang)
    export_jpg_bar("periode-creation", labels, values, lang=lang)
    out.append(block("periode-creation", svg, lang))

    categories = list(DATE_ACCESS_CATEGORIES)
    labels, grouped = display_grouped(categories, data["date_access"], lang)
    svg = stacked_svg(labels, series, grouped, lang)
    export_table("acces-date-creation", ["Période", "Accès ouvert", "Accès restreint"], [(label, grouped[label]["open"], grouped[label]["restricted"]) for label in labels], lang=lang)
    export_svg("acces-date-creation", svg, lang=lang)
    export_jpg_stacked("acces-date-creation", labels, series, grouped, lang=lang)
    out.append(block("acces-date-creation", svg, lang, legend_html=stacked_legend(series, lang)))

    categories = list(PERIODICITY_CATEGORIES)
    values = [data["periodicities"][c] for c in categories]
    labels = translate_categories(categories, lang)
    svg = pie_svg(labels, values, lang)
    export_table("periodicite-revues", ["Périodicité", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(labels, values)], lang=lang)
    export_svg("periodicite-revues", svg, lang=lang)
    export_jpg_pie("periodicite-revues", labels, values, lang=lang)
    out.append(block("periodicite-revues", svg, lang, legend_html=pie_legend(labels, values, lang)))

    categories = [c for c, _ in data["disciplines"].most_common()]
    values = [data["disciplines"][c] for c in categories]
    labels = translate_categories(categories, lang)
    svg = pie_svg(labels, values, lang)
    export_table("disciplines-revues", ["Discipline", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(labels, values)], lang=lang)
    export_svg("disciplines-revues", svg, lang=lang)
    export_jpg_pie("disciplines-revues", labels, values, lang=lang)
    out.append(block("disciplines-revues", svg, lang, legend_html=pie_legend(labels, values, lang)))

    categories = [c for c, _ in data["structures"].most_common()]
    values = [data["structures"][c] for c in categories]
    labels = translate_categories(categories, lang)
    svg = pie_svg(labels, values, lang)
    export_table("structures-editoriales", ["Structure", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(labels, values)], lang=lang)
    export_svg("structures-editoriales", svg, lang=lang)
    export_jpg_pie("structures-editoriales", labels, values, lang=lang)
    out.append(block("structures-editoriales", svg, lang, legend_html=pie_legend(labels, values, lang)))

    categories = [c for c in STRUCTURE_ACCESS_ORDER if c in data["struct_access"]]
    labels, grouped = display_grouped(categories, data["struct_access"], lang)
    svg = stacked_svg(labels, series, grouped, lang, percent=True)
    export_table("acces-structure-editoriale", ["Structure", "Accès ouvert", "Accès restreint"], [(label, grouped[label]["open"], grouped[label]["restricted"]) for label in labels], lang=lang)
    export_svg("acces-structure-editoriale", svg, lang=lang)
    export_jpg_stacked("acces-structure-editoriale", labels, series, grouped, percent=True, lang=lang)
    out.append(block("acces-structure-editoriale", svg, lang, legend_html=stacked_legend(series, lang)))

    categories = list(RIGHTS_CATEGORIES)
    values = [data["rights"][c] for c in categories]
    labels = translate_categories(categories, lang)
    svg = pie_svg(labels, values, lang)
    export_table("droits-reutilisation", ["Droits", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(labels, values)], lang=lang)
    export_svg("droits-reutilisation", svg, lang=lang)
    export_jpg_pie("droits-reutilisation", labels, values, lang=lang)
    out.append(block("droits-reutilisation", svg, lang, legend_html=pie_legend(labels, values, lang)))

    title = PAGE_TITLES[lang]
    intro = load_intro(lang)

    return (
        f'# {title} {{.statistics-page-title}}\n\n'
        f'<div class="statistics-intro" markdown="1">\n\n'
        f'{intro}\n\n'
        f'</div>\n\n'
        + grouped_blocks(out, lang)
        + "\n"
    )
