# 2026-10-30 · AI 科技日报

## 今日要点

- Mistral 开放 Mistral Large 4 权重，这是 1 万亿参数原生多模态 MoE 模型，面向编码与防御性安全场景。
- Liquid AI 发布 LFM3-Omni-2B，用单个 2.2B 模型端到端处理文本、图像、视频与音频，并支持语音输出。
- Recursive 开放 Flint 权重，这是一款面向编码 Agent 的 MoE 模型，总参数 39.8B、每 token 激活约 2.5B。

## 🔥 头条

### Mistral 开放 Mistral Large 4 权重，主打编码与防御性安全

Mistral 发布了 Mistral Large 4（Le Chonk）的权重，这是其 1 万亿参数、原生多模态的 MoE 模型。官方称它在编码和防御性安全基准上领先开源权重模型，并提供 low、medium、high 三档推理强度，开发者可自行托管和定制部署。

来源：[Mistral AI News](https://mistral.ai/news/mistral-large-4-oss/) · [GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.22.0) · [Hugging Face Trending Models](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B)　`模型` `开源` `推理`

### Liquid AI 发布 LFM3-Omni-2B，统一文本图像视频音频

Liquid AI 推出 LFM3 家族的首个全模态模型 LFM3-Omni-2B，单个端到端模型可理解文本、图像、视频和音频，并以文本或语音作答。参数量为 2.2B，定位手机、笔记本等端侧设备，一个模型即可替代 ASR、视觉语言、LLM 与 TTS 模型。

来源：[LiquidAI/LFM3-Omni-2B](https://huggingface.co/LiquidAI/LFM3-Omni-2B) · [LiquidAI/LFM3-VL-2B](https://huggingface.co/LiquidAI/LFM3-VL-2B)　`模型` `多模态` `语音`

### Recursive 开放 Flint 权重，专注编码 Agent

Recursive 发布了 Flint 的 BF16 权重、配置、tokenizer、chat template 与 SGLang 服务套件。Flint 是面向编码 Agent 的 MoE 模型，总参数 39.8B、每 token 激活约 2.5B，支持文本输入输出、推理和多轮工具调用，官方公布的 Terminal-Bench 2.1 得分为 54.9%。

来源：[Hugging Face Trending Models](https://huggingface.co/RecursiveSI/flint)　`模型` `开源` `Agent`

### OpenAI 更新 Model Spec，并公开前沿模型失配检测方法

OpenAI 发布新版 Model Spec，用五个核心价值引导能力更强的模型做出更可靠的判断、保持人类自主权并忠实于用户意图。同日 OpenAI 还说明了检测前沿模型失配与 Agent 未经授权行为的方法：通过分层监控发现风险，以便在事态升级前介入。

来源：[An updated Model Spec for more capable and beneficial AI](https://openai.com/index/updated-model-spec) · [How we detect frontier model misalignment](https://openai.com/index/how-we-detect-frontier-model-misalignment)　`安全` `Agent` `行业`

### Falcon 用更少参数实现流式音视频目标说话人提取

清华大学机器学习团队提出因果式音视频目标说话人提取方法 Falcon，用单次 encoder-decoder 过程完成多尺度时频分离，并以编码器空间的说话人对比损失抑制近场泄漏。作者同时发布 RealSSA 基准，包含模拟与真实录音场景；相比因果 AV-TFGridNet，Falcon 参数量减少 91.9%，计算量降低 20.2 倍，GPU 推理延迟降低 11.1 倍。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.32749)　`论文` `多模态` `语音`

## 🧠 模型

### 百度发布 Unlimited-OCR-2，主打无限长文档解析

百度发布 Unlimited-OCR-2，称其通过 SR-SWA 注意力把超长序列的文本-视觉交互压缩为固定大小的参考集合，从而在有限上下文窗口内实现无界文档解析。模型同时发布 ultra-long 文档解析基准 MarathonDocBench，支持 Transformers 与 SGLang 部署。

来源：[Hugging Face Trending Models](https://huggingface.co/baidu/Unlimited-OCR-2)　`模型` `多模态` `工具`

### IBM 发布 Granite Switch 4.1.1 补丁版

IBM 的 Granite Switch 4.1.1 是与 4.1 完全向后兼容的补丁版本，无需迁移即可获得增量改进。本次更新包含多语言语音识别模型（覆盖 10 种语言、带标点和大小写）和改进后的 Decision 适配器，基础模型未重新训练。

来源：[Hugging Face Blog](https://huggingface.co/blog/ibm-granite/granite-switch-4-1-1)　`模型` `语音`

## 📄 论文

### TAO：面向 Agent 服务的工具感知联合调度

论文提出工具感知的联合调度框架 TAO，把工具就绪时间、带时间衰减的节点级缓存信用和 token 占用纳入统一的会话价值评估，再用动态规划联合完成会话选择与放置。在 12 组模型-负载-并发设置中，相比各项指标上最优的已有基线，TAO 最多降低 26.8% 延迟、降低 36.3% 平均首 token 时间，并提升 29.5% 解码吞吐。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.37230)　`论文` `推理` `Agent`

### Sensorimotor Alignment 用离线指标预测机器人策略表现

Rice University 团队提出 Sensorimotor Alignment（S²），一个免训练的离线指标，用于衡量模型的感知表征与物理运动几何结构的对齐程度。研究发现 S² 与下游机器人任务成功率正相关，可作为闭环评测前的低成本筛选手段，还能在昂贵的 VLA 微调之前挑出有潜力的视觉语言模型骨干。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.31670)　`论文` `多模态` `工具`

### PersonaCUABench 揭示 Agent 难以满足真实用户约束

PersonaCUABench 固定 74 个任务和 11 个领域，只改变提出请求的人，由扮演 44 种人设的 persona agent 改写指令并回答提问。在 9 个骨干模型共 3,330 次运行中，平均任务完成率相对原始请求下降 36%；即使完全完成，人设请求获得最高满意度评分的比例也只有 62.7%，原始请求为 84.1%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.22990)　`论文` `Agent` `工具`

### RealCLI：统一评估 CLI Agent 的任务执行与协作质量

REALCLI 是一套成对评测基准，同时衡量 CLI Agent 的任务执行与运行时人机协作质量，包含五维框架、22 个子维度和 51 个交互场景模板，并提供 REALCLI-EXEC 与 REALCLI-COLLAB 两种模式。评测显示前沿 Agent 差距明显：最佳配置平均分仅 49.2%，联合协作分最高只到 37.6%，在可控性、可信度校准和安全边界管理上普遍吃力。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.22507)　`论文` `Agent` `工具`

## 🛠 开源与工具

### Claude Code v2.1.314 新增工作目录写入拦截与空闲压缩

Claude Code v2.1.314 新增 permissions.blockWritesOutsideWorkingDirectories，Write、Edit 和 NotebookEdit 在所有权限模式下都会拒绝工作目录之外的路径。版本还为 VS Code 和 Claude Desktop 的 Code tab 加入空闲压缩：200K+ token 的会话闲置后会被总结，并在 prompt 缓存过期时用于下一条消息，同时修复了多个 Bedrock、Foundry 与 TLS 相关问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.314)　`工具` `Agent` `安全`

### OpenAI Codex 0.166.0 增加 transcript 选择与网络诊断

openai/codex 0.166.0 为 transcript 加入基于键盘的按词、按行、按页选择、集成搜索和可配置快捷键，并统一异步问答与 transcript 回复中的 Markdown 渲染。新版本还提供 codex doctor --network-only 用于配置、连通性和 WebSocket 诊断，并加入 codex queue --resume 以恢复排队后卸载的线程。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.166.0)　`工具` `代码`

### OpenMausBot：把 Claude、Codex 变成聊天里的本地 Agent

OpenMausBot 是一个 Apache-2.0 许可的开源项目，把 Claude 或 Codex 等 CLI 以聊天应用的形式组织成多个 Agent，每个 Bot 可拥有独立人格、模型、云端或本地虚拟机以及连接的应用。它在本地运行 Agent 进程，transcript、密钥和事件存放在 ~/.openmausbot，危险操作会弹出 Allow / Deny 审批卡片。

来源：[GitHub Trending](https://github.com/milind-soni/OpenMausBot)　`开源` `Agent` `工具`

### claude-mem 为各类 Agent 提供跨会话记忆

claude-mem 自动捕获 Agent 会话中的工具使用记录，生成语义摘要并在后续会话中注入，让项目上下文在会话结束后依然延续。它以插件形式支持 Claude Code、OpenClaw、Codex、Gemini、OpenCode 等多种 IDE 与 harness，并提供分层记忆检索、token 成本可见的渐进式披露以及用 <private> 标签排除敏感内容的机制。

来源：[GitHub Trending](https://github.com/thedotmack/claude-mem)　`开源` `Agent` `工具`

## ⚡ 快讯

- **transformers 补丁版修复 vLLM 远程代码加载** huggingface/transformers 发布补丁版，修复了在初始化期间赋值 rope_scaling 的配置问题，并修复了破坏 vLLM 远程代码加载的问题。 [GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.21.1)
- **langchain-core 1.7.3 发布** langchain-core 1.7.3 是 1.7.2 之后的更新版本，对应上游 PR #41564。 [GitHub Releases](https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D1.7.3)
