# 2026-11-13 · AI 晨报

## 今日要点

- Google 发布 Gemini 4 Hydrogen，定位为日常编码与 agentic 工作流的高效模型，并配套推出 Orchestrator 动态模型切换。
- Anthropic 推出自托管版 Claude Managed Agents，agent 的 harness、沙箱、凭据与会话历史都可运行在企业自有环境，当前为 private beta。
- Apple 研究团队给出 KL 正则化对齐的信息论上限，指出 best-of-N 逼近理论极限，而 PPO 与 GRPO 仍明显次优。

## 🔥 头条

### Google 发布 Gemini 4 Hydrogen 与 Orchestrator

Google DeepMind 推出 Gemini 4 Hydrogen，主打日常编码与 agentic 工作流中的速度与效率，并把它开放给 Google AI Studio、Gemini API 等所有层级。配套的 Orchestrator 会在同一会话中动态切换 Carbon 与 Hydrogen：官方称在 Terminal-Bench 4.0 上，Orchestrator 的任务成功率接近 Carbon，而平均少消耗 24% 配额、快 19%。

来源：[Google DeepMind Blog](https://deepmind.google/blog/introducing-gemini-4-hydrogen/) · [Google AI Blog](https://blog.google/products-and-platforms/products/search/gemini-4-hydrogen-search-upgrade/) · [antigravity.google](https://antigravity.google/blog/gemini-4-hydrogen-in-google-antigravity/) · [blog.google](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/)　`模型` `Agent`

### Anthropic 开放自托管 Claude Managed Agents 私有测试

Anthropic 发布 self-hosted Claude Managed Agents，可把 agent harness、沙箱、凭据处理和会话历史整体部署在自己的云或本地环境，目前处于 private beta。开发者仍用同一套核心 API 构建 agent，模型请求可发往 Anthropic、Amazon Bedrock、Google 的 Agent Platform、Microsoft Foundry 或自有网关。

来源：[Claude Blog](https://claude.com/resources/articles/self-hosted-claude-managed-agents)　`Agent` `产品` `安全`

### Apple 研究给出 KL 约束下模型对齐的理论上限

Apple 机器学习研究团队推导了 KL 正则化对齐可达到的最大期望奖励增益，给出由 Jeffreys divergence 项主导的最优表达式，并说明 PPO 与 GRPO 在两个任务上仍明显次优。论文还给出只用基座模型样本即可预测可达对齐收益的估计器，同时证明 reward ensembling 能缓解 reward hacking。

来源：[Apple Machine Learning Research](https://machinelearning.apple.com/research/theoretical-limits-alignment)　`论文` `训练` `推理`

### IBM 发布 LLMON 标记语言与 Granite 预览模型

IBM 团队提出 LLMON（LLM Object Notation），用保留的特殊 token 标签显式表达上下文结构，把指令与数据分开绑定，并据此发布 granite-4.1-3b-LLMON-preview 与 granite-4.1-8b-LLMON-preview 两个实验性预览模型。作者称在 OPI 基准上它比最强前沿模型多避开 47% 的攻击、比最强开源模型多避开 95%，同时通用能力与 Granite 4.1 Instruct 持平。

来源：[Hugging Face Blog](https://huggingface.co/blog/ibm-granite/llmon-an-llm-native-markup-language-now-in-granite)　`开源` `安全` `工具`

## 🧠 模型

### Edge0 开源 Edge0-145B 与 Edge0-120B 本地模型

Edge0 宣布开源 Edge0-145B 与 Edge0-120B，并同步发布统一推理框架和部署工具，官方称 Edge0-145B 是首个 145B 参数的开放源码端侧模型。它采用共享大矩阵的稀疏专家结构，总参数 145B 中每步仅约 10B 参与计算，官方报告在兼容笔记本上峰值内存 29GB、解码速度 80+ tokens/s。

来源：[edge0.ai](https://edge0.ai/blog/introducing-edge0-145b-frontier-ai-capabilities-on-your-own-computer) · [Hugging Face](https://huggingface.co/Edge0/Edge0-145B-q3k)　`模型` `开源` `推理`

### Runway 发布 Praxis-1 视频与动作生成模型

Runway 的 Praxis-1 是一个 27B 参数的 mixture-of-experts diffusion transformer，同时预测视频与动作，官方称其在 NVIDIA 的 RoboLab-120 榜单上领先所有开放权重 VLA。权重、推理与微调代码以 Apache 2.0 发布，并提供 LeRobot 支持、vLLM-Omni 支持以及面向 H100、B200、RTX 5090 等硬件的运行方案。

来源：[Hugging Face](https://huggingface.co/collections/runwayml/praxis-1)　`模型` `开源` `视频`

### Tether 开源 BotPsy-0.8B 端侧 Agent 模型

Tether AI Research 发布 BotPsy-0.8B，一个基于 Qwen3.5-0.8B 的 0.8B 参数工具调用与 agentic 模型，面向端侧部署。官方称其 BFCL v4 从基座的 23.4 提升到 44.0、ACEBench 从 30.1 提升到 58.7、τ-bench 从 23.2 提升到 51.5，并提供 BF16 safetensors 权重与面向 llama.cpp 的 GGUF 版本。

来源：[Hugging Face](https://huggingface.co/qvac/BotPsy-0.8B)　`模型` `开源` `Agent`

## 📄 论文

### TOME-Math：从结构化教材构建数学证明监督语料

TOME-Math 把 2,118 本大学数学教材转换为约 380K 条结构化证明监督记录，保留章节顺序、命题与证明的关联、依赖引用和来源信息。用它做微调时，模型在留出评测与公开基准上的非加权平均分相对基座提升 16.7 个百分点，整体超过评测的三个公开指令数据基线。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.40394)　`论文` `训练` `推理`

### BookNavigator：用强化学习激励模型自学教材

研究者提出 BookNavigator 接口，让模型自主检索、学习并即时应用长文本教材中的知识，并用带细粒度奖励的强化学习激励这一过程。实验显示 Intern-S2-Preview-35B 的整体证明准确率从 51.5% 提升到 79.5%，并在 BrowseComp-Plus 与 CL-bench 上相对基座分别提升 1.7 和 2.3 个百分点。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.39671)　`论文` `训练` `Agent`

### SteerDistill：闭环教师引导量化 LLM Agent

SteerDistill 是一种量化感知的蒸馏方法：全精度教师引导学生修订失败响应，并依据学生执行反馈迭代修正指导，再让学生在无引导条件下模仿修正后的行为。在五个 agentic 基准和三个模型上，其 W4A16 平均分超过最强量化基线 1.67--2.18 分，与 BF16 差距在 1 分以内。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.13410)　`论文` `推理` `Agent`

### Evolving Infra：面向 Agent 工作负载的自适应推理服务

Evolving Infra 是一个 agent 自适应的 LLM 服务框架，把计算分配与 KV cache 管理解耦，允许节点在 prefill 与 decode 间高效切换，并在线按工作负载构成调整 PD 划分。作者称在编码、数学和 computer-use 任务上，使用 GLM-5.2 与 Kimi K2.6、最多 256 张 GB300 GPU 时，端到端平均延迟与 P95 TTFT 相比 NVIDIA 的 Dynamo 最高改善 4.1x 与 14x。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12304)　`论文` `硬件` `推理`

### SparseRead：给 Agent 加一层稀疏阅读控制

SparseRead 是一个可复用的阅读控制层，无需修改 Agent 模型即可决定放行哪些外部内容，包含 Read Intent Protocol、Adaptive Reader Backends 和带完整视图回退的 Budgeted Read Gate。作者报告在六个模型、五个场景下 token 最多减少 92.9%、耗时最多减少 89.0%，并在 97% 的设置中保持或提升任务质量；Web 深度搜索任务上 token 减少 31.0--43.0%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2608.22237)　`论文` `Agent` `工具`

### PISA-E：按提示自适应选择模型集成

PISA 是按提示自适应、兼顾成本的单模型路由器，PISA-E 把路由扩展到模型集成，联合决定集成组成与规模，成本—质量偏好可在推理时调整而无需重训。在四个 LLM 路由基准上，PISA-E 在优先质量的设定下宏观平均任务性能超过最强竞争者，ID 与 OOD 条件下分别领先 2.09 和 2.87 个百分点。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.10193)　`论文` `推理` `工具`

### Interactive Visual Gym：用模拟用户评测视觉交互模型

Interactive Visual Gym 通过联合仿真可执行任务环境与人类用户，为视觉交互模型提供闭环评测与训练框架，并给出包含 315 个交互场景的 IVG-Bench，覆盖烹饪、家务操作和移动界面。评测显示最好的模型 Gemini 4 Argon 也只在时限内完成 53.4% 的任务，作者用人工研究验证交互质量指标与参与者偏好的一致性为 78.5%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08286)　`论文` `多模态` `Agent`

## 🛠 开源与工具

### Claude Code v2.1.323 新增实验性 Code Mode

anthropics/claude-code 发布 v2.1.323，新增实验性的 opt-in Code Mode，Claude 会写 JavaScript 来调用自己的工具；同时 plugin.json 支持 engines["claude-code"] 声明版本范围，超范围的插件不会被安装或加载。该版本还为长时间运行的 hooks 增加每 30 秒一次的进度心跳，避免宿主误判为卡死，并修复了会话、权限与后台进程等多处问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.323)　`工具` `代码`

### OpenAI Codex 0.168.0 支持模型供应商浏览与并行对话

openai/codex 发布 rust-v0.168.0，终端界面可以在 Sessions → Model providers 下浏览模型供应商并为新会话选择默认项。打开 features.tui_workspace 后可在主对话旁并排查看侧边对话，还支持为支持音频的模型附加录音、生成动画 GIF，以及把 app-server 文档扩展到自定义网关和 Bedrock、GCP 设置。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.168.0)　`工具` `代码`

### Hugging Face 详解多向量检索的 token pooling 训练

Hugging Face 博客介绍了多向量嵌入模型（如 ColBERT）的 token pooling 机制与 pooling-aware 训练：合并相似 token 向量以压缩文档表示，同时让编码器学会在压缩后仍保留检索所需信息。作者报告 pool_factor=4 时，常规训练模型保留 94.6% 的未 pooling NanoBEIR nDCG@10，pooling-aware 训练提升到 97.8%，存储预算相同。

来源：[Hugging Face Blog](https://huggingface.co/blog/token-pooling)　`工具` `推理`

### 3D 模型 LoRA 微调指南：面向 TRELLIS.2

Hugging Face 博客给出 TRELLIS.2 的 LoRA 微调指南，提供可在本地或 Hugging Face Jobs 上运行的容器与脚本。指南建议只对控制结构与几何的 sparse-structure flow DiT 和 shape flow DiT 加 LoRA，冻结 texture flow DiT，并用 GSO 中 188 双鞋做实验；两个目标 DiT 合计训练约 9.3 million 适配器参数。

来源：[Hugging Face Blog](https://huggingface.co/blog/3d-lora-finetuning)　`工具` `图像` `训练`
