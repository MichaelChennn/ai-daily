# 2026-11-10 · AI 科技日报

## 今日要点

- Anthropic 发布 Claude Fable 5.2 与 Mythos 5.2，价格为每百万 token 输入 $8、输出 $40，Artificial Analysis Intelligence Index 给出 65 分。
- 美团以 MIT License 开放 1.6T 参数的多模态 MoE 模型 LongCat-2.5；字节 Seed 发布 Seedream 5.5，支持 100 轮连续编辑和原生 RGBA 输出。
- 两篇论文给热门方向泼了冷水：weight-space programming 的收益不稳定，不少编辑轨迹最后只能保留原始权重；进化后的 agent 在多做对一些任务的同时，也会做错原本能做对的任务。

## 🔥 头条

### Anthropic 发布 Claude Fable 5.2 与 Mythos 5.2

Fable 5.2 和 Mythos 5.2 是同一个底层模型：Fable 带网络安全和生物安全防护、向所有用户开放，Mythos 需通过 Cyber / Life Sciences Verification Program 申请；输出速度比 5.1 快至多 30%，价格为每百万 token 输入 $8、输出 $40，在 FrontierCode 2.0 上以 Xhigh effort 达到 49.1%（Opus 5.5 为 45.5%）。Claude Code v2.1.321 已把 claude-fable-5-2 设为默认 Fable 模型（1M 上下文），Artificial Analysis 给出 65 分、排名第一，但也显示它每道题平均花 $26.54、耗时 46.4 分钟，更适合难度高的长任务，日常调用要算好成本。

来源：[anthropic.com](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [HN 讨论](https://news.ycombinator.com/item?id=50429906) · [GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.321) · [artificialanalysis.ai](https://artificialanalysis.ai/models/claude-fable-5-2) · [Ethan Mollick](https://www.oneusefulthing.org/p/fable-52-and-jagged-agi)　`模型` `产品` `Agent`

### 美团以 MIT License 开放多模态 MoE 模型 LongCat-2.5

LongCat-2.5 是面向长程 agent 任务的原生多模态 MoE 模型，总参数 1.6T、每个 token 激活约 48 billion，在 LongCat-2.0 基础上把视觉理解和 agentic coding 结合起来；模型卡给出的 Terminal Bench v2.1 为 88.4（LongCat-2.0 为 70.8），BrowseComp 为 91.9。权重用 MIT License，商用限制少，但这个规模自部署门槛很高。

来源：[Hugging Face](https://huggingface.co/meituan-longcat/LongCat-2.5) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xrsptp/meituanlongcatlongcat25_hugging_face/)　`模型` `开源` `多模态`

### 字节 Seed 发布图像生成模型 Seedream 5.5

Seedream 5.5 在多轮编辑时按像素保留未编辑区域，演示中对同一张图连续编辑 100 轮；还能直接生成带 alpha channel 的 RGBA 图像，支持完全和部分透明；在覆盖中英文（含密集小字）的评测中，文字严重错误率降到 0.4%、轻微错误率 1.7%。对做设计素材和海报的开发者来说，透明底元素可以直接进下游流程，不用再单独抠图。

来源：[ByteDance Seed](https://seed.bytedance.com/en/blog/more-realistic-images-more-stable-editing-across-100-rounds-introducing-seedream-5-5)　`图像` `模型` `产品`

### Claude Fable 5.2 设计三款电子设备，原型未改电路即可工作

Anthropic 让 Claude Fable 5.2 从简短提示出发设计免提电话、语音助手中枢和掌上电子宠物，Diode Computers 按它的文件做出了能用的原型；在 Diode 的 PCB Gym 上它得到 69%，Fable 5 为 25%。原文也说明三款设备仍是原型，没做电气验证、热测试和认证，适合当作硬件设计 agent 能力的参考，而不是量产流程。

来源：[Anthropic Research](https://www.anthropic.com/research/claude-electronics-design)　`Agent` `硬件` `代码`

## 🧠 模型

### 网易有道开放流式语音识别模型 Confucius4-R2T2

Confucius4-R2T2 在 Qwen3-ASR-1.7B 上用 1,500 小时中英文音频做后训练，输出的文字一旦给出就不再修改，解码块可在 80 ms 到 2 s 之间配置；代码用 Apache License 2.0，权重用 NetEase Model Use License Agreement。给语音 agent、同声传译这类边听边执行的下游用，可以少处理被撤回的 token。

来源：[Hugging Face](https://huggingface.co/netease-youdao/Confucius4-R2T2) · [Hugging Face Daily Papers](https://huggingface.co/papers/2611.06043)　`语音` `模型` `开源`

### Opper 直接改写 Qwen3.5-4B 权重，做出 Pac-Man 决策模型 Jevlar

Jevlar 不用梯度下降训练，而是根据记录的激活直接计算并改写 Qwen3.5-4B 0.69% 的权重，在 Opper 的 JevMan 基准上 100 局得分 3604，高于所有模型参赛者，低于手写的贪心规则（4450），GPU 花费约 $50。改动、每一轮的 notebook 和 100 局录像都已公开，可以当作 weight-space programming 的完整实操案例来读。

来源：[opper.ai](https://opper.ai/blog/jevlar-weight-space-programming)　`模型` `训练` `开源`

## 📄 论文

### PCBRouteAgent：用 LLM agent 调度 KiCad 完成 PCB 布线

PCBRouteAgent 由全局规划器结合板图和电气、几何信息定好拓扑、顺序和走线通道，再交给 KiCad 原生布线引擎执行，失败的连线以结构化反馈返回重规划；在 247 块板子上，D2、D3-A、D3-B、D3-C 四个测试集的 clean-pass rate 分别为 100%、94.9%、100% 和 40%。“LLM 规划 + 传统布线工具执行”的分工值得做 EDA agent 的人参考。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08175)　`论文` `Agent` `硬件`

### 系统评测 weight-space programming：收益局部且不稳定

论文在 Qwen3.5-0.8B 和 Qwen3.5-9B 上跑了 16 条编辑轨迹：只改 1,023 个参数就让 MATH-500 提升 29.45 个百分点，但跨任务迁移不均匀，不少轨迹因为无法可靠验证改进而保留了原始权重。想尝试直接改权重的人，可以把它当作对上面 Jevlar 这类案例的冷静补充。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.09382)　`论文` `训练`

### Agent harness 自我进化：分数上涨背后会丢掉原本做对的任务

作者评测了四种不改权重、只进化 agent harness 的方法，发现 所有进化后的 agent 都在新做对一些任务的同时丢掉了原本做对的任务，多数可靠性提升还伴随部署成本上升，得分最高的 agent 也不一定带来最大的平均提升；据此提出 EvoAudit。做 agent 自动优化时，只看总分容易误判。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.07624)　`论文` `Agent`

### StepFun 提出 P^2-MOPD：把专家权重当先验，加速多教师蒸馏

P^2-MOPD 把学生与多个专家参数的线性组合视为一个可微模型，在同一个 on-policy 蒸馏目标下同时训练混合系数和学生权重；在 1.7B 和 4B 规模、四个领域上，用一半训练步数就超过 MOPD 的最终平均恢复率，1.7B 模型最终达到 94.7%（MOPD 为 80.9%）。适合想把多个领域专家合并成一个小模型的团队。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03953)　`论文` `训练`

## 🛠 开源与工具

### Ollama v0.40.16 上架 65B 编程模型 Ripple Preview

新版加入 Ricursive Intelligence 的 65B dense 编程模型 Ripple Preview（ollama run ripple-preview），Qwen3.8 Flash Next 在 Apple silicon 上少用约 27 GiB 内存，/v1/responses 默认不再静默截断。在 Mac 上跑大 MoE 模型的用户值得升级。

来源：[GitHub Releases](https://github.com/ollama/ollama/releases/tag/v0.40.16)　`工具` `开源` `推理`

## ⚡ 快讯

- **Claude Code v2.1.322 在 Vertex 上支持 fast mode** Claude Code v2.1.322 在 Vertex 的 global、us 和 eu 区域加入 fast mode，Vertex 拒绝时回退到标准速度。 [GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.322)
- **OpenAI 介绍 Control Room：集中追踪并可紧急停止模型任务** OpenAI 介绍内部系统 Control Room，用来追踪研究基础设施上的模型工作负载，并在出现安全问题时快速停止它们。 [OpenAI News](https://openai.com/index/control-room)
- **DeepX 称可在 5 W 以内运行最高 100B 参数模型的推理** 据 EE Times 报道，DeepX 宣称能以低于 5 W 的功耗完成最高 100B 参数模型的推理。 [eetimes.com](https://www.eetimes.com/deepx-tapes-out-second-gen-chip-projects-6-7x-performance-gain-with-lpddr5x-pim/) · [HN 讨论](https://news.ycombinator.com/item?id=50429545)
- **Simon Willison：把 agent 写的 PR 描述折叠进 details** Simon Willison 认为 coding agent 写的 PR 描述准确但太长、读着像 slop，他的做法是写一段人工确认的简介，其余放进 HTML 的 <details>/<summary> 折叠起来。 [Simon Willison](https://simonwillison.net/2026/Nov/9/details-summary/)
