"""Hand-author a neofetch-style info card as a self-contained SVG.

The heatmap already carries the GitHub numbers, so this card is for the
things a contribution graph cannot say. Rows fade in on a short stagger
so the panel looks like it is printing.

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


def render():
    css = (
        "  .r{opacity:1}"
        if STATIC
        else (
            "  .r{opacity:0;animation:in .42s ease-out forwards}"
            "  @keyframes in{from{opacity:0;transform:translateX(-8px)}"
            "to{opacity:1;transform:translateX(0)}}"
            "  @media (prefers-reduced-motion:reduce){"
            ".r{animation:none;opacity:1;transform:none}}"
        )
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace,SFMono-Regular,'
        f'Menlo,Consolas,monospace" role="img" aria-label="About {USER}">',
        f"<style>{css}</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" '
        f'fill="none" stroke="{BORDER}"/>',
    ]

    for i, colour in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        parts.append(f'<circle cx="{PAD + i * 18}" cy="26" r="6" fill="{colour}"/>')
    parts.append(
        f'<text class="r" x="{PAD + 62}" y="31" font-size="13" fill="{DIM}">'
        f"{USER}@{HOST} ~ neofetch</text>"
    )

    parts.append(
        f'<text class="r" x="{PAD}" y="66" font-size="15" fill="{ACCENT}" '
        f'style="animation-delay:.1s">{USER}@{HOST}</text>'
    )
    parts.append(
        f'<line class="r" x1="{PAD}" y1="76" x2="{WIDTH - PAD}" y2="76" '
        f'stroke="{BORDER}" style="animation-delay:.14s"/>'
    )

    key_w = max(len(label) for label, _ in ROWS) * 9 + 22
    for i, (label, value) in enumerate(ROWS):
        y = TOP + i * ROW_H
        delay = 0.2 + i * 0.09
        parts.append(
            f'<text class="r" x="{PAD}" y="{y}" font-size="13" fill="{KEY}" '
            f'style="animation-delay:{delay:.2f}s">{esc(label)}</text>'
        )
        parts.append(
            f'<text class="r" x="{PAD + key_w}" y="{y}" font-size="13" fill="{VALUE}" '
            f'style="animation-delay:{delay:.2f}s">{esc(value)}</text>'
        )

    swatch_y = HEIGHT - 26
    delay = 0.2 + len(ROWS) * 0.09
    for i, colour in enumerate(
        ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0")
    ):
        parts.append(
            f'<rect class="r" x="{PAD + i * 20}" y="{swatch_y}" width="15" height="10" '
            f'rx="2" fill="{colour}" style="animation-delay:{delay + i * .04:.2f}s"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    OUT.write_text(render())
    print(f"{OUT.name}: {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
