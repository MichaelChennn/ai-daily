"""Generates daily-flow.html: how one issue is made each day, as a swimlane in the diagram-design grammar.

python3 docs/diagrams/gen_daily_flow.py docs/diagrams/daily-flow.html
"""

import sys

PAPER = "#f7f7f5"
INK = "#111111"
MUTED = "#4a4a4a"
SOFT = "#5c5c5c"
WHITE = "#ffffff"
W, H = 1280, 864
SLUG = "daily-flow"

out: list[str] = []
add = out.append


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def has_han(s: str) -> bool:
    return any("一" <= ch <= "鿿" for ch in s)


COLS = [192, 408, 624, 840, 1056]
CW, NH = 184, 64
LANE_H = 120
LANES = [48 + i * LANE_H for i in range(6)]  # L1 .. L6 tops


def cx(c):
    return COLS[c] + CW // 2


def top(lane):
    return LANES[lane] + 28


def mid(lane):
    return LANES[lane] + 60


def bot(lane):
    return LANES[lane] + 92


def gap(lane):  # the free strip under a lane's nodes, for connectors
    return LANES[lane] + 106


def node(lane, c, name, mono=None, zh=None, kind="step"):
    x, y = COLS[c], top(lane)
    rx = 20 if kind == "end" else 6
    if kind == "store":
        fill, stroke = "rgba(17,17,17,0.05)", MUTED
    elif kind == "end":
        fill, stroke = INK, INK
    else:
        fill, stroke = WHITE, INK
    c_name = WHITE if kind == "end" else INK
    c_mono = "rgba(255,255,255,0.72)" if kind == "end" else MUTED
    c_zh = "rgba(255,255,255,0.86)" if kind == "end" else SOFT
    add(f'<g data-node-id="{esc(name)}">')
    add(f'<rect x="{x}" y="{y}" width="{CW}" height="{NH}" rx="{rx}" fill="{PAPER}"/>')
    add(
        f'<rect x="{x}" y="{y}" width="{CW}" height="{NH}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
    )
    add(f'<text x="{x + 12}" y="{y + 20}" class="name" fill="{c_name}">{esc(name)}</text>')
    if mono:
        add(f'<text x="{x + 12}" y="{y + 36}" class="mono" fill="{c_mono}">{esc(mono)}</text>')
    if zh:
        add(f'<text x="{x + 12}" y="{y + 54}" class="zh" fill="{c_zh}">{esc(zh)}</text>')
    add("</g>")


def path(points, arrow=True):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(points))
    end = f' marker-end="url(#{SLUG}-arrow)"' if arrow else ""
    add(f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-linejoin="round"{end}/>')


def label(x, y, text):
    lw = 12 * len(text) + 12
    add(f'<rect x="{x - lw // 2}" y="{y - 8}" width="{lw}" height="16" rx="2" fill="{PAPER}"/>')
    add(f'<text x="{x}" y="{y + 4}" class="alabel" fill="{SOFT}" text-anchor="middle">{esc(text)}</text>')


def dot(x, y):
    add(f'<circle cx="{x}" cy="{y}" r="4" fill="{INK}"/>')


def chain(lane, first, last):
    for c in range(first, last):
        path([(COLS[c] + CW, mid(lane)), (COLS[c + 1] - 2, mid(lane))])


# ---- lanes -----------------------------------------------------------------------------------------
lanes = [
    ("05:07", "抓取", "fetch.yml"),
    ("05:30", "Claude 通道", "daily-editor skill"),
    ("05:30", "API 通道", "editor-api.yml"),
    ("推送后", "并入", "ingest.yml"),
    ("06:30", "兜底", "fallback.yml"),
    ("之后", "网站", "pages.yml"),
]
for i, (when, name, mono) in enumerate(lanes):
    y = LANES[i]
    if i:
        add(f'<line x1="40" y1="{y}" x2="1240" y2="{y}" stroke="rgba(17,17,17,0.12)" stroke-width="0.8"/>')
    cls = "when-zh" if has_han(when) else "when"
    add(f'<text x="40" y="{y + 40}" class="{cls}" fill="{MUTED}">{esc(when)}</text>')
    add(f'<text x="40" y="{y + 62}" class="head" fill="{INK}">{esc(name)}</text>')
    add(f'<text x="40" y="{y + 80}" class="mono" fill="{SOFT}">{esc(mono)}</text>')
add(f'<line x1="40" y1="{LANES[0]}" x2="1240" y2="{LANES[0]}" stroke="{INK}" stroke-width="2"/>')
add(
    f'<line x1="40" y1="{LANES[5] + LANE_H}" x2="1240" y2="{LANES[5] + LANE_H}" stroke="{INK}" stroke-width="2"/>'
)

# ---- connectors ------------------------------------------------------------------------------------
chain(0, 0, 2)
# candidates -> both editor routes, along the strip under lane 1 and down the margin
FX = 172
path([(cx(2), bot(0)), (cx(2), gap(0)), (FX, gap(0)), (FX, mid(2)), (COLS[0] - 2, mid(2))])
path([(FX, mid(1)), (COLS[0] - 2, mid(1))])
chain(1, 0, 4)
chain(2, 0, 3)
# both routes -> ingest: the Claude branch down the empty last column, the API run joins it
path([(cx(4), bot(1)), (cx(4), gap(2)), (cx(2), gap(2)), (cx(2), top(3) - 2)])
path([(cx(3), bot(2)), (cx(3), gap(2))], arrow=False)
chain(3, 2, 4)
chain(4, 0, 1)
# fallback -> main
path([(COLS[1] + CW, mid(4)), (COLS[4] + 52, mid(4)), (COLS[4] + 52, bot(3) + 2)])
# main -> the site
path([(COLS[4] + 132, bot(3)), (COLS[4] + 132, gap(4)), (cx(0), gap(4)), (cx(0), top(5) - 2)])
chain(5, 0, 2)
dot(FX, mid(1))
dot(cx(3), gap(2))
label(444, gap(0), "两条通道同时读取")
label(1040, gap(2), "push 触发")
label(824, mid(4), "仍无合格日报")
label(660, gap(4), "每次提交 main 后重建")
connectors = "\n".join(out)
out.clear()

# ---- nodes -----------------------------------------------------------------------------------------
node(0, 0, "抓取信源", "daily fetch · pipeline", "各类抓取器并发请求")
node(0, 1, "窗口与去重", "window · dedup", "只留本期窗口，跨源合并")
node(0, 2, "candidates.json", "data/YYYY-MM-DD/", "提交到 main", kind="store")

node(1, 0, "打分筛选", "SKILL.md §1–2", "浏览候选，逐条打分")
node(1, 1, "读原文写稿", "§3–4 · digest.json", "打开原文，写中文版")
node(1, 2, "自检与校验", "daily trace · validate", "忠实性自检，校验到通过")
node(1, 3, "英文版", "digest.en.json", "依据同一份材料来写")
node(1, 4, "推到 claude/ 分支", "git push", "会话只能推自己的分支")

node(2, 0, "选稿", "daily edit · Editor", "每个模型各编一份")
node(2, 1, "读原文写稿", "api_editor · llm.Chat", "流式请求，断流重发")
node(2, 2, "校验与重写", "digest.validate", "不过就发回问题重写")
node(2, 3, "主版写英文版", "edit.write_en_for", "只有将成主版的模型写")

node(3, 2, "daily ingest", "--ref · --from-dir", "取分支或产物里的日报")
node(3, 3, "选主版", "publish.decide", "Claude > API > 降级版")
node(3, 4, "main · data/", "digest · betas · traces", "提交到 main", kind="store")

node(4, 0, "daily degrade", "fallback", "已有合格日报就不动")
node(4, 1, "daily render", "digest.md", "GitHub 上的版本")

node(5, 0, "daily export", "JSON · RSS → web/", "已发布各期给网站")
node(5, 1, "Astro 构建", "npm run build", "web/ → dist/")
node(5, 2, "GitHub Pages", "deploy-pages", "网站更新", kind="end")

# ---- legend ----------------------------------------------------------------------------------------
LY = 800
add(f'<text x="40" y="{LY + 20}" class="eyebrow" fill="{MUTED}">LEGEND</text>')
lx = 136
add(f'<rect x="{lx}" y="{LY + 8}" width="20" height="16" rx="3" fill="{WHITE}" stroke="{INK}"/>')
add(f'<text x="{lx + 28}" y="{LY + 21}" class="zh" fill="{SOFT}">步骤</text>')
lx = 248
add(
    f'<rect x="{lx}" y="{LY + 8}" width="20" height="16" rx="3" fill="rgba(17,17,17,0.05)" stroke="{MUTED}"/>'
)
add(f'<text x="{lx + 28}" y="{LY + 21}" class="zh" fill="{SOFT}">提交到 main 的数据</text>')
lx = 444
add(f'<rect x="{lx}" y="{LY + 8}" width="28" height="16" rx="8" fill="{INK}"/>')
add(f'<text x="{lx + 36}" y="{LY + 21}" class="zh" fill="{SOFT}">终点</text>')
lx = 564
add(f'<circle cx="{lx + 4}" cy="{LY + 16}" r="4" fill="{INK}"/>')
add(f'<text x="{lx + 16}" y="{LY + 21}" class="zh" fill="{SOFT}">分叉与合流</text>')
lx = 700
add(
    f'<line x1="{lx}" y1="{LY + 16}" x2="{lx + 30}" y2="{LY + 16}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{SLUG}-arrow)"/>'
)
add(f'<text x="{lx + 40}" y="{LY + 21}" class="zh" fill="{SOFT}">流向</text>')
add(f'<text x="1240" y="{LY + 21}" class="zh" fill="{SOFT}" text-anchor="end">左侧为柏林时间</text>')
nodes = "\n".join(out)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI 科技日报生成流程</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600&family=Noto+Serif+SC:wght@400;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --color-paper:   {PAPER};
      --color-ink:     {INK};
      --color-muted:   {MUTED};
      --color-soft:    {SOFT};
      --font-sans:     'Geist', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
      --font-serif:    'Instrument Serif', 'Noto Serif SC', serif;
      --font-mono:     'Geist Mono', ui-monospace, monospace;
    }}
    body {{
      font-family: var(--font-sans);
      background: var(--color-paper);
      color: var(--color-ink);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 3rem 1rem;
    }}
    .frame {{ max-width: 1320px; width: 100%; min-width: 0; }}
    .diagram-container {{ width: 100%; overflow-x: auto; }}
    .eyebrow-html {{
      font-family: var(--font-mono);
      font-size: 0.66rem;
      font-weight: 500;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--color-muted);
      margin-bottom: 0.5rem;
    }}
    h1 {{
      font-family: var(--font-serif);
      font-size: clamp(1.75rem, 2.4vw + 1rem, 2.5rem);
      font-weight: 400;
      letter-spacing: -0.01em;
      line-height: 1.15;
      margin-bottom: 0.75rem;
    }}
    .lede {{ font-size: 0.95rem; line-height: 1.6; color: var(--color-muted); max-width: 46rem; margin-bottom: 2rem; }}
    svg {{ width: 100%; min-width: {W}px; display: block; }}
    svg .name {{ font-family: var(--font-sans); font-size: 13px; font-weight: 600; }}
    svg .mono {{ font-family: var(--font-mono); font-size: 10px; }}
    svg .zh {{ font-family: var(--font-sans); font-size: 12px; font-weight: 400; }}
    svg .head {{ font-family: var(--font-sans); font-size: 14px; font-weight: 600; }}
    svg .when {{ font-family: var(--font-mono); font-size: 12px; font-weight: 500; letter-spacing: 0.06em; }}
    svg .when-zh {{ font-family: var(--font-sans); font-size: 12px; font-weight: 500; }}
    svg .eyebrow {{ font-family: var(--font-mono); font-size: 8px; font-weight: 500; letter-spacing: 0.14em; }}
    svg .alabel {{ font-family: var(--font-sans); font-size: 12px; font-weight: 500; }}
    @media print {{
      .diagram-container {{ overflow-x: visible; }}
      svg {{ min-width: 0; }}
    }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow-html">Process · ai-daily</p>
    <h1>AI 科技日报 · 每日生成流程</h1>
    <p class="lede">05:07 抓取候选，05:30 Claude 和 API 两条通道同时开编，推送后并入 main，按 Claude &gt; API &gt; 降级版选主版。06:30 还没有合格日报就发布降级版。每次提交 main 都会重建网站。</p>
    <div class="diagram-container">
      <svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{SLUG}-title {SLUG}-desc">
        <title id="{SLUG}-title">AI 科技日报每日生成流程</title>
        <desc id="{SLUG}-desc">每天 05:07 fetch.yml 抓取并提交 candidates.json；05:30 Claude 通道和 API 通道各自读取候选、打分、写稿、校验、写英文版；之后 daily ingest 把日报并入 main，按 Claude、API、降级版的优先级选出主版；06:30 fallback.yml 在仍无合格日报时发布降级版；每次提交 main 后 pages.yml 导出数据、构建并发布网站。</desc>
        <defs>
          <marker id="{SLUG}-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
        </defs>
        <rect width="100%" height="100%" fill="{PAPER}"/>
{connectors}
{nodes}
      </svg>
    </div>
  </div>
</body>
</html>
"""
open(sys.argv[1], "w", encoding="utf-8").write(html)
