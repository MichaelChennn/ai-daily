# 候选新信源调研（#46）

调研日期：2026-11-03（柏林时间晚上）。「最近 30 天」指 2026-10-04 到 2026-11-03。

方法：

- RSS 用项目自己的 `daily.pipeline.make_client()`（UA `ai-daily/<ver> (+https://github.com/MichaelChennn/ai-daily)`）请求，再用 `daily.fetchers.feeds.entry_datetime` 解析日期。所以「有没有时刻」看的是 `fetch_rss` 实际拿到的值，00:00:00 算没有时刻。
- 列表页用 `daily.fetchers.html_listing.fetch_html_listing` 实测，窗口放宽到 30 天。「能解析」的意思是这个 fetcher 原样就能产出带日期的候选，不是肉眼看 HTML 得出的。
- 请求都从本机（家用宽带 IP）发出，**没有在 GitHub Actions 上跑过**。「Actions 能否抓」一栏根据三点判断：响应里有没有 Cloudflare / 验证码拦截；要不要跑 JS；两个跑在 Actions 上的 RSS 生成仓库的运行记录（[alan-turing-institute/ai-rss-feeds](https://github.com/alan-turing-institute/ai-rss-feeds)、[Olshansk/rss-feeds](https://github.com/Olshansk/rss-feeds)，见第 2 节）。
- 「fetcher」一栏写的是现有的 `type`（`rss`、`html_listing`、`github_releases`、`github_trending`、`hf_daily_papers`、`hf_trending_models`、`hackernews`、`reddit`）。现有 type 都不合适的，写成「新 type：…」。

## 结论速览

**零代码就能加（只改 `sources.yaml`）**

| 优先级 | 信源 | type | 30 天篇数 | 性质 |
| --- | --- | --- | --- | --- |
| 高 | Google Research Blog `https://research.google/blog/rss/` | rss | 10 | 一手（研究） |
| 高 | Ai2 `https://allenai.org/rss.xml` | rss | 13 | 一手 |
| 高 | Claude 博客 `https://claude.com/resources/articles` | html_listing | 10 | 一手（产品发布） |
| 中 | Microsoft Research `https://www.microsoft.com/en-us/research/feed/` | rss | 10 | 一手（研究） |
| 中 | Apple ML Research `https://machinelearning.apple.com/rss.xml` | rss | 10 以上 | 一手（研究） |
| 中 | Cohere `https://cohere.com/blog` | html_listing | 18 | 一手，标题带杂质 |
| 中 | Black Forest Labs `https://bfl.ai/blog` | html_listing | 1 | 一手（FLUX） |
| 中 | Liquid AI `https://www.liquid.ai/news/models` | html_listing | 4 | 一手 |
| 中 | 博主，tier 2：Simon Willison（entries）、Interconnects、Import AI、Latent Space、Sebastian Raschka、Karpathy | rss | 见第 1 节 | 评论 / 周报 |
| 低 | NVIDIA Blog `https://blogs.nvidia.com/feed/` | rss | 约 40（feed 只留 18 条） | 一手，偏企业宣传 |
| 低 | Cursor `https://cursor.com/blog` | html_listing | 3 | 一手，标题带杂质 |

**要写一个新 type 才能接（值得做）**

- **Qwen**：`qwen.ai` 背后有匿名可用的 JSON 接口 `https://qwen.ai/api/v2/article/retrieval?type=qwen_ai&language=en-US`，返回 40 篇，每篇带精确到秒的发布时间（在 `article:published_time` 里）。#15 认为「Qwen 没有可抓的列表页」，这个结论现在可以推翻了。需要一个通用的 `json_api` 类 fetcher。
- **字节 Seed**：`https://seed.bytedance.com/api/get_article_list_v2?article_type=2&count=30&order_desc=true`，匿名 GET 就能用，带 `PublishDate`（毫秒时间戳，只到天）。可以和 Qwen 共用同一个 `json_api` fetcher。
- **周末论文**：HF `daily_papers?week=YYYY-Www`（第 5 节）。只需给 `hf_daily_papers` 加个选项，不用新 type。

**暂不加**：xAI（Cloudflare 403，要伪装 Chrome 的 TLS 指纹）、腾讯混元、阶跃、小米 MiMo、美团 LongCat（都是 JS 渲染，没找到公开接口）、Microsoft AI（列表页没有日期）、Perplexity（JS + 验证码）、The Batch（在 Actions 上会被拦）、Google Developers Blog（feed 没有日期）、Stability 和百度 ERNIE（能抓，但 30 天里 0 篇）。

**中文版**：DeepSeek、MiniMax 的中英文列表一模一样，Kimi 没有中文博客，**这三家都不用换**。中文明显更全的是智谱（`docs.bigmodel.cn` 的更新日志有 26 条，英文版只有 8 条）和阿里云百炼的「新模型上线」页（中文版比英文版早一天，也更全），但这两页都没有单篇 URL，`html_listing` 用不了。

**周末论文**：现在**周日和周一**这两期的 HF 论文是 0 篇，不是周六和周日（原因见第 5 节）。建议周日、周一这两期改用 HF 的周榜（`?week=`），去重会排除已经发过的论文。arXiv 只能补上周一，周日还是空的。

---

## 1. 博主和 newsletter

### #20 名单复查

| 博主 | feed | 30 天 | 最新一篇 | 时刻 | 备注 |
| --- | --- | --- | --- | --- | --- |
| Simon Willison（长文） | `https://simonwillison.net/atom/entries/` | 7 | 11-03 | 有 | 推荐用这个 |
| Simon Willison（全部） | `https://simonwillison.net/atom/everything/` | 30 条只覆盖 13 天，按比例约 70 | 11-03 | 有 | 含短链和引用，噪声大 |
| Interconnects | `https://www.interconnects.ai/feed` | 7 | 10-30 | 有 | |
| Latent Space | `https://www.latent.space/feed` | 20 条只覆盖 12 天，按比例约 50 | 11-03 | 有 | 混有每天一期的 **[AINews]** 汇总和播客。AINews 原来的 `news.smol.ai/rss.xml` 2026-09-09 以后停更，搬到了这里 |
| Import AI | `https://importai.substack.com/feed` | 5 | 11-02 | 有 | 周更 |
| Sebastian Raschka | `https://magazine.sebastianraschka.com/feed` | 1 | 10-24 | 有 | |
| Karpathy | `https://karpathy.bearblog.dev/feed/` | 1 | 10-31 | 有 | |
| Lilian Weng | `https://lilianweng.github.io/index.xml` | 0 | 07-04 | 无（53 条里只有 4 条有时刻） | |
| Thinking Machines | `https://thinkingmachines.ai/blog/index.xml` | 0 | 07-31 | 无 | |
| Answer.AI | `https://www.answer.ai/index.xml` | 0 | 08-18 | 有 | |
| Sam Altman | `https://blog.samaltman.com/posts.atom` | 0 | 04-10 | 有 | 响应头是 `text/html`，但 feedparser 能解析 |
| Ethan Mollick | `https://www.oneusefulthing.org/feed` | 1 | 10-20 | 有 | |

全部返回 200，都能解析。Substack（Interconnects、Latent Space、Import AI、Raschka、Mollick）、bearblog 和 GitHub Pages 都没有拦截 bot 的迹象。

低频的五个（Lilian Weng、Thinking Machines、Answer.AI、Altman、Mollick）一个月 0 到 1 篇，加上也不会添噪声。不过 `rss` fetcher 只看窗口，不需要设 `max_age_days`，#20 担心的「低频博客 `max_age_days` 怎么设」其实不存在。

### 补充候选

| 名称 | feed | 30 天 | 时刻 | 性质 | 建议 |
| --- | --- | --- | --- | --- | --- |
| 科学空间（苏剑林） | `https://kexue.fm/feed` | 5 | 有 | 中文，一手研究笔记（注意力、优化器） | **推荐**，tier 2 |
| Recode China AI | `https://recodechinaai.substack.com/feed` | 8 | 有 | 英文周报，专写中国 AI（例：10-25 那期写了 DeepSeek 150 亿美元融资、K3.1 Pro） | 推荐，能补上中国厂商没有 feed 的空缺 |
| ChinAI（Jeffrey Ding） | `https://chinai.substack.com/feed` | 5 | 有 | 英文周报，翻译中文报道，偏政策和产业 | 可选 |
| SemiAnalysis | `https://newsletter.semianalysis.com/feed` | 9 | 有 | 算力 / 产业分析，正文多数付费 | 可选 |
| Dwarkesh | `https://www.dwarkesh.com/feed` | 3 | 有 | 访谈，近期多是非 AI 话题 | 不推荐 |
| Zvi Mowshowitz | `https://thezvi.substack.com/feed` | 20 条只覆盖 26 天 | 有 | 超长评论，话题杂 | 不推荐 |
| Hamel Husain | `https://hamel.dev/index.xml` | 1 | 有 | evals 实践 | 可选，低频 |
| 宝玉 | `https://baoyu.io/feed.xml` | 1 | 无 | 中文，以翻译和提示词为主 | 不推荐 |
| 量子位 | `https://www.qbitai.com/feed` | feed 只留 10 条，都是当天的，估计每天 20–30 条 | 有 | 中文媒体，混有汽车、硬件 | 不推荐当信源（量太大、是二手内容） |
| 机器之心 | `https://www.jiqizhixin.com/rss` | — | — | 返回 HTML，不是 feed | 不可用 |
| 极客公园 / 爱范儿 / InfoQ / 开源中国 / 少数派 | 各自的 `/feed`、`/rss` | 都能用，每天十几到几十条 | 有 | 综合科技媒体，AI 只占一部分 | 不推荐 |
| BestBlogs.dev | `https://www.bestblogs.dev/feeds/rss` | 100 条只覆盖 1 天 | 有 | 中文聚合，混有腾讯新闻、光明网 | 不推荐 |
| TLDR AI | 第三方生成的 feed（见第 2 节） | 20 | 无 | 每日汇总 | 不推荐（二手） |
| Eugene Yan / Chip Huyen / BAIR | `eugeneyan.com/rss/`、`huyenchip.com/feed.xml`、`bair.berkeley.edu/blog/feed.xml` | 0 / 0 / 0 | | | 停更或很低频 |

中文 AI 圈的一手内容（新智元、Founder Park、海外独角兽、各厂商公众号）基本都只发微信公众号，没有可以合规抓取的 feed。

---

## 2. GitHub 上的 AI RSS 合集

| 仓库 | 星数 | 最后推送 | 做法 |
| --- | --- | --- | --- |
| [Olshansk/rss-feeds](https://github.com/Olshansk/rss-feeds) | 733 | 2026-11-03 | 在 Actions 上给没有 RSS 的博客生成 feed（requests 或 selenium） |
| [alan-turing-institute/ai-rss-feeds](https://github.com/alan-turing-institute/ai-rss-feeds) | 43 | 2026-11-03 | 在 Actions 上用 Scrapy 每 3 小时生成一次（`cron: "41 1/3 * * *"`），配置在 `feeds.toml` |
| [leontloveless/ai-rss-feeds](https://github.com/leontloveless/ai-rss-feeds) | 49 | 2026-11-03 | 用 LLM 生成选择器，再定时抓取 |
| [plenaryapp/awesome-rss-feeds](https://github.com/plenaryapp/awesome-rss-feeds) | 2867 | 2026-10-05 | 通用 OPML，没有 AI 专题 |
| [RSS-Renaissance/awesome-AI-feeds](https://github.com/RSS-Renaissance/awesome-AI-feeds) | 100 | 2019-02 | 早就没人维护 |

### 从这些合集里找到、我们还没有的

Ai2、Cohere、Claude 博客、Anthropic Engineering、xAI、The Batch、Stability、Cursor、Groq、Ollama 博客、OpenAI 的 Developer / Engineering / Research 子栏目、AISI、Mila、EleutherAI、Goodfire、Transluce、FAR.AI。Ai2 到 Cursor 在第 3 节逐个验证了（Anthropic Engineering 其实已经被 `anthropic-research` 覆盖）。Groq、Ollama、OpenAI 子栏目（主 feed 已经在用）和 AISI 以下的研究机构、安全组织，这次没有验证。

### 这些合集透露的「能不能在 Actions 上抓」

这是本次最有用的旁证，因为它们就跑在 GitHub Actions 的机房 IP 上：

- **x.ai**：ATI 在 `feeds.toml` 里给 `spacex-ai-news` 配了 `impersonate = "chrome"`（用 curl_cffi 伪装 Chrome 的 TLS 指纹）才抓得到；Olshansk 的 xAI feed 标着「updates paused: browser navigation times out in CI」。说明普通 httpx 在 Actions 上也会被拦。（xAI 新闻页现在的品牌是「SpaceX AI」。）
- **The Batch**：Olshansk 写的是「Paused: publisher challenges GitHub requests」，ATI 也标了 `broken = true`（最新一条停在 2026-07-03）。**从 Actions 抓 The Batch 会被拦**，虽然本机能抓。
- **Perplexity Hub**：Olshansk 写的是「recurring browser challenges block CI」。
- **Cohere、Ai2、Claude 博客、Anthropic News/Research、Mistral**：ATI 的 feed 都更新到了最近几天，说明这些站对 Actions 的 IP 不拦。

### 直接订阅第三方生成的 feed？

技术上可以：把 `rss` 的 `url` 指向 `raw.githubusercontent.com/...`。实测 ATI 的 xAI feed 30 天 6 条。但不建议当主路线：

- 只有日期，没有时刻（日期都是 00:00）；
- 生成频率 3 小时一次，有延迟；
- 依赖别人的仓库，选择器坏了不归我们修，`min_item_count` 一触发 feed 就停更。

xAI 是唯一一个值得这样做的：我们自己确实抓不到，而 ATI 一直在维护它。可以先 `enabled: false` 放着，或者 tier 2 试用。

---

## 3. 各家官方渠道

对照 `sources.yaml`：已经有 OpenAI、Anthropic News/Research、DeepMind、Google AI Blog、Mistral、HF、Meta、MiniMax、Kimi、DeepSeek。

### 海外厂商

| 厂商 | 端点 | type | 30 天 | 时刻 | 一手？ | Actions | 结论 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Google Research | `https://research.google/blog/rss/` | rss | 10 | 有 | 一手 | 应该能（Google 前端，无拦截） | **加**。和 `google-ai-blog` 不重复：这里是研究成果（例：10-27「The sleep framework」） |
| Google Developers | `https://developers.googleblog.com/rss/` | — | — | — | 一手 | — | feed 的 `<item>` 里**没有 `pubDate`**，`fetch_rss` 会全部丢掉。列表页 `/search/?technology_categories=AI` 也解析不出日期。**不加** |
| Ai2 | `https://allenai.org/rss.xml` | rss | 13 | 名义上有（全是 08:00，实际只到天） | 一手（Olmo、olmOCR 等） | ATI 在 Actions 上能抓 `allenai.org/news` | **加**。#15 时没发现这个 feed（链接在 `/news` 页面的 HTML 里）。部分文章也发在 HF 博客，按 URL 去重不会合并，靠编辑判断 |
| Anthropic Engineering | `https://www.anthropic.com/engineering`，`link_pattern: ^/research/[a-z0-9-]+$` | html_listing | 1（10-13 Redesigning source control） | 无 | 一手 | 同 anthropic.com，能 | **不用加**。工程文章的链接现在都在 `/research/` 下面（`/engineering/*` 一篇也匹配不到），而且也出现在 `/research` 列表页上：现有的 `anthropic-research` 实测能抓到 10-13 这一篇，日期正确 |
| Claude 博客 | `https://claude.com/resources/articles`，`link_pattern: ^(https://claude.com)?/(blog\|resources/articles)/[a-z0-9-]+$` | html_listing | 10 | 无 | 一手（产品功能发布，例：11-02 message threads） | ATI 在 Actions 上能抓 | **加**。`claude.com/blog` 会 302 到这里 |
| Microsoft Research | `https://www.microsoft.com/en-us/research/feed/` | rss | 10 | 有 | 一手（研究） | 应该能 | 加，tier 1 |
| Microsoft AI（MAI 模型） | `https://microsoft.ai/blog/`（`/news/` 302 过来） | — | — | — | 一手（MAI-Image、MAI-Code 等模型） | — | 列表页卡片里**没有日期**，只有 JSON-LD 里有页面级日期；`/feed/` 是空 feed；`wp-json` 要登录（401）。**现有 fetcher 接不了**。MAI 的发布大多会同步到 HN、Reddit |
| Microsoft Source · AI | `https://news.microsoft.com/source/topics/ai/feed/` | rss | 4 | 有 | 企业新闻（例：Maia 300 芯片） | 应该能 | 可选 |
| Apple ML Research | `https://machinelearning.apple.com/rss.xml` | rss | 至少 10（feed 只保留 10 条，最早一条 10-12） | 无 | 一手（论文和 MLX） | 应该能 | 加 |
| NVIDIA Blog | `https://blogs.nvidia.com/feed/`（`nvidianews.nvidia.com/releases.xml` 内容一样） | rss | 18 条只覆盖 14 天 | 有 | 一手，但大量行业案例宣传 | 应该能 | 可选，tier 1 但噪声高 |
| NVIDIA Developer | `https://developer.nvidia.com/blog/feed` | rss | 44 | 有 | 一手技术文章（Nemotron 等发布也会出现在这里） | 应该能 | 不推荐，太多 |
| AWS ML Blog | `https://aws.amazon.com/blogs/machine-learning/feed/` | rss | 20 条只覆盖 5 天 | 有 | 一手，以客户案例为主 | 应该能 | 不推荐 |
| xAI / SpaceX AI | `https://x.ai/news` | — | 6（来自 ATI 的 feed） | — | 一手 | **不能**（403 Cloudflare；ATI 要伪装 Chrome TLS） | 自己抓不了；可选用 ATI 的 feed：`https://raw.githubusercontent.com/alan-turing-institute/ai-rss-feeds/refs/heads/main/feeds/spacex-ai-news.xml`，type rss，只有日期 |
| Cohere | `https://cohere.com/blog`，`link_pattern: ^(https://cohere.com)?/blog/[a-z0-9-]+$` | html_listing | 18 | 无 | 一手，混有客户案例 | ATI 在 Actions 上能抓 | 加。**标题会带上「Oct 29, 2026 11 min read」**：卡片里没有 heading，`_title()` 只能取最长的链接文字。要么改 `_title`，要么交给编辑清理 |
| Stability AI | `https://stability.ai/news-updates?format=rss` | rss | 0（最新 08-25） | 有 | 一手 | Squarespace，应该能 | feed 能用，但一个多月没更新。低优先级 |
| Black Forest Labs | `https://bfl.ai/blog`，`^/blog/[a-z0-9-]+$` | html_listing | 1（10-15 FLUX 3 Image Klein） | 有（精确到秒） | 一手 | Vercel，应该能 | 加 |
| Liquid AI | `https://www.liquid.ai/news/models`（`/blog` 会跳到这里），`^/(news\|blog)/[a-z0-9-]+(/[a-z0-9-]+)?$` | html_listing | 4 | 无 | 一手（LFM3 等） | 应该能 | 加，tier 1 |
| Cursor | `https://cursor.com/blog`，`^/blog/[a-z0-9-]+$` | html_listing | 3 | 解析成 12:00 | 一手 | Vercel，应该能 | 可选。和 Cohere 一样，标题会带「Oct 29, 2026 · company」和作者名 |
| ElevenLabs | `https://elevenlabs.io/blog/rss.xml` | rss | 50 | 有 | 以 SEO 文章为主 | 页面有验证码标记 | 不推荐 |
| Runway | `https://runway.com/news` | — | — | — | 一手 | — | 静态 HTML 里只有 1 个文章链接，其余靠 JS。不加 |
| Perplexity | `https://www.perplexity.ai/hub` | — | — | — | — | 不能（见第 2 节） | 不加 |
| Nous Research | `https://nousresearch.com/blog` | — | — | — | — | — | 文章链接在根路径，卡片没有日期。不加 |
| Together AI | `https://www.together.ai/blog/rss.xml` | rss | 5 | 无 | 推理平台，偶尔有研究 | 应该能 | 不推荐 |
| Sakana AI | `https://sakana.ai/feed.xml` | rss | 10 | 有 | 一手，**大多是日文** | 应该能 | 不推荐 |
| The Batch | `https://www.deeplearning.ai/the-batch/`，`^/the-batch/[a-z0-9-]+/?$` | html_listing | 4（周更） | 无 | 周报 | **不能**（见第 2 节） | 不加 |

### 中国厂商

| 厂商 | 端点 | type | 30 天 | 时刻 | 一手？ | Actions | 结论 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Qwen / 阿里** | `https://qwen.ai/api/v2/article/retrieval?type=qwen_ai&language=en-US`（JSON） | **新 type：json_api** | 0（最新 09-20 Qwen-Image-2.1；2026 年大约每月 2–5 篇） | **有**（`article:published_time`，例 `2026-09-20T20:00:00+08:00`） | 一手 | 没有拦截（返回 JSON，无 Cloudflare） | **值得接**。字段：`id`、`title`、`path`（slug）、`content`（整页 HTML，发布时间要从里面的 `<meta>` 取）。旧接口 `/api/page_config?code=research.research-list` 只到 2025-12，别用。文章链接格式这次没确认，大概是 `https://qwen.ai/blog?id=<path>` |
| 阿里云百炼「新模型上线」 | `https://help.aliyun.com/zh/model-studio/newly-released-models` | 新 type：表格型更新日志 | 很多（10 月有 20 多条） | 无 | 一手，但包含第三方模型（Tripo、PixVerse、蚂蚁 Ling） | 应该能 | 每条没有独立 URL，噪声大。不推荐 |
| **字节 Seed** | `https://seed.bytedance.com/api/get_article_list_v2?article_type=2&count=30&order_desc=true`（GET，JSON） | 新 type：json_api | 1（10-13，招聘帖；最近的模型发布是 08-04 SeedRealtime） | 无（`PublishDate` 是北京时间零点） | 一手（Seedance、Seed 系列） | 没有拦截 | 和 Qwen 一起做。文章链接：`https://seed.bytedance.com/en/blog/<TitleKey>`。返回里同时有中英文标题 |
| 智谱 | `https://docs.bigmodel.cn/cn/update/new-releases`（中文）、`https://docs.z.ai/release-notes/new-released`（英文） | 新 type：changelog | 0（最新 08-26 GLM-5.3-Flash） | 无 | 一手 | 应该能（Mintlify 文档站） | 每条只有页内锚点（`#2026-08-26`），没有单篇 URL。`zhipuai.cn/zh/news` 是公司新闻，最新一条停在 03-31。`z.ai/blog` 404。暂不加，靠 HF Trending |
| 百度 ERNIE | `https://ernie.baidu.com/blog/index.xml`（中文 `/blog/zh/index.xml`） | rss | 0（最新 05-09） | 无 | 一手 | 应该能 | feed 能用，但近半年没更新。低优先级，可以 tier 1 挂着 |
| 腾讯混元 | `https://hunyuan.tencent.com/` | — | — | — | — | — | 整站是 SPA。博客列表接口在懒加载的 JS chunk 里，这次没找到能匿名访问的。不加；靠 GitHub `Tencent-Hunyuan`、HF Trending |
| 阶跃星辰 | `https://www.stepfun.com/news` | — | — | — | — | — | SPA，新闻列表直接写死在 JS bundle 里（`assets/images/news/...`）；`stepfun.ai/news` 跳到平台首页。不加 |
| 小米 MiMo | `https://mimo.xiaomi.com/` | — | — | — | — | — | SPA，只有 `#blog` 锚点。不加 |
| 美团 LongCat | `https://longcat.chat/` | — | — | — | — | — | SPA。不加 |

### 需要的新 type：`json_api`

Qwen 和 Seed 都是「GET 一个 JSON → 一个数组 → 每项有标题、slug、时间」，可以写一个通用 fetcher，选项大致是：

```yaml
type: json_api
url: https://seed.bytedance.com/api/get_article_list_v2?article_type=2&count=30&order_desc=true
items: sub_article_list            # 数组所在的路径
title: ArticleSubContentEn.Title
date: ArticleMeta.PublishDate      # 毫秒时间戳 / ISO 字符串
link: https://seed.bytedance.com/en/blog/{ArticleSubContentEn.TitleKey}
```

Qwen 多一个麻烦：日期不在 JSON 字段里，而在 `content` 里那段 HTML 的 `<meta property="article:published_time">` 里，要么支持「从字段里用正则取」，要么给 Qwen 单独写一个 fetcher。这两个接口都是网站前端自己用的、没有文档，随时可能改；用了要接受这一点，失败时会显示在 `candidates.json` 的 `sources` 里。

alphaXiv（第 5 节）也能用同一个 fetcher。

---

## 4. 中文版值不值得换

| 厂商 | 中文端点 | 和英文比 | 结论 |
| --- | --- | --- | --- |
| DeepSeek | `https://api-docs.deepseek.com/zh-cn/news/news250120`，`^/zh-cn/news/news[0-9]+/?$` | 同样 19 篇，日期完全一样（最新 10-17） | **不换**。另外，TLDR AI 11-02 写到「DeepSeek super agent」，但 DeepSeek 的新闻侧栏里没有：这个新闻页只记 API 和模型的发布 |
| MiniMax | `https://www.minimax.cn/blog`（`minimaxi.com` 会跳过去），`^/blog/[a-z0-9-]+$` | 同样 14 篇，日期一样；只有 H3 一篇中文版带时刻（03:38），英文版是 00:00 | **不换**。`/news` 的中英文版都是 JS 渲染 |
| Kimi | `https://www.kimi.com/blog/`、`/zh/blog/` | 没有中文博客：`/blog/` 页面上的文章链接都指向 `/en/blog/`，`/zh/blog/` 跳到首页 | **不换**。中文的 `platform.kimi.com/blog`（开放平台博客）最新一篇是 2025-11-07，停更了 |
| 智谱 | `docs.bigmodel.cn` 更新日志 | 中文 26 条，英文 8 条：中文多了 GLM-5V-Turbo、GLM-5-Turbo、GLM-OCR、GLM-4.7-Flash、TTS/ASR 等。同一个 GLM-5.3，中文写 8-19，英文写 08-18 | 中文**更全**，但没有单篇 URL，现在接不了 |
| Qwen | 同一接口加 `language=zh-CN` | 同样 40 篇 | 中英文一样，用英文 |
| 阿里云百炼 | 中文 `help.aliyun.com` vs 英文 `alibabacloud.com/help/en` | 中文最新 10-29（蚂蚁 Ling-3.1-flash），英文最新 10-27；英文版还按 International 区域过滤过 | 中文**更早更全**，但这一页本身就不推荐接 |
| 百度 ERNIE | `/blog/zh/index.xml` | 同样 18 篇 | 一样 |
| Cursor | `https://cursor.com/cn/blog` | 同样 15 篇，同一天 | 不相干，用英文 |

总的来说：已经接入的三家（DeepSeek、MiniMax、Kimi）**换中文版没有收益**。中文更全的只有智谱和阿里云这种「文档站更新日志」，它们的问题是结构（没有单篇 URL），换语言解决不了。英文版日报直接引用英文原文也更顺。

---

## 5. 周末的论文来源

### 现在到底哪几期是空的

`hf_daily_papers` 取的是 `(window.end - 12h)` 那一天的 HF 列表，也就是期号的前一天。HF 周六、周日都没有列表（实测 10-17/18、10-24/25、10-31/11-01 都是 `n=0`），所以空的是**周日期和周一期**：

| 期号 | 星期 | hf-daily-papers 条数 |
| --- | --- | --- |
| 10-25 | 日 | 0 |
| 10-26 | 一 | 0 |
| 11-01 | 日 | 0 |
| 11-02 | 一 | 0 |
| 其他日子 | | 6–37 |

（来自 `data/*/candidates.json`。）

### 几种做法

| 做法 | 端点 | 周日期 | 周一期 | 质量信号 | 代价 |
| --- | --- | --- | --- | --- | --- |
| A. HF 回看最近一个有论文的日子 | `daily_papers?date=<周五>` | 有，但周五的列表周六那期已经用过，去重后几乎什么都不剩 | 同左 | upvotes | 改动小，收益也小 |
| **B. HF 周榜** | `https://huggingface.co/api/daily_papers?week=2026-W44&limit=100` | **有** | **有** | upvotes（W44 第一名 152 票） | 只需给 `hf_daily_papers` 加一个选项，例如「当天列表为空时改取 ISO 周榜」。周日期和周一期的日期都落在同一个 ISO 周（例：10-31、11-01 都属于 W44），周日期拿走前几名之后，周一期靠去重自动往后取 |
| C. arXiv 按分类过滤 | `https://rss.arxiv.org/rss/cs.CL` 等（旧配置里有，`enabled: false`） | **没有**：arXiv「Sunday through Thursday」公告，周五、周六不公告（[arXiv 公告时间表](https://info.arxiv.org/help/availability.html)） | 有：周日晚上的公告（美东 20:00，即柏林周一 02:00）正好落进周一期的窗口 | 没有，cs.CL 一天 381 篇 | 要另做过滤（关键词 / 机构），而且解决不了周日期 |
| D. alphaXiv 热门 | `https://api.alphaxiv.org/papers/v3/feed?pageNum=0&sort=Hot&pageSize=20&interval=3%20Days`（JSON，匿名可用） | 有（滚动 3 天窗口） | 有 | `total_votes`、`visits_count`；还收厂商技术报告（例：11-02 Mistral Large 4） | 新 type `json_api`；接口没有文档 |
| E. papers.cool | `https://papers.cool/arxiv/cs.CL/feed`（Atom，能用） | 跟 arXiv 一样没有 | 有 | 没有 | 只是 arXiv 镜像，不解决问题 |
| — HF「trending」 | `daily_papers?sort=trending` | | | | 返回的结果混着 2024 年的旧论文，不能用 |
| — Papers with Code | `paperswithcode.com` | | | | 已经 302 到 `huggingface.co/papers/trending` |
| — Emergent Mind | `emergentmind.com/feeds/rss` | | | | feed 是空的，首页有验证码标记 |

**建议 B**：它是唯一一个不用新 type、周日和周一都能补上、又自带质量信号的办法。周榜里有周一到周五已经发过的论文，跨天去重会把它们标成已发，剩下的是那一周里当时没过 `min_upvotes`、后来票数涨上来的论文，正好适合周末版「本周回顾」。如果以后做了 `json_api`，可以再加 D 作为 tier 2，补厂商技术报告。

---

## 本次没有核实的

- 所有「Actions 能否抓」都没有在 Actions 上实际跑过，判断依据见开头。最稳的做法是：新信源先加进 `sources.yaml`，跑一两天 `candidates.json` 看 `sources[].status`。
- Qwen 文章的公开 URL 格式（`qwen.ai/blog?id=<path>`）没有在浏览器里确认。
- 腾讯混元的博客 API 没有挖到底，也许存在可以匿名访问的接口。
- 第 2 节列出的研究机构 / 安全组织 feed（AISI、Mila、EleutherAI、Goodfire 等）没有逐个验证。
