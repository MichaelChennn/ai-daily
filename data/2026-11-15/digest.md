# 2026-11-15 · AI 晨报

## 今日要点

- IBM 发布 Granite 4.1 LLMON 预览模型，用标记语言区分指令和数据来防御提示注入。
- 小型开源语音模型扎堆：Kitten TTS 2、全双工对话模型 Haru-4B 和 4.5M 参数的 tiny-voca。
- NVIDIA 演示两台 DGX Station 用 vLLM 服务 GLM-5.3，峰值吞吐 607.8 tok/s。

## 🔥 头条

### IBM 发布 Granite 4.1 LLMON 预览模型，专防提示注入

IBM Granite 团队发布 granite-4.1-3b-LLMON-preview 和 granite-4.1-8b-LLMON-preview 两个实验性预览模型，用一种叫 LLMON（LLM Object Notation）的标记语言把用户指令和模型读取的数据分开标注。IBM 称在 OPI 基准上 LLMON 几乎消除了这类注入问题，比测试过的最佳前沿模型多挡住 47% 的攻击，通用能力与 Granite 4.1 Instruct 持平。做 RAG 和工具调用 Agent 的开发者可以拿它评估“文档里藏指令”的风险，但官方明确说只适合探索和评估，不要用于生产。

来源：[Hugging Face Blog: LLMON](https://huggingface.co/blog/ibm-granite/llmon-an-llm-native-markup-language-now-in-granite) · [maccus.fr](https://maccus.fr/en/ibm-granite-prompt-injection/)　`模型` `安全` `开源`

### KittenML 发布 Kitten TTS 2 系列小型语音合成模型

Kitten TTS 2 分 Mini、Nano、Pico 三个规格：Mini 有 82M 参数，支持 16 种语言、118 种音色和 24 kHz 输出，int8 的 ONNX 权重只有 82.7 MB，在 CPU 上运行且不需要 PyTorch；Nano 和 Pico 每个语言模型分别是 17M 和 7.2M 参数。模型、音色包和 G2P 文件都采用 Apache-2.0，pip install kittenml 即可调用，适合要在端侧或没有 GPU 的服务器上加语音输出的应用。

来源：[Hugging Face](https://huggingface.co/KittenML/kitten-tts-2-mini)　`语音` `开源` `模型`

### NVIDIA 教程：两台 DGX Station 用 vLLM 跑 GLM-5.3

NVIDIA 开发者博客演示用两台 DGX Station 以张量并行（TP=2）提供 GLM-5.3 NVFP4 服务：约 464 GB 的检查点超过单块 GB300 的 252 GB HBM3e，两块 GPU 各存约一半权重，通过一个 OpenAI 兼容接口对外服务。在 SPEED-Bench Coding 上，并发 16 时总吞吐达到峰值 607.8 tok/s，并发 32 时回落到 385.0 tok/s、平均请求延迟 453.5 s。想在本地部署超大 MoE 模型的团队可以照这套双机配置做，也要注意并发数是主要的调优点。

来源：[developer.nvidia.com](https://developer.nvidia.com/blog/when-one-gpu-isnt-enough-serving-glm-5-3-across-two-nvidia-dgx-stations-with-vllm/) · [HN 讨论](https://news.ycombinator.com/item?id=50497155)　`推理` `硬件` `开源`

### Claude 博客发布常驻 Agent 构建指南

指南把常驻（always-on）Agent 拆成事件收件箱、定时器、记忆、权限和发件箱五个基本组件：Agent 大部分时间在休眠，被收件箱里的事件唤醒后执行一次 run。文中给了不少可直接借鉴的设计原则，比如记忆只存 Agent 无法再查到的东西、需要审批时用延迟工具调用结束当前 run 并保存会话、推送消息先保持克制再逐步争取用户注意力。正在做后台 Agent 或定时任务型 Agent 的团队可以对照检查自己的架构。

来源：[Claude Blog](https://claude.com/resources/articles/building-always-on-agents)　`Agent` `产品`

## 🧠 模型

### Haru-4B：边听边说的全双工语音对话基座模型

higurashi-ai 开源 Haru-4B，一个低延迟、多语言的全双工连续语音对话基座模型，基于 Qwen3.5-4B 文本骨干，每 133 ms 读入一帧用户音频，同时输出自己的一帧音频和文本。权重采用 Apache License 2.0，PyTorch 实现需要约 12 GB 显存的 NVIDIA GPU，另有 MLX 实现和 vLLM-Omni 插件。官方说明它是面向研究的预训练基座，不是可靠的事实来源，也不会像助手那样遵循指令。

来源：[Hugging Face Trending Models](https://huggingface.co/higurashi-ai/Haru-4B)　`语音` `开源` `模型`

### Rayline 开源 0.6B 路由模型 ARC 1.0，帮 Agent 选模型

ARC 1.0 读取 Agent 的对话，输出任务成功率、token 用量、推理强度等信号，由应用结合自己的模型、价格和策略决定下一次请求交给云端还是本地模型；模型基于 Qwen3.5-0.8B，采用 Apache 2.0。模型卡称混合端云配置在六个基准上保留了 Opus 5.5 97.5% 的质量、成本低 92.9%，但公开的 vllm-arc 插件仍在开发中，原版 vLLM 加载不了这个架构。

来源：[Hugging Face](https://huggingface.co/rayline-ai/ARC-1.0) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xw29ic/arc_10_a_decision_model_for_routing_ai_agents/)　`模型` `Agent` `开源`

### tiny-voca：4.5M 参数、代码权重数据全开放的英文 TTS

tiny-voca 是一个从头训练的英文语音合成模型，共 4,537,291 个参数、18 MB，提供两种 24 kHz 美式英语音色，在 4 个 CPU 线程上约为实时速度的 70x，可用 PyTorch、ONNX Runtime 或在浏览器里运行。代码和权重采用 Apache-2.0，数据集采用 CC BY 4.0，训练配方也一并公开，发布的权重在一块 RTX 4090 上训练了 7.7 小时，适合想复现或改造小型 TTS 的开发者。

来源：[tiny-voca](https://github.com/n4ze3m/tiny-voca) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xw7zrg/tinyvoca_a_fully_open_45mparameter_tts_code/)　`语音` `开源`

## 📄 论文

### WorldFoundry：统一世界模型推理与评测的开源基础设施

论文先把生成式世界模型定义为维护持久状态、能响应动作或干预并生成时间连贯轨迹的预测动力系统，再推出开源基础设施 WorldFoundry，覆盖视频、3D 和 4D、具身动作和交互式世界系统的推理与评测。目前目录收录 270 个模型条目、74 个基准和 62 个指标条目，并把“能跑通”和“评测结论”分开记录。做世界模型的研究者可以用它在同一套流程下可复现地比较不同模型。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.10771) · [WorldFoundry](https://github.com/OpenEnvision/WorldFoundry)　`论文` `视频` `开源`

### Sage-Taiyi：用元认知引导 AI 做科研构思

Sage-Taiyi 让系统在搜索过程中持续监控自己对证据、假设和未解问题的理解，并据此调整研究目标、选择推理方法。在包含 265 个任务（来自十个学科的 50 篇论文）的 AI 科研构思基准 Taiyi-Bench 上，它在全部八项指标上排第一，Overall 得分 54.0，最强基线 AI Scientist-v2 为 47.9；化学合作实验中，钴催化羰基化的产率从痕量提高到 84%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12762)　`论文` `Agent`

### SplatAnything：归一化高斯间距，让前馈 3DGS 适应任意场景

论文指出现有前馈 3DGS 方法在径向距离归一化的空间里预测高斯属性，但相邻高斯中心的间距仍会随场景尺度和相机配置大幅变化，导致高斯尺度的监督目标含糊。作者提出 GSNorm，对场景级的高斯间距统计量做归一化，并建立覆盖多种数据集、输入稀疏度和外推视角的评测；实验显示在场景尺度和视角变化大时提升尤其明显。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08264) · [SplatAnything](https://github.com/zju3dv/SplatAnything)　`论文` `图像`

## 🛠 开源与工具

### tandem.cpp 更新：16 GB 显卡跑 DeepSeek-V4.1，并支持 ROCm

tandem.cpp 是 llama.cpp 的补丁集，把最常用的专家留在 GPU、其余交给 CPU 协助计算，让显存放不下的 MoE 模型跑得更快。作者实测在 RTX 5070 Ti 16 GB 加 64 GB 内存的 PC 上，DeepSeek-V4.1-Flash IQ2_XS 的解码速度从 llama.cpp 的 7.4 tok/s 提到 14.2 tok/s；补丁现在也能用 HIP 构建，跑在 AMD 显卡上。想在消费级硬件上跑大 MoE 模型的人可以直接试。

来源：[tandem.cpp](https://github.com/ewhacc/tandem.cpp) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xwan2j/update_tandemcpp_deepseekv41_on_a_64_gb_pc_with_a/)　`推理` `开源` `工具`

### LLVQ 的 Rust 实现：Qwen3 压到约 2.7 bit/参数

这是 Qualcomm 的 Leech 格向量量化论文（LLVQ）的独立 Rust 实现，自带融合的 CUDA 和 Metal kernel，推理时直接读取 2-bit 码字、不构建稠密矩阵；作者已把 Qwen3 的 4B、8B、14B 压到约 2.7 bit/参数并放上 Hugging Face。README 称 4B 比 llama.cpp 的 IQ2_XXS 高 23.6 分、每参数只多 0.25 bit，但三个模型的 MMLU 分别比 4-bit AWQ 低 4.76、4.21 和 2.46 分，而且在 A100 上解码比 vLLM 的 FP16 还慢。

来源：[LLVQ in Rust](https://github.com/pjmalandrino/llvq) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xwerbo/qwen3_4b_8b_14b_at_27_bits_per_weight_with_leech/)　`推理` `开源` `工具`

### Plannotator：在浏览器里审阅编码 Agent 的计划和代码

Plannotator 是本地运行、基于浏览器的审阅界面，支持 Claude Code、Codex、Copilot CLI、Gemini CLI、OpenCode 等编码 Agent：Agent 给出计划或改完代码后，可以在浏览器里批注、审阅 diff 和 PR，再把反馈一键发回 Agent。新推出的 Plannotator Inbox 把多个 Agent 的决策、原型和计划集中到一处；项目称不收集使用遥测，数据默认留在本地。

来源：[GitHub Trending](https://github.com/backnotprop/plannotator)　`工具` `Agent` `代码`

### agweb：给编码 Agent 用、不抢焦点的 macOS 浏览器

agweb 基于 WebKit，Agent 在 shell 里用类似 playwright-cli 的 agweb 命令操作它，窗口从不抢焦点，对话框、文件选择和下载都在代码里处理，用户可以实时查看所有 Agent 的页面。作者实测五个空闲页面占 590 MB 内存，Headless Chrome 为 730 MB；代价是只支持 WebKit，Playwright 和 Chrome 扩展都接不上，需要 macOS 26 或更高版本。

来源：[GitHub](https://github.com/paul-nameless/agweb) · [HN 讨论](https://news.ycombinator.com/item?id=50497147)　`工具` `Agent`

## ⚡ 快讯

- **chrome-devtools-mcp v1.13.0 加入 logpoints 和网络 mock** chrome-devtools-mcp v1.13.0 新增基于 DevTools BreakpointManager 的 logpoints 和页面级网络 mock，编码 Agent 调试网页时可直接用。 [GitHub Trending](https://github.com/ChromeDevTools/chrome-devtools-mcp) · [chrome-devtools-mcp releases](https://github.com/ChromeDevTools/chrome-devtools-mcp/releases)
- **Cohere 完成收购 AISLE，组建网络安全业务 Cohere Cyber** Cohere 完成对漏洞自动发现与修复公司 AISLE 的收购并以其为基础成立 Cohere Cyber，同时迎来 AI 代码审查平台 cubic 的团队。 [Cohere](https://cohere.com/blog/cohere-expands-its-sovereign-ai-platform-with-aisle-and-cubic)
- **Interconnects：黄仁勋离任后，Nvidia 对开放模型的投入可能收缩** Interconnects 认为开放模型是 Jensen 更具雄心的创始人式押注，他离任后 Nvidia 以稳住局面为先，大笔投入很可能减少，Nemotron 也还谈不上大功告成。 [Interconnects](https://www.interconnects.ai/p/open-source-ai-without-jensen)
- **190 行纯 JAX 实现 DeepSeek V3 架构** 有人用 190 行纯 JAX 实现了 DeepSeek V3 的 MLA、DeepSeekMoE、无辅助损失负载均衡和 MTP，并在 MacBook Air 上从头预训练了一个 36.2M 参数的小模型，作者说明这只是架构演示。 [GitHub](https://github.com/Vaibhaav-Tiwari/deepseek-v3-jax) · [HN 讨论](https://news.ycombinator.com/item?id=50497589)
