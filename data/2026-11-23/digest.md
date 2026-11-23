# 2026-11-23 · AI 晨报

## 今日要点

- OpenAI 首席科学家 Jakub Pachocki 公开内部困惑度（perplexity）数据，主张用这一指标建立跨实验室的安全与评测标准。
- 开源侧今天被 Agent 工具链刷屏：superpowers、CLI-Anything、Firecrawl Local、OpenSRE 都提供了可直接接入编码 Agent 的工作流。
- 模型方面，InternLM 的 Sage S2.1 Flash 技术报告、OVHcloud 的 Olala-v1.0-mini-7A1B 与 LingSante-3.1-flash 分别覆盖推理 Agent、多语言小模型和医疗长上下文。

## 🔥 头条

### OpenAI 公开困惑度数据，主张用它统一模型评测与安全标准

OpenAI 首席科学家 Jakub Pachocki 在博客中公开了从 GPT‑3.5 起的内部困惑度（perplexity）测量，低于 0.8 的损失区间催生了网络安全与数学等方向的 transformative capabilities。他主张用困惑度（或等价地 cross-entropy loss）作为跨实验室可比的共同基准，并提出在模型能力被充分理解前设定各方共同承诺不逾越的开发上限。

来源：[OpenAI News](https://openai.com/index/perplexity-and-intelligence)　`安全` `行业` `推理`

### Sage S2.1 Flash：320B 混合专家模型面向科学与交互式任务

InternLM 团队发布 Sage S2.1 Flash 技术报告，提出 320-billion-parameter 的通用 mixture-of-experts 模型，用于科学证据推理与交互式环境中的行动。Sage Sci-Perception 用专门编码器处理分子图、生物序列与光谱，再由模态专用 projector 映射到共享骨干的输入空间。在 33 个基准的评测中，它在 OfficeQA Pro（72.2）、MLE-bench Lite（90.3 HumanRank）等项目排名第一，在 OSWorld-Verified（85.2）等项目排名第二。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21072)　`模型` `多模态` `Agent`

### CLI-Anything 把桌面软件变成 Agent 可调用的 CLI

HKUDS 的 CLI-Anything 项目通过为各类软件生成 CLI harness，让 Agent 以命令行方式操作图形软件，官方称目标是让所有软件都变成 agent-ready。社区已为 Blender、GIMP、LibreOffice、Obsidian、Chrome 等大量软件贡献 harness，并通过 CLI-Hub 统一安装与管理。开发者可用 pip install cli-anything-hub 后用 cli-hub install <name> 获取社区构建的 CLI。

来源：[GitHub Trending](https://github.com/HKUDS/CLI-Anything)　`Agent` `开源` `工具`

### superpowers：面向编码 Agent 的软件开发方法论

obra 的 superpowers 提供一套完整的编码 Agent 开发方法论，先让 Agent 澄清需求并给出可读的设计，再产出实现计划，然后进入 subagent-driven-development 流程，由多个 Agent 逐任务执行并检查。技能可自动触发，无需额外配置，并提供 Claude Code、Codex、Cursor、Gemini CLI 等多种 harness 的安装方式。

来源：[GitHub Trending](https://github.com/obra/superpowers)　`Agent` `工具` `代码`

### Firecrawl Local：单二进制把网页转 Markdown 并接入 Agent

Firecrawl 的新形态是 Firecrawl Local，可在本机以单个二进制运行，把网站转为干净 Markdown，同时作为 MCP server 接入 AI Agent，并在 localhost 上提供 Firecrawl API。它支持 scrape、crawl、map 与 batch scrape，并可在本地解析 PDF 与 Office 文档；需要搜索或云端能力时再回落到 Firecrawl Cloud 的 550+ 数据提供商。

来源：[GitHub Trending](https://github.com/firecrawl/firecrawl)　`工具` `Agent` `开源`

## 🧠 模型

### Olala-v1.0-mini-7A1B：OVHcloud 开源 7A1B 多语言推理模型

OVHcloud 旗下 OVHai LLM 发布 Olala-v1.0-mini-7A1B，这是一个基于 hybrid Mamba-3 / attention mixture-of-experts 架构的小型推理模型，面向对话、指令遵循与工具调用。模型总参数 6.8B、每 token 约 1B 激活，在 JUPITER、Jean Zay 和 MeluXina 三台欧洲超算上用 12.8T tokens 训练，权重以 apache-2.0 开放。当前官方 llama.cpp、vLLM 与 mlx-lm 尚不能直接加载，需要使用其 fork。

来源：[Hugging Face Trending Models](https://huggingface.co/OVHaiLLM/Olala-v1.0-mini-7A1B)　`模型` `开源` `推理`

### LingSante-3.1-flash：面向医疗长任务的开源混合专家模型

inclusionAI 发布基于 Ling-3.1-flash 的开源权重模型 LingSante-3.1-flash，总参数 560 billion、每 token 激活 25 billion，支持 1-million-token 上下文。它通过医疗混合预训练、中训练、任务级强化学习与多教师 on-policy 蒸馏，训练模型在证据核验、复杂医疗推理与长流程医疗任务上的表现。模型卡说明它仅供研究与评测，不能作为独立诊断、处方或治疗依据。

来源：[Hugging Face Trending Models](https://huggingface.co/inclusionAI/LingSante-3.1-flash)　`模型` `开源` `安全`

### KORMo-Web-11B：KAIST 出品的韩英双语 GUI Agent 模型

KAIST MLP Lab 基于自研基础模型扩展出 KORMo-Web-11B，把 LLM 推理、VLM 图像理解与 GUI 浏览器操作合到一个模型中。训练使用 10M+ 原子级网页预训练样本与 100K+ 双语浏览器操作轨迹，权重以 Apache-2.0 开放。在 Online-Mind2Web 的 612 个真实网站任务上，其韩语任务成功率为 33.7%，比最强非 KORMo 开源权重基线高 13.5 个百分点。

来源：[Hugging Face Trending Models](https://huggingface.co/KORMo-VL/KORMo-Web-11B)　`模型` `多模态` `Agent`

### tiny-voca：4.5M 参数的英文 TTS 模型，可跑在手机与浏览器

n4ze3m 发布 tiny-voca，一个带两个音色的英文小模型，完整模型含波形生成器共 4.5M 参数，用约 18 小时的合成语音从零训练。它在四个 CPU 线程上约比实时快 70x，提供 PyTorch 权重与 ONNX 导出，权重和代码以 Apache-2.0 发布。模型卡也坦承其局限：声音偏合成感、语速略快、外来名易读错。

来源：[Hugging Face Trending Models](https://huggingface.co/n4ze3m/tiny-voca)　`模型` `语音` `开源`

## 📄 论文

### 论文：Agentic Robotics 提出 Embodied System 2 与评测框架

Grid Robotics 等作者的论文主张以 foundation model 与 embodied harness 组成的 Embodied System 2 作为 agentic robotics 的决策核心，并指出社区尚无统一评测框架与研究路线图。其闭环流程为观察环境、理解意图、推理任务、调用技能与工具、验证结果并调整策略，核心难点是在反应时间、机械限制与不可逆后果等物理约束下把通用推理转化为可验证行动。论文同时提出一套同时衡量模型能力与闭环系统表现的评测框架。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18359)　`论文` `Agent` `行业`

### 论文：AllocFlow 端到端生成加密货币永续合约组合

南洋理工大学的 AllocFlow 用端到端 flow-matching 框架，直接从原始多资产市场历史生成联合组合配置，由 cross-asset flow Transformer 统一输出各品种的连续带符号仓位权重。训练分两阶段：先做策略监督模仿形成候选组合分布，再用 group-relative RL 结合组合层面的财务奖励与冻结参考策略微调。在小时级加密货币永续合约上，RL 把模仿策略的年化净收益从 27.79% 提升到 51.38%，Calmar ratio 从 0.955 提升到 4.043。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.19937)　`论文` `训练` `推理`

## 🛠 开源与工具

### OpenSRE：可自托管的 CI/CD 可靠性 Agent

Tracer-Cloud 的 OpenSRE 是一个 CLI Agent，在 CI 失败时读取失败日志、追查原因并推送修复供人评审，同时区分 CI 引起的失败与代码引起的失败。它可连接 EKS、EC2、CloudWatch、Kubernetes、Grafana、Datadog、Slack 和 GitHub 等系统排查线上事故，并提供交互式 shell、无头 CLI 与 Python API 三种接入方式。项目目前处于 Public Alpha 阶段，API 与集成仍在演进。

来源：[GitHub Trending](https://github.com/Tracer-Cloud/opensre)　`Agent` `工具` `开源`

### AutoClip：链接进、长视频自动剪成短视频

zhouxiaoka 的 AutoClip 是开源的 AI 视频剪辑桌面工具，贴一个链接即可把播客、访谈、课程等长视频自动剪成适配抖音、小红书、TikTok、Reels、YouTube Shorts 等平台的短视频，并生成字幕、封面与发布文案。剪辑、取景与渲染在本机完成，字幕可用作者字幕、本地 Whisper / SenseVoice 或云端转写，CLI / MCP 与桌面共用同一条一键出片链路。软件本身免费、MIT 开源，云端模型按量计费。

来源：[GitHub Trending](https://github.com/zhouxiaoka/autoclip)　`工具` `视频` `开源`

### diagram-design：让编码 Agent 输出单文件 HTML + SVG 图表

cathrynlavery 的 diagram-design 是一个 Agent Skill，能把架构图、象限图、时序图等图表输出为一个自包含的 HTML + SVG 文件，并支持从站点提取配色与字体以匹配品牌。它可安装到 Cursor、Claude Code、Codex、Qoder、GitHub Copilot、Gemini CLI 等多种 Agent Skills 宿主，README 中给出的图表类型数量在不同位置分别写作 45 与 52。

来源：[GitHub Trending](https://github.com/cathrynlavery/diagram-design)　`工具` `代码` `开源`

### last30days-skill：跨 Reddit、X、YouTube 的 Agent 调研技能

mvanhorn 的 last30days-skill 是一个 Agent Skill，可并行检索 Reddit、X、YouTube、HN、Polymarket 等来源，按点赞、收藏与真实资金赔率打分，再由 AI agent 汇总成一份简报。Reddit、HN、Polymarket 与 GitHub 无需配置即可使用，安装后约 30 秒即可解锁 X、YouTube、TikTok、arXiv、Techmeme 等数据源。

来源：[GitHub Trending](https://github.com/mvanhorn/last30days-skill)　`工具` `Agent` `开源`

### app-store-compliance：提交前扫描 iOS 与 Android 拒审风险

mjmirza 的 app-store-compliance 提供开放的 App Store 与 Google Play 拒审手册，以及一个提交前检查脚本，覆盖隐私清单、Data safety 等检查点。它整理了 124 种拒审模式与对应修复方案，并跟踪 112 项合规截止日期（含 EU AI Act、DSA、COPPA 等），可安装为 Claude Code、Codex、Cursor 等编码工具的 hook。仓库也明确说明扫描结果不等于通过审核。

来源：[GitHub Trending](https://github.com/mjmirza/app-store-compliance)　`工具` `代码` `安全`
