"""Hand-author a neofetch-style info card as a self-contained SVG.

The heatmap already carries the GitHub numbers, so this card is for the
things a contribution graph cannot say. Rows fade in on a short stagger
so the panel looks like it is printing.

Motion is SMIL rather than CSS keyframes, which do not run in an SVG that
GitHub loads through <img>. Elements keep their default opacity of 1, so
a renderer without SMIL shows the finished card instead of a blank panel.

STATIC=1 emits a frozen frame for local previews.
"""

import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

USER, HOST = "garv503", "github"

# (label, value) - keep values short enough to stay on one line.
ROWS = [
    ("Name", "Garv Bhargava"),
    ("Now", "SpeakQL"),
    ("Prev", "Foresight / Inkwell / Shivam Garments"),
    ("Stack", "Python / SQL / Flask / React / Docker"),
    ("Focus", "Backend and data-heavy interfaces"),
    ("Habit", "Ships coursework like production"),
]

BG, BORDER = "#0d1117", "#30363d"
KEY, VALUE, DIM, ACCENT = "#69f0a0", "#c9d1d9", "#7d8590", "#39d353"

PAD, ROW_H, TOP = 30, 30, 92
WIDTH = 620
HEIGHT = TOP + len(ROWS) * ROW_H + 46


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def reveal(delay, fade=0.35):
    """SMIL fade-in carrying its own delay; default opacity stays 1."""
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


def render():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace,SFMono-Regular,'
        f'Menlo,Consolas,monospace" role="img" aria-label="About {USER}">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" '
        f'fill="none" stroke="{BORDER}"/>',
    ]

    for i, colour in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        parts.append(f'<circle cx="{PAD + i * 18}" cy="26" r="6" fill="{colour}"/>')
    parts.append(
        f'<text x="{PAD + 62}" y="31" font-size="13" fill="{DIM}">'
        f'{reveal(0.05)}{USER}@{HOST} ~ neofetch</text>'
    )

    parts.append(
        f'<text x="{PAD}" y="66" font-size="15" fill="{ACCENT}">'
        f'{reveal(0.1)}{USER}@{HOST}</text>'
    )
    parts.append(
        f'<line x1="{PAD}" y1="76" x2="{WIDTH - PAD}" y2="76" '
        f'stroke="{BORDER}">{reveal(0.14)}</line>'
    )

    key_w = max(len(label) for label, _ in ROWS) * 9 + 22
    for i, (label, value) in enumerate(ROWS):
        y = TOP + i * ROW_H
        delay = 0.2 + i * 0.09
        parts.append(
            f'<text x="{PAD}" y="{y}" font-size="13" fill="{KEY}">'
            f'{reveal(delay)}{esc(label)}</text>'
        )
        parts.append(
            f'<text x="{PAD + key_w}" y="{y}" font-size="13" fill="{VALUE}">'
            f'{reveal(delay)}{esc(value)}</text>'
        )

    swatch_y = HEIGHT - 26
    delay = 0.2 + len(ROWS) * 0.09
    for i, colour in enumerate(
        ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0")
    ):
        parts.append(
            f'<rect x="{PAD + i * 20}" y="{swatch_y}" width="15" height="10" '
            f'rx="2" fill="{colour}">{reveal(delay + i * .04)}</rect>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    OUT.write_text(render())
    print(f"{OUT.name}: {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
