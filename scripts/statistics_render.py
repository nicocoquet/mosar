import csv
import html
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from statistics_data import rpct
from statistics_publication import downloads_for

BLUES = ["#07558c", "#367fb8", "#67a9df", "#a7d5f5", "#8fc1e8", "#bdddf4", "#4d91c7", "#245f92"]
OPEN = {"open": "#07558c", "restricted": "#a7d5f5"}


def esc(value):
    return html.escape(str(value), quote=True)


def fmt_pct(value, total, lang):
    value = rpct(value, total)
    return f"{value} %" if lang == "fr" else f"{value}%"


def icon(ext):
    """Inline decorative SVG; the format remains accessible HTML text below."""
    shapes = {
        "csv": '<path d="M8 3h19l11 11v31H8z"/><path d="M27 3v11h11"/><path d="M15 23h16M15 29h16M15 35h11"/>',
        "xlsx": '<rect x="8" y="5" width="30" height="39" rx="2"/><path d="M8 17h30M8 27h30M8 37h30M23 17v27"/>',
        "jpg": '<rect x="6" y="7" width="34" height="34" rx="3"/><circle cx="17" cy="17" r="3"/><path d="m9 35 11-11 7 7 5-5 6 9"/>',
        "svg": '<path d="M8 3h19l11 11v31H8z"/><path d="M27 3v11h11"/><circle cx="16" cy="33" r="2"/><circle cx="30" cy="23" r="2"/><circle cx="30" cy="37" r="2"/><path d="M18 32c5-11 10-10 10-9M18 34c5 7 9 5 10 3"/>',
    }
    return (
        '<span class="chart-download-icon" aria-hidden="true">'
        '<svg viewBox="0 0 46 48" focusable="false" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        + shapes[ext] + '</svg></span>'
    )


def actions(chart_id, lang):
    base = "../downloads/" if lang == "fr" else "../../downloads/en/"
    groups = (
        (("Données", ("csv", "xlsx")), ("Graphique", ("jpg", "svg")))
        if lang == "fr" else
        (("Data", ("csv", "xlsx")), ("Chart", ("jpg", "svg")))
    )

    def group(label, formats):
        links = []
        for ext in formats:
            description = (
                ("Télécharger les données" if ext in ("csv", "xlsx") else "Télécharger le graphique")
                if lang == "fr" else
                ("Download data" if ext in ("csv", "xlsx") else "Download chart")
            )
            readable = ext.upper()
            links.append(
                f'<a class="chart-download" href="{base}{chart_id}.{ext}" download '
                f'aria-label="{description} ({readable})" title="{description} ({readable})">'
                f'{icon(ext)}<span class="chart-download-format">{readable}</span></a>'
            )
        return (
            '<div class="chart-actions-row">'
            f'<span class="chart-actions-label">{label} :</span>'
            '<div class="chart-actions-formats">' + "".join(links) + '</div>'
            '</div>'
        )

    return '<div class="chart-actions">' + "".join(group(label, formats) for label, formats in groups) + '</div>'


def pie_legend(labels, values, lang, sort_by_count=True):
    """HTML legend, sorted visually without altering sector positions or colors."""
    total = sum(values)
    items = list(enumerate(zip(labels, values)))
    if sort_by_count:
        items.sort(key=lambda item: -item[1][1])  # stable on ties
    entries = []
    for i, (label, value) in items:
        entries.append(
            f'<span class="chart-legend-item"><span class="chart-legend-swatch" '
            f'style="background:{BLUES[i % len(BLUES)]}" aria-hidden="true"></span>'
            f'<span>{esc(label)} — {value} ({fmt_pct(value, total, lang)})</span></span>'
        )
    return '<div class="chart-legend" role="group" aria-label="' + ('Légende' if lang == 'fr' else 'Legend') + '">' + ''.join(entries) + '</div>'


def stacked_legend(series, lang):
    entries = [
        f'<span class="chart-legend-item"><span class="chart-legend-swatch" '
        f'style="background:{color}" aria-hidden="true"></span><span>{esc(label)}</span></span>'
        for label, key, color in series
    ]
    return '<div class="chart-legend" role="group" aria-label="' + ('Légende' if lang == 'fr' else 'Legend') + '">' + ''.join(entries) + '</div>'


def pie_svg(labels, values, lang):
    total = sum(values)
    cx, cy, radius = 180, 180, 140
    angle = 0
    parts = []
    for i, (label, value) in enumerate(zip(labels, values)):
        sweep = value * 360 / total
        a1 = math.radians(angle - 90)
        a2 = math.radians(angle + sweep - 90)
        x1, y1 = cx + radius * math.cos(a1), cy + radius * math.sin(a1)
        x2, y2 = cx + radius * math.cos(a2), cy + radius * math.sin(a2)
        large = 1 if sweep > 180 else 0
        color = BLUES[i % len(BLUES)]
        parts.append(f'<path d="M {cx},{cy} L {x1:.2f},{y1:.2f} A {radius},{radius} 0 {large},1 {x2:.2f},{y2:.2f} Z" fill="{color}" stroke="#fff" stroke-width="2"/>')
        mid = math.radians(angle + sweep / 2 - 90)
        tx, ty = cx + radius * .62 * math.cos(mid), cy + radius * .62 * math.sin(mid)
        if sweep >= 18:
            parts.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" style="font:700 14px Arial;fill:#08264a"><tspan x="{tx:.1f}">{value}</tspan><tspan x="{tx:.1f}" dy="18">{fmt_pct(value,total,lang)}</tspan></text>')
        angle += sweep

    return f'<svg style="display:block;width:100%;max-width:540px;height:auto" viewBox="0 0 360 360">' + "".join(parts) + "</svg>"


def stacked_svg(categories, series, values, lang, percent=False, average=None):
    width, height, left, right, top, bottom = 900, 520, 70, 30, 30, 145
    plot_width = width - left - right
    plot_height = height - top - bottom
    gap = plot_width / max(len(categories), 1)
    bar_width = min(115, gap * .62)
    max_total = max(sum(values[c].values()) for c in categories) if categories else 1
    parts = []

    for i, category in enumerate(categories):
        x = left + i * gap + (gap - bar_width) / 2
        base = top + plot_height
        total = sum(values[category].values())
        for label, key, color in series:
            value = values[category].get(key, 0)
            height_value = plot_height * (value / total if percent and total else value / max_total)
            y = base - height_value
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{height_value:.1f}" fill="{color}"/>')
            text = fmt_pct(value, total, lang) if percent else str(value)
            if height_value > 25:
                text_color = "#fff" if key == "open" else "#08264a"
                parts.append(f'<text x="{x+bar_width/2:.1f}" y="{y+height_value/2+5:.1f}" text-anchor="middle" style="font:700 14px Arial;fill:{text_color}">{text}</text>')
            base = y
        tx = x + bar_width / 2
        parts.append(f'<text x="{tx:.1f}" y="{top+plot_height+22}" text-anchor="end" transform="rotate(-32 {tx:.1f},{top+plot_height+22})" style="font:13px Arial;fill:#08264a">{esc(category)}</text>')

    parts.append(f'<line x1="{left}" y1="{top+plot_height}" x2="{width-right}" y2="{top+plot_height}" stroke="#dce7f2"/>')
    if average is not None and percent:
        ay = top + plot_height * (1 - average)
        opened = round(average * 100)
        restricted = 100 - opened
        label = (f"Moyenne sur l’ensemble des revues du périmètre ({opened} % en accès ouvert, {restricted} % en accès restreint)" if lang == "fr" else f"Average across all journals in the corpus ({opened}% open access, {restricted}% restricted access)")
        parts.append(f'<line x1="{left}" y1="{ay:.1f}" x2="{width-right}" y2="{ay:.1f}" stroke="#b74f17" stroke-width="2" stroke-dasharray="7 5"/><text x="{left+5}" y="{max(top+14,ay-7):.1f}" style="font:13px Arial;fill:#08264a">{esc(label)}</text>')

    return f'<svg style="display:block;width:100%;max-width:900px;height:auto" viewBox="0 0 {width} {height}">' + "".join(parts) + "</svg>"





def periodicity_display_labels(lang):
    """Ordered presentation labels, independent of source category keys."""
    if lang == "fr":
        return (
            "Plus de 4 nᵒˢ/an", "Trimestriel (4 nᵒˢ/an)",
            "Quadrimestriel (3 nᵒˢ/an)", "Semestriel (2 nᵒˢ/an)",
            "Annuel (1 nᵒ/an)", "Biennal (0,5 nᵒ/an)",
            "Parution continue", "Parution irrégulière",
        )
    return (
        "More than 4 issues/year", "Quarterly (4 issues/year)",
        "Three issues/year", "Semiannual (2 issues/year)",
        "Annual (1 issue/year)", "Biennial (0.5 issue/year)",
        "Continuous publication", "Irregular publication",
    )


def periodicity_legend(lang):
    """Frequency-ordered legend without numerical counts."""
    labels = periodicity_display_labels(lang)
    entries = []
    for i, label in enumerate(labels):
        if lang == "fr":
            label = (esc(label).replace("nᵒˢ", "n<sup>os</sup>")
                     .replace("nᵒ", "n<sup>o</sup>"))
        else:
            label = esc(label)
        entries.append(
            f'<span class="chart-legend-item"><span class="chart-legend-swatch" '
            f'style="background:{BLUES[i]}" aria-hidden="true"></span><span>{label}</span></span>'
        )
    return '<div class="chart-legend" role="group" aria-label="' + ('Légende' if lang == 'fr' else 'Legend') + '">' + ''.join(entries) + '</div>'


def periodicity_treemap_rectangles(values, width=920, height=450):
    """Binary treemap: exact area shares, stable order by size for layout only."""
    items = sorted(enumerate(values), key=lambda pair: (-pair[1], pair[0]))
    result = {}
    def partition(group, x, y, w, h):
        if not group:
            return
        if len(group) == 1:
            result[group[0][0]] = (x, y, w, h)
            return
        total = sum(value for _, value in group)
        if not total:
            return
        half = total / 2
        cut = 1
        running = group[0][1]
        while cut < len(group) - 1 and abs(running + group[cut][1] - half) < abs(running - half):
            running += group[cut][1]
            cut += 1
        share = running / total
        if w >= h:
            partition(group[:cut], x, y, w * share, h)
            partition(group[cut:], x + w * share, y, w * (1 - share), h)
        else:
            partition(group[:cut], x, y, w, h * share)
            partition(group[cut:], x, y + h * share, w, h * (1 - share))
    partition(items, 0, 0, width, height)
    return result


def periodicity_treemap_svg(values, lang):
    labels = periodicity_display_labels(lang)
    total = sum(values)
    width, height = 960, 490
    rects = periodicity_treemap_rectangles(values, 920, 450)
    exact = [100 * v / total if total else 0 for v in values]
    rounded = [math.floor(v) for v in exact]
    for i in sorted(range(len(values)), key=lambda i: (-(exact[i] - rounded[i]), i))[:100 - sum(rounded) if total else 0]:
        rounded[i] += 1
    parts = []
    for i, (label, count) in enumerate(zip(labels, values)):
        if not count or i not in rects:
            continue
        rx, ry, rw, rh = rects[i]
        x, y = rx + 20, ry + 20
        color = BLUES[i]
        detail = f"{label} : {count} revues ({rounded[i]} %)" if lang == "fr" else f"{label}: {count} journals ({rounded[i]}%)"
        parts.append(
            f'<g class="chart-tooltip-target" tabindex="0" role="button" '
            f'aria-label="{esc(detail)}" data-tooltip-label="{esc(label)}" '
            f'data-tooltip-count="{count}" data-tooltip-percent="{rounded[i]}">'
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{rw:.2f}" height="{rh:.2f}" '
            f'fill="{color}" stroke="#fff" stroke-width="4"/>'
        )
        if rw >= 92 and rh >= 58:
            text_color = "#fff" if i in (0, 1, 7) else "#08264a"
            cx, cy = x + rw / 2, y + rh / 2
            parts.append(
                f'<text x="{cx:.2f}" y="{cy-5:.2f}" text-anchor="middle" '
                f'pointer-events="none" style="font:700 20px Arial;fill:{text_color}">'
                f'{rounded[i]} %</text>'
                f'<text x="{cx:.2f}" y="{cy+19:.2f}" text-anchor="middle" '
                f'pointer-events="none" style="font:15px Arial;fill:{text_color}">'
                f'{count} {"revues" if lang == "fr" else "journals"}</text>'
            )
        elif rw >= 50 and rh >= 30:
            parts.append(
                f'<text x="{x+rw/2:.2f}" y="{y+rh/2+5:.2f}" text-anchor="middle" '
                f'pointer-events="none" style="font:700 13px Arial;fill:#08264a">{rounded[i]} %</text>'
            )
        parts.append('</g>')
    description = "Répartition des revues selon leur périodicité de publication" if lang == "fr" else "Distribution of journals by publication frequency"
    return f'<svg aria-label="{esc(description)}" style="display:block;width:100%;max-width:960px;height:auto" viewBox="0 0 {width} {height}">' + "".join(parts) + '</svg>'


def export_jpg_periodicity_treemap(chart_id, values, lang="fr"):
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    total = sum(values)
    exact = [100 * v / total if total else 0 for v in values]
    rounded = [math.floor(v) for v in exact]
    for i in sorted(range(len(values)), key=lambda i: (-(exact[i] - rounded[i]), i))[:100 - sum(rounded) if total else 0]:
        rounded[i] += 1
    rects = periodicity_treemap_rectangles(values, 920, 450)
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    for i, count in enumerate(values):
        if not count or i not in rects:
            continue
        x, y, w, h = rects[i]
        ax.add_patch(Rectangle((x, y), w, h, facecolor=BLUES[i], edgecolor="white", linewidth=3))
        if w >= 92 and h >= 58:
            color = "white" if i in (0, 1, 7) else "#08264a"
            ax.text(x+w/2, y+h/2-10, f"{rounded[i]} %", ha="center", va="center", fontsize=15, color=color, fontweight="bold")
            ax.text(x+w/2, y+h/2+13, f"{count} " + ("revues" if lang == "fr" else "journals"), ha="center", va="center", fontsize=11, color=color)
        elif w >= 50 and h >= 30:
            ax.text(x+w/2, y+h/2, f"{rounded[i]} %", ha="center", va="center", fontsize=10, color="#08264a")
    ax.set_xlim(0, 920)
    ax.set_ylim(450, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=.2)
    fig.savefig(destination / f"{chart_id}.jpg", bbox_inches="tight", facecolor="white")
    plt.close(fig)



def rights_legend(labels, lang):
    """Legend for the three distinct rights categories, without counts."""
    names = (
        ("Licence Creative Commons (CC)", "Tous droits réservés (DR)",
         "Licence variable (CC ou DR)")
        if lang == "fr" else
        ("Creative Commons licence (CC)", "All rights reserved (DR)",
         "Variable licence (CC or all rights reserved)")
    )
    return '<div class="chart-legend" role="group" aria-label="' + ("Légende" if lang == "fr" else "Legend") + '">' + "".join(
        f'<span class="chart-legend-item"><span class="chart-legend-swatch" style="background:{BLUES[i % len(BLUES)]}" aria-hidden="true"></span><span>{esc(name)}</span></span>'
        for i, name in enumerate(names)
    ) + '</div>'


def rights_horizontal_svg(labels, values, lang):
    """Single 100% stacked bar, with native SVG tooltips and keyboard focus."""
    total = sum(values)
    width, height, left, top, bar_width, bar_height = 960, 110, 25, 25, 910, 56
    x = left
    parts = []
    # Largest-remainder rounding: displayed integers sum to exactly 100.
    exact = [100 * v / total if total else 0 for v in values]
    rounded = [math.floor(v) for v in exact]
    remainder = 100 - sum(rounded) if total else 0
    for i in sorted(range(len(values)), key=lambda i: (-(exact[i] - rounded[i]), i))[:remainder]:
        rounded[i] += 1
    for i, (label, value) in enumerate(zip(labels, values)):
        w = bar_width * value / total if total else 0
        color = BLUES[i % len(BLUES)]
        detail = f"{label} : {value} revues ({rounded[i]} %)" if lang == "fr" else f"{label}: {value} journals ({rounded[i]}%)"
        parts.append(f'<g class="chart-tooltip-target" tabindex="0" role="button" aria-label="{esc(detail)}" data-tooltip-label="{esc(label)}" data-tooltip-count="{value}" data-tooltip-percent="{rounded[i]}"><rect x="{x:.2f}" y="{top}" width="{w:.2f}" height="{bar_height}" fill="{color}"/>')
        if w >= 34:
            text_color = "#fff" if i in (0, 2) else "#08264a"
            parts.append(f'<text x="{x+w/2:.2f}" y="{top+bar_height/2+5}" text-anchor="middle" pointer-events="none" style="font:700 14px Arial;fill:{text_color}">{rounded[i]} %</text>')
        parts.append('</g>')
        x += w
    return f'<svg aria-label="{esc("Répartition des droits de réutilisation" if lang == "fr" else "Reuse rights distribution")}" style="display:block;width:100%;max-width:960px;height:auto" viewBox="0 0 {width} {height}">' + "".join(parts) + "</svg>"


def export_jpg_rights_horizontal(chart_id, labels, values, lang="fr"):
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    total = sum(values)
    exact = [100 * v / total if total else 0 for v in values]
    rounded = [math.floor(v) for v in exact]
    remainder = 100 - sum(rounded) if total else 0
    for i in sorted(range(len(values)), key=lambda i: (-(exact[i] - rounded[i]), i))[:remainder]:
        rounded[i] += 1
    fig, ax = plt.subplots(figsize=(10, 2.2), dpi=150)
    x = 0
    for i, (label, value) in enumerate(zip(labels, values)):
        pct = 100 * value / total if total else 0
        ax.barh([0], [pct], left=x, height=.55, color=BLUES[i % len(BLUES)], label=label)
        if pct >= 3.7:
            ax.text(x + pct/2, 0, f"{rounded[i]} %", ha="center", va="center",
                    color="white" if i in (0, 2) else "#08264a", fontweight="bold", fontsize=10)
        x += pct
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.05), fontsize=8, ncol=1)
    fig.tight_layout()
    fig.savefig(destination / f"{chart_id}.jpg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def structure_access_display_lines(category, lang):
    """Presentation-only labels; preserve original category keys and exports."""
    if lang == "fr":
        if category == "Organisme public de recherche":
            return ("Organisme public", "de recherche")
        if category == "Coédition éditeur privé & structure publique ou associative":
            return ("Éditeur privé/", "structure publique", "ou associative")
    return (category,)


def structure_access_horizontal_svg(categories, series, values, lang):
    """100% horizontal stacked bars, ordered by exact open-access rate."""
    width, left, right, top, row_height, bottom = 960, 260, 35, 20, 70, 20
    height = top + row_height * len(categories) + bottom
    plot_width = width - left - right
    parts = []
    for i, category in enumerate(categories):
        y = top + i * row_height
        total = sum(values[category].values())
        open_count = values[category].get("open", 0)
        open_pct = round(100 * open_count / total) if total else 0
        percentages = {"open": open_pct, "restricted": 100 - open_pct}
        lines = structure_access_display_lines(category, lang)
        line_height = 17
        first_y = y + 30 - (len(lines) - 1) * line_height / 2
        tspans = "".join(f'<tspan x="20" y="{first_y+j*line_height:.1f}">{esc(line)}</tspan>' for j, line in enumerate(lines))
        parts.append(f'<text text-anchor="start" style="font:14px Arial;fill:#08264a">{tspans}</text>')
        x = left
        for label, key, color in series:
            count = values[category].get(key, 0)
            segment_width = plot_width * count / total if total else 0
            parts.append(f'<g class="chart-tooltip-target" tabindex="0" role="button" aria-label="{esc(category)} — {esc(label)} : {count} ({percentages[key]} %)" data-tooltip-label="{esc(category)} — {esc(label)}" data-tooltip-count="{count}" data-tooltip-percent="{percentages[key]}"><rect x="{x:.2f}" y="{y+5}" width="{segment_width:.2f}" height="40" fill="{color}"/>')
            if segment_width >= 38:
                color_text = "#fff" if key == "open" else "#08264a"
                parts.append(f'<text x="{x+segment_width/2:.2f}" y="{y+30}" text-anchor="middle" pointer-events="none" style="font:700 14px Arial;fill:{color_text}">{percentages[key]} %</text>')
            parts.append('</g>')
            x += segment_width
    return f'<svg aria-label="{esc("Accès ouvert et restreint par structure éditoriale" if lang == "fr" else "Open and restricted access by editorial structure")}" style="display:block;width:100%;max-width:960px;height:auto" viewBox="0 0 {width} {height}">' + "".join(parts) + "</svg>"


def export_jpg_structure_horizontal(chart_id, categories, series, values, lang="fr"):
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, max(3.5, len(categories) * .8)), dpi=150)
    display_labels = ["\\n".join(structure_access_display_lines(category, lang)) for category in categories]
    lefts = [0.0] * len(categories)
    for label, key, color in series:
        widths = []
        for category in categories:
            total = sum(values[category].values())
            widths.append(100 * values[category].get(key, 0) / total if total else 0)
        bars = ax.barh(display_labels, widths, left=lefts, label=label, color=color, height=.62)
        for i, bar in enumerate(bars):
            if widths[i] >= 6:
                total = sum(values[categories[i]].values())
                open_pct = round(100 * values[categories[i]].get("open", 0) / total) if total else 0
                pct = open_pct if key == "open" else 100 - open_pct
                ax.text(lefts[i] + widths[i] / 2, bar.get_y() + bar.get_height() / 2,
                        f"{pct} %", ha="center", va="center", fontsize=10,
                        color="white" if key == "open" else "#08264a", fontweight="bold")
        lefts = [a+b for a, b in zip(lefts, widths)]
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.legend()
    fig.tight_layout()
    fig.savefig(destination / f"{chart_id}.jpg", facecolor="white", bbox_inches="tight")
    plt.close(fig)


def bar_svg(labels, values):
    width, height, left, right, top, bottom = 960, 430, 55, 25, 25, 95
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = max(values) if values else 1
    gap = plot_width / max(len(labels), 1)
    bar_width = max(5, gap * .68)
    parts = []
    for i, (label, value) in enumerate(zip(labels, values)):
        x = left + i * gap + (gap - bar_width) / 2
        bar_height = plot_height * value / max_value
        y = top + plot_height - bar_height
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{BLUES[i % 4]}"/><text x="{x+bar_width/2:.1f}" y="{max(y-5,12):.1f}" text-anchor="middle" style="font:700 12px Arial;fill:#08264a">{value}</text>')
        if len(labels) <= 15 or i % max(1, math.ceil(len(labels) / 12)) == 0:
            parts.append(f'<text x="{x+bar_width/2:.1f}" y="{top+plot_height+18}" text-anchor="end" transform="rotate(-45 {x+bar_width/2:.1f},{top+plot_height+18})" style="font:12px Arial;fill:#08264a">{esc(label)}</text>')
    return f'<svg style="display:block;width:100%;max-width:960px;height:auto" viewBox="0 0 {width} {height}">' + "".join(parts) + "</svg>"


def export_csv(chart_id, headers, rows, lang="fr"):
    """Export the same tabular data as CSV and as a typed Excel workbook."""
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    rows = list(rows)

    with (destination / f"{chart_id}.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)
        writer.writerows(rows)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Données" if lang == "fr" else "Data"
    sheet.append(list(headers))
    for row in rows:
        sheet.append([_excel_value(value) for value in row])

    header_fill = PatternFill(fill_type="solid", fgColor="08264A")
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = Font(bold=True, color="FFFFFF")
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column in sheet.columns:
        letter = get_column_letter(column[0].column)
        width = min(60, max(12, max(len(str(cell.value or "")) for cell in column) + 2))
        sheet.column_dimensions[letter].width = width
    workbook.save(destination / f"{chart_id}.xlsx")


def _excel_value(value):
    """Keep genuine numbers numeric; leave textual labels unchanged."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return value


def export_svg(chart_id, svg, lang="fr"):
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / f"{chart_id}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1), encoding="utf-8")


def export_jpg_pie(chart_id, labels, values, lang="fr"):
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.pie(values, labels=labels, autopct=lambda p: f"{round(p)}%", colors=[BLUES[i % len(BLUES)] for i in range(len(values))], startangle=90)
    ax.axis("equal")
    fig.savefig(destination / f"{chart_id}.jpg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def export_jpg_bar(chart_id, labels, values, lang="fr"):
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax.bar(range(len(values)), values)
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(destination / f"{chart_id}.jpg", facecolor="white")
    plt.close(fig)


def export_jpg_stacked(chart_id, categories, series, values, percent=False, average=None, lang="fr"):
    destination = downloads_for(lang)
    destination.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    bottom = [0] * len(categories)
    for label, key, color in series:
        ys = []
        for category in categories:
            total = sum(values[category].values())
            ys.append(values[category].get(key, 0) * 100 / total if percent and total else values[category].get(key, 0))
        ax.bar(categories, ys, bottom=bottom, label=label, color=color)
        bottom = [a + b for a, b in zip(bottom, ys)]
    if average is not None and percent:
        ax.axhline(average * 100, linestyle="--")
    ax.legend()
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(destination / f"{chart_id}.jpg", facecolor="white")
    plt.close(fig)
