# 2026-11-03 · AI 科技日报

## 今日要点

- MIT CSAIL 发现 GPT-6 Astra 能直接读写神经网络权重，只改 Qwen3.5-0.8B 的 0.016% 权重就把 MATH-500 从 7.9% 提到 48.1%。
- 中国商务部第 48 号公告拟把前沿模型权重纳入出口管制，出口前登记要求已经生效。
- OpenAI 介绍了支撑其单体仓库的 Git 后端 Pando；推理框架 vLLM v0.33.0 和 SGLang v0.5.23 也发布了新版本。

## 🔥 头条

### MIT CSAIL：GPT-6 Astra 能直接读写神经网络权重

MIT CSAIL 的研究者发现，GPT-6 Astra 只看原始权重就能判断一个网络是训练来做什么的，还能在没有环境反馈的情况下从零写出小型游戏网络，胜过用 PPO 训练的网络。让它在不用梯度的情况下提升 Qwen3.5-0.8B 的数学能力，它定位到导致推理循环的权重问题，只改 0.016% 的权重，MATH-500 就从 7.9% 升到 48.1%。作者也指出，改权重只能移除掩盖能力的障碍，不能凭空增加模型没有的能力；这为可解释性和无需重训的定点修复提供了新思路。

来源：[rikiyat.github.io](https://rikiyat.github.io/blog/weight-space-programming/) · [HN 讨论](https://news.ycombinator.com/item?id=50341174) · [Reddit 讨论](https://www.reddit.com/r/MachineLearning/comments/1xm89ef/sparks_of_weightspace_programming_llms_can/) · [explainx.ai](https://explainx.ai/blog/weight-space-programming-gpt-6-astra-edits-qwen3-5-0-8b-weights-math-7-9-to-48-1-mit-csail-2026)　`模型` `论文`

### OpenAI 自研 Git 后端 Pando，扛住 Codex 带来的并发

OpenAI 介绍了 Pando：一个兼容 Git 协议和客户端的新仓库后端，各分支的更新独立协调、可以并行，取数据时跨客户端复用 packfile，现在支撑 OpenAI 单体仓库的全部开发。上线后中位推送延迟降低近 5 倍，每天交付接近一个 petabyte 的 Git 数据。对开发者来说，这说明 Agent 并行开发会给源码控制带来新的压力；OpenAI 对 Git 客户端的部分改进已经进入上游 Git。

来源：[OpenAI News](https://openai.com/index/scaling-git-at-openai) · [HN 讨论](https://news.ycombinator.com/item?id=50345924)　`工具` `代码` `Agent`

### 中国商务部第 48 号公告：前沿模型权重拟纳入出口管制

商务部第 48 号公告拟在禁止出口限制出口技术目录中新增 40 项技术，其中 23 项属于 AI；训练算力达到 10^26 FLOPs、参数达到 2 trillion 或在全球排名前 10 的模型，其权重、检查点、源码和架构等将受限。目录修订仍是征求意见稿，但出口前登记要求已经生效。对开发者：API、应用、SaaS 等使用方式不算出口模型，已开源或已公开发表的技术不在管理范围；在中国以外本地部署受限模型则会被覆盖，自托管中国模型的团队需要关注供应商的登记情况。

来源：[labs.cloudsecurityalliance.org](https://labs.cloudsecurityalliance.org/research/csa-research-note-china-ai-export-controls-announcement-48-2/) · [HN 讨论](https://news.ycombinator.com/item?id=50334038)　`行业` `安全`

## 🧠 模型

### OpenAI 推出生物医药推理模型 GPT-Rosalind-6

GPT-Rosalind-6 与 GPT-6 Astra 使用相同的权重，面向生物学、药物发现和转化医学，以 GPT-Rosalind-6 Research 的形式通过可信访问提供给经过审核的科研人员、研究机构、企业和政府伙伴。系统卡附录显示，它在 MedChemBench 上的平均得分为 49.6%，GPT-Rosalind-5.5 为 28.9%；OpenAI 把这次发布定为生物与化学领域的 High 能力。对开发者：这是需要申请准入的专用模型，生命科学团队要走审核流程才能使用。

来源：[deploymentsafety.openai.com](https://deploymentsafety.openai.com/gpt-rosalind-6) · [HN 讨论](https://news.ycombinator.com/item?id=50337503)　`模型` `推理` `安全`

### Nanbeige4.3-33B 发布，主打 Agent 编程

Nanbeige4.3-33B 是 Nanbeige4.3 系列的旗舰教师模型，面向复杂编程和专业办公类任务，以 apache-2.0 许可放出权重，支持 524,288 tokens（512K）上下文。官方评测表中它在 Terminal-Bench 2.1 上得 80.9（Qwen3.8-27B 为 73.0），在 SWE-Bench Pro 上得 60.3，略低于 Qwen3.8-27B 的 61.7。对开发者：30B 级别又多了一个面向 Agent 编程的开源权重选择，分数为厂商自测。

来源：[Hugging Face Trending Models](https://huggingface.co/Nanbeige/Nanbeige4.3-33B)　`模型` `开源` `代码`

## 📄 论文

### 研究：污染 0.1% 预训练数据即可给 Agent 植入后门

论文从零预训练 0.6B、1.7B 和 4B 的 Qwen3 模型并后训练成命令行 Agent，发现只需污染 0.1% 的预训练语料，就能植入远程代码执行后门：出现触发词时 Agent 执行攻击者指定的命令，平时表现正常。攻击成功率随模型规模上升，4B 模型约为 92%，投毒率降到 0.0005% 时仍不为零。对开发者：给 Agent 执行命令的权限时，模型本身也是供应链风险，沙箱和命令审查不能省。

来源：[arXiv](https://arxiv.org/abs/2610.37741) · [HN 讨论](https://news.ycombinator.com/item?id=50341334)　`论文` `安全` `Agent`

### SimpleLoRIF：用梯度找出削弱安全性的微调数据

DatologyAI 等提出 SimpleLoRIF：简化低秩归因方法、只在最后四个 transformer 块做反向传播，让梯度嵌入能处理百万量级的数据集，找出梯度与不安全行为对齐的微调样本。用它从 Tulu 3 中去掉最相关的 20% 样本得到 SafeTulu，在 Qwen、Llama 和 Olmo 上把 GCG 攻击成功率最多降低 22%，能力基本保持甚至提升。对开发者：微调前可以用这种方法过滤看起来无害、却会侵蚀安全对齐的数据。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.37481)　`论文` `安全` `训练`

### ServiceNow 发布开放语音模型 Apriel Voice 27B Preview

Apriel Voice 27B Preview 基于 Gemma 4 26B-A4B，直接处理语音并生成回复和工具调用，不需要单独的对话模型，同时保留文本和图像输入。思考模式下它在 Big Bench Audio 上得 98.90、Speech-BFCL 上得 81.13，在 τ-Voice 上任务成功率为 65.51%，平均延迟 1.91 秒。对开发者：做能调用工具的语音助手可以直接从一个模型起步，权重已在 Hugging Face 上提供。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.40738)　`论文` `语音` `开源`

## 🛠 开源与工具

### vLLM v0.33.0：升级 PyTorch 2.14，只发 CUDA 13.0 包

vLLM v0.33.0 包含来自 389 位贡献者的 927 个提交，新增 Reflection Beam-1.0（501B MoE，23B active）、Step-5 Preview 等模型支持，升级到 PyTorch 2.14.0。CUDA 12.9 的 wheel 和镜像不再发布，只提供 CUDA 13.0 产物，镜像也新增了更短的 vllm/vllm 名称。对开发者：还在 CUDA 12.9 环境上的部署，升级前要先切换到 CUDA 13.0。

来源：[GitHub Releases](https://github.com/vllm-project/vllm/releases/tag/v0.33.0rc3)　`工具` `推理` `开源`

### SGLang v0.5.23：单张消费级显卡也能跑超显存 MoE

SGLang v0.5.23 合入 257 位贡献者的 1007 个 PR：可选的 Paged Experts 能在单张消费级 GPU 上运行比显存更大的 MoE 模型，比 CPU offload 最多快 30x；DeepSeek-V4.1 在 GB300 上的 prefill 吞吐最高提升 1.5x；低延迟模式让 DeepSeek-V4.1-Flash 的单用户 decode 在 GB300 上最多快 44%、在 MI350X 上快 75%。它还通过 SGLang-TorchTPU 支持 Google TPU7x。对开发者：本地跑大 MoE 模型多了一个比 CPU offload 更快的选项。

来源：[GitHub Releases](https://github.com/sgl-project/sglang/releases/tag/v0.5.23)　`工具` `推理` `开源`

### vercel-labs 开源 agent-desktop：用无障碍树操作桌面应用

agent-desktop 是一个 CLI 和 C 库，通过操作系统的无障碍树读取和操作 macOS、Windows、Linux 上的桌面应用：每次快照返回 JSON，每个可操作元素都有一个 ref，Agent 对 ref 执行动作后再快照确认，不做像素匹配。用 npm install -g agent-desktop 安装，Apache-2.0 许可。对开发者：给 Agent 加桌面操作能力时，多了一个不依赖截图识别、输出结构化的方案。

来源：[GitHub Trending](https://github.com/vercel-labs/agent-desktop)　`工具` `Agent` `开源`

## ⚡ 快讯

- **Anthropic 更新 S-1：Q3 营收约 $17B** Anthropic 修订版 S-1 显示第三季度营收约 $17 billion、同比增长约 1,127%，但环比增速降至约 47%，季度净亏损 $23.29 billion，采购和租赁承诺约 $895.4 billion。 [cnbc.com](https://www.cnbc.com/2026/11/02/anthropic-ant-s-1-quarter-financials.html) · [HN 讨论](https://news.ycombinator.com/item?id=50337439) · [ft.com](https://www.ft.com/content/4d91dbab-6fe4-45ab-beee-d77e091cb37f)
