# 2026-10-23 · AI 科技日报

## 今日要点

- Anthropic 用 Claude 为 123 个开源库的 239 个入口点写出形式化证明，过程中发现数百个 bug。
- Agent Skills 标准捐给 Agentic AI Foundation，NVIDIA 开源 Agent 安全运行时 OpenShell。
- OpenAI 推出官方命令行工具 OpenAI CLI。

## 🔥 头条

### Anthropic 用 Claude 为 123 个开源库写出形式化证明

Anthropic 让 Claude 在几周内修复发现的 bug，并证明 123 个 OSS-Fuzz 开源库的 239 个入口点在 64 MB 以内的任何输入下都不会崩溃；证明直接作用在编译后的 RISC-V 指令上，尝试证明的过程中发现了数百个 bug。形式化验证过去只适用于小代码库，这项工作说明大模型能把它扩展到真实生产库；但文中也强调，“形式化验证”不等于“没有 bug”。

来源：[Anthropic Research](https://www.anthropic.com/research/formal-verification) · [HN 讨论](https://news.ycombinator.com/item?id=50202217)　`安全` `代码` `Agent`

### Anthropic 把 Agent Skills 标准捐给 Agentic AI Foundation

Anthropic 将 Agent Skills 开放标准（连同名称、GitHub 组织和 agentskills.io 域名）捐给 Linux 基金会旗下的 Agentic AI Foundation（AAIF），由来自 Anthropic、Google、OpenAI 等公司的工程师以个人身份维护。ChatGPT、Cursor、GitHub Copilot、VS Code 等 70 多个 Agent 平台已经集成该标准；继 MCP 之后它也有了中立的归属，开发者不加入 AAIF 也能继续使用和贡献，写一次 Skill 跨平台复用更有保障。

来源：[Anthropic News](https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation)　`Agent` `行业`

### NVIDIA 开源 Agent 安全运行时 OpenShell

OpenShell 是 NVIDIA 开源的自主 Agent 运行时（Apache 2.0）：用策略声明每个 Agent 能访问什么，在内核层隔离沙箱，所有网络连接出沙箱前都要经过策略检查，Agent 也看不到真实凭据，只有发往批准端点的请求才会被注入凭据。支持 Linux、Apple Silicon 上的 macOS 和 WSL 2（实验性）；想让 Agent 自主装包、调 API 又担心越权，可以拿它做隔离层。

来源：[GitHub](https://github.com/NVIDIA/OpenShell) · [HN 讨论](https://news.ycombinator.com/item?id=50198675)　`开源` `Agent` `安全`

## 🧠 模型

### 蚂蚁 inclusionAI 开源医疗模型 Ling-3.0-flash-Sante

Ling-3.0-flash-Sante 基于 Ling-3.0-flash，总参数 124B、每 token 激活 5.1B，采用 KDA、gated MLA 与稀疏 MoE 的混合线性架构，训练上下文扩展到 256K，面向医学推理、医疗研究和工具辅助工作流，权重已上架 Hugging Face 和 ModelScope。做医疗方向研究或 Agent 可以直接拿来实验，但官方明确它是研究模型而非医疗器械。

来源：[Hugging Face](https://huggingface.co/inclusionAI/Ling-3.0-flash-Sante) · [Reddit 讨论](https://www.reddit.com/gallery/1xcljvi)　`模型` `开源`

### Bria 发布 Fibo 2.0：生成与编辑合一的 8B 图像模型

Fibo 2.0 是 8B 参数的 flow-matching 模型，工作在 FLUX.2 VAE 的潜空间，用 Qwen3-VL-4B-Instruct 编码提示词，一套权重同时做文生图和图像编辑；Dev 版是未蒸馏的基础模型，适合作为 LoRA 或全量微调的起点，ComfyUI 已有对应权重。许可是 CC BY-NC 4.0，商用需要另签协议。

来源：[briaai/Fibo-2.0-dev](https://huggingface.co/briaai/Fibo-2.0-dev) · [Comfy-Org/Fibo-2.0](https://huggingface.co/Comfy-Org/Fibo-2.0)　`模型` `图像`

## 📄 论文

### Cache Engineering：让 Agent 直接管理自己的 KV cache

论文提出 cache engineering：Agent 不改写对话历史，而是用 drop 把选中的缓存排除出后续注意力、用 repos 调整保留 key 的位置编码，从而避免上下文裁剪或摘要带来的重新 prefill；配套的服务系统 AKV 已开源。与常规的阈值触发摘要相比，按工具返回滚动丢弃的策略让平均分提高 1.7 分、平均成本降低 27.7%，对长轨迹 Agent 的推理成本很有参考价值。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.28577)　`论文` `Agent` `推理`

### StreamEval：交互式流式视频生成基准

StreamEval 覆盖数字人对话、数字人表演、世界生成、指令编辑和参考编辑五类任务，共 300 个 15–300 秒的脚本化用例，请求在生成过程中陆续到达。作者评测了 37 个模型，发现画质高、身份保持好并不等于能可靠执行请求，请求执行仍是短板；做实时视频生成或数字人的团队可以用它找到模型的真实弱项。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.28402)　`论文` `视频`

### Qwen-Audio-3.1-ASR 技术报告

Qwen-Audio-3.1-ASR 在 Qwen-Audio-3.0-ASR 基础上改进识别，并新增说话人分离转写和通用音频理解，继续支持 30 种语言和 16 种汉语方言，还支持上下文、分层热词和原生转写润色。家族提供异步文件转写、低延迟流式、交互式语音输入和非流式识别等变体，方便按部署场景选型；报告未说明是否开放权重。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.28711)　`论文` `语音`

## 🛠 开源与工具

### langchain-core 1.7.0：工具调用参数改为增量流式输出

langchain-core 1.7.0 让流式工具调用参数以 tool-call-delta 增量片段输出，不再是到目前为止参数的 block-delta 快照；.tool_calls.get() 和 .output 不变。直接读原始流事件的代码需要改读 tool-call-delta，想保留旧行为可以固定 langchain-core<1.7。

来源：[GitHub Releases](https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D1.7.0)　`工具` `Agent`

### Claude Code v2.1.309 修复一批沙箱与权限问题

v2.1.309 修复了沙箱中 Bash 命令在沙箱外执行 shell 启动文件、沙箱命令和自动接受的编辑可修改 --mcp-config 指定的 MCP 配置文件等问题，并收紧了多处 Bash 权限检查和 worktree 隔离；v2.1.308 为缺陷修复与稳定性改进。依赖沙箱或权限规则的用户建议尽快升级。

来源：[anthropics/claude-code v2.1.309](https://github.com/anthropics/claude-code/releases/tag/v2.1.309) · [anthropics/claude-code v2.1.308](https://github.com/anthropics/claude-code/releases/tag/v2.1.308)　`工具` `代码` `安全`
