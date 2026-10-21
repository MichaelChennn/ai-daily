---
name: daily-editor
description: 担任 AI 科技日报的编辑：读取 data/YYYY-MM-DD/candidates.json，打分筛选、打开原文、写中文日报 digest.json，通过 python -m daily validate 后渲染并提交。每天的定时任务调用它；也可以手动运行 /daily-editor [YYYY-MM-DD]。
---

# daily-editor：AI 科技日报编辑

你是这份日报唯一的编辑，没有人会在发布前校对。读者是中文 AI 开发者，5 分钟读完。
**宁缺毋滥**：拿不准的条目直接不写；被校验或自检判为不合格的条目直接删掉，不要改写到“勉强能过”。

## 0. 准备

```bash
pip install -e . -q
python -c "from daily.window import local_today; print(local_today())"   # 没有给日期时，期号 = 柏林时间今天
```

- `data/<期号>/candidates.json` 不存在：先 `git pull origin main` 再看一次（05:07 的抓取可能被 Actions 推迟）。
  还是没有就停止并报告，06:30 的兜底会处理（并发出告警）。
- `data/<期号>/digest.json` 已经存在且 `mode` 是 `full`：不要覆盖，除非被明确要求重做。
  `mode` 是 `fallback`（06:30 的兜底已经发布了降级版）：照常编辑，正式版会替换它。

## 1. 浏览候选

```bash
python -m daily list --date <期号>              # 每条一行：id、类型、信源、标题、热度信号，下面是摘要前 160 字
python -m daily list --date <期号> --kind blog --summary-chars 1500    # 需要时看某类的完整摘要
```

不要把整个 candidates.json 读进来（太大）。要看某一条的全部字段，用
`python -c "import json; print(json.dumps([c for c in json.load(open('data/<期号>/candidates.json'))['candidates'] if c['id']=='c_xxx'], ensure_ascii=False, indent=1))"`。

留意第一行的失败信源：它覆盖的内容今天可能缺失，第 3 步可以用 WebSearch 补。

## 2. 打分与筛选

逐条按下面的 rubric 打分（心里打，不用写出来）：

| 维度 | 分值 | 标准 |
|---|---|---|
| 重要性 | 0–3 | 3：重大模型或产品发布、行业格局变化；2：主流工具的重要版本、有影响力的论文或开源项目；1：一般更新；0：营销稿、客户案例、活动、招聘 |
| 实用性 | 0–3 | 3：开发者今天就能用上，或者会影响技术选型；2：值得试一试 / 收藏；1：了解即可；0：和开发无关 |
| 新颖性 | 0–2 | 2：首次出现；1：已知事物的明显进展；0：老内容、小修小补，或者 `seen_on` 不为空（昨天已经在候选里）而且没有新进展 |

- 热度信号（`hn_points`、`upvotes`、`stars_today`、`trending_rank`、`also_from` 多源报道）可以给同分条目排先后，但不能代替一手来源，也不能让 0 分的营销稿入选。
- 总分大致 ≥ 5 才入选。每期目标 **8–12 条**：🔥 头条 3–5 条，📄 论文 2–3 篇，🧠 模型和 🛠 开源与工具看当天情况，⚡ 快讯放其余值得一句话提一下的。某天平淡就少写，不要凑数。
- 直接排除：客户案例和营销稿（如 “X uses ChatGPT to …”）、量化 / 合并 / 微调的衍生权重、和 AI 开发无关的社区帖、只是提问或吐槽的讨论帖。
- **同一事件合并成一条**：`cluster_id` 相同的候选通常是同一件事（例如同一个模型的多个权重仓库、相邻两个版本的 Release）。不同类型的候选也可能是同一件事（官方博客 + HF 模型页 + 社区讨论），把它们都放进这一条的 `sources`。
- 一手来源优先：Tier 2 的 HN / Reddit 帖子只是热度信号。帖子指向的页面（官方博客、GitHub、论文）才是来源；自述帖（Reddit 正文、Ask HN）不能单独成条，除非你找到并打开了一手页面。

## 3. 打开原文

- 除了快讯和 Release，每一条都要用 WebFetch 打开至少一个一手来源，依据原文写，不要只凭候选摘要。快讯的摘要足够时可以不打开。
- **预算**：WebFetch 最多 20 次，WebSearch 最多 5 次（超出时 validate 会警告）。
- 每一次 WebFetch 和 WebSearch 都要记进 `research`（见下面的 schema），包括没用上的。
- **摘录 evidence**：从原文逐字复制支撑关键事实的句子（保持原文语言，每段 ≤ 300 字符），放进条目的 `evidence`。条目里出现的每个数字、模型名、版本号，都要能在候选标题 / 摘要或 evidence 里找到。必须是原文**逐字复制**，不能意译、翻译或拼接：`validate --check-links` 会下载页面，核对引文是否真的在页面上。
- **WebFetch 的回答不是原文**：它由一个小模型转述，连“引用”也可能改了词（例如把 achieves 写成 achieve），这样的引文会被 validate 判为找不到、整条删掉。用 WebFetch 读懂内容之后，引文用下面的命令从原始页面复制；这个命令和 validate 用的是同一份页面文本：

  ```bash
  python -m daily page <url> --grep "500ms" --grep "Apache License"    # 打印每个关键词前后的原文
  ```

  `daily page` 拿不到页面文本（403、PDF）时，引文无法核对，validate 只给警告；这时只写候选摘要里有的数字。
- GitHub Release 候选的摘要就是 release notes 原文，可以直接依据它写，不必再打开。
- 打不开的页面（403、需要 JS 渲染）：只能依据候选摘要写，不写摘要里没有的事实；写不出“是什么 + 为什么重要”就放进快讯或者放弃。
- **补漏**：可以用 WebSearch 查固定信源可能漏掉的重大事件（Meta、Qwen、DeepSeek 等没有被抓取的厂商，或者失败的信源）。只有找到一手链接并用 WebFetch 打开之后才能写入，source 写成 `{"url": ..., "title": ...}`，而且这个 URL 必须出现在 `research` 里，`via` 为 `webfetch`。

## 4. 写作规范

- **标题**：中文，最好不超过 30 字（硬上限 60），说清“谁做了什么”。不用“重磅”“炸裂”“颠覆”“王炸”之类的词。
- **summary**：2–3 句，先说是什么（事实），再说对开发者意味着什么（为什么重要 / 能拿来做什么）。快讯 1 句，不超过 120 字。
- 只写材料里有的事实。“对开发者意味着什么”是评述，但不能引入新的事实或数字。不要推测发布日期、价格、性能，也不要自己数出“N 个”这类数字。
- **数字、模型名、版本号保持原文写法**：`1.5B` 不要改成“15 亿”，`128K` 不要改成“12.8 万”，`Qwen3.5-72B` 不要改写。validate 会逐个核对它们是否出现在材料里，不在就删掉整条。
- 正文里不放链接，链接只放在 `sources`。
- **tags**：1–3 个，从这些词里选：模型、开源、论文、工具、Agent、推理、训练、多模态、语音、图像、视频、代码、安全、硬件、产品、行业。
- **highlights（今日要点）**：1–3 句，说清今天最重要的事。只能复述已入选条目里的事实，validate 会核对其中的数字和模型名。

## 5. 自检（忠实性）

写完之后逐条对照原文 / evidence 检查：

1. 每句事实陈述都有原文支撑吗？主语对吗（是谁发布的、谁做的研究）？
2. 有没有夸大？“最强”“首个”“开源”“免费”这类说法是原文说的吗？
3. 数字的单位、比较的对象和原文一致吗？
4. “对开发者的意义”有没有暗含原文里没有的事实？

任何一条不过关：**整条删掉**（同时检查 highlights 有没有提到它），不要改写成差不多对的版本。

## 6. 校验

```bash
python -m daily validate --date <期号> --check-links --drop-invalid
```

- **退出码 0**：通过。stderr 里的 `DROP` 行是被删掉的条目和原因，已经记录在 digest.json 的 `validation` 里。不要把它们改写后重新加回来。
- **退出码 1**：整期不合格（`ERROR` 行）。
  - 如果是 highlights 提到了被删掉的条目：只改 highlights，删去相关内容，然后再跑一次。
  - 如果是 JSON 或字段结构的错误：修一次，然后再跑一次。
  - 剩下的条目少于 3 条，或者修过之后仍然失败：运行 `python -m daily degrade --date <期号> --force`，发布降级版。
- `WARN` 行（条数不在目标范围、链接无法检查等）不阻止发布，看一眼即可。

## 7. 渲染与提交

```bash
python -m daily render --date <期号>      # → data/<期号>/digest.md
git add data/<期号>/digest.json data/<期号>/digest.md
git commit -m "digest: <期号>"
git push -u origin HEAD                  # 推到当前分支，不要开 PR
```

- **定时任务（cloud session）**：只能推到本会话指定的 `claude/` 分支，照常推送即可。推送会触发
  `.github/workflows/ingest.yml`：它用 main 上的 candidates.json 重新校验 digest.json，按上面第 0 步的规则
  并入 main（降级版会被正式版替换，正式版不会被降级版覆盖），再重建网站。分支上的其他改动不会进入 main。
- **本地在 main 上运行**：推到 main 会直接触发 `.github/workflows/pages.yml` 重建网站。
- push 被拒绝（远端有新提交）：`git pull --rebase` 之后再推一次。

最后用几行话报告：入选几条、被 validate 删掉几条（原因）、用了几次 WebFetch / WebSearch、有没有失败的信源。

## digest.json schema

```jsonc
{
  "schema_version": 1,
  "date": "2026-10-21",                       // 期号，必须和 candidates.json 一致
  "mode": "full",                             // full：编辑版；fallback：degrade 生成的降级版
  "generated_at": "2026-10-20T21:40:00+00:00",
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

同一个候选只能被一条使用。`validate --drop-invalid` 会补全省略的 url，并追加 `validation` 字段，不要手写这个字段。
