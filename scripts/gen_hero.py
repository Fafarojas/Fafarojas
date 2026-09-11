"""Builds assets/hero.svg - animated pixel banner."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixelfont import text_rects, text_width

VOID = "#0B0713"
PANEL = "#14101F"
GRID = "#241C38"
VIOLET = "#7C5CFF"
LILAC = "#A78BFA"
LAV = "#C3B0FF"
MINT = "#9DF4B8"
CYAN = "#8FE9FF"
PINK = "#FF9EC4"
PEACH = "#FFC48A"
CREAM = "#F2ECFF"
MUTED = "#6E6390"

PALETTE = {
    "K": "#0B0713",
    "P": VIOLET,
    "p": LILAC,
    "M": MINT,
    "C": CYAN,
    "N": PINK,
    "W": CREAM,
    "Y": PEACH,
}

# 24 x 20 pixel mascot: a cyber-moth creature
SPRITE = [
    "....NN............MM....",
    "...NNNN..........MMMM...",
    "....NN............MM....",
    ".....P............P.....",
    "......P..........P......",
    ".......KKKKKKKKKK.......",
    "......KpWWpppppppK......",
    ".....KpWppppppppppK.....",
    "....KpWWWWppppWWWWpK....",
    "....KpWKKWppppWKKWpK....",
    "....KpWWWWppppWWWWpK....",
    "....KpNNppppppppNNpK....",
    "....KpppppMMMMpppppK....",
    ".....KYCCCCCCCCCCYK.....",
    ".....KYCCCCCCCCCCYK.....",
    "......KMMMMMMMMMMK......",
    ".......KKKKKKKKKK.......",
    ".....KppK......KppK.....",
    ".....KMMK......KMMK.....",
    ".....KKKK......KKKK.....",
]

W, H = 1000, 340
PX = 9  # mascot pixel size


def sprite_rects(ox, oy):
    out = []
    for ry, row in enumerate(SPRITE):
        for rx, ch in enumerate(row):
            if ch == ".":
                continue
            out.append(
                f'<rect x="{ox + rx * PX}" y="{oy + ry * PX}" width="{PX}" height="{PX}" '
                f'fill="{PALETTE[ch]}"/>'
            )
    return out


def blink_rects(ox, oy):
    """Dark lids covering the eye block (rows 8-10, cols 5-18)."""
    out = []
    for ry in (8, 9, 10):
        for rx in range(5, 19):
            if SPRITE[ry][rx] == ".":
                continue
            out.append(
                f'<rect x="{ox + rx * PX}" y="{oy + ry * PX}" width="{PX}" height="{PX}" '
                f'fill="{LILAC}"/>'
            )
    return out


def dither_band(y, rows, cols, cell, colors, seed, invert=False):
    """Pixel dissolve band like an 8-bit gradient edge."""
    rnd = random.Random(seed)
    out = []
    for r in range(rows):
        # probability of a filled cell fades across the band
        p = (r + 1) / (rows + 1)
        if invert:
            p = 1 - p
        for c in range(cols):
            if rnd.random() < p * 0.55:
                col = colors[rnd.randrange(len(colors))]
                out.append(
                    f'<rect x="{c * cell}" y="{y + r * cell}" width="{cell}" height="{cell}" '
                    f'fill="{col}"/>'
                )
    return out


def build():
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Fabricio Rojas - full stack developer">'
    )

    parts.append(
        """<style>
  @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }
  @keyframes blink { 0%,92%,100%{opacity:0} 94%,97%{opacity:1} }
  @keyframes pulse { 0%,100%{opacity:.35} 50%{opacity:1} }
  @keyframes twinkle { 0%,100%{opacity:0} 45%,55%{opacity:1} }
  @keyframes sweep { 0%{transform:translateX(-40px)} 100%{transform:translateX(1040px)} }
  @keyframes typein { from{opacity:0} to{opacity:1} }
  .bob   { animation: float 3.6s steps(4,end) infinite; transform-origin:center }
  .lid   { animation: blink 5.2s steps(1,end) infinite }
  .glow  { animation: pulse 2.4s ease-in-out infinite }
  .star  { animation: twinkle 3s steps(1,end) infinite }
  .scan  { animation: sweep 7s linear infinite }
  .name  { animation: typein .5s steps(2,end) both }
  @media (prefers-reduced-motion: reduce){
    .bob,.lid,.glow,.star,.scan,.name{animation:none}
    .lid{opacity:0}
  }
</style>"""
    )

    # background
    parts.append(f'<rect width="{W}" height="{H}" fill="{VOID}"/>')

    # faint grid
    parts.append(f'<g stroke="{GRID}" stroke-width="1" opacity=".45">')
    for x in range(0, W + 1, 25):
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
    for y in range(0, H + 1, 25):
        parts.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    parts.append("</g>")

    # twinkling stars
    rnd = random.Random(7)
    for i in range(46):
        sx, sy = rnd.randrange(0, W, 5), rnd.randrange(0, H, 5)
        col = rnd.choice([LAV, CYAN, MINT, PINK])
        parts.append(
            f'<rect class="star" x="{sx}" y="{sy}" width="5" height="5" fill="{col}" '
            f'opacity="0" style="animation-delay:{rnd.random()*3:.2f}s"/>'
        )

    # top dither band
    parts.extend(dither_band(0, 5, W // 10, 10, [VIOLET, LILAC, GRID], 21, invert=True))
    # bottom dither band
    parts.extend(dither_band(H - 50, 5, W // 10, 10, [VIOLET, LAV, MINT], 42))

    # scanline sweep
    parts.append(
        f'<rect class="scan" x="0" y="0" width="3" height="{H}" fill="{LAV}" opacity=".2"/>'
    )

    # ---- left block: name ----
    nx, ny = 70, 120
    parts.append(f'<g class="name">')
    # shadow layer for chunky depth
    parts.extend(text_rects("FABRICIO", nx + 4, ny + 4, 6, "#2A1F4D"))
    parts.extend(text_rects("FABRICIO", nx, ny, 6, CREAM))
    parts.extend(text_rects("ROJAS", nx + 4, ny + 60, 6, "#2A1F4D"))
    parts.extend(text_rects("ROJAS", nx, ny + 56, 6, LAV))
    parts.append("</g>")

    # subtitle in mono
    parts.append(
        f'<text x="{nx}" y="{ny - 26}" fill="{MUTED}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="15" letter-spacing="3">full stack developer</text>'
    )

    # small pixel tags
    tags = [("NEXT.JS", LAV), ("NODE", MINT), ("TYPESCRIPT", CYAN)]
    tx = nx
    for label, col in tags:
        tw = text_width(label, 3) + 16
        parts.append(
            f'<rect x="{tx}" y="{ny + 132}" width="{tw}" height="24" fill="{col}"/>'
        )
        parts.extend(text_rects(label, tx + 8, ny + 139, 3, VOID))
        tx += tw + 10

    # ---- right block: mascot ----
    mx, my = 706, 80
    parts.append('<g class="bob">')
    # pixel halo behind each antenna orb
    halo = [(-1, 0), (2, 0), (-1, 1), (2, 1), (0, -1), (1, -1), (0, 2), (1, 2)]
    for ocx, gcol in ((4, PINK), (18, MINT)):
        for dx, dy in halo:
            parts.append(
                f'<rect class="glow" x="{mx + (ocx + dx) * PX}" y="{mx * 0 + my + dy * PX}" '
                f'width="{PX}" height="{PX}" fill="{gcol}" opacity=".22"/>'
            )
    # ground shadow
    parts.append(
        f'<rect x="{mx + 5 * PX}" y="{my + 20 * PX + 8}" width="{14 * PX}" height="{PX}" '
        f'fill="{VIOLET}" opacity=".25"/>'
    )
    parts.extend(sprite_rects(mx, my))
    parts.append(f'<g class="lid" opacity="0">')
    parts.extend(blink_rects(mx, my))
    parts.append("</g>")
    # antenna glow
    parts.append("</g>")

    # sparkle pixels orbiting the mascot
    srnd = random.Random(11)
    for i in range(10):
        ang = i / 10
        sx = mx - 30 + srnd.randrange(0, 24 * PX + 60, PX)
        sy = my - 20 + srnd.randrange(0, 20 * PX + 40, PX)
        col = srnd.choice([PINK, MINT, CYAN, PEACH, LAV])
        parts.append(
            f'<rect class="star" x="{sx}" y="{sy}" width="{PX//2}" height="{PX//2}" '
            f'fill="{col}" opacity="0" style="animation-delay:{ang*3:.2f}s"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "hero.svg")
    with open(os.path.abspath(out), "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote hero.svg")
