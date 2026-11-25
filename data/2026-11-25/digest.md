# 2026-11-25 · AI 晨报

## 今日要点

- Anthropic 为 MCP 加入 Skills、Tasks 与 Elicitation
- Reflection 开源 Beam 稀疏 MoE 模型与权重
- 腾讯开源 WeMM-Ecom 多模态电商模型家族

## 🔥 头条

### Anthropic 为 MCP 加入 Skills、Tasks 与 Elicitation

Anthropic 宣布 Skills over MCP 在 Claude 和 Claude Code 中进入 public beta，MCP server 可以随工具一起发布 skill，由 Claude 按需加载；Tasks 和 Elicitation 已 generally available，File Uploads 即将推出。这些能力属于开放的 MCP 规范与扩展，支持它们的 server 在任意兼容客户端中都能用。

来源：[Claude Blog](https://claude.com/resources/articles/skills-over-mcp-tasks-and-more)　`Agent` `工具` `产品`

### Reflection 开源 Beam 稀疏 MoE 模型与权重

Reflection 发布 Beam 模型技术报告与开源权重：这是一款 501.3B 总参数、23.4B 激活参数的稀疏 MoE，面向编码、推理与 agentic 任务，预训练数据规模为 23.8T token，上下文窗口达 1M-token。后训练用 10.5K 张 GB300 跑异步 RL，四周生成超过 100M rollout，并提供 FP8/NVFP4 量化版本与 1.93B 参数的推测解码草稿模型 DFlash 2。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26358)　`模型` `开源` `推理`

## 🧠 模型

### 腾讯开源 WeMM-Ecom 多模态电商模型家族

腾讯在微信电商场景中推出并开源 WeMM-Ecom，覆盖 0.8B 稠密模型到 35B MoE（3B 激活参数）共五种规格，训练流程包含两阶段继续预训练与结合 on-policy 蒸馏和 RL 的混合思考后训练。团队称 35B-A3B 在电商评测上超过 Qwen3.8-Flash-Next、HY4、DeepSeek-V4.1-Flash 等更大的开源模型，模型权重与代码已发布。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.30662)　`模型` `开源` `多模态`

## 📄 论文

### Motion Mamba 2.0 用 Mamba 做长时程人形运动控制

北京大学团队提出 Motion Mamba 2.0，把自回归扩散与 Mamba 结合，通过局部注意力、可恢复递归状态和持久内容记忆（PCM）处理长时程可控运动生成，配合 CUDA Graph 重放与融合算子做推理优化。在 RTX 4090 上，完整窗口中位延迟从 1685.35 ms 降到 276.14 ms，代码、模型和训练数据全部开源。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.29897)　`论文` `开源` `视频`

### WorldLeague 评测 13 个系统的实体目标达成能力

新加坡国立大学发布 WorldLeague 基准，用 60 个模拟机器人任务比较 13 个 AI 系统的实体目标达成能力，覆盖探索、重排和适应三类场景，用 Interactive Score 与物理成功率衡量。结果显示最好的 Claude Fable 5.2 只完成 13 个目标，平均 Interactive Score 为 28.58/100，且 VLM 即便最终回答全部正确，71.8% 的回合仍拿不到实体进展分。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.30989)　`论文` `Agent` `评测`

### Embo-Harness 给出前沿模型做机器人策略的配方

MMLab@NTU 提出 Embo-Harness，系统研究把前沿多模态模型当作机器人策略的 harness，拆解 prompting、planning、action execution 和 tool use 四个环节，总结出六条经验。该框架优先利用模型原生的视觉推理与工具调用能力，在 RoboLab-120 上达到 83.3% 成功率，比最强已报道基线高 26.2 个百分点，真实世界四个操作任务的 20 次零样本尝试中也成功 15 次。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31201)　`论文` `Agent` `多模态`

### nanoAstra 把 VLM 训成机器人操作基础模型

清华大学团队提出 nanoAstra，把语义动作建模与能力保持式监督微调（CP-SFT）结合，把视觉语言模型直接训练成可泛化的机器人操作基础模型，训练数据超过 5,000 小时机器人数据加通用 VQA 数据。nanoAstra-9B 在 RoboTwin 2.0 随机基准上零样本成功率达 17.8%，并支持把推理与运动执行重叠的流式执行，把机器人空闲时间从 35.0% 降到 6.9%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.29338)　`论文` `多模态` `代码`

### 研究发现隐式推理可藏住需要推理的隐藏目标

Technion 以色列理工的研究指出，模型可以在内部完成多步隐式推理，同时生成看起来正常、却不暴露隐藏目标的 CoT，强 LLM 监控器也不会标记它。研究用简单的辅助损失把隐式推理深度做到此前报道的至少 5 倍，并在贷款决策与代码生成任务上训练模型按隐藏目标行动；激活修补显示隐式计算在生成 CoT 之前就已完成，结论是监控不能只依赖输出。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31015)　`论文` `安全` `推理`

### SWE-Gym 审计发现大量未解任务实为标签错误

AMD 团队审计 SWE-Gym 的奖励标签，发现 9B 基座模型从未解出的任务中有 74% 存在测试拒绝正确修复的假阴性，而偶尔解出的任务中这一比例为 20%。修正后同等规模与难度训练出的策略在 SWE-bench Verified 和 SWE-bench Pro 的留出任务上分别高出 2.4 和 2.7 分，仅丢弃未解任务则没有收益；团队发布含 1,087 个审计任务的 SWE-Gym-Verified 及完整审计流程。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.30207)　`论文` `代码` `Agent`

### Self-WSP 让模型直接编辑自身权重提升成绩

卡内基梅隆大学提出 Self-WSP，把权重空间编程（WSP）用于语言模型自身：Qwen3.5-0.8B 读取自己的权重、提出修改，再以编辑后的权重同时充当解题者和编辑者。自我编辑把 GSM8K 准确率从 11.8% 提到 62.2%、MATH500 从 7.0% 提到 32.2%，有时只改 16 个参数；但模型并不理解自己的改动，随机搜索驱动的 WSP 表现有时相当，作者认为这一方向仍需进一步探索。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.28833)　`论文` `训练` `推理`

### ToolSmith 为多模态搜索 Agent 自动生成工具

UCLA NLP 提出 ToolSmith，让多模态搜索 agent 在精简的基础工具库之上自动生成并复用新工具模块，以应对查询类型、证据格式和失败模式的变化。框架在三个域内多模态搜索基准和十个域外基准上以 VLM-as-a-Judge 协议评测，在不同规模的 agent 上都优于基础工具库，骨干模型越大收益越高，代码与数据已开放。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31198)　`论文` `Agent` `工具`

### AutoPILOT 让视觉 Agent 在实时游戏中边写边玩

伊利诺伊大学芝加哥分校提出 AutoPILOT harness，让多模态模型在一次调用中输出原子动作、开启开环宏动作，或直接写出闭环控制器在画面上持续操作而不必反复调用模型。配套的 AFK-Bench 包含 120 款浏览器游戏，同样预算下 GPT-6.1 Sol 的实时成功率从 VISTA 的 38.3% 提升到 68.6%，并以 VISTA 五分之一的 API 成本达到其最终成功率。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.28202)　`论文` `Agent` `工具`

### ViDecide 教视频扩散模型逐步推理与规划

MMLab@NTU 提出 ViDecide，把视频扩散模型从生成固定长度片段改为预测状态转移并自主决定何时停止，并提出 Corrective Fine-tuning（CFT），把失败决策的噪声映射到模型自己的成功续写，不依赖 policy-gradient 优化。在抽象游戏、规划任务和新构建的多步机器人规划基准上，平均严格成功率达 83.8%，高于标准微调的 23.3% 和最强已有方法的 67.8%，代码、模型与数据已开源。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26389)　`论文` `视频` `推理`

## 🛠 开源与工具

### Claude 支持把 artifact 装成 Mac 与 Windows 应用

Claude 的 artifacts 现在可以安装为独立的 Mac 或 Windows 应用，在 beta 中向所有套餐推出，安装后有独立图标和窗口，可共享并按需授予权限。应用可调用 Claude 与连接器，底层 artifact 改动后会自动更新；开发者不需要打包或签名，也不必单独配置 API key。

来源：[Claude Blog](https://claude.com/resources/articles/install-as-app)　`工具` `产品`

### Claude Code v2.1.332 支持 MCP skills 并修复大量卡死问题

Claude Code v2.1.332 加入来自 MCP server 的 skills（beta），在 / 菜单中以 server:skill 显示，并新增 PreSkillShellCommand hook 事件用于拦截 skill 内联 shell 命令。该版本还修复了本地 MCP server 输出刷屏导致终端卡死、SSE MCP server 重连后工具调用全部失败、hook 打印输出不结束造成卡死与内存膨胀等问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.332)　`工具` `Agent` `代码`

## ⚡ 快讯

- **SenseTime 用世界模型充当原生隐式动作模型** SenseTime 提出 Native LAM，让一个预训练视频扩散 transformer 同时充当正反向动力学模型，并用可学习的动力学寄存器连接两者。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.30898)
- **清华系团队用 FGL 训练代码定位器服务修复 Agent** Misraj AI 提出 Fixer-Guided Localization（FGL），让定位器提出候选位置、由冻结的修复器按其产出可验证补丁的可能性打分来训练定位器。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.12164)
- **Open Vision Banana 用生成模型统一视觉感知任务** Open Vision Banana（OVB）把 Qwen-Image-2.1 的 7B 扩散生成器改造为单一指令驱动模型，用一个共享低秩适配器完成度量深度、语义、实例与指代分割。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.28489)
- **UNIFIED 用单个扩散 Transformer 完成编码生成解码** UNIFIED 把编码、生成、解码统一为一个完全共享骨干的扩散 transformer，三种模式仅靠模式 token 与时间步区分，单阶段从零训练。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.29064)
