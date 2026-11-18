# 2026-11-18 · AI 晨报

## 今日要点

- OpenAI 发布 GPT-6.2 Astra 和 Sol，同步上线 ChatGPT Work、Codex 和 API；从 GPT-6.2 起，Responses API 改动对话前缀会丢弃 reasoning items，迁移前要检查集成。
- 开源模型方面，K2-Horizon 一次放出六个完全开放的模型（0.9B 到 375B-A23B），SenseNova-Loop-9B 正式版和 NVIDIA 面向本地语音助手的 Nemotron-3.5-Bolt-E4B 也已上架 Hugging Face。
- Claude Code 团队公开验证流程：约 90% 的代码由 Claude 编写和审查，靠端到端运行、verify skill 和按 diff 触发的检查清单兜底。

## 🔥 头条

### OpenAI 发布 GPT-6.2 Astra 和 Sol

OpenAI 推出 GPT-6.2 Astra 和 Sol，称专业产出、编码、computer use 和效率都有提升且成本更低，覆盖 ChatGPT Work、Codex 和 API。开发者文档建议最难的任务用 Astra、成本敏感的复杂工作用 Sol，并提示两处行为变化：Responses API 在对话前缀被修改后会丢弃 reasoning items，顶层 instructions 改为追加在 input 之后。迁移时应保持前缀不变，把可复用的指令放进 input 的第一条 developer 消息，以免推理质量下降、prompt caching 失效。

来源：[OpenAI News](https://openai.com/index/introducing-gpt-6-2-astra-sol) · [Using GPT-6.2 – OpenAI API docs](https://developers.openai.com/api/docs/guides/latest-model.md) · [HN 讨论](https://news.ycombinator.com/item?id=50535230)　`模型` `产品` `代码`

### K2-Horizon 发布六个完全开放的语言模型

K2-Horizon 一次发布六个完全开放的语言模型，从 0.9B 稠密模型到 375B-A23B MoE，面向推理和 Agent 工作，论文称在同尺寸开源模型中的 Agent 与编码基准上领先或有竞争力。它引入 MoVA（把 MoE 用在注意力的 value 投影上）和 softplus 注意力门控，其中 36B-A4B 以七分之一的激活参数接近同数据训练的 32B 稠密模型；Uno 扩散适配器无需单独的草稿模型即可把解码提速最多 2.2x。发布按 LLM360 的开源定义，连各训练阶段的中间 checkpoint、预训练数据、训练日志和代码一起公开，适合想复现或研究完整训练流程的团队。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21003)　`开源` `模型` `论文`

### Claude Code 团队公开如何让 Agent 验证自己的代码

Claude Code 团队介绍其验证做法：团队约 90% 的代码由 Claude 编写和审查，因此优先投入端到端测试、属性测试和差分测试，并把启动和驱动应用的步骤写成 verify skill 放在 .claude/skills/ 下，让 Claude 提交前先自测。检查连续三轮仍失败才交给人；另有一份 39 项的可靠性清单，Claude 读 diff 后只检查触发条件匹配的条目。想同时跑多个编码 Agent 的团队，可以直接照搬这套验证闭环。

来源：[claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/) · [HN 讨论](https://news.ycombinator.com/item?id=50529612)　`Agent` `代码` `工具`

### Gemini 任务模式免费开放：能打电话、付账单、办事

Google 让 Gemini 代用户完成预约、分析账单、购物等多步任务，它连接邮件、日历和支付方式，在隔离的虚拟机里执行。该功能使用新的 Gemini 4 Hydrogen 模型，免费面向美国、日本、韩国、加拿大、澳大利亚和印度推出，更高级的功能先在美国上线。消费级 Agent 正在直接接管真实账户里的操作，做同类产品的团队需要关注它在权限与隔离上的做法。

来源：[Google AI Blog](https://blog.google/innovation-and-ai/products/gemini-app/tasks-in-gemini-free-new-features/)　`产品` `Agent`

## 🧠 模型

### SenseNova-Loop-9B 正式版发布

SenseNova 在 Preview 之后发布 SenseNova-Loop-9B 正式版，Apache-2.0 许可：通过重复执行共享的中间层，把 32 个物理解码层扩展为 56 次层计算，接受文本和图像输入。官方称正式版在展示的七个基准上都超过 Preview，Agent 和数据分析评测与 Qwen3.8-27B 相当；4-bit 权重加 8-bit KV cache 时，256K 上下文多模态推理约需 15 GiB 显存。想在单卡上跑长上下文多模态 Agent，可以试一试。

来源：[Hugging Face Trending Models](https://huggingface.co/sensenova/SenseNova-Loop-9B)　`开源` `多模态` `模型`

### NVIDIA 发布本地助手小模型 Nemotron-3.5-Bolt-E4B

NVIDIA 基于 Gemma-4-E4B-it 后训练出 NVIDIA-Nemotron-3.5-Bolt-E4B-4GB，总参数 8B（有效 4B），Q4_K_M 精度，强化多轮工具调用、指令遵循和输入 grounding，面向本地语音/设备助手和嵌入式界面。它可搭配配套的 DFlash drafter 做投机解码，许可为 OpenMDW-1.1。需要低显存、低首 token 延迟的端侧 Agent，可以拿它做基座。

来源：[Hugging Face Trending Models](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-4GB)　`模型` `语音` `推理`

### Apple 发布交互级延迟视频生成模型 FastFrames

Apple 发布 FastFrames-S（1.3B）和 FastFrames-L（14B），都是自回归、两步的视频扩散模型，能以交互级延迟生成 480p 视频，其中 FastFrames-L 由 Wan2.1-14B 训练而来，权重许可为 apple-amlr。同时发布的优化版 LingBot 1.3B 比官方模型快 16x，支持相机控制。做实时、可交互视频生成的开发者可以参考。

来源：[Hugging Face Trending Models](https://huggingface.co/apple/FastFrames-L)　`视频` `模型`

### Maxwell-V1-Flash：35B 总参、3B 激活的开源 MoE

Maxwell 团队发布 Maxwell-V1.0-Flash，Apache-2.0 许可的 MoE 语言模型，总参数 35B、每 token 激活 3B，支持最长 256K 上下文，主打推理、Agent 和长上下文。它采用自研的 Maxwell Block Sparse Attention（MBSA），官方称该内核在 256K 下比稠密 GQA 快 6.7x。想要激活参数小、上下文长的本地模型，可以加入候选。

来源：[Hugging Face Trending Models](https://huggingface.co/maxwell-model/Maxwell-V1-Flash)　`开源` `模型`

## 📄 论文

### SWE-CoWork：把编码 Agent 放进模拟公司里干活

SWE-CoWork 包含 101 个开发任务，覆盖 101 个真实仓库、11 种编程语言，每个任务把 Agent 放进有 26 名同事的模拟工程组织，需要从同事和工作记录里找回需求再实现。领先的两个模型能通过约 63% 的 F2P 测试，但完整交付的任务不到 8%，而且自报完成的需求有 31% 过不了测试。结论是 Agent 的瓶颈在于从澄清到交付全程跟踪需求，这对设计多人协作的 Agent 工作流有参考价值。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.20218)　`论文` `Agent` `代码`

### SPILLWAY：不靠模型判断的提示注入防御

SPILLWAY 针对工具型 Agent 的提示注入：邮件发件人、付款账户这类目标来自工具的类型化字段，注入指令则以自由文本出现，于是它用一道确定性检查决定是否放行调用，不需要为每个任务做规划。只有当工具输出中出现、但用户任务里没有的目标值来自只读工具的类型化字段或固定的委托规则时，调用才会放行；论文称在三个 backbone 上，标准模板注入都没能把操作导向攻击者的目标。给能发邮件、付款的 Agent 加安全护栏时，这个思路成本低、可复用。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.07222)　`论文` `安全` `Agent`

### ScaleVLA：用 552B 模型做机器人策略骨干

ScaleVLA 把 552B 的 DeepSeek-V4.1-Flash 作为骨干接到可训练的动作 DiT 上，在统一训练设置下比较 2B 到 552B 的 VLM。结果显示，10 条演示就超过用 50 条训练的 2B 骨干（87.8% 对 85.6%），LIBERO-PRO 成功率 45.1%，而较小骨干最多 31.3%；真实充电器插接从 4/10 提升到 9/10，每个动作块的中位延迟为 216 ms。它说明前沿规模 VLM 的表征在机器人数据少时尤其有用。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21607)　`论文` `多模态`

### Accelerate Bench：考编码 Agent 优化整个程序的能力

Accelerate Bench 收录 32 个来自科学计算应用和超算竞赛的 CPU 优化任务，给出可运行程序、负载和正确性要求，让 Agent 自己决定在哪里、怎么优化。在 1.1 版上评测的 16 个编码 Agent，Score@1 从 25.5% 到 67.4%；多数程序都正确，拉开差距的是加速幅度。论文还发现同一份源码仅因构建和运行设置不同就会跑出 0.29x 到 2.12x，用 Agent 做性能优化时别只盯代码改动。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.20882)　`论文` `代码` `Agent`

## 🛠 开源与工具

### Google Research 开源 PaperOrchestra：多 Agent 写论文

Google Cloud AI Research 开源 PaperOrchestra，Apache-2.0 许可，用大纲、文献综述、分节写作、内容润色、绘图等专门 Agent，把想法和实验日志转成可投稿的 LaTeX 稿件，并自动检索整合相关文献。它可接 Gemini 或 OpenAI 的模型。想搭多 Agent 长文档生成流水线，可以参考它的分工设计。

来源：[GitHub Trending](https://github.com/google-research/paper-orchestra)　`开源` `Agent` `工具`

### Claude-BugHunter：漏洞挖掘用的 Claude Code skill 包

Claude-BugHunter 是面向漏洞赏金和外部红队工作的 Claude Code skill 包，其中的 hunt-* skills 整理自 681 份公开的 HackerOne 报告，含各类漏洞的检测模式、payload 和利用链模板，还带 Burp MCP 集成。可以在 Claude Code 里通过插件市场安装，按话题自动加载对应 skill。做授权渗透测试的安全团队可以拿来补充方法论。

来源：[GitHub Trending](https://github.com/elementalsouls/Claude-BugHunter)　`安全` `工具` `Agent`

## ⚡ 快讯

- **Claude Platform 推出 linked billing（beta）** 第三方平台可让终端客户直接用自己的 Anthropic 账户为 Claude API 用量付费，无需交出 API key，客户可自设消费上限。 [Claude Blog](https://claude.com/resources/articles/linked-billing-on-claude-platform)
- **Claude Code v2.1.327 发布** 新增 claude mcp add-json 从 stdin 读取服务器 JSON，避免 token 出现在命令行；/status 会列出损坏的 agent、skill 等配置文件。 [GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.327)
- **OpenAI Codex 0.170.0 发布** TUI 新增实时语音通话的 WebRTC 协商，实验性支持跨环境使用同名 MCP 服务器，并修复 MCP OAuth 凭据竞争等问题。 [GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.170.0)
- **Simon Willison 用 service worker 重写 Datasette Lite** Datasette Lite 改用 service worker 和 Pyodide 在浏览器里运行完整的服务端 Datasette，可加载 SQLite、CSV、JSON，并从 PyPI 安装插件。 [Simon Willison](https://simonwillison.net/2026/Nov/17/datasette-lite/)
