"""Draws the AI 晨报 / AI Daily logo: the mark, its lockups and the favicon, with the type outlined.

    cd web && npm ci && cd ..
    uv run --no-project --with fonttools --with brotli python docs/assets/brand/build.py

The fonts are the site's own, read from web/node_modules/@fontsource*, so the lockups match the
pages letter for letter and render without any font installed. Writes docs/assets/brand/*.svg and
web/public/favicon.svg. Each SVG follows the reader's light or dark mode on its own. The README's
hero imports `lockup()` from here (docs/assets/readme/source/build.py).

Lockups, per docs/design-system.md § Brand:
  a     mark + 「AI 晨报」, the Chinese site's top left (the site sets it as live text)
  c     mark + "AI Daily", the English site's top left (live text too)
  b     mark + 「AI 晨报」 over mono AI DAILY, the Chinese README
  b-en  mark + "AI Daily" over a small 「AI 晨报」, the English README
  d     mark above 「AI 晨报」 and AI DAILY, Chinese covers and social cards
  d-en  mark above "AI Daily" and 「AI 晨报」, English covers and social cards
"""

import re
from functools import cache
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
NM = ROOT / "web" / "node_modules"

INK = {"light": "#161A15", "dark": "#EDEBE6"}  # --ink, press.css

# The mark: two spines stacked over an open card with one line of type. 24 grid, 2px monoline.
MARK = (
    '<path d="M7 3.5h10"/><path d="M5 7.5h14"/>'
    '<rect x="3" y="11.5" width="18" height="9" rx="2"/><path d="M7 16h6"/>'
)
MARK_STYLE = "fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"

# family: (fontsource css, variable weight or None)
FACES = {
    "serif": (NM / "@fontsource/noto-serif-sc/700.css", None),
    "sans": (NM / "@fontsource/noto-sans-sc/500.css", None),
    "mono": (NM / "@fontsource-variable/jetbrains-mono/wght.css", 500),
}


@cache
def _ranges(css: Path) -> list[tuple[list[tuple[int, int]], Path]]:
    out = []
    for block in re.findall(r"@font-face\s*{(.*?)}", css.read_text(), re.S):
        if "font-style: italic" in block:
            continue
        src = re.search(r"url\(\./(files/[^)]+\.woff2)\)", block).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", block)
        spans = []
        for part in rng.group(1).split(",") if rng else ["U+0-10FFFF"]:
            a, _, b = part.strip()[2:].partition("-")
            spans.append((int(a, 16), int(b or a, 16)))
        out.append((spans, css.parent / src))
    return out


@cache
def _font(path: Path, wght: int | None) -> TTFont:
    f = TTFont(path)
    if wght is not None and "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": wght})
    return f


def _font_for(face: str, ch: str) -> TTFont:
    css, wght = FACES[face]
    for spans, path in _ranges(css):
        if any(a <= ord(ch) <= b for a, b in spans):
            return _font(path, wght)
    raise KeyError(f"{face} has no file for {ch!r}")


def text(s: str, face: str, size: float, x: float, top: float, tracking: float = 0):
    """Outlines s with its line box (line-height 1, as CSS sets it) starting at x, top.

    Returns the path data, the advance (trailing letter-spacing included, as Chrome lays it out) and
    the ink's bounds, which can spill out of the line box, as a descender does.
    """
    ref = _font_for(face, "A")
    upm = ref["head"].unitsPerEm
    asc, desc = ref["hhea"].ascent, -ref["hhea"].descent
    baseline = top + (size - (asc + desc) * size / upm) / 2 + asc * size / upm
    d, pen_x, ys = [], x, []
    for ch in s:
        f = _font_for(face, ch)
        gs = f.getGlyphSet()
        name = f.getBestCmap()[ord(ch)]
        k = size / f["head"].unitsPerEm
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, pen_x, baseline)))
        d.append(pen.getCommands())
        bp = BoundsPen(gs)
        gs[name].draw(TransformPen(bp, (k, 0, 0, -k, pen_x, baseline)))
        if bp.bounds:
            ys += [bp.bounds[1], bp.bounds[3]]
        pen_x += gs[name].width * k + tracking * size
    return " ".join(p for p in d if p), pen_x - x, (min(ys), max(ys))


def _mark(x, y, px, color):
    move = f"translate({x:g} {y:g}) scale({px / 24:g})"
    return f'<g transform="{move}" style="{MARK_STYLE};stroke:{color}">{MARK}</g>'


def _line(s, face, size, tracking=0, opacity=1.0):
    return dict(s=s, face=face, size=size, tracking=tracking, opacity=opacity)


ZH = lambda size: _line("AI 晨报", "serif", size, 0.04)  # noqa: E731
EN = lambda size: _line("AI Daily", "serif", size, 0.01)  # noqa: E731
MONO_SUB = _line("AI DAILY", "mono", 10, 0.28, 0.65)
ZH_SUB = lambda size, tr: _line("AI 晨报", "sans", size, tr, 0.65)  # noqa: E731

# id: (mark px, layout, gap, lines, line gap). In a column the gap also falls between the lines, so
# D's line gap is 14 - 4: its second line has margin-top:-4px.
LOCKUPS = {
    "a": (28, "row", 10, [ZH(24)], 0),
    "c": (28, "row", 10, [EN(26)], 0),
    "b": (40, "row", 12, [ZH(22), MONO_SUB], 7),
    "b-en": (40, "row", 12, [EN(25), ZH_SUB(11, 0.14)], 6),
    "d": (56, "col", 14, [ZH(24), MONO_SUB], 10),
    "d-en": (56, "col", 14, [EN(28), ZH_SUB(12, 0.24)], 10),
}


def lockup(key: str, color: str) -> tuple[str, float, float]:
    """The lockup's SVG body in one color, with its width and height, origin at the top left.

    The height covers the ink too, so a descender spilling out of its line box is never cut off.
    """
    px, layout, gap, lines, lgap = LOCKUPS[key]
    widths = [text(ln["s"], ln["face"], ln["size"], 0, 0, ln["tracking"])[1] for ln in lines]
    text_h = sum(ln["size"] for ln in lines) + lgap * (len(lines) - 1)
    if layout == "row":
        w, h = px + gap + max(widths), max(px, text_h)
        mx, my, tx, ty = 0, (h - px) / 2, px + gap, (h - text_h) / 2
    else:
        w, h = max(px, *widths), px + gap + text_h
        mx, my, tx, ty = (w - px) / 2, 0, None, px + gap
    out, top, bottom = [_mark(mx, my, px, color)], 0.0, h
    for ln, lw in zip(lines, widths, strict=True):
        x = tx if tx is not None else (w - lw) / 2
        d, _, (y0, y1) = text(ln["s"], ln["face"], ln["size"], x, ty, ln["tracking"])
        top, bottom = min(top, y0), max(bottom, y1)
        op = f";opacity:{ln['opacity']}" if ln["opacity"] < 1 else ""
        out.append(f'<path style="fill:{color}{op}" d="{d}"/>')
        ty += ln["size"] + lgap
    body = "\n".join(out)
    if top < 0:
        body = f'<g transform="translate(0 {-top:g})">{body}</g>'
    return body, w, bottom - top


def _adaptive(body_light: str, w: float, h: float, title: str) -> str:
    """One SVG for both modes: ink on light, night ink when the reader's system is dark."""
    body = body_light.replace(INK["light"], "var(--ink)")
    dark = f"@media (prefers-color-scheme:dark){{svg{{--ink:{INK['dark']}}}}}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{title}">\n'
        f"<style>svg{{--ink:{INK['light']}}}{dark}</style>\n"
        f"{body}\n</svg>\n"
    )


def main() -> None:
    (OUT / "mark.svg").write_text(_adaptive(_mark(0, 0, 24, INK["light"]), 24, 24, "AI 晨报"))
    for key in LOCKUPS:
        body, w, h = lockup(key, INK["light"])
        title = "AI Daily · AI 晨报" if key in ("c", "b-en", "d-en") else "AI 晨报 · AI Daily"
        (OUT / f"lockup-{key}.svg").write_text(_adaptive(body, w, h, title))
    (ROOT / "web" / "public" / "favicon.svg").write_text(
        _adaptive(_mark(0, 0, 24, INK["light"]), 24, 24, "AI 晨报")
    )


if __name__ == "__main__":
    main()
