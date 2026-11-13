# 2026-11-13 · AI 晨报

## 今日要点

- Google 发布面向编码和 Agent 工作流的 Gemini 4 Hydrogen，全上下文窗口统一按每百万 token $1.50（输入）/ $7.50（输出）计价。
- Anthropic 推出自托管 Claude Managed Agents 私测；一份取证报告称 DeepSeek、Moonshot AI 等实验室的最新模型权重带有 NVIDIA Blackwell 指纹。
- 开放权重方面，Inkling 2 Small、Edge0-145B 和 Runway 的 Praxis-1 都已可以下载。

## 🔥 头条

### Google 发布 Gemini 4 Hydrogen，主打编码与 Agent

Gemini 4 Hydrogen 是 Google 面向快速执行 Agent 工作流的新模型，今天起在 Gemini API、Google AI Studio、Gemini app 和 Google Search 等处全球上线，全上下文窗口统一按每百万 token $1.50（输入）/ $7.50（输出）计价，并新增 xhigh 推理档。Google 称它在默认 high 档下完成任务比 Gemini 3.8 Flash 快 2.5 倍，Terminal-Bench 4.1 得分 57%（对比 18.2%）；Antigravity 同时上线 Orchestrator，可以在同一任务中先由 Carbon 做只读规划、再交给 Hydrogen 改代码和跑测试。还在用 Gemini 3.8 Flash 的开发者可以直接对比迁移后的速度和成本。

来源：[Google DeepMind Blog](https://deepmind.google/blog/introducing-gemini-4-hydrogen/) · [blog.google](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/) · [Google AI Blog](https://blog.google/products-and-platforms/products/search/gemini-4-hydrogen-search-upgrade/) · [antigravity.google](https://antigravity.google/blog/gemini-4-hydrogen-in-google-antigravity/) · [HN 讨论](https://news.ycombinator.com/item?id=50471431)　`模型` `代码` `Agent`

### Anthropic 推出自托管 Claude Managed Agents 私测

自托管版 Claude Managed Agents 进入 private beta：harness、沙箱、凭据和会话历史都运行在企业自己的云或本地环境中，模型请求可以直连 Anthropic，也可以走 Amazon Bedrock、Google's Agent Platform、Microsoft Foundry 或自有网关，开发者沿用托管版的同一套核心 API。需要让 Agent 直接操作内部代码和系统、又不能把数据交给托管服务的团队，可以通过 Anthropic 客户团队申请试用。

来源：[Claude Blog](https://claude.com/resources/articles/self-hosted-claude-managed-agents)　`Agent` `安全` `产品`

### 研究称多家中国实验室新模型权重带有 Blackwell 指纹

Unemployment Labs 的 Will DePue 发布取证报告：通过还原 PyTorch 初始化权重时的随机数种子和 GPU 线程布局，认为 DeepSeek、Moonshot AI、MiniMax 和 Ant Group 最新发布的六个模型与 NVIDIA Blackwell 硬件匹配，而这些公司更早的模型匹配上一代 Hopper。报告也说明，指纹只能说明初始权重由什么硬件生成，不能确定芯片在哪里、如何获得，也不能确定是否违反出口管制。这说明公开的权重本身就可能泄露训练硬件信息。

来源：[unemploymentlabs.com](https://unemploymentlabs.com/checkpoint-forensics) · [HN 讨论](https://news.ycombinator.com/item?id=50474883)　`硬件` `行业` `安全`

## 🧠 模型

### Edge0 开源可在笔记本上运行的 Edge0-145B

Edge0 开源了 Edge0-145B 和 Edge0-120B 以及配套推理框架：145B 总参数中每步约 10B 参与计算，每组 64 个专家共享两个大矩阵，热门专家留在显存，专家库放在系统内存，词表数据放在 SSD 上按需读取。官方报告峰值内存 29GB、解码速度超过 80 tokens/s，可在 48GB 笔记本上本地运行，六项基准均值 72.8。数字来自团队自测，想在个人电脑上跑大模型的开发者可以自己验证。

来源：[edge0.ai](https://edge0.ai/blog/introducing-edge0-145b-frontier-ai-capabilities-on-your-own-computer) · [Hugging Face](https://huggingface.co/Edge0/Edge0-145B-q3k) · [HN 讨论](https://news.ycombinator.com/item?id=50475713)　`模型` `开源` `推理`

### Thinking Machines 开放 Inkling 2 Small 权重

Inkling 2 Small 的权重已在 Hugging Face 以 apache-2.0 许可开放，它是 594B 总参数、17B 激活的多模态模型，接受文本和图像输入，上下文最长 1M tokens。模型以 NVFP4 原生训练，主推的 NVFP4 checkpoint 需要至少 500GB 聚合显存，另有 MXFP8 版本。想自托管或微调大型开放 MoE 的团队现在可以直接下载。

来源：[Hugging Face Trending Models](https://huggingface.co/thinkingmachines/Inkling-2-Small) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xuqplg/thinkingmachinesinkling2small_is_released/)　`模型` `开源` `多模态`

### Runway 发布机器人视频-动作策略模型 Praxis-1

Praxis-1 是 Runway 的机器人策略模型，每次调用同时预测下一段视频和下一段动作，Hugging Face 上有 27B 的 base、单臂 DROID 和双臂 YAM 等版本，还提供 LeRobot 格式和 NVFP4 版本。代码采用 Apache License 2.0，bf16 推理需要一块至少 80 GB 显存的 GPU，仓库也给出了用 LoRA 在单块 80 GB GPU 上适配任务的说明。做具身智能的团队可以直接拿来在自己的机械臂上微调。

来源：[Hugging Face](https://huggingface.co/collections/runwayml/praxis-1) · [runwayml/praxis-1-oss](https://github.com/runwayml/praxis-1-oss) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xu8u4f/praxis1_a_runwayml_collection/)　`模型` `开源` `视频`

### Meta 发布 MetaEncoder，一个编码器做检索与决策

MetaEncoder 由 meta-models/Muse-Glimmer-30B 对比微调而来：用自然语言描述任务和一组候选（可附图像、视频），模型按任务给候选打分。任务和候选分开编码，匹配是表示之间的内积，因此候选表示可以缓存，用 ANN 索引服务海量候选而不必重跑模型；权重采用 Apache 2.0 许可。适合需要快速做检索、排序和封闭式选择的场景。

来源：[Hugging Face](https://huggingface.co/collections/facebook/metaencoder) · [facebook/meta-encoder](https://huggingface.co/facebook/meta-encoder) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xu8eie/metaencoder_a_facebook_collection_one_encoder_for/)　`模型` `多模态` `开源`

## 📄 论文

### Evolving Infra：按 Agent 负载自适应的 LLM 推理服务

Evolving Infra 把算力分配和 KV cache 管理解耦，节点可以在 prefill 和 decode 之间高效切换；在线规划器按负载构成调整 PD 比例，分布式 KV 管理器借助 Agent 上下文管理的信号决定缓存淘汰和传输。在最多 256 张 GB300 上用 GLM-5.2 和 Kimi K2.6 跑编码、数学和 computer-use 任务，平均端到端延迟和 P95 TTFT 比 Dynamo 最多降低 4.1x 和 14x。自建 Agent 推理集群的团队可以参考它的调度思路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12304)　`论文` `推理` `Agent`

### SparseRead：让 Agent 只读需要的那部分内容

SparseRead 是一个不改动 Agent 模型的读取控制层：跟踪不断变化的阅读意图和来源覆盖，选择定位证据的后端，并给每个 episode 的累计原文读取量设上限，必要时回退到完整视图。在包括 Claude Opus 5 在内的六个模型上，总 token 最多减少 92.9%、耗时最多减少 89.0%，97% 的设置下任务质量持平或提升。经常读网页、文档和代码仓库的 Agent 可以借鉴，代码已公开。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2608.22237)　`论文` `Agent`

### SteerDistill：用闭环教师引导量化 LLM Agent

作者发现低比特量化后的 Agent 常忽略任务要求或环境条件；SteerDistill 让全精度教师引导学生修正失败的回答，并根据学生的执行反馈迭代改进引导，再把这些修正蒸馏进不需要引导就能运行的学生模型。在五个 Agent 基准和三个模型上，W4A16 下比最强量化基线平均高 1.67–2.18 分，与 BF16 相差不到一分。想用低比特部署 Agent 降成本的团队可以参考，代码已在 GitHub 公开。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.13410)　`论文` `推理` `Agent`

## 🛠 开源与工具

### Claude Code v2.1.323 加入实验性 Code Mode

新版加入实验性的 Code Mode：开启后 Claude 编写 JavaScript 来调用自己的工具，组织也可以统一关闭。插件可以在 plugin.json 里用 engines["claude-code"] 声明支持的版本范围，范围外的插件不会被安装、更新或加载；claude plugin validate 还会对插件的 TypeScript hooks 模块做类型检查。维护插件的开发者升级后可以给插件加上版本约束。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.323)　`工具` `代码` `Agent`

### Codex 0.168.0 支持切换模型提供方和并排侧边对话

新版可以在 Sessions → Model providers 里浏览模型提供方，并设定新会话默认使用哪一个；开启 TUI workspace 功能后，可以在主对话旁并排查看侧边对话。它还支持在使用音频模型时附加录音，以及生成或编辑动画 GIF。在多个模型提供方之间切换的团队可以升级试试。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.168.0)　`工具` `代码`

### KittenML 开源 inferencekit，让编码 Agent 调优推理

inferencekit 是 Claude Code、Codex 和 OpenCode 的插件：告诉 Agent 模型、硬件和目标，它会查找、基准测试并调优兼容的推理引擎，还可以进一步做包括 GPU kernel 在内的自定义优化，不达标的改动会被回退，最后输出一份 REPORT.md。项目采用 Apache-2.0 许可。本地硬件和模型作者不同的开发者，可以让 Agent 为自己的机器找出最快的配置。

来源：[KittenML/inferencekit](https://github.com/KittenML/inferencekit) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xut6z0/inferencekit_opensource_plugin_to_optimize_any/)　`工具` `推理` `开源`

### llama.cpp 合并 Intel 专用 Vulkan FA prefill kernel

llama.cpp 合并了针对 Intel 平台的 Vulkan Flash Attention prefill shader，目前在 ARL-H 和 XE2/XE3 上启用，A770 因测试结果不一致仍保持关闭。作者在 B70 Pro（Windows）上测得 qwen3 8B 的 pp8192 prefill 从 1064.67 提升到 2955.83 t/s。用 Intel 核显或 Arc 显卡跑本地模型的开发者更新到 master 就能用上。

来源：[vulkan : Intel FA kernel for prefill · llama.cpp #29357](https://github.com/ggml-org/llama.cpp/pull/29357) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xumdj4/intel_arc_vulkan_prefill_got_a_dedicated_fa/)　`工具` `推理` `硬件`

## ⚡ 快讯

- **Jensen Huang 辞去 Nvidia CEO，Colette Kress 任临时 CEO** Jensen Huang 辞去 Nvidia CEO 职务，Colette Kress 被任命为临时 CEO。 [NVIDIA Form 8-K](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000082/nvidiaannouncesceotransiti.htm) · [bloomberg.com](https://www.bloomberg.com/news/live-blog/2026-11-11/nvidia-turmoil-board-to-weigh-ceo-jensen-huang-future-over-alleged-affairs)
- **Claude Meetings beta 上线，Claude 可加入视频会议** Claude 现在可以作为可见参会者加入视频会议、回答问题并记录笔记和待办，目前支持 Google Meet，正在 Team 和 Enterprise 计划中以 beta 推出。 [Claude Blog](https://claude.com/resources/articles/claude-meetings)
- **UMAP 0.6 发布，换用新的初始化和优化器** UMAP 0.6 带来新的初始化和优化器流程，作者称在 3 million 篇 arXiv 论文上不到 5 分钟即可跑完，可用 pip install -U umap-learn 升级。 [lmcinnes/umap releases](https://github.com/lmcinnes/umap/releases) · [Reddit 讨论](https://www.reddit.com/gallery/1xudaah)
