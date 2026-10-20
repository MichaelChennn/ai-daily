# ai-daily · AI 科技日报

每天早上 6 点（北京时间）自动生成的中文 AI 技术日报：5 分钟读完，每一条都能追溯到一手来源。

立项书：[docs/charter/00_Project_Charter.md](docs/charter/00_Project_Charter.md)

## 当前进度

| 里程碑 | 状态 |
|---|---|
| M0 立项 | ✅ |
| M1 信源与数据：`daily fetch` + 去重 | 🚧 代码已完成，等待连续 7 天的覆盖率验证 |
| M2 编辑 skill 与质量闸门（`validate`、降级） | — |
| M3 发布（静态站点 + RSS + 定时任务） | — |

## 使用

```bash
pip install -e ".[dev]"

python -m daily fetch                       # 今天这一期 → data/YYYY-MM-DD/candidates.json
python -m daily fetch --date 2026-10-20     # 指定期号（北京时间日期）
python -m daily fetch --only hackernews     # 只跑某个信源，调试用（可重复）

pytest -q && ruff check . && ruff format --check .
```

`GITHUB_TOKEN` 环境变量可选，用于 GitHub Releases（不设置时限额 60 次/小时）。

退出码：`0` 成功（个别信源失败只记录在输出里）；`1` 所有信源都没有拿到内容；`2` 参数错误。

## 流水线

```
sources.yaml ──► fetchers（并发、相互隔离）──► 去重 ──► data/YYYY-MM-DD/candidates.json
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

## 定时抓取

抓取在 GitHub Actions 里跑，不在 Claude 的定时任务里：Claude cloud session 访问不了其他仓库的 GitHub API，Reddit 也会拒绝它的请求；Actions 自带 `GITHUB_TOKEN`，网络不受限制。

`.github/workflows/fetch.yml` 每天北京时间 05:07 运行 `daily fetch`，把 `data/YYYY-MM-DD/candidates.json` 提交到 main。05:30 的 Claude 编辑任务（M2/M3）直接从仓库读取；M1 阶段这些文件用于 7 天覆盖率抽查。没有拿到任何内容时 job 失败，GitHub 会发通知。也可以在 Actions 页面手动触发，指定期号日期补抓。

## 目录

```
daily/
  cli.py            python -m daily 入口
  pipeline.py       并发抓取、信源隔离、写 candidates.json
  dedup.py          URL 合并、标题聚类、跨天去重
  window.py         期号时间窗口
  text.py           文本清洗、日期解析
  fetchers/         各类信源
sources.yaml        信源白名单
data/YYYY-MM-DD/    每期的候选（以及之后的 digest.json）
```
