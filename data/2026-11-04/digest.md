# 2026-11-04 · AI 科技日报

## 今日要点

- agent 框架与评测密集涌现：CoworkOS 用分层运行时做长周期协作，CUA-Master、NorthCUA 与 ReTRACE 分别从数据飞轮、经验闭环和失败恢复切入计算机使用智能体。
- 视频生成走向实时与长时一致：Wave Forcing 提出流式生成与执行协同设计，History Forcing 用历史残差修正蒸馏目标。
- Claude Code v2.1.318 修复多项会话、认证与配置写入问题，并为 mantle 上游加入 assume_role 与 mod 的 effort 选项。

## 🔥 头条

### CoworkOS 把长期工作拆成策略与执行两层

中国人民大学团队提出通用长周期工作框架 CoworkOS，把任务策略与执行管理分离：模型决定动作、委派与验收，运行时维护状态和反馈。三层架构支持直接执行或委派给 Subagents，并借助分层工作区与持久语义记忆让工作文件、关键决策和长时间 Job 日志可共享、可恢复。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03178)　`Agent` `论文` `工具`

### CUA-Master 用嵌套双循环扩展计算机使用智能体

CUA-Master 提出系统层与数据层嵌套的递归改进框架：外层持续引入开放世界语料并利用模型弱点指导迭代，内层从教学视频挖掘种子任务并将其转化为可复用的可验证任务原语。它还引入反馈引导的快照回滚重试机制以稳定采集轨迹。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03126)　`Agent` `论文` `训练`

### Wave Forcing 让流式视频生成跑出 147.6 DiT FPS

Wave Forcing 协同设计生成、训练与执行流程，用分块因果注意力在早期分块去噪完成前读取其更干净的状态，并在完整模型副本间错开去噪与缓存刷新以实现 1F1C。配套的 Wave Runtime 用 Wave Parallelism 提前投递 K/V 并重叠通信与计算，在八块 H200 上 4-step WF 达到 147.6 DiT FPS 和 134.8 端到端 FPS。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.00859)　`视频` `论文` `推理`

### Claude Code v2.1.318 修复会话与配置写入问题

Claude Code v2.1.318 新增 mantle 上游的 assume_role（支持跨 AWS 账号角色与按开发者归集成本）、mod 的 $.model.fork effort 选项，并把登录过期时间写入 claude auth status 与 claude -p JSON 结果。版本还修复了 --continue 丢失早前对话、macOS 上大量 Bash 命令卡死、共享网络目录配置写入失败等问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.318)　`工具` `代码`

## 🧠 模型

### NorthCUA 用经验飞轮训练计算机使用模型

NorthCUA 以 Experience Flywheel 提供可执行任务，由 Harness 维持长交互、记录决策并核验结果，再据此筛选已验证轨迹；未解决任务则通过递归自我改进演化可复用技能并保留已验证里程碑。训练端结合中训与长周期监督微调以及桌面-网页联合强化学习，产出 Nano、Mini 和 Pro 三个规模。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.02102)　`Agent` `模型` `训练`

### colibri 在本机分层运行超大 MoE 模型

colibri 是用 C 编写的分层推理引擎：热点专家放在 GPU（支持 CUDA、Vulkan），温层放 RAM，冷层从 NVMe 流式读取，可在不持有整台模型的前提下运行大参数 MoE。仓库当前提供十种语言模型引擎与 Qwen-Image-2.1 图像引擎，最低需要 8 GB 内存，显卡为可选，并暴露 OpenAI 与 Anthropic 兼容的 base URL。

来源：[GitHub Trending](https://github.com/JustVugg/colibri)　`模型` `开源` `工具`

## 📄 论文

### StateBench 划分四级长文档状态跟踪难度

StateBench 基准用四个难度层级衡量语言模型在长文档中跟踪实体状态变化的能力，层级越高越依赖链式更新。测试显示，Gemini 3.8 Flash、Claude Opus 5.5 和 GPT-6 Sol、Luna 在最难的一般有限问题上随输入变长准确率降至 13% 或更低；直接在任务上训练时，Gated DeltaNet 与混合模型在 r-trivial、aperiodic 和 soluble 上几乎完美泛化，Transformer 则始终学不会一般有限问题。

来源：[Hugging Face Blog](https://huggingface.co/blog/allenai/statebench)　`论文` `推理` `训练`

### FLAMIA 为 Blackwell 上的低比特注意力加速

FLAMIA 是面向 NVIDIA Blackwell 的注意力内核家族，提供 MXFP8 与混合 NVFP4/FP8 训练路径，通过 token 分块缩放复用量化操作数，并加入防缩放信息泄漏的机制。在多种因果打包文档负载下，MXFP8 路径相对各负载最快基线，在 B200 上加速 1.10–1.40 倍、在 B300 上加速 1.06–1.42 倍。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03344)　`论文` `训练` `硬件`

### CrossSWE 评测跨仓库联合开发

CrossSWE 基准包含来自 165 个仓库、20 个技术领域和 13 种编程语言的 171 个真实任务，要求 coding agent 在多个相互依赖的仓库间协调改动。五个 LLM 的评测显示，最强的 GPT-6.1 Sol 仅取得 58.48% Pass@1，跨仓库不一致是最主要的失败模式，占 44.2%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.01484)　`论文` `代码` `Agent`

### SWE-Trail 用历史轨迹指导采集但不进上下文

蚂蚁集团提出轨迹采集器 SWE-Trail，用早期轨迹决定后续采集投入的位置，同时把历史留在 coding agent 上下文之外，避免模型在测试时依赖拿不到的建议。实验中，以 Ling-3.0-flash-base 初始化的 124B 学生模型，相比独立采样在 SWE-bench Multilingual 和 SWE-bench Pro 上平均解决率分别提升 2.33 和 1.60 个百分点。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.02074)　`论文` `代码` `训练`

### O³PD 只蒸馏教师 token 的排序

Order-Only On-Policy Distillation（O³PD）在学生生成的前缀上只训练学生复现教师 top-K token 的顺序，不拟合概率值，因此目标对教师温度不变且无需调温。在六组教师-学生组合上，O³PD 在 HMMT25、AIME24 和 AIME25 的平均成绩上都优于 OPD，平均最多提升 2.9 分，AIME25 上最多提升 5.6 分。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.02112)　`论文` `训练` `推理`

### ReTRACE 系统研究计算机使用智能体的恢复能力

ReTRACE 提出 Transition-Consistent Recovery：从恢复后的状态与目标状态执行相同后续动作，必须得到一致结果，并通过受控注入错误后的目标导向动作回放来操作化这一标准。基于该框架的研究首次系统考察自主的、基于模型的恢复能力，发现理想的恢复能释放模型潜在的任务完成能力，而现有智能体未能利用这种潜力。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.27954)　`论文` `Agent` `安全`

### uni-robot-agent 让开源权重模型做机器人操作

uni-robot-agent 是面向开源权重机器人使用智能体的统一 harness，支持后续训练。在没有特权输入的情况下，开箱即用的 Qwen3.8-Flash-Next 取得 31.39 的 RoboDojo Score，高于已发表的 GPT-6 Astra-RoboProbe 结果 28.97，并在 19 个真实任务上表现有竞争力。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.01560)　`论文` `Agent` `模型`

## ⚡ 快讯

- **IBM Palette 用 20B 开源权重模型生成演示文稿** IBM 微调了一个 20B 模型按 IBM Design Language 生成演示文稿，设计者与编码者由单一 LoRA adapter 承载，并在 PresentBench 三个领域中的两个排名第一。 [Hugging Face Blog](https://huggingface.co/blog/ibm-research/palette-deck-building)
- **History Forcing 用历史残差修正视频蒸馏目标** History Forcing 用教师在有无历史上下文两种预测之间的残差分离历史监督，再加权加到蒸馏所用的 score 或 velocity 预测上。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.02782)
- **Video Generation 与 Agent Harness 的交叉综述** 综述以围绕视频模型构建上下文、暴露工具、维护状态、路由反馈并管理预算的可执行运行时为主线，梳理三个研究方向。 [Hugging Face Daily Papers](https://huggingface.co/papers/2610.40191)
- **Collaborative Intelligence Benchmark 测 AI 当队友** 该基准用 240 个任务、8 个团队协作维度衡量 AI 智能体作为队友的表现，任务结果可程序化验证。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.02633)
