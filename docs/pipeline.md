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
| `rss` | OpenAI、Google DeepMind、Google AI、Hugging Face Blog、Meta 新闻室（AI 标签） | Meta 用新闻室的 AI 标签 feed（ai.meta.com 拒绝非浏览器请求） |
| `html_listing` | Anthropic News / Research、Mistral、MiniMax、Kimi、DeepSeek（API 文档的新闻侧栏） | 没有 RSS，按链接定位卡片，日期只精确到天 |
| `hf_daily_papers` | Hugging Face Daily Papers | 带 upvotes、代码仓库 |
| `github_releases` | vLLM、Ollama、llama.cpp、transformers 等 | 跳过 draft 和 pre-release |
| `github_trending` | GitHub Trending | 只保留 AI 相关、当日 star 达到阈值的 |
| `hf_trending_models` | Hugging Face Trending Models | 过滤量化 / 合并 / 适配器，以及创建超过 45 天的（`createdAt` 是建仓时间，大厂会提前建私有仓库） |
| `hackernews` | Hacker News（Algolia API） | Tier 2，AI 相关且分数达到阈值 |
| `reddit` | r/LocalLLaMA + r/MachineLearning | Tier 2，RSS（JSON API 拒绝匿名的云端请求）；匿名 RSS 每分钟只给 1 次，两个版合成一个请求 |

Qwen（官方列表页是 JS 渲染）、xAI（对非浏览器 UA 返回 403）暂时没有可抓的官方列表页，由 HF Trending、HN 和 Reddit 覆盖。

## 去重

`daily/dedup.py` 分三层：

1. **同一页面**：URL 归一化（去 tracking 参数、`www.`、结尾斜杠；arXiv abs/pdf/版本号和 HF Papers 页面统一成 `arxiv:ID`）。同一个 key 的记录合并成一条：tier 小的当主记录，同 tier 按 `sources.yaml` 中的顺序；其他记录放进 `also_from`，HN 分数等热度信号并入 `signals`。
2. **同一事件**：标题词重合度 + 共同的模型名（`gpt-6`、`qwen3.5`、`deepseek-v4.1`……）。相似的候选会拿到同一个 `cluster_id`。聚类只是给编辑的提示，不会合并条目。
3. **跨天**：过去 7 天的 `candidates.json` 里出现过的，在 `seen_on` 里记下日期；过去 7 天 `digest.json` 里已经发布过的，直接丢弃（记录在 `dropped`）。

## candidates.json

```jsonc
{
  "schema_version": 1,
  "date": "2026-10-21",                     // 期号（柏林时间）
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

编辑通道只负责写，能不能发布由 `daily validate`（`daily/digest.py`）决定。不合格的条目整条删掉并记录原因，不会被“修正”（立项书原则 5）：

| 检查 | 不通过时 |
|---|---|
| 结构：schema_version、期号、mode、版块、标题 / 摘要长度、正文里不能有链接 | 条目删除；整期结构错误则整期不合格 |
| 每个来源都是候选，或是编辑记录在 `research` 里、用 WebFetch 打开过的页面 | 条目删除 |
| 至少有一个一手来源，不能只有 HN / Reddit 讨论帖 | 条目删除 |
| 同一个候选只能用一次 | 后出现的条目删除 |
| 正文里的每个数字、模型名 / 版本号（`GPT-6`、`Qwen3.5-72B`、`v2.1.305`、`128K`）都要出现在所引候选的标题 / 摘要或 evidence 引文里 | 条目删除 |
| `--check-links`：链接不是 404 / 410；evidence 引文确实出现在页面上（403 等打不开的页面只给警告） | 条目删除 |
| 今日要点里的数字和模型名必须来自入选条目；正式版至少 3 条有效条目 | 整期不合格 → `degrade` |

英文版（`digest.en.json`）用同一套 schema 和检查，标题、摘要的长度上限放宽。

编辑预算（立项书待决 2，暂定）：每期 WebFetch ≤ 20 次、WebSearch ≤ 5 次，超出时 validate 只给警告。

`degrade` 不用 LLM：官方博客优先，再按热度信号挑各类候选的前几名，保留英文原标题和链接。
