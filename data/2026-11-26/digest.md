# 2026-11-26 · AI 晨报

## 今日要点

- Anthropic 把 Messages API 从 Python 迁移到 Rust，单请求 CPU 用量约降 70%，首 token 中位延迟约降 20%，并用生产 API 当验证器自动派发 Agent 修差异。
- 蚂蚁 Antom 3-in-1 Transformer 把序列、表格、图三种表征统一到支付风控，跨业务迁移让目标业务指标提升 34.5%，线上整体损失率相对 XGB-Online 降 37.88%。
- LlamaIndex 开源 OCRia-nano-1，把 4B 文档 VLM 蒸馏到 8.1M 参数，在 CPU 上随 LiteParse 提供文档解析。

## 🔥 头条

### Anthropic 用 Rust 重写 Messages API

Anthropic 把 Messages API 从 Python 迁移到 Rust，在不停服、不冻结功能开发的前提下让单请求 CPU 用量降约 70%，首 token 中位延迟降约 20%。他们把生产 API 本身当作验证器，在生产流量上比对差异并自动派发 Agent 修复，Claude 完成了核心请求路径的第一版代码。

来源：[Anthropic Research](https://www.anthropic.com/research/migrating-api-to-rust)　`工具` `Agent` `工程`

### 蚂蚁发布支付基础模型 Antom 3-in-1 Transformer

蚂蚁国际推出 Antom 3-in-1 Transformer，把交易序列、表格特征和关系图统一进一个骨干做支付风控，总参数约 7B、每条任务路由激活约 1.7B。预训练让跨业务迁移的目标业务指标提升 34.5%，在十亿级支付平台的四个月线上实验中，整体损失率相对 XGB-Online 下降 37.88%；出于反欺诈考虑未放出权重。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.25403)　`模型` `训练` `行业`

### LlamaIndex 开源 CPU 文档解析模型 OCRia-nano-1

LlamaIndex 发布 OCRia-nano-1，一个 8.1M 参数的文档解析流水线，把检测-识别 OCR 栈与 LayoutNet 表格版面模型结合，作为 LiteParse 的默认 OCR 后端在 CPU 上运行。模型由 4B 文档 VLM OCRia-1 蒸馏而来，ParseBench-2 得分为 59.2，16 vCPU 下每秒处理 27.8 页，可通过 CLI、Python、Node.js 及浏览器 WebAssembly 使用。

来源：[Hugging Face Trending Models](https://huggingface.co/llamaindex/OCRia-nano-1)　`模型` `开源` `工具`

## 🧠 模型

### LlamaIndex 发布 4B 文档解析模型 OCRia-1

LlamaIndex 开源 OCRia-1，一个 4B 视觉语言模型，单次调用读入页面图像直接输出 Markdown，表格用 HTML 表示，不需要额外版面检测、OCR 引擎或文本层。作者称其在两个 ParseBench 榜单上都是得分最高的开放权重模型，ParseBench 2 得分 85.2、ParseBench 1 得分 84.7，并提供 GGUF 权重与 vLLM 部署方式。

来源：[Hugging Face Trending Models](https://huggingface.co/llamaindex/OCRia-1)　`模型` `开源` `多模态`

### MemTensor 发布记忆原生模型 MemT-1.0-Pro

MemTensor 发布 MemT-1.0-Pro，基于 NVIDIA-Nemotron-3-Ultra-550B-A55B，把动态局部记忆与可训练超记忆做成原生计算的一部分，推理时无需回看原始上下文。其持久状态大小恒定，在 128K 历史长度下相对完整上下文 KV cache 约省 66× 存储，并提供面向长程编码任务的经验复用智能体框架。

来源：[Hugging Face Trending Models](https://huggingface.co/MemTensor/MemT-1.0-Pro)　`模型` `Agent` `推理`

## 📄 论文

### NightWatch：为计算机操作 Agent 补上持续感知

NightWatch 是一个即插即用框架，把轻量 System-1 模型 NightWatch-0.8B 与视觉语言计算机操作 Agent 配对，做流式界面监控，无需改动原 Agent 的模型、提示词或动作空间。在 OSWorld-Verified 上它把非推理墙钟时间减少 33%、浪费时间减少 53%，在 DynaCU-Bench 上把大模型 Agent 的成功率从 39.5% 提升到 44.2%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.28947)　`论文` `Agent` `工具`

### RLVB：用可验证信念训练 Agent 延迟作答

Reinforcement Learning with Verifiable Beliefs 在训练时利用模拟器计算的答案后验分布，奖励 Agent 在证据不足时继续探索、证据充分时才作答，不需要评判器、评论器或奖励模型，也从不读取 Agent 写下的信念行。它在三种视觉语言模型与三个基准的九种设定下平均提升基线 17.1%，并同时发布视觉谜题基准 Pro Worlds。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.32884)　`论文` `Agent` `训练`

### S-Mind：用空间 token 内化多视角几何

S-Mind 用一组紧凑的空间 token 让多模态大模型内化多视角几何，训练时监督这些 token 承载融合后的 3D 场景，并按推理所取的视角重新表达该场景。在四个空间基准上它让 Qwen3.5 骨干平均提升最多 22.26 分，并在平均准确率上超过 GPT-6-Astra、Kimi-K3.1-Pro 和 GLM-5.3-Flash，推理速度约为工具型 Agent 的 100 倍。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.28649)　`论文` `多模态` `训练`

### LoomFormer：逐 token 重接 Transformer 回路

论文提出 loom attention，让 Transformer 在每个 token 上把注意力头对更早注意力头输出的纵向注意力与对 token 的横向注意力交织，从而动态重接内部回路，并由此得到双流架构 LoomFormer。作者报告在相同 300B token 训练量、仅增加 2% FLOPs 的条件下，LoomPythia-2.8B 取得 mHC-Pythia-2.8B 约 1.6 倍的下游平均增益。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.30634)　`论文` `模型` `训练`

### ICLWorld 评测 Agent 从数字到物理的上下文学习

ICLWorld 是一个在线基准，配合统一 harness UIverse，评测 Agent 在计算机操作与机器人操作任务上的上下文学习，覆盖 30 个环境、160 个需要从上下文学习反直觉规则的任务和 630 段演示视频。结果显示 Claude Opus 5.5 与 GPT-6 Astra 在计算机操作上的成功率为 82% 与 76%，但在机器人操作上只有 27% 与 26%，无规则对照组最高仅 8%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.32649)　`论文` `Agent` `评测`

### CoT-Proxy：只蒸馏动作也能迁移长程策略

CoT-Proxy 表明训练长程 Agent 不必拿到教师隐藏的思维链：学生只学教师的动作，推理块留空，再用自身生成回放缓冲区的 KL 损失限制漂移，训练出的策略在推理时开启思考仍能以自己的风格像教师那样行动。蒸馏 Qwen3.6-27B 的动作把 Qwen3-4B 在 AppWorld 上的成功率从 7% 提到 18%，加上 CoT-proxies 后进一步到 35%，同样方法用于 GPT-5.6 Luna 时把 Qwen3-4B 从 7% 提到 48%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.33148)　`论文` `Agent` `训练`

### ACAP：用异步编码 Agent 组控制机器人

ACAP 把一台机器人组织成多个常驻编码 Agent 组成的团队，每个成员负责可配置的控制组，由 hyper-agent 分配任务、协调依赖并在主 Agent 与成员之间动态切换控制权，从而让互不依赖的工作并行推进。在 72 次覆盖 25 种任务/平台设定的真机 rollout 中，它相对单 Agent 的 Direct Policy 把任务均衡时间成本降低 28.2%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31205)　`论文` `Agent` `硬件`

### PartAgent：免训练智能体做 3D 部件分割

PartAgent 是一个免训练的智能体框架，用结构-语义专家整合把 3D 专家预测的区域与 2D 专家的多视角语义证据经图像-表面对应结合起来，再用观测驱动的闭环分区细化选择检查、修补、组合或重选动作并验证修改。在 PartObjaverse-Tiny-WT 上取得 68.41 mIoU，比最强对比方法高 8.53 点，在四个数据集上的平均 mIoU 为 69.36。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.32554)　`论文` `Agent` `图像`

### SpecEngineeringBench 测编码 Agent 的自主规格工程

SpecEngineeringBench 收集 78 个开源 Python 仓库的 100 个实例，每个实例含多个已记录缺陷，要求编码 Agent 自行确定测什么、在哪里查，而不是按提示写测试。七个前沿编码 Agent 的测试有效率与覆盖率很高（Head Pass Rate 91.47%、Change-focused Coverage 80.48%），但 Fail-to-Pass Rate 只有 26.36%，定位召回率从文件级的 78.11% 降到函数级的 51.29%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.32973)　`论文` `代码` `Agent`

### Qwen-Image-HD：用分块自回归做高清图像生成

Qwen-Image-HD 把 Qwen-Image 2.0 改造为局部训练加分块自回归生成：每次预测覆盖一块 1K 尺度的目标 tile，条件是高分辨率的上方与左方邻居以及压缩的历史缩略图。作者报告在 Qwen-Image-Bench 的 4K 设置下整体评测优于 FLUX-3-Image-Klein 的直接 4K 生成，并提出 Wavefront-AutoRegressive 调度让同一反对角线上的 tile 跨 GPU 并发以降低单图延迟。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.32736)　`论文` `图像` `模型`

## 🛠 开源与工具

### Google 推出可验证社交推理评测框架

Google Research 发布一个基于多智能体社交模拟的评测框架：目标 Agent 带有隐藏动机，用户 Agent 向被测助手转述经过主观筛选的经历，助手需推断真实动机，由框架天然提供可验证的 ground truth。团队开源框架与超过 20K 条生成样本的数据集，并发现模型对用户框架敏感、需要比人类更多细节，且未能充分利用澄清提问。

来源：[Google Research](https://research.google/blog/verifiable-social-reasoning-for-llm-assistants/)　`工具` `评测` `开源`

### CodecOPSD 剪掉视频生成中冗余条件 token

CodecOPSD 先用基于视频编解码器的 token 剪枝方法丢弃冗余条件 token，再用 on-policy 自蒸馏训练 DiT adapter 学会这种剪枝模式而不损失质量。在其自研视频扩散模型上扩展到 16 种条件模态，平均剪掉 66% 的条件 token，去噪速度变为 2 倍，KV cache 模式下缓存内存最多缩小 73%，方法也可迁移到其他预训练图像与视频生成模型。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31184)　`工具` `视频` `训练`

## ⚡ 快讯

- **CUA-SEE 让计算机操作评测环境自我演化** 阿里通义实验室提出 CUA-SEE 闭环评测环境，从 rollout 证据中共同演化任务与可执行验证器，把目标拆成基准演化、诊断演化和验证器演化，用于持续追踪 Agent 的能力边界。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.30962)
