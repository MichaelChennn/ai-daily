"""Generates the backend architecture diagram, in the #43 design system.

python3 docs/diagrams/gen_architecture.py --lang zh docs/diagrams/architecture.zh.html

Three triggers, the one cli entry, five flows with their modules, and the shared layer under them. Every
node is named by what it does and the module behind it; no descriptions, labels or legend.
"""

from press_style import Svg, args, page

A = args(__doc__)


def T(zh: str, en: str) -> str:
    return en if A.lang == "en" else zh


W, H = 1280, 704
SLUG = "backend-architecture"
s = Svg(SLUG)

COLS = [40, 284, 528, 772, 1016]
CW, NH = 224, 56
SW = 104  # a half-width node, two to a column
TRIG_Y, CLI_Y, CLI_H, HEAD_Y = 32, 128, 56, 224
R1, R2, R3 = 280, 376, 472
BASE_HEAD_Y, BASE_Y = 568, 608
BX, BW = [40 + i * 248 for i in range(5)], 208


def header(x, w, y, title, mono=None):
    s.rule(x, x + w, y, strong=True)
    s.text(x + w // 2, y + 24, title, "head", anchor="middle")
    if mono:
        s.text(x + w // 2, y + 40, mono, "mono", "muted", "middle")


def node(*a, **kw):
    s.node(*a, center=True, **kw)


# ---- arrows first ----------------------------------------------------------------------------------
for x, w in [(40, 468), (528, 468), (1016, 224)]:
    s.path([(x + w // 2, TRIG_Y + NH), (x + w // 2, CLI_Y - 2)])
for x in COLS:
    s.path([(x + CW // 2, CLI_Y + CLI_H), (x + CW // 2, HEAD_Y - 2)])
for x, y in [(92, R1), (212, R1), (396, R1), (396, R2), (884, R1), (1068, R1), (1188, R1), (1068, R2)]:
    s.path([(x, y + NH), (x, y + 40 + NH - 2)])
mid_y = BASE_Y + NH // 2
# the folder's files <- issue.py <- trace -> routes <- digest
for x1, x2 in [(BX[1], BX[0] + BW), (BX[2], BX[1] + BW), (BX[2] + BW, BX[3]), (BX[4], BX[3] + BW)]:
    s.path([(x1, mid_y), (x2 + (2 if x2 < x1 else -2), mid_y)])
arrows = s.take()

# ---- nodes -----------------------------------------------------------------------------------------
node(40, TRIG_Y, 468, NH, "GitHub Actions", "fetch · editor-api · ingest · fallback · pages", kind="input")
node(528, TRIG_Y, 468, NH, "daily-editor skill", "Claude Code cloud session", kind="input")
node(1016, TRIG_Y, 224, NH, T("本地手动", "By hand"), "uv run python -m daily", kind="input")

s.add('<g data-node-id="cli.py">')
s.box(40, CLI_Y, 1200, CLI_H, "focal")
s.text(W // 2, CLI_Y + 34, "cli.py", "cli", "paper", "middle")
s.add("</g>")

header(COLS[0], CW, HEAD_Y, T("抓取", "Fetch"), "fetch · list")
header(COLS[1], CW, HEAD_Y, T("API 通道", "API route"), "edit")
header(COLS[2], CW, HEAD_Y, T("Claude 通道与降级", "Claude route, fallback"), "validate · trace · degrade")
header(COLS[3], CW, HEAD_Y, T("并入", "Ingest"), "adopt · ingest")
header(COLS[4], CW, HEAD_Y, T("网站", "Site"), "export · render")

node(COLS[0], R1, CW, NH, T("抓取流程", "Fetch run"), "pipeline")
node(40, R2, SW, NH, T("抓取器", "Fetchers"), "fetchers/*")
node(160, R2, SW, NH, T("去重", "Dedup"), "dedup")

node(COLS[1], R1, CW, NH, T("各模型编辑，选主版", "Models edit, pick main"), "edit.py")
node(COLS[1], R2, CW, NH, T("选稿、写稿、英文版", "Pick, write, English"), "api_editor")
node(COLS[1], R3, CW, NH, T("调用模型，断流重发", "Call models, resend"), "llm.py")

node(COLS[2], R1, CW, NH, T("降级版", "Fallback issue"), "fallback")

node(COLS[3], R1, CW, NH, T("并入分支上的日报", "Take pushed issues"), "ingest")
node(COLS[3], R2, CW, NH, T("按优先级选主版", "Pick the main"), "publish")

node(COLS[4], R1, CW, NH, T("导出给网站", "Export for the site"), "export")
node(1016, R2, SW, NH, T("每期页面", "Issues"), "site")
node(1136, R2, SW, NH, T("过程页", "Process"), "process")
node(COLS[4], R3, CW, NH, T("渲染 Markdown 版", "Render Markdown"), "render")

header(40, 1200, BASE_HEAD_Y, T("共享下层", "Shared layer"))
node(BX[0], BASE_Y, BW, NH, T("一期的全部文件", "One issue's files"), "data/YYYY-MM-DD/", kind="store")
node(BX[1], BASE_Y, BW, NH, T("一期目录读写", "Issue folder I/O"), "issue.py")
node(BX[2], BASE_Y, BW, NH, T("生成记录", "Run trace"), "trace")
node(BX[3], BASE_Y, BW, NH, T("通道表", "Route table"), "routes")
node(BX[4], BASE_Y, BW, NH, T("日报校验", "Issue validation"), "digest")
nodes = s.take()

html = page(
    lang=A.lang,
    slug=SLUG,
    title=T("AI 晨报 · 后端架构", "AI Daily · Backend architecture"),
    eyebrow="Architecture · ai-daily",
    lede=T(
        "三个触发方都只调 cli，cli 按命令分到五条流程，五条流程共用同一个下层。",
        "All three triggers call cli, which hands each command to one of five flows, and all five share one layer below.",
    ),
    desc=T(
        "GitHub Actions、daily-editor skill 和本地手动运行都经 cli.py 进入抓取、API 通道、Claude 通道与降级、并入、网站五条流程，它们共用 issue.py、trace、routes 和 digest 读写与校验 data 目录里的每一期。",
        "GitHub Actions, the daily-editor skill and local runs all enter through cli.py into five flows: fetch, the API route, the Claude route and fallback, ingest, and the site. They share issue.py, trace, routes and digest to read, write and validate each issue under data/.",
    ),
    w=W,
    h=H,
    body=arrows + "\n" + nodes,
)
open(A.out, "w", encoding="utf-8").write(html)
