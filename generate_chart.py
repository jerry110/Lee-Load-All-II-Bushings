#!/usr/bin/env python3
"""Render the sand estimate chart as a self-contained SVG using only Python's standard library."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "lee_sand_bushings_oem_fit" / "bushing_sand_chart.csv"
OUTPUT = ROOT / "docs" / "estimated-sand-mass-vs-bore.svg"

with CSV_PATH.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
points = [(float(r["Bore_mm"]), float(r["Est_Grains"])) for r in rows]
if not points:
    raise SystemExit("No data rows found in the sand chart CSV")

width, height = 1200, 760
left, right, top, bottom = 130, 1140, 125, 610
xmin, xmax, ymin, ymax = 1.0, 13.0, 0.0, 45.0
sx = lambda x: left + (x - xmin) / (xmax - xmin) * (right - left)
sy = lambda y: bottom - (y - ymin) / (ymax - ymin) * (bottom - top)

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
    '<title id="title">Estimated sand mass by bushing bore diameter</title>',
    '<desc id="desc">Scatter plot of 200 bore diameters and corresponding estimated sand masses from the repository CSV. Estimates are for sand only.</desc>',
    '<rect width="100%" height="100%" fill="#ffffff"/>',
    '<g font-family="DejaVu Sans, Arial, sans-serif" fill="#202124">',
    '<text x="600" y="48" text-anchor="middle" font-size="28" font-weight="700">Bore diameter vs. estimated sand mass</text>',
    '<text x="600" y="80" text-anchor="middle" font-size="16" fill="#5f6368">200 bushing estimates from bushing_sand_chart.csv</text>',
]
# Grid and tick labels.
for y in range(0, 46, 5):
    yy = sy(y)
    parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#d9dde3" stroke-width="1"/>')
    parts.append(f'<text x="{left-16}" y="{yy+5:.1f}" text-anchor="end" font-size="14">{y}</text>')
for x in range(2, 13, 2):
    xx = sx(x)
    parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{bottom}" stroke="#edf0f3" stroke-width="1"/>')
    parts.append(f'<text x="{xx:.1f}" y="{bottom+27}" text-anchor="middle" font-size="14">{x}</text>')
parts.extend([
    f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#30343b" stroke-width="2"/>',
    f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#30343b" stroke-width="2"/>',
])
path = " ".join(("M" if i == 0 else "L") + f"{sx(x):.2f},{sy(y):.2f}" for i, (x, y) in enumerate(points))
parts.append(f'<path d="{path}" fill="none" stroke="#1769aa" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
for x, y in points:
    parts.append(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="2.2" fill="#1769aa"/>')
parts.extend([
    f'<text x="{(left+right)/2:.1f}" y="{bottom+65}" text-anchor="middle" font-size="17" font-weight="600">Bore diameter (mm)</text>',
    f'<text x="36" y="{(top+bottom)/2:.1f}" transform="rotate(-90 36 {(top+bottom)/2:.1f})" text-anchor="middle" font-size="17" font-weight="600">Estimated sand mass (grains)</text>',
    '<text x="130" y="725" font-size="14" fill="#8a2d20">Sand estimates only — not propellant measurements or loading data.</text>',
    '</g>',
    '</svg>',
])
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)} using {len(points)} rows")
