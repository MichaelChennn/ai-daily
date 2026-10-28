# 2026-10-28 · AI 科技日报

## 今日要点

- Google DeepMind 发布实时世界模型 Genie 4，可用自然语言实时修改模拟场景，并首次原生生成音频。
- Liquid AI 发布 LFM3 系列，六个 2B 级模型全部开放权重；inclusionAI 发布 Ling-3.1-flash-1019 并放出基座模型。
- Anthropic 研究发现，分析师在 86% 的分析选择上与 AI Agent 被随机指定的倾向一致。

## 🔥 头条

### Google DeepMind 发布实时世界模型 Genie 4

Genie 4 是 Google DeepMind 的新一代世界模型，可以用自然语言实时修改正在运行的模拟（如改变天气、移动镜头、加入人物或物体），也是其首个原生生成音频的实时世界模型。目前以研究预览形式向受信任测试者开放，即将面向 Project Genie 中的 Google AI Ultra 订阅者，以及 Gemini API 和 Google AI Studio 的早期合作伙伴。对开发者来说，它可以在写引擎代码之前把想法变成可探索的原型，也可用于为机器人和 Agent 构建训练环境。

来源：[Google DeepMind Blog](https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation/)　`模型` `视频` `多模态`

### Anthropic 公布用 Claude 加速药物研发的早期进展

Anthropic 生命科学团队过去几个月与 BigHat Biosciences、Bristol Myers Squibb、Divergence Labs、Enveda、Generate Biomedicines 和 The Column Group 六家机构合作药物研发：Claude 约一个月内大体自主生成了约 35,000 个抗体设计；在 1,061 页生产文档的测试中，它发现了人工审查发现的全部 11 个问题，还标出了人工遗漏的问题，人工审查时间减少 89%。Anthropic 还收购了开发罕见肌营养不良疗法的 Mithril Medicine，开始自己的药物研发项目。这说明 Claude Code 这类 Agent 已经进入真实的科研设计和合规文档流程，不只是写代码。

来源：[Anthropic Research](https://www.anthropic.com/research/early-progress-drug-development) · [HN 讨论](https://news.ycombinator.com/item?id=50265609)　`Agent` `行业`

### Liquid AI 发布 LFM3 系列端侧开放权重模型

Liquid AI 发布 LFM3，在同一个 LFM3-1.7B-Base 骨干上训练出文本、视觉、音频、全模态和决策六个 2B 级模型，包括其首个全模态模型 LFM3-Omni-2B，全部开放权重并已上架 Hugging Face。官方称 LFM3-1.7B 参数比 LFM2.5-2.6B 少 35% 但表现更好，在 WebArena-Verified 上得分 38.42（前代 3.02），文本模型在 4-bit 精度下约 1 GB。每个模型都能在单张 GPU 上微调，适合要在本地设备上做语音、视觉或 Agent 任务的开发者。

来源：[Hugging Face Blog](https://huggingface.co/blog/LiquidAI/lfm3) · [Hugging Face Trending Models](https://huggingface.co/LiquidAI/LFM3-1.7B) · [LiquidAI/LFM3-Omni-2B-GGUF](https://huggingface.co/LiquidAI/LFM3-Omni-2B-GGUF) · [New audio model: LFM3-Audio-2B](https://huggingface.co/LiquidAI/LFM3-Audio-2B)　`模型` `开源` `多模态`

### Anthropic 研究：专家常在不知不觉中跟随 AI Agent 的判断

Anthropic 让 50 位有因果推断经验的专业分析师用 Claude Code 完成一项统计分析，并在每个关键决策上随机指定 Agent 倾向两个合理选项中的哪一个。在四个分析选择上，分析师 86% 的时候选择了 Agent 倾向的一方（如果 Agent 没有影响，预期约为 50%）；事后 77% 的人复述了 Agent 的论据，只有 15% 提到 Agent 是来源。对构建 Agent 产品、依赖“人在回路”把关的团队来说，这意味着人的最终签字未必是独立的检查。

来源：[Anthropic Research](https://www.anthropic.com/research/agents-judgment-calls)　`Agent` `安全`

## 🧠 模型

### inclusionAI 发布 Ling-3.1-flash-1019 并放出基座模型

inclusionAI 发布 Ling-3.1-flash 的升级版 Ling-3.1-flash-1019，总参数 560B、每 token 激活 25B，上下文窗口 1M token；同时发布基座模型 Ling-3.1-flash-base，供继续预训练和后训练研究使用。官方称 AutomationBench-AA 从 62% 提升到 68%，在 Artificial Analysis Intelligence Index v4.3.2 上得分 44（前代为 41）。模型卡提供 day-0 的 SGLang 镜像，想做领域适配的团队可以直接从基座模型开始。

来源：[Hugging Face](https://huggingface.co/inclusionAI/Ling-3.1-flash-1019) · [inclusionAI/Ling-3.1-flash-1019 · Hugging Face](https://www.reddit.com/r/LocalLLaMA/comments/1xgpo4q/inclusionailing31flash1019_hugging_face/) · [Ling-3.1-flash-1019 weights are out, and they released the base model too](https://www.reddit.com/r/LocalLLaMA/comments/1xgrr8n/ling31flash1019_weights_are_out_and_they_released/)　`模型` `开源`

### OpenBMB 开源 OCR 质检模型 MiniCPM-OCR Jev

OpenBMB 发布 1.3B 的文档解析模型 MiniCPM-OCR 1.0，以及 2B 的 OCR 质量评估模型 MiniCPM-OCR Jev：后者输入区域图像和候选 OCR 结果，输出 0 到 1 的分数，覆盖文本、公式和表格。Jev 在 JevOCRBench 上的 AUROC（×100）为 93.6，接近 Qwen3.5-397B-A17B 的 93.8，也能给其他 OCR 解析器的结果打分；权重、代码和文档采用 Apache License 2.0。做 RAG 的开发者可以用它在入库前自动放行可靠区域，把可疑区域交给人工复核。

来源：[Hugging Face](https://huggingface.co/openbmb/MiniCPM-OCR-Jev) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xgyqbb/openbmb_released_a_13b_ocr_model_and_a_separate/)　`模型` `开源` `多模态`

## 📄 论文

### TraceTrial-Bench：单独评测 Agent harness 的可靠性

论文提出 TraceTrial-Bench，把 Agent harness 的可靠性拆成上下文、执行、治理、生命周期、可观测性、工具和验证七个部分，构建 95 个专家级任务，分别评估 Agent 任务表现和 harness 可靠性。在 4 个 harness、9 个模型、3,420 次运行中，harness 宏平均得分在 59.8% 到 72.0% 之间，31.1% 的运行虽然完成了任务，却未满足至少一项 harness 标准。对搭建或选型 Agent 框架的开发者来说，只看任务成功率可能掩盖框架层面的问题。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.32285)　`论文` `Agent`

### Trajectory2Gym：只用有依据的决策训练工具调用 Agent

论文认为成功的工具调用轨迹不一定是有用的监督数据，提出 Trajectory2Gym：围绕覆盖不足的多步依赖构造可执行交互，只从 Agent 决策时可见历史能支撑的动作中提取监督。在五个规模的 Qwen3 上，它在 Tau1、Tau2 和 BFCL 上都有提升，三项基准的等权平均分提高 16.9-29.8 个百分点，有状态和多轮交互提升最明显。对准备 Agent 微调数据的团队来说，关键不只是收集更多成功轨迹，还要有意构造可学习的交互。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.33568)　`论文` `Agent` `训练`

### DynaFlow：让主 Agent 自己编写多 Agent 协作流程

DynaFlow 把可执行工作流的生成放进主 Agent 的动作空间：主 Agent 自行决定何时需要协作，并生成任务专用的程序，以顺序或并行方式调度子 Agent、交换信息并做验证；训练只针对主 Agent，子 Agent 保持不变。在覆盖数学推理、科学问答和多跳检索的六个基准上，基于 Qwen3.5-27B 的 DynaFlow 在 Forced 模式下总体准确率为 88.08%，比最强基线高 10.90 个百分点。对构建多 Agent 系统的开发者，它提供了用学习代替固定协作结构的思路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.34467)　`论文` `Agent`

## 🛠 开源与工具

### Codex 0.165.0 内置 Vertex AI 并加入 GPT-6.1 Terra

OpenAI Codex 0.165.0 新增内置的 Google Cloud Vertex AI 提供方（配置 model provider = "gcp"），并把 GPT-6.1 Terra 加入模型目录；支持的模型默认可在对话中途调整推理强度，新建配置默认启用 memory v2，并支持导入其他 Agent 的记忆。本版还修复了 marketplace URL 校验漏洞，该漏洞可能让 Git 连接到与白名单检查不同的主机。在 GCP 上统一管理模型调用的团队可以直接让 Codex 走 Vertex AI。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.165.0)　`工具` `代码` `Agent`

## ⚡ 快讯

- **Claude Code v2.1.312 修复超大 CLAUDE.md 被覆盖的问题** Claude Code v2.1.312 修复了 Claude 只看到开头就覆盖超大 CLAUDE.md、规则文件的问题，现在 Write 会要求先读完或原地编辑。 [GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.312)
- **Anthropic 给美国政府客户 40% 折扣** Anthropic 扩大与美国总务管理局（GSA）的合作，政府客户使用 Claude Enterprise、Claude for Government 和 Claude API 可享 40% 折扣。 [Anthropic News](https://www.anthropic.com/news/expanding-partnership-gsa)
