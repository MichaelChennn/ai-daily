# 现有信源健康检查（10-21 ~ 11-03）

对应 issue #47（地图 #45）。调查日期 2026-11-03。

## 结论

| 信源 | 结论 | 说明 |
|---|---|---|
| openai-news | **抓漏了** | feed 里时间写成 `00:00:00 GMT` 的文章全部漏掉，两周共 12 篇，包括 *Introducing GPT-6.1 Terra* |
| huggingface-blog | **抓漏了** | 原因同上，HF 官方账号的文章时间都是 `00:00:00`，漏了 6 篇 |
| anthropic-research | **抓漏了**（1 篇） | 只有日期的文章如果发在美西晚上，两期都收不到：11-02 的 *Progress on provable inference* |
| github-releases | **抓漏了**（ollama 4 个版本） | 周末 0 条是真的没有发布。漏掉的是 ollama：先发 pre-release，几小时后才转正式版 |
| deepmind-blog | **抓漏了**（1 篇，原因没查清） | 10-30 14:18 的 *Speeding up planning decisions with AI*，10-31 那期没抓到 |
| deepseek-news | **抓取失败**（CI 上时好时坏） | 失败的 6 期本来也没有新文章，没有实际漏掉内容 |
| minimax-blog | 真没更新 | 最新两篇是 10-19 和 10-22，都早于该信源启用的日期 10-26 |
| kimi-blog | 真没更新 | 最新一篇是 10-24 的 *Kimi K3.1 Pro*，也早于 10-26；再往前一篇是 07-16 |
| meta-ai-news | 真没更新 | 新闻室的 AI 标签两周内只发了 10-28 那一篇，已经抓到 |
| anthropic-news、google-ai-blog、mistral-news | 正常 | 网站上的文章都进了对应的期 |
| hf-daily-papers、hf-trending-models、github-trending、hackernews、reddit-ai | 正常 | 不按发布时间过滤（或网站本身周末不更新），没有发现漏抓 |

meta-ai-news、minimax-blog、kimi-blog、deepseek-news 是 10-25 的 `526d39d` 加进来的，从 10-26 那期开始才有数据，所以"9 期都是 0 条"指的是 10-26 ~ 11-03。

## 方法

- 对每个按时间过滤的信源（RSS、html_listing、github-releases），用仓库里的抓取函数抓一遍网站当前的内容，窗口放宽到 09-01 ~ 11-04，列出所有文章。
- 每篇文章用 `data/<期>/candidates.json` 里记录的窗口算出"应该进哪几期"，再按规范化 URL 去所有期的 `candidates[]` 里查"实际进了哪期、来自哪个信源"。
- github-releases 用 `gh api repos/<repo>/releases?per_page=40` 拿完整列表，按同样的方式对照。
- 对可疑信源单独 curl 原始页面，看日期和链接。
- `uv run python -m daily fetch --date 2026-11-03 --only …` 重跑了 6 个信源，结果写到临时目录，没有覆盖仓库数据。

脚本和输出在本地临时目录，没有提交。

## 1. 逐个信源

### openai-news：`00:00:00` 的文章全部漏掉

OpenAI 的 RSS（`https://openai.com/news/rss.xml`）有一部分文章的 `pubDate` 是当天 `00:00:00 GMT`。这其实只是日期，文章往往在美国白天才发。`fetch_rss` 把所有时间都当作精确到秒（`published_precision` 默认 `second`），于是：

- D 期的窗口是 `[D-1 03:00, D 04:15]` UTC，包含 D 日 00:00，但抓取时（D 日 04:15 UTC，美西前一天晚上）文章还没发；
- D+1 期的窗口从 D 日 03:00 开始，D 日 00:00 不在里面。

两期都收不到。10-21 ~ 11-03 共漏 12 篇，没有一篇 `00:00` 的文章被 openai-news 抓到过：

| feed 时间 | 标题 |
|---|---|
| 10-21 00:00 | Cloudflare links vulnerability discovery to defense with OpenAI |
| 10-21 00:00 | Democratic governance of frontier AI, part II: Empowering cyber defenders |
| 10-22 00:00 | Uber brings ChatGPT Work to all employees with OpenAI |
| 10-23 00:00 | Anima helps clinics cut call waits by 75% with GPT-6 and GPT-Live |
| 10-23 00:00 | OpenAI and Poland's NASK partner to advance AI safety and security |
| 10-26 00:00 | **Introducing GPT-6.1 Terra** |
| 10-27 00:00 | How Check Point accelerates vulnerability research with Daybreak |
| 10-29 00:00 | Credit Saison achieves 954% ROI in a ChatGPT Enterprise pilot |
| 10-30 00:00 | Fair use benefits everyone |
| 11-02 00:00 | OpenAI appoints Dan Driscoll as Senior Counselor for National Security |
| 11-02 00:00 | Qodo builds context into AI code review with Codex |
| 11-03 00:00 | OpenAI appoints Jill Hazelbaker as Chief Corporate Affairs Officer（11-04 那期的窗口从 11-03 03:00 开始，同样会漏） |

另有 10-20 07:00 的 *Terminal X matches senior investor judgment…* 没进 10-21 那期。10-21 那期是本地在 10-20 21:19 跑的，窗口包含 07:00，原因不明，可能是文章后来才进 feed、时间往前写了。

日期带时刻的文章都正常进了对应的期。

### huggingface-blog：同样的 `00:00:00` 问题

HF 官方账号（`huggingface.co/blog/<slug>`，不带组织名）的文章在 feed 里都是 `00:00:00`；社区和合作方的文章（`/blog/<org>/<slug>`）有真实时刻，都抓到了。漏掉的 6 篇：

- 10-23 *Does Your Model Run on AWS Trainium? Look It Up*
- 10-29 *Announcing Project ProtoStar*、*Welcome Le Chonk: Mistral Large 4 on Hugging Face*、*Introducing AnySpeechRecognizer and AnyDecisionModel*
- 11-03 *CWE-bench v2*、*Transformers Model Integration Contracts*（11-04 那期也收不到）

10-20 的三篇 `00:00` 文章被抓到，是因为 10-21 那期是本地 21:19 跑的，那时文章已经发了。

### anthropic-news / anthropic-research：只有日期，美西晚上发的会漏

Anthropic 的列表页只有日期，抓取器记为 `published_precision="day"`，`Window.contains` 接受窗口两端碰到的日期（UTC 和柏林时间）。D 日的文章能进 D 期和 D+1 期。D+1 期在 D+1 日约 04:15 UTC 抓取，也就是美西 D 日晚上 8～9 点，之后发的文章两期都进不去。

- anthropic-news：6 篇都进了期，全部是 D+1 期（10-26 的 S-1 进了 10-27 那期，见第 3 节）。
- anthropic-research：5 篇里 4 篇正常。**11-02 的 *Progress on provable inference for large language models* 没进 11-03 那期**。现在按 11-03 重跑 `fetch --only anthropic-research` 能抓到 1 条，说明 11-03 04:16 抓取时页面上还没有这篇。11-04 那期的日期集合是 {11-03, 11-04}，这篇也会漏。

### mistral-news、google-ai-blog：正常

- mistral-news：10-20 *Voxtral 3*、10-21 *Mistral Advances AI for Engineering with NVIDIA*、10-29 *Le Chonk* 都进了期（只有日期，在 D+1 期）。
- google-ai-blog：3 篇都进了期。

### deepmind-blog：漏了 1 篇，原因没查清

feed 里 10-30 14:18:30 的 *Speeding up planning decisions with AI* 应该进 10-31 那期（窗口 `10-30 03:00 ~ 10-31 04:14`），但 10-31 那期 deepmind-blog 是 0 条。时间是精确的，不是上面的 `00:00` 问题。可能是 feed 当时还没收录这篇（时间往前写了），也可能是 CDN 缓存了旧的 feed。Wayback Machine 没有这几天的 feed 快照，没法确认。其余 4 篇都正常。

### meta-ai-news：真没更新

`https://about.fb.com/news/tag/ai/feed/` 在 10-21 ~ 11-03 只有 10-28 的 *Meta Partners With Five US Universities…* 一篇，已经进了 10-29 那期；上一篇是 10-12 的 *Introducing Muse Wonder*。新闻室全站 feed 同期还有几篇 AI 相关的地区新闻稿（比如 APAC 的 *Muse Is Now Available in Singapore*），没有打 AI 标签，不算漏抓。

`ai.meta.com/blog` 对非浏览器客户端返回 400（sources.yaml 的注释里已经写了）。用 WebFetch 看到的卡片最新是 07 月的，没看到 10-21 之后的文章。我没有尝试绕过它的访问限制。

### minimax-blog：真没更新

`https://www.minimax.io/blog` 是服务端渲染的，抓取器能解析。各文章页面的 `datePublished`：最新两篇是 M3.1 Flash（10-19）和 Code Mini App（10-22 06:32），再往前是 08-13 的 Music 3.0。10-26 启用之后没有新文章。

另外：列表页也链接了 `/news/minimax-speech-28`（01-23），`link_pattern: ^/blog/…` 不收 `/news/` 下的文章。目前没有因此漏掉什么，但 MiniMax 以后在 `/news/` 发东西会漏。

### kimi-blog：真没更新

`https://www.kimi.com/en/blog/` 上的日期依次是 10-24、07-16、04-20……10-24 的 *Kimi K3.1 Pro* 早于启用日期。它在 10-24 那期通过 HN（`kimi.ai/blog/kimi-k3-1-pro`）进了候选。页面写的是北京日期，HN 上 10-23 17:10 UTC 就有了。

### deepseek-news：真没更新，但在 CI 上时好时坏

`api-docs.deepseek.com` 新闻侧栏最新一条是 10-17 的 *DeepSeek-V4.1-Flash-1017 Release*，10-21 之后没有新内容，所以失败的几期没有实际漏掉文章。CI 上的问题见第 2 节。

DeepSeek 11-01 在 X 上发了一篇 *Exploring Super-agent Design*（对应仓库 `deepseek-ai/dsh-superagent-prototype`，10-31 建立），只在 X 上，官网和 API 文档都没有。这是信源覆盖的问题，不是抓取器的问题；这次是 reddit-ai 在 11-02 那期带进来的。

### github-releases：周末真没发布；ollama 漏了 4 个版本

**周末。** 用完整的 releases 列表对照 10-25、11-01、11-02 三期的窗口：14 个仓库里只有 llama.cpp 的 `b12xxx` 自动构建，都是 pre-release，`include_prereleases: false` 按设计不收。周六还有 10-24 01:08 的 langgraph 1.2.17 和 10-31 01:01 的 claude-code v2.1.316，分别进了 10-24 和 10-31 那期。所以周末 0 条是真的没有正式版本。

**ollama。** 下面 4 个版本现在是正式版、在窗口里，但没抓到：

| 版本 | published_at（UTC） | 该进的期 | 那期的抓取时间 |
|---|---|---|---|
| v0.40.9 | 10-22 01:33 | 10-22 | 03:25 |
| v0.40.11 | 10-24 00:30 | 10-24 | 03:23 |
| v0.40.12 | 10-27 00:07 | 10-27 | 04:25 |
| v0.40.14 | 11-03 01:40 | 11-03 | 04:16 |

抓到的 v0.40.8、.10、.13 都是 UTC 白天发的；漏掉的 4 个都在抓取前 2～4 小时。ollama 的习惯是先发 pre-release，测试几小时后再转正式版，`published_at` 不变。抓取时它们还是 pre-release，被跳过；转正后 `published_at` 已经在下一期窗口之前。GitHub API 不提供 pre-release 状态的变更历史，这一点是推断，但时间规律很一致。

**`per_page=10`。** llama.cpp 每天十几个 b-build，最近 10 个全是 pre-release；v0.8.0（10-28 12:47）现在排在第 63 位。这次在第二天 04:19 抓到了，但如果一个正式版之后又有 10 个 build，它就会被挤出第一页。目前没有因此漏掉什么，只是隐患。

### 其他信源

- hf-daily-papers：周末两天是 0，HF 周末不出 Daily Papers（#28 已查过）。
- reddit-ai：每期都是 50 条，正好等于 `limit: 50`，说明每次都被截断。不算故障，但条数上限决定了看得到多少。10-21 ~ 10-24 拆成两个版时，r/MachineLearning 有 3 期是 429，10-26 合并之后没再出现。
- hackernews、hf-trending-models、github-trending：每期都有内容，没有报错。

## 2. deepseek-news 在 CI 上失败

**发生了什么。** `fetch` 工作流里，10-26 ~ 10-30 和 11-03 失败，错误都是 `ValueError: no post links found; page layout may have changed`；10-31、11-01、11-02 是 `ok`（0 条）。所以不是固定被挡，而是时好时坏。本地今天抓取正常（`/news/news250120` → 302 到 `/news/news250120/` → 200，23720 字节，侧栏有 `/news/news260424` … `/news/news261017`）。

**日志里有什么。** `gh run view 41577139144 --log`（11-03）里只有这两行：

```
WARNING daily.pipeline: source deepseek-news failed: ValueError: no post links found; page layout may have changed
  deepseek-news            ERROR ValueError: no post links found; page layout may have changed  (1.0s)
```

没有状态码、最终 URL 和响应内容，**现有日志判断不了 runner 拿到的是什么页面**。能确定的只有：状态码不是 4xx/5xx（否则 `raise_for_status` 会先报 `HTTPStatusError`），页面里没有匹配 `^/news/news[0-9]+/?$` 的链接。

**线索。** `api-docs.deepseek.com` 的响应头是 `server: tencent-cos`，带 `eo-log-uuid`、`eo-cache-status`，也就是腾讯云 EdgeOne CDN 加 COS。GitHub 的 runner 在 Azure 美国机房，可能被 EdgeOne 分到别的节点，拿到 JS 验证页或者旧缓存。这是推测，没有证据。

**建议加的诊断日志。** `fetch_html_listing` 找不到链接时，把下面这些写进异常信息（会进 `candidates.json` 的 `sources[].error`，也会出现在 Actions 日志里）：

- `response.status_code`、`response.url`（跳转后的最终 URL）、`len(response.content)`；
- 几个响应头：`server`、`content-type`、`eo-cache-status`、`cf-ray` / `x-amz-cf-pop`；
- 页面里 `<a>` 的总数，以及正文去掉空白后的前 300 字符。

这些都是通用信息，对所有 html_listing 信源都有用。工作流只在默认分支上按计划跑，所以要等这段代码合进 main 之后，下一次失败才能拿到数据。

**备选端点。**

| 端点 | 情况 | 评价 |
|---|---|---|
| `https://www.deepseek.com/en/news/` | 官方，AWS CloudFront + S3（响应头 `server: AmazonS3`、`x-cache: Hit from cloudfront`），Next.js 服务端渲染。用现有 html_listing 加 `link_pattern: ^/en/news/[a-z0-9-]+/$` 本地试过，能解析出 5 篇带日期的文章（09-10 V4.1-Flash、04-24 V4 Preview、2025-12-01 V3.2…） | **推荐**：CDN 不一样，从美国机房访问大概率更稳（没在 CI 上验证）。缺点是只收大版本，10-17 的 V4.1-Flash-1017 只在 API 文档里有 |
| `https://api-docs.deepseek.com/sitemap.xml` | 有 `/news/news261017` 等条目，没有 `lastmod` | 和现在的端点同一个 EdgeOne 域名，不解决问题 |
| GitHub 上的文档仓库 | `deepseek-ai` 组织下没有 API 文档仓库 | 不可行。模型发布已经由 hf-trending-models 覆盖 |
| `deepseek.ai/blog` | 非官方网站 | 不符合 Tier 1 一手信源的要求，不建议 |

建议：先加诊断日志；同时新增 `www.deepseek.com/en/news/` 作为一个信源（或者给 deepseek-news 换主端点），api-docs 保留，用来收小版本更新。

## 3. 只有日期的信源，以及 10-26 那两篇

**哪些信源只有日期。**

- 明确记为 `day` 的：anthropic-news、anthropic-research、mistral-news、kimi-blog、deepseek-news（都是 html_listing）。
- 记为 `second`、其实只有日期的：openai-news 的部分文章、huggingface-blog 里 HF 官方账号的文章（RSS 写 `00:00:00`）。minimax-blog 的 M3.1 Flash 也是 `00:00:00`，但最近没有新文章，没受影响。
- 时刻真实的：deepmind-blog、google-ai-blog、meta-ai-news、HF 社区文章、github-releases。

**"晚一天"不是真正的问题，丢文章才是。** #28 说只有日期的文章"进日报晚一天"。实际上，美国白天发的文章即使有精确时刻，也只能进下一期：D 期在 D 日 04:15 UTC 抓取，那时美国还是 D-1 日晚上。所以只有日期并不会多拖一天。真正的问题有两个：

1. 写成 `00:00:00` 的 RSS 文章被当成精确时间，**两期都进不去**（openai-news 12 篇、huggingface-blog 6 篇）；
2. `day` 精度的文章如果在美西 D 日晚上 8～9 点以后发，也**两期都进不去**（anthropic-research 1 篇）。

**10-26 的两篇。**

- Anthropic *Anthropic files S-1 with the SEC*（`/news/s1-sec`，`2026-10-26`，`day`）：**进了 10-27 那期的候选**，来源 anthropic-news，也上了 10-27 主版的头条。
- OpenAI *Introducing GPT-6.1 Terra*：**openai-news 没抓到**（feed 时间 `Mon, 26 Oct 2026 00:00:00 GMT`，属于上面第 1 种情况）。它进 10-27 那期的候选，是靠 hackernews（HN 10-26 18:01 UTC，URL `openai.com/index/introducing-gpt-6-1-terra/`），也上了 10-27 主版的头条。如果当天 HN 没人发，这条就漏了。

## 建议的修复

按影响从大到小排：

1. **RSS 的 `00:00:00` 当作只有日期。** `fetch_rss` 里如果时间正好是 UTC 午夜，就把 `published_precision` 设为 `day`。只改这一处就能救回 openai-news 和 huggingface-blog 的漏抓，包括 GPT-6.1 Terra 这种大发布。代价是极少数真在 UTC 午夜发的文章会多进一期，跨期去重会给它标上 `seen_on`。
2. **`day` 精度的窗口往前多放一天。** `Window.contains(precision="day")` 接受 `start.date() - 1`，解决美西晚上发的文章（anthropic-research 那种）。重复的部分由跨期去重处理：已经发布过的会被丢掉，候选里出现过的会标 `seen_on`。
3. **github-releases 处理"先 pre-release 后转正"。** 两种做法：对 ollama 这类仓库按"之前的候选里没出现过、`published_at` 在最近 3 天内"来收；或者直接把 `include_prereleases` 打开，标 `signals.prerelease`，交给编辑判断。前一种做法和第 2 条可以用同一套"首次出现"逻辑。顺便把 `per_page` 提到 30，避免 llama.cpp 的正式版被 b-build 挤出第一页。
4. **deepseek-news：** 先按第 2 节加诊断日志，再新增 `www.deepseek.com/en/news/`。
5. **minimax-blog：** `link_pattern` 改成 `^/(blog|news)/[a-z0-9-]+$`，收列表页上链接的 `/news/` 文章。优先级低。
6. **deepmind-blog 那一次漏抓：** 原因查不清。第 2 节的诊断日志思路也可以用在 RSS 上：每次记下 feed 的 `lastBuildDate` 和条目数，下次再出现就能看出是不是拿到了旧 feed。
7. 不需要改的：minimax-blog、kimi-blog、meta-ai-news 是真没更新；github-releases 周末 0 条是真没发布；hf-daily-papers 周末 0 条是 HF 本身不更新。

## 来源

- 各网站当前内容（2026-11-03 抓取）：`openai.com/news/rss.xml`、`www.anthropic.com/news`、`www.anthropic.com/research`、`deepmind.google/blog/rss.xml`、`blog.google/innovation-and-ai/technology/ai/rss/`、`mistral.ai/news`、`huggingface.co/blog/feed.xml`、`about.fb.com/news/tag/ai/feed/`、`about.fb.com/news/feed/`、`www.minimax.io/blog`（以及各文章页的 `datePublished`）、`www.kimi.com/en/blog/`、`api-docs.deepseek.com/news/news250120`、`api-docs.deepseek.com/sitemap.xml`、`www.deepseek.com/en/news/`
- GitHub API：`repos/<repo>/releases`（sources.yaml 里的 14 个仓库）、`orgs/deepseek-ai/repos`
- Actions：`gh run list --workflow fetch.yml`，`gh run view 41577139144 --log`
- 仓库：`data/2026-10-21 … 2026-11-03/candidates.json`、`data/2026-10-27/digest.json`、`daily/fetchers/feeds.py`、`daily/fetchers/html_listing.py`、`daily/fetchers/github.py`、`daily/window.py`、`sources.yaml`、`git log -- sources.yaml`
