# 2026-11-14 · AI 晨报

## 今日要点

- llama.cpp 发布 v1.0.0，进入语义化版本管理，移除已弃用的公开 API；Perplexity 发布决策模型 pplx-decider-v1.3，新增 Locate 逐字片段抽取能力。
- DeepSeek 把 App 内的搜索、文件、链接、安全检查和语音能力开放为 API，V4.1-Flash 已在 Messages、Responses 和 Chat Completions 接口上支持。
- Anthropic 系统梳理了常驻 Agent 的五个核心构件；Cursor 公布安全事件调查结论，攻击者借第三方厂商泄露的访问密钥获取部分 Agent 轨迹与凭据，并发布了恶意的 Claude Code 扩展副本。

## 🔥 头条

### llama.cpp 发布 v1.0.0，移除已弃用公开 API

llama.cpp 官方博客宣布发布 v1.0.0，并同步更新 ggml 到 v1.0.0；从此公开 C API 的破坏性变更会随主版本号升级可见。项目同时承诺持续支持模型架构，当前 llama.cpp 支持超过 150 种架构变体和所有主流投机解码方法。
对依赖 llama.cpp 做本地推理的开发者来说，这是接口稳定性的一次重要信号，升级前需要按其语义化版本规则检查下游依赖。

来源：[Hugging Face Blog](https://huggingface.co/blog/ggml-org/llama-cpp-v1) · [GitHub Releases](https://github.com/ggml-org/llama.cpp/releases/tag/v1.0.0)　`开源` `工具`

### DeepSeek 开放 App 全套能力为 API

DeepSeek 宣布把 DeepSeek App 背后的搜索、文件、链接、安全检查和语音能力通过 API 提供。V4.1-Flash（deepseek-flash）已在 Messages、Responses 和 Chat Completions 接口上支持 Web Search、Deep Thinking Search、文件输入、URL 阅读与安全检查，Search、Fetch、OCR、ASR 和 TTS 也可作为独立 API 调用。
开发者可以在自己的应用里直接复用这些能力，不必自行重建搜索、文档解析和语音链路，但扩展能力会额外产生工具调用费用。

来源：[DeepSeek News](https://api-docs.deepseek.com/news/news261113)　`产品` `工具`

### Perplexity 发布决策模型 pplx-decider-v1.3

Perplexity 发布多模态分类模型 pplx-decider-v1.3，基于 Qwen3.8-27B，支持文本与图像输入，可返回选项概率分布，并新增 Locate 能力来抽取带字符偏移和置信度分数的原文片段。模型卡标注 apache-2.0 许可，运行需要 Python 3.12+ 以及能容纳约 49 GiB BF16 权重的 CUDA GPU。
它把分类、结构化打分和片段抽取统一在一个接口里，适合做 NER、PII 检测和抽取式问答，但本地部署门槛不低。

来源：[Hugging Face](https://huggingface.co/perplexity-ai/pplx-decider-v1.3)　`模型` `开源`

## 🧠 模型

### Anthropic 解析常驻 Agent 的五个核心构件

Anthropic 发布指南说明 always-on agents 如何长期运行：这类 Agent 有状态且主动，跨会话管理上下文，其运行由 event inbox、timers、memory、permissions 和 outbox 五个核心构件支撑。指南强调 inbox 应作为事件的事实来源且同时只保留一个活跃 worker，memory 建议只保存无法再查到的信息。
文章还提到，在一项长程编程基准上 Opus 5.5 每个已解任务成本比 Opus 5 低 78%，这对评估常驻 Agent 的推理开销有参考价值。

来源：[Claude Blog](https://claude.com/resources/articles/building-always-on-agents)　`Agent`

### Transformers v5.23.0 新增模型支持与统一导出接口

Hugging Face 发布 Transformers v5.23.0，新增 Inkling 2 Small、LFM3、Dots 3 Note Preview、IQuest-Coder-V1 和 InternLM3 等模型支持。其中 Inkling 2 Small 来自 Thinking Machines Lab，接受文本和图像输入，其语言骨干为 48 层 mixture-of-experts decoder，for 594B total and 17B active parameters。
本版本还统一了导出接口：export() 现在返回 ExportedModel，同一套 API 覆盖 Dynamo、ONNX Runtime、OpenVINO 和 ExecuTorch，可将模型推到 Hub 并在后端运行时加载。

来源：[GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.23.0)　`工具` `模型`

### Cohere 收购 AISLE 与代码评审平台 cubic

Cohere 宣布完成对 AISLE 的收购，并引入 AI 代码评审平台 cubic 的团队，两项交易均围绕其 sovereign AI 平台展开。AISLE 专注漏洞发现与修复的自主系统，其联合创始人将分别担任 Cohere Cyber 高级副总裁、CISO 和 AI 安全副总裁。
cubic 团队将组建 Cohere 的 secure coding 业务线，方向是在本地部署和隔离网络等企业环境中做代码评审、缺陷与漏洞发现。

来源：[Cohere](https://cohere.com/blog/cohere-expands-its-sovereign-ai-platform-with-aisle-and-cubic)　`行业` `安全`

## 📄 论文

### SO-Arena 评测 System One 模型的可靠性

SO-Arena 基准覆盖 11 个领域和五个能力族，评估 System One 模型的能力谱与决策可靠性，除准确率外还用选项集变化下的决策稳定性和无有效选项时的缺失答案识别来衡量可靠性。跨 21 个模型的评测显示，扩展与额外推理的收益在不同领域差异很大，综合表现最好的 System One 模型在可靠性上仅排第七。
对做快速决策模型的团队来说，这提示不能只看聚合准确率来选型。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15777)　`论文` `评测`

### Duo v1 全双工世界模型支持实时视听交互

inclusionAI 提出 Reciprocal World Model（RWM）并发布 Duo v1，一个持续感知视听输入、实时响应的全双工世界模型。RWM 把能力分为提供交互认知的 Intent 和生成连贯视听行为的 Realization 两部分，Duo v1 用自回归建模做连续交互推理与参与决策，并让两个模块在统一时间轴上同步 token。
两者会持续接收实时音频、视频和文本，支持 spontaneous conversations and interruptions；论文同时公布了开源仓库与 Duo-1.0 相关模型权重。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15131)　`论文` `多模态`

### PhysLoop 用 LLM 引导视频生成自我改进

PhysLoop 是一个统一的 harness，用大语言模型的物理知识在视频生成、筛选和纠错三个环节引导并约束模型，把物理一致性蒸馏进生成视频。框架支持可控训练数据构建与推理阶段的视频修复。
团队发布了 100K 视频、生成工具以及两个评测集 PhysLoop-Gen 和 PhysLoop-Repair，并在外部 Physics-IQ Verified 基准上评估物理行为；代码发布尚待公司政策审核。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.16748)　`论文` `视频`

### G-STAR 提出空间-分组协同缩放的图像生成框架

G-STAR 提出空间-分组协同缩放框架，让离散自回归图像生成在保持重建、理解与生成性能的前提下实现深度压缩，并引入半自回归解码器结合并行特征计算与轻量因果建模。论文报告在 1024×1024 分辨率下相对此前的离散自回归模型有明显加速，在单张 NVIDIA H200 上生成每张图像耗时 2.5 秒。
这些结果表明高压缩率的离散表示可以兼顾图像质量与低延迟，对自回归生图方向的工程落地有参考价值。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.13004)　`论文` `图像`

### Actor、Judge 还是 Teacher：决策模型的三种用法

浙江大学团队比较了三个决策模型和三个通用 LLM 作为 actor 与 judge 的表现，并用 JEV 作为 teacher 在 ALFWorld 和 WebShop 上训练策略。当作为 actor 时六个模型都被更简单的子目标吸引而偏离必须先完成的子目标，但看到完整轨迹后它们能正确评价进展。
作为 teacher，JEV 把基于 GRPO 训练的 Qwen2.5-1.5B 策略成功率在 ALFWorld 从 72.8% 提升到 82.9%，在 WebShop 从 56.8% 提升到 71.4%；结论是表现差的 actor 仍可能是好 teacher。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17167)　`论文` `Agent`

### Open Vision Banana 开放生成式视觉感知配方

Open Vision Banana（OVB）提供把预训练生成器转为统一多任务感知系统的完全开放配方，作者分析了颜色编码、prompt 设计、参数适配和任务平衡等关键设计选择，并指出这些选择之间存在相互作用。从 4B 和 9B 开源权重基座出发、使用 2.1M-3.8M 公开数据训练对，OVB 在 Cityscapes 零样本上达到 73.9 mIoU，超过 Vision Banana 报告的 69.9 mIoU。
论文还提出 legend ensembling 测试时扩展方法，在无需重训的情况下把 Cityscapes 和 COCO-Object 的 mIoU 分别最多提升 8.7 和 15.0 个点。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15844)　`论文` `多模态`

### SimpleHC 简化 Hyper-Connections 架构

dots studio 系统研究了 Hyper-Connections（HC）架构的组件，指出学习式读写门控不混合、以及固定门控下的无约束混合构成两组有效交互方式，单独使用即可达到与 mHC 可比的性能。据此提出 SimpleHC，去掉残差混合并用共享内存访问简化执行。
SimpleHC 在最大测试规模上相比 vanilla residual 基线只增加 2.4% 端到端训练时间，并在从 15B 到 30B MoE 模型的扩展中保持与 mHC 可比的性能。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.05984)　`论文` `训练`

### Meta 拆解多模态模型的视觉编码设计

Meta 的研究把视觉编码器捆绑的三个设计选择拆开：上游预训练带来的视觉先验、专属视觉容量以及视觉容量在融合前的放置位置，并在相同数据与同等训练算力下从零预训练做对照实验。结论是视觉先验并非必要，与语言模型联合从零训练的编码器可与预训练编码器相当。
真正重要的是专属视觉容量：去掉编码器的模型在视觉理解上仍落后；而把视觉模块以融合内方式加入骨干早期层，性能可与融合前编码器相当并能降低首 token 延迟。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17334)　`论文` `多模态`

## 🛠 开源与工具

### Tontaube V1.1 开源 TTS 支持声音克隆

Craitech 发布 TontaubeV1.1 多语言文本转语音模型，面向表达性声音克隆、长篇语音和低延迟流式生成，一等支持英语和德语，并支持西班牙语、法语、意大利语、荷兰语和葡萄牙语。官方仓库提供推理服务器，默认运行 4-bit 模型在小型 NVIDIA GPU 或 CPU 上，全精度模型则由 vLLM 后端服务。
默认后端加载约 4 GiB GPU 内存、长文本峰值约 6.5 GiB，声音克隆需要 5–60 秒干净单人语音参考；Linux 是受支持的参考环境。

来源：[GitHub](https://github.com/craitech/tontaube.git)　`语音` `开源`

## ⚡ 快讯

- **TTB 把跨视角注意力烘焙成 MLP 加速新视角渲染** NVIDIA 提出 Test-Time Baking（TTB），在测试时把跨视角注意力中的全局场景信息烘焙进轻量 MLP，实现无需 3D 表示的新视角解码；论文报告最高 23x 渲染加速，质量与多个基准上的最先进方法相当。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.17331)
- **ChatGPT Wallet 让 Agent 在用户批准下完成购买** OpenAI 推出 ChatGPT Wallet，为 ChatGPT Work、Codex 和 dots 中的 Agent 提供在用户批准下完成购买的方式，并沿用现有银行卡保护机制。 [OpenAI News](https://openai.com/index/introducing-chatgpt-wallet)
- **WorldDraft 评测视频模型作为 4D 生成式渲染器** WorldDraft 基准含 432 个严格配对的测试用例，覆盖 48 个可执行 4D 世界族和六类动态挑战；跨 12 个代表性模型的评测显示，世界保持与视觉实现之间存在明显张力，冲突线索下源泄漏最高达 64%。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.16217)
