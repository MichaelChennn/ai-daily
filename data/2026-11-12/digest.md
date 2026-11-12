# 2026-11-12 · AI 科技日报

## 今日要点

- Google 推出 Gemini Decisions API：Gemini Decision 1 一次前向为选项打分，单次请求最多 1,000 题、端到端延迟 150-250 ms。
- 决策模型集中出现：LangChain 1.5.0 把 decision models 加进 core，Strands Decider 开源可本地部署的小型决策模型，MMDM 基准显示多选任务最高仅 36.81%。
- 华为开源量化工具 MACaQ，称 64 分钟即可量化 122B 参数模型。

## 🔥 头条

### Google 推出 Gemini Decisions API，专做快速封闭式决策

Gemini Decisions API 由新模型 Gemini Decision 1（gemini-decision-1）驱动，不逐 token 生成文本，而是在一次前向中为候选选项打分，返回概率和置信度；一次请求最多可带 1,000 个是/否、多选或评分题，端到端延迟 150-250 ms，价格为 $0.10 / 1M 输入 token，输出不计费。工具选择、策略检查、模型路由这类 Agent 里的有界判断，可以从通用大模型调用中拆出来，交给更快、更便宜、带置信度的专用接口。

来源：[Google AI Blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/) · [HN 讨论](https://news.ycombinator.com/item?id=50456791)　`模型` `Agent` `产品`

### LangChain 1.5.0 加入决策模型和模型路由中间件

langchain-core 1.8.0 新增 decision models，langchain 1.5.0 加入 model router 和 auto mode 中间件（ModelRouterMiddleware 标为 beta），langchain-typesafe 0.1.0 把 TypeSafeClassifier 实现为决策模型；三个包都移除了已停止维护的 Python 3.10，最低要求 Python 3.11。还在 Python 3.10 上的项目会继续停留在旧版本，升级前要先换解释器；决策模型进入 core 后，在 LangChain 里做路由和分类判断可以直接用上这类模型。

来源：[langchain-ai/langchain langchain==1.5.0](https://github.com/langchain-ai/langchain/releases/tag/langchain%3D%3D1.5.0) · [langchain-ai/langchain langchain-core==1.8.0](https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D1.8.0) · [langchain-ai/langchain langchain-typesafe==0.1.0](https://github.com/langchain-ai/langchain/releases/tag/langchain-typesafe%3D%3D0.1.0)　`工具` `Agent` `开源`

### 华为开源量化工具 MACaQ，覆盖 GGUF、vLLM 和扩散模型

MACaQ 是华为计算系统实验室提出的逐层独立 MXFP4 W4A4 训练后量化方法，代码以 Apache 2.0 发布，可为 llama.cpp 生成 2/3/4-bit GGUF，也支持 vLLM、Diffusers 和 PyTorch；官方称量化一个 122B 参数模型只需 64 分钟、32.5 GB 显存。MACaQ-R 产出的 GGUF 可在标准 llama.cpp 上运行，README 中 Qwen3.6-35B-A3B 的 Q4_K_XL 在相同 22.36 GB 下 KL 散度低于 Unsloth UD-Q4_K_XL，本地跑模型的开发者可以拿它和现有量化对比。

来源：[GitHub](https://github.com/huawei-csl/MACaQ) · [Hugging Face Daily Papers](https://huggingface.co/papers/2611.10649) · [HN 讨论](https://news.ycombinator.com/item?id=50458166) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xto0fa/opensource_method_macaq_beats_unsloth_ggufs/)　`工具` `开源` `推理`

### DeepMind 发布 AlphaGenome 2，按细胞类型预测 DNA 变异影响

AlphaGenome 2 改为条件模型：在 DNA 序列之外输入目标组织、细胞类型或状态，一次预测一个条件，并新增 DNA 甲基化读数，训练数据覆盖 68 种组织。在 TenK10K 数据集上，它识别出的因果变异为 30%，原版 AlphaGenome 等工具为 16%。模型已通过 AlphaGenome API 开放给非商业研究，商业研究处于私测，做计算生物学的团队可以直接调用。

来源：[Google DeepMind Blog](https://deepmind.google/blog/alphagenome-2-deciphering-how-cells-read-dna-to-better-understand-disease/)　`模型` `行业`

## 🧠 模型

### Nex-AGI 发布 Agent 模型 Nex-N2.6，基于 GLM-5.3-Flash

Nex-N2.6 是面向计算机操作、编程和长程工具任务的多模态 Agent 模型，开放约 321B 参数的 FP8 权重。团队内部评测中，相比 Nex-N2.5-Pro，推理重复率从 16.0% 降到 1.6%，OSWorld 从 82.2 升到 83.0。这一版专门针对推理死循环和调用当前环境里不存在的工具，跑长时间 Agent 任务时更值得一试。

来源：[Nex-N2.6 · Hugging Face](https://huggingface.co/nex-agi/Nex-N2.6) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xthiki/nexn26_is_out_the_update_is_mostly_about_getting/)　`模型` `Agent` `开源`

### Zyphra 开源 TTS 模型 ZONOS3-Mini，激活参数约 100M

ZONOS3-Mini 是总参数 800M、每 token 激活约 100M 的 MoE 语音合成模型，支持 43 种语言，可从音频样本克隆音色，并能细到单个词地控制情绪和语速，权重以 Apache 2.0 发布。官方称它能在手机、笔记本甚至浏览器里实时运行，需要本地语音合成的应用多了一个开源选择。

来源：[Hugging Face Trending Models](https://huggingface.co/Zyphra/ZONOS3-Mini) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xtb9gw/zyphrazonos3mini_hugging_face/)　`模型` `语音` `开源`

### KRAFTON 开源韩英双语小模型 Raon-1 nano

Raon-1 nano 有效参数 1.5B（含 1.5B 逐层 embedding 表，共 3.1B），由 Raon-1 mini preview（30B-A4B）剪枝蒸馏而来，采用 18 层线性注意力加 6 层全注意力的混合架构，原生支持 262,144 token 上下文，以 Apache 2.0 发布。它主打韩语、英语对话和工具调用，提供 GGUF、MLX 和 LiteRT-LM 格式，适合在端侧做本地助手。

来源：[Hugging Face](https://huggingface.co/KRAFTON/Raon-1-nano) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xtmbkn/kraftonraon1nano_hugging_face/)　`模型` `开源`

### MBZUAI 开源世界模型 PAN 2，按文字动作生成未来视频

PAN 2 由 MBZUAI 的 IFM 发布，输入可选图片和文字描述的动作，生成最长 20 秒的视频来模拟世界如何变化：大语言模型先写出结构化的下一状态描述，再由从零训练的 29B MMDiT 预测视频潜变量、Wan 2.2 VAE 解码。代码和权重以 Apache 2.0 发布，Agent 可以先用它模拟几个候选计划的结果，再挑最好的执行。

来源：[Hugging Face](https://huggingface.co/IFM/PAN2) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xtb199/ifmpan2_hugging_face/)　`模型` `视频` `开源`

## 📄 论文

### WikiTrace：给 Agent 记忆附上原始轨迹以便核查

论文指出，外部记忆会让 Agent 在本可完成的任务上失败，因为经验只靠成败标签归纳、又不附来源，Agent 无从核对。WikiTrace 把每条经验链接到成败原因摘要和原始轨迹，经验缺细节、互相冲突或来自失败任务时，Agent 用终端工具沿链接回查再行动，在五个 Agent 基准上优于现有记忆方法。给 Agent 做长期记忆时可以借鉴：保留证据链，而不只存提炼后的结论。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.14320) · [arXiv](https://arxiv.org/abs/2611.14320)　`论文` `Agent`

### WICL：机器人在模拟器里排练，把经验写进上下文

论文提出 World In-Context Learning（WICL）：冻结的模型从一次演示出发，在模拟器中排练任务，把反馈写进上下文而不是权重。配套系统 RoboScript 在 RoboTwin 2.0 全部 50 个任务上平均成功率 83.4%，每个任务一次演示、不做梯度更新，比最强的训练式动作策略高出 20 多个点，并迁移到了真实双臂机器人。上下文学习在机器人操作上开始能和训练策略竞争，代码已公开。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12885) · [arXiv](https://arxiv.org/abs/2611.12885)　`论文` `Agent`

### Embodied First Exam：测编程 Agent 控制机器人的基准

这个基准包含 47 个机器人上 35 个套件的 1,156 个任务，编程 Agent 可以自己选择直接控制、写代码控制或训练策略来完成。在 456 个核心任务的标准设置下，八个 Agent 中最强的 GPT-6 Astra in Codex 成功率只有 34%。想把编程 Agent 用到实体机器人上，这个结果说明离可靠还有很长的路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12177) · [arXiv](https://arxiv.org/abs/2611.12177)　`论文` `Agent` `代码`

### MMDM：评测决策模型的大规模多任务基准

MMDM 收录 16 类任务的 5,448 道题，选项数从 2 到 1,024，输入最长 64,817 token，覆盖 Agent 状态跟踪、工具与技能选择、偏好判断和评分等场景。作者评测了 28 个决策模型：Perplexity Decider-V1.2 在世界知识上的困难单选准确率为 78.75%，在选项逻辑上只有 53.95%，所有模型困难多选准确率最高仅 36.81%。决策模型接口正在增多，选型时可以用它检验选项相互依赖、带约束的场景。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.14309) · [arXiv](https://arxiv.org/abs/2611.14309)　`论文` `Agent`

## 🛠 开源与工具

### OpenAI 的 Codex Security CLI 和 SDK 登上 GitHub 趋势榜

Codex Security 用来查找、调查和修复代码中的漏洞，可以在 Codex 里使用，也能通过 @openai/codex-security CLI 和 TypeScript SDK 接入终端与 CI，支持导出 SARIF、JSON 和 CSV，许可证为 Apache-2.0。想在流水线里加一道 AI 安全扫描的团队可以直接试。

来源：[GitHub Trending](https://github.com/openai/codex-security)　`工具` `安全` `代码`

### Strands Labs 开源小型决策模型 Strands Decider

Strands Decider 去掉 Qwen3.5-2B-Base 的语言模型头，换成约一百万参数的 pointer head，只在选项间做选择或按刻度打分，每个决策附带校准过的置信度；2B 模型在 RTX 3090 上单题中位延迟 115 ms，以 Apache 2.0 发布。思路和 Gemini Decisions API 一致，区别是可以本地部署。

来源：[strands-labs/strands-decider](https://github.com/strands-labs/strands-decider) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xthu1w/strands_decider_v_the_jevs/)　`工具` `Agent` `开源`

### llama.cpp 合并 FP8 KV-cache 支持

PR #28392 为 llama.cpp 加入基于 OCP-FP8 的 KV cache，可选支持运行时的静态逐张量缩放，已由 ggerganov 合并进 master。本地跑长上下文时，KV cache 多了一个低精度存储选项。

来源：[GitHub](https://github.com/ggml-org/llama.cpp/pull/28392) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xt9o3t/llamacpp_add_fp8_kvcache/)　`工具` `推理` `开源`

### Unsloth 发布 Dynamic V3.1 量化，更新 Qwen3.8-27B 等 GGUF

Unsloth Dynamic V3.1 用于 Qwen3.8-27B、DeepSeek-V4.1-Flash-1017 和 Qwen3.8-Flash-Next，官方称比同尺寸的其他量化准确率高 10-15%、token 用量少 50%；Qwen3.8-27B 从 2-bit 到 6-bit 的量化都已更新，3-bit 因与 UD3 持平没有动。社区评论认为部分 Q4 量化在 DeepSWE v1.1 上 V3 仍优于 V3.1，换用前最好自己测一遍。

来源：[unsloth.ai](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs) · [i.redd.it](https://i.redd.it/rdisl2kib01i1.png)　`工具` `推理`

## ⚡ 快讯

- **美联航禁止第三方个人 AI Agent 代旅客订票** United 称将限制未经授权的第三方个人 AI Agent 或助手使用其平台，理由包括账户凭证泄露、误购和 MileagePlus 里程被误用。 [cbsnews.com](https://www.cbsnews.com/news/united-airlines-bans-ai-agents-booking-flights/) · [HN 讨论](https://news.ycombinator.com/item?id=50458900)
