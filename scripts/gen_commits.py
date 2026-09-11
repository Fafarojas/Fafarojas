"""Builds assets/commits.svg from the real GitHub contribution calendar.

Reads the public contributions endpoint (no token needed) and renders an
animated pixel bar chart: one bar per week for the last 52 weeks.
"""
import datetime as dt
import html as htmllib
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from pixelfont import text_rects, text_width

USER = os.environ.get("GH_USER", "Fafarojas")

VOID = "#0B0713"
GRID = "#241C38"
DIM = "#3A2F58"
MUTED = "#6E6390"
CREAM = "#F2ECFF"

# bottom -> top of each bar
RAMP = ["#4C31B0", "#6D48E0", "#8B6BFF", "#A78BFA", "#C3B0FF", "#8FE9FF", "#9DF4B8", "#FF9EC4"]

W, H = 940, 300
PAD_L, PAD_R = 28, 28
BASE_Y = 232          # bars sit on this line
CELL = 9              # block height
CELL_GAP = 2
MAX_BLOCKS = 14


def fetch_days(user):
    """Return [(date, count)] for the last year, oldest first."""
    url = f"https://github.com/users/{user}/contributions"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (pixel-stats)",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    page = urllib.request.urlopen(req, timeout=45).read().decode("utf-8")

    cells = {}
    for m in re.finditer(r"<td[^>]*?>", page):
        tag = m.group(0)
        date = re.search(r'data-date="([\d-]+)"', tag)
        cid = re.search(r'id="(contribution-day-component-[^"]+)"', tag)
        if date and cid:
            cells[cid.group(1)] = [date.group(1), 0]

    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>', page, re.S):
        key, body = m.group(1), htmllib.unescape(m.group(2))
        if key not in cells:
            continue
        num = re.match(r"\s*(\d[\d,]*)\s+contribution", body)
        cells[key][1] = int(num.group(1).replace(",", "")) if num else 0

    days = sorted(cells.values(), key=lambda r: r[0])
    return [(dt.date.fromisoformat(d), c) for d, c in days]


def weekly(days, weeks=26):
    """Bucket days into ISO weeks (Sunday start), newest `weeks` kept."""
    buckets = []
    cur, total = None, 0
    for d, c in days:
        wk = d - dt.timedelta(days=(d.weekday() + 1) % 7)
        if wk != cur:
            if cur is not None:
                buckets.append((cur, total))
            cur, total = wk, 0
        total += c
    if cur is not None:
        buckets.append((cur, total))
    return buckets[-weeks:]


def streaks(days):
    best = cur = 0
    for _, c in days:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    now = 0
    for _, c in reversed(days):
        if c > 0:
            now += 1
        else:
            break
    return now, best


def build(days):
    bars = weekly(days)
    total = sum(c for _, c in days)
    peak = max((c for _, c in bars), default=0) or 1
    cur_streak, best_streak = streaks(days)
    busiest = max(days, key=lambda r: r[1]) if days else (dt.date.today(), 0)

    n = len(bars)
    avail = W - PAD_L - PAD_R
    slot = avail / n
    bar_w = max(6, int(slot) - 4)

    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" role="img" aria-label="{total} contributions in the last year">'
    )
    p.append(
        """<style>
  @keyframes grow { from{transform:scaleY(0);opacity:0} to{transform:scaleY(1);opacity:1} }
  @keyframes tip  { 0%,100%{opacity:1} 50%{opacity:.45} }
  @keyframes fade { from{opacity:0} to{opacity:1} }
  .blk { animation: grow .34s steps(3,end) both; transform-box: fill-box; transform-origin: bottom }
  .tip { animation: tip 1.6s steps(2,end) infinite }
  .in  { animation: fade .6s ease-out both }
  @media (prefers-reduced-motion: reduce){ .blk,.tip,.in{animation:none} }
</style>"""
    )
    p.append(f'<rect width="{W}" height="{H}" fill="{VOID}"/>')

    # grid
    p.append(f'<g stroke="{GRID}" stroke-width="1" opacity=".5">')
    for x in range(0, W + 1, 20):
        p.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
    for y in range(0, H + 1, 20):
        p.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    p.append("</g>")

    # header
    p.append('<g class="in">')
    p.extend(text_rects("COMMITS", PAD_L, 26, 4, CREAM))
    p.append(
        f'<text x="{PAD_L + text_width("COMMITS", 4) + 16}" y="{26 + 22}" fill="{MUTED}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13">'
        f'ultimos 6 meses / por semana</text>'
    )
    # big total, right aligned
    tw = text_width(str(total), 6)
    p.extend(text_rects(str(total), W - PAD_R - tw, 20, 6, "#C3B0FF"))
    p.append(
        f'<text x="{W - PAD_R}" y="{78}" fill="{MUTED}" text-anchor="end" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">'
        f'contribuicoes no ano</text>'
    )
    p.append("</g>")

    # baseline
    p.append(
        f'<rect x="{PAD_L}" y="{BASE_Y + 4}" width="{W - PAD_L - PAD_R}" height="2" fill="{DIM}"/>'
    )

    # bars
    for i, (wk, count) in enumerate(bars):
        x = PAD_L + i * slot
        blocks = 0 if count == 0 else max(1, round(count / peak * MAX_BLOCKS))
        delay = i * 0.018
        if blocks == 0:
            p.append(
                f'<rect x="{x:.1f}" y="{BASE_Y - 3}" width="{bar_w}" height="3" fill="{DIM}"/>'
            )
            continue
        for b in range(blocks):
            y = BASE_Y - (b + 1) * (CELL + CELL_GAP)
            col = RAMP[min(b * len(RAMP) // MAX_BLOCKS, len(RAMP) - 1)]
            cls = "blk tip" if b == blocks - 1 else "blk"
            p.append(
                f'<rect class="{cls}" x="{x:.1f}" y="{y}" width="{bar_w}" height="{CELL}" '
                f'fill="{col}" style="animation-delay:{delay:.2f}s"/>'
            )

    # month ruler
    seen = set()
    for i, (wk, _) in enumerate(bars):
        label = wk.strftime("%b").upper()
        if wk.month in seen or wk.day > 7:
            continue
        seen.add(wk.month)
        p.extend(text_rects(label, PAD_L + i * slot, BASE_Y + 16, 2, MUTED))

    # footer stats
    fy = H - 26
    items = [
        ("STREAK", f"{cur_streak}D", "#9DF4B8"),
        ("RECORDE", f"{best_streak}D", "#8FE9FF"),
        ("PICO", f"{busiest[1]}", "#FF9EC4"),
    ]
    fx = PAD_L
    for label, value, col in items:
        p.extend(text_rects(label, fx, fy, 2, MUTED))
        lw = text_width(label, 2)
        p.extend(text_rects(value, fx + lw + 10, fy - 2, 3, col))
        fx += lw + text_width(value, 3) + 46

    # legend
    lx = W - PAD_R - 8 * 12
    p.append(
        f'<text x="{lx - 12}" y="{fy + 10}" fill="{MUTED}" text-anchor="end" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">'
        f'menos</text>'
    )
    for i, col in enumerate(RAMP):
        p.append(f'<rect x="{lx + i * 12}" y="{fy}" width="9" height="9" fill="{col}"/>')
    p.append(
        f'<text x="{W - PAD_R}" y="{fy + 10}" fill="{MUTED}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" '
        f'text-anchor="end">    mais</text>'
    )

    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    out = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets", "commits.svg")
    )
    try:
        days = fetch_days(USER)
        if not days:
            raise RuntimeError("empty contribution calendar")
    except Exception as exc:  # keep the previous SVG rather than shipping a broken one
        print(f"skip: could not read contributions ({exc})")
        sys.exit(0)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build(days))
    print(f"wrote commits.svg ({sum(c for _, c in days)} contributions)")
