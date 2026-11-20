# 2026-11-20 · AI 晨报

## 今日要点

- Google 在 Gemini API 预览 Tool Retrieval，让 Agent 按需加载工具参数 schema，减少大工具库的输入 token 与延迟。
- Codex 0.171.0 与 Claude Code v2.1.329 同期更新，前者加入 GPT-6.2 Sol/Astra 模型目录与远程会话，后者补上 Code Mode 的 OpenTelemetry 支持。
- 论文方面，Jeveration 用单次前向生成 512x512 图像，Piccolo 家族用递归自我改进训练多模态决策模型，AnyS1 用小模型接管 Agent 的常规决策点以降低成本与延迟。

## 🔥 头条

### Gemini API 预览 Tool Retrieval，按需加载工具 schema

Google 在 Gemini API 的 Interactions API 中推出预览版 Tool Retrieval：Agent 保留完整工具库，只在需要时由模型按名请求、API 再加载对应参数 schema，搜索过程在服务端完成。开发者可在请求中加入 tool_search 并对要延后加载的工具设置 defer_loading: true，从而减少输入 token 与延迟，也兼容远程 MCP 服务器。

来源：[Google AI Blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/)　`Agent` `工具` `产品`

### Codex 0.171.0 加入 GPT-6.2 Sol 与 Astra 模型

openai/codex 0.171.0 把 GPT-6.2 Sol 和 Astra 加入模型目录，其中 Sol 为默认目录选项，TUI 工作区也默认开启，可搜索文档预览、查看图片预览和 subagent 转写。新增 codex exec --remote 与 /rc、/remote 命令，用于在已有 app server 上启动或恢复非交互会话、管理本地远程控制。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.171.0)　`工具` `代码`

### Claude Code v2.1.329 支持 Code Mode 接入 OpenTelemetry

anthropics/claude-code v2.1.329 允许在启用 OpenTelemetry 事件与指标时同时打开 Code Mode，代码每次发起的工具调用都会发送对应事件，而 tracing 仍保持关闭。新版本还把本次会话的定时任务、/loop 唤醒、goal 和会话分支并入 /tasks，并在 /mcp 中为拒绝连接的远程 HTTP MCP 服务器增加 Server message 一行。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.329)　`工具` `代码`

### Jeveration：单次前向生成 512x512 图像

Jeveration 复用冻结的视觉语言模型，把 System One 的并行决策范式用于图像生成：所有位置以共享随机状态为条件以保证整体一致性，并先学习离散图像码分布来引导单次前向生成。论文报告 512x512 图像生成耗时 78 ms，最快比已有统一模型快 122x，同一 checkpoint 还支持图生图与稠密预测。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.24738)　`论文` `图像` `多模态`

## 🧠 模型

### Piccolo：用递归自我改进训练多模态决策模型

Piccolo 是一族 0.8B 到 27B 的多模态决策模型，通过 Agentic Data Engineering 与递归自我改进（RSI）让模型与训练数据协同演进，输出候选答案的概率。Piccolo-27B 在 Decision Index Vision Full 榜单以 75.59 分居首，Piccolo-9B 与 Piccolo-4B 分别取得 68.35 和 67.46，权重与 Data-Juicer、AgentScope 工具一并发布。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.24651)　`模型` `Agent` `训练`

### Microsoft 开源 Aion-1.0-Instruct-2.3B 端侧小模型

microsoft/Aion-1.0-Instruct-2.3B 是 Microsoft Windows Applied Sciences Group 面向端侧场景的 2.3B 参数小模型，采用 MIT 许可发布，支持英语、德语、西班牙语等语言，上下文窗口 32K tokens。模型卡称其未被训练以精通世界知识，也不适合高风险决策场景，量化版本将在未量化权重之后发布。

来源：[Hugging Face Trending Models](https://huggingface.co/microsoft/Aion-1.0-Instruct-2.3B)　`模型` `开源` `行业`

### Inworld 开源 48 kHz 人声分离模型

Inworld 发布 voice-isolator v1，采用 Apache-2.0 许可，包含离线与实时两个 checkpoint：离线模型每帧可见完整 8 s 区块，实时模型是因果流式、带 20 ms 前瞻，在 20 ms 前瞻下算法延迟为 63 ms。它用于从含噪录音或实时音频中分离人声并保留说话人身份，可配合 pip install inworld-voice-isolation 在本地运行。

来源：[Hugging Face Trending Models](https://huggingface.co/inworld/voice-isolator)　`模型` `语音` `开源`

## 📄 论文

### AnyS1：用 4B 小模型接管 Agent 的常规决策点

AnyS1 把人写的流程技能文档转成通用的决策点来源，离线阶段挖掘超过 1,000 个公开技能中的可枚举决策并训练一个校准过的 4B 指针式 System-1 模型。运行时常规决策由该模型一次前向解决，置信度低于校准阈值时回退到 System-2，在三个未见过基准上相对未编译的 System-2 Agent 将回合成本降低 75-91%、模型调用时间降低 63-92%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.23751)　`论文` `Agent` `推理`

### 分辨率假说：Agent 演化的瓶颈在识别改进

论文提出 Resolution Hypothesis：Agent 演化停滞并非因为无法提出更好的产物，而是噪声过大的评测无法可靠识别改进。在七种演化方法、六个模型和超过 10M 次 LLM 调用中，候选层面挑选好产物的能力并不优于随机，方法层面几个百分点的差距小于同一方法两次独立运行的差距。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.23068)　`论文` `Agent` `推理`

### ALIVE：让流式视频模型具备主动交互能力

ALIVE 是交互式流式视频模型，支持主动监控、流式任务协调与主动追问三类能力。作者构建 ALIVE-SFT-288K 与 ALIVE-RL-3K 做两阶段训练，用 Behavior-Aligned Credit Assignment（BACA）结合轨迹级与局部优势来优化多轮交互中的决策、回复与沉默，并提出 FSI-Bench 评估追问行为。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21366)　`论文` `视频` `多模态`

### CurvDelta：在低曲率空间做能力学习与遗忘

CurvDelta 把能力保持约束直接写进模型更新的参数化，通过分析保持约束在预适配模型附近的局部几何，构建参数更新几乎不改变保持损失的低曲率空间。它借助 Kronecker-factored approximate curvature（K-FAC）与因子化投影落地到 LLM，并给出同几何下的低秩变体 CurvLoRA，用于数学推理、代码生成与知识遗忘等任务。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.24654)　`论文` `训练` `安全`

### Code World Model 2.0：四步流式可控视频生成

Invoker-Render 是 Code World Model 2.0 背后的视频渲染器，把双向创作模型与因果四步流式模型配对，共享结构代理、外观参考与语言的条件接口。训练先用 Progressive Forcing 将因果预测器蒸馏为四步渲染器，再转向连续自生成 rollout 以减少漂移，论文报告稳定 30 分钟的赛车演示中场景与车辆保持一致。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.22925)　`论文` `视频` `多模态`

### LogT：用自动 SFT 数据引擎训练图像缩放推理

LogT 是自动化的 SFT 数据引擎，生成带逻辑链引导的难题、结构化工具使用轨迹，目标是让视觉语言模型在放大细节时兼顾逻辑推理与工具效率。作者用 LogT-SFT 微调 Qwen2.5-VL-7B，报告其表现超过同时用 SFT 与 RL 训练的现有方法，数据量少 3.1 倍、GPU 小时少 120 倍；该工作被 NeurIPS 2026 接收。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.19200)　`论文` `多模态` `Agent`

## 🛠 开源与工具

### Thorizer 进入 Asta 并开放源码

Ai2 在 Asta 平台推出 Theorizer 并开源其代码，该 Agent 检索科研文献、抽取证据并生成待检验的解释，每个解释都关联到已发表研究的证据并说明适用范围。研究者既可通过 Asta 网页界面使用，也可在本地运行其开源库并自行承担 token 费用，Ai2 同时提醒搜索可能遗漏早期工作、模型也可能误判原创性。

来源：[Ai2](https://allenai.org/blog/theorizer-in-asta)　`工具` `论文` `开源`

## ⚡ 快讯

- **WorldRuler：可配置规则驱动的交互式世界模型** WorldRuler 把规则定义、依赖关系与物体状态组织成可执行的 3D 规则图，把规则执行、视频生成与感知反馈连成闭环，支持规则与世界状态的联合存取与恢复，并用 RuleVerse 数据集覆盖规则先于受影响物体出现的情况。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.24869)
- **StrideWorld：交互式视频世界模型的刚性与动作一致性基准** StrideWorld 在运动开始前固定评测参考，用起始视角的真值几何衡量场景刚性，用每个动作自身的步长衡量动作一致性，其测量在已知相机运动的渲染视频上验证并与人类判断一致。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.24408)
