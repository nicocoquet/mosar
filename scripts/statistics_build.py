from statistics_data import INTRO, OUTPUTS, PROX_DEFS, TITLES, rpct
from statistics_render import OPEN, actions, bar_svg, export_csv, export_jpg_bar, export_jpg_pie, export_jpg_stacked, export_svg, pie_svg, stacked_svg


def block(chart_id, svg, lang, extra=""):
    return (
        f'<!-- CHART:{chart_id}:START -->\n'
        f'## {TITLES[chart_id][lang]} {{.statistics-title}}\n\n'
        f'<div class="chart-block"><div class="chart-layout" style="display:block;max-width:960px"><div class="chart-shell">{svg}</div>{extra}</div>{actions(chart_id, lang)}</div>\n'
        f'<!-- CHART:{chart_id}:END -->'
    )


def build(data, lang):
    total = data["total"]
    out = []
    series = [
        ("Accès ouvert" if lang == "fr" else "Open access", "open", OPEN["open"]),
        ("Accès restreint" if lang == "fr" else "Restricted access", "restricted", OPEN["restricted"]),
    ]

    labels = [f"Niveau {n}" if lang == "fr" else f"Level {n}" for n in (1, 2, 3, 4)]
    values = [data["levels"][n] for n in (1, 2, 3, 4)]
    svg = pie_svg(labels, values, lang)
    export_csv("proximite-revues", ["Niveau", "Nombre", "Pourcentage"], [(n, data["levels"][n], rpct(data["levels"][n], total)) for n in (1, 2, 3, 4)])
    export_svg("proximite-revues", svg)
    export_jpg_pie("proximite-revues", labels, values)
    legend = '<section class="level-legend">' + "".join(
        f'<div class="legend-item"><span class="legend-dot level-{n}"></span><p><strong>{labels[n-1]} :</strong> {PROX_DEFS[lang][n]}</p></div>'
        for n in (1, 2, 3, 4)
    ) + "</section>"
    out.append(block("proximite-revues", svg, lang, legend))

    categories = labels
    grouped = {categories[i]: data["level_access"][i + 1] for i in range(4)}
    average = sum(x["open"] for x in data["level_access"].values()) / total
    svg = stacked_svg(categories, series, grouped, lang, percent=True, average=average)
    export_csv("acces-ouvert-rattachement", ["Niveau", "Accès ouvert", "Accès restreint"], [(i + 1, data["level_access"][i + 1]["open"], data["level_access"][i + 1]["restricted"]) for i in range(4)])
    export_svg("acces-ouvert-rattachement", svg)
    export_jpg_stacked("acces-ouvert-rattachement", categories, series, grouped, percent=True, average=average)
    out.append(block("acces-ouvert-rattachement", svg, lang))

    categories = ["Numérique", "Papier", "Papier et numérique"]
    values = [data["formats"][c] for c in categories]
    svg = pie_svg(categories, values, lang)
    export_csv("format-publication", ["Format", "Nombre", "Pourcentage"], [(c, data["formats"][c], rpct(data["formats"][c], total)) for c in categories])
    export_svg("format-publication", svg)
    export_jpg_pie("format-publication", categories, values)
    out.append(block("format-publication", svg, lang))

    grouped = {c: data["format_access"][c] for c in categories}
    svg = stacked_svg(categories, series, grouped, lang)
    export_csv("acces-format-publication", ["Format", "Accès ouvert", "Accès restreint"], [(c, grouped[c]["open"], grouped[c]["restricted"]) for c in categories])
    export_svg("acces-format-publication", svg)
    export_jpg_stacked("acces-format-publication", categories, series, grouped)
    out.append(block("acces-format-publication", svg, lang))

    years = sorted(data["years"])
    values = [data["years"][y] for y in years]
    svg = bar_svg([str(y) for y in years], values)
    export_csv("annee-creation", ["Année", "Nombre"], zip(years, values))
    export_svg("annee-creation", svg)
    export_jpg_bar("annee-creation", [str(y) for y in years], values)
    out.append(block("annee-creation", svg, lang))

    period_order = ["XIXe siècle", "1900–1924", "1925–1949", "Années 1950", "Années 1960", "Années 1970", "Années 1980", "Années 1990", "Années 2000", "Années 2010", "Années 2020"]
    categories = [c for c in [k for k in data["periods"] if k not in period_order] + period_order if data["periods"][c]]
    values = [data["periods"][c] for c in categories]
    svg = bar_svg(categories, values)
    export_csv("periode-creation", ["Période", "Nombre"], zip(categories, values))
    export_svg("periode-creation", svg)
    export_jpg_bar("periode-creation", categories, values)
    out.append(block("periode-creation", svg, lang))

    categories = ["Avant 1960", "1960–1999", "À partir de 2000"]
    grouped = {c: data["date_access"][c] for c in categories}
    svg = stacked_svg(categories, series, grouped, lang)
    export_csv("acces-date-creation", ["Période", "Accès ouvert", "Accès restreint"], [(c, grouped[c]["open"], grouped[c]["restricted"]) for c in categories])
    export_svg("acces-date-creation", svg)
    export_jpg_stacked("acces-date-creation", categories, series, grouped)
    out.append(block("acces-date-creation", svg, lang))

    categories = [
        "Un numéro tous les deux ans", "Annuel (1 nᵒ/an)", "Semestriel (2 nᵒˢ/an)", "Quadrimestriel (3 nᵒˢ/an)",
        "Trimestriel (4 nᵒˢ/an)", "Plus de 4 nᵒˢ/an", "Parution irrégulière", "Parution continue",
    ]
    values = [data["periodicities"][c] for c in categories]
    svg = pie_svg(categories, values, lang)
    export_csv("periodicite-revues", ["Périodicité", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(categories, values)])
    export_svg("periodicite-revues", svg)
    export_jpg_pie("periodicite-revues", categories, values)
    out.append(block("periodicite-revues", svg, lang))

    categories = [c for c, _ in data["disciplines"].most_common()]
    values = [data["disciplines"][c] for c in categories]
    svg = pie_svg(categories, values, lang)
    export_csv("disciplines-revues", ["Discipline", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(categories, values)])
    export_svg("disciplines-revues", svg)
    export_jpg_pie("disciplines-revues", categories, values)
    out.append(block("disciplines-revues", svg, lang))

    categories = [c for c, _ in data["structures"].most_common()]
    values = [data["structures"][c] for c in categories]
    svg = pie_svg(categories, values, lang)
    export_csv("structures-editoriales", ["Structure", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(categories, values)])
    export_svg("structures-editoriales", svg)
    export_jpg_pie("structures-editoriales", categories, values)
    out.append(block("structures-editoriales", svg, lang))

    structure_order = ["Éditeur privé", "Éditeur public", "Organisme public de recherche", "Association", "Coédition éditeur privé & structure publique ou associative"]
    categories = [c for c in structure_order if c in data["struct_access"]]
    grouped = {c: data["struct_access"][c] for c in categories}
    svg = stacked_svg(categories, series, grouped, lang, percent=True)
    export_csv("acces-structure-editoriale", ["Structure", "Accès ouvert", "Accès restreint"], [(c, grouped[c]["open"], grouped[c]["restricted"]) for c in categories])
    export_svg("acces-structure-editoriale", svg)
    export_jpg_stacked("acces-structure-editoriale", categories, series, grouped, percent=True)
    out.append(block("acces-structure-editoriale", svg, lang))

    categories = ["Licence Creative Commons", "Tous droits réservés", "Licence CC ou DR variable pour une même publication"]
    values = [data["rights"][c] for c in categories]
    svg = pie_svg(categories, values, lang)
    export_csv("droits-reutilisation", ["Droits", "Nombre", "Pourcentage"], [(c, x, rpct(x, total)) for c, x in zip(categories, values)])
    export_svg("droits-reutilisation", svg)
    export_jpg_pie("droits-reutilisation", categories, values)
    out.append(block("droits-reutilisation", svg, lang))

    title = "Statistiques" if lang == "fr" else "Statistics"
    return f'# {title} {{.statistics-page-title}}\n\n<div class="statistics-intro"><p>{INTRO[lang]}</p></div>\n\n' + "\n\n".join(out) + "\n"
