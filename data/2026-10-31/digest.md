# 2026-10-31 · AI 科技日报

## 今日要点

- DeepSeek-V4.1-Flash-1017 权重以 MIT License 发布，主打推理、编码与 Agent 任务，并提供 Transformers、vLLM、SGLang 的调用示例。
- 腾讯发布 Youtu-Parsing-Omni，用一套编码器与一套 Schema 统一解析文档、图像、音频和视频；LiquidAI 的 LFM3-Omni-2B 把视觉、音频与语音输出放进同一个端到端模型。
- 多篇论文聚焦推理与训练的效率：LOWN 通过按需处理图像降低扩散式视觉语言模型的解码开销，Soft-MTP 用一行代码改动去掉多 token 预测梯度中的噪声残差。

## 🔥 头条

### DeepSeek-V4.1-Flash-1017 权重以 MIT License 发布

DeepSeek 发布 DeepSeek-V4.1-Flash-1017，这是 DeepSeek-V4.1-Flash 的小版本更新，官方称在推理、编码、Agent 任务和视觉基准上均有提升，同时降低任务执行时间与输出长度。仓库支持 Transformers、vLLM、SGLang 和 Docker，权重以 MIT License 发布，但本次发布不含 Jinja 格式的 chat template，官方另附了参考实现和 deepseek-recipe。

来源：[Hugging Face Trending Models](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)　`模型` `开源`

### 腾讯发布 Youtu-Parsing-Omni 多模态解析模型

腾讯提出 Youtu-Parsing-Omni，用共享权重的 Youtu-Omni-Encoder 把文档、图像、音频和视频编码到统一的时空坐标系，并用 OmniSchema 统一十类解析任务的输出。单个 5 B 参数检查点在 OmniDocBench v1.6 达到 96.96 Overall，在 OmniParsingBench 以 75.08 Avg. 领先所有开放权重模型；代码与模型权重已公开，并提供 vLLM 插件。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.39301)　`多模态` `模型` `开源`

### LiquidAI 发布端到端全模态模型 LFM3-Omni-2B

LiquidAI 发布 LFM3 家族首个全模态模型 LFM3-Omni-2B，单个模型即可理解文本、图像、视频和音频，并以文本和语音作答，不再需要单独的 ASR、视觉语言模型、LLM 和 TTS 模型。该模型参数量为 2.2B，面向手机、笔记本等端侧硬件设计，支持 16 kHz 音频输入、24 kHz 语音输出，并可输出交错的文本与语音。

来源：[Hugging Face Trending Models](https://huggingface.co/LiquidAI/LFM3-Omni-2B)　`多模态` `语音` `模型`

### Claude Code v2.1.316 新增子代理努力级别与网关预算池

anthropics/claude-code 发布 v2.1.316，新增 CLAUDE_CODE_SUBAGENT_EFFORT 环境变量，可为未指定努力级别的子代理设定运行档位；同时为 Claude apps gateway 加入共享月度预算池和 layered 策略模式。版本还修复了 Claude Code 自行退出后残留 shell 命令、bash 别名丢失、以及 Vertex AI 与 Amazon Bedrock 上新模型不可用时未回退到旧模型等问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.316)　`工具` `Agent`

### OpenAI 支持通过 robots.txt 表达 AI 训练偏好

OpenAI 宣布将遵循一个共享的 robots.txt 信号，帮助网站运营者向参与该机制的提供商表达 AI 训练偏好。对开发者而言，网站爬取与数据使用的边界有了新的通用约定信号。

来源：[OpenAI News](https://openai.com/index/helping-websites-express-ai-training-preferences)　`行业` `安全`

## 🧠 模型

### NVIDIA 用 Nemotron 开源模型搭出语音交互万圣节装置

NVIDIA 工程师用开源 Nemotron 系列模型搭建了 MonsterHouse 互动投影：Nemotron 3 ASB 负责听、Bolt E4B 负责思考、Nemotron Magpie TTS Zeroshot 负责说，Audio2Face-3D 驱动表情动画，整套系统跑在一台工作站上。文中给出 Bolt E4B 与 Nemotron Voice Agent 的组合方式、LoRA 角色训练和端到端延迟数据，可作为语音 Agent 与数字人落地参考。

来源：[Hugging Face Blog](https://huggingface.co/blog/nvidia/nemotron-halloween)　`开源` `语音` `Agent`

## 📄 论文

### LOWN：扩散式视觉语言模型按需处理图像

KAIST AI 提出 LOWN，一种无需训练、无需调阈值的解码方法：先在无图像条件下预测 token，仅当预测与上一次带图像预测不一致时才处理图像。论文报告 LOWN 在十个基准上平均保留 LLaDA-V 99.6% 的分数，同时把解码 FLOPs 降到平均 35.3%，生成时间平均减少 57.4%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.36671)　`论文` `多模态` `推理`

### IDM：在分布匹配蒸馏中加入显式矩约束

inclusionAI 提出 Intrinsic Distribution Matching（IDM），在保留完整 DMD 校正的同时，用生成器的 EMA 副本匹配特征均值与逐坐标标准差，无需外部特征编码器。实验在 Z-Image-Turbo 6B 和 Qwen-Image 20B 上进行，在两次网络评估下于 LongText-Bench 中文与英文分别达到 94.25% 和 90.20%，为该预算下对比方法中的最高分。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.39633)　`论文` `图像` `训练`

### Soft-MTP：一行代码去掉多 token 预测的梯度噪声

论文指出标准多 token 预测（MTP）训练的交叉熵梯度可精确分解为一个 KL 自蒸馏项和一个低信噪比残差，后者会干扰 next-token 与多 token 学习。作者提出 KL 梯度恢复技巧，实现为 Soft-MTP：复用已有的 NTP 与 MTP 交叉熵计算，只回传 KL 自蒸馏信号，不增加参数也无可测开销，并兼容 DeepSeek 与 Meta 风格 MTP。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.38331)　`论文` `训练` `推理`

## 🛠 开源与工具

### LangGraph 发布 1.2.19 与 SDK 0.4.11

langchain-ai/langgraph 发布 langgraph 1.2.19 与 langgraph-sdk 0.4.11，SDK 版本重点改进流式断线重连：失败重连带 backoff 重试、保留 SSE 数据与游标状态、缺少 Last-Event-ID 时告警。langgraph 1.2.19 修复了流式节点输出消息命名空间、RemoteGraph.stream 的子图行为，以及暂停工具被误报为失败等问题。

来源：[langchain-ai/langgraph langgraph-sdk==0.4.11](https://github.com/langchain-ai/langgraph/releases/tag/sdk%3D%3D0.4.11) · [langchain-ai/langgraph langgraph==1.2.19](https://github.com/langchain-ai/langgraph/releases/tag/1.2.19)　`工具` `Agent`

## ⚡ 快讯

- **A-RSI：按学习信号变化刷新多模态自改进任务池** 小米研究提出 A-RSI：监测训练日志中的奖励波动与准确率，在学习信号下降时刷新任务池，任务答案由程序生成并独立校验。加入 800 个新任务后，十一个基准的性能均值从 57.77 提升到 61.05。 [Hugging Face Daily Papers](https://huggingface.co/papers/2610.38568)
- **VibeGame：用对抗式 Agent 团队从提示生成 2D 游戏** VibeGame 用 AI 原生引擎把项目状态表示为 schema 校验的结构化文本，Agent 可自行检查状态、执行动作并验证行为。框架由八个专职 Agent 组成的对抗式团队分离实现与评审，并沉淀可复用的骨架、模块与协作契约。 [Hugging Face Daily Papers](https://huggingface.co/papers/2610.33106)
