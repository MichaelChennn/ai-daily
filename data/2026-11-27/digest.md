# 2026-11-27 · AI 晨报

## 今日要点

- llama.cpp v1.1.0 发布：新增 Inkling 2 系列模型支持、大批 TTS 与音频模型、DFlash 推测解码拆分，并弃用旧 llama batch API。
- NVIDIA 发布 Agentic LongLive，用异步 Agent 记忆维持长视频流中的人物与场景一致性，在 H100 上仅增加约 1% 生成时间。
- Sage-Med-Preview 以 35B 总参数、3B 激活的医疗多模态模型，在 31 个公开多模态基准上取得 58.26% 平均分。

## 🔥 头条

### llama.cpp v1.1.0 发布，扩音频与推测解码

llama.cpp v1.1.0 加入 Inkling 2 家族、Domyn Edge 4B、Zaya1 8B 等模型支持，并带来 Kokoro、Zonos3-Mini、MiniMax-Music3、YuE2 等 TTS 与音频模型。旧 llama batch API 被弃用，DFlash 推测解码拆分为多种 draft 方法，服务器端还新增 named tool_choice 与按 bpw 或体积预算的自动量化。对本地推理开发者来说，这个版本同时带来更广的模型覆盖与一批 API 迁移改动。

来源：[GitHub Releases](https://github.com/ggml-org/llama.cpp/releases/tag/v1.1.0)　`工具` `开源` `推理`

### NVIDIA 用 Agent 记忆延长长视频流一致性

NVIDIA 提出 Agentic LongLive，为实时自回归视频生成加入异步 Agent 记忆：记忆 Agent 只读取已披露的提示词，为人物、物体和场景维护文本状态与演化图像，并在下一镜头开始前预填生成器的 attention sink。在新基准 LongStory-Online 上，它相对基座生成器 LongLive-2.0 把持久状态准确率提升 26.3 分、主角身份提升 44.9、重访地点一致性提升 40.4，H100 上仅增加约 1% 生成时间。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34907)　`视频` `Agent` `模型`

### Sage-Med-Preview 探索医疗多模态的缩放规律

上海 AI Laboratory 等团队提出 Sage-Med-Preview，一个 35B 参数、3B 激活的医疗多模态模型，训练数据来自 322.7 million 条候选记录的阶段化筛选，并结合医学预训练、分阶段监督微调与自适应强化学习。作者的评测显示，模型在 31 个公开多模态基准上平均分为 58.26%，高于 Hulu-Med-235B-A22B 的 50.99% 和 Intern-S2-Preview 的 52.24%。论文同时指出，单纯放大参数主要提升文本能力，视觉感知提升有限，推理模式也难以弥合视觉差距。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34575)　`模型` `多模态` `论文`

### NVIDIA 开源 Nemotron 3.5 Parse 训练数据与配方

NVIDIA 公布 Nemotron 3.5 Parse 的合成训练数据集、微调配方与 DFlash2 推测解码方案。该文档模型把页面图像转成带阅读顺序、内容类别和边界框的结构化数据，可用于 RAG 与 Agent。三个开源数据集分别包含 Synthetic Charts V1 的 9.98M 条样本、Synthetic Tables V1 的 1M 条样本和 OCR Synthetic Multilingual v2 的 7.9M 条样本，训练流程先用 SFT 建立能力，再用 GRPO 形式的 RLVR 提升一致性与完成度。

来源：[Hugging Face Blog](https://huggingface.co/blog/nvidia/building-on-nemotron-35-parse-open-data-fine-tunin)　`模型` `开源` `训练`

### Mixture-of-Loops Transformer 复用 KV 记忆

字节跳动 Seed 提出 Mixture-of-Loops Transformer（MoLT），其 Mixture-of-Loops Attention 用 keys 和 values 作为跨层、跨循环的记忆。其中 U-shaped MoLT 把记忆构建与预测读出分离，可跳过未使用的解码遍历而不改变预测结果。在 400B-token 预训练中，U-MoLT 相对 OLMo3 在 700M 模型上取得 1.7x 验证交叉熵 token 效率，并在 3B MoE 上把 10-task 准确率提升 2.1 个百分点。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34923)　`论文` `训练` `推理`

## 🧠 模型

### DyLoMo-DiT 用循环复用扩散 Transformer 参数

DyLoMo-DiT 把扩散 Transformer 的深度、参数与算力拆开处理：权重共享的循环反复应用中间层，稀疏专家按 token 分配参数，并按噪声水平动态改变循环次数。在 ImageNet 256times256 上，它相对 DiT 将 FID 降低 11-24%；放大后的文本到图像模型 GenEval 得分为 0.714，高于 FLUX.1 的 0.673，而每 token 激活参数为 1.05B，低于 12B。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.30844)　`论文` `图像`

### Integral 让 VLM 在共享表征空间里生成图像

KAIST AI 提出 Integral，把预训练视觉语言模型改造为统一多模态模型，核心是让理解与生成共用视觉表征空间。其 Abstraction Fusion 从冻结的视觉编码器聚合分层表征构造共享视觉 token，Block-wise MoT 则引入只在 block 边界与视觉语言模型交互的轻量生成流。作者的对照实验显示，相比使用独立视觉表征空间，共享表征能显著改善生成学习效果。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31237)　`论文` `多模态` `图像`

## 📄 论文

### Real2SimLab 统一真实到仿真评测平台

北京大学 PKU-VaLuE-Lab 提出 Real2SimLab，用统一平台评测从真实观测构建仿真的方法：运行方法写出的程序，再用各基准原始 scorer 给输出仿真打分，避免为每个方法与基准做重复集成。平台还提供训练数据与奖励标注流水线，并通过过滤已存在于基准中的视频记录来避免数据污染。目前支持 47 个 coding agents、5 个非 agent 方法和 6 个基准，平台与收录近 300 篇论文的 Awesome-Real2Sim 均开源。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34849)　`论文` `Agent` `开源`

### VibeVideoAgent 为代码生成视频补上感知回路

可灵 Kling-Keye 提出 VibeVideoAgent，这是一个无需训练的框架，让 coding agent 在制作过程中持续检查自己的草稿。多模态感知运行在与编码器分离的短生命周期上下文中，返回紧凑且有依据的 Findings，七个原语可以在统一的多时钟资产表示上从粗到细查看素材、核对需求并比对不同版本。在 239 个 VibeVideoBench 任务上，固定感知模型并匹配运行时后，Claude Opus 5.5 的整体视听质量（L3）从 4.03 提升到 4.43。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34237)　`论文` `Agent` `视频`

### PyRUA-Dex 用编码 Agent 开发灵巧手策略

北京大学 DAGroup 提出 PyRUA-Dex，让编码 Agent 通过程序化策略学习灵巧操作，从而摆脱对高质量示教数据的依赖。流程分两阶段：多个 Agent 并行探索任务技能并组合，一个蒸馏 Agent 把成功尝试凝练成任务库与一份程序；随后在随机化布局下改进这份程序以增强鲁棒性。模拟环境中它取得 Bench2Dex 72.9 分和 DexJoCo 全随机化下 81.0% 成功率，真实平台上用两只 22-DoF 手弹钢琴、写书法，学习新曲谱最快只需 30 分钟。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.33144)　`论文` `Agent` `训练`

### I2VT 把图像编辑能力迁移给视频编辑器

卡内基梅隆大学提出 Image-to-Video Transfer（I2VT），让视频编辑器把单张图像当作一帧视频来扮演图像编辑器，由图像编辑器在每个去噪步引导视频编辑器的预测。训练只需单张图像，不改架构也不需要新的成对视频，测试时则把增强后的能力应用到整段视频并保持时间一致性。作者同时扩展出 OpenVE++，加入动作变化、表情变化、身体动作与场景重光照四类任务，在三个视频编辑器上均取得 OpenVE-Bench 与 OpenVE++ 的 SOTA 结果。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34941)　`论文` `视频`

### TT-RSI 在测试时递归自我改进

上海 AI Laboratory 提出 TT-RSI，一个无标签的测试时改进框架，由两部分互相支撑：In-Context RSI 反复带上完整的上一次解答重做题目，让模型自己决定如何利用旧推理；In-Weight RSI 则把连续改进蒸馏进模型权重，从而越过一开始就出错的多数答案。实验显示 TT-RSI 相对基座模型平均准确率提升 +13.89%，在相同测试时扩展预算下比最强的自一致性方法高出 +4.79%。作者也承认当前方法没有正确性感知的拒绝规则，持续错误的问题仍待解决。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.30965)　`论文` `推理` `训练`

## 🛠 开源与工具

### llama.cpp 推出 AMD 平台基准看板

ggml-org 在 Hugging Face 上线 llama.cpp × AMD Benchmark 看板，可按硬件、模型和 llama.cpp 构建版本对比不同量化下的提示处理与文本生成性能。看板当前收录 Radeon 8060S（gfx1151）和 Radeon AI Pro R9700S（gfx1201），提供 Overview、Build history 与 Context scaling 三个视图，并直接读取公开的存储桶数据，便于 AMD 开发者复用结果做自己的图表或与本地运行对比。

来源：[Hugging Face Blog](https://huggingface.co/blog/ggml-org/llamacpp-amd-bench)　`工具` `硬件`

### HF 博客教程：训练与评估多智能体集群

Hugging Face 博客推出多智能体系统系列教程，核心问题是通信是否真的带来收益，还是只是多花了算力。首个示例用四个共享 Qwen3-0.6B 策略的智能体协作排序数字，通信工具包括 message(to, text)、read_messages() 和 check_notifications()，并通过共享团队奖励的集中式训练与去中心化执行来训练协作，配套示例可在 Hugging Face Jobs 上复现。

来源：[Hugging Face Blog](https://huggingface.co/blog/training-swarms)　`Agent` `训练` `工具`

## ⚡ 快讯

- **EgoUseBench 评测随身设备上下文下的电脑操作** 浙江大学提出 EgoUseBench，含 693 个任务，评测 Agent 在三种第一人称上下文设定下的表现。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.34466)
- **AIRIS 评测流式视频中的社交具身智能** 腾讯提出 AIRIS 流式基准，含 8,000 条专家问题、357 段第一人称片段与 36 个能力维度。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.34347)
- **DocSEAM 为多页文档注入跨页上下文** MMLab@NTU 提出 DocSEAM，用中心锚定掩码自注意力融合邻页信息且不改变视觉 token 数量。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.34420)
- **Entangle 用人类视频做机器人上下文学习** Entangle 把单个人类视频与机器人观测映射为未来视觉状态和可执行动作，在 Astribot S1 上取得 83.5/100。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.28732)
- **WorldReforge 用仿真失败轨迹训练世界模型** 浙江大学提出 WorldReforge，构建 62k 条仿真轨迹，在 Cosmos3 Nano 上把物体轨迹误差整体降低 28.2%。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.33925)
- **SEEK 让机器人跨次尝试积累执行知识** 南洋理工大学提出 SEEK，用程序化策略与动作效果库积累知识，RoboDojo 成功率从 19.7% 升到 48.0%。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.33915)
