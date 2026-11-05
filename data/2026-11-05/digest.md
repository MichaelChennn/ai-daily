# 2026-11-05 · AI 科技日报

## 今日要点

- Moonshot AI 开放 Kimi K3.1 Pro 权重，MoE 总参数 2.8T、激活 104B。
- OpenAI 的自主流水线为 948 个 Linux 内核本地提权漏洞生成补丁；Anthropic 以 Apache 2.0 开源可证明推理原型 FlashProve。
- Ricursive 发布稠密模型 Ripple-65B Preview，官方称 TerminalBench 2.1 得分 80.52。

## 🔥 头条

### Moonshot AI 开放 Kimi K3.1 Pro 权重

Kimi K3.1 Pro 是 Moonshot AI 的开放权重原生多模态 Agent 模型，从 Kimi K3 后训练而来，MoE 架构，总参数 2.8T、激活 104B，上下文长度 1048576。官方表格中它在 Terminal-Bench 4.0 得 65.7、SWE Marathon v1.1 得 51.7（max 推理档）。官方推荐用 vLLM、SGLang 或 TokenSpeed 部署，有算力自托管大模型的团队可以开始评估。

来源：[Hugging Face Trending Models](https://huggingface.co/moonshotai/Kimi-K3.1-Pro) · [HN 讨论](https://news.ycombinator.com/item?id=50366999)　`模型` `开源` `Agent`

### OpenAI 自主流水线为 948 个 Linux 内核提权漏洞生成补丁

OpenAI 搭建了一条自主流水线，在 Linux 内核中发现、验证并生成补丁，共覆盖 948 个本地提权漏洞。这说明 AI 已能跑通从发现漏洞到给出补丁的完整流程，维护底层代码的团队值得关注这类工具对安全工作量的影响。

来源：[OpenAI News](https://openai.com/index/a-thousand-fewer-paths-to-root)　`安全` `Agent`

### Anthropic 开源可证明推理原型 FlashProve

FlashProve 用 zkSNARK 让模型提供方先对模型做承诺，再证明每条回复确实由该模型生成，证明不泄露权重。在 Llama 4 Maverick（400B MoE、4-bit 权重）上，单张 H100 生成证明约 110 tokens/second，每个 1,024-token 请求的证明约 19 MB，GPU 时间约为 vLLM 直接推理的 70-95 倍。代码、Lean 证明和文档以 Apache 2.0 发布，目前仍是研究原型，关心第三方 API 是否真用了声明模型的团队可以研究。

来源：[anthropic.com](https://www.anthropic.com/research/provable-inference) · [HN 讨论](https://news.ycombinator.com/item?id=50368626)　`安全` `推理` `开源`

### Ricursive 发布稠密开放权重模型 Ripple-65B Preview

Ripple-65B Preview 是 Ricursive Intelligence 芯片设计平台所用专有模型的通用版本，采用稠密 Transformer 而非 MoE，在 12 trillion token 上预训练，支持最长 1M 上下文。官方称它在 TerminalBench 2.1 上得 80.52，是美国开放权重模型中的最好成绩。模型已上线 Hugging Face、Together AI、GMI Cloud 和 OpenRouter，官方称它能在 NVIDIA DGX Spark 等本地设备上高效运行。

来源：[Hugging Face Trending Models](https://huggingface.co/ricursiveAI/Ripple-65B-Preview) · [ricursive.com](https://www.ricursive.com/ripple)　`模型` `开源` `代码`

## 🧠 模型

### OpenAI 发布 Images 2.6

Images 2.6 带来更快的图像生成、GIF 制作、更精确的编辑和新的 API 控制项，覆盖 ChatGPT、Codex 和 API。在产品里接入 OpenAI 图像生成的开发者可以留意这次 API 的变化。

来源：[OpenAI News](https://openai.com/index/introducing-images-2-6)　`图像` `产品`

### Deep Principle 开放科学模型 Hydrogen-1.0

Hydrogen-1.0 基于 GLM-5.3 后训练，面向化学、材料科学和生命科学，模型大小 753B，BF16 权重采用 MIT License。团队自述它在 FrontierScience Research 上通过率 38.3%，高于 GPT-6 Astra（max thinking）的 33.3%。需要自部署科研辅助模型的团队可以参考，不过评测数字来自团队自己的设置。

来源：[Hugging Face](https://huggingface.co/deep-principle/Hydrogen-1.0) · [Reddit 讨论](https://www.reddit.com/gallery/1xnjhdd)　`模型` `开源`

### Cohere Embed 5 和 Rerank 5 上线 OpenRouter

Cohere 的检索模型 Embed 5 和 Rerank 5 现在可以通过 OpenRouter 的统一 API 调用，统一计费，不需要额外 SDK。Embed 5 Pro 和 Fast 共享同一个向量空间，可以用 Pro 建索引、用 Fast 处理查询；Rerank 5 的分数经过校准，一个阈值就能跨查询过滤弱相关内容。已经在用 OpenRouter 的 RAG 应用可以少接一家供应商。

来源：[Cohere](https://cohere.com/blog/embed-rerank-5-openrouter)　`模型` `工具`

## 📄 论文

### Axion 1.0：开放完整训练配方的 Agent 基础模型

Axion 1.0 只用两轮轻量 SFT 加一轮强化学习训练，不做专门的 mid-training、DPO 或 on-policy 蒸馏，论文称它在多项 Agent 基准上可与领先商业模型竞争。除权重外，作者还开放了数据构造、生成、过滤、验证、提示词和训练代码；Hugging Face 上的 Axion 1.0-35B 复现检查点是 MoE，约 35B 总参数、3B 激活，采用 Apache License 2.0。想复现 Agent 后训练流程的团队可以直接拿来改。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03233) · [Hugging Face](https://huggingface.co/Axion1-0/Axion-1.0-35B)　`论文` `Agent` `开源`

### SpecPilot：用 Agent 自动优化投机解码

SpecPilot 是一个自主 Agent 循环：成本模型找出当前系统与上限之间最大的差距，并行 Agent 探索并整合有效方向，token forcing 逐个对照原始系统的输出来防止奖励作弊。它发现了无损的 12-bit 权重格式、面向混合循环目标模型的树验证等机制，在不训练、不损失质量的前提下，把单请求相对自回归解码的加速比从 4.46 倍提高到 10.87 倍，批处理从 1.94 倍提高到 3.93 倍。部署投机解码的推理团队可以参考这种按部署场景自动调优的思路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.02501) · [Reddit 讨论](https://www.reddit.com/gallery/1xnjrgj)　`论文` `推理` `Agent`

### LoCo：教推理模型判断何时停止思考

LoCo 从模型自己的推理轨迹中找出可能过度思考的状态，冻结前缀后重新生成更短且经过验证的续写，再用 DPO 训练这些状态上的偏好对。在五个数学和三个代码基准上，输出长度在数学上减少 41.7%–45.4%、代码上减少 23.4%–36.3%，准确率持平或提升。训练数据完全来自自生成的数学轨迹，想压缩推理 token 成本的团队可以参考。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.04814) · [Reddit 讨论](https://www.reddit.com/gallery/1xnrcfw)　`论文` `推理` `训练`

### Caper：先在沙箱预执行，再审批编码 Agent 的命令

Caper 在快照沙箱里预先执行编码 Agent 提出的每条 shell 命令，把观察到的实际影响交给独立审批者判断：允许的命令提交，被拦截的回滚，并附上 Agent 可以据此调整的理由。与六个现有系统相比，它在 SABER 上的有害结果率为 6.7%（其他至少 14.8%），在作者构建的 YoloFS-Ext 上为 7.8%（其他至少 35.3%），同时只拦截了 1.0% 的安全对照任务。给编码 Agent 做权限控制的开发者可以参考这种按后果而不是按命令文本审批的做法。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.40753)　`论文` `安全` `Agent`

## 🛠 开源与工具

### llama.cpp v0.9.0 支持 FP8 E4M3 和 Mistral Large 4

llama.cpp v0.9.0 加入 OCP FP8 E4M3 量化，新增 flash attn ext rows 算子让统一 KV cache 在多序列推理时更高效，并支持 Clover、Limite、Metis-1.6 和 Mistral Large 4 四个新架构。音频方面新增 Chatterbox TTS、Nemotron 3.5 Transcribe，Gemma 4 E2B/E4B 的 prefill 也有大幅优化；ggml 升到 v0.29.0，带来基于 NCCL 的多节点张量并行。本地推理用户升级后可以试 FP8 量化和多机部署。

来源：[GitHub Releases](https://github.com/ggml-org/llama.cpp/releases/tag/v0.9.0)　`开源` `推理` `工具`

### NVIDIA 开源 Auto Ontology，给 Agent 提供企业数据语义层

Auto Ontology 是 NVIDIA 的 Python 框架，从企业元数据生成本体和语义目录，调和不同系统里的冲突定义，并通过 MCP、CLI 和 API 提供给任意 Agent 使用。自然语言问题会被翻译成 SQL，在已连接的数据库上执行，回答附带来源信息，项目采用 Apache License 2.0。做企业数据问答或 text-to-SQL Agent 的团队可以拿它当上下文层。

来源：[GitHub Trending](https://github.com/NVIDIA/auto-ontology)　`开源` `Agent` `工具`

### Collinear AI 公开 CWE-bench v2 漏洞修复基准

CWE-bench v2 公开了 100 个任务，覆盖 91 种 CWE：Agent 拿到真实开源仓库和一句指令，要找出并修复安全弱点。在评测的 11 个模型中，Gemini 4 Argon 以 67.8% pass@1 领先，Claude Opus 5.5 为 67.3%；DeepSeek V4.1 Flash 以每次 $0.04 拿到 57.0%，但领先者仍有 19% 的任务每次都失败。公开集、评分器和 harness 都已开放，可以直接用来评测自己的安全 Agent。

来源：[Hugging Face Blog](https://huggingface.co/blog/cwe-bench)　`安全` `代码` `工具`

### Ai2 发布长文档状态追踪基准 StateBench

StateBench 用四个难度等级测试语言模型能否在长文档中追踪不断变化的变量值。Gemini 3.8 Flash、Claude Opus 5.5、GPT-6 Sol 和 Luna 在较易的两级表现良好，但在最长的 general finite 问题上准确率跌到 13% 或更低；从零训练时，Gated DeltaNet 和混合架构在前三级几乎完美泛化，Transformer 则在长序列上退化。做长上下文应用或比较模型架构的团队可以用它检验状态追踪能力。

来源：[Ai2](https://allenai.org/blog/statebench)　`论文` `推理`

### Hugging Face 提出 Transformers 模型集成契约 MIC

Model Integration Contract 由缩小版 fixture 模型、可运行的使用示例和人工审核的基线输出组成，在便宜的 CPU runner 上就能发现完整集成测试才能抓到的回归，例如曾在 main 上留存近两个月的 UMT5 bug。配套 CLI tmic 可以起草契约、构建 fixture 并在本地记录基线，由 LLM 起草、人来审批。给 Transformers 接入新模型的作者可以用它降低兼容性回归的风险。

来源：[Hugging Face Blog](https://huggingface.co/blog/transformers-mic)　`开源` `工具` `模型`

## ⚡ 快讯

- **OpenAI 将收购 Pierre Computer Company** OpenAI 将收购 Pierre Computer Company，以扩充 Codex 在构建、理解和审查代码方面的工具。 [OpenAI News](https://openai.com/index/openai-to-acquire-pierre) · [HN 讨论](https://news.ycombinator.com/item?id=50366863)
