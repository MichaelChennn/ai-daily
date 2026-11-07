# 2026-11-07 · AI 科技日报

## 今日要点

- Anthropic 提出用「dreaming」整理 Agent 记忆，并用 Pokémon Red、CL-Bench 等任务评估不同模型写入记忆的方式。
- NVIDIA 的 VFlash 用 Flash Primitive Decoding 联合预测视觉图元，3D 轨迹生成速度约 25 倍，配套世界动作模型在 MolmoSpaces 四个任务集上平均成功率 70.2%。
- Cloudflare 开源 security-audit-skill：把安全审计拆成六个阶段，用独立 agent 复核发现并输出机器可读结果。

## 🔥 头条

### Anthropic 探索用「dreaming」整理 Agent 记忆

Anthropic 研究了 Agent 记忆的组成：Agent 把日志整理成笔记、标记重要事件，再在空闲时通过「dreaming」反思日志、修正错误并组织记忆。评测显示，不同模型判断什么值得记住的能力差异明显——在 Pokémon Red 中，Claude Fable 5 只写了九个文件、四个文件夹，却拿到四个徽章，而 Claude Sonnet 3.7 写了 413 个记忆文件、225 个文件夹，只拿到一个徽章。这给做长期记忆的开发者一个直接抓手：记忆质量取决于判断和取舍，而非记得更多。

来源：[Anthropic Research](https://www.anthropic.com/research/components-of-agent-memory)　`Agent` `论文`

### NVIDIA 提出 VFlash 视觉规划解码，3D 轨迹生成约 25 倍加速

NVIDIA 等团队提出 VFlash，用轻量 drafter 一次前向联合预测整个视觉图元（点、框、轨迹），不再逐坐标 token 自回归解码。在评测的 2D 和 3D 机器人轨迹任务上预测误差持续低于自回归解码，初步单次 rollout 测量显示 3D 点运动预测生成约快 25 倍。以 VFlash 规划为条件的世界动作模型在四个 MolmoSpaces 任务集上平均成功率 70.2%，基线为 62.6%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08449)　`论文` `多模态`

### Cloudflare 开源 security-audit-skill 编码 Agent 安全审计技能

Cloudflare 发布 security-audit-skill，把安全审计拆成六个阶段：勘察、按覆盖度分配 hunt、候选验证、结构化输出、记录独立复核和目标中立报告，产出 findings.json、REPORT.md 等文件。设计上强调「发现的 Agent 不能是验证的 Agent」，并把无法确认的线索记为 needs_validation 而不是直接判定漏洞。开发者可用 Skills CLI 安装，在目标代码库中直接触发完整审计。

来源：[GitHub Trending](https://github.com/cloudflare/security-audit-skill)　`开源` `安全` `Agent`

### Harness-S 让 Agent 从兄弟 harness 中学习并迁移能力

上海交通大学等团队提出 Harness-S：不追求通用最优的 harness，而是用「兄弟 harness」补齐基础执行系统的失败。只有当基础 harness 下所有尝试都失败时，才调用兄弟 harness 池重新采样，用这些轨迹替换失败组做强化学习，再把获得的能力迁移回原 harness。论文称在 AppWorld、SWE-Gym 和 DBBench 上训练后的策略回到基础 harness 仍明显优于只做策略训练。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.04277)　`Agent` `论文` `训练`

### Drex 开源决策模型家族，单次前向输出选项概率

Nace.AI 提出 Drex 决策模型家族：给定问题与用户提供的选项，直接返回选项上的概率分布，不做自回归解码，输出无需解析长文本。家族包含 8B（DLM）、9B（v1.5）、35B-A3B（v2.0）和 27B（Max）四个模型，训练结合监督微调与 RLAF，Max 还做了视觉调优。论文报告 Max 在 Decision Index 0.4.1 公开集上取得 67.52，典型请求响应 183 ms，而 GPT-6 Sol 约 2.0 s、Claude Opus 5.5 约 3.5 s；全部权重与推理代码开放。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.07854)　`模型` `开源` `推理`

### SLA 把空间对齐扩展到 VLA 持续预训练

港科大等团队提出 SLA（Spatial-Language-Action Model），在预训练阶段就让策略对齐冻结 3D 感知模型给出的空间表征，并在后训练中保持这种对齐。SLA 从预训练 pi05 策略初始化，联合优化动作预测与中间视觉嵌入的空间对齐，并用 feature-dependent gates 聚合多层视觉特征、概率化 state dropout 抑制对演示轨迹的过拟合。所有辅助组件只用于训练，可直接复用预训练 VLA 权重，推理架构不变。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08373)　`论文` `多模态`

## 🧠 模型

### Open-HumanScale 开源 5 万小时第一人称视频配方

北京大学团队提出 Open-HumanScale，一套完全开放的具身基础模型配方，配套开放标注了手部动作和自然语言的 Open-HumanScale-50K 第一人称视频语料。研究用闭环仿真评估发现预训练数据时长与下游机器人成功率之间存在对数线性 scaling law，并据此训练只用人类视频的 HumanWAM-Vanilla，机器人后训练后在 RoboTwin 2.0 Clean2Clean 达 92.08%、Clean2Random 达 68.88%。人机混合预训练的 HumanWAM-Goal 后训练后达到 92.70% 和 84.60%，语料、检查点与代码一并开放。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.06817)　`模型` `开源` `多模态`

### TailSteer 在训练尾段抑制多轮图像编辑漂移

TailSteer 是一个末段训练框架，针对图像编辑反复复用输出时不断累积的视觉漂移。它的做法是让早期去噪动态贴近基座模型，只在轨迹尾部集中学习保持性修正，这些修正从编辑器自身的 on-policy 去噪 rollout 中学习，用未改动的源内容作为保持参考，不需要精标编辑对。在 FLUX、SenseNova 和 Qwen 系列上的实验显示，它在 15-20 轮编辑中显著降低累积漂移，同时基本保持基座模型原有的生成与编辑能力，且不改动架构和推理流程。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.06741)　`论文` `图像`

### PLatour 跨模型 latent 通信框架与 PACT-Check 检验

伦敦国王学院团队提出 PLatour，一个开源的 prefill-to-autoregressive 跨模型迁移（PACT）框架：用轻量零初始化线性桥连接冻结模型，直接以任务奖励训练，并支持混合注意力架构。作者同时提出 PACT-Check 来量化收益有多少真正来自通信，因为对照实验显示部分任务上的提升可由无信息发送方信号、自我通信或只训练接收方复现，线性桥可能只是参数高效的适配机制。论文称 PLatour 在生成任务上超过所评开源 PACT 基线，并以 35B 发送方在共享数学与代码基准上超过 Mostik 报告的结果（其发送方为 753B）。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.06976)　`论文` `模型` `训练`

### EvoMemState 用关系状态与推理状态管理 Agent 记忆

EvoMemState 针对以独立事实为单位存储记忆的局限，把持久化事实扩展为两种互补状态：记录事实有效性、范围和相互关系的 Relational States，以及决定这些事实如何用于当前请求的 Reasoning State。框架由本体引导的记忆状态归纳、用强化学习内化记忆使用经验的 RL-Based State Evolution，以及结合事实与两类状态做推理的 State-Aware Reasoning 三部分组成。论文称在长期对话与记忆使用基准上，检索完整性和基于记忆的回复准确率都稳定优于既有记忆系统，代码与实现细节已开放。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03743)　`Agent` `论文`

## 📄 论文

### BestRand：把评测子集选择的随机误差长尾压下去

CMU 等团队推导了用子集估计全量基准分数时误差分布的近似解析式，发现多数随机子集误差很小、少数子集误差很大，呈长尾分布，因此随机采样常常够用但不稳定，并指出这种不稳定在现代基础模型上依然存在。据此提出 BestRand，在保留随机采样效率的同时削减高误差尾部：在 70+ 文本、多模态和 Agent 基准上，相比有竞争力的方法将高误差风险降低 50.2%、平均估计误差降低 16.4%，构建成本只需 51.3%，OOD 估计误差平均再降 21.8%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.00883)　`论文` `工具`

### VisSearch-Bench 评测多模态 Agent 的长程视觉搜索

蚂蚁集团等团队提出 VisSearch-Bench，聚焦多模态 Agent 的视觉上下文管理——把图像、物体外观、局部细节和空间关系与外部检索结果串联起来，而不是只用图片识别出首个实体再转纯文本检索。基准含 7 个主领域、25 个子领域的 204 个人工编写任务，覆盖集合式、序贯式、宽深混合、竞争性视觉消歧和视觉结构引导搜索，每题给出参考答案、可追溯证据和评分规则。评测 16 个多模态模型时，即使带上搜索工具，最好的系统也只完整解出 26.47% 的任务。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.04894)　`论文` `多模态` `Agent`

## 🛠 开源与工具

### Apple 用小神经网络加速 MIPS 检索

Apple 介绍 ICML 2026 论文 Amortizing Maximum Inner Product Search with Learned Support Functions：在固定的 key 数据库上离线训练小神经网络，学习如何把查询更快路由到最佳匹配，用一次性的摊销成本换取推理时更快、更准的检索。方法把最大内积搜索看成支撑函数，用 SupportNet 近似支撑函数改善聚类路由，用 KeyNet 直接输出最佳匹配的 key 向量，两者都基于真实查询分布采样训练。对做 RAG 的团队，这意味着在高维、大规模向量库上可以绕开纯几何索引的部分误差，换取检索延迟收益。

来源：[Apple Machine Learning Research](https://machinelearning.apple.com/research/faster-retrieval)　`工具` `论文`

### ToyBlocks 开放机器人学习仿真框架

ToyBlocks 是 FoundationWorlds 的第一个环境：一个开放仿真框架，围绕桌面上的机械臂和积木，支持自动生成任务与训练演示，并给出行为指标，目标是让研究者能改变训练数据、重复测试并追溯失败原因。框架用强化学习和运动规划生成短时程技能，在 Isaac Lab 中训练推、翻等非抓取技能，再由任务-运动规划器串接技能产出带标签的演示数据，单 GPU 并行执行可达 24 倍实时。开发者可用网页界面接入 Claude 等前沿模型用自然语言指挥机器人。

来源：[Hugging Face Blog](https://huggingface.co/blog/allenai/toyblocks) · [Ai2](https://allenai.org/blog/toyblocks)　`开源` `工具` `多模态`

### Hugging Face Transformers 发 v5.22.2 补丁版修安全问题

Hugging Face 发布 Transformers v5.22.2 补丁版本，包含安全与分布式相关修复：其中一项是加固 Jinja 沙箱，另一项是让 device_id 只为 NCCL 设置。升级量不大，但模板沙箱与多卡训练配置都属于容易在生产里踩坑的环节，升级前值得核对现有部署的模板与分布式启动方式。

来源：[GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.22.2)　`开源` `安全` `工具`

## ⚡ 快讯

- **LangGraph CLI 与 SDK 小版本更新** langgraph-cli 0.4.42 新增 deploy metrics 命令并升级 filelock、langgraph-api 依赖以修复安全问题。 [langchain-ai/langgraph langgraph-cli==0.4.42](https://github.com/langchain-ai/langgraph/releases/tag/cli%3D%3D0.4.42) · [langchain-ai/langgraph langgraph-sdk==0.4.14](https://github.com/langchain-ai/langgraph/releases/tag/sdk%3D%3D0.4.14)
- **Open ASR 榜单新增埃及与尼日利亚英语私有数据** Open ASR Leaderboard 与 Liva AI 合作新增埃及英语、尼日利亚英语两个口音的私有数据分区。 [Hugging Face Blog](https://huggingface.co/blog/open-asr-leaderboard-liva)
- **OpenAI 推出湿实验科学 Agent 基准 BioBasicsBench** OpenAI 发布 BioBasicsBench，用 100 个任务衡量 AI Agent 解读原始实验数据、处理日常湿实验科学工作的能力。 [OpenAI News](https://openai.com/index/measuring-how-ai-agents-handle-wet-lab-science)
- **Anthropic 报告 207,000 次科研会话中的 Claude 使用情况** Anthropic 分析 207,000 次科研会话：数据分析约占 Claude 会话的三分之一、Claude Code 会话接近一半。 [Anthropic Research](https://www.anthropic.com/research/how-researchers-use-claude)
