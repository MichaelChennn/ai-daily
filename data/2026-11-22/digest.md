# 2026-11-22 · AI 晨报

## 今日要点

- Anthropic 完成 IPO，发行价 $83.00，合计募资约 $93.5 billion，Class A 股票已在 Nasdaq 以 "ANT" 交易。
- OpenAI 客户案例显示 GPT-6 Astra 在金融研究中的引用覆盖与演示稿质量测试表现，Hebbia 称其为同时在两项指标上排名第一的模型。
- Hugging Face transformers 发布 v5.24.0，加入 Inkling 2 Mini、Apertus 1.5、Omnilingual ASR 等新模型支持，并统一缓存接口命名。

## 🔥 头条

### Anthropic 完成 IPO，发行价 $83.00

Anthropic, PBC 宣布首次公开发行完成，共发行 1,127,000,000 股 Class A 普通股，发行价为每股 $83.00，含承销商全额行使超额配售权。发行总毛收入约 $93.5 billion，其中约 $91.6 billion 由 Anthropic 获得；Class A 股票已于 November 19, 2026 在 Nasdaq Global Select Market 以 "ANT" 为代码开始交易。

来源：[Anthropic News](https://www.anthropic.com/news/ipo-close)　`行业` `产品`

### Apple 发布 Depth Pro 2 单目深度估计

Apple Machine Learning Research 发布 Depth Pro 2，用单一可扩展网络处理图像和视频，在输入原生分辨率上预测稠密度量深度图。作者称其同时具备度量准确、边缘锐利和跨帧时间一致，并称代码与权重已开放。

来源：[Apple Machine Learning Research](https://machinelearning.apple.com/research/depth-pro-2-monocular) · [Hugging Face Trending Models](https://huggingface.co/apple/DepthPro2)　`论文` `多模态` `图像`

### transformers v5.24.0 加入多款新模型支持

Hugging Face transformers 发布 v5.24.0，新增多模型支持，包括 Thinking Machines Lab 的多模态模型 Inkling 2 Mini、Swiss AI Initiative 的多模态模型 Apertus 1.5、Meta FAIR 的 Omnilingual ASR 以及 NVIDIA 的 Dory。该版本还把 past_key_values / cache_params 统一改名为 cache，旧名仍可用但会有一次性弃用警告。

来源：[GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.24.0)　`工具` `模型` `开源`

### Sage S1.5 Flash：320B 混合专家科学推理模型

Intern Large Models 发布 Sage S1.5 Flash 技术报告，介绍一个 320-billion-parameter 通用混合专家模型，用专门编码器处理分子图、生物序列与光谱等科学数据，并通过可验证环境训练工具调用、搜索与编码能力。报告在七个领域 33 个基准上评测，与五个基线对比时在 OfficeQA Pro、MLE-bench Lite、Harvey LAB 和 SpreadsheetBench 上排名第一。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21072)　`模型` `论文` `Agent`

## 🧠 模型

### OVH 发布 Olala-v1.0-mini-7A1B 推理模型

OVHai LLM 开放了 Olala-v1.0-mini-7A1B 权重，模型为 6.8B 总参数、每 token 约 1B 激活参数的混合 Mamba-3 / 注意力混合专家架构，支持 32K tokens 输入输出、推理与工具调用。官方提供 Transformers 与 vLLM 加载方式，并说明 llama.cpp、vLLM、ollama、mlx-lm 等默认尚不能直接加载该模型。

来源：[Hugging Face Trending Models](https://huggingface.co/OVHaiLLM/Olala-v1.0-mini-7A1B)　`模型` `开源` `推理`

### pi-H3 用 2–4 步生成 MiniMax H3 视频

Lakonik/pi-H3 提供 MiniMax H3 的 2 步与 4 步适配器，结合 pi-Flow v2 少步蒸馏与 DWD（Decoding Without a Decoder），在最后一步直接预测视频帧以跳过 VAE 解码，并生成同步音频。适配器支持文本、首帧和尾帧条件，提供 INT8 ConvRot 版本，但官方推荐使用 DWD 适配器。

来源：[Hugging Face Trending Models](https://huggingface.co/Lakonik/pi-H3)　`模型` `视频` `开源`

## 📄 论文

### InclusionMed：包容性医疗 AI 评测基准

InclusionMed Collaboration 提出面向包容性医疗的开放评测计划，用 Atlas 按医疗角色与 AI 能力组织基准，并发布汇总前沿模型结果的 InclusionMed Index。首版从 388 个候选中审计并复现 4 个公开基准，加上私有诊断推理基准共 5 个，覆盖九个角色—能力组合中的三个，模型总分区间为 17.5 至 49.1（满分 100）。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21218)　`论文` `评测`

### AscendGYM：面向真实负载的算子优化基准

AI Training Platform Team 等提出 AscendGYM，用于评估在 Ascend NPU 上优化已有算子的能力，初始套件包含三个难度等级的 48 个算子，测试用例的数据类型与张量形状采自真实训练与推理任务。基准提供 model evaluation 与 model-harness evaluation 两种模式，并提出兼顾加速比与 token 成本的 Speedup-Token Score（STS）。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17621)　`论文` `Agent` `硬件`

### VibePrevisBench：Blender 4D 场景生成的 Agent 编码评测

Kling-Keye 发布 VibePrevisBench，评测编码 Agent 能否把一段需求变成可执行的 4D 场景并渲染代理视频，242 个任务覆盖脚本、照片、续写和参考视频四类输入。评测分两层：Rule-based Scene Check 重新运行代码并与隐藏真值在九个维度比对，VLM-based Screen Check 判断通过的事实能否在代理视频中被识别；对 11 个前沿编码 Agent 的分析显示，多模态理解尤其是空间与相机运动理解是主要差距。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15789)　`论文` `Agent` `代码`

### Agentic Robotics：具身智能体评测框架与路线图

Grid Robotics 等提出 agentic robotics 视角，主张由基础模型与 embodied harness 组成的 Embodied System 2 是其决策核心，并提出同时衡量模型能力与闭环系统表现的评测框架。作者指出 GPT-6 Astra 发布后数周内，带 agentic harness 的前沿模型已在多个具身基准上追平或超过任务专用策略，但社区仍缺少统一定义与可靠评测。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18359)　`论文` `Agent`

## 🛠 开源与工具

### CLI-Anything：让任意软件接入 Agent

HKUDS/CLI-Anything 通过为各类软件生成命令行 harness，让 Pi、OpenClaw、nanobot、Cursor、Claude Code 等 Agent 可以调用它们，仓库内已包含 Blender、GIMP、LibreOffice、Obsidian、Godot 等软件的 agent-harness 目录。项目提供 CLI-Hub，可通过 pip install cli-anything-hub 后用 cli-hub install <name> 浏览并安装社区构建的 CLI。

来源：[GitHub Trending](https://github.com/HKUDS/CLI-Anything)　`工具` `Agent` `开源`

### superpowers：编码 Agent 的开发方法论框架

obra/superpowers 是一套构建在可组合技能之上的编码 Agent 开发方法论：Agent 先澄清目标并给出分段 spec，经确认后制定实现计划，再以 subagent-driven-development 流程逐任务实现并检查结果。该方法强调 red/green TDD、YAGNI 与 DRY，技能可自动触发，并提供 Claude Code、Codex、Cursor、Gemini CLI 等多种 harness 的安装方式。

来源：[GitHub Trending](https://github.com/obra/superpowers)　`工具` `Agent` `代码`

### Firecrawl Local：本地运行的抓取与 Agent 上下文服务

firecrawl/firecrawl 仓库包含 Firecrawl Local 与自托管服务端代码，可在本地把网站转成干净 markdown，并作为 MCP 服务器接入 AI Agent；serve 命令在 3002 端口提供 Firecrawl v2 API，本地路由无需 API key。需要搜索、结构化 JSON、截图等能力时会转向 Firecrawl Cloud 的 search 与 Alexandria 服务。

来源：[GitHub Trending](https://github.com/firecrawl/firecrawl)　`工具` `Agent` `开源`

### ClawDOS：在 DOS 上运行的 Claude 编码 Agent

ClawDOS 是一个在 IBM PC XT（8088 at 4.77 MHz、640K RAM、CGA）上运行的 AI 编码 Agent，harness 直接讲 Claude Messages API，在 DOS 下读写文件、用 Turbo C 编译并运行程序、读取屏幕截图和保存对话记忆。TLS 由另一台“bridge” PC 承担，仓库含约 13,000 行 C 与 C++ 代码、HARNESS.EXE 启动镜像以及 DOS 环境下的测试。

来源：[ricapar.net](http://ricapar.net/ClawDOS/)　`工具` `Agent` `代码`

## ⚡ 快讯

- **AutoClip：长视频一键剪成短视频** zhouxiaoka/autoclip 是开源的 AI 视频剪辑桌面工具，贴一个链接即可把长视频剪成适配抖音、小红书、TikTok、Reels 与 YouTube Shorts 的短视频，并生成字幕、封面和发布文案。 [GitHub Trending](https://github.com/zhouxiaoka/autoclip)
- **OpenSRE：面向 CI/CD 可靠性的开源 Agent** Tracer-Cloud/opensre 是自托管 CLI Agent，可读取失败的 CI 运行记录、追踪原因并推送待审阅的修复，同时统计失败率与 main 分支变红时长等可靠性指标。 [GitHub Trending](https://github.com/Tracer-Cloud/opensre)
- **last30days-skill：聚合社交平台的 Agent 调研技能** mvanhorn/last30days-skill 让 Agent 并行检索 Reddit、X、YouTube、HN、Polymarket 与网页，按点赞、播放与真实资金赔率等信号排序，再由 AI judge 合成简报。 [GitHub Trending](https://github.com/mvanhorn/last30days-skill)
