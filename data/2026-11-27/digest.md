# 2026-11-27 · AI 晨报

## 今日要点

- Google 的 Workspace MCP 服务器正式可用，并要求 AI agent 改用 MCP 服务器或 Workspace CLI 访问 Workspace，而不是现有 REST API。
- llama.cpp v1.1.0 加入 Inkling 2 系列、Hy4 flash 和一批 TTS 与音频模型。

## 🔥 头条

### Google 要求 AI agent 改用 Workspace MCP 服务器访问数据

Google 宣布 Gmail、Google Drive、Docs、Sheets、Slides、Calendar、Chat 和 Tasks 的 Workspace MCP 服务器正式可用；按新的 Workspace AI Tools Addendum，AI agent 必须使用 Workspace MCP 服务器或 Workspace CLI，而不是现有 REST API，技术上的强制执行从 2027 年 2 月 1 日开始。第三方文章指出，公开的 Gmail MCP 服务器不能发送、回复或转发邮件，这些工具需要合作伙伴权限。直接调用 Gmail、Drive REST API 的 agent 产品需要在期限前评估迁移，并核对缺失的操作和配额。

来源：[Google Cloud Blog](https://cloud.google.com/blog/products/identity-security/deploying-agents-safely-in-your-enterprise) · [Workspace AI Tools Addendum](https://workspace.google.com/terms/ai-tools) · [techstackups.com](https://techstackups.com/articles/google-workspace-ai-agents-mcp/)　`Agent` `工具` `行业`

### llama.cpp v1.1.0：加入 Inkling 2 系列和一批音频模型

llama.cpp v1.1.0 加入 Inkling 2 系列（base、Mini 和 DSpark）、Domyn Edge 4B、Zaya1 8B、RAON-1-mini 和 Hy4 flash，并带来 Kokoro、VoxCPM2、Fish S2 等 TTS 与音频模型。这一版还支持按 bpw 或体积预算自动逐张量量化，llama-server 接受 OpenAI 的 named tool choice，并弃用旧的 llama batch API。本地部署的开发者可以直接用上新模型和量化方式，调用旧 batch API 的代码需要迁移。

来源：[GitHub Releases](https://github.com/ggml-org/llama.cpp/releases/tag/v1.1.0)　`开源` `推理` `工具`

## 🧠 模型

### Kandinsky Lab 发布图像超分模型 Kandinsky ImageSR 2.0

Kandinsky ImageSR 2.0 是一个 5B 参数的图像超分模型，以 Diffusers 管线发布，同一套 transformer 权重同时支持 x2 和 x4 放大。模型卡给出的数据是在 H100 上把 1K 图放大到 4K 约 7.80 s，代码以 MIT License 发布。需要开源超分的图像工作流可以直接通过 Diffusers 接入。

来源：[Hugging Face Trending Models](https://huggingface.co/kandinskylab/Kandinsky-ImageSR-2.0)　`模型` `图像` `开源`

### MiniMax 公布 H3 家族：开源 100 天衍生出 1,472 个模型

MiniMax 介绍 H3 家族的 H3-Highspeed、H3-Lite 等型号，其中 H3-Lite 输出 768P 或 480P，起价 $0.025 每秒。MiniMax 说开源 MiniMax H3 的 100 天里，开发者做出了 1,472 个衍生模型，总下载量超过 148 million 次。做视频生成的开发者可以按画质和成本在几个档位之间选择，也可以基于 H3 自己做衍生模型。

来源：[MiniMax Blog](https://www.minimax.io/blog/minimax-h3-family)　`模型` `视频` `开源`

## 📄 论文

### Mixture-of-Loops Transformer：用 KV 记忆改进循环 Transformer

论文提出 MoLT，用 Mixture-of-Loops Attention 把 KV 作为跨层、跨循环复用的记忆。在 400B token 预训练中，U-MoLT 在 700M/1.5B dense 和 3B MoE 上都超过 OLMo3，700M 上验证交叉熵的 token 效率达到 1.7x，代码已开源。想用循环结构换取参数效率的团队可以参考它的设计。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34923)　`论文` `训练`

### Agentic LongLive：给实时长视频生成加上 agent 记忆

Agentic LongLive 让一个记忆 agent 在单独的 GPU 上只读已给出的提示词，为每个人物、物体和场景维护文本状态和图像，再注入生成器的 attention sink。在 LongStory-Online 上，它把 LongLive-2.0 的持久状态准确率提高 26.3 分、主角身份一致性提高 44.9，生成时间只增加约 1%。做交互式长视频的团队可以借鉴这种异步记忆设计。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34907)　`论文` `视频` `Agent`

### Sage-Med-Preview：35B 参数、3B 激活的医疗多模态模型

论文介绍 Sage-Med-Preview，一个 35B 参数、3B 激活参数的医疗多模态模型，经过医疗预训练、分阶段 SFT 和自适应强化学习训练。它在 31 个公开多模态基准上平均 58.26%，高于 Hulu-Med-235B-A22B 的 50.99%。论文同时给出了医疗 MLLM 扩展规律的系统评测，对做垂直领域多模态模型的团队有参考价值。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34575)　`论文` `多模态` `模型`

### Real2SimLab：统一评测“从真实视频生成仿真”的平台

Real2SimLab 让各方法交付可运行的程序，再用每个基准原有的评分器给生成的仿真打分，免去每对方法和基准单独对接；它还提供避开数据污染的训练数据与奖励标注流水线。目前支持 47 个编码 agent 和 5 个非 agent 方法、6 个基准，平台已开源。研究编码 agent 生成仿真程序的团队可以直接用它做横向比较。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34849)　`论文` `Agent` `代码`

## 🛠 开源与工具

### NVIDIA 开源 Nemotron 3.5 Parse 训练数据和微调配方

NVIDIA 开源了 Parse 3.5 训练用的三个合成数据集：Synthetic Charts V1（9.98M 条）、Synthetic Tables V1（1M 条）和 OCR Synthetic Multilingual v2（7.9M 条），并给出基于 NeMo Automodel SFT 和 NeMo RL GRPO 的微调配方。文章称在单张 H200 上用 BF16，DFlash2 让吞吐在并发 1 时提升 7.62×。需要把文档解析模型适配到自家表单的团队，可以照这套 SFT 加 RLVR 流程来做。

来源：[Hugging Face Blog](https://huggingface.co/blog/nvidia/building-on-nemotron-35-parse-open-data-fine-tunin)　`开源` `训练` `多模态`

### Hugging Face 用 TRL 训练四个 agent 协作的多智能体系统

Hugging Face 的文章用 TRL 的示例训练一个共享 Qwen3-0.6B 策略的四 agent 团队，agent 之间通过消息工具交换信息；75 步训练里成功率从 6.6% 升到 82.3%。示例可以在 Hugging Face Jobs 上复现，在两张 H200 上约五小时、花费大约 $50。想低成本试验多 agent 强化学习的开发者可以从这个示例起步。

来源：[Hugging Face Blog](https://huggingface.co/blog/training-swarms)　`Agent` `训练` `工具`

### llama.cpp 推出 AMD Ryzen 和 Radeon 性能看板

ggml-org 在 Hugging Face 上推出 llama.cpp × AMD Benchmark 看板，按 llama.cpp 版本、模型和量化追踪提示处理和文本生成速度，目前覆盖 Radeon 8060S（gfx1151）和 Radeon AI Pro R9700S（gfx1201）。测试每周运行一次，用 llama-bench 分别开关 Flash Attention。在 AMD 硬件上做本地推理选型时，可以先查这里的数据。

来源：[Hugging Face Blog](https://huggingface.co/blog/ggml-org/llamacpp-amd-bench)　`工具` `推理` `硬件`

## ⚡ 快讯

- **社区补丁集 llama-cpp-rdna-boosts 提升 AMD 显卡推理速度** 一位开发者推荐 llama-cpp-rdna-boosts 补丁集，称在自己的 AMD 显卡上把 token 生成从 35 提到 55 tokens/second，prefill 从 700 提到 1300。 [devnull.land](https://devnull.land/amd-specific-llama-cpp)
- **VibeVideoAgent：让编码 agent 在制作中检查视频草稿** VibeVideoAgent 是免训练框架，让编码 agent 在代码驱动的视频生成过程中用独立的多模态感知检查草稿，在 239 个 VibeVideoBench 任务上提升了多个模型的整体音视频质量。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.34237)
