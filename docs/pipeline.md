# 抓取、去重与质量闸门

从信源到一期日报的数据流。术语（期、信源、候选、条目、主版……）以 [GLOSSARY.md](../GLOSSARY.md) 为准。

```
sources.yaml ──► fetchers（并发、相互隔离）──► 去重 ──► data/YYYY-MM-DD/candidates.json
             ──► 编辑通道（Claude / API）──► digest.json ──► validate ──► render ──► digest.md
                                       （失败时）degrade ──► 降级版 digest.json
```

## 时间窗口

第 D 期覆盖柏林时间 D-1 04:00 到 D 06:00（截止到运行时刻；跟随夏令时，UTC 时刻冬夏相差 1 小时）。比 24 小时多出的 2 小时用来接住上一次运行之后、06:00 之前发布的内容：只要每天在 04:00 之后运行，相邻两期之间就没有空档，Actions 的 cron 延迟也不会漏内容；重叠部分由跨天去重处理。

## 信源类型

`sources.yaml` 里每个信源有一个 `type`，对应 `daily/fetchers/` 里的一个抓取器：

| type | 信源 | 说明 |
|---|---|---|
| `rss` | OpenAI、Google DeepMind、Google AI、Google Research、Microsoft Research、Apple ML Research、Ai2、Thinking Machines、Stability AI、百度 ERNIE、Hugging Face Blog、Meta 新闻室（AI 标签）、xAI（第三方 feed），以及全部博主和周报 | Meta 用新闻室的 AI 标签 feed（ai.meta.com 拒绝非浏览器请求）；xAI 用 alan-turing-institute/ai-rss-feeds 生成的 feed（x.ai 拒绝非浏览器请求）。feed 自己的时钟正好是午夜的条目按「只有日期」处理 |
| `html_listing` | Anthropic News / Research、Claude 博客、Mistral、MiniMax、Kimi、DeepSeek（官网和 API 文档的新闻侧栏）、Black Forest Labs、Liquid AI、Cohere、Cursor | 没有 RSS，按链接定位卡片，日期只精确到天。找不到文章链接时，报错里写上状态码、最终 URL、页面大小、CDN 响应头、链接总数和正文开头 |
| `json_api` | Qwen、字节 Seed | 网站前端用的 JSON 接口（没有文档），数组路径、标题、日期、链接模板写在 `sources.yaml` 里 |
| `hf_daily_papers` | Hugging Face Daily Papers | 带 upvotes、代码仓库。当天列表为空（周末、节假日）时取所在 ISO 周周榜的前 `week_fallback_limit` 篇，带 `signals.week` |
| `github_releases` | vLLM、Ollama、llama.cpp、transformers 等 | 跳过 draft 和 pre-release。窗口之前 3 天内的版本带 `signals.late_release`：之前的候选里没出现过才收，用来接住先发 pre-release、后转正的版本（如 Ollama） |
| `github_trending` | GitHub Trending | 只保留 AI 相关、当日 star 达到阈值的 |
| `hf_trending_models` | Hugging Face Trending Models | 过滤量化 / 合并 / 适配器，以及创建超过 45 天的（`createdAt` 是建仓时间，大厂会提前建私有仓库） |
| `hackernews` | Hacker News（Algolia API） | Tier 2，AI 相关且分数达到阈值 |
| `reddit` | r/LocalLLaMA + r/MachineLearning | Tier 2，RSS（JSON API 拒绝匿名的云端请求）；匿名 RSS 每分钟只给 1 次，两个版合成一个请求 |

`day` 精度的日期按日历日判断：窗口两端碰到的 UTC 和柏林日期，再加窗口开始的前一天（美西晚上发的文章日期是前一天）。

## 去重

`daily/dedup.py` 分三层：

1. **同一页面**：URL 归一化（去 tracking 参数、`www.`、结尾斜杠；arXiv abs/pdf/版本号和 HF Papers 页面统一成 `arxiv:ID`）。同一个 key 的记录合并成一条：tier 小的当主记录，同 tier 按 `sources.yaml` 中的顺序；其他记录放进 `also_from`，HN 分数等热度信号并入 `signals`。
2. **同一事件**：标题词重合度 + 共同的模型名（`gpt-6`、`qwen3.5`、`deepseek-v4.1`……）。相似的候选会拿到同一个 `cluster_id`。聚类只是给编辑的提示，不会合并条目。
3. **跨天**：过去 7 天的 `candidates.json` 里出现过的，在 `seen_on` 里记下日期；过去 7 天 `digest.json` 里已经发布过的，直接丢弃（记录在 `dropped`）。另外回看 30 天的主版 `digest.json`（`--reported-days`，和 7 天分开设置）：候选的链接（含 `also_from`）是某个条目的来源，或者标题和条目标题相近（第 2 层的比较；对不上时去掉中文再比一次，因为候选标题多是英文），就在 `reported_on` 里记下那一期的日期和条目标题。这些候选不丢弃，同一个模型页可能更新了权重，由编辑判断有没有新进展。标题相近不一定是同一件事，编辑要对照旧标题看。

去重之前还有一道**过滤**，由各个抓取器按内容跳过条目，跳过的条目记录在 `filtered` 里：

| 原因 | 信源 | 触发值举例 |
|---|---|---|
| `not_ai` | GitHub Trending、Hacker News | 和 AI 无关（关键词没有命中） |
| `min_stars_today` | GitHub Trending | `stars_today 12 < 20` |
| `min_upvotes` | HF Daily Papers | `upvotes 3 < 5` |
| `max_age_days` | HF Trending Models | `61 days old > 14` |
| `noisy_model` | HF Trending Models | `repo id contains gguf` |
| `exclude_title` | 配了 `exclude_title_pattern` 的 RSS（Latent Space） | `title matches ^\[AINews\]` |

时间窗口之外的、缺标题或链接的条目本来就不是候选，不记录。Hacker News 的 `min_points` 由 Algolia 在服务器端过滤，分数不够的帖子我们看不到，也就无法记录。

## candidates.json

```jsonc
{
  "schema_version": 1,
  "date": "2026-10-21",                     // 期号（柏林时间）
  "generated_at": "...",
  "window": {"start": "...", "end": "..."}, // UTC
  "stats": {"filtered": 40, "raw": 102, "after_url_merge": 101, "dropped_already_published": 0,
            "candidates": 101, "clusters": 3, "seen_before": 0, "reported_before": 0},
  "sources": [{"id": "openai-news", "status": "ok|error|disabled", "count": 2, "seconds": 1.0, "error": null,
               "filtered": {"not_ai": 12}}],     // 按原因计数；有生成记录之前的期没有这个字段
  "clusters": [{"id": "k_...", "title": "...", "candidate_ids": ["c_...", "c_..."]}],
  "filtered": [{"source": "github-trending", "title": "owner/repo", "url": "...",
                "reason": "min_stars_today", "value": "stars_today 12 < 20"}],
  "dropped": [{"id": "c_...", "title": "...", "url": "...", "published_on": "2026-10-20"}],
  "candidates": [{
    "id": "c_6ecc1d71a5",                   // 由 URL key 生成，跨天稳定
    "source": "openai-news", "source_name": "OpenAI News", "tier": 1,
    "kind": "blog|paper|release|model|repo|commentary|discussion",
    "title": "...", "url": "...", "summary": "...",
    "published_at": "...", "published_precision": "second|day",
    "discussion_url": null, "signals": {"hn_points": 812}, "tags": [],
    "key": "openai.com/index/...", "cluster_id": "k_...",
    "also_from": [{"source": "hackernews", "url": "...", "title": "...", "discussion_url": "..."}],
    "links": ["https://github.com/..."],
    "seen_on": ["2026-10-20"],
    "reported_on": [{"date": "2026-10-12", "title": "以前主版里的条目标题"}]   // 引入这个字段之前的期没有
  }]
}
```

## digest.json 与质量闸门

编辑通道只负责写，能不能发布由 `daily validate`（`daily/digest.py`）决定。不合格的条目整条删掉并记录原因，不会被“修正”（立项书原则 5）：

| 检查 | 不通过时 |
|---|---|
| 结构：schema_version、期号、mode、版块、标题 / 摘要长度、正文里不能有链接 | 条目删除；整期结构错误则整期不合格 |
| 每个来源都是候选，或是编辑记录在 `research` 里、用 WebFetch 打开过的页面 | 条目删除 |
| 至少有一个一手来源，不能只有 HN / Reddit 讨论帖、`i.redd.it` / `v.redd.it` 图片和视频或 `x.com` / `twitter.com` 推文（正文下载不到，引文核对不了） | 条目删除 |
| 📄 论文的主来源是 `kind` 为 `paper` 的候选，或 arXiv、HF papers、OpenReview 的链接 | 条目删除 |
| 同一个候选只能用一次 | 后出现的条目删除 |
| 正文里的每个数字、模型名 / 版本号（`GPT-6`、`Qwen3.5-72B`、`v2.1.305`、`128K`）都要出现在所引候选的标题 / 摘要或 evidence 引文里 | 条目删除 |
| `--check-links`：链接不是 404 / 410；evidence 引文确实出现在页面上。拿不到页面文本（403、PDF 等）时只给警告，但这个页面的引文不算材料，支撑不了上一行的数字和名称 | 条目删除 |
| 今日要点里的数字和模型名必须来自入选条目；正式版至少 3 条有效条目 | 整期不合格 → `degrade` |

英文版（`digest.en.json`）用同一套 schema 和检查，标题、摘要的长度上限放宽。

条数目标：期望约 15 条（`ITEMS_EXPECTED`），8–18 条（`ITEMS_TARGET`）；🔥 头条 3–5 条、📄 论文 2–4 篇（`SECTION_TARGETS`）。不符合只给警告，不删条目，也不凑数。

编辑预算（立项书待决 2，暂定）：每期 WebFetch ≤ 30 次、WebSearch ≤ 5 次，超出时 validate 只给警告。

`degrade` 不用 LLM：官方博客优先，再按热度信号挑各类候选的前几名，保留英文原标题和链接。

`validation.dropped` 里每条记下被删条目的标题、版块、原因，以及它用的候选 id（`candidates`，有生成记录之后才有）。

## 生成记录（trace）

validate 只留下最后一轮删掉的条目。编辑过程中的其他步骤（挑了哪些、自检删了什么、每一轮校验删了什么、通道在哪一步失败、adopt 有没有采用）记在每个通道的生成记录里，网站的「生成过程」页（`/<期号>/process/`）和 #25 的统计都读它。格式见 `daily/trace.py` 的模块说明。

| 文件 | 谁写 | 步骤 |
|---|---|---|
| `trace.claude.json` | `daily trace scores`（开始新的记录）和 `daily trace self-check` 由 Claude 写；`daily validate` 每跑一轮自动追加；`degrade --force` 记下失败 | 自检、预检、正式校验、英文版校验 |
| `trace.api.<slug>.json` | `daily edit` 和 `daily edit --en`，成功失败都写 | 无一手来源预先去掉、挑选、超出 18 组截掉、第一稿校验、修改稿校验、英文版校验 |

- **打分**：两个通道都给每个候选打 SKILL.md 第 2 节的三维分数（重要性 0–3、实用性 0–3、新颖性 0–2），写在 `scores` 里。代码不按分数筛选，分数只用来看编辑是怎么选的。有生成记录之前的期没有分数。
- **adopt**：`daily adopt` 把结果（采用 / 不采用和原因）追加进那个通道的生成记录。生成记录跟着日报走：Claude 通道的新稿被采用，`ingest.yml` 用分支上的 `trace.claude.json` 替换 main 上的；没被采用，就保留 main 上原来的，只追加一条「运行被拒」。API 通道每次运行都覆盖自己的 Beta 版，生成记录也一起覆盖，`editor-api.yml` 在模型失败时也提交。
- **导出**：`daily export` 把每期的过程数据写进 `web/data/process/<期号>.json`（格式见 `daily/process.py`）。没有生成记录的旧期，只能从 digest 的 `validation` 推出最后一轮校验，页面上把其他步骤标为「当时未记录」。
