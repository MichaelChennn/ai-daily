"""What the diagram generators share: the #43 design-system tokens, the node and arrow drawing, the page.

The values are copied from web/src/styles/press.css (docs/design-system.md); change them there and here
together. Colors are CSS variables, so one page follows the system's day or night mode, and
`?theme=dark` / `?theme=light` forces one (screenshot.py uses `--theme`).
"""

import argparse
from dataclasses import dataclass, field

DAY = {
    "paper": "#E8EBE3",
    "card": "#F5F7F2",
    "ink": "#161A15",
    "ink-2": "#333A31",
    "muted": "#626A5E",
    "line": "rgba(22,26,21,.10)",
    "chip": "#D9DED2",
    "shade": "rgba(22,26,21,.13)",
}
NIGHT = {
    "paper": "#16171A",
    "card": "#202226",
    "ink": "#EDEBE6",
    "ink-2": "#C9C6BF",
    "muted": "#8E8B85",
    "line": "rgba(237,235,230,.12)",
    "chip": "#2E3035",
    "shade": "rgba(0,0,0,.45)",
}
FONTS = (
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600"
    "&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600"
    "&family=Noto+Serif+SC:wght@700&display=swap"
)
RADIUS = 12  # --r-card


def args(doc: str) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=doc.splitlines()[0])
    p.add_argument("--lang", choices=["zh", "en"], default="zh")
    p.add_argument("out")
    return p.parse_args()


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width(s: str, px: float = 12) -> float:
    """Rough width of a label: Han characters are square, Latin runs about 0.52 em in Inter."""
    return sum(px if "⺀" <= ch <= "鿿" or "＀" <= ch <= "￯" else px * 0.52 for ch in s)


def v(role: str) -> str:
    return f"var(--{role})"


@dataclass
class Svg:
    slug: str
    out: list[str] = field(default_factory=list)

    def add(self, s: str) -> None:
        self.out.append(s)

    def take(self) -> str:
        s = "\n".join(self.out)
        self.out.clear()
        return s

    def text(self, x, y, s, cls, color="ink", anchor=None):
        a = f' text-anchor="{anchor}"' if anchor else ""
        self.add(f'<text x="{x}" y="{y}" class="{cls}" style="fill:{v(color)}"{a}>{esc(s)}</text>')

    def box(self, x, y, w, h, kind="step", rx=RADIUS):
        """step: a card. input: a chip-colored trigger. store: dashed data. focal: solid ink."""
        if kind == "focal":
            style, cls = f"fill:{v('ink')}", ""
        elif kind == "input":
            style, cls = f"fill:{v('chip')}", ""
        elif kind == "store":
            style, cls = f"fill:{v('paper')};stroke:{v('muted')};stroke-dasharray:4 3", ""
        else:
            style, cls = f"fill:{v('card')};stroke:{v('line')}", ' class="card"'
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"{cls} style="{style}"/>')

    def node(self, x, y, w, h, name, mono=None, desc=None, kind="step", rx=RADIUS, gap=18, center=False):
        on_ink = kind == "focal"
        tx, anchor = (x + w // 2, "middle") if center else (x + 14, None)
        self.add(f'<g data-node-id="{esc(name)}">')
        self.box(x, y, w, h, kind, rx)
        top = y + 22 if desc else y + h // 2 - (2 if mono else -5)
        self.text(tx, top, name, "name", "paper" if on_ink else "ink", anchor)
        line = top
        if mono:
            line += 17
            cls = "mono on-ink" if on_ink else "mono"
            self.text(tx, line, mono, cls, "paper" if on_ink else "muted", anchor)
        if desc:
            line += gap
            cls = "desc on-ink" if on_ink else "desc"
            self.text(tx, line, desc, cls, "paper" if on_ink else "ink-2", anchor)
        self.add("</g>")

    def path(self, points, arrow=True, r=8):
        """An orthogonal connector; interior corners are rounded at r."""
        d = f"M{points[0][0]},{points[0][1]}"
        for i in range(1, len(points) - 1):
            (x0, y0), (x1, y1), (x2, y2) = points[i - 1], points[i], points[i + 1]
            sx, sy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
            tx, ty = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
            d += f" L{x1 - sx * r},{y1 - sy * r} Q{x1},{y1} {x1 + tx * r},{y1 + ty * r}"
        d += f" L{points[-1][0]},{points[-1][1]}"
        end = f' marker-end="url(#{self.slug}-arrow)"' if arrow else ""
        self.add(f'<path d="{d}" class="wire"{end}/>')

    def label(self, x, y, s):
        """An arrow label on a paper mask, centred on (x, y)."""
        lw = int(width(s)) + 14
        self.add(f'<rect x="{x - lw // 2}" y="{y - 9}" width="{lw}" height="18" style="fill:{v("paper")}"/>')
        self.text(x, y + 4, s, "alabel", "ink-2", "middle")

    def rule(self, x1, x2, y, strong=False):
        if strong:
            self.add(
                f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" style="stroke:{v("ink")};stroke-width:2"/>'
            )
        else:
            self.add(
                f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" style="stroke:{v("line")};stroke-width:1"/>'
            )

    def dot(self, x, y):
        self.add(f'<circle cx="{x}" cy="{y}" r="4" style="fill:{v("ink")}"/>')

    def legend_swatch(self, x, y, kind, w=20, rx=4):
        self.box(x, y, w, 16, kind, rx)

    def legend_arrow(self, x, y, w=30):
        self.path([(x, y), (x + w, y)])


def _vars(t: dict) -> str:
    return " ".join(f"--{k}:{val};" for k, val in t.items())


def page(*, lang, slug, title, eyebrow, lede, desc, w, h, body) -> str:
    html_lang = "zh-CN" if lang == "zh" else "en"
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <link href="{FONTS}" rel="stylesheet">
  <script>
    const t = new URLSearchParams(location.search).get("theme");
    if (t === "dark" || t === "light") document.documentElement.dataset.theme = t;
  </script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{ {_vars(DAY)} }}
    @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {_vars(NIGHT)} color-scheme: dark; }} }}
    :root[data-theme="dark"] {{ {_vars(NIGHT)} color-scheme: dark; }}
    :root {{
      --f-title: "Noto Serif SC", serif;
      --f-body: "Inter", "PingFang SC", "Noto Sans SC", sans-serif;
      --f-mono: "JetBrains Mono", "Noto Sans SC", monospace;
    }}
    html, body {{ background: var(--paper); }}
    body {{
      font-family: var(--f-body);
      color: var(--ink);
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 48px 16px;
    }}
    .frame {{ max-width: {max(1320, w)}px; width: 100%; min-width: 0; }}
    .diagram-container {{ width: 100%; overflow-x: auto; }}
    .eyebrow-html {{
      font-family: var(--f-mono);
      font-size: 12px;
      letter-spacing: .14em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    h1 {{ font-family: var(--f-title); font-weight: 700; font-size: 28px; line-height: 1.3; margin-bottom: 12px; }}
    .lede {{ font-size: 15px; line-height: 1.7; color: var(--ink-2); max-width: 720px; margin-bottom: 32px; }}
    svg {{ width: 100%; min-width: {w}px; display: block; }}
    svg .card {{ filter: drop-shadow(0 6px 8px var(--shade)); }}
    svg .wire {{ fill: none; stroke: var(--muted); stroke-width: 1.2; stroke-linejoin: round; }}
    svg .name {{ font-family: var(--f-body); font-size: 13px; font-weight: 600; }}
    svg .cli {{ font-family: var(--f-mono); font-size: 18px; font-weight: 600; }}
    svg .mono {{ font-family: var(--f-mono); font-size: 11px; }}
    svg .desc {{ font-family: var(--f-body); font-size: 12px; }}
    svg .desc-strong {{ font-family: var(--f-body); font-size: 13px; font-weight: 500; }}
    svg .on-ink {{ opacity: .78; }}
    svg .head {{ font-family: var(--f-title); font-size: 15px; font-weight: 700; }}
    svg .when {{ font-family: var(--f-mono); font-size: 12px; font-weight: 500; }}
    svg .eyebrow {{ font-family: var(--f-mono); font-size: 9px; font-weight: 500; letter-spacing: .14em; }}
    svg .alabel {{ font-family: var(--f-body); font-size: 12px; font-weight: 500; }}
    @media print {{
      .diagram-container {{ overflow-x: visible; }}
      svg {{ min-width: 0; }}
    }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow-html">{esc(eyebrow)}</p>
    <h1>{esc(title)}</h1>
    <p class="lede">{esc(lede)}</p>
    <div class="diagram-container">
      <svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
        <title id="{slug}-title">{esc(title)}</title>
        <desc id="{slug}-desc">{esc(desc)}</desc>
        <defs>
          <marker id="{slug}-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" style="fill:var(--muted)"/></marker>
        </defs>
        <rect width="100%" height="100%" style="fill:var(--paper)"/>
{body}
      </svg>
    </div>
  </div>
</body>
</html>
"""
