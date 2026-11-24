# 2026-11-24 · AI 晨报

## 今日要点

- Claude 推出 Claude Ship 自动处理 PR 审查与批准
- OpenAI 与 Cisco 开源 eBPF 安全运行时 Shirudo
- DeepMind 用 Gemini 4 agent 团队优化量子算法并形式化验证

## 🔥 头条

### Claude 推出 Claude Ship 自动处理 PR 审查与批准

Anthropic 发布 Claude Ship beta，由已正式可用的 Code Review 和两个 beta agent 组成，可审查 PR、修复问题并按团队策略决定是否批准合并。开发者可在 Claude Code 用 /ship 命令触发，管理员可按仓库配置审查级别、运行时机与消费上限。

来源：[Claude Blog](https://claude.com/resources/articles/introducing-claude-ship)　`工具` `Agent` `代码`

### OpenAI 与 Cisco 开源 eBPF 安全运行时 Shirudo

Shirudo 是面向 Linux 的开源运行时，用 eBPF shield 在补丁部署期间拦截漏洞利用路径而无需重启服务，shield 加载前会被加密签名和校验。在一项受控测试中，团队用 Codex 生成的 shield 挡住了针对运行中 Elasticsearch 服务的 Java4Shell 攻击。

来源：[OpenAI News](https://openai.com/index/introducing-shirudo)　`安全` `开源` `工具`

### DeepMind 用 Gemini 4 agent 团队优化量子算法并形式化验证

Google DeepMind 在新论文中用 Gemini 4 agent 团队改进量子算法，并用 Lean 形式化定理证明器逐一验证结果。agent 团队把惯性约束聚变的计算成本降低 11.8×，所需纠错量子比特从 5,650 降到 4,338，团队同时开源了 Lean 库、问题规格和已验证解法。

来源：[Google DeepMind Blog](https://deepmind.google/blog/finding-faster-quantum-algorithms-with-agents-and-formal-verification/)　`论文` `Agent` `推理`

### 阿里开源 Ling-3.2-air 多模态 MoE 模型

inclusionAI 发布 Ling-3.2-air，沿用 Ling-3.0-flash-VL 的原生多模态架构，总参数 124B、激活 5.5B。其 Terminal-Bench 4.0 通过率从 0% 提升到 27%，AA-Briefcase v1.1 的 Elo 从 987 升至 1340。

来源：[Hugging Face Trending Models](https://huggingface.co/inclusionAI/Ling-3.2-air)　`模型` `开源` `多模态`

## 🧠 模型

### Google 提出 DeepCrossAttention 改造残差连接

Google Research 的 DeepCrossAttention（DCA）用可学习权重和深度方向的交叉注意力动态组合前序层输出，避免深层网络中的信息稀释。DCA 增加的参数量不到模型总大小的 0.2%，在 LM1B 上达到同等困惑度所需层数从 42 层降到 30 层，并可加载到已预训练模型上继续训练。

来源：[Google Research](https://research.google/blog/supercharging-transformer-residual-connections/)　`训练` `推理`

### MemOnce 用可扩展记忆架构压缩长上下文 KV 缓存

南京大学团队提出 MemOnce，通过记忆编码器-解码器只缓存少量末层隐藏状态并动态解码回各层 KV 缓存，再用记忆稀疏注意力按需检索。改造 Qwen3.5-4B 后，记忆状态缓存减少 1313 倍，1M 上下文下预填充延迟降低，吞吐提升 3.5 倍。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.27973)　`论文` `推理` `训练`

### Duopra 让全双工语音模型具备任务执行能力

Duopra 是一种全双工交互模型，在学习对话控制的同时学习任务执行，把后端当作工具来调用，并用协议 SFT、全双工 RL 和投影器修复三阶段训练。搭配同一后端时 Pass@1 从 4.7% 升至 44.7%，直接调用工具达到 47.7%，接 DeepSeek 后端时为 49.3%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.25773)　`论文` `语音` `Agent`

## 📄 论文

### cmHC 用几何收缩平衡超连接的残差流混合

cmHC 指出流混合存在权衡：混合不足会让超连接退化成彼此独立的流，混合过度则让各流难以区分。作者提出把双随机矩阵约束的 Birkhoff 多面体向内部做几何收缩的方法，不引入新参数化，并在昇腾 NPU 上开发融合算子，使超连接执行延迟最多降低 44.8%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.27193)　`论文` `训练`

### NoPeWorld 让视频世界模型不再穿墙

NoPeWorld 利用冻结扩散 Transformer（DiT）隐藏状态中已编码的碰撞信息，训练一个小预测头判断候选动作是否安全，再把不安全动作替换为保留原意的安全动作。在六个视频世界模型上平均，物理违规率从 74% 降到 16%，并能零样本泛化到开放域图像、第三人称视角和移动障碍物。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.27963)　`论文` `视频` `推理`

### Future-OPSD 用无标注视频自蒸馏训练前瞻推理

Future-OPSD 把过去与未来的视频对转为自监督信号，无需标注或外部大模型监督，并用前瞻分数导出的对比特权优势让模型聚焦决策相关片段、压制无关上下文。在开放式预测和闭环规划任务上，基座模型分别最多提升 14.2 和 15.9 分，且不损害通用视频理解。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26954)　`论文` `多模态` `视频`

### TAISR 文字超分需要推理而非只看局部像素

论文提出 ReasonText 人工标注基准和 GTTCA 指标，评测十二个近期超分模型后发现在需要推理的文字上存在系统性短板。作者提出无需训练的 RTC 插件，用外部多模态大模型推断模糊文字并写入 caption 喂给文字条件超分模型，在评测的六个文字条件模型上均带来提升。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15449)　`论文` `图像` `多模态`

### ReSpaceBench 评测智能体跨重访的持久空间记忆

ReSpaceBench 包含 590 个合成与真实家居场景中的 3,244 个问题、9 类任务，刻意加入同类型房间干扰与跨会话物品变化。32 个模型和 3 个智能体视频理解框架的评测显示，最强零样本模型总体准确率 50.5%，低于人工标注者的 90.1%，而智能体框架相比同基座模型直接推理没有整体提升。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21485)　`论文` `Agent` `多模态`

## 🛠 开源与工具

### RoboTrack 发布机器人点跟踪基准与模型

RoboTrack-Bench 收录 307 个人工标注视频和 2,522 条人工校验点轨迹，覆盖杂乱场景与第一、第三人称视角；评测显示现有跟踪器在该基准上的 AJ 比 RoboTAP 低 3.0 到 6.6。项目同时发布合成训练集 RoboTrack-15M 以及两个模型 RoboTracker 和 RoboTracker-Warp。

来源：[Hugging Face Blog](https://huggingface.co/blog/allenai/robotrack) · [Ai2](https://allenai.org/blog/robotrack)　`工具` `开源` `论文`

### Hugging Face 详解如何构建与维护 agentic 评测

Hugging Face 的指南以一个物理实验室 agent 评测为例，梳理从定义主张、复用任务、校验、读 trace 到报告分数和比较模型的八步流程，并讨论基准错误、污染与饱和问题。文中指出，在 Terminal-Bench 的审计中只更换 agent harness 就让准确率波动最多 29.9 个百分点，说明评测外围软件同样会左右成绩。

来源：[Hugging Face Blog](https://huggingface.co/blog/agentic-evals)　`工具` `Agent`

### Anthropic 企业版 EFS 支持零数据保留

Anthropic 把 Enterprise Frontier Safeguards（EFS）开放公测，在不存储客户数据的前提下提供跨请求的自动化安全监控，可捕捉单条请求看似无害的复合攻击。EFS 兼容零数据保留（ZDR），输入输出写入客户自有存储并由客户自行控制访问策略、审计日志与加密密钥，Anthropic 不用这些数据做训练。

来源：[Claude Blog](https://claude.com/resources/articles/zero-data-retention-with-enterprise-frontier-safeguards)　`安全` `产品` `行业`

### obra/superpowers 用技能与子 agent 驱动编码流程

Superpowers 是面向编码智能体的开发方法论与技能框架，流程从先厘清需求、分段确认设计、产出实施计划，再进入子 agent 驱动的开发与审查，技能会自动触发。仓库同时提供 Claude Code、Codex、Cursor、Gemini CLI 等多种 harness 的安装方式，采用 MIT 协议。

来源：[GitHub Trending](https://github.com/obra/superpowers)　`工具` `开源` `Agent`

## ⚡ 快讯

- **CLI-Anything 把各类软件包装成 agent 可用的 CLI** CLI-Anything 通过 CLI-Hub 安装社区构建的 CLI，仓库内已为 Blender、GIMP、LibreOffice、Obsidian 等软件提供 agent-harness 适配，采用 Apache-2.0 协议。 [GitHub Trending](https://github.com/HKUDS/CLI-Anything)
- **MiniMind 主线结构对齐 Qwen3 并支持 Agentic RL** MiniMind 开源约 64M 的超小语言模型完整训练链路，核心算法用 PyTorch 原生实现，覆盖 Pretrain、SFT、LoRA、DPO 以及 GRPO、CISPO 等 Agentic RL 训练。 [GitHub Trending](https://github.com/jingyaogong/minimind)
