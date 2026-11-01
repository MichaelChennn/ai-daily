"""Draws the README's hero and pipeline SVGs, in Chinese and English, light and dark.

    python docs/assets/readme/source/build.py

Writes docs/assets/readme/{hero,pipeline}-{zh,en}-{light,dark}.svg. Brand icons come from
simple-icons (CC0), copied into icons.json next to this file.
"""

import json
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
OUT = HERE.parent
ICONS = json.loads((HERE / "icons.json").read_text())

SANS = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', "
    "'Microsoft YaHei', 'Noto Sans SC', sans-serif"
)
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# The site's shadcn neutral tokens.
THEMES = {
    "light": dict(bg="#FAFAFA", card="#FFFFFF", fg="#0A0A0A", body="#404040", muted="#737373",
                  border="#E5E5E5", chip="#F5F5F5", shadow=0.06),
    "dark": dict(bg="#0A0A0A", card="#171717", fg="#FAFAFA", body="#D4D4D4", muted="#A3A3A3",
                 border="#2E2E2E", chip="#262626", shadow=0),
}
# Near-black brand colours vanish on a dark card: draw those in the foreground colour.
DARK_BRANDS = {"anthropic", "github"}

TEXT = {
    "zh": {
        "eyebrow": "每天 06:00 · 柏林时间",
        "name": "AI 科技日报",
        "name_size": 76,
        "lines": ["每天一期 AI 技术日报，5 分钟读完。", "每个数字都能追到一手来源的原文。"],
        "chips": ["17 个信源", "中文 / English", "全文 RSS"],
        "meta": "Mistral AI News · 10月29日",
        "title": "Mistral 开放 Mistral Large 4 权重",
        "summary": [["官方称它在 Terminal-Bench 4.0 上比预览版"],
                    ["提升 ", ("13",), " 个百分点至 ", ("41%",), "。"]],
        "check": "逐字核对",
        "pipeline_title": "AI 科技日报的流水线",
        "s1": "信源采集", "s1_note": "17 个信源 · 05:07",
        "merge": "去重 → 候选",
        "s2": "编辑与把关", "s2_note": "05:30 → 06:00",
        "claude": "Claude 通道", "claude_sub": "daily-editor skill",
        "api": "API 通道", "api_sub": "云端模型 · 另出 Beta 版",
        "validate_sub": ["数字和模型名", "逐个对照原文引文"],
        "pass": "通过",
        "loop": "不合格：补引文，或整条删掉",
        "final": "今日日报", "priority": "Claude > API > 降级版",
        "outputs": ["中文", "English", "RSS"],
    },
    "en": {
        "eyebrow": "DAILY AT 06:00 BERLIN TIME",
        "name": "AI Daily",
        "name_size": 84,
        "lines": ["A five-minute AI tech digest, every morning.", "Every number traces back to a primary source."],
        "chips": ["17 sources", "English / 中文", "Full-text RSS"],
        "meta": "Mistral AI News · Oct 29",
        "title": "Mistral releases Mistral Large 4 weights",
        "summary": [["Mistral says it improved by ", ("13",), " percentage"],
                    ["points to ", ("41%",), " on Terminal-Bench 4.0."]],
        "check": "verbatim",
        "pipeline_title": "The AI Daily pipeline",
        "s1": "Source collection", "s1_note": "17 sources · 05:07",
        "merge": "dedupe → candidates",
        "s2": "Editing and checks", "s2_note": "05:30 → 06:00",
        "claude": "Claude route", "claude_sub": "daily-editor skill",
        "api": "API route", "api_sub": "cloud models + Beta",
        "validate_sub": ["numbers and model names", "matched against quotes"],
        "pass": "pass",
        "loop": "fails: add a quote, or drop the item",
        "final": "Today's issue", "priority": "Claude > API > fallback",
        "outputs": ["中文", "English", "RSS"],
    },
}

QUOTE = [["“On Terminal-Bench 4.0, Mistral Large 4"],
         ["improved by ", ("13",), " percentage points to ", ("41%",)],
         ["compared to its public preview …”"]]

SOURCES = [("anthropic", "Anthropic"), ("google", "Google"), ("huggingface", "Hugging Face"),
           ("meta", "Meta"), ("mistralai", "Mistral"), ("deepseek", "DeepSeek"),
           ("github", "GitHub"), ("ycombinator", "Hacker News"), ("reddit", "Reddit")]


def icon(name, x, y, size, t):
    """A simple-icons glyph (24×24 viewBox) with its top-left corner at x, y."""
    colour = t["fg"] if name in DARK_BRANDS or ICONS[name]["hex"] in ("#000000", "#181717") else ICONS[name]["hex"]
    return (f'<path transform="translate({x} {y}) scale({size / 24:g})" fill="{colour}" '
            f'd="{ICONS[name]["path"]}"/>')


def text(x, y, content, size, fill, weight=400, family=SANS, anchor="start", extra=""):
    if family == MONO and any(ord(c) > 0x2E80 for c in content):
        family = SANS  # CJK in a monospace stack falls back unevenly
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{extra}>{content}</text>')


def runs(parts, strong, plain):
    """A line of text whose ("…",) parts are set bold in the foreground colour."""
    out = []
    for part in parts:
        if isinstance(part, tuple):
            out.append(f'<tspan font-weight="700" fill="{strong}">{escape(part[0])}</tspan>')
        else:
            out.append(f'<tspan fill="{plain}">{escape(part)}</tspan>')
    return "".join(out)


def chip_width(label, size):
    """Rough rendered width: CJK characters are square, Latin ones about 0.56em."""
    return sum(size if ord(c) > 0x2E80 else size * 0.53 for c in label)


def card(x, y, w, h, t, fill=None, rx=16):
    shadow = ' filter="url(#shadow)"' if t["shadow"] else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or t["card"]}" '
            f'stroke="{t["border"]}" stroke-width="1.5"{shadow}/>')


def svg(w, h, title, desc, t, body):
    shadow = (
        '<filter id="shadow" x="-10%" y="-10%" width="120%" height="140%">'
        f'<feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="{t["shadow"]}"/>'
        "</filter>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="title desc">\n'
        f"<title id=\"title\">{escape(title)}</title>\n<desc id=\"desc\">{escape(desc)}</desc>\n"
        f'<defs>{shadow}<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L8 5 L1 9" fill="none" '
        f'stroke="{t["fg"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>\n'
        f'<rect width="{w}" height="{h}" rx="24" fill="{t["bg"]}"/>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def hero(lang, t):
    s = TEXT[lang]
    b = []
    # Masthead: what it is, in the reader's words.
    b.append(text(64, 150, escape(s["eyebrow"]), 18, t["muted"], 500, MONO, extra=' letter-spacing="1"'))
    b.append(text(60, 236, escape(s["name"]), s["name_size"], t["fg"], 800, extra=' letter-spacing="-2"'))
    for i, line in enumerate(s["lines"]):
        b.append(text(64, 292 + i * 36, escape(line), 23, t["body"]))
    x = 64
    for label in s["chips"]:
        w = chip_width(label, 18) + 36
        b.append(f'<rect x="{x}" y="364" width="{w:.0f}" height="40" rx="20" fill="none" '
                 f'stroke="{t["border"]}" stroke-width="1.5"/>')
        b.append(text(x + w / 2, 390, escape(label), 18, t["fg"], 500, anchor="middle"))
        x += w + 10

    # Proof: a real item from 2026-10-30, and the sentence on mistral.ai its numbers come from.
    cx, cw = 640, 496
    b.append(card(cx, 48, cw, 176, t))
    b.append(icon("mistralai", cx + 24, 66, 20, t))
    b.append(text(cx + 54, 82, escape(s["meta"]), 17, t["muted"]))
    b.append(text(cx + 24, 124, escape(s["title"]), 23, t["fg"], 700))
    for i, line in enumerate(s["summary"]):
        b.append(text(cx + 24, 162 + i * 32, runs(line, t["fg"], t["body"]), 19, t["body"]))

    # The trace between the two: the motif of the whole README.
    lx = cx + 64
    b.append(f'<line x1="{lx}" y1="226" x2="{lx}" y2="270" stroke="{t["fg"]}" stroke-width="1.5" '
             f'stroke-dasharray="4 4"/>')
    b.append(f'<circle cx="{lx}" cy="226" r="4" fill="{t["fg"]}"/><circle cx="{lx}" cy="270" r="4" fill="{t["fg"]}"/>')
    b.append(text(lx + 20, 254, "validate ✓", 17, t["fg"], 600, MONO))
    b.append(text(lx + 132, 254, escape(s["check"]), 17, t["muted"], 500))

    b.append(card(cx, 272, cw, 148, t, fill=t["chip"]))
    b.append(text(cx + 24, 304, "EVIDENCE · mistral.ai/news", 15, t["muted"], 500, MONO,
                  extra=' letter-spacing="0.5"'))
    for i, line in enumerate(QUOTE):
        b.append(text(cx + 24, 340 + i * 29, runs(line, t["fg"], t["body"]), 19, t["body"],
                      extra=' font-style="italic"'))
    return svg(1200, 464, s["name"], " ".join(s["lines"]), t, b)


def step(x, y, n, label, note, t):
    """A panel heading: numbered disc, title, and a mono note."""
    return [
        f'<circle cx="{x + 22}" cy="{y - 10}" r="22" fill="{t["chip"]}"/>',
        text(x + 22, y - 2, str(n), 22, t["fg"], 700, anchor="middle"),
        text(x + 58, y, escape(label), 32, t["fg"], 700),
        text(1152 - 24, y - 2, escape(note), 18, t["muted"], 500, MONO, anchor="end"),
    ]


def pipeline(lang, t):
    s = TEXT[lang]
    b = []
    # 1 · Sources: a row of real sources whose lines merge into one candidate list.
    b.append(card(24, 24, 1152, 280, t, rx=24))
    b += step(48, 88, 1, s["s1"], s["s1_note"], t)
    w, gap, x0, y0 = 112, 12, 48, 118
    for i, (key, name) in enumerate(SOURCES):
        x = x0 + i * (w + gap)
        b.append(card(x, y0, w, 100, t, fill=t["card"], rx=14))
        b.append(icon(key, x + w / 2 - 17, y0 + 18, 34, t))
        b.append(text(x + w / 2, y0 + 82, escape(name), 16 if len(name) > 9 else 17, t["fg"], 500, anchor="middle"))
        cx = x + w / 2
        b.append(f'<circle cx="{cx}" cy="{y0 + 112}" r="4" fill="{t["fg"]}"/>')
        b.append(f'<path d="M{cx} {y0 + 112} C{cx} {y0 + 150} 600 {y0 + 130} 600 {y0 + 172}" fill="none" '
                 f'stroke="{t["fg"]}" stroke-width="1.4" opacity="0.55"/>')
    mw = chip_width(s["merge"], 18) + 40
    b.append(f'<line x1="600" y1="290" x2="600" y2="336" stroke="{t["fg"]}" stroke-width="1.5" marker-end="url(#arrow)"/>')
    b.append(f'<rect x="{600 - mw / 2:.0f}" y="266" width="{mw:.0f}" height="38" rx="19" fill="{t["chip"]}" '
             f'stroke="{t["border"]}" stroke-width="1.5"/>')
    b.append(text(600, 291, escape(s["merge"]), 18, t["fg"], 600, MONO, anchor="middle"))

    # 2 · Editing: two routes write, validate decides, the main issue goes out.
    b.append(card(24, 344, 1152, 412, t, rx=24))
    b += step(48, 408, 2, s["s2"], s["s2_note"], t)

    def route(y, icons, title, sub):
        out = [card(48, y, 312, 104, t, rx=16)]
        for j, name in enumerate(icons):
            out.append(icon(name, 72 + j * 38, y + 37, 30, t))
        out.append(text(160, y + 46, escape(title), 22, t["fg"], 700))
        out.append(text(160, y + 76, escape(sub), 16, t["muted"], 400, MONO))
        return out

    b += route(440, ["claude"], s["claude"], s["claude_sub"])
    b += route(572, ["nvidia", "googlegemini"], s["api"], s["api_sub"])
    # Both routes feed validate.
    for y in (492, 624):
        b.append(f'<path d="M360 {y} C392 {y} 392 558 424 558" fill="none" stroke="{t["fg"]}" '
                 f'stroke-width="1.5" marker-end="url(#arrow)"/>')
    b.append(card(428, 486, 300, 144, t, rx=16))
    b.append(f'<circle cx="466" cy="526" r="16" fill="{t["fg"]}"/>')
    b.append(f'<path d="M458 526 l6 6 l11 -12" fill="none" stroke="{t["card"]}" stroke-width="3" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(text(494, 534, "validate", 26, t["fg"], 700, MONO))
    for i, line in enumerate(s["validate_sub"]):
        b.append(text(452, 580 + i * 28, escape(line), 18, t["body"]))
    # Revise and resubmit: the pre-check loop back to the editors.
    b.append(f'<path d="M578 630 L578 700 Q578 712 566 712 L216 712 Q204 712 204 700 L204 680" fill="none" '
             f'stroke="{t["fg"]}" stroke-width="1.5" stroke-dasharray="5 5" marker-end="url(#arrow)"/>')
    b.append(text(391, 740, escape(s["loop"]), 17, t["muted"], 500, anchor="middle"))
    # Pass → today's issue.
    b.append(f'<line x1="728" y1="558" x2="814" y2="558" stroke="{t["fg"]}" stroke-width="1.5" marker-end="url(#arrow)"/>')
    pw = chip_width(s["pass"], 16) + 28
    b.append(f'<rect x="{771 - pw / 2:.0f}" y="514" width="{pw:.0f}" height="30" rx="15" fill="{t["chip"]}"/>')
    b.append(text(771, 535, escape(s["pass"]), 16, t["fg"], 600, anchor="middle"))

    fx, fy = 824, 432
    b.append(card(fx, fy, 304, 296, t, rx=18))
    # A small award rosette, after the one in design/flow.jpg.
    b.append(f'<circle cx="{fx + 38}" cy="{fy + 38}" r="13" fill="none" stroke="{t["fg"]}" stroke-width="2.5"/>')
    b.append(f'<path d="M{fx + 31} {fy + 49} l-5 16 l8 -4 l4 7 l4 -14 M{fx + 45} {fy + 49} l5 16 l-8 -4 l-4 7" '
             f'fill="none" stroke="{t["fg"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    b.append(text(fx + 66, fy + 48, escape(s["final"]), 24, t["fg"], 700))
    prw = chip_width(s["priority"], 15) + 28
    b.append(f'<rect x="{fx + 24}" y="{fy + 76}" width="{prw:.0f}" height="30" rx="15" fill="{t["chip"]}"/>')
    b.append(text(fx + 38, fy + 96, escape(s["priority"]), 15, t["fg"], 500, MONO))
    for i in range(3):
        y = fy + 138 + i * 38
        b.append(f'<circle cx="{fx + 40}" cy="{y}" r="15" fill="{t["chip"]}"/>')
        b.append(text(fx + 40, y + 6, str(i + 1), 17, t["fg"], 700, anchor="middle"))
        b.append(f'<rect x="{fx + 68}" y="{y - 10}" width="{200 - i * 12}" height="8" rx="4" fill="{t["border"]}"/>')
        b.append(f'<rect x="{fx + 68}" y="{y + 4}" width="{140 - i * 20}" height="8" rx="4" fill="{t["border"]}"/>')
    x = fx + 24
    for label in s["outputs"]:
        ow = chip_width(label, 16) + 28
        b.append(f'<rect x="{x:.0f}" y="{fy + 248}" width="{ow:.0f}" height="30" rx="15" fill="none" '
                 f'stroke="{t["border"]}" stroke-width="1.5"/>')
        b.append(text(x + ow / 2, fy + 268, escape(label), 16, t["fg"], 500, anchor="middle"))
        x += ow + 8
    desc = f"{s['s1']} → {s['merge']} → {s['claude']} / {s['api']} → validate → {s['final']}"
    return svg(1200, 780, s["pipeline_title"], desc, t, b)


if __name__ == "__main__":
    for lang in TEXT:
        for theme, t in THEMES.items():
            (OUT / f"hero-{lang}-{theme}.svg").write_text(hero(lang, t), encoding="utf-8")
            (OUT / f"pipeline-{lang}-{theme}.svg").write_text(pipeline(lang, t), encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
