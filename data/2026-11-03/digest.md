# 2026-11-03 · AI 科技日报

## 今日要点

- GPT-6 Astra 可直接读写模型权重
- vLLM v0.33.0 升级 PyTorch 并放弃 CUDA 12.9
- SGLang v0.5.23 支持 TPU7x 与低延迟内核

## 🔥 头条

### GPT-6 Astra 可直接读写模型权重

研究者在博客中展示，GPT-6 Astra 能直接读取神经网络权重判断网络行为，并在不写训练循环、也不用环境反馈的情况下修改权重：修复 Qwen3.5-0.8B 数学能力时只改动 0.016% 的权重，同一采样设置下 MATH-500 从 7.9% 升到 48.1%，IFEval 提升 3 倍。
这被称为 Weight-Space Programming，若经得起复核，意味着模型优化可能不再局限于梯度下降和符号优化器。

来源：[rikiyat.github.io](https://rikiyat.github.io/blog/weight-space-programming/) · [explainx.ai](https://explainx.ai/blog/weight-space-programming-gpt-6-astra-edits-qwen3-5-0-8b-weights-math-7-9-to-48-1-mit-csail-2026)　`模型` `推理`

### vLLM v0.33.0 升级 PyTorch 并放弃 CUDA 12.9

vLLM v0.33.0 包含 927 个提交、389 位贡献者，升级到 PyTorch 2.14.0、torchvision 0.29.0 和 Triton 3.8.0，同时发布 wheel 和镜像只保留 CUDA 13.0，CUDA 12.9 的 wheel 与 -cu129 镜像不再发布。
新版本加入 Reflection Beam-1.0 等模型支持、推测解码与多硬件加速，开发者升级前需要检查 PyTorch 与 CUDA 版本兼容性。

来源：[GitHub Releases](https://github.com/vllm-project/vllm/releases/tag/v0.33.0rc3)　`工具` `开源`

### SGLang v0.5.23 支持 TPU7x 与低延迟内核

SGLang v0.5.23 合并了 1007 个 PR，新增 Muse Spark Open、MiniMax-M3.1-Flash 等模型支持，并通过 SGLang-TorchTPU 在 Google TPU7x 上运行。
新版本提供 NVIDIA megakernel 和 AMD monokernel 低延迟模式，以及在单张消费级 GPU 上运行超出显存容量 MoE 模型的 Paged Experts 选项。

来源：[GitHub Releases](https://github.com/sgl-project/sglang/releases/tag/v0.5.23)　`工具` `开源`

### Apriel Voice 27B Preview 统一语音、推理与工具调用

ServiceNow-AI 发布开源语音语言模型 Apriel Voice 27B Preview，基于 post-trained Gemma 4 26B-A4B 构建，在共享推理骨干内直接处理语音并生成回复和工具调用，不需要单独的对话模型。
模型通过两阶段训练适配语音并使用在线蒸馏，思考模式下在 Big Bench Audio 得分 98.90、Speech-BFCL 得分 81.13、τ-Voice 任务成功率 65.51%，平均延迟 1.91 秒。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.40738)　`模型` `语音` `多模态`

### REA 用异步运行时协调机器人快慢策略

REA 提出统一运行时，让审慎的 System 2、具身路由 System 1 与反应式 System 0 策略协作，核心规则是正在运行的策略不等待大脑，并通过路由记忆、边界触发的判断门和共享预算升级阶梯完成恢复。
在 60 个 LIBERO-Pro 任务的 3,000 次测试回合中成功率 95.9%，控制步数减少 25%、控制时间减少 17%，并迁移到 BEHAVIOR-1K 和真实的 Unitree G1 人形机器人。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.42053)　`论文` `Agent` `工具`

## 🧠 模型

### Nanbeige4.3-33B 面向轻量 Agent 场景

Nanbeige 团队发布 Nanbeige4.3-33B，将其定位为 Nanbeige4.3 系列的旗舰教师模型，后续用于把 Agent 能力蒸馏到更小的模型。
该模型支持最长 524,288 tokens 上下文，可用 Transformers、SGLang 或 vLLM 部署，模型卡给出的成绩包括 Terminal-Bench 2.1 为 80.9、Terminal-Bench 4.0 为 23.8、DeepSWE 为 65.5。

来源：[Hugging Face Trending Models](https://huggingface.co/Nanbeige/Nanbeige4.3-33B)　`模型` `Agent` `开源`

## 📄 论文

### R²Orch 用递归自博弈训练 Agent 编排器

R²Orch 提出递归自博弈编排范式：内层自博弈让 Proposer 自行选择任务训练编排器，外层循环则改进内层循环本身，并引入 Recursive Learnability 训练目标和 Skill Withdrawal 机制。
作者称其在十二个数据集的问答、数学、代码与交互任务上稳定超过基线，代码已放出。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.22740)　`论文` `Agent`

### FrameForge 用视频模型先验统一图像生成

FrameForge 把条件生成建模为输入自适应的虚拟时间关系，在预训练视频模型上用 Mixture of Temporal Experts 动态选择不同虚拟间隔的 temporal RoPE 专家，并用 Chain of Temporal Reasoning 的推理瓶颈注意力掩码引导信息传播。
在 DreamBench、COCO2017 和 GEdit-Bench 上，作者称该方法在主体驱动生成、canny-to-image 生成和图像编辑上优于对比方法。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.36545)　`论文` `图像` `视频`

### SimpleLoRIF 定位削弱安全性的微调数据

SimpleLoRIF 用梯度嵌入找出与不安全行为梯度对齐的微调样本，把反向传播限制在最后四个 transformer block，从而可处理百万量级的数据集。
作者据此构建 SafeTulu，移除 Tulu 3 中最对齐的 20% 样本后，跨 Qwen、Llama 和 Olmo 的 GCG 攻击成功率最多下降 22%，同时基本保留甚至提升模型能力，数据集与可定制 Space 均已发布。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.37481)　`论文` `安全` `训练`

### OSWAM 用一步扩散生成动作

OSWAM 为自动驾驶与具身控制提出一步动作生成的世界动作模型，用 imagination tokens 初始化扩散过程以提供物理先验和动作条件表示，并通过带未来条件的特权信息蒸馏增强动作生成。
作者称 OSWAM 在两项任务上取得与需要数十步的直接策略 WAM 和 Joint-WAM 相当或更好的结果，相对直接策略 WAM 基线约有 3 倍加速，编译后推理延迟在 NVIDIA RTX 5090 上低至 40ms。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.35850)　`论文` `推理` `多模态`

## 🛠 开源与工具

### agent-desktop 开源跨平台桌面操作 CLI

vercel-labs 发布 agent-desktop，一套面向 AI Agent 的桌面操作 CLI 和 C 库，覆盖 macOS、Windows 和 Linux，通过操作系统无障碍树读取并操作桌面应用，不依赖像素匹配。
每次调用返回带元素 ref 的 JSON 快照，Agent 按 ref 操作后再次快照校验，并提供 FFI 以便在进程内直接调用，适合把桌面操作能力接入 Agent 循环。

来源：[GitHub Trending](https://github.com/vercel-labs/agent-desktop)　`工具` `开源` `Agent`

### Latent Sparse Attention 开源超长上下文稀疏注意力

研究团队发布 Latent Sparse Attention (LSA)，面向超长上下文的次二次注意力方向，在 10M tokens 下把稀疏注意力最高加速 22.7×，全注意力加速 72.4x。
作者称 LSA 在超长上下文上匹配全注意力的精度，并公开内核、SGLang 集成、论文与细节，方便在本地部署更长上下文时降低注意力成本。

来源：[x.com](https://x.com/jcrwhittington/status/2117317159777177602?a=02yfc9wrBoQ2Xi7DDjQ&amp;s=46)　`工具` `开源` `推理`
