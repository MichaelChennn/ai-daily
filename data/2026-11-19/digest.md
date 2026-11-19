# 2026-11-19 · AI 晨报

## 今日要点

- Google 发布 Gemini 4 Neon，在 Artificial Analysis Coding Agent Index 上以 58.6 排第 1，输入定价每百万 token $3。
- Anthropic 首次公开募股定价每股 $83.00，股票预计今天在 Nasdaq Global Select Market 以代码 ANT 开始交易。
- OpenAI 披露：在需要人类两到四小时的研究任务上，编码 Agent 的估计成功率已从 23% 升到 46%。

## 🔥 头条

### Google 发布 Gemini 4 Neon，主打快速完成编码与 Agent 任务

Google DeepMind 发布 Gemini 4 Neon，在 Artificial Analysis Intelligence Index 上以 61 分排第 3，在 Artificial Analysis Coding Agent Index 上以 58.6 排第 1，Terminal-Bench 4.1 得分 65.2%。定价为每百万输入 token $3、每百万输出 token $15，上下文窗口为 1 million token，今天起在 Google AI Studio 的 Gemini API 和 Gemini app 等渠道推出。对开发者来说，这是又一个能直接通过 API 接入、面向长时间 Agent 工作流和编码的前沿模型选项。

来源：[blog.google](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/) · [Google DeepMind Blog](https://deepmind.google/blog/introducing-gemini-4-neon/) · [HN 讨论](https://news.ycombinator.com/item?id=50552424) · [micjm.com](https://micjm.com/blog/gemini-4-neon-looks-like-a-top-model/)　`模型` `Agent` `代码`

### Anthropic IPO 定价每股 $83.00，今天起在 Nasdaq 交易

Anthropic 公布首次公开募股定价：A 类普通股每股 $83.00，共发行 980,000,000 股，股票预计今天在 Nasdaq Global Select Market 以代码 “ANT” 开始交易。Claude 的开发方由此成为上市公司，是今年 AI 行业格局中的一件大事。

来源：[Anthropic News](https://www.anthropic.com/news/anthropic-prices-initial-public-offering) · [HN 讨论](https://news.ycombinator.com/item?id=50553843)　`行业`

### OpenAI 用自家模型改进芯片设计，AMD 已采用部分改动

OpenAI 介绍其模型在芯片设计上的成果：在自研推理芯片 Jalapeño 上，模型提出的改动让向量单元的标准单元面积减少约 13%、矩阵单元减少 10%，并已在硅片上验证；与 AMD 合作时，在旗舰 GPU IP 上相对高度优化的基线取得最高 14% 的提升，部分改动已进入 AMD 送去制造的设计。在两个开源 RISC-V 核心的测试中，GPT‑6.2 Astra 平均得分最高。这说明前沿模型已经能在 RTL 层面做专家级的硬件优化，并借助 Synopsys 等 EDA 工具验证结果。

来源：[OpenAI News](https://openai.com/index/advancing-chip-design-with-our-models) · [HN 讨论](https://news.ycombinator.com/item?id=50549493)　`硬件` `行业`

### OpenAI：编码 Agent 已能独立完成近半数两到四小时的研究任务

OpenAI 更新了内部研究加速的度量：从三月到十月，在需要人类两到四小时的任务上，Agent 的估计成功率从 23% 升到 46%，四到八小时的任务从 13% 升到 35%；但不同工作差距很大，监控训练任务的自主成功率为 79%，编写推理与服务代码只有 25%。OpenAI 认为提升是“参差不齐”的，人类仍是研究循环的核心。对开发者来说，这是编码 Agent 在真实研发中能做什么、还做不好什么的一手参照。

来源：[OpenAI News](https://openai.com/index/research-acceleration-jagged-frontier)　`Agent` `代码` `行业`

### Anthropic：Claude Fable 5.2 解决黑洞物理中的两个未解问题

Anthropic 介绍 Claude Fable 5.2 解决了理论物理中两个与黑洞和量子引力有关的问题：一是完成了物理学家 20 多年前列出、却从未算完的一项计算，证明相关相变是突变的；二是为一种排除错误理论的方法的最简版本求出精确上限，并证明它无法再降低。第一项计算由 Claude 运行的一个由自身副本组成的小型研究小组完成，几乎每一步都独立推导并对照已知结果检查。这是模型在长链条科学计算中推进前沿研究的一个具体案例。

来源：[Anthropic Research](https://www.anthropic.com/research/claude-black-hole-physics)　`推理` `Agent`

## 🧠 模型

### Google 向 AI Ultra 订阅用户开放世界模型 Genie 4

Google 在新版 Project Genie 中向符合条件的 Google AI Ultra 订阅用户推出 Genie 4：探索过程中可以输入新提示实时修改世界，例如换天气、加角色，并首次配上随场景变化的实时原生音频；Genie 3 的单次生成时长也从 60 秒延长到 3 分钟。这是 Genie 4 首次对外开放使用，Google AI Pro 用户目前只能加入候补名单。

来源：[Google DeepMind Blog](https://deepmind.google/blog/genie-4-is-now-available/)　`模型` `视频` `产品`

### RadixArk 发布 DaisyRose-27B：基于 Qwen3.8-27B 做 Agent 强化学习

RadixArk 发布首个模型 DaisyRose-27B，在 Qwen3.8-27B 上用开源 RL 框架 Miles 做长程 Agent 任务训练，只用 1,200 个精选任务、在 144 H200 GPUs 上训练 18 天，把 Terminal-Bench 4.1 pass@1 从 5.6% 提到 12.0%。权重以 Apache 2.0 发布，保留了原模型的架构、tokenizer、chat template 和 256K 上下文。对想用少量高质量任务做 Agent 后训练的团队，这是一个有完整配方可参考的开放权重案例。

来源：[Hugging Face Blog](https://huggingface.co/blog/RadixArk/daisyrose-27b-pushing-the-frontier-of-post-trainin) · [Hugging Face Trending Models](https://huggingface.co/RadixArk/DaisyRose-27B)　`模型` `开源` `训练`

### Reson8 开源 0.5B 语音识别模型 Rumble-2-Flash，支持 40+ 种语言

Reson8 以 Apache 2.0 许可开源 Rumble-2-Flash，这是一个 0.5B 参数、支持 40+ 种语言的语音识别模型，在 Open ASR Leaderboard 多语言榜上平均错误率 6.96%，在 302 小时的呼叫中心基准上 WER 为 7.86%，与 NVIDIA 的 Nemotron 3.5 Transcribe (30B) 的 7.78% 相当。模型沿用 Qwen3-ASR 架构，可直接在 Transformers 和 vLLM 上运行，不需要 trust_remote_code，适合对成本和速度敏感的多语种转写场景。

来源：[Hugging Face Blog](https://huggingface.co/blog/rumble-2-flash) · [Hugging Face Trending Models](https://huggingface.co/Reson8/Rumble-2-Flash)　`模型` `开源` `语音`

## 📄 论文

### TeleChat 系列新作 Xing 4：在 Ascend 910C 上训练 Agent 模型

Xing 4 技术报告介绍了这一延续 TeleChat 系列的大模型如何针对 Ascend 做架构和训练基础设施设计：基于 MindSpore HyperParallel 的预训练栈支撑在 8,192 张 Ascend 910C 卡上预训练 285B 参数模型，后训练则引入统一的 Agent 执行平台 TeleGym，用异步执行和部分 rollout 处理时长不一的任务。对在国产芯片上做大模型训练的团队，这是一份少见的从架构到系统的工程参考。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.22115)　`论文` `训练` `硬件`

### FastFrames 把自回归视频生成做到交互级延迟

论文发现 VAE 解码、KV cache 更新这些常被当作固定开销的环节占了端到端推理延迟的一半以上，换成轻量替代方案后，1.3B 版本在单张 B200 上每帧 36 ms（28 RPS），画质与慢近 8x 的 SOTA 模型相当；14B 版本在 8x B200 节点上每帧 45 ms。它让相机条件、物理条件的视频生成可以实时交互，对做交互式世界模型和游戏的开发者有直接参考价值。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.23226)　`论文` `视频` `推理`

### Multi-Branch Transformer：用并行分支扩展模型，KV cache 最多省 34%

论文提出 Multi-Branch Transformer（MBT），在共享的首尾层之间并行执行多个独立参数的 Transformer 分支，并用 Joint-KV 让同一深度的分支共用一份 KV cache。在 0.8B 到 2.1B 的 MoE 规模上，拟合的 scaling 曲线显示标准 Transformer 需要多达 1.26x 的训练计算才能达到相同验证损失，KV cache 最多减少 34%，单张 H200 上解码吞吐最高提升 51.4%。这为加宽、加深之外的模型扩展提供了第三条路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.19800)　`论文` `训练` `推理`

### Energy-Based Reasoners：1.8M 参数在 Sudoku-Extreme 上达 99.9%

论文提出 Energy-Based Reasoners（EBR），让循环推理模型学习潜在推理状态上的能量函数，把每轮循环更新变成对能量的梯度下降：能量值给候选打分，梯度指导改进，并作为何时停止的信号。只有 1.8M 参数的 EBR 在 Sudoku-Extreme 上达到 99.9% 准确率，推理计算比次优模型少 345×。这为不依赖外部验证器、按难度自适应停止的推理模型提供了一种思路。

来源：[arXiv: Energy-Based Reasoners](https://arxiv.org/abs/2611.08977) · [energy-based-reasoners.github.io](https://energy-based-reasoners.github.io/) · [HN 讨论](https://news.ycombinator.com/item?id=50543989)　`论文` `推理`

## 🛠 开源与工具

### OpenAI 详解 Codex 沙箱：用系统原生机制限制本机命令

OpenAI 介绍 Codex 如何在用户现有环境中安全地运行命令：不用虚拟机或容器，而是调用各平台自带的沙箱机制（macOS 上是 Seatbelt），通过权限配置限制文件系统和网络访问；默认的 :workspace 配置允许在工作区内写入、保持 .git 和 .codex 只读，并禁用网络。文中还演示了用 codex sandbox 命令测试权限配置、给 MCP server 加沙箱。自己做 Agent 的开发者可以直接借鉴这套本地沙箱的取舍和实现。

来源：[OpenAI News](https://openai.com/index/inside-the-codex-sandbox)　`工具` `安全` `Agent`

### 在 32 GB 的 Mac 上用 Transformers 跑 180B MoE 模型

Tarek Ziadé 在 Hugging Face 博客介绍了 Transformers 的 MoE 专家流式加载：只从 SSD 读取路由选中的专家，配合有界缓存，在 32 GB 内存的 MacBook M5 上跑通了 Qwen3.8-Flash-Next，解码约 14 tok/s，与专用引擎 Strata 只差约 6%。通用实现已提交为 huggingface/transformers#50717。对想在本地跑超出内存的大 MoE 模型的开发者，这是一个不离开 Transformers 生态的方案。

来源：[Hugging Face Blog](https://huggingface.co/blog/moe-expert-streaming)　`工具` `推理` `开源`

### Dharma-AI：用 CatBoost 预测微调耗时，比 FLOP 估算准得多

Dharma-AI 用生产集群上 272 个 NVIDIA H200 的 SFT 任务（约 7,382 GPU-hours）做对比：常用的 FLOP 估算只有 R² = 0.31、平均绝对误差 12.41 h，只用派发前信息的 CatBoost 回归器则达到 R² = 0.98，平均误差 1.71 h、中位误差 0.51 h。差距来自评估频率、checkpoint 策略、单卡负载这些纯计算公式算不进去的因素。管理共享 GPU 集群的团队可以借鉴这个做法改进排程。

来源：[Hugging Face Blog](https://huggingface.co/blog/Dharma-AI/predicting-fine-tuning-time)　`工具` `训练`

## ⚡ 快讯

- **langchain-openai 1.8.2 支持 GPT-6.2 Astra 和 Sol** langchain-openai==1.8.2 加入对 GPT-6.2 Astra 和 Sol 的支持，随后的 1.8.3 为 GPT-6.2 启用了 Codex prompt caching。 [langchain-ai/langchain langchain-openai==1.8.2](https://github.com/langchain-ai/langchain/releases/tag/langchain-openai%3D%3D1.8.2) · [langchain-ai/langchain langchain-openai==1.8.3](https://github.com/langchain-ai/langchain/releases/tag/langchain-openai%3D%3D1.8.3)
