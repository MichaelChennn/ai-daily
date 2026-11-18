# 2026-11-18 · AI 晨报

## 今日要点

- OpenAI 发布 GPT-6.2 Astra 和 Sol，覆盖 ChatGPT Work、Codex 与 API，主打专业输出、编程、计算机操作与更低成本。
- K2-Horizon 一次性开源六个模型及训练全流程，包含完整开发历史、训练数据与基础设施代码。
- Google 与 Meta 同日把个人 Agent 推向落地：Gemini Tasks 可代办事务并付费，Muse 上线澳大利亚并接入大量本地服务。

## 🔥 头条

### OpenAI 发布 GPT-6.2 Astra 与 Sol

OpenAI 推出 GPT-6.2 Astra 和 Sol，改进专业输出、编程与计算机操作表现，并提升效率、降低成本，覆盖 ChatGPT Work、Codex 和 API。官方页面暂不可访问，开发者可关注其在 Codex 与 API 中的实际可用性和成本变化。

来源：[OpenAI News](https://openai.com/index/introducing-gpt-6-2-astra-sol)　`模型` `产品`

### K2-Horizon 开源六个模型与完整训练链路

K2 团队发布 K2-Horizon，包含从 0.9B 稠密模型到 375B-A23B MoE 的六个完全开源模型，面向通用推理与 Agent 任务。团队同时公开训练历史、中间检查点、预训练数据、训练日志以及 xLLM 训练框架和 RL360 强化学习栈，Uno 扩散适配器可在无需独立 draft 模型的情况下将解码提速最高 2.2x。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21003)　`模型` `开源` `推理`

### Gemini Tasks 上线，可代办事务与购物付款

Google 让 Gemini 通过邮箱、日历和支付方式处理预约、账单与购物等任务，并接入 Google Password Manager、Google Pay 和 Instacart 等服务。任务模式在 U.S.、Japan、Korea、Canada、Australia 和 India 免费推出，Gemini 目前与超过 60 个应用连接，开发者可申请加入 Connected Apps Platform。

来源：[Google AI Blog](https://blog.google/innovation-and-ai/products/gemini-app/tasks-in-gemini-free-new-features/)　`Agent` `产品`

### Meta Muse 上线澳大利亚，接入本地服务

Meta 的个人 AI Agent Muse 正式在澳大利亚推出，可连接 Gmail、Google Calendar、Instagram 和 OpenTable 管理邮件、日程与预订。澳洲本地合作伙伴包括 Canva、Domain、Kogan、MECCA、Officeworks、realestate.com.au、SWEAT、ShopBack 和 Ticketek，另有实时语音对话与自建 Spaces。

来源：[Meta Newsroom · AI](https://about.fb.com/news/2026/11/muse-is-now-available-in-australia/)　`Agent` `产品`

## 🧠 模型

### Maxwell-V1-Flash 开源：35B MoE，支持 256K 上下文

Maxwell 团队发布 Maxwell-V1.0-Flash MoE 语言模型，总参数 35B、每 token 激活 3B（均不含 embedding），上下文最长 256K tokens。其块稀疏注意力 Maxwell Block Sparse Attention 在 256K 下比 dense GQA 快 6.7x，权重以 Apache-2.0 许可发布，并提供了 vLLM 启动方式。

来源：[Hugging Face Trending Models](https://huggingface.co/maxwell-model/Maxwell-V1-Flash)　`模型` `开源`

### MiniMind 更新至 minimind-3，覆盖完整训练链路

minimind 仓库发布 minimind-3 / minimind-3-moe，结构主线对齐 Qwen3 / Qwen3-MoE 生态，Dense 约 64M、MoE 约 198M-A64M。项目以 PyTorch 原生实现覆盖 Pretrain、SFT、LoRA、RLHF-DPO、RLAIF、Tool Use 和 Agentic RL 全流程，普通个人 GPU 即可复现训练。

来源：[GitHub Trending](https://github.com/jingyaogong/minimind)　`模型` `开源` `训练`

## 📄 论文

### SWE-CoWork：编码 Agent 完成任务不足 8%

SWE-CoWork 基准在 101 个真实仓库上提供 101 个开发任务、11 种编程语言和 12 个应用领域，每个任务模拟一个含 26 名同事的工程组织。评测显示两个领先模型能满足约 63% 的 F2P 测试，却完成不到 8% 的任务，31% 被报告为完成的需求实际未通过测试。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.20218)　`论文` `Agent` `代码`

### SPILLWAY：用确定性检查拦截 Agent 提示注入

SPILLWAY 把 Agent 的目标准入与指令清洗分开：只允许来自用户任务或只读工具类型化字段的目标值通过，检查本身不调用模型。论文称在三种 backbone 与多个任务套件上，标准模板化注入未把动作重定向到攻击者目标，可选的本地 judge 只恢复被拒调用而不会恢复目标位于被删文本中的调用。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.07222)　`论文` `Agent` `安全`

### ScaleVLA：把 VLA 策略扩到 552B 参数

ScaleVLA 将 552B DeepSeek-V4.1-Flash 骨干接到可训练的 action DiT 上，并在统一训练设置下比较 2B 到 552B 的 VLM。实验显示 10 次演示即可超过用 50 次训练的 2B 骨干（87.8% 对 85.6%），LIBERO-PRO 成功率达 45.1%，真实充电头插入从 4/10 提升到 9/10，中位延迟为每个动作块 216 ms。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21607)　`论文` `多模态` `模型`

### VoxMel：无 tokenizer 的自回归 TTS 框架

VoxMel 用固定且完全可逆的双轴 Haar 变换把 mel 频谱分解为 Coarse-Mel 与残差层，让语言模型骨干自回归生成 Coarse-Mel，从而免去学习型声学 tokenizer。在 100K 小时 Emilia 数据上训练，监督版 0.6B 模型在 test-en 取得 1.51% WER 与 0.738 SIM，GRPO 优化后为 1.15% WER 与 0.753 SIM。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.20254)　`论文` `语音`

### MovieRoll：面向长视频的流式生成框架

MovieRoll 把流式微调、长 rollout 蒸馏和长时程推理串成一个 base-to-distilled 框架，其中 HieraKV 分层 KV 缓存压缩最多减少 78% 缓存内存并提升生成质量。在 HeliosBench 上，MovieRoll-Base 在只用最长 15s 视频训练后于 30s 保持竞争力，MovieRoll-Distilled 在最长 60s 的单事件与多事件评测中取得最高总分。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21339)　`论文` `视频`

### InclusionMed：医疗 AI 评测排名随场景变化

InclusionMed 是一个开放的医疗 AI 评测倡议，其 Atlas 按三类医疗角色和三类 AI 能力组织基准，首批从 388 个候选中审计并独立复现了 4 个公开基准，加上私有的 InclusionMed-DxFiles 共 5 个基准。前沿模型在 InclusionMed Index 上的总分从 17.5 到 49.1（满分 100）不等，排名随所选角色或能力而变化。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21218)　`论文` `评测`

## 🛠 开源与工具

### Anthropic 推出 Claude Platform 关联计费测试版

Anthropic 在 Claude Platform 上推出 linked billing beta，允许第三方平台让终端客户直接绑定自己的 Claude Platform 组织付费，无需共享 API key。客户可按平台设置月度支出上限并随时解绑，平台可选择由自己或终端客户承担每次请求的费用，Asana、Linear、Warp、Railway 等平台已支持。

来源：[Claude Blog](https://claude.com/resources/articles/linked-billing-on-claude-platform)　`工具` `产品`

### openai-agents-python v0.25.0 发布

openai-agents-python v0.25.0 开放第三方 session adapter 工具函数，新增可选的 handoff 错误恢复，并修复 MCP v2 并发 Streamable HTTP 请求等一批问题。版本同时将 GPT-6 Chat Completions 工具请求默认改为 non-reasoning，并更新了模型默认配置以对齐 TS SDK。

来源：[GitHub Releases](https://github.com/openai/openai-agents-python/releases/tag/v0.25.0)　`工具` `Agent`

### claude-code v2.1.327 修复会话丢失等一批问题

claude-code v2.1.327 新增 claude mcp add-json 从 stdin 读取服务器 JSON，令 token 不必出现在命令行，并在 /status 中列出损坏的 agent、skill、command 等文件。版本修复了会话恢复后消息丢失、后台 agent 状态判断错误、远程 MCP 服务器断连后无法恢复等问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.327)　`工具` `代码`

### codex 0.170.0 增加 TUI 语音与 MCP 支持

openai/codex 0.170.0 为 TUI 中的实时语音通话加入 WebRTC 协商，并为 OpenTelemetry HTTP exporter 增加自动刷新的认证 header。该版本还实验性支持在不同环境中使用同名 MCP 服务器，并修复了 WebSocket 超大请求回退、MCP OAuth 凭据竞态以及 Cloud 会话重连等问题。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.170.0)　`工具` `代码`

### PaperOrchestra：多 Agent 自动写论文框架

Google Cloud AI Research 开源 PaperOrchestra，一个用于自动化 AI 研究论文写作的多 Agent 框架，可把想法和实验日志等原始材料转为符合会议模板的 LaTeX 稿件。框架编排提纲、文献综述、分节写作、内容精修和绘图等专职 Agent，并提供自动文献综述、图表生成与 Streamlit 交互演示。

来源：[GitHub Trending](https://github.com/google-research/paper-orchestra)　`工具` `Agent` `开源`
