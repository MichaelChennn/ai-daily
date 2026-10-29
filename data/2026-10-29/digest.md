# 2026-10-29 · AI 科技日报

## 今日要点

- Google DeepMind 发布前沿模型 Gemini 4 Carbon，主打网络安全和长时程任务，本周先向部分网络安全防御者开放。
- NVIDIA 放出开放权重语音模型 Nemotron 3.5 Transcribe，一个模型覆盖 40 种语言的转写、翻译和说话人标注。
- Cursor 开放内部用来构建 Bugbot 等 Agent 的 Agent SDK，今天起正式可用。

## 🔥 头条

### Google DeepMind 发布 Gemini 4 Carbon，先向网络安全防御者开放

Gemini 4 Carbon 是 Google 继两周前的 Gemini 4 Argon 之后的新前沿模型，在 Artificial Analysis Intelligence Index v5.0 上以 59 分排第一，SEC-bench Pro、ExploitGym、CWE-bench 分别为 88.2%、54.8%、71.0%。本周只向部分网络安全防御者开放，再通过 Fairwind Program 逐步扩大，面向开发者的上线时间未定；介绍期价格与 Argon 相同，为每百万 token 输入 $2、输出 $10。

来源：[Google DeepMind Blog](https://deepmind.google/blog/gemini-4-carbon-our-next-frontier-model/) · [blog.google](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/) · [HN 讨论](https://news.ycombinator.com/item?id=50276792)　`模型` `安全` `产品`

### NVIDIA 发布开放权重语音模型 Nemotron 3.5 Transcribe

Nemotron 3.5 Transcribe 用一个模型完成转写、翻译、说话人标注和音频问答：支持 40 种语言转写，可处理最长一小时、最多八名说话人的录音，30B 参数中每个 token 只激活约 4B；在 Open ASR 英文榜上以 5.33% 平均 WER 位列开放权重模型第一。它面向录音而非实时流，可以用自然语言提示控制输出；同时发布的 Granary v2 数据集覆盖 463,062 小时、48 种语言，可用于做领域适配。

来源：[Hugging Face Blog](https://huggingface.co/blog/nvidia/nemotron-transcribe-granary) · [Hugging Face Trending Models](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B) · [HN 讨论](https://news.ycombinator.com/item?id=50275128)　`语音` `模型` `开源`

### Cursor 开放 Agent SDK：用代码定义和部署 Agent

Cursor 发布 Agent SDK，也就是它自己构建 Bugbot、Security Reviewer、Rollouts 等托管 Agent 的框架，今天起正式可用。Agent 用代码定义，自带 evals 和事件回放，可以一条命令部署到 Cursor 的基础设施，也可以作为单个 Node 进程打包进容器自托管。想把代码评审、发布流程交给 Agent 的团队，可以像普通软件项目一样对 Agent 做版本控制和评审。

来源：[cursor.com](https://cursor.com/blog/agent-sdk) · [HN 讨论](https://news.ycombinator.com/item?id=50273731)　`Agent` `工具` `代码`

## 🧠 模型

### Google 发布统一多模态嵌入模型 EmbeddingGemma 2

EmbeddingGemma 2 是开放的多模态嵌入模型，把文本、图像、音频、视频及其组合映射到同一个向量空间；论文称它在各模态的嵌入基准上胜过专用模型和更大的模型。它支持按需加载模态编码器、调整视觉 token 预算、截断嵌入维度和量化权重，适合在资源受限的环境里做跨模态检索。

来源：[Hugging Face Trending Models](https://huggingface.co/google/embeddinggemma-2) · [Hugging Face Daily Papers](https://huggingface.co/papers/2610.37364) · [arXiv](https://arxiv.org/abs/2610.37364)　`模型` `多模态` `开源`

### DiffuSpace 发布扩散语言模型 Clover-35B-A3B-Preview

Clover-35B-A3B-Preview 由 Qwen3.6-35B-A3B 改造而来，用块扩散方式生成文本，35B 参数的 MoE 每个 token 激活约 3B，上下文 128K，许可证沿用 Apache-2.0。官方推荐用其 SGLang 实现部署和评测，想试扩散语言模型的开发者可以直接拿来跑。

来源：[Hugging Face](https://huggingface.co/Diffuspace/Clover-35B-A3B-Preview) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xhinyj/diffuspaceclover35ba3bpreview_hugging_face/)　`模型` `开源`

## 📄 论文

### Memory Tax：很多 Agent 记忆系统不如朴素 RAG

一项研究在多个基准和模型上评测 Agent 记忆系统，发现很多专门的记忆系统在不少情况下不如直接对原始历史做朴素 RAG。作者把记忆相对直接检索的得失拆成“记忆收益”和“记忆税”，指出整理事实、提炼偏好时可能删掉或掩盖证据。给 Agent 加记忆模块前，值得先拿 RAG 做基线比一比。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.34073) · [arXiv](https://arxiv.org/abs/2610.34073)　`论文` `Agent`

### 腾讯混元开源交互式世界模型 Hy-Nomas

Hy-Nomas 是基于 8B 扩散主干的视频世界模型，支持多轮自由文本指令和连续相机控制，按当前输入和缓存的历史生成变长片段。团队放出了权重、代码、评测基准和轻量适配流程，做交互式视频生成的开发者可以直接复现和微调。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.36729) · [Hugging Face Trending Models](https://huggingface.co/tencent/Hy-Nomas) · [arXiv](https://arxiv.org/abs/2610.36729)　`论文` `视频` `开源`

### MPO：在“轮”的粒度上做长程 Agent 强化学习

作者观察到长程 Agent 训练中 critic 值主要在轮与轮之间变化，于是提出 Multiscale Policy Optimization（MPO），结合多尺度优势估计和轮级重要性采样，把信用分配和策略更新对齐到轮的粒度。在搜索、工具调用和自动化任务上，用 4B 和 30B-A3B 模型都稳定超过强 RL 基线，对训练多轮工具调用 Agent 有参考价值。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.35013) · [arXiv](https://arxiv.org/abs/2610.35013)　`论文` `Agent` `训练`

## 🛠 开源与工具

### PyTorch 2.15.0 正式发布，重写的 NCCL 后端成为默认

PyTorch 2.15.0 默认启用重写的 NCCL 后端，挂起时由 flight recorder 转储，并保留回退路径；torch.distributed 新增单边传输和 NIXL 后端，NVIDIA Blackwell 上的 NVFP4 解码更快。默认 wheel 改为 CUDA 13.2，做分布式训练的团队升级前要留意 NCCL 行为变化。

来源：[GitHub Releases](https://github.com/pytorch/pytorch/releases/tag/v2.15.0)　`工具` `训练` `硬件`

### llama.cpp v0.8.0 支持 LFM3 全系并加入实时语音接口

llama.cpp v0.8.0 加入 LiquidAI LFM3 系列（文本、视觉、音频和全模态），server 新增 /v1/realtime 和 /tts 端点，可以直接做实时语音输入输出；同时 ggml 升级到 v0.28.0，UI 也能直接从 HF Hub 浏览和下载模型。在本地做语音应用的开发者可以直接接入 llama.cpp server。

来源：[GitHub Releases](https://github.com/ggml-org/llama.cpp/releases/tag/v0.8.0)　`工具` `语音` `推理`

## ⚡ 快讯

- **Surge AI 发布税务 Agent 基准 DAYJOB: Tax** 50 个专业税务任务中，排名第一的 Claude Sonnet 5.5 通过率仅 10.8%（pass@1，95% 评分阈值）。 [surgehq.ai](https://surgehq.ai/blog/dayjob-tax) · [HN 讨论](https://news.ycombinator.com/item?id=50275626)
