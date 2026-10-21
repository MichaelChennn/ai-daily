# ai-daily · AI 科技日报

每天早上 6 点（北京时间）自动生成的中文 AI 技术日报：5 分钟读完，每一条都能追溯到一手来源。

网站：<https://michaelchennn.github.io/ai-daily/> · RSS（全文）：<https://michaelchennn.github.io/ai-daily/feed.xml>

立项书：[docs/charter/00_Project_Charter.md](docs/charter/00_Project_Charter.md)

## 当前进度

| 里程碑 | 状态 |
|---|---|
| M0 立项 | ✅ |
| M1 信源与数据：`daily fetch` + 去重 | 🚧 代码已完成，等待连续 7 天的覆盖率验证 |
| M2 编辑 skill 与质量闸门（`validate`、降级） | 🚧 代码与 skill 已完成，第一期见 [data/2026-10-21/digest.md](data/2026-10-21/digest.md)；等待回放 7 天数据 |
| M3 发布（静态站点 + RSS + 定时任务） | 🚧 代码、workflow 和定时任务已完成，等待无人干预连续发布 3 天 |

## 使用

```bash
pip install -e ".[dev]"

python -m daily fetch                       # 今天这一期 → data/YYYY-MM-DD/candidates.json
python -m daily fetch --date 2026-10-20     # 指定期号（北京时间日期）
python -m daily fetch --only hackernews     # 只跑某个信源，调试用（可重复）

python -m daily list --date 2026-10-21      # 精简列出候选（给编辑看）
python -m daily page <url> --grep 关键词     # 打印原始页面里关键词附近的原文，用来逐字摘录 evidence
python -m daily validate --date 2026-10-21 --check-links --drop-invalid   # 程序闸门
python -m daily degrade --date 2026-10-21   # digest.json 缺失或不合格时，写入“标题 + 链接”降级版
python -m daily render --date 2026-10-21    # digest.json → digest.md
python -m daily adopt --date 2026-10-21 --from x.json   # 按规则并入编辑分支推来的 digest.json（ingest 用）
python -m daily build                       # 静态网站 + RSS → _site/（不提交）
python -m http.server -d _site              # 本地预览：http://localhost:8000/

pytest -q && ruff check . && ruff format --check .
```

编辑环节在 Claude Code 里运行 skill：`/daily-editor 2026-10-21`（[.claude/skills/daily-editor/SKILL.md](.claude/skills/daily-editor/SKILL.md)）。

`GITHUB_TOKEN` 环境变量可选，用于 GitHub Releases（不设置时限额 60 次/小时）。

退出码：`0` 成功（个别信源失败只记录在输出里）；`1` 所有信源都没有拿到内容；`2` 参数错误。

## 流水线

```
sources.yaml ──► fetchers（并发、相互隔离）──► 去重 ──► data/YYYY-MM-DD/candidates.json
             ──► daily-editor skill（Claude）──► digest.json ──► validate ──► render ──► digest.md
                                       （失败时）degrade ──► 降级版 digest.json
```

**时间窗口**：第 D 期覆盖北京时间 D-1 04:00 到 D 06:00（截止到运行时刻）。比 24 小时多出的 2 小时用来接住上一次运行之后、06:00 之前发布的内容：只要每天在 04:00 之后运行，相邻两期之间就没有空档，Actions 的 cron 延迟也不会漏内容；重叠部分由跨天去重处理。

**信源**（`sources.yaml`，立项书 7.1）：

| type | 信源 | 说明 |
|---|---|---|
| `rss` | OpenAI、Google DeepMind、Google AI、Hugging Face Blog、arXiv | arXiv 每天数百篇，默认关闭 |
| `html_listing` | Anthropic News / Research、Mistral | 没有 RSS，按链接定位卡片，日期只精确到天 |
| `hf_daily_papers` | Hugging Face Daily Papers | 带 upvotes、代码仓库 |
| `github_releases` | vLLM、Ollama、llama.cpp、transformers 等 | 跳过 draft 和 pre-release |
| `github_trending` | GitHub Trending | 只保留 AI 相关、当日 star 达到阈值的 |
| `hf_trending_models` | Hugging Face Trending Models | 过滤量化 / 合并 / 适配器，以及创建超过 14 天的 |
| `hackernews` | Hacker News（Algolia API） | Tier 2，AI 相关且分数达到阈值 |
| `reddit` | r/LocalLLaMA、r/MachineLearning | Tier 2，RSS（JSON API 拒绝匿名的云端请求） |

Meta AI、Qwen、DeepSeek 暂时没有可抓的官方列表页（JS 渲染或没有博客），由 HF Trending、GitHub 和 HN 覆盖。

**去重**（`daily/dedup.py`）分三层：

1. **同一页面**：URL 归一化（去 tracking 参数、`www.`、结尾斜杠；arXiv abs/pdf/版本号和 HF Papers 页面统一成 `arxiv:ID`）。同一个 key 的记录合并成一条：tier 小的当主记录，同 tier 按 `sources.yaml` 中的顺序；其他记录放进 `also_from`，HN 分数等热度信号并入 `signals`。
2. **同一事件**：标题词重合度 + 共同的模型名（`gpt-6`、`qwen3.5`、`deepseek-v4.1`……）。相似的候选会拿到同一个 `cluster_id`。聚类只是给编辑的提示，不会合并条目。
3. **跨天**：过去 7 天的 `candidates.json` 里出现过的，在 `seen_on` 里记下日期；过去 7 天 `digest.json` 里已经发布过的，直接丢弃（记录在 `dropped`）。

## candidates.json

```jsonc
{
  "schema_version": 1,
  "date": "2026-10-21",                     // 期号（北京时间）
  "generated_at": "...",
  "window": {"start": "...", "end": "..."}, // UTC
  "stats": {"raw": 102, "after_url_merge": 101, "dropped_already_published": 0,
            "candidates": 101, "clusters": 3, "seen_before": 0},
  "sources": [{"id": "openai-news", "status": "ok|error|disabled", "count": 2, "seconds": 1.0, "error": null}],
  "clusters": [{"id": "k_...", "title": "...", "candidate_ids": ["c_...", "c_..."]}],
  "dropped": [{"id": "c_...", "title": "...", "url": "...", "published_on": "2026-10-20"}],
  "candidates": [{
    "id": "c_6ecc1d71a5",                   // 由 URL key 生成，跨天稳定
    "source": "openai-news", "source_name": "OpenAI News", "tier": 1,
    "kind": "blog|paper|release|model|repo|discussion",
    "title": "...", "url": "...", "summary": "...",
    "published_at": "...", "published_precision": "second|day",
    "discussion_url": null, "signals": {"hn_points": 812}, "tags": [],
    "key": "openai.com/index/...", "cluster_id": "k_...",
    "also_from": [{"source": "hackernews", "url": "...", "title": "...", "discussion_url": "..."}],
    "seen_on": ["2026-10-20"]
  }]
}
```

## digest.json 与质量闸门

编辑（Claude）只负责写，能不能发布由 `daily validate`（`daily/digest.py`）决定。不合格的条目整条删掉并记录原因，不会被“修正”（立项书原则 5）：

| 检查 | 不通过时 |
|---|---|
| 结构：schema_version、期号、mode、版块、标题 / 摘要长度、正文里不能有链接 | 条目删除；整期结构错误则整期不合格 |
| 每个来源都是候选，或是编辑记录在 `research` 里、用 WebFetch 打开过的页面 | 条目删除 |
| 至少有一个一手来源，不能只有 HN / Reddit 讨论帖 | 条目删除 |
| 同一个候选只能用一次 | 后出现的条目删除 |
| 正文里的每个数字、模型名 / 版本号（`GPT-6`、`Qwen3.5-72B`、`v2.1.305`、`128K`）都要出现在所引候选的标题 / 摘要或 evidence 引文里 | 条目删除 |
| `--check-links`：链接不是 404 / 410；evidence 引文确实出现在页面上（403 等打不开的页面只给警告） | 条目删除 |
| 今日要点里的数字和模型名必须来自入选条目；正式版至少 3 条有效条目 | 整期不合格 → `degrade` |

编辑预算（立项书待决 2，暂定）：每期 WebFetch ≤ 20 次、WebSearch ≤ 5 次，超出时 validate 只给警告。

`degrade` 不用 LLM：官方博客优先，再按热度信号挑各类候选的前几名，保留英文原标题和链接。

## 定时抓取

抓取在 GitHub Actions 里跑，不在 Claude 的定时任务里：Claude cloud session 访问不了其他仓库的 GitHub API，Reddit 也会拒绝它的请求；Actions 自带 `GITHUB_TOKEN`，网络不受限制。

`.github/workflows/fetch.yml` 每天北京时间 05:07 运行 `daily fetch`，把 `data/YYYY-MM-DD/candidates.json` 提交到 main。05:30 的 Claude 编辑任务直接从仓库读取。没有拿到任何内容时 job 失败，GitHub 会发通知。也可以在 Actions 页面手动触发，指定期号日期补抓。

## 发布（M3）

| 北京时间 | 谁 | 做什么 |
|---|---|---|
| 05:07 | Actions `fetch.yml` | 抓取，把 `candidates.json` 提交到 main |
| 05:30 | Claude 定时任务（每次新开一个 cloud session） | 运行 daily-editor skill，把 `digest.json` 推到本会话的 `claude/` 分支 |
| 推送后 | Actions `ingest.yml` | 用 main 上的候选重新校验，按规则并入 main，启动 `pages.yml` |
| 06:30 | Actions `fallback.yml` | 当天没有合格的 digest 就发布降级版，提交并启动 `pages.yml` |
| 之后 | Actions `pages.yml` | `daily build` → GitHub Pages |

- **为什么要 ingest**：cloud session 只能推送到它自己的 `claude/` 分支。ingest 只从分支拿 `data/*/digest.json`，其他改动不会进入 main。也可以在 Actions 页面手动运行 ingest，指定分支名，补收没有触发它的分支。
- **为什么用 workflow_dispatch 串起来**：用 `GITHUB_TOKEN` 推送的提交不会触发其他 workflow（workflow_dispatch 除外），所以 ingest 和兜底提交之后用 `gh workflow run pages.yml --ref main` 启动构建。人推到 main（合并 PR）会直接触发 `pages.yml`。
- **并入规则**（`daily/publish.py`）：正式版替换降级版（编辑在 06:30 之后才完成），降级版不会覆盖正式版，正式版只会被更新的正式版替换（重做）。
- **告警**（Actions 失败 → GitHub 发通知）：`fetch` 没有拿到任何内容；06:30 时连 `candidates.json` 都没有；连续两天都是降级版。
- **一次性设置**：仓库 Settings → Pages → Source 选 **GitHub Actions**。

网站（`daily/site.py`，样式在 `daily/static/style.css`）：首页是最新一期全文和最近 30 天的列表，每期一页，存档页按月列出全部历史，信息源页用卡片列出白名单和最近 30 期的抓取成功次数、平均候选数、入选条目数。降级版在标题旁、正文顶部和 RSS 标题里都有标注。只发布能通过 `validate`（离线部分）的 digest。RSS 的 guid 带上 mode，降级版被正式版替换后，阅读器会把正式版当作新条目收到。

## 目录

```
daily/
  cli.py            python -m daily 入口
  pipeline.py       并发抓取、信源隔离、写 candidates.json
  dedup.py          URL 合并、标题聚类、跨天去重
  digest.py         digest.json schema 与 validate
  fallback.py       降级版
  render.py         digest.json → Markdown
  site.py           静态网站和 RSS（daily build）
  publish.py        编辑分支的 digest 能不能并入 main（daily adopt）
  static/           网站样式
  throttle.py       同一主机的请求间隔、429 重试
  window.py         期号时间窗口
  text.py           文本清洗、日期解析
  fetchers/         各类信源
sources.yaml        信源白名单
.claude/skills/daily-editor/   编辑 skill
data/YYYY-MM-DD/    每期的 candidates.json、digest.json、digest.md
```
