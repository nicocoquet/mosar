from collections import Counter
from pathlib import Path
import math

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "Recensement-revues-stat.xlsx"
SHEET = "recencement"
OUTPUTS = {"fr": ROOT / "docs/statistiques.md", "en": ROOT / "docs/statistiques.en.md"}
BLUES = ["#07558c", "#367fb8", "#67a9df", "#a7d5f5"]

DEFINITIONS = {
    "fr": {
        1: "revues publiées par la MSH Mondes, les Presses universitaires de Nanterre et les Éditions de la Sorbonne",
        2: "revues portées ou hébergées par un laboratoire des universités Paris 1 ou Paris Nanterre",
        3: "revues dont le.a rédacteur.rice en chef est membre des universités Paris 1 ou Paris Nanterre, qui comprennent au moins un.e membre du comité de rédaction restreint (≤ 8) de Paris 1 ou Paris Nanterre ou si la revue est soutenue financièrement par une UR",
        4: "revues dont au moins un.e membre appartient à l’université Paris 1 ou Paris Nanterre (comité de rédaction ou comité scientifique)",
    },
    "en": {
        1: "journals published by MSH Mondes, Presses universitaires de Nanterre or Éditions de la Sorbonne",
        2: "journals hosted or supported by a research unit affiliated with Paris 1 or Paris Nanterre University",
        3: "journals whose editor-in-chief is affiliated with Paris 1 or Paris Nanterre University, which include at least one member from Paris 1 or Paris Nanterre in a small editorial board (≤ 8), or which receive financial support from a research unit",
        4: "journals with at least one member affiliated with Paris 1 or Paris Nanterre University on the editorial or scientific board",
    },
}

TITLES = {
    "fr": "Répartition des revues selon le degré de proximité avec les universités Paris Nanterre, Paris 1 et la MSH Mondes",
    "en": "Distribution of journals by degree of proximity to Paris Nanterre University, Paris 1 University and MSH Mondes",
}


def percent(value, total):
    return value * 100 / total if total else 0


def polar(cx, cy, r, angle):
    a = math.radians(angle - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def sector(cx, cy, r, start, end):
    x1, y1 = polar(cx, cy, r, start)
    x2, y2 = polar(cx, cy, r, end)
    large = 1 if end - start > 180 else 0
    return f"M {cx},{cy} L {x1:.2f},{y1:.2f} A {r},{r} 0 {large},1 {x2:.2f},{y2:.2f} Z"


def read_counts():
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    if SHEET not in wb.sheetnames:
        raise SystemExit(f"Onglet attendu introuvable : {SHEET}")
    ws = wb[SHEET]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    name_col = headers.index("Nom revue")
    level_col = headers.index("Niveau rattachement")
    counts = Counter()
    total = 0
    for row_number, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[name_col] or not str(row[name_col]).strip():
            continue
        total += 1
        try:
            level = int(row[level_col])
        except (TypeError, ValueError):
            raise SystemExit(f"Niveau de rattachement invalide ligne {row_number}")
        if level not in (1, 2, 3, 4):
            raise SystemExit(f"Niveau de rattachement invalide ligne {row_number}: {level}")
        counts[level] += 1
    if sum(counts.values()) != total:
        raise SystemExit("Toutes les revues doivent avoir un niveau de rattachement valide.")
    return {n: counts[n] for n in (1, 2, 3, 4)}, total


def fmt_pct(value, lang):
    text = f"{value:.1f}"
    return (text.replace(".", ",") + " %") if lang == "fr" else (text + "%")


def svg(counts, total, lang):
    cx, cy, r = 285, 285, 220
    current = 0
    label = "Niveau" if lang == "fr" else "Level"
    parts = []
    for i, level in enumerate((1, 2, 3, 4)):
        value = counts[level]
        end = current + percent(value, total) * 3.6
        parts.append(f'<path d="{sector(cx, cy, r, current, end)}" fill="{BLUES[i]}" class="pie-sector"/>')
        tx, ty = polar(cx, cy, r * .62, current + (end-current)/2)
        color = "#fff" if level in (1, 2) else "#08264a"
        parts.append(f'<text x="{tx:.1f}" y="{ty-20:.1f}" text-anchor="middle" class="pie-label" fill="{color}"><tspan x="{tx:.1f}">{label} {level}</tspan><tspan x="{tx:.1f}" dy="28">({value})</tspan><tspan x="{tx:.1f}" dy="28">{fmt_pct(percent(value,total),lang)}</tspan></text>')
        current = end
    combined = counts[1] + counts[2]
    combined_label = "Niveau 1 et 2" if lang == "fr" else "Levels 1 and 2"
    unit = "revues" if lang == "fr" else "journals"
    return f'''<div class="chart-shell">
<svg class="proximity-chart" viewBox="0 0 900 590" role="img" aria-label="{combined_label}">
  <g>{''.join(parts)}</g>
  <path d="M520,110 C548,110 548,135 548,160 C548,190 565,195 575,195 C565,195 548,200 548,230 C548,255 548,280 520,280" class="brace"/>
  <g><rect x="605" y="115" width="250" height="170" rx="12" class="summary-rect"/><text x="730" y="165" text-anchor="middle" class="summary-title">{combined_label}</text><text x="730" y="215" text-anchor="middle" class="summary-value">({combined})</text><text x="730" y="260" text-anchor="middle" class="summary-value">{round(percent(combined,total))} %</text></g>
  <g><rect x="625" y="335" width="210" height="70" rx="10" class="summary-rect"/><text x="730" y="379" text-anchor="middle" class="total-text">Total : {total} {unit}</text></g>
</svg>
</div>'''


def legend(lang):
    title = "Légende des niveaux de proximité" if lang == "fr" else "Proximity level legend"
    label = "Niveau" if lang == "fr" else "Level"
    items = "".join(f'<div class="legend-item"><span class="legend-dot level-{n}"></span><p><strong>{label} {n} :</strong> {DEFINITIONS[lang][n]}</p></div>' for n in (1,2,3,4))
    return f'<section class="level-legend"><h2>{title}</h2>{items}</section>'


def main():
    counts, total = read_counts()
    for lang, output in OUTPUTS.items():
        output.write_text(f"# {TITLES[lang]}\n\n{svg(counts,total,lang)}\n\n{legend(lang)}\n", encoding="utf-8")
    print(f"Corpus : {total} | N1={counts[1]} N2={counts[2]} N3={counts[3]} N4={counts[4]} | N1+N2={counts[1]+counts[2]} ({percent(counts[1]+counts[2], total):.1f} %)")


if __name__ == "__main__":
    main()
