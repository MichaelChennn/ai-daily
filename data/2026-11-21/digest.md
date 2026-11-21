# 2026-11-21 · AI 晨报

## 今日要点

- Thinking Machines Lab 发布 Inkling 2 Mini：约 26B 物理参数、每 token 激活 3B 参数的多模态 MoE 模型，支持 1M-token 上下文，已提供 transformers、llama.cpp、MLX 与 SGLang 推理支持。
- Apple 发布 Depth Pro 2 并公开代码与权重，单一网络同时处理图片与视频，在原生分辨率输出兼具度量精度、边界锐利与时间一致性的深度图。
- OpenAI 公布对抗性蒸馏防护进展：内部自适应评估中，针对受保护推理链的提取攻击成功率从 54.0% 降至 0.2%。

## 🔥 头条

### Thinking Machines Lab 发布 Inkling 2 Mini 本地多模态模型

Inkling 2 Mini 是新的循环式 Transformer 模型，约 26B 物理总参数、每个 token 激活 3B 参数，是多模态 Mixture-of-Experts，支持 1M-token 上下文并接受图像与文本输入。Thinking Machines Lab 以 NVFP4 和 MXFP8 专家权重混合精度发布，并提供 transformers、llama.cpp、MLX 与 SGLang 的推理支持，适合本地部署。

来源：[Hugging Face Blog](https://huggingface.co/blog/inkling2mini) · [Hugging Face Trending Models](https://huggingface.co/thinkingmachines/Inkling-2-Mini)　`模型` `多模态` `开源`

### Apple 发布 Depth Pro 2 单目深度估计模型

Depth Pro 2 用一个可扩展网络同时处理图片和视频，在原生分辨率预测稠密度量深度，输出既在物体边缘锐利、又在帧间保持稳定。官方同时开放了代码与权重，该模型家族在度量精度、锐度、时间一致性和运行时间上构成新的 Pareto 前沿。

来源：[Apple Machine Learning Research](https://machinelearning.apple.com/research/depth-pro-2-monocular) · [Hugging Face Daily Papers](https://huggingface.co/papers/2611.26603) · [Hugging Face Trending Models](https://huggingface.co/apple/DepthPro2)　`论文` `多模态` `图像` `开源`

### OpenAI 公布对抗性蒸馏防护与推理链提取防御

OpenAI 说明其对抗性蒸馏防护体系，结合对抗测试、模型训练、分类器、API 级保护以及对协同提取活动的调查。在内部自适应评估中，针对受保护推理链的提取攻击成功率从原有防护下的 54.0% 降至更新防护后的 0.2%。

来源：[OpenAI News](https://openai.com/index/combatting-adversarial-distillation)　`安全` `模型` `行业`

### 腾讯开源 WeMM-Video 全模态视频理解模型家族

WeMM-Video 是中英双语的全模态基础模型家族，包含 2B、4B、9B 和 35B-A3B 变体，统一处理文本、图像、音频和视频，并同时提供非思考的 instruct 模式与显式逐步推理的 thinking 模式。团队公开了模型、评测与复现流水线，其中 WeMM-Video-35B-A3B 在全模态视频评测中确立开源最优表现，WeMM-Video-9B 超过更大的开源 Qwen3-Omni-30B-A3B-Instruct。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26409)　`模型` `多模态` `视频` `开源`

## 🧠 模型

### Anthropic 完成 IPO，募资总额约 119.5 亿美元

Anthropic 宣布完成首次公开发行，合计 1,127,000,000 股 A 类普通股，公开发行价 $83.00 每股，承销商全额行使了额外购买 147,000,000 股的选择权。发行总毛收入约 $93.5 billion，其中约 $91.6 billion 由 Anthropic 获得；连同向 AMD、Broadcom、Google、Micron、Microsoft、NVIDIA 和 TSMC Partners 私募发行 Class N 普通股，合计约 $119.5 billion。A 类普通股于 11 月 19 日开始在 Nasdaq 交易，代码为 “ANT”。

来源：[Anthropic News](https://www.anthropic.com/news/ipo-close)　`行业` `产品`

## 📄 论文

### WeVisForensics：自进化 Agent 检测 AI 生成视频

WeVisForensics 是一个 Agent 框架，由主调查 Agent 协调覆盖视觉与音频线索的自进化取证子 Agent，负责决定检查哪类伪影、检查哪个时间窗口以及何时下结论。配合双时间尺度强化学习策略 DTPO 和新标注数据集 ForenCue-30K，该方法在域内、域外与 Agent 基准上平均检测准确率达到 95.2%，比最强已有检测器高 9.0%，并能给出局部化的证据。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21373)　`论文` `Agent` `视频` `安全`

### Mind2Act World：分离推理与执行的具身诊断基准

Mind2Act World 包含 30 个来自五个真实应用领域的仿真操作任务，每个任务设三个难度等级和 Clean、Random 两种场景设置，共 180 种配置，分为 Mind、Act 与 Mind2Act 三个视图，用于判断系统是缺少某种能力还是无法把已有能力组合起来。评测显示最强的 Agent 在 Mind 上成功率为 52.7%、Act 上为 39.0%，但在需要闭环组合的 Mind2Act 上只有 12.0%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26444)　`论文` `Agent` `多模态`

### NVIDIA 提出 Posterior Matching Distillation 扩散蒸馏方法

Posterior Matching Distillation（PMD）通过匹配指数重加权的学生样本均值与教师后验均值，在不依赖额外学生打分网络的前提下监督整个条件分布，并支持在训练时间步网格内任意步数采样，无需额外训练。在 SDXL 和 FLUX.2 [klein] 4B 上，PMD 在两个模型上都取得了 4-step 方法中最好的 FID，同时在提示词对齐与感知质量指标上保持有竞争力或领先的表现。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26629)　`论文` `图像` `视频` `训练`

### Coda-DaVinci：用 Code2Video 与 3D 代理控制视频生成

Coda-DaVinci 是一个面向 Code2Video 的任务自适应 Agent 框架，在代理引导生成与直接生成之间切换，按实体调整建模粒度，并协调物理模拟与基于代理的提示词。它的多 Agent harness 会保留场景资产，并通过视觉检查和独立评审指导修复；实验显示其在 VTR 指令遵循和 R2M 场景一致性上领先，物理合理性优于直接生成，视觉真实感高于所对比的 Code2Video 基线。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26595)　`论文` `视频` `Agent`

### RL 后训练对扩散 Transformer 相当于激活引导

这项工作用一组固定的 steering vectors 加到冻结基座模型的 block 输出上，探究扩散 Transformer 的 RL 后训练收益有多少能被与输入无关的常量偏移解释。在 SD3.5-M 上这些向量参数量比 RL 微调的 LoRA 少 65 倍（0.29M 对 18.8M），却能恢复六个 RL 图像模型 90.0-96.3% 的奖励增益，并在两个 RL 视频模型上恢复 89.8% 和 111.9%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26627)　`论文` `图像` `视频` `训练`

### HiUni 用共享骨干统一视觉理解与生成

HiUni 探索能否把预训练视觉语言模型直接扩展为统一模型，让理解与生成共用同一个语言对齐的 ViT 和 dense Transformer 骨干，只把任务相关计算限制在输出侧。为此它引入 Pixel Diffusion Head 面向像素空间优化，并设计轻量的 HiGate 通路补回视觉压缩丢失的细粒度空间细节；实验显示其平均理解得分与预训练 VLM 相近，同时在图像生成与编辑上具备有竞争力的表现。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26107)　`论文` `多模态` `图像` `开源`

### AltRA-Test：判断 LLM 评委能否替代人类标注者

AltRA-Test 是一种不要求所有条目由同一批标注者标注的统计检验，它通过 bootstrap 重采样条目、为每条抽取 k 个人工标注并把其中一个替换为 LLM 标注，构成全人工与人类-LLM 混合配对面板。当混合面板的标注者一致性在统计上不劣于全人工面板时，才支持替换。作者在文本、图像、音频和视频的 20 个数据集上测试了 18 个 LLM 和 5 种提示技巧，评估显示约 100 个条目往往就足够完成检验。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26073)　`论文` `评测` `工具`

## 🛠 开源与工具

### Claude Code v2.1.330 新增组织登录与内置图表功能

Claude Code v2.1.330 支持登录 Anthropic Enterprise Admin Console 管理的组织，登录后自动套用组织设置并使用其云服务商或网关；同时加入内置模组 easel，可在被要求时以及 MCP metrics 结果下绘制图表，可用 /config 关闭。版本还修复了长对话压缩后卡顿、WebFetch 冻结会话、并发保存用户设置丢失以及 MCP 工具 input schema 不合法导致会话文件膨胀等问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.330)　`工具` `Agent` `代码`

### Hugging Face 用 RL 训练 harness 适配器提升 Agent 表现

Hugging Face 为 Qwen3.8-27B 分别在 pi、Hermes Agent、OpenCode 三种 Agent harness 内训练 LoRA 适配器，训练数据、rollout 全部在 Hugging Face Jobs 上通过 TRL 的 AsyncGRPOTrainer、OpenEnv 和 harbor 完成。以 pi 为例，模型在 Terminal-Bench 2.1 上的 pass@1 从 39% 提升到 55%，平均每个任务 token 用量从 2.9K 降到 1.5K；三个 LoRA 还可合并成通用于三种 harness 的 super adapter，相关适配器、GGUF、RL 任务和 safeagents 插件均已开放浏览。

来源：[Hugging Face Blog](https://huggingface.co/blog/harness-adapters-at-scale) · [harness-hub/Qwen3.8-27B-opencode-adapted](https://huggingface.co/harness-hub/Qwen3.8-27B-opencode-adapted) · [harness-hub/Qwen3.8-27B-pi-adapted](https://huggingface.co/harness-hub/Qwen3.8-27B-pi-adapted)　`工具` `Agent` `训练` `开源`

### obra/superpowers：面向编码 Agent 的软件开发方法论

Superpowers 是构建在可组合技能之上的完整软件开发方法论：Agent 先通过对话澄清需求并分段展示设计，确认后再给出实现计划，然后进入子 Agent 驱动的开发流程，逐个任务实现、检查与评审。技能会自动触发，可通过 Claude Code 官方插件市场、Codex、Cursor、Gemini、Pi、Qwen Code、Hermes 等多种方式安装。

来源：[GitHub Trending](https://github.com/obra/superpowers)　`工具` `Agent` `代码` `开源`

### CLI-Anything 把常用软件变成 Agent 可用的 CLI

CLI-Anything 的目标是让任意软件都具备 Agent 原生能力，配套 CLI-Hub 可以用 pip install cli-anything-hub 后通过 cli-hub install <name> 浏览并安装社区构建的 CLI。仓库中已包含 Blender、GIMP、Krita、FreeCAD、Audacity、Obsidian、LibreOffice、Ollama 等大量软件的 agent-harness 适配目录，并可通过一条命令接入 Pi、OpenClaw、nanobot、Cursor、Claude Code 等 harness。

来源：[GitHub Trending](https://github.com/HKUDS/CLI-Anything)　`工具` `Agent` `开源`

### Firecrawl 推出可本地运行的 Firecrawl Local

Firecrawl Local 以单一二进制在本机完成网页转 Markdown、爬取与站点地图，无需数据库、队列或容器，并可作为 MCP 服务器接入 Claude Code、Claude Desktop、Cursor、Windsurf、Gemini CLI 与 Codex。它的 serve 命令在端口 3002 上提供 Firecrawl v2 API，本地路由无需 API key；需要搜索或 Alexandria 的 550+ 数据源时可切到 Firecrawl Cloud。

来源：[GitHub Trending](https://github.com/firecrawl/firecrawl)　`工具` `Agent` `开源`

### OpenSRE：可自托管的 CI/CD 可靠性 Agent

OpenSRE 是一个 CLI Agent，读取失败的 CI 运行记录、追踪原因并推送待你审核的修复，可自托管并使用自己的模型。它会区分 CI 导致的失败与代码导致的失败，在工具调用循环中跨多个系统验证假设，并可把摘要直接发到 Slack、PagerDuty 或 Telegram。项目目前处于 Public Alpha，核心流程可用但尚不完全稳定。

来源：[GitHub Trending](https://github.com/Tracer-Cloud/opensre)　`工具` `Agent` `开源`

### AutoClip：链接转短视频的开源桌面剪辑工具

AutoClip 是一个开源 AI 视频剪辑桌面工具，贴一个链接即可把播客、访谈、课程等长视频自动剪成短视频，并生成字幕、封面和发布文案，适配抖音、小红书、TikTok、Reels、YouTube Shorts 等平台。剪辑、取景与渲染在本机完成，字幕可选作者字幕、本地 Whisper / SenseVoice 或云端转写，桌面、CLI 与 MCP 共用同一条一键出片链路。

来源：[GitHub Trending](https://github.com/zhouxiaoka/autoclip)　`工具` `视频` `多模态` `开源`

## ⚡ 快讯

- **ZeroVLN：不做导航域 SFT 的慢-快导航框架** ZeroVLN 用语义工具调用接口把移动决策以自然语言传给 action expert，再通过闭环 RL 联合优化两者，在 VLN-CE 基准上超过基于 SFT 的分层方法，同时只让 VLM 权重发生 0.01497% 的相对位移。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.26414)
- **为 LLM 权重编程准备视觉模型** 该基准让五个 LLM 直接编辑视觉模型完成重标注与纠错任务，报告超过 2,600 次编辑过程；Edit-Ready Training 预先演练闭式权重编辑，在 GPT-6 Astra 和 Claude Opus 5.5 上取得最高平均分。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.26408)
