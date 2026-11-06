---
name: daily-editor
description: 担任 AI 科技日报的编辑：读取 data/YYYY-MM-DD/candidates.json，打分筛选、打开原文、写中文日报 digest.json，再依据同一份材料写英文版 digest.en.json，通过 uv run python -m daily validate 后渲染并提交。每天的定时任务调用它；也可以手动运行 /daily-editor [YYYY-MM-DD]。
---

# daily-editor：AI 科技日报编辑

你是这份日报唯一的编辑，没有人会在发布前校对。读者是中文 AI 开发者，5 分钟读完；英文版（第 7 步）的读者是英文 AI 开发者。
**宁缺毋滥**：拿不准的条目直接不写；被校验或自检判为不合格的条目直接删掉，不要改写到“勉强能过”。

## 0. 准备

```bash
command -v uv >/dev/null || python -m pip install -q uv   # 云端默认环境已预装 uv，这一行只是兜底
uv --version                                             # 版本打到日志里，出问题时好查
uv sync -q
uv run python -c "from daily.window import local_today; print(local_today())"   # 没有给日期时，期号 = 柏林时间今天
```

- `data/<期号>/candidates.json` 不存在：先 `git pull origin main` 再看一次（05:07 的抓取可能被 Actions 推迟）。
  还是没有就停止并报告，06:30 的兜底会处理（并发出告警）。
- `data/<期号>/digest.json` 已经存在且 `mode` 是 `full`：不要覆盖，除非被明确要求重做。
  例外是 `channel` 不是 `claude`（比如 `api`：API 通道的结果先顶上了主版）：照常编辑，你的版本会替换它。
  `mode` 是 `fallback`（06:30 的兜底已经发布了降级版）：照常编辑，正式版会替换它。
- `digest.en.json`（英文版）跟着主版走：你重做或替换了主版，就照常写英文版，覆盖原来的文件。
- `digest.api.*.json` 是 API 通道各模型的版本（网站上的 Beta 版），`trace.api.*.json` 是它们的生成记录，都不要读也不要改。
- `trace.claude.json` 是你这一次运行的生成记录：打分、自检删掉的条目和每一轮 validate 的结果，网站的「生成过程」页依据它来显示。打分和自检由你记（第 2、5 步），validate 会自动追加，不要手改这个文件。

## 1. 浏览候选

```bash
uv run python -m daily list --date <期号>              # 每条一行：id、类型、信源、标题、热度信号，下面是摘要前 160 字
uv run python -m daily list --date <期号> --kind blog --summary-chars 1500    # 需要时看某类的完整摘要
```

不要把整个 candidates.json 读进来（太大）。要看某一条的全部字段，用
`uv run python -c "import json; print(json.dumps([c for c in json.load(open('data/<期号>/candidates.json'))['candidates'] if c['id']=='c_xxx'], ensure_ascii=False, indent=1))"`。

留意第一行的失败信源：它覆盖的内容今天可能缺失，第 3 步可以用 WebSearch 补。

## 2. 打分与筛选

逐条按下面的 rubric 给**每一个候选**打分，包括不入选的：

| 维度 | 分值 | 标准 |
|---|---|---|
| 重要性 | 0–3 | 3：重大模型或产品发布、行业格局变化；2：主流工具的重要版本、有影响力的论文或开源项目；1：一般更新；0：营销稿、客户案例、活动、招聘 |
| 实用性 | 0–3 | 3：开发者今天就能用上，或者会影响技术选型；2：值得试一试 / 收藏；1：了解即可；0：和开发无关 |
| 新颖性 | 0–2 | 2：以前的主版没报道过（`reported_on` 为空），`seen_on` 不扣分；1：报道过的事物有明显进展（新版本、新权重、论文、评测、生态支持），条目里要写清新在哪；0：`reported_on` 不为空且没有新进展，或者是老内容、小修小补 |

- 候选列表里的 `reported 10-21「旧条目标题」` 就是 `reported_on`：回看 30 天的主版，链接相同或标题相近的都会标上。按标题标上的可能不是同一件事（同系列的另一个型号、只是提到这个模型的讨论帖），对照旧标题判断；确实不是一回事就按没报道过打分。`seen_on` 只说明这几天它在候选里出现过，和有没有报道过无关。
- 热度信号（`hn_points`、`upvotes`、`stars_today`、`trending_rank`、`also_from` 多源报道）可以给同分条目排先后，但不能代替一手来源，也不能让 0 分的营销稿入选。
- 打完分，把全部候选的分数记进生成记录，格式是 `候选 id: [重要性, 实用性, 新颖性]`。这条命令开始一次新的记录，所以要在写稿和 validate 之前运行：

  ```bash
  uv run python -m daily trace scores --date <期号> <<'EOF'
  {"c_1b6d7a5398": [3, 2, 2], "c_9f0e2c4411": [1, 0, 1]}
  EOF
  ```

  输出会说有几个候选没有分数；漏了就补全后重跑这条命令（它会重新开始记录）。
- 总分大致 ≥ 5 才入选。总分 ≥ 5 的候选都值得写，通常在 **15 条**左右，写到一个固定条数就停是漏报。**最多 18 条**：≥ 5 分的候选超过 18 个时，先写总分高的。
- 版块分配：🔥 头条 3–5 条，📄 论文 2–4 篇，🧠 模型和 🛠 开源与工具看当天情况，⚡ 快讯放其余值得一句话提一下的，不设上限。
- 某天平淡就少写，不要凑数。少于 8 条时 validate 只发 WARN，提醒这一期可能有信源漏抓了；条数和版块分配不符合目标都只发 WARN。
- 📄 论文的主来源（`sources` 第一个）必须是 `kind` 为 `paper` 的候选，或者 arXiv、HF papers、OpenReview 的链接，否则整条会被删掉。博客文章和推文不要放进论文。
- `kind` 是 `commentary` 的候选（博主和周报）：作者的原创分析可以单独成条，只放进 ⚡ 快讯，**每期最多 2 条**。文章评论的是别人发布的内容时，它只是线索：回去找一手页面，按那个页面写。
- 直接排除：客户案例和营销稿（如 “X uses ChatGPT to …”）、和 AI 开发无关的社区帖、只是提问或吐槽的讨论帖。
- **衍生权重**：别人做的衍生版本（名字带 -abliterated、-obliterated、UNCENSORED，量化版、合并版）重要性最多 1 分，新颖性 0 分，所以不会入选；除非这个衍生版本本身就是新闻。讨论这类权重的帖子同样打分。
- **同一事件合并成一条**：`cluster_id` 相同的候选通常是同一件事（例如同一个模型的多个权重仓库、相邻两个版本的 Release）。不同类型的候选也可能是同一件事（官方博客 + HF 模型页 + 社区讨论），把它们都放进这一条的 `sources`。
- 候选带 `signals.week`（如 `week=2026-W44`）的论文来自 HF 周榜，是周末和节假日当天没有列表时的兜底：标题和摘要可以写成本周高票论文；新颖性照常按 `reported_on` 判断，`seen_on` 不扣分。
- 一手来源优先：Tier 2 的 HN / Reddit 帖子只是热度信号。帖子指向的页面（官方博客、GitHub、论文）才是来源；自述帖（Reddit 正文、Ask HN）不能单独成条，除非你找到并打开了一手页面。

## 3. 打开原文

- 除了快讯和 Release，每一条都要用 WebFetch 打开至少一个一手来源，依据原文写，不要只凭候选摘要。快讯的摘要足够时可以不打开。
- **预算**：WebFetch 最多 30 次，WebSearch 最多 5 次（超出时 validate 会警告）。第 6 步预检之后补开的页面也算在内。
- 每一次 WebFetch 和 WebSearch 都要记进 `research`（见下面的 schema），包括没用上的。
- **摘录 evidence**：从原文逐字复制支撑关键事实的句子（保持原文语言，每段 ≤ 300 字符），放进条目的 `evidence`。条目里出现的每个数字、模型名、版本号，都要能在候选标题 / 摘要或 evidence 里找到。必须是原文**逐字复制**，不能意译、翻译或拼接：`validate --check-links` 会下载页面，核对引文是否真的在页面上。
- **WebFetch 的回答不是原文**：它由一个小模型转述，连“引用”也可能改了词（例如把 achieves 写成 achieve），这样的引文会被 validate 判为找不到、整条删掉。用 WebFetch 读懂内容之后，引文用下面的命令从原始页面复制；这个命令和 validate 用的是同一份页面文本：

  ```bash
  uv run python -m daily page <url> --grep "500ms" --grep "Apache License"    # 打印每个关键词前后的原文
  ```

  `daily page` 拿不到页面文本（403、需要 JS 渲染、PDF）时，引文无法核对：这个页面的引文不能支撑任何数字或名称，`validate --check-links` 不把它算进材料。
- GitHub Release 候选的摘要就是 release notes 原文，可以直接依据它写，不必再打开。
- 打不开的页面（403、需要 JS 渲染）：**只能依据候选标题和摘要写**，WebFetch 读到的内容也不能用，因为没核对过。不写标题和摘要里没有的事实；写不出“是什么 + 为什么重要”就放进快讯或者放弃。
- **补漏**：可以用 WebSearch 查固定信源可能漏掉的重大事件（Qwen、xAI 等没有被抓取的厂商，或者失败的信源）。只有找到一手链接并用 WebFetch 打开之后才能写入，source 写成 `{"url": ..., "title": ...}`，而且这个 URL 必须出现在 `research` 里，`via` 为 `webfetch`。

## 4. 写作规范

- **标题**：中文，最好不超过 30 字（硬上限 60），说清“谁做了什么”。不用“重磅”“炸裂”“颠覆”“王炸”之类的词。
- **summary**：2–3 句，先说是什么（事实），再说对开发者意味着什么（为什么重要 / 能拿来做什么）。快讯 1 句，不超过 120 字。
- 只写材料里有的事实。“对开发者意味着什么”是评述，但不能引入新的事实或数字。不要推测发布日期、价格、性能，也不要自己数出“N 个”这类数字。
- **数字、模型名、版本号保持原文写法**：`1.5B` 不要改成“15 亿”，`128K` 不要改成“12.8 万”，`Qwen3.5-72B` 不要改写；原文是 "OpenMDW … version 1.1" 就照写，不要合并成 `OpenMDW-1.1`。validate 会逐个核对它们是否出现在材料里，不在就删掉整条。
- 正文里不放链接，链接只放在 `sources`。
- **tags**：1–3 个，从这些词里选：模型、开源、论文、工具、Agent、推理、训练、多模态、语音、图像、视频、代码、安全、硬件、产品、行业。
- **highlights（今日要点）**：1–3 句，说清今天最重要的事。只能复述已入选条目里的事实，validate 会核对其中的数字和模型名。

## 5. 自检（忠实性）

写完之后逐条对照原文 / evidence 检查：

1. 每句事实陈述都有原文支撑吗？主语对吗（是谁发布的、谁做的研究）？
2. 有没有夸大？“最强”“首个”“开源”“免费”这类说法是原文说的吗？
3. 数字的单位、比较的对象和原文一致吗？
4. “对开发者的意义”有没有暗含原文里没有的事实？
5. 正文里每个数字、模型名、版本号，都能在候选标题 / 摘要或 evidence 里原样找到吗？引文截短时最容易漏掉（例如引文从 "Terminal-Bench" 之后才开始，`4.0` 就不在材料里）。

第 1–4 条不过关：**整条删掉**（同时检查 highlights 有没有提到它），不要改写成差不多对的版本。第 5 条不过关：先按下一步补 evidence，补不上再整条删掉。

**这一步必做**，完成后确认两项：

- [ ] 自检结果记进了生成记录：自检删掉的条目 validate 看不到，要你自己记，每条写它用的候选 id、标题和一句原因。没有删掉任何条目也要记，传一个空列表 `[]`，这样页面能分清「自检过、没删」和「没做自检」。没有记录时 validate 会发 WARN。
- [ ] `generated_at` 是真实时间：用 `date -u +%Y-%m-%dT%H:%M:%S+00:00` 取，不要手写整点。

```bash
uv run python -m daily trace self-check --date <期号> <<'EOF'
[{"candidates": ["c_1b6d7a5398"], "title": "DeepSeek 开源推理框架 DeepInfer", "reason": "原文没说开源，摘要写成了开源"}]
EOF
```

## 6. 预检与校验

流程：写完 → 自检 → 预检 → 补 evidence → 正式校验。

### 预检（只跑一轮）

```bash
uv run python -m daily validate --date <期号> --check-links    # 不带 --drop-invalid：只报告，不写文件
```

有不合格条目时退出码是 1，这是预期的；看 `DROP` 行逐条处理。如果出现 `ERROR` 行（例如 highlights 提到了不合格的条目），这一轮没有联网核对链接和引文，正式校验时还可能删掉别的条目。

预检之后，**只允许下面三种修改**：

- **补充或延长 evidence 引文**：用 `uv run python -m daily page <url> --grep "<关键词>"` 从原文逐字复制，把缺的数字、模型名、版本号包含进去。evidence 的 url 必须是本条的某个 source。
- **打开还没打开的一手来源**：用 WebFetch 打开，记进 `research`（`via` 为 `webfetch`），再从中摘 evidence。这里的 WebFetch 算进每天 30 次的预算。
- **整条删掉**：同时检查 highlights 有没有提到它，提到了就一起删去相关内容。

**不允许改写正文**（标题、summary）去迁就材料：原文里找不到某个写法（例如正文写 `OpenMDW-1.1`，原文是 "version 1.1"），就整条删掉。预检不重跑，改完直接进入正式校验。

### 正式校验

```bash
uv run python -m daily validate --date <期号> --check-links --drop-invalid
```

- **退出码 0**：通过。stderr 里的 `DROP` 行是被删掉的条目和原因，已经记录在 digest.json 的 `validation` 里。不要把它们改写后重新加回来。
- **退出码 1**：整期不合格（`ERROR` 行）。
  - 如果是 highlights 提到了被删掉的条目：只改 highlights，删去相关内容，然后再跑一次。**不要手动删条目**：这次运行什么都没写，重跑时让 validate 删掉它们，原因才会记进 `validation.dropped`。
  - 如果是 JSON 或字段结构的错误：修一次，然后再跑一次。
  - 剩下的条目少于 3 条，或者修过之后仍然失败：运行 `uv run python -m daily degrade --date <期号> --force`，发布降级版。
- `WARN` 行（条数不在目标范围、链接无法检查等）不阻止发布，看一眼即可。

## 7. 英文版

中文版通过正式校验后，接着写英文版 `data/<期号>/digest.en.json`。中文版最后发布的是降级版时，不写英文版（英文页直接用原文标题）。

- **从校验后的 digest.json 开始**：复制一份，加上 `"lang": "en"`，`generated_at` 改成现在，删掉 `validation` 字段。版块、顺序、`sources`、`evidence`、`research`、`tags`（仍用中文词表）都不动。
- **只重写 `title`、`summary`、`highlights`**：依据原文和 evidence 直接用英文写，**不要翻译中文版**。两版各自报道同一批原文，中文里的意译、换算不要带过来。
- 不打开新页面，不加条目，也不改 evidence。某条写不好就整条删掉，同时检查 highlights。
- 写作规范同第 4 步，英文对应的写法：
  - **标题**：说清 who did what，最好不超过 70 个字符（硬上限 120），sentence case。不用 groundbreaking、game-changing、revolutionary 之类的词。
  - **summary**：2–3 句，先说是什么，再说对开发者意味着什么。快讯 1 句，不超过 250 个字符。
  - 数字、模型名、版本号照原文写法，validate 同样会逐个核对。
  - 正文里不放链接。
- 自检同第 5 步。
- 校验只跑一轮（引文已经在中文版的校验里核对过）：

  ```bash
  uv run python -m daily validate --date <期号> --en --drop-invalid
  ```

  - **退出码 0**：通过，`DROP` 行的条目已删掉，不要改写后加回来。
  - **退出码 1**：如果是 highlights 提到了被删掉的条目，只改 highlights，再跑一次。别的情况，或者再跑仍然失败：删掉 `digest.en.json`，照常提交中文版。英文版失败不影响中文版发布，英文页会只显示原文标题。

## 8. 渲染与提交

```bash
uv run python -m daily render --date <期号>      # → data/<期号>/digest.md
git add data/<期号>/digest.json data/<期号>/digest.md data/<期号>/trace.claude.json data/<期号>/digest.en.json   # 没有英文版就去掉最后一个
git commit -m "digest: <期号>"
git push -u origin HEAD                  # 推到当前分支，不要开 PR
```

- **定时任务（cloud session）**：只能推到本会话指定的 `claude/` 分支，照常推送即可。推送会触发
  `.github/workflows/ingest.yml`：它用 main 上的 candidates.json 重新校验 digest.json，按上面第 0 步的规则
  并入 main（降级版会被正式版替换，正式版不会被降级版覆盖），再重建网站。分支上的其他改动不会进入 main。
- **本地在 main 上运行**：推到 main 会直接触发 `.github/workflows/pages.yml` 重建网站。
- push 被拒绝（远端有新提交）：`git pull --rebase` 之后再推一次。

最后用几行话报告：入选几条、被 validate 删掉几条（原因）、英文版写了几条（或者为什么没写）、用了几次 WebFetch / WebSearch、有没有失败的信源。

## digest.json schema

```jsonc
{
  "schema_version": 1,
  "date": "2026-10-21",                       // 期号，必须和 candidates.json 一致
  "mode": "full",                             // full：编辑版；fallback：degrade 生成的降级版
  "channel": "claude",                        // 必填：写这一期的通道，你永远写 claude；缺了 validate 会报错
  "generated_at": "2026-10-20T21:40:00+00:00", // 用 date -u 取真实时间
  "model": "claude-opus-5-5",                 // 可选：你自己的模型 ID，网站页脚显示“本期由 … 编辑”；不确定就省略
  "highlights": ["今日要点第一句。", "第二句。"],   // 1-3 句，不含链接
  "items": [                                  // 按版块的顺序写，版块内按重要性排
    {
      "section": "headline",                  // headline | model | paper | tool | brief
      "title": "DeepSeek 开源推理框架 DeepInfer",
      "summary": "是什么……。对开发者意味着什么……。",
      "sources": [                            // 第一个是主来源；至少一个不是讨论帖
        {"candidate_id": "c_1b6d7a5398"},                    // 候选：url 可省略，默认是候选的 url
        {"candidate_id": "c_1b6d7a5398", "url": "https://news.ycombinator.com/item?id=…"},  // 候选的其他链接（讨论帖、also_from）
        {"url": "https://api-docs.deepseek.com/news/…", "title": "DeepSeek"}   // 不在候选里：必须在 research 里 webfetch 过
      ],
      "evidence": [                           // 原文逐字引用；url 必须是本条的某个 source
        {"url": "https://github.com/deepseek-ai/DeepInfer", "quote": "…verbatim text…"}
      ],
      "tags": ["开源", "推理"]
    }
  ],
  "research": [                               // 每次 WebFetch / WebSearch 都记一条
    {"via": "webfetch", "url": "https://github.com/deepseek-ai/DeepInfer"},
    {"via": "websearch", "query": "Qwen3.8 release"}
  ]
}
```

英文版 `digest.en.json` 用同一个 schema，多一个 `"lang": "en"`，标题和 summary 的长度上限按英文放宽（见第 7 步）。

同一个候选只能被一条使用。`validate --drop-invalid` 会补全省略的 url，并追加 `validation` 字段，不要手写这个字段。
