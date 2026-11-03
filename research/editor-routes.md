# 编辑通道对比（#48）

调研时间 2026-11-03，范围 10-21～11-03 共 14 期。只读数据和代码，没有改动。

## 结论

1. **条数下降主要是候选少了，不是编辑不稳定。** Claude 主版条数和候选数的相关系数是 0.94。条数少的 5 期（10-24、10-25、10-26、11-01、11-02）都是周末内容那几期：HF 每日论文和官方博客为 0。条数没有逐日下降的趋势，是一周一次的低谷。
2. **validate 删错的很少，而且是在加预检之前。** 14 期主版里 validate 一共删了 6 条，都在 10-21～10-25；10-25 加了预检（#12）以后，主版一条都没再被删。这 6 条都是想看的新闻，都是因为缺一个版本号或名称这类小错被删掉的。
3. **Claude 通道的问题是写得偏少，不是删得多。** 11-03 Claude 打 ≥5 分的有 21 个候选，最后写了 12 条，正好是 `ITEMS_TARGET` 的上限，LongCat-2.5 这类三个通道都打 ≥5 分的候选没写进去。11-02 只有 7 个候选 ≥5，写了 6 条，打分标准本身就严。
4. **API 通道的打分区分不开好坏。** Gemini 给 63%（11-02）和 57%（11-03）的候选打了 ≥5，和 Claude 完全一致的只有 2/51、12/88。MiniMax 和 Claude 更接近（平均总分差 1.2 / 1.0），但也会把看不到的旧闻和图片帖写进来。
5. **validate 有两处漏洞，还有两处误判**（见第 4 节 V1–V4）：只有图片或视频的 Reddit 链接被当成一手来源；页面 403 时，引文没核对也能发布；`2.14` 和 `2.14.0` 被当成两个数，`763B-parameter` 也对不上材料里的 `763B params`。

## 1. 有生成记录的两期（11-02、11-03）

数据：`data/2026-11-0{2,3}/trace.{claude,api.gemini,api.minimax}.json`，以及同目录的 digest 和 candidates。

### 1.1 打分分布

API 通道看不到「只有讨论帖、没有一手来源」的候选（`no_first_hand`，两天都是 32 个），所以它的分数比 Claude 少。

| 期 | 通道 | 打分数 | 平均总分 | 总分 ≥5 | 重要性 0/1/2/3 | 实用性 0/1/2/3 | 新颖性 0/1/2 |
|---|---|---|---|---|---|---|---|
| 11-02 | Claude | 83 | 2.0 | 7 | 42/35/6/0 | 41/31/10/1 | 26/49/8 |
| 11-02 | Gemini | 51 | 4.2 | 32 | 1/18/31/1 | 7/7/23/14 | 16/35/0 |
| 11-02 | MiniMax | 51 | 3.3 | 12 | 7/37/7/0 | 7/22/21/1 | 20/12/19 |
| 11-03 | Claude | 120 | 2.8 | 21 | 50/51/16/3 | 44/53/19/4 | 23/53/44 |
| 11-03 | Gemini | 88 | 4.4 | 50 | 5/32/46/5 | 13/26/34/15 | 21/21/46 |
| 11-03 | MiniMax | 88 | 3.6 | 28 | 5/46/36/1 | 8/55/23/2 | 24/42/22 |

- Gemini 打分普遍偏高：实用性 3 分 11-02 给了 14 个，11-03 给了 15 个，Claude 是 1 个和 4 个。11-02 Gemini 一个新颖性 2 都没给，11-03 又给了 46 个，看不出它按什么标准。
- 通道两两比较（只比都打了分的候选）：

| 期 | 比较 | 完全一致 | 平均总分差 | 都 ≥5 | 只有前者 ≥5 | 只有后者 ≥5 |
|---|---|---|---|---|---|---|
| 11-02 | Claude vs Gemini | 2/51 | 2.33 | 4 | 1 | 28 |
| 11-02 | Claude vs MiniMax | 19/51 | 1.22 | 3 | 2 | 9 |
| 11-03 | Claude vs Gemini | 12/88 | 1.85 | 16 | 3 | 34 |
| 11-03 | Claude vs MiniMax | 16/88 | 1.02 | 14 | 5 | 14 |

- 分歧最大的几类：
  - **衍生权重和讨论帖**：`c_cf1c6eb2e1` OBLITERATUS/DeepSeek-V4.1-Flash-1017-obliterated（去审查衍生权重），Claude [0,0,0]，Gemini [2,2,1]；11-03 的 `c_34cdaf29bd`「Running UNCENSORED DeepSeek-V4.1-Flash-1017 on a 12 Gb VRAM」，Claude [0,0,0]，Gemini [2,3,2]。SKILL.md 第 2 节写明衍生权重直接排除，Gemini 没照做。
  - **旧闻**：DeepSeek-V4.1-Flash-1017（`c_8b553ca25e`）Claude 两天都给新颖性 0（10-21 报道过），Gemini 11-03 给 [2,3,2]；`c_6ecc1d71a5` flux-3-image-klein-comfy，Claude [0,1,0]，Gemini [2,2,2]。这就是 #41 说的问题。
  - **重大但只有讨论帖的新闻**：`c_9967463597`「China's First Frontier AI Export Controls: Mofcom Announcement No. 48」，Claude [3,2,2] 写成了头条，MiniMax 只给 [2,1,1]。

### 1.2 各通道写了哪些

| 期 | Claude（主版） | Gemini | MiniMax | 三家都写的 |
|---|---|---|---|---|
| 11-02 | 6 条 | 10 条（和主版共有 3 条） | 15 条（和主版共有 3 条） | 2 个候选 |
| 11-03 | 12 条 | 6 条（共有 4 条） | 12 条（共有 7 条） | 4 个候选 |

- 11-02 三家都写的只有 Drex Max v1（`c_f2001e1382`）和 AiSOC（`c_1cc8167e7b`）。
- 11-02 API 通道写了，Claude 判为旧闻没写的：DeepSeek-V4.1-Flash-1017（Gemini、MiniMax 都写了）、MiniMax-M3.1-Flash（MiniMax）、LFM3-Omni-2B（都写了），和 #41 列的一致。
- 11-02 只有 Claude 写的：Heretic 2.0（`c_a742bd7fc3`，[2,2,2]）。它只有 Reddit 帖子，API 通道在挑选前就把它去掉了；Claude 自己找到并打开了 `github.com/p-e-w/heretic`。
- 11-03 只有 Claude 写的：Pando（`c_006ec733ab`，MiniMax 挑了但没写）、出口管制（`c_9967463597`，Gemini 挑了但没写）、GPT-Rosalind-6、0.1% 预训练数据投毒、Anthropic S-1。
- 11-03 Gemini 挑了 15 组，只写了 6 条，没有头条。GPT-6 Astra（`c_cf0ceff712`，HN 2143 分，它自己打了 [3,2,2]）和出口管制都挑了，但没写。修改轮提示了「合格 5 条，目标 8–12 条，还没用上的组……」，它只修好了原来那一条，一条也没补。

### 1.3 validate 拒了什么、为什么

| 期 | 通道 | 轮次 | 条目 | 原因 | 结果 |
|---|---|---|---|---|---|
| 11-02 | Claude | 预检 | Mellum2.1（`c_bd3013759b`）、dsh-superagent（`c_6686bf182a`） | `evidence quote must be 1-300 characters` | 截短引文后正式校验通过 |
| 11-02 | Claude | 预检 | 今日要点 | 要点提到了上面两条，两条一删，要点里的 `Mellum2.1-12B-A2.5B-Thinking-MTP`、`1.8x` 就对不上 | 有 ERROR，这一轮没有联网核对 |
| 11-02 | Gemini | draft | Claude-Code-Game-Studios（`c_6609ae6f1b`） | `number 5 does not appear` | 修改轮修好 |
| 11-02 | MiniMax | draft | LFM3-Omni-2B | `number 23` | 修改轮修好 |
| 11-02 | MiniMax | draft | Minecraft Agent（`c_2fd6149769`） | `GPT-6.1`、`6.1`、`10`、`5.5` 都不在材料里 | 删了数字以后保留；Claude 给它 [1,0,1] |
| 11-02 | MiniMax | draft | FineDNA、Kapitsa、GLB-3D-Coder 三条快讯 | `summary longer than 120 characters` | 修改轮缩短 |
| 11-02 | MiniMax | draft | 今日要点 | 超过 3 句，还提到了被拒的条目 | 修改轮重写 |
| 11-02 | MiniMax | en | DeepSeek、numbat | `'763B-parameter'`、`'6.8T-parameter' does not appear`（材料写的是 `763B params`、`6.8T params`） | **误判**，英文版删了这两条（见 V3） |
| 11-02 | MiniMax | en | 三条快讯 | `summary longer than 250 characters` | 删掉 |
| 11-03 | Gemini | draft | agent-desktop（`c_885299c2ed`） | `'v0.3.0' does not appear` | 修改轮去掉版本号 |
| 11-03 | MiniMax | draft、fix | 今日要点 | `number 2.14 does not appear in the published items`；vLLM 条目的 summary 写的是「PyTorch 2.14.0」 | **误判**（见 V3）。修改轮原样交回同样的要点，最后程序用前三条标题顶替 |
| 11-03 | MiniMax | draft | R²Orch（`c_4185c9fbf8`） | `'9B'`、`9` 不在材料里 | 修改轮修好 |
| 11-03 | Claude | 预检、正式 | — | 没有删任何条目 | 只有 403 的警告 |

### 1.4 自检和修改轮删了什么

- Claude 11-03 自检记了 `[]`（没删）。11-02 的生成记录**没有 `self_check` 这一步**（步骤只有 precheck、final、en），按 SKILL.md 第 5 节，没删也要记一个空列表。`trace` 是 11-02 00:34 才合进来的（`4bae0a4`），当天第一次跑，可能没跟上。
- API 通道的修改轮两天都没有删掉整条：被拒的条目都改到能通过为止。比如 Minecraft 这条（11-02 MiniMax）draft 里有 4 个材料里没有的数字，说明模型编了数字；修改轮把数字删掉，条目照样发布了。这和 SKILL.md 开头「被校验判为不合格的条目直接删掉，不要改写到勉强能过」相反，原因是 `api_editor.FIX_RULES` 允许「删掉材料里没有的数字和名称」。
- 11-02 Claude 的 `digest.json` 里 `generated_at` 是 `04:55:00`，比 adopt 采用它的时间（04:42:53）还晚，是手写的整点时间，不是真实时间。

### 1.5 采用情况

- 11-02：Claude 版 04:42:53 当主版；两个 API 版都是「keeping the edited issue over an API edit」。
- 11-03：MiniMax 版 04:44:30 先当了主版（「no valid digest yet」），Claude 版 04:45:27 把它换掉（「a Claude edit replaces the API edit」）。中间这一分钟，网站上的主版是 MiniMax 写的。

## 2. 10-21 以后的 14 期

数据：各期的 `candidates.json`、`digest.json`、`digest.api.*.json`。API 通道从 10-27 才开始有输出（10-26 合进来，`b59964e`）。

| 期 | 星期* | 候选 | 博客+论文+Release | 主版条数 | Gemini | MiniMax | Gemini 和主版共有 | MiniMax 和主版共有 |
|---|---|---|---|---|---|---|---|---|
| 10-21 | 三 | 111 | 49 | 11 | — | — | | |
| 10-22 | 四 | 112 | 54 | 12 | — | — | | |
| 10-23 | 五 | 111 | 48 | 10 | — | — | | |
| 10-24 | 六 | 87 | 36 | 8 | — | — | | |
| 10-25 | 日 | 51 | 0 | 5 | — | — | | |
| 10-26 | 一 | 82 | 0 | 8 | — | — | | |
| 10-27 | 二 | 117 | 29 | 12 | 8 | 12 | 6/8 | 10/12 |
| 10-28 | 三 | 129 | 47 | 12 | 8 | 12 | 5/8 | 10/12 |
| 10-29 | 四 | 125 | 35 | 11 | 12 | — | 8/12 | |
| 10-30 | 五 | 107 | 17 | 11 | 10 | 17 | 7/10 | 9/17 |
| 10-31 | 六 | 124 | 29 | 12 | 10 | 12 | 4/10 | 4/12 |
| 11-01 | 日 | 91 | 0 | 9 | 10 | 13 | 3/10 | 5/13 |
| 11-02 | 一 | 83 | 0 | 6 | 10 | 15 | 3/10 | 3/15 |
| 11-03 | 二 | 120 | 31 | 12 | 6 | 12 | 4/6 | 7/12 |

\* 期号的日期。一期覆盖的是前一天的内容，所以 10-25、10-26、11-01、11-02 这四期覆盖的是周六和周日。

- 「共有」指 API 版的条目里，有几条和主版用了同一个候选。
- 主版条数 vs 候选数：相关系数 0.94；主版条数 vs 博客+论文+Release 数：0.71。
- 主版有 5 期是 12 条，正好卡在 `ITEMS_TARGET = (8, 12)` 的上限。
- MiniMax 有两期超过上限（10-30 17 条、11-02 15 条），validate 只警告。
- 10-31 以后，API 版和主版的重合明显变少（4/10、3/10、3/15）。一个原因是 API 通道把 7 天以外报道过的旧闻又写了一遍（下表）。
- MiniMax 10-29 没有输出，Gemini 那天写了 12 条。

主版报道过、后来又被写进来的条目（按来源链接对比，比较的是更早的主版）：

| 期 | 通道 | 条目 | 第一次出现在主版 |
|---|---|---|---|
| 10-29 | Gemini | DeepSeek-V4.1-Flash-1017 发布 | 10-21 |
| 10-30 | **主版** | Recursive 开源编码 Agent 模型 Flint | 10-22 |
| 10-30 | MiniMax | Flint | 10-22 |
| 10-31 | Gemini、MiniMax | DeepSeek-V4.1-Flash-1017 | 10-21 |
| 11-01 | Gemini | FLUX 3 Image Klein；DeepSeek-V4.1-Flash-1017 | 10-21 |
| 11-01 | MiniMax | DeepSeek-V4.1-Flash-1017；MiniMax-M3.1-Flash | 10-21、10-24 |
| 11-02 | Gemini、MiniMax | DeepSeek-V4.1-Flash-1017；MiniMax-M3.1-Flash（MiniMax） | 10-21、10-24 |
| 11-03 | **主版**、MiniMax | Nanbeige4.3-33B | 10-26 |

Claude 也会重复：10-30 的 Flint 和 11-03 的 Nanbeige4.3-33B 都是同一个 HF 链接，前后隔了 8 天，超出 7 天去重窗口。11-03 Claude 还给 Nanbeige 打了新颖性 2，两期 summary 里的分数一模一样（Terminal-Bench 2.1 80.9、SWE-Bench Pro 60.3）。所以 #41 的 `reported_on` 两个通道都要用，不只是 API 通道。

## 3. #25 的几个问题

**有多少条被错误丢弃？**

- validate 在主版里删掉的 6 条（`validation.dropped`）：

| 期 | 条目 | 原因 | 想不想看 |
|---|---|---|---|
| 10-21 | Mistral 发布 Voxtral 3（`c_e267c7cec9`） | 引文 `achieve high-quality transcriptions…` 在页面上找不到（WebFetch 把 achieves 转述成了 achieve） | 想看，头条级别 |
| 10-22 | IBM Granite Speech 5.0（`c_306ae3469f`） | `number 4.1` 不在材料里 | 想看 |
| 10-23 | Ai2 OlmoEarth v1.3（`c_d357653ad5`） | `'Ai2'` 不在材料里（材料里是 `allenai`） | 想看 |
| 10-23 | OpenAI CLI（`c_f23d56f924`） | `number 2.0` 不在材料里 | 想看 |
| 10-25 | HF 开源 DNA 模型 Carbon-X（`c_fa50901d53`） | `Qwen3-14B` 不在材料里 | 想看，那天一共只有 5 条 |
| 10-25 | Impeccable（`c_fa50ebc2e9`） | `number 2.0` 不在材料里 | 可看可不看 |

  这 6 条都是因为一个词或一个数在材料里找不到被整条删掉的，删的规则本身没错（不能写材料里没有的事实）。其中 5 条是想看的。预检和 `daily page` 加进来以后（10-25，#12），后面 9 期主版都没再被删过。
- 「打了高分却没写」，只有 11-02、11-03 两期能查：
  - 11-02：Claude ≥5 分没写的只有 tandem.cpp（`c_74565ab595`，[1,2,2]，只有 Reddit 帖子），可以不算。
  - 11-03：Claude ≥5 分没写的有 7 个。LongCat-2.5（`c_8ab87767fb`，[2,2,2]，三家都 ≥5，HN 80 分，链接是官方博客 longcat.ai）、FlashMLA（`c_1b40eb9cef`，「An AI agent just beat NVIDIA's FlashMLA baseline by 9.8% on B200」，Gemini [3,3,2]）、claude-code v2.1.317（`c_8b09de7d1b`）、Qwen 坚持开源的声明（`c_9275e4f791`，r/LocalLLaMA 第 1）、llama.cpp 加入 Clover 支持（`c_2c2379b515`）、Latent Sparse Attention（`c_7564218447`）、RidgeFill（`c_af444cdf0d`）。自检和 validate 都没删东西，是 Claude 写满 12 条就停了。**至少 LongCat-2.5 是想看的**；后面几条看条数目标定多少。
- API 通道在挑选前去掉的 32 个「只有讨论帖」的候选里，有 Claude 写进主版的条目（11-02 Heretic 2.0，11-03 `c_0437f6bbde` 合并进了 Astra 那一条）。API 通道永远写不到这类新闻。

**有多少条是因为 validate 太严或小错误被丢掉，其中多少是我们想看的？**

- 主版：6 条，都是小错；5 条想看。全部发生在预检之前。
- 有生成记录的两期，误判有 2 处，都在 API 通道：MiniMax 11-02 英文版的 `763B-parameter`、`6.8T-parameter`（删了 DeepSeek、numbat 两条，这个英文版没有采用），MiniMax 11-03 今日要点的 `2.14`（要点被换成了标题）。这些误判都不影响主版。
- 反过来，**validate 有漏洞，放过了不该发的**：见 V1、V2。

**条数越来越少，是候选少了还是编辑不稳定？**

- 候选少了，而且是固定在周末那几期少：10-25、10-26、11-01、11-02 这四期的博客+论文+Release 都是 0（#28 第 1、3 点）。主版条数和候选数的相关系数是 0.94。
- Claude 通道在稳定的那些天，条数被上限 12 卡住了，不是不稳定。
- 不稳定的是 API 通道：Gemini 6～12 条、MiniMax 12～17 条，和主版共有的条目在 3 条到 10 条之间来回跳，MiniMax 10-29 还没出版。

**要不要设最少、最多条数和平均期望？** #28 已经提出「15 条左右，最少 8 条」。从数据看：上限 12 确实在挡掉想看的条目（11-03）；周末那几期即使放宽也凑不出 8 条（10-25 Claude 写了 5 条，每条都是认真挑的），所以最少条数应该是警告，不能当成硬性要求，否则 API 通道会凑数（#27）。

## 4. 能改的地方

### SKILL.md

- **S1 新颖性按 `reported_on` 判**（就是 #41）。证据：Claude 自己也重复了两次（10-30 Flint ← 10-22，11-03 Nanbeige4.3-33B ← 10-26，Nanbeige 新颖性打了 2）；API 通道 10-29～11-03 有 12 次重复报道。
- **S2 条数目标改成约 15 条，12 条不再是上限**（#28）。证据：11-03 Claude 写到 12 条就停了，LongCat-2.5 [2,2,2] 和 FlashMLA [2,2,2] 都没写；主版 14 期里有 5 期正好 12 条。
- **S3 第 3 节写明：页面 403 时，引文不能来自 WebFetch。** 现在的写法是「`daily page` 拿不到页面文本时……只写候选摘要里有的数字」。11-03 Pando 一条有 5 段引文都是 `evidence quote unverified`（openai.com 403），summary 里「中位推送延迟降低近 5 倍」「每天接近一个 petabyte」都来自没核对过的引文，候选摘要里没有。要么照现在的规则严格执行，要么明确允许，并把它记在自检里。
- **S4 第 5 节：自检记录写成必做的检查项**，并要求 `generated_at` 用 `date -u` 的真实时间。证据：11-02 `trace.claude.json` 没有 `self_check`；`generated_at` 是 `04:55:00`，比 adopt 时间晚。
- **S5 第 2 节把「衍生权重、去审查版本」写得更具体一些。** API 通道是直接读这一节的。证据：Gemini 给 `c_cf1c6eb2e1`（-obliterated）[2,2,1]，给 `c_34cdaf29bd`（UNCENSORED …）[2,3,2]。

### validate（`daily/digest.py`）

- **V1 `i.redd.it`、`v.redd.it` 这类图片和视频链接不算一手来源。** `DISCUSSION_HOSTS = ("news.ycombinator.com", "reddit.com")` 只认 reddit.com，`i.redd.it` 匹配不上。证据：MiniMax 11-02 有 3 条快讯的唯一来源是图片或视频，evidence 都是 0 条：FineDNA `https://i.redd.it/cdh8dfe7dyyh1.png`、Kapitsa `https://i.redd.it/32s48p6jx2zh1.png`、GLB-3D-Coder `https://v.redd.it/6ssijtngz2zh1`；Gemini 10-28 的 MiniCPM-OCR 也是 `i.redd.it/...jpeg`。`x.com` 的推文要不要算，也要定下来（MiniMax 11-02 JEPA、11-03 Latent Sparse Attention 都只有一条推文作来源）。
- **V2 页面打不开时，没核对过的引文不能支撑数字。** `_check_online` 在 `page.text is None` 时只加一条 warning。可以改成：这种引文不算进 `_check_facts` 的材料，只能依据候选标题和摘要写。证据：11-03 Pando（见 S3）。
- **V3 修两处误判：**
  - 版本号前缀：summary 里有 `2.14.0`，要点里写 `2.14` 应该算出现过。`_NUMBER` 把 `2.14.0` 当成一个整体，所以 `2.14` 找不到。证据：MiniMax 11-03 要点「vLLM v0.33.0 升级到 PyTorch 2.14」被拒了两轮。
  - 数字连着英文词：`_MIXED` 把 `763B-parameter` 当成一个词。可以在连字符处拆开，只核对带数字的那一段（`763B`）。证据：MiniMax 11-02 英文版 `'763B-parameter'`、`'6.8T-parameter'`，材料里是 `763B params`、`6.8T params`。
- **V4 条数超过上限要不要拦。** 现在超过 12 条只给警告。MiniMax 10-30 写了 17 条，11-02 写了 15 条。如果按 S2 改成 15 条左右，可以给 API 通道设一个硬上限（比如 18 条）。

### API 通道的提示词和循环（`daily/api_editor.py`）

- **A1 修改轮只允许删掉不合格的条目，不允许删数字后保留。** `FIX_RULES` 现在写的是「删掉材料里没有的数字和名称……或者整条删掉」。证据：11-02 MiniMax Minecraft 一条在 draft 里编了 `GPT-6.1`、`10`、`5.5`，修改轮删掉数字以后照样发布了。模型编了数字，这一条的其他内容也不可信。
- **A2 今日要点的反馈要具体。** 11-03 MiniMax 两轮都交回了同样的要点，最后程序用前三条标题顶替。反馈里可以加一句：要点的数字只能来自条目的标题和 summary，并写出它引用的是哪一条（V3 修好以后这次就不会被拒了）。
- **A3 讨论帖里的链接也给 API 通道用。** 现在 `first_hand_url()` 只看候选的 `url` 和 `also_from`，32 个只有讨论帖的候选直接被去掉。Claude 的做法是从帖子里找到一手页面，例如 11-02 Heretic 2.0 → `github.com/p-e-w/heretic`。程序可以从 Reddit 正文里抽出 GitHub、HF、arXiv 链接，当成候选的一手来源去打开。
- **A4 生成记录里记下 read 这一步每个页面的状态**（打开成功、403、没有成句的正文）。现在 Gemini 11-03 挑了 GPT-6 Astra 和出口管制却没写，看不出是页面打不开，还是模型自己放弃了。`_read()` 里本来就有 `page.status` 和 `page.error`。
- **A5 写作那一步提醒模型「挑了的组都要写，写不了就说原因」**，或者把没写的组和原因记进回答。证据：Gemini 11-03 挑了 15 组写了 6 条，修改轮提示了没用上的组，它一条也没补。
- **A6 打分要先校准，或者不再用 API 通道的分数。** Gemini 两天给 57%～63% 的候选打了 ≥5，11-02 新颖性一个 2 都没有，它的分数不能拿来排序或做 #25 的统计。可以在提示词里给几个打分例子（从 Claude 的分数里各挑一个 0 分、1 分、3 分的），或者让程序按分数排序以后再挑。
- **A7 版块用错。** MiniMax 11-02 把 Nolan Lawson 的博客文章（`c_d6756f65c5`）和一条推文（JEPA）放进了 📄 论文。可以让程序检查：`paper` 版块的主来源应该是 `kind == "paper"` 的候选，或者是 arXiv、HF papers 的链接。

### 顺带发现

- 候选链接里有没解码的 HTML 实体：`c_7564218447` 的 url 是 `...?a=02yfc9wrBoQ2Xi7DDjQ&amp;s=46`。是抓取器的问题，不属于这个 issue。

## 方法和数据

- 分数、各步骤和 adopt：从 `trace.*.json` 的 `scores`、`steps`、`adopt` 字段读出来（schema 见 `daily/trace.py` 的文档字符串）。
- 「≥5 分」用的是 SKILL.md 第 2 节的入选线「总分大致 ≥ 5」。
- 重合：两条条目只要引用了同一个 `candidate_id` 就算同一条。重复报道：条目来源的 URL（去掉协议和末尾 `/`）在更早的主版里出现过。
- 只有两期有生成记录，打分的结论样本很小。10-27～11-01 的 API 版只有最后的结果，看不到修改轮。
