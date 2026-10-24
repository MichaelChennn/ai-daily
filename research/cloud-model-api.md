# 云端模型 API 选型调研（issue #14）

调研日期：2026-10-25。下文所有网页都在这一天读取；官方页面标了页脚上的 "Last updated" 日期。

## 结论

| | 供应商 | 模型 | base_url |
|---|---|---|---|
| **默认** | Gemini API 免费档 | `gemini-3.5-flash-lite` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| **备选** | OpenRouter 免费模型 | `google/gemma-4-31b-it:free` | `https://openrouter.ai/api/v1` |

- Gemini 免费档里最强的 `gemini-3.8-flash` 能力更好，但有社区报告说它的免费额度只有 **20 RPD**，跑一次 Beta 版的 tool-call 循环可能就用完了。所以默认用 Flash-Lite，同一份社区报告说它是 500 RPD。英文版只要 2–3 次请求，可以单独配成 `gemini-3.8-flash`（见下面的变量）。
- 中文 Beta 版 + 英文版每天两份，**免费额度按请求数够用**，前提是两条：`fetch_page` 工具要**截断页面文本**（建议 ≤ 12,000 字符），而且要允许模型一轮发多个并行 tool call。估算见「用量估算」。
- 这些 RPM / RPD / TPM 数字 Google 没有公开成表，只在 AI Studio 里按项目显示。第一次配好密钥后，去 AI Studio 的 rate limit 页面核对一遍，再定循环的轮数上限和节流间隔。
- 排除的：**NVIDIA build.nvidia.com**（试用条款禁止生产使用）、**Groq**（8K TPM，第一次请求就超）、**硅基流动**（免费模型只有 7B 级小模型）。理由见下文。
- 中文写作质量没有找到一手的、能直接比较这几个模型的评测。这一项是判断，不是查到的事实。建议在 API 通道实现之后，用 `data/2026-10-24` 跑一次默认和备选，和主版并排看一眼再拍板。

### 要存的 GitHub secrets / variables

| 名字 | 类型 | 默认值 |
|---|---|---|
| `EDITOR_API_KEY` | secret | Gemini API key（AI Studio 里创建） |
| `EDITOR_API_BASE_URL` | variable | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `EDITOR_API_MODEL` | variable | `gemini-3.5-flash-lite` |
| `EDITOR_API_MODEL_EN` | variable，可选 | 不设就用 `EDITOR_API_MODEL`；想让英文版写得好一点可以设 `gemini-3.8-flash` |

切换到备选只改这三项：`EDITOR_API_KEY` 换成 OpenRouter key，`EDITOR_API_BASE_URL` 设 `https://openrouter.ai/api/v1`，`EDITOR_API_MODEL` 设 `google/gemma-4-31b-it:free`。如果以后要做「默认失败自动切备选」，再加一套 `EDITOR_API_FALLBACK_KEY` / `_BASE_URL` / `_MODEL`；第一版不需要。

## 用量估算（本地实测，2026-10-24 这一期）

### 实测大小

| 输入 | 实测 | 折算 token（约） |
|---|---|---|
| `.claude/skills/daily-editor/SKILL.md`（将成为 system prompt） | 6,320 字符，其中汉字 2,089 | ≈ 3.2k（汉字按 ~1 token/字，其余按 ~4 字符/token） |
| `daily list --date 2026-10-24`（87 条候选，几乎全是英文） | 24,192 字符 | ≈ 6k |
| 原文页面文本（和 `daily page` / `validate --check-links` 同一套抽取），这期 digest 用到的 12 个 URL | 3.5k–112k 字符，中位数约 28k；openai.com 两个页面 403 | 中位 ≈ 7k，最大 ≈ 28k |
| `daily page --grep`（每个关键词前后 200 字符，最多 5 处） | 每次几百到 2k 字符 | ≈ 0.1–0.5k |
| 产出 `digest.json`（8 条） | 9,713 字符，其中汉字 763 | ≈ 3k |

页面文本的明细：MiniMax HF 模型卡 70,649；HF papers 两篇 17,959 / 26,901；claude-code release 7,373；codex release 30,303；sverigesradio 3,573；HN 讨论 40,205；anthropic.com research 55,820；kimi.ai blog 23,288；NVIDIA HF 模型卡 112,277。

每期候选在 100 条左右时，`daily list` 按比例约 7k token。

### Beta 版一次运行

- 固定前缀：system prompt ≈ 3.2k + 工具定义 ≈ 0.8k + `list` 结果 ≈ 7k，**约 11k**。
- 抓原文 ≤ 20 次：如果 `fetch_page` 截到 12k 字符（≈ 3k token），合计约 60k；**不截断**的话按中位数算约 140k，碰上几个 HF 模型卡还会更多。
- 摘录引文（`page --grep`）约 5 次，约 2k；写 digest 约 3–4k 输出；validate 往返 1–2 轮。
- 最后一轮的上下文：截断时约 80k，不截断约 200k 以上。几个候选模型的上下文都放得下（Gemini 3.5 Flash-Lite / 3.8 Flash 都是 1,048,576 输入 token），但截断后每轮重发历史的成本小很多。

请求数和累计输入 token（每一轮都会把整个历史重发一遍）：

| 循环方式 | 请求数 | 累计输入 token |
|---|---|---|
| 并行 tool call（一轮抓 4–5 页） | 约 12–15 | 约 0.5–0.7M |
| 串行（一轮一个 tool call） | 约 30 | 约 1.2–1.5M |
| 串行且页面不截断 | 约 30 | 约 3M 以上 |

### 英文版一次运行

英文版沿用主版的条目和 evidence，直接用英文写，不用调研：输入是条目和 evidence（约 3k）+ 英文写作规则（约 2k），输出约 2.5k；1 次写作 + 最多 2 次 validate 修正，**约 3 次请求、累计 20k token 以内**，是 Beta 版的 2–3%。

### 和免费额度对比

| | 一天要用的量（Beta + 英文） | 免费额度 | 够不够 |
|---|---|---|---|
| Gemini `gemini-3.5-flash-lite` | 15–33 次请求 | 500 RPD（社区报告，见 [G5]） | 够，余量大 |
| Gemini `gemini-3.8-flash` | 同上 | 20 RPD（社区报告，见 [G5]） | Beta 版不够；只跑英文版（3 次）够 |
| OpenRouter `:free` | 同上 | 20 RPM；50 RPD，累计买过 ≥ 10 credits 后 1,000 RPD [O1] | 不买 credits 时很紧（并行循环勉强）；买一次 10 美元后够 |

TPM：最后一轮约 80k token，如果 AI Studio 显示的 TPM 是几十万这个量级，一分钟只能发两三轮，循环里要有节流（仓库里已有 `daily/throttle.py`）。Google 论坛上有人报告某个模型免费档只有 5 RPM，不够跑一轮 agent [G5]，所以 RPM 也要在 AI Studio 里核对。

## 各家详情

### Gemini API 免费档（默认）

- OpenAI 兼容：base_url `https://generativelanguage.googleapis.com/v1beta/openai/`，支持 function calling、streaming、structured output；官方写明 "Support for the OpenAI libraries is still in beta while we extend feature support" [G3]。
- 免费档的模型（官方定价页）：Gemini 3.8 Flash、3.6 Flash、3.5 Flash-Lite、3.1 Flash-Lite 免费；Gemini 4 Argon、3.1 Pro Preview 没有免费档；Gemma 4 免费且只有免费档 [G2]。
- 模型规格：`gemini-3.8-flash`（New Stable）和 `gemini-3.5-flash-lite`（Stable）都是 1,048,576 输入 / 65,536 输出 token，都支持 function calling 和 thinking；3.8 Flash 不支持 minimal thinking 级别，传了会报错 [G4][G6][G7]。
- 额度：官方页面不列具体数字，"can be viewed in Google AI Studio"；额度按项目算，不按 key 算；RPD 在太平洋时间午夜重置；任意一项超限就报错 [G1]。具体数字只有论坛帖：3.8 Flash 20 RPD，Flash-Lite 500 RPD（2026-09-03 的帖子，没有 Google 员工回复）[G5]。
- 数据：免费档 "Content used to improve our products"，付费档不会 [G2]。我们的输入是公开网页、输出要公开发布，SKILL.md 也在公开仓库里，所以这一点可以接受。
- 地区：GitHub Actions runner 在美国，可用。中国大陆和香港不在可用地区列表里 [G8]，在本地调试要走代理。
- 付费价（万一要升级）：3.5 Flash-Lite 输入 $0.30 / 输出 $2.50 每 1M token；3.8 Flash 到 2026-12-31 为 $0.75 / $3.75，2027-01-01 起 $1.50 / $7.50 [G2]。按上面的估算，一期 Beta 版用 Flash-Lite 付费也只要约 0.2–0.5 美元。

### OpenRouter 免费模型（备选）

- 额度：`:free` 模型 20 RPM；累计购买不到 10 credits 时 50 RPD，≥ 10 credits 时 1,000 RPD [O1]。
- 2026-10-25 从 `GET https://openrouter.ai/api/v1/models` 拉到的、`supported_parameters` 含 `tools` 的免费模型共 16 个，包括 `google/gemma-4-31b-it:free`、`google/gemma-4-26b-a4b-it:free`（262,144 上下文）、`nvidia/nemotron-3-super-120b-a12b:free`、`nvidia/nemotron-3-ultra-550b-a55b:free`、`thinkingmachines/inkling:free` 等。**没有** Qwen、DeepSeek、Kimi、GLM 这几家中文强项模型的免费版。
- 数据：免费模型和付费模型有各自独立的训练设置；在账号里关掉训练，OpenRouter 就不会路由到会训练的供应商 [O2]。Gemma 4 免费版的上游是 Google AI Studio，Nemotron 免费版的上游是 NVIDIA（endpoints 接口实测 [O3]）。
- 注意：Gemma 4 免费版的上游也是 Google，Google 那边出问题时它可能一起挂。要一个和 Google 完全无关的备选，可以把模型换成 `nvidia/nemotron-3-super-120b-a12b:free`，但它的中文写作没验证过。

### NVIDIA NIM / build.nvidia.com（排除）

- 接口：`https://integrate.api.nvidia.com/v1/chat/completions` [N1]；论坛上普遍报告默认 40 RPM，版主说免费档没有正式的提额途径 [N3]。
- **排除原因在条款**：NVIDIA API Trial Terms of Service（PDF 创建于 2025-10-07）1.2 节："access to the API Service for limited trial purposes only and without use of the API Service or Generated Content in production"；1.4 节："you may only use the API Service for internal testing and evaluation purposes, not in production" [N2]。每天自动发布的公开日报就是生产用途。
- 数据：3.3 节，NVIDIA 会收集 "User Content and Generated Content to improve NVIDIA products and services, including AI models" [N2]。

### Groq（排除）

- 官方限额页列的是 Developer 档的基础限额（Free 档要登录后看）：`openai/gpt-oss-120b`、`qwen/qwen3.8-27b` 都是 30 RPM / 1K RPD / **8K TPM** / **200K TPD** [Q1]。
- 第一次请求（system prompt + `list`）就有约 11k token，超过 8K TPM；一天 200K TPD 也不够一期 Beta 版（0.5M 以上）。免费档只会更低。

### 硅基流动 SiliconFlow（排除）

- 官方定价页上标「免费」的对话模型只有 `tencent/Hunyuan-MT-7B`（翻译模型）和 `XingChenAGI/Xing4.0-29B`，其余免费项是 embedding / rerank / OCR [S1]。没有能跑这种 agent 循环的大模型免费版。
- 第三方站点说注册送 ¥14 额度，没有在官方页面上核实。限速文档的官方 URL 在调研当天返回 404。它的付费 DeepSeek / Qwen 价格便宜，如果以后愿意花一点钱、而且想要更好的中文，可以重新考虑。

## 实现时要注意的

1. `fetch_page` 必须截断（建议 12,000 字符），再单独给一个 `grep_page` 工具（等同 `daily page --grep`）去逐字摘录 evidence。不截断的话，累计 token 会翻好几倍。
2. 打开并行 tool call，并在 system prompt 里鼓励模型「一轮抓多页」，这样请求数从约 30 降到约 15。
3. 循环加上限（例如 25 轮）和按 RPM 的节流；遇到 429 时指数退避，RPD 用完就让 Beta 版这一天跳过，不影响主版。
4. Gemini 的 OpenAI 兼容层还是 beta [G3]；工具参数解析失败、空回复这类情况要当作可重试的错误处理。
5. 第一次配置 key 后，把 AI Studio 里看到的真实 RPM / TPM / RPD 补进这份文档。

## 来源

- [G1] Gemini API Rate limits，https://ai.google.dev/gemini-api/docs/rate-limits（Last updated 2026-10-15 UTC）
- [G2] Gemini API Pricing，https://ai.google.dev/gemini-api/docs/pricing（Last updated 2026-10-22 UTC）
- [G3] Gemini API OpenAI compatibility，https://ai.google.dev/gemini-api/docs/openai（Last updated 2026-10-22 UTC）
- [G4] Gemini models，https://ai.google.dev/gemini-api/docs/models
- [G5] Google AI 开发者论坛「Gemini 3.8 Flash Free Tier 20 RPD Is Too Limited for Practical Evaluation」，https://discuss.ai.google.dev/t/gemini-3-8-flash-free-tier-20-rpd-is-too-limited-for-practical-evaluation/180609（2026-09-03，用户帖，非官方）
- [G6] Gemini 3.8 Flash，https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash（Last updated 2026-10-22 UTC）
- [G7] Gemini 3.5 Flash-Lite，https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite（Last updated 2026-10-22 UTC）
- [G8] Gemini API available regions，https://ai.google.dev/gemini-api/docs/available-regions（Last updated 2026-10-22 UTC）
- [O1] OpenRouter API Limits，https://openrouter.ai/docs/api/reference/limits
- [O2] OpenRouter Provider Logging，https://openrouter.ai/docs/guides/privacy/provider-logging
- [O3] OpenRouter 模型和 endpoints 接口，https://openrouter.ai/api/v1/models、https://openrouter.ai/api/v1/models/google/gemma-4-31b-it:free/endpoints（2026-10-25 实测）
- [N1] NVIDIA NIM LLM APIs reference，https://docs.api.nvidia.com/nim/reference/llm-apis（2026-10-23）
- [N2] NVIDIA API Trial Terms of Service，https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf（PDF 创建于 2025-10-07）
- [N3] NVIDIA 开发者论坛提额帖，例如 https://forums.developer.nvidia.com/t/api-rate-limit-increase-is-not-granted-by-requesting-it-here/368420（用户帖与版主回复，非正式文档）
- [Q1] Groq Rate Limits，https://console.groq.com/docs/rate-limits（页面无日期）
- [S1] 硅基流动定价，https://siliconflow.cn/pricing
