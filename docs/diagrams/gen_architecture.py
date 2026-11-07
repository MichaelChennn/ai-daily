"""Generates architecture.html: the backend architecture, in the diagram-design grammar.

python3 docs/diagrams/gen_architecture.py docs/diagrams/architecture.html
"""

import sys

PAPER = "#f7f7f5"
INK = "#111111"
MUTED = "#4a4a4a"
SOFT = "#5c5c5c"
WHITE = "#ffffff"
W, H = 1280, 872
SLUG = "backend-architecture"

out: list[str] = []
add = out.append


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def node(x, y, w, h, name, mono=None, zh=None, kind="backend", new=False):
    if kind == "focal":
        fill, stroke, c_name, c_mono, c_zh = (
            INK,
            INK,
            WHITE,
            "rgba(255,255,255,0.72)",
            "rgba(255,255,255,0.86)",
        )
    elif kind == "store":
        fill, stroke, c_name, c_mono, c_zh = "rgba(17,17,17,0.05)", MUTED, INK, MUTED, SOFT
    elif kind == "input":
        fill, stroke, c_name, c_mono, c_zh = "rgba(74,74,74,0.08)", SOFT, INK, MUTED, SOFT
    else:
        fill, stroke, c_name, c_mono, c_zh = WHITE, INK, INK, MUTED, SOFT
    add(f'<g data-node-id="{esc(name)}">')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PAPER}"/>')
    add(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
    )
    add(f'<text x="{x + 12}" y="{y + 24}" class="name" fill="{c_name}">{esc(name)}</text>')
    if new:
        tx = x + w - 40
        tag = WHITE if kind == "focal" else INK
        add(
            f'<rect x="{tx}" y="{y + 10}" width="28" height="14" rx="2" fill="none" stroke="{tag}" stroke-width="0.8"/>'
        )
        add(f'<text x="{tx + 14}" y="{y + 20}" class="tag" fill="{tag}" text-anchor="middle">NEW</text>')
    if mono:
        add(f'<text x="{x + 12}" y="{y + 42}" class="mono" fill="{c_mono}">{esc(mono)}</text>')
    if zh:
        add(f'<text x="{x + 12}" y="{y + (60 if mono else 48)}" class="zh" fill="{c_zh}">{esc(zh)}</text>')
    add("</g>")


def vline(x, y1, y2):
    add(
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2 - 2}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{SLUG}-arrow)"/>'
    )


def hline(x1, x2, y, label):
    add(
        f'<line x1="{x1}" y1="{y}" x2="{x2 + (2 if x2 < x1 else -2)}" y2="{y}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{SLUG}-arrow)"/>'
    )
    mid = (x1 + x2) // 2
    lw = 12 * len(label) + 8
    add(f'<rect x="{mid - lw // 2}" y="{y - 24}" width="{lw}" height="16" rx="2" fill="{PAPER}"/>')
    add(f'<text x="{mid}" y="{y - 12}" class="alabel" fill="{SOFT}" text-anchor="middle">{esc(label)}</text>')


def header(x, w, y, zh, mono):
    add(f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{INK}" stroke-width="2"/>')
    add(f'<text x="{x}" y="{y + 22}" class="head" fill="{INK}">{esc(zh)}</text>')
    if mono:
        add(f'<text x="{x}" y="{y + 38}" class="mono" fill="{SOFT}">{esc(mono)}</text>')


# ---- arrows first ----------------------------------------------------------------------------------
COLS = [40, 284, 528, 772, 1016]
CW = 224
NH = 72
TRIG_Y, CLI_Y, CLI_H, HEAD_Y, R1, R2, R3 = 48, 160, 56, 248, 304, 416, 528
BASE_HEAD_Y, BASE_Y = 640, 696

triggers = [(40, 468), (528, 468), (1016, 224)]
for x, w in triggers:
    vline(x + w // 2, TRIG_Y + NH, CLI_Y)
for x in COLS:
    vline(x + CW // 2, CLI_Y + CLI_H, HEAD_Y)
# inside the columns
vline(92, R1 + NH, R2)  # pipeline -> fetchers
vline(212, R1 + NH, R2)  # pipeline -> dedup
vline(396, R1 + NH, R2)  # edit -> api_editor
vline(396, R2 + NH, R3)  # api_editor -> llm
vline(884, R1 + NH, R2)  # ingest -> publish
vline(1068, R1 + NH, R2)  # export -> site
vline(1188, R1 + NH, R2)  # export -> process
# the shared layer: data/ <- issue.py -> routes <- digest
BX = [40, 356, 672, 988]
BW = 252
mid_y = BASE_Y + NH // 2
hline(BX[1], BX[0] + BW, mid_y, "读写")
hline(BX[1] + BW, BX[2], mid_y, "命名")
hline(BX[3], BX[2] + BW, mid_y, "查通道")
arrows = "\n".join(out)
out.clear()

# ---- nodes -----------------------------------------------------------------------------------------
node(
    40,
    TRIG_Y,
    468,
    NH,
    "GitHub Actions",
    "fetch · editor-api · ingest · fallback · pages · due",
    "定时抓取、API 编辑、并入、降级、发布网站",
    kind="input",
)
node(
    528,
    TRIG_Y,
    468,
    NH,
    "daily-editor skill",
    "SKILL.md · Claude Code cloud session",
    "Claude 通道：读候选、打分、写日报、自检",
    kind="input",
)
node(1016, TRIG_Y, 224, NH, "本地手动", "uv run python -m daily …", "调试与补跑", kind="input")

# cli: the one entry, a black bar
add('<g data-node-id="cli.py">')
add(f'<rect x="40" y="{CLI_Y}" width="1200" height="{CLI_H}" rx="6" fill="{INK}"/>')
add(f'<text x="64" y="{CLI_Y + 34}" class="cli" fill="{WHITE}">cli.py</text>')
add(
    f'<text x="148" y="{CLI_Y + 33}" class="zh-strong" fill="rgba(255,255,255,0.86)">只解析参数，每条命令调一个函数</text>'
)
add(
    f'<text x="1216" y="{CLI_Y + 33}" class="mono" fill="rgba(255,255,255,0.72)" text-anchor="end">'
    "fetch · list · validate · degrade · trace · edit · adopt · ingest · render · export · page</text>"
)
add("</g>")

header(COLS[0], CW, HEAD_Y, "抓取", "fetch · list")
header(COLS[1], CW, HEAD_Y, "API 通道", "edit")
header(COLS[2], CW, HEAD_Y, "Claude 通道与降级", "validate · trace · degrade")
header(COLS[3], CW, HEAD_Y, "并入", "adopt · ingest")
header(COLS[4], CW, HEAD_Y, "网站", "export · render")

node(40, R1, CW, NH, "pipeline", "config · window · throttle", "抓取信源，写 candidates.json")
node(40, R2, 104, NH, "fetchers/*", None, "六类抓取器")
node(160, R2, 104, NH, "dedup", None, "跨源去重")

node(284, R1, CW, NH, "edit.py", "run · write_en_for", "各模型编辑 → 选主版 → 英文版")
node(284, R2, CW, NH, "api_editor", "Editor · write_en", "选稿、写稿、英文版等编辑步骤")
node(284, R3, CW, NH, "llm.py", "Provider · Chat · Reply", "流式读取、断流重发、重试")

node(528, R1, CW, NH, "trace", "record_* · needs_self_check", "打分、自检、每轮校验的记录")
node(528, R2, CW, NH, "fallback", "degrade", "只留标题和链接的降级版")

node(772, R1, CW, NH, "ingest", "adopt · from_dir · save_run", "并入编辑分支推来的日报")
node(772, R2, CW, NH, "publish", "decide · main_of", "按通道优先级选出主版")

node(1016, R1, CW, NH, "export", "JSON · RSS → web/", "已发布各期导出给网站")
node(1016, R2, 104, NH, "site", None, "每期页面")
node(1136, R2, 104, NH, "process", None, "生成过程页")
node(1016, R3, CW, NH, "render", "digest.json → digest.md", "日报在 GitHub 上的版本")

header(40, 1200, BASE_HEAD_Y, "共享下层", "上面各列都经 issue.py 读写一期目录，校验和通道规则各在一处")
node(
    BX[0],
    BASE_Y,
    BW,
    NH,
    "data/YYYY-MM-DD/",
    "candidates · digest · trace.*.json",
    "一期的全部文件",
    kind="store",
)
node(BX[1], BASE_Y, BW, NH, "issue.py", "IssueDir · read · write", "一期目录：文件路径与 JSON 读写")
node(BX[2], BASE_Y, BW, NH, "routes", "ROUTES · file_name · slug", "通道表：文件命名、优先级、beta")
node(BX[3], BASE_Y, BW, NH, "digest", "validate · SCHEMA_VERSION", "日报校验，联网查链接")

# ---- legend ----------------------------------------------------------------------------------------
LY = 812
add(f'<line x1="40" y1="{LY - 8}" x2="1240" y2="{LY - 8}" stroke="rgba(17,17,17,0.12)" stroke-width="0.8"/>')
add(f'<text x="40" y="{LY + 20}" class="eyebrow" fill="{MUTED}">LEGEND</text>')
lx = 136
add(f'<rect x="{lx}" y="{LY + 8}" width="20" height="16" rx="3" fill="{INK}"/>')
add(f'<text x="{lx + 28}" y="{LY + 21}" class="zh" fill="{SOFT}">入口</text>')
lx = 248
add(f'<rect x="{lx}" y="{LY + 8}" width="20" height="16" rx="3" fill="rgba(74,74,74,0.08)" stroke="{SOFT}"/>')
add(f'<text x="{lx + 28}" y="{LY + 21}" class="zh" fill="{SOFT}">触发方</text>')
lx = 380
add(
    f'<rect x="{lx}" y="{LY + 8}" width="20" height="16" rx="3" fill="rgba(17,17,17,0.05)" stroke="{MUTED}"/>'
)
add(f'<text x="{lx + 28}" y="{LY + 21}" class="zh" fill="{SOFT}">数据</text>')
lx = 500
add(
    f'<line x1="{lx}" y1="{LY + 16}" x2="{lx + 30}" y2="{LY + 16}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#{SLUG}-arrow)"/>'
)
add(f'<text x="{lx + 40}" y="{LY + 21}" class="zh" fill="{SOFT}">调用</text>')
add(
    f'<text x="1240" y="{LY + 21}" class="mono" fill="{SOFT}" text-anchor="end">daily/ · Python 3.11+ · uv</text>'
)
nodes = "\n".join(out)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI 科技日报后端架构</title>
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
    svg .cli {{ font-family: var(--font-mono); font-size: 18px; font-weight: 600; }}
    svg .mono {{ font-family: var(--font-mono); font-size: 10px; }}
    svg .zh {{ font-family: var(--font-sans); font-size: 12px; font-weight: 400; }}
    svg .zh-strong {{ font-family: var(--font-sans); font-size: 13px; font-weight: 500; }}
    svg .head {{ font-family: var(--font-sans); font-size: 14px; font-weight: 600; }}
    svg .tag {{ font-family: var(--font-mono); font-size: 7px; font-weight: 500; letter-spacing: 0.08em; }}
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
    <p class="eyebrow-html">Architecture · ai-daily</p>
    <h1>AI 科技日报 · 后端架构</h1>
    <p class="lede">三个触发方都只调 cli；cli 按命令分到五条流程；一期目录的读写、通道规则和日报校验放在共享下层，各列共用。</p>
    <div class="diagram-container">
      <svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{SLUG}-title {SLUG}-desc">
        <title id="{SLUG}-title">AI 科技日报后端架构</title>
        <desc id="{SLUG}-desc">GitHub Actions、daily-editor skill 和本地手动运行都经 cli.py 进入抓取、API 通道、Claude 通道与降级、并入、网站五条流程，它们共用 issue.py、routes 和 digest 读写与校验 data 目录里的每一期。</desc>
        <defs>
          <marker id="{SLUG}-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
        </defs>
        <rect width="100%" height="100%" fill="{PAPER}"/>
{arrows}
{nodes}
      </svg>
    </div>
  </div>
</body>
</html>
"""
open(sys.argv[1], "w", encoding="utf-8").write(html)
