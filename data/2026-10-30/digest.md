# 2026-10-30 · AI 科技日报

## 今日要点

- Mistral 以修改版 MIT 许可开放 Mistral Large 4（Le Chonk）权重：约 1T 总参数、52B 激活，transformers v5.22.0 已支持。
- Recursive 以 Apache 2.0 开源编码 Agent 模型 Flint，ServiceNow 以 MIT 许可开源语音 + 工具调用模型 Apriel Voice 27B Preview。
- PersonaCUABench 和 RealCLI 两个新基准都显示：换成真实用户的说法和协作方式后，Agent 的表现明显下滑。

## 🔥 头条

### Mistral 开放旗舰模型 Mistral Large 4（Le Chonk）权重

Mistral Large 4 是约 1T 总参数、52B 激活参数的原生多模态 MoE 模型，支持 1M 上下文和三档推理强度；权重以 Mistral Ecosystem Open-Weight license（修改版 MIT）发布，只有提供 Model-as-a-Service 的企业需要另购商业许可。官方称它在 Terminal-Bench 4.0 上比预览版提升 13 个百分点至 41%，API 价格为每百万 token 输入 $0.70、输出 $2.10。transformers v5.22.0 已加入支持，也可以用 vLLM 或 SGLang 自行部署。

来源：[Mistral AI News](https://mistral.ai/news/mistral-large-4-oss/) · [GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.22.0) · [Hugging Face Trending Models](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B) · [HN 讨论](https://news.ycombinator.com/item?id=50289418)　`模型` `开源` `代码`

### Recursive 开源编码 Agent 模型 Flint

Flint 是 Recursive 面向编码 Agent 的 MoE 模型，39.8B 总参数、约 2.5B 激活，文档给出的上下文为 262,144 tokens，以 Apache 2.0 许可发布，仓库附带 BF16 权重和 SGLang 部署套件。官方自测 Terminal-Bench 2.1 为 54.9%、SWE-bench Verified 为 74.2%。激活参数小、许可宽松，适合想自托管编码 Agent 的团队拿来评估。

来源：[Hugging Face Trending Models](https://huggingface.co/RecursiveSI/flint)　`模型` `开源` `代码`

### ServiceNow 开源语音理解与工具调用模型 Apriel Voice 27B Preview

Apriel Voice 27B Preview 用 Whisper large-v3-turbo 语音编码器接上 Gemma 4 26B-A4B 主干，能做转写、语音翻译、语音问答和结构化工具调用，同时保留文本和图像输入，以 MIT 许可发布。它只输出文本和工具调用，不是原生全双工语音模型，做语音助手时需要外接语音合成。

来源：[Hugging Face](https://huggingface.co/ServiceNow-AI/Apriel-Voice-27B-preview) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xipftk/servicenowaiaprielvoice27bpreview_hugging_face/)　`模型` `开源` `语音`

## 🧠 模型

### IBM 发布 Granite Switch 4.1.1：只换适配器，不动基座

Granite Switch 4.1.1 是 4.1 的补丁版，完全向后兼容：这次只新训练了覆盖 10 种语言的 Granite Speech ASR 模型和 granitelib-core 里的 Decision adapter，基座模型没有重算，用户组合最新的适配器即可部署。IBM 还在做 Adapter SDK，让第三方也能像发布软件一样迭代自己的适配器，这种“基座 + 可替换适配器”的更新方式值得做模型运维的团队关注。

来源：[Hugging Face Blog](https://huggingface.co/blog/ibm-granite/granite-switch-4-1-1)　`模型` `语音` `工具`

## 📄 论文

### PersonaCUABench：换成真实用户的说法，电脑操作 Agent 完成率大跌

PersonaCUABench 固定 74 个任务、11 个领域，只改变“谁在提问”：由扮演 44 种 persona 的 Agent 用自己的话重述需求并回答追问。在九个 backbone 的 3,330 次运行里，任务完成率相对原始指令平均下降 36%。对做电脑操作 Agent 的团队来说，只看固定指令下的完成率会高估真实可用性。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.22990)　`论文` `Agent`

### RealCLI：评测 CLI Agent 与人协作的能力

RealCLI 把同一批 CLI 任务分成两种模式：一次给全需求，或由脚本化用户逐步补充信息、纠错、改约束和做授权决定，并用 5 个维度、22 个子维度评估协作质量。最好的配置平均得分只有 49.2%，联合协作分最高 37.6%，模型在可引导性、信任校准和安全边界上最弱。做编码 Agent 的团队可以用它衡量“中途被打断、被改需求”时的表现。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.22507)　`论文` `Agent` `代码`

### Falcon：面向端侧的流式音视频目标说话人提取

论文发布了更贴近真实场景的 RealSSA 基准（含 1–5 个动态近场干扰说话人的模拟场景和真实录制评测集），并提出因果模型 Falcon。相比因果 AV-TFGridNet，Falcon 参数减少 91.9%、计算量降低 20.2 倍、GPU 推理延迟降低 11.1 倍，代码和 demo 已公开，适合做低延迟语音前端的开发者参考。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.32749)　`论文` `语音` `多模态`

## 🛠 开源与工具

### Claude Code v2.1.314 新增禁止写出工作目录的权限开关

新版加入 permissions.blockWritesOutsideWorkingDirectories：开启后 Write、Edit 和 NotebookEdit 在任何权限模式下都拒绝写工作目录以外的路径；VS Code 和 Claude Desktop 的 Code 标签页加入空闲压缩，闲置的 200K+ token 对话会被自动摘要。另外修复了 claude -p 启动失败时以退出码 0 静默结束的问题，现在会打印错误并返回 1，对脚本化调用更友好。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.314)　`工具` `代码` `Agent`

### Codex 0.166.0 加入 GPT-6.1 Terra 与网络诊断命令

OpenAI Codex 0.166.0 把 GPT-6.1 Terra 加入内置、Vertex AI 和 Amazon Bedrock 的模型目录，新增 codex doctor --network-only 用于排查配置、连通性和 WebSocket 问题，以及 codex queue --resume。TUI 支持用键盘按词、行、页选择对话记录并内置搜索，恢复或分叉线程时也会保留已确认的审批和权限设置。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.166.0)　`工具` `代码` `Agent`

## ⚡ 快讯

- **OpenAI 更新 Model Spec** OpenAI 发布新版 Model Spec，用 5 项核心价值引导更强的模型做出合理判断、尊重人的能动性并忠实于人的意图。 [OpenAI News](https://openai.com/index/updated-model-spec)
- **OpenAI 介绍如何检测前沿模型失准** OpenAI 介绍了用分层监控检测前沿模型失准和未经授权的 Agent 行为，以便在事件升级前让响应人员介入。 [OpenAI News](https://openai.com/index/how-we-detect-frontier-model-misalignment)
