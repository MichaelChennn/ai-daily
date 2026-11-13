"""Generates the daily flow: how one issue is made each day, as a swimlane, in the #43 design system.

python3 docs/diagrams/gen_daily_flow.py --lang zh docs/diagrams/daily-flow.zh.html

Six lanes, one per workflow, every step named by what it does and the command or file behind it; no
descriptions, labels or legend.
"""

from press_style import Svg, args, page

A = args(__doc__)


def T(zh: str, en: str) -> str:
    return en if A.lang == "en" else zh


W, H = 1352, 640
SLUG = "daily-flow"
s = Svg(SLUG)

LANE_H, NH = 96, 56
LANES = [32 + i * LANE_H for i in range(6)]
COLS = [160 + i * 168 for i in range(7)]
CW = 144


def cx(c):
    return COLS[c] + CW // 2


def top(lane):
    return LANES[lane] + 20


def mid(lane):
    return LANES[lane] + 48


def bot(lane):
    return LANES[lane] + 76


def under(lane):  # the strip under a lane's nodes, for connectors
    return LANES[lane] + 88


def node(lane, c, name, mono, kind="step", **kw):
    rx = NH // 2 if kind == "focal" else 12
    s.node(COLS[c], top(lane), CW, NH, name, mono, kind=kind, rx=rx, **kw)


def chain(lane, first, last):
    for c in range(first, last):
        s.path([(COLS[c] + CW, mid(lane)), (COLS[c + 1] - 2, mid(lane))])


# ---- lanes -----------------------------------------------------------------------------------------
for i, (when, name, who) in enumerate(
    [
        ("05:07", T("抓取", "Fetch"), "fetch.yml"),
        ("05:30", T("Claude 通道", "Claude route"), "daily-editor"),
        ("05:30", T("API 通道", "API route"), "editor-api.yml"),
        (T("推送后", "on push"), T("并入", "Ingest"), "ingest.yml"),
        ("06:30", T("降级", "Fallback"), "fallback.yml"),
        (T("之后", "then"), T("网站", "Site"), "pages.yml"),
    ]
):
    y = LANES[i]
    if i:
        s.rule(40, W - 40, y)
    s.text(40, y + 30, when, "when", "muted")
    s.text(40, y + 52, name, "head")
    s.text(40, y + 70, who, "mono", "muted")
s.rule(40, W - 40, LANES[0], strong=True)
s.rule(40, W - 40, LANES[-1] + LANE_H, strong=True)

# ---- connectors ------------------------------------------------------------------------------------
chain(0, 0, 1)
for lane in (1, 2):  # both routes read the same candidates
    s.path([(cx(1), bot(0)), (cx(1), mid(lane)), (COLS[2] - 2, mid(lane))])
chain(1, 2, 6)
chain(2, 2, 5)
# the Claude push and the API run both end in ingest
s.path([(cx(6), bot(1)), (cx(6), under(2)), (cx(4), under(2)), (cx(4), top(3) - 2)])
s.path([(cx(5), bot(2)), (cx(5), under(2))], arrow=False)
chain(3, 4, 6)
s.path([(cx(5), top(4)), (cx(5), bot(3) + 2)])  # the fallback goes through the same pick
s.path([(cx(6), bot(3)), (cx(6), under(4)), (cx(4), under(4)), (cx(4), top(5) - 2)])
chain(5, 4, 6)
s.dot(cx(1), mid(1))
s.dot(cx(5), under(2))
connectors = s.take()

# ---- nodes -----------------------------------------------------------------------------------------
node(0, 0, T("抓取信源并去重", "Fetch, dedup"), "daily fetch")
node(0, 1, T("候选", "Candidates"), "candidates.json", kind="store")

node(1, 2, T("打分筛选", "Score, pick"), "SKILL.md §1–2")
node(1, 3, T("读原文写中文版", "Read, write zh"), "digest.json")
node(1, 4, T("自检与校验", "Check, validate"), "trace · validate")
node(1, 5, T("写英文版", "Write English"), "digest.en.json")
node(1, 6, T("推到 claude/ 分支", "Push to claude/"), "git push")

node(2, 2, T("各模型选稿", "Each model picks"), "daily edit")
node(2, 3, T("读原文写稿", "Read, write"), "api_editor")
node(2, 4, T("校验，不过就重写", "Validate, redo"), "digest.validate")
node(2, 5, T("主版模型写英文版", "Main writes EN"), "write_en_for")

node(3, 4, T("重新校验后并入", "Recheck, ingest"), "daily ingest")
node(3, 5, T("按优先级选主版", "Pick the main"), "publish.decide")
node(3, 6, T("提交到 main", "Commit to main"), "data/YYYY-MM-DD/", kind="store")

node(4, 5, T("无合格日报才降级", "If none is valid"), "daily degrade")

node(5, 4, T("导出各期数据", "Export issues"), "daily export")
node(5, 5, T("构建网站", "Build the site"), "npm run build")
node(5, 6, T("网站", "Site"), "GitHub Pages", kind="focal", center=True)
nodes = s.take()

html = page(
    lang=A.lang,
    slug=SLUG,
    title=T("AI 晨报 · 每日生成流程", "AI Daily · How an issue is made"),
    eyebrow="Process · ai-daily",
    lede=T(
        "05:07 抓取候选，05:30 Claude 和 API 两条通道同时开编，推送后并入 main 并选出主版，06:30 仍无合格日报就发布降级版，提交后重建网站。",
        "Candidates are fetched at 05:07, both routes start editing at 05:30, each pushed issue is ingested into main and the main one picked, the fallback goes out at 06:30 if none is valid, and every commit rebuilds the site.",
    ),
    desc=T(
        "05:07 fetch.yml 抓取信源、去重并提交 candidates.json；05:30 Claude 通道打分筛选、读原文写中文版、自检与校验、写英文版后推到 claude/ 分支，API 通道每个模型选稿、写稿、校验重写，主版模型再写英文版；ingest.yml 重新校验后并入，按 Claude、API、降级版的优先级选主版并提交到 main；06:30 fallback.yml 在仍无合格日报时发布降级版；之后 pages.yml 导出各期数据、构建并发布到 GitHub Pages。",
        "At 05:07 fetch.yml fetches the sources, removes repeats and commits candidates.json. At 05:30 the Claude route scores and picks, reads the sources and writes the Chinese issue, self-checks and validates, writes the English issue and pushes to its claude/ branch; on the API route each model picks, writes and is validated until it passes, and the main issue's model writes the English one. ingest.yml rechecks and ingests each issue, picks the main by priority Claude, API, fallback and commits it to main. At 06:30 fallback.yml publishes the fallback if there is still no valid issue. pages.yml then exports the issues, builds the site and deploys it to GitHub Pages.",
    ),
    w=W,
    h=H,
    body=connectors + "\n" + nodes,
)
open(A.out, "w", encoding="utf-8").write(html)
