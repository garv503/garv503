"""Render data/contributions.json as a self-contained animated SVG.

Motion is SMIL, embedded in the file. GitHub strips <script> and external
CSS from READMEs, and CSS keyframes do not run in an SVG loaded through
<img> either -- SMIL does. Every element keeps its default opacity of 1 and
each <animate> carries its own delay, so a renderer that ignores SMIL shows
the finished art instead of a blank panel. The reveal runs once and freezes.
"""

import json
import os
from datetime import date
from pathlib import Path

STATIC = os.environ.get("STATIC") == "1"

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL, GAP, RADIUS = 13, 4, 3
PAD_X, TOP = 34, 54
LABEL_W = 30
FG, DIM, BG = "#c9d1d9", "#7d8590", "#0d1117"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def reveal(delay, fade=0.3):
    """A SMIL fade-in that carries its own delay.

    Elements keep their default opacity of 1, so a renderer that ignores
    SMIL shows the finished art rather than a blank panel. When SMIL does
    run, the element starts hidden and appears at the given delay.
    """
    if STATIC:
        return ""
    if delay <= 0:
        return (
            f'<animate attributeName="opacity" values="0;1" dur="{fade}s" '
            f'fill="freeze"/>'
        )
    total = delay + fade
    return (
        f'<animate attributeName="opacity" values="0;0;1" '
        f'keyTimes="0;{delay / total:.4f};1" dur="{total:.3f}s" fill="freeze"/>'
    )


def build_weeks(days):
    """Group days into columns, Sunday at the top of each column."""
    weeks = []
    column = []
    for day in days:
        weekday = date.fromisoformat(day["date"]).isoweekday() % 7
        if not column:
            column = [None] * weekday
        column.append(day)
        if len(column) == 7:
            weeks.append(column)
            column = []
    if column:
        weeks.append(column + [None] * (7 - len(column)))
    return weeks


def month_labels(weeks):
    labels, seen = [], None
    for index, column in enumerate(weeks):
        first = next((d for d in column if d), None)
        if not first:
            continue
        month = date.fromisoformat(first["date"]).month
        if month != seen:
            labels.append((index, MONTHS[month - 1]))
            seen = month
    return labels


def render(data):
    weeks = build_weeks(data["days"])
    step = CELL + GAP
    grid_w = len(weeks) * step - GAP
    width = PAD_X * 2 + LABEL_W + grid_w
    height = TOP + 7 * step - GAP + 68

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,'
        f'Menlo,Consolas,monospace" role="img" '
        f'aria-label="{data["total"]} contributions in the last year">',
        f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="none" stroke="#30363d"/>',
    ]

    # Title bar, styled like a terminal window.
    for i, colour in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        parts.append(f'<circle cx="{PAD_X + i * 18}" cy="26" r="6" fill="{colour}"/>')
    parts.append(
        f'<text x="{PAD_X + 62}" y="31" font-size="13" fill="{DIM}">'
        f'{reveal(0.05)}{data["username"]}@github ~ contributions</text>'
    )

    grid_x = PAD_X + LABEL_W

    for index, label in month_labels(weeks):
        parts.append(
            f'<text x="{grid_x + index * step}" y="{TOP - 8}" '
            f'font-size="11" fill="{DIM}">{reveal(0.15)}{label}</text>'
        )

    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(
            f'<text x="{PAD_X}" y="{TOP + row * step + 11}" font-size="10" '
            f'fill="{DIM}">{reveal(0.15)}{label}</text>'
        )

    for col, column in enumerate(weeks):
        for row, day in enumerate(column):
            if day is None:
                continue
            level = min(day["level"], 4)
            if day["count"] >= 7:
                level = 5
            delay = (col + row) * 0.012
            parts.append(
                f'<rect x="{grid_x + col * step}" y="{TOP + row * step}" '
                f'width="{CELL}" height="{CELL}" rx="{RADIUS}" fill="{PALETTE[level]}">'
                f'{reveal(delay)}'
                f'<title>{day["count"]} on {day["date"]}</title></rect>'
            )

    footer = TOP + 7 * step + 18
    parts.append(
        f'<text x="{PAD_X}" y="{footer + 12}" font-size="12" fill="{FG}">'
        f'{reveal(1.0)}{data["total"]:,} contributions in the last year'
        f'</text>'
    )
    parts.append(
        f'<text x="{PAD_X}" y="{footer + 31}" font-size="11" fill="{DIM}">'
        f'{reveal(1.1)}current streak {data["current_streak"]}d &#183; '
        f'longest {data["longest_streak"]}d &#183; best day {data["best_day"]["count"]} &#183; '
        f'{data["active_days"]} active days</text>'
    )

    legend_x = width - PAD_X - 6 * 16 - 62
    parts.append(
        f'<text x="{legend_x}" y="{footer + 12}" font-size="11" fill="{DIM}">'
        f'{reveal(1.0)}Less</text>'
    )
    for i, colour in enumerate(PALETTE):
        parts.append(
            f'<rect x="{legend_x + 32 + i * 16}" y="{footer + 2}" width="12" '
            f'height="12" rx="3" fill="{colour}">{reveal(1 + i * .04)}</rect>'
        )
    parts.append(
        f'<text x="{legend_x + 32 + 6 * 16 + 6}" y="{footer + 12}" '
        f'font-size="11" fill="{DIM}">{reveal(1.3)}More</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    data = json.loads(DATA.read_text())
    OUT.write_text(render(data))
    print(f"{OUT.name}: {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
