# 2026-11-05 · AI 科技日报

## 今日要点

- Moonshot AI 发布开源权重的 Kimi K3.1 Pro，原生多模态、1-million-token 上下文，定位为最强 3T 级模型。
- 字节跳动 Axion 1.0 用「两段轻量 SFT + 强化学习」三阶段流程训练 Agent 基础模型，并公开完整训练配方。
- Ricursive 推出 Ripple-65B Preview，65B 稠密模型主打 Agent 编码，可在消费级硬件上运行。

## 🔥 头条

### Moonshot AI 开源 Kimi K3.1 Pro 多模态模型

Moonshot AI 发布 Kimi K3.1 Pro，称其为迄今最强的 3T 级模型：原生多模态、1-million-token 上下文，并从 Kimi K3 出发做了大规模联合强化学习。模型权重已在 Hugging Face 开放，支持 Transformers、vLLM、SGLang 等部署方式。

来源：[Hugging Face Trending Models](https://huggingface.co/moonshotai/Kimi-K3.1-Pro)　`模型` `多模态` `推理`

### 字节 Axion 1.0 用三阶段配方训练开源 Agent 模型

Axion 1.0 是一个 fully open 的 Agent 基础模型，训练仅需两段轻量 SFT 加一段强化学习，不使用中途训练、DPO 或 OPD，并公开了数据构造、验证、提示词与训练代码。论文称约 18K 条 SFT 样本，Axion 1.0-35B 复现检查点在 Apache 2.0 协议下开放。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03233) · [Hugging Face](https://huggingface.co/Axion1-0/Axion-1.0-35B)　`模型` `Agent` `训练` `开源`

### Ricursive 发布 Ripple-65B Preview 稠密模型

Ricursive Intelligence 推出 Ripple-65B Preview：65B 稠密 Transformer，12T token 预训练，支持 1M 上下文，模型卡称其在 TerminalBench 2.1 得分 80.52。官方同时放出 BF16 指令版、BF16 基座版和 NVFP4 检查点，65B 规模可装进 NVIDIA DGX Spark 等消费级硬件。

来源：[Hugging Face Trending Models](https://huggingface.co/ricursiveAI/Ripple-65B-Preview) · [ricursive.com](https://www.ricursive.com/ripple)　`模型` `开源` `代码`

### 腾讯发布 Hy4，权重开放仍未落地

腾讯 Hy 团队发布 Hy4 正式版，当天即可通过腾讯云和 OpenRouter 的 API 使用，新增视觉与计算机操作能力，并支持编辑 Word、Excel 和 PowerPoint 文件。官方称计划开放模型权重但未给日期，也承认与顶级闭源模型仍有很大差距，目前在 Hugging Face 上只有 Hy4-preview 及其 FP8 版本。

来源：[maccus.fr](https://maccus.fr/en/tencent-hy4-ai-model/) · [hy.tencent.ai](https://hy.tencent.ai/research/hy4?langVersion=en)　`模型` `多模态` `Agent` `产品`

### Ai2 与 Google 合建开源气候模型 NeuralGCM+

Ai2 获得 Google.org 数百万美元、为期三年的资助，并与 Google Research 合作开发开源模型 NeuralGCM+，在物理方程模拟基础上用 AI 表示云、降雨等小尺度过程。新模型将把大气与海洋放在一起模拟，目标是生成跨数十年的稳定投影。

来源：[Ai2](https://allenai.org/blog/google-climate-partnership)　`论文` `多模态` `行业`

## 🧠 模型

### Deep Principle 发布科学模型 Hydrogen-1.0

Deep Principle 基于 GLM-5.3 后训练出 Hydrogen-1.0，面向化学、材料与生命科学的科研辅助，提供 BF16、NVFP4 和 MXFP4 三个权重仓库，模型卡说明已用 SGLang 在 8 张 GPU 上测试。完整训练数据集与配方未随权重公开，作者也提醒输出仍需人工核验。

来源：[deep-principle/Hydrogen-1.0 · Hugging Face](https://huggingface.co/deep-principle/Hydrogen-1.0) · [Hydrogen-1.0: open-weight scientific model beats GPT-6 Astra on FSR with 72% lower estimated output cost [P]](https://huggingface.co/deep-principle/Hydrogen-1.0)　`模型` `开源` `推理`

### AuroraIMG2-100M 开源 256×256 文生图模型

AuroraAI Research 发布 AuroraIMG2-100M：100.6M 参数 flow-matching 扩散 Transformer 配 44.9M 文本编码器，输出 256×256 RGB 图像，工作在 FLUX.2 VAE latent 空间。模型在单张 NVIDIA RTX PRO 6000 上从零训练，Apache-2.0 协议，diffusers 可直接加载。

来源：[Hugging Face](https://huggingface.co/AuroraAI-Research/AuroraIMG2-100M)　`模型` `开源` `图像`

## 📄 论文

### SpecPilot：自动发现投机解码优化

UC Berkeley 团队提出 SpecPilot，用 Agent 循环为不同部署场景自动寻找投机解码的算法与系统优化，并通过 token forcing 逐 token 对照原始系统防止 reward hacking。论文称在四个目标模型、三种 drafter、两种 GPU 平台和五个 benchmark 上，单请求相对自回归解码的加速比从 4.46× 提升到 10.87×。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.02501) · [arXiv](https://arxiv.org/abs/2611.02501)　`论文` `推理` `Agent`

### Route Anything 研究多模态模型与策略路由

Route Anything 提供统一的模型与策略路由框架，先给出质量—成本权衡下的最优路由理论基础，再构建横跨 25 个 benchmark 的全模态轨迹矩阵，含 452 组候选配置的 374,401 次打分运行。论文称逐输入的 oracle 路由比最优固定候选高 5.4 分，学习型路由器平均相对参考模型带来 8.82× 效率提升。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.05275)　`论文` `推理` `Agent`

### ToolSpace 合成多环境长程 Agent 训练数据

ToolSpace 主张从真实 MCP 服务与公开 Agent 语料的执行轨迹中挖掘依赖，用确定性规则而非 LLM 判断聚类出环境，再通过带回滚的状态感知随机游走合成可回放任务。该方法把 AutomationBench 与 tau3-Bench Banking 升级为 Pro 版本，7 个前沿模型在更难任务上最多下降 38.2 分。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.05036)　`论文` `Agent` `训练`

### MoviEdit 实现长视频多镜头一致性编辑

Adobe 提出 MoviEdit，面向长时段多镜头视频编辑，采用级联的双向—自回归结构：先在时空压缩表示上生成全局连贯的编辑草稿，再自回归地在完整视频上传播与细化。团队还构建了 MoviEdit-Bench，并生成 87K 对无需人工标注的编辑视频用于训练。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.02737)　`论文` `视频` `多模态`

### LoCo 用局部偏好学习压缩推理长度

腾讯提出 LoCo，从模型自身轨迹中检测可能过度思考的位置，冻结对应推理前缀、重新生成更短且经验证的续写，再用这些状态条件化的偏好对做 DPO 训练。论文称数学任务完成长度减少 41.7%--45.4%、代码任务减少 23.4%--36.3%，同时保持或提升准确率，代码与模型将公开。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.04814) · [arXiv](https://arxiv.org/abs/2611.04814)　`论文` `推理` `训练`

## 🛠 开源与工具

### llama.cpp v0.9.0 支持 OCP FP8 E4M3 量化

llama.cpp v0.9.0 加入 OCP FP8 E4M3 量化类型与新的 flash_attn_ext_rows 算子，让统一 KV cache 在多序列推理下更高效，并提供通用批量张量拷贝 API。新版本还支持 Clover、Limite、Metis-1.6 和 Mistral Large 4 等架构，以及 Chatterbox TTS、Nemotron 3.5 Transcribe 等多模态能力，ggml 同步升级到 v0.29.0。

来源：[GitHub Releases](https://github.com/ggml-org/llama.cpp/releases/tag/v0.9.0)　`工具` `开源` `推理`

### RustingStrata：纯 Rust 的 Qwen MoE 推理引擎

RustingStrata 是一个纯 Rust 编写的 Qwen GGUF 推理引擎，不用 ggml，CUDA 内核在运行时用 NVRTC 编译，同一套内核也能跑在 Vulkan 上。它支持把放不进显存的 MoE 专家放在 CPU 与 GPU 并行计算，并提供 OpenAI 兼容服务接口；仓库当前版本为 v1.1.0。

来源：[GitHub](https://github.com/RustingStudio/RustingStrata)　`工具` `开源` `推理`

### CWE-bench v2 开放 100 个安全修复任务

Collinear AI 公开 CWE-bench v2 的 100 个任务，覆盖 91 类 CWE：Agent 拿到真实开源仓库检出和一段简短指令，需要找出并修复安全弱点且不破坏原有功能。评分完全程序化且可复现，任务、评分器与 harness 全部开放，每个任务是带 Docker 环境与确定性验证器的 Harbor 任务。

来源：[Hugging Face Blog](https://huggingface.co/blog/cwe-bench)　`工具` `安全` `Agent` `开源`

## ⚡ 快讯

- **OpenAI 发布 Images 2.6 图像生成更新** OpenAI 推出 Images 2.6，带来更快的图像生成、GIF 制作和更精确的编辑，并在 ChatGPT、Codex 与 API 中加入新的控制项。 [OpenAI News](https://openai.com/index/introducing-images-2-6)
- **OpenAI 将收购 Pierre Computer Company** OpenAI 宣布收购 Pierre Computer Company，以扩展 Codex 在代码构建、理解与审查方面的工具能力。 [OpenAI News](https://openai.com/index/openai-to-acquire-pierre)
- **OpenAI 用自动化流水线修补 Linux 内核提权漏洞** OpenAI 称其自建自动化流水线发现、验证并生成了 948 个 Linux 内核本地提权漏洞的补丁。 [OpenAI News](https://openai.com/index/a-thousand-fewer-paths-to-root)
- **Ollama v0.40.14 修正采样默认值与响应解析** Ollama v0.40.14 让 OpenAI 兼容端点不再覆盖模型自带采样默认值，并修复云端搜索响应解码问题。 [GitHub Releases](https://github.com/ollama/ollama/releases/tag/v0.40.14)
- **StateBench 评测长文档状态跟踪能力** Ai2 发布 StateBench，用四个难度层级测试模型在长文档中跟踪状态变化的能力。 [Ai2](https://allenai.org/blog/statebench)
- **Claude Marketplace 新增 25 个以上合作 Agent 与产品** Claude Marketplace 引入安全、开发基础设施与生产力方向的新 Agent 和产品，目前超过 25 个合作项。 [Claude Blog](https://claude.com/resources/articles/new-agents-and-products-claude-marketplace)
