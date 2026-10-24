# 新信源端点调研（#15）

调研日期：2026-10-25（柏林时间，抓取在 2026-10-24 夜间完成）。所有结论都来自不跑 JS 的直接请求：`curl`，
或者用项目自己的 `daily.pipeline.make_client()`（UA `ai-daily/<ver> (+https://github.com/MichaelChennn/ai-daily)`）。
`html_listing` 能不能用，是把下载的页面喂给 `daily/fetchers/html_listing.py` 里的解析函数实测的，不是凭肉眼看 HTML。

## 结论速览

| 厂商 | 可用端点 | type | 现在就能用？ |
| --- | --- | --- | --- |
| MiniMax | `https://www.minimax.io/blog` | `html_listing` | 需要改动 A（最新两篇会丢日期） |
| Kimi / Moonshot | `https://www.kimi.com/en/blog/` | `html_listing` | 需要改动 A + B（卡片链接没有文字） |
| DeepSeek | `https://api-docs.deepseek.com/news/news250120`（侧栏新闻列表） | `html_listing` | 需要改动 C（日期写成 `2026/10/17`） |
| Meta AI | `https://about.fb.com/news/tag/ai/feed/` | `rss` | 能 |
| Qwen | 无 | — | 官方列表页全靠 JS；GitHub 博客停更于 2025-09-23 |
| xAI | 无 | — | x.ai 对非浏览器 UA 一律 403（Cloudflare） |
| r/MachineLearning | 和 r/LocalLLaMA 合并成一次请求 | `reddit` | 能；建议同时改动 D |

改动 A–D 见文末“需要的代码改动”，都是小改动，A/B/C 都在 `html_listing.py` / `text.py` 里。

## 逐家结果

### MiniMax

- RSS：没有。`/rss.xml`、`/feed` 都 200 但会重定向回首页 HTML；`/news/rss` 是 404。
- `https://www.minimax.io/news`：Next.js 客户端渲染，静态 HTML 里只有导航菜单里的一个 `/news/minimax-speech-28` 链接，列表本身靠 JS 加载。不能用。
- **`https://www.minimax.io/blog`：服务端渲染，能用。** `link_pattern: ^/blog/[a-z0-9-]+$` 能匹配 14 篇，卡片里有 `2026-10-22` 这种日期和摘要。
  - 问题：导航的大菜单里也有最新两篇（M3.1 Flash、H3）的链接，而且在页面里排在卡片前面。`_card()` 从这个帖子的第一个 `<a>` 往外扩，结果扩到的是菜单，拿不到日期，于是 M3.1 Flash（2026-10-19）**在它发布当天会被静默丢掉**。打上改动 A 以后 14 篇都能拿到日期。
  - `/news/*` 下的帖子（比如 Speech 2.8）只出现在导航里、没有日期，`/blog` 抓不到。语音和音乐类的发布会漏，可以接受。
- GitHub `MiniMax-AI`：有 Releases 的仓库（OpenAgentCore、minimax-code）都是工具类小版本，噪声大，不建议加。
- HF `MiniMaxAI`：每月 1–2 个新模型，`hf-trending-models` 已经覆盖。

### Kimi（Moonshot AI）

- `moonshot.ai` 是落地页，链接指向 `kimi.ai`；`www.moonshot.ai/blog` 重定向回首页。`moonshotai.github.io` 只有 883 字节，没有 feed。
- `platform.kimi.ai/blog`（API 平台博客）：有 `/blog/posts/*` 链接，但多是教程和 newsletter，没有日期。不建议。
- **`https://www.kimi.com/en/blog/`：服务端渲染，日期在 HTML 里。** 每张卡片的结构是：

  ```html
  <a href="/en/blog/kimi-k3-1-pro" aria-label="Kimi K3.1 Pro"></a>   <!-- 空的覆盖层链接 -->
  <div><img …></div><div><h4>Kimi K3.1 Pro</h4><p>2026-10-24</p></div>
  ```

  链接本身没有文字也不包含标题，`_defines_post()` 不认它；能被认出来的只有页脚里的 “Kimi K3.1 Pro tech blog” 这种链接，而页脚没有日期。所以现在 7 篇全部是 `None` 日期，**一篇都进不了窗口**。打上改动 A + B 以后 10 篇全部有日期，最新的 Kimi K3.1 Pro 是 2026-10-24。
  - 链接格式：`link_pattern: ^/en/blog/[a-z0-9-]+/?$`。
- GitHub `MoonshotAI`：`kimi-code`、`kimi-cli` 几乎每周发版，属于 CLI 小版本，不建议加。
- HF `moonshotai`：见下文“HF createdAt 的坑”。

### Qwen

- `https://qwenlm.github.io/blog/index.xml`：feed 正常，但最新一条是 2025-09-23（Qwen3Guard），之后就停更了。sources.yaml 注释里的判断仍然成立。
- `qwen.ai/research`、`qwen.ai/blog`：200，但正文是 `g.alicdn.com/qwenweb/qwen-ai-fe/*.js` 渲染出来的，静态 HTML 里没有文章链接，也没有公开的 feed。
- GitHub `QwenLM`：唯一频繁发版的是 `qwen-code`（每天都有 `v0.26.x` / `desktop-v*` / nightly），模型仓库不用 Releases。不建议加。
- HF `Qwen`：新模型很多（9 月 3 个、10 月 1 个），`hf-trending-models` 能抓到热门的那些。
- **结论：Qwen 暂时没有可以确定性抓取的一手列表页**，继续靠 HF Trending、HN 和 Reddit。

### xAI

- `https://x.ai/news`：不管是 curl 默认 UA 还是项目 UA，都返回 `403`（`server: cloudflare`）。只有带浏览器 UA 才会返回 200，而且那份 HTML 交给 `html_listing`（`^/news/[a-z0-9-]+$`）能干净地解析出 87 篇、日期齐全。但伪装浏览器 UA 去绕过 bot 拦截不是“确定性抓取”，本次不采用。
- `/rss.xml`、`/news/rss.xml`：404。
- `https://docs.x.ai/developers/release-notes`：项目 UA 能拿到（200），但只按月份分组（`<h2>October</h2>`），每一条只是 `#grok-47` 这样的页内锚点，没有具体日期和独立 URL。不能用 `html_listing`。
- GitHub `xai-org`：`xai-sdk-python` / `xai-sdk-ts` 每月发版，算是新模型上线的间接信号，价值低。
- HF `xai-org`：只有 grok-1、grok-2 两个模型。
- **结论：xAI 暂时不加。** 以后如果 x.ai 对 bot 放开，或者出了官方 feed，可以直接用上面的 `link_pattern`。

### DeepSeek（复查）

- 官网 `deepseek.com` 没有博客，这一点没变。
- **`api-docs.deepseek.com` 的每个 `/news/*` 页面都带完整的新闻侧栏**，链接文字自带日期：`DeepSeek-V4.1-Flash-1017 Release 2026/10/17`。用 `link_pattern: ^/news/news[0-9]+/?$` 能匹配 19 篇。
  - 问题：`find_date()` 的 `_ISO_DATE` 只认 `YYYY-MM-DD`，`2026/10/17` 不认，所以日期全是 `None`。打上改动 C 以后 19 篇全部有日期。
  - 列表 URL 选一个不会被删的老页面，比如 R1 那篇 `/news/news250120`：它的侧栏和最新那一页完全一样，“上一篇 / 下一篇”指向的也都是老文章，不会干扰标题。首页 `api-docs.deepseek.com/` 的侧栏是折叠的，只有一个链接，不能用。
  - `/news/news250120` 会 302 到带斜杠的版本，`make_client()` 设了 `follow_redirects=True`，没有影响。
  - 标题里会带着日期（`… Release 2026/10/17`），编辑写稿时自己会处理。
- GitHub `deepseek-ai`：有 rc 版（`deepseek-harness`），没有稳定版的模型发布。HF `deepseek-ai`：新模型都会在 HF Trending 冲上去。

### Meta AI（复查）

- `ai.meta.com/blog/`、`ai.meta.com/blog/rss/`、`ai.meta.com/sitemap.xml`：对非浏览器客户端一律 `400`。不可抓。
- **`https://about.fb.com/news/tag/ai/feed/`：Meta 官方新闻室 AI 标签的 RSS，正常可用。** 最近一个月 10 条，里面有 Muse Wonder（2026-10-12）这样的模型发布，也有“数据中心”这类企业新闻。噪声中等，交给编辑打分即可。已经用项目 client 实测：`status=ok`。
- `engineering.fb.com/category/ai-research/feed/`：可用，但内容偏广告系统工程，更新慢（最近一条 10-19，再往前一条 9-02）。不建议。
- HF `meta-llama`：最后一个模型是 2025-04；`facebook` 下是研究小模型。

## r/MachineLearning 的 429

### 实测的限流规则

同一个 IP，匿名请求 `www.reddit.com/r/<sub>/top/.rss`：

```
00:17:45 www-ML  ua=bot     429 used=1 rem=0.0 reset=15
00:17:45 www-LL  ua=bot     429 used=1 rem=0.0 reset=15
00:18:50 www-LL  ua=bot     200 used=1 rem=0.0 reset=10   ← 新的一分钟，第一个请求成功
00:18:55 www-ML  ua=bot     429 used=1 rem=0.0 reset=4    ← 同一分钟里的第二个请求
00:20:01 www-ML  ua=browser 200 used=1 rem=0.0 reset=59
00:20:04 www-LL  ua=browser 429 used=1 rem=0.0 reset=56   ← 换浏览器 UA 也一样
00:21:09 old-ML  ua=bot     403
00:22:18 multi   ua=bot     200 used=1 rem=0.0 reset=42 entries=47
00:22:21 multi   ua=bot     429 used=1 rem=0.0 reset=38
```

- **配额是每分钟 1 次**：成功一次以后 `x-ratelimit-remaining` 立刻变成 `0.0`。`x-ratelimit-reset` 倒数到整分钟，说明窗口是对齐到整分钟的固定窗口。
- **429 响应里没有 `Retry-After`**，只有 `x-ratelimit-reset`。
- **UA 没用**：浏览器 UA 照样 429。
- **old.reddit.com 不行**：直接 403（curl 看到的是 302，跟过去还是 403）。

### 为什么现在 4 天里坏 3 天

`daily/throttle.py` 的 `PoliteTransport` 给 `www.reddit.com` 设了 3 秒间隔，429 时按 `backoff * 2**attempt`（5 秒、10 秒）重试 2 次，因为没有 `Retry-After`。两个 subreddit 的请求间隔 3 秒，第二个基本都落在同一分钟里；5 秒和 10 秒的重试也大概率还在同一分钟。只有前一个请求恰好在整分钟前十几秒发出时，重试才会跨过分钟边界。这和数据对得上：10-22 和 10-24 失败时耗时 18.3 秒（3 + 5 + 10 秒，全部用完），10-23 成功时耗时 8.2 秒（3 + 5 秒，跨过了分钟）。10-21 那次只用了 0.9 秒就失败，是因为它的抓取（2026-10-20 21:19 UTC）比 `throttle.py` 合入（21:29 UTC，commit 2f6d936）早，当时还没有间隔和重试。r/LocalLLaMA 排在前面，总是抢到这一分钟的配额，所以从来没坏过。

### 建议

1. **把两个 subreddit 合成一个请求**：`https://www.reddit.com/r/LocalLLaMA+MachineLearning/top/.rss?t=day&limit=50`。实测 200，47 条，每条都有 `<category term="LocalLLaMA">` / `<category term="MachineLearning">`，能分清来自哪个版。现在的 `fetch_reddit` 直接把 `subreddit: LocalLLaMA+MachineLearning` 拼进 URL 就能跑，唯一的问题是 `signals.subreddit` 会写成合并后的字符串，最好改成读每条的 `entry.tags[0].term`（改动 D 的一半）。
   - 代价：排名混在一起。r/ML 本身每天进 top 的帖子很少（10-23 成功那天 6 条，今天实测 2 条），合并后它们排在后面，但仍然在 50 条以内。
2. **429 时读 `x-ratelimit-reset`**（改动 D 的另一半）：`Retry-After` 缺失时用 `x-ratelimit-reset + 1` 当等待时间，`max_wait` 放宽到 65 秒以上。注意 `SOURCE_TIMEOUT_SECONDS = 60`，单个信源的总时间不能超过它，所以这条只能救“合并后的那一个请求偶尔撞上别人”的情况，救不了两个信源串行排队。这也是第 1 条必须做的原因。
3. 不建议：换 UA、换 old.reddit、OAuth（要注册应用、存 secret，超出“确定性、零配置”的范围）。

## 体检：`data/*/candidates.json`（2026-10-21 至 10-24）

| 信源 | 10-21 | 10-22 | 10-23 | 10-24 | 判断 |
| --- | --- | --- | --- | --- | --- |
| openai-news | 2 | 7 | 2 | 2 | 正常 |
| anthropic-news | 0 | 1 | 2 | 0 | 正常（列表页实测能解析，日期齐全） |
| anthropic-research | 1 | 0 | 1 | 1 | 正常，但有隐患：头图卡片（hero）的第一个 `<a>` 只包着图片、没有日期，现在置顶的 3 篇解析出来都是 `None`。新文章刚好放进 hero 的那天会丢，同样靠改动 A 修复 |
| deepmind-blog | 0 | 0 | 1 | 0 | 正常（feed 最新一条 10-22 14:30，和 10-23 的 1 条对得上） |
| google-ai-blog | 0 | 1 | 0 | 0 | 正常（feed 最新一条 10-21 04:00，和 10-22 的 1 条对得上） |
| mistral-news | 1 | 1 | 0 | 0 | 正常（列表页 92 篇，日期齐全） |
| huggingface-blog | 6 | 4 | 3 | 1 | 正常 |
| hf-daily-papers | 37 | 34 | 36 | 26 | 正常 |
| github-releases | 2 | 6 | 3 | 6 | 正常 |
| github-trending | 12 | 10 | 6 | 5 | 正常 |
| hf-trending-models | 21 | 21 | 23 | 25 | 正常（见下文 createdAt 的坑） |
| hackernews | 6 | 13 | 11 | 6 | 正常 |
| reddit-localllama | 25 | 25 | 25 | 25 | 正常 |
| reddit-machinelearning | **429** | **429** | 6 | **429** | 3/4 失败，原因见上 |
| arxiv-cs-* | 停用 | 停用 | 停用 | 停用 | — |

除了 r/MachineLearning，**没有信源真正失效**。条数为 0 的都是官方博客那天确实没发文：feed 和列表页的最新日期都和每天的窗口对得上。只有 4 天数据，结论只能说明“目前没坏”。

### HF createdAt 的坑（顺带发现）

HF API 的 `createdAt` 是**仓库创建时间**，不是公开时间。大厂会提前建私有仓库：

| 模型 | HF createdAt | 官方发布日 | 差 |
| --- | --- | --- | --- |
| moonshotai/Kimi-K3 | 2026-06-13 | 2026-07-16（kimi.com 博客） | 33 天 |
| moonshotai/Kimi-K2.6 | 2026-04-14 | 2026-04-20 | 6 天 |
| MiniMaxAI/MiniMax-H3 | 2026-07-28 | 2026-07-31 | 3 天 |
| MiniMaxAI/MiniMax-M3.1-Flash | 2026-10-17 | 2026-10-19 | 2 天 |

`hf-trending-models` 的 `max_age_days: 14` 用的就是 `createdAt`，**所以像 Kimi-K3 这样的大发布会被它当成“老模型”过滤掉**。如果以后要写 `hf_org_models` 一类的新抓取器，也会遇到同样的问题。建议先把 `max_age_days` 放宽到 45，后续另开 issue 研究更准的“公开时间”（这次没有找到 HF API 公开提供的字段）。这也是本次**不推荐** HF org 新模型这条路的原因。

## 建议的增删名单

现在启用 14 个，加上停用的 arXiv 3 个，共 17 条。建议改成**启用 17 个、停用 3 个，共 20 条**：

- **新增 4 个**：`minimax-blog`、`kimi-blog`、`deepseek-news`、`meta-ai-news`
- **合并 2 → 1**：`reddit-localllama` + `reddit-machinelearning` → `reddit-ai`
- **不加**：Qwen（无端点）、xAI（403）、各家 GitHub org Releases（都是 CLI 小版本）
- **保留**：其余全部保留，体检没有发现失效的
- **调参**：`hf-trending-models.max_age_days` 从 14 改成 45

前三个新增需要先合入改动 A/B/C，否则它们会一直是 0 条，而且不报错。

### sources.yaml 条目

放在“官方博客（Tier 1）”段落里，`huggingface-blog` 之后：

```yaml
  - id: meta-ai-news
    name: Meta Newsroom · AI
    type: rss # ai.meta.com 对非浏览器客户端返回 400；新闻室的 AI 标签 feed 可用
    tier: 1
    kind: blog
    url: https://about.fb.com/news/tag/ai/feed/
    homepage: https://about.fb.com/news/tag/ai/

  - id: minimax-blog
    name: MiniMax Blog
    type: html_listing # /news 是 JS 渲染，/blog 是服务端渲染
    tier: 1
    kind: blog
    url: https://www.minimax.io/blog
    link_pattern: ^/blog/[a-z0-9-]+$

  - id: kimi-blog
    name: Kimi Blog
    type: html_listing
    tier: 1
    kind: blog
    url: https://www.kimi.com/en/blog/
    link_pattern: ^/en/blog/[a-z0-9-]+/?$

  - id: deepseek-news
    name: DeepSeek News
    type: html_listing # 没有博客；API 文档每页都带完整的新闻侧栏，选一篇老页面当列表
    tier: 1
    kind: release
    url: https://api-docs.deepseek.com/news/news250120
    link_pattern: ^/news/news[0-9]+/?$
    homepage: https://api-docs.deepseek.com/
```

同时把那段注释更新成：

```yaml
  # Qwen（qwenlm.github.io 停更于 2025-09，qwen.ai 是 JS 渲染）、xAI（x.ai 对非浏览器 UA 返回 403）
  # 暂无可抓的官方列表页；它们的发布靠 HF Trending、HN、Reddit 覆盖。
```

社区段落把两个 Reddit 源替换成：

```yaml
  - id: reddit-ai
    name: r/LocalLLaMA + r/MachineLearning
    type: reddit # 匿名 RSS 每个 IP 每分钟只给 1 次，两个版必须合成一个请求
    tier: 2
    kind: discussion
    subreddit: LocalLLaMA+MachineLearning
    limit: 50
```

`hf-trending-models` 改成 `max_age_days: 45`。

## 需要的代码改动

改动 A/B/C 都已经在本地对着保存的页面实测过（monkeypatch 方式，没有改仓库代码）。

- **A. `html_listing`：从“第一个有日期的卡片”取卡片。** 现在 `_card(anchors[0], …)` 只看帖子的第一个 `<a>`。改成按顺序对每个 anchor 求 `_card`，选第一个 `_date()` 不为 `None` 的；都没有日期时再退回 `anchors[0]`。修复 MiniMax 导航链接、Anthropic Research hero 图片链接、Kimi 页脚链接这三种情况。
- **B. `html_listing`：`aria-label` 算链接文字。** `_defines_post()` 里，空链接只要带 `aria-label` 就算帖子链接（标题仍然从卡片里的 heading 取）。修复 Kimi 的覆盖层卡片。
- **C. `daily/text.py`：`_ISO_DATE` 也认斜杠。** 从 `(\d{4})-(\d{2})-(\d{2})` 改成 `(\d{4})[-/](\d{2})[-/](\d{2})`。修复 DeepSeek。
- **D. Reddit：** `fetch_reddit` 的 `signals.subreddit` 改成取每条的 `entry.tags[0].term`（退回到 option）；`PoliteTransport._retry_delay` 在没有 `Retry-After` 时读 `x-ratelimit-reset`，`max_wait` 放宽到约 65 秒。

每个改动都应该配一个用保存的 HTML 片段做输入的测试，放在 `tests/test_fetchers.py` 里现有的 html_listing 测试旁边；改动 D 的重试部分放进 `tests/test_throttle.py`。

## 来源

全部是 2026-10-24 至 25 的一手请求：

- 各厂商页面：上文列出的每个 URL，状态码和结构都是直接请求得到的。
- Reddit 限流：`www.reddit.com` 返回的 `x-ratelimit-used` / `x-ratelimit-remaining` / `x-ratelimit-reset` 响应头（实测日志见上）。
- HF：`https://huggingface.co/api/models?author=<org>&sort=createdAt&direction=-1`。
- GitHub：`https://api.github.com/orgs/<org>/repos?sort=pushed` 和 `/repos/<repo>/releases`。
- 本仓库：`daily/fetchers/html_listing.py`、`daily/fetchers/community.py`、`daily/throttle.py`、`daily/pipeline.py`、`daily/text.py`、`daily/window.py`、`data/2026-10-2{1..4}/candidates.json`。
