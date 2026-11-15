# 2026-11-15 · AI 晨报

## 今日要点

- Claude 官方梳理了常驻 Agent 的五个核心构件：事件收件箱、定时器、记忆、权限和发件箱，为自建长时运行 Agent 提供了架构参考。
- IBM Granite 团队开源了带 LLMON 标注格式的预览模型 granite-4.1-3b-llmon-preview 与 granite-4.1-8b-llmon-preview，用于抵抗文档中的间接提示注入。
- 开源推理侧，tandem.cpp 为 llama.cpp 提供 MoE 卸载补丁并新增 AMD ROCm 支持，HarborRL 则更新了弹性网关与免 SSH 集群部署。

## 🔥 头条

### Claude 官方详解常驻 Agent 的五个核心构件

Claude 博客把常驻 Agent 的实现拆成五个核心构件：事件收件箱、定时器、记忆、权限和发件箱，并说明它们如何组合成跨会话、有状态的主动型 Agent。文中称新模型判断力更好、推理成本下降，Opus 5.5 在某长程编码基准上每个已解任务成本比 Opus 5 低 78%。这套划分可直接作为自建常驻 Agent 的架构参考。

来源：[Claude Blog](https://claude.com/resources/articles/building-always-on-agents)　`Agent` `产品`

### IBM 开源两款抵抗提示注入的 Granite 预览模型

IBM Granite 团队发布 granite-4.1-3b-llmon-preview 和 granite-4.1-8b-llmon-preview，两个开放权重模型基于新的 LLMON 标注格式训练，让模型把文档、工具输出等素材当作内容而非指令。在 OPI 基准上攻击成功率从 100% 降至 0.1%（3B）、从 96.3% 降至 0.02%（8B）；IBM 将其限定为探索与评测用途。

来源：[maccus.fr](https://maccus.fr/en/ibm-granite-prompt-injection/)　`安全` `模型` `开源`

### tandem.cpp 让 llama.cpp 加速大 MoE 模型并支持 AMD

tandem.cpp 是 llama.cpp 的补丁集，把常用专家留在 GPU、其余交给 CPU，面向装不进显存的 MoE 模型。项目 README 称其他难以装入显存的 MoE 模型通常能获得 1.4–2.1× 提速，本次更新改进了共享的 CUDA/HIP 内核，RX 7900 XTX 上 +2.5%、RTX 5070 Ti 上 +1.3%，补丁也可用 HIP 构建。

来源：[GitHub](https://github.com/ewhacc/tandem.cpp)　`开源` `工具` `推理`

### NVIDIA 教程：用两台 DGX Station 跑 GLM-5.3

NVIDIA 开发者博客给出用 vLLM 在两台通过 ConnectX-8 RDMA 互联的 NVIDIA DGX Station 上服务 GLM-5.3 的教程，采用 TP=2 张量并行。文中称 GLM-5.3 NVFP4 是 753 billion 参数、每 token 激活 40 billion 的量化 MoE 模型，约 464 GB 权重超过单块 GB300 的 252 GB HBM3e。

来源：[developer.nvidia.com](https://developer.nvidia.com/blog/when-one-gpu-isnt-enough-serving-glm-5-3-across-two-nvidia-dgx-stations-with-vllm/)　`工具` `硬件` `推理`

### HarborRL 更新弹性网关与免 SSH 集群部署

开源 Agentic RL 框架 HarborRL 的更新日志列出四项改动：带静态路由的弹性网关扩展、节点通过 HTTP 拉取任务的 Hub 部署模式、多算法统一到 Slime 训练管线，以及配置向导与沙箱 rollout 改进。项目 README 称其把模型服务、轨迹生成、工具执行、验证奖励和策略更新整合为一条可复现管线。

来源：[GitHub](https://github.com/datamllab/HarborRL)　`开源` `Agent` `训练`

## 🧠 模型

### Haru-4B：全双工语音对话基础模型

higurashi-ai 发布 Haru-4B，一个低延迟、多语言的全双工连续语音对话基础模型，听与说同时进行，原生全双工频率为 7.5 Hz，每 133 ms 处理一帧用户音频并产出一帧自身音频和文本。模型卡说明它以 Qwen3.5-4B 为文本骨干、采用 VibeVoice 声学 tokenizer，权重以 Apache-2.0 发布。

来源：[Hugging Face Trending Models](https://huggingface.co/higurashi-ai/Haru-4B)　`模型` `语音` `开源`

### Viggle-Remake：MiniMax-H3 的视频重拍 LoRA

Viggle 发布 Viggle-Remake，一组基于 MiniMax-H3 的 rank 256 LoRA，用于给视频换人换物、改背景天气与光线，也提供 MCP server 让编码 Agent 自行切窗口、画关键帧并渲染。项目说明提供 ComfyUI 节点包和 int8/GGUF 文件以适配 12–24 GB 显卡，代码以 Apache 2.0 发布，权重沿用 MiniMax H3 Community License。

来源：[Hugging Face Trending Models](https://huggingface.co/Viggle/Viggle-Remake)　`模型` `视频` `开源`

### tiny-voca：4.5M 参数的全开放英文 TTS

tiny-voca 是一个从零训练的小型英文 TTS 模型，含波形生成部分共 4,537,291 参数、18 MB，支持两个音色、24 kHz 采样率。README 称其在四线程 CPU 上约 70 倍实时运行，可用 PyTorch、ONNX Runtime 和 ONNX Runtime Web，代码、权重、训练配方与数据集全部开放。

来源：[GitHub](https://github.com/n4ze3m/tiny-voca)　`模型` `语音` `开源`

## 📄 论文

### APEX 用条件偏移实现少步流式视频生成

清华大学团队提出 APEX，把 DMD 中独立的 fake-score network 换成生成器内部的条件偏移估计，用同一套参数分别做生成与伪分数估计。论文在 180 秒视频上报告，相比 S2-Avatar 指令遵循得分 3.856 对 3.831、视觉美学 0.641898 对 0.632606，相比 DMD 每 GPU 峰值显存低 4.4%、平均迭代时间短 9.2%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.14033)　`论文` `视频`

### SparseRead：给 Agent 加一层稀疏阅读控制

SparseRead 是可复用的阅读控制层，无需改动 Agent 模型即可管控内容准入，包含 Read Intent Protocol、Adaptive Reader Backends 和带完整视图回退的 Budgeted Read Gate。论文称在六个模型和五种场景下最多减少 92.9% token 与 89.0% 墙钟时间，97% 的设置下任务质量持平或更好，Web 深度搜索任务 token 减少 31.0--43.0%。

来源：[arXiv](https://arxiv.org/abs/2608.22237)　`论文` `Agent`

### Sage-Taiyi：用元认知架构做科学发现

上海人工智能实验室等提出 Sage-Taiyi，一个受元认知启发的架构，通过显式监控与控制修订对证据、假设和未解问题的理解，再据此调整研究目标与选择可复用的推理方法。在 Taiyi-Bench 的 265 个任务上，八项指标均排名第一，Overall 得分为 54.0，强于最强基线 AI Scientist-v2 的 47.9。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12762)　`论文` `Agent` `推理`

### WorldFoundry：统一生成式世界模型的基础设施

WorldFoundry 是面向生成式世界模型的开源基础设施，覆盖视频、3D 和 4D、具身动作与交互式系统的可复现推理与评测。项目把模型与基准发现、运行时与资产准备、执行编排、产物管理和交互式可视化统一起来，并以显式清单和可追溯的评分卡区分执行就绪与评测结论。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.10771)　`论文` `开源` `工具`

### SplatAnything：跨场景的前馈 3DGS 归一化方法

浙江大学团队提出 SplatAnything，用 Gaussian Spacing Normalization（GSNorm）把场景级高斯间距归一化，为高斯预测提供更一致的空间参照，缓解原有前馈 3DGS 中径向归一化与真实间距不匹配导致的监督歧义。论文同时建立了覆盖多数据集、输入稀疏度与外推视角的基准。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08264)　`论文` `图像`

## 🛠 开源与工具

### Chrome DevTools MCP：给编码 Agent 的浏览器调试

ChromeDevTools 的 chrome-devtools-mcp 让编码 Agent（如 Claude、Cursor、Copilot）控制和检查运行中的 Chrome，既提供 MCP server 也提供 CLI。README 列出的能力包括记录性能 trace、分析网络请求与控制台消息、截图，以及用 Puppeteer 做可靠自动化。

来源：[GitHub Trending](https://github.com/ChromeDevTools/chrome-devtools-mcp)　`工具` `开源` `Agent`

### Plannotator：面向编码 Agent 的本地审阅界面

Plannotator 是一个基于浏览器的本地审阅界面，让 Agent 把计划、规格、HTML 原型或代码评审推给开发者，开发者标注、评论后一键把反馈发回 Agent 会话。项目支持 Claude Code、Codex、Gemini CLI、OpenCode 等，可通过插件、hook 和命令接入，也可经 MCP 连接其他 Agent。

来源：[GitHub Trending](https://github.com/backnotprop/plannotator)　`工具` `开源` `Agent`

### ARC-1.0：跨云端与本地模型的路由决策模型

Rayline 发布 ARC-1.0，一个 0.6B 的决策模型：读取 Agent 对话，输出选择模型与推理强度的信号，由应用结合可用模型、价格和策略决定下一次请求怎么跑。它把预测与策略分开——预测任务成功率和 token 用量，应用自行提供价格与权衡；模型卡称混合配置在六个基准上保留 Opus 5.5 的 97.5% 质量、成本低 92.9%。

来源：[Hugging Face](https://huggingface.co/rayline-ai/ARC-1.0)　`工具` `模型` `Agent`

### Univer：构建自有 AI 办公套件的 Office SDK

Univer 是构建 Office 应用的 SDK，提供表格、文档、演示、关系表、画布和 PDF 的编辑、计算、协作与文件处理能力，可嵌入产品或供 Agent 使用。仓库以 Apache-2.0 开放 Web SDK 的核心架构与引擎实现，包括内容模型、命令系统、公式与渲染引擎、Facade APIs 以及 Sheets 与 Docs 编辑能力。

来源：[GitHub Trending](https://github.com/dream-num/univer)　`工具` `开源` `Agent`
