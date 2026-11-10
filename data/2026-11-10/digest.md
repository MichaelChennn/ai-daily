# 2026-11-10 · AI 科技日报

## 今日要点

- 字节跳动 Seed 发布 Seedream 5.5，主打 100 轮多轮编辑下的像素级未编辑区域保持，并加入原生 RGBA 输出。
- 美团 LongCat-2.5 开源，1.6 trillion 总参数、约 48 billion 每 token 激活的原生多模态 MoE，面向长程智能体任务。
- 多项工作把智能体能力推向真实工程与部署：Codex SSH agent 转发暴露凭据风险，sentinel-eval 复现 Agent 记忆写入路径的 ACL 泄漏。

## 🔥 头条

### 字节跳动发布 Seedream 5.5 图像模型

Seedream 5.5 带来三项升级：未编辑区域在像素级保持、跨 100 轮编辑仍稳定；原生 RGBA 输出可直接生成带透明背景的素材；写实与小字渲染改进。官方称其在文本结构与文生图写实性上取得领先结果，创作者可把生成结果直接用于排版与合成流程。

来源：[ByteDance Seed](https://seed.bytedance.com/en/blog/more-realistic-images-more-stable-editing-across-100-rounds-introducing-seedream-5-5)　`模型` `图像` `产品`

### 美团开源多模态 MoE 模型 LongCat-2.5

LongCat-2.5 是面向长程智能体任务的原生多模态 MoE 模型，总参数 1.6 trillion，每 token 约激活 48 billion 参数，视觉特征与文本在共享语义空间对齐。模型卡列出 Terminal Bench v4.0、DeepSWE (v1.1) 等编码与智能体评测成绩，并提供 W4A4 量化与 NPU 部署方案。

来源：[Hugging Face](https://huggingface.co/meituan-longcat/LongCat-2.5)　`模型` `开源` `多模态` `Agent`

### Claude Fable 5.2 可端到端设计电子设备

Anthropic 与 Diode Computers 合作，让 Claude Fable 5.2 从简短提示出发完成电路板布局、CAD 建模、固件编写与物料清单，并指导人类工程师做出无需修改电路即可工作的原型。Diode 的内部基准 PCB Gym 上 Fable 5.2 得 69%，对比 Fable 5 的 25%；公开基准 BenchCAD 2.1 得 83.5%。作者也提醒，这些仍是早期原型，能否长期耐用或通过商业认证尚不清楚。

来源：[Anthropic Research](https://www.anthropic.com/research/claude-electronics-design)　`行业` `工具` `Agent`

### Codex SSH agent 转发让远程代理获得本地凭据

openai/codex 的 PR #28131 提出为 app-server proxy 增加 --forward-ssh-agent 选项，在 SSH 会话退出后刷新转发 agent 的符号链接。其评审指出，内置 daemon 路径不会设置 SSH_AUTH_SOCK，因此用旧 socket 启动的 daemon 仍可能使用失效凭据；该 PR 已因长期无更新被关闭。

来源：[GitHub](https://github.com/openai/codex/pull/28131#discussion_r3410013180)　`安全` `工具` `Agent`

## 🧠 模型

### 网易有道开源稳定前缀流式 ASR 模型

Confucius4-R2T2（Real Real-Time Transcription）通过 Longest Stable Prefix 学习，把 Qwen3-ASR-1.7B 改造为不修改已输出文本的流式识别模型，冻结预训练音频编码器与投影层。它在 1,500 小时中英文音频上做后训练，评测显示流式识别接近基线的全上下文质量，同时保持低输出延迟，模型权重与代码均已公开。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.06043)　`模型` `开源` `语音`

### SplatAnything 用高斯间距归一化改进前馈 3DGS

SplatAnything 指出前馈 3D 高斯泼溅方法的局限：属性在径向距离归一化空间预测，但相邻高斯中心的间距仍随场景尺度与相机配置变化，导致监督目标偏移。论文提出 Gaussian Spacing Normalization（GSNorm），用鲁棒的场景级间距统计量统一空间参照，并建立覆盖多种数据集与外推视角的基准。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08264)　`论文` `图像` `3D`

## 📄 论文

### P²-MOPD 用参数先验加速多教师在策略蒸馏

P²-MOPD 把学生权重与冻结专家参数的线性组合视为一个可微模型，在同一在策略蒸馏目标下联合优化混合系数与学生权重，专家因此充当参数先验而非只提供 logits。论文在 1.7B 与 4B 规模上报告：1.7B 模型的平均恢复率达 94.7%，MOPD 为 80.9%；4B 为 94.9% 对 83.1%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03953)　`论文` `训练` `模型`

### Video-Coder 用代码驱动视频生成智能体

Video-Coder 是一个代码驱动的视频生成智能体，自主编写并执行代码构建动态 3D 场景（Draft Video），再把结构与运动信号交给下游视频生成器。训练采用 SFT 后接 harness 原生的智能体强化学习，奖励融合执行反馈与视频反馈，并配套 Video-Coder-SFT-6k、Video-Coder-RL-2k 数据集与 Video-Coder Harness。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.09894)　`论文` `Agent` `视频` `代码`

### LongBanana 评测长上下文多参考图生成

LongBanana 是面向长上下文多参考图合成的专家设计与专家校验基准，要求模型从分散的视觉证据中检索、排除干扰项、绑定实体与关系，再合成一张连贯图像。基准含 90 个任务、约 4,670 条专家原子评测项，基于实体关系图把节点、边与全图约束转为检查项，并配套 LongBanana-Gen 智能体框架。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.06856)　`论文` `评测` `图像` `Agent`

### EvoWorld 让视频模型推演视野外世界演化

EvoWorld 提出 Out-of-Sight Causal Evolution 问题，要求视频模型在渲染事件后推理其对世界状态的影响，并呈现视野外合理的因果结果。其参考方案由视觉语言模型充当 world brain，观察生成片段、维护演化中的世界状态并推理状态转移，再由分段自回归视频渲染器实现画面，同时配套 EvoWorld-Data 与 EvoWorld-Bench。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.06748)　`论文` `视频` `推理` `Agent`

### A2-MEAS 用修正代码提升机器人失败恢复

A2-MEAS 是以代码为扩展接口的具身多智能体框架，学习到的修正代码结合纠正性语言、空间证据、执行历史与动作提议，MetaBrain 负责训练监督与运行时引导。其动作模型 A2-WLA 在视觉-语言-动作策略上加入运动感知历史与潜在世界模型，在 BEHAVIOR 2026 公开任务上取得 0.6411 Q-score 与 45.40% 任务成功率。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.09124)　`论文` `Agent` `推理`

### PCBRouteAgent 让智能体接手 PCB 布线

PCBRouteAgent 是多模态 PCB 布线智能体：Global Routing Planner 依据板图与电气几何信息给出连接拓扑、布线顺序、通道与换层策略，Detailed Routing Executor 通过 KiCad 原生布线引擎落地并做有界局部恢复，未解决的失败以结构化反馈返回。论文在 247 块合成与真实板子上评测，D3-C 子集 clean-pass 率为 40%，作者也指出全局规划仍是瓶颈。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08175)　`论文` `Agent` `工具` `代码`

### 低秩键与摊销值实现可组合 KV 缓存压缩

LowRAM 发现同一注意力头内的 value 大多可由对应 key 预测，于是用测试时的轻量 per-head 预测器摊销 value 缓存，仅为最难重建的 token 保留残差，得到 4times 近无损的 value 压缩。再配合跨层低秩 key 压缩，论文报告在 4times 压缩下峰值解码吞吐最高提升 5times，与量化、淘汰组合可达 26.9times 压缩。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.07025)　`论文` `推理` `工具`

### FinDendro 检验模型是否已知金融回测答案

FinDendro 用 2,226 条 1999 到 2026 的美国金融事实检验模型的时间自知识，涵盖月度宏观序列、月末股价与美联储决议。GPT-5 答对 76% 的受控事实，却只声称知道 38%，并能答对自己声称不知道的事实中的 61%；论文因此认为自述、指令或厂商声明的截止日期都无法为训练窗口内的回测提供无泄漏保证。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.06808)　`论文` `评测` `行业`

## 🛠 开源与工具

### sentinel-eval 复现 Agent 记忆写入路径 ACL 泄漏

sentinel-eval 是一个确定性离线基准与 linter，用 24 篇文档（18 公开、6 受限）检验派生上下文中的 ACL 泄漏。ChromaDB 与 LlamaIndex 下原始 RAG 查询泄漏率为 0%，但跨文档摘要写入共享记忆后 2/3 派生工件失败，泄漏 6/18 个受限 canary；项目指出授权应落在数据层，并解释严格 ACL 交集等常见修补为何会摧毁多源可用性。

来源：[GitHub](https://github.com/harishbalasubramanian/sentinel-eval)　`安全` `工具` `Agent` `开源`

### Twindex 用可重放证书证明数据无法定参

Twindex 面向 ODE 与 PDE 反问题，找出能同样拟合测量数据的「孪生参数」，并输出标准库 Python、无浮点运算的精确证书，可重放为 VALID、INVALID 或 INCONCLUSIVE。VALID 表示在声明的有界噪声假设下，任何估计器都无法把该参数恢复得比参数间距的一半更好；检查器约 5,700 行并通过 mypy --strict 类型检查。

来源：[GitHub](https://github.com/Arnav-M10/Twindex)　`开源` `工具` `推理`

## ⚡ 快讯

- **Agent 进化评测：16 个进化体都在丢任务** 论文评估四种智能体 harness 进化方法，16 个进化体全部拿下原本未覆盖的任务、同时丢掉原本覆盖的任务。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.07624)
- **AgentBaton 用模型接力降低 API 成本** AgentBaton 检测器在 11 组模型配对、两个基准上平均降低 65.9% 的 API 成本，准确率最高提升 8.8 个百分点。 [Hugging Face Daily Papers](https://huggingface.co/papers/2610.35959)
- **结构感知内核加速相对位置注意力** 在 8K token 序列上，该算法前向加速 1.8-6.4times、反向 2.0-21times。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.01182)
- **Claude Code v2.1.321 上线 Fable 5.2 与多项修复** claude-code v2.1.321 把 Claude Fable 5.2 设为默认 Fable 模型，支持 1M context。 [anthropics/claude-code v2.1.321](https://github.com/anthropics/claude-code/releases/tag/v2.1.321) · [anthropics/claude-code v2.1.322](https://github.com/anthropics/claude-code/releases/tag/v2.1.322)
