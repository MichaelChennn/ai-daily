# 2026-11-23 · AI 晨报

## 今日要点

- OpenAI 首席科学家 Jakub Pachocki 提议把 perplexity 作为各家模型开发方之间的比较指标和共同安全标准的依据，并公开了 OpenAI 内部的预训练测量。
- Dragos 用近两百万条带 canary token 的提示发现，至少三家 AI 服务商的数据遭窃，Zero Data Retention 标记也常被无视。
- 开放模型方面，inclusionAI 发布 560B 总参数的医疗模型 LingSante-3.1-flash，OVHcloud 发布可在笔记本上运行的 Olala-v1.0-mini-7A1B。

## 🔥 头条

### OpenAI 首席科学家提议用 perplexity 统一衡量 AI 进展

OpenAI 首席科学家 Jakub Pachocki 发文，主张把 perplexity（即 cross-entropy loss）作为各家模型开发方之间的比较指标和共同安全标准的依据，并公开了 OpenAI 内部的预训练 perplexity 测量；文中称 log-perplexity 降到约 0.76 的模型开始在数学开放问题上给出突破性结果。他还提议设定基于 perplexity 等指标的共同上限，在理解和监控 AI 行为的能力达到具体里程碑之前不越过。文章也承认 chain-of-thought 推理带来的能力提升不会体现在 perplexity 上，所以对开发者来说，它更适合当作预训练进展的标尺，而不是替代任务评测。

来源：[OpenAI News](https://openai.com/index/perplexity-and-intelligence)　`安全` `训练` `行业`

### Dragos 用 canary token 追踪提示泄露：多家 AI 服务商遭入侵

Dragos 在五个月里向常用 AI 服务提交了近两百万条带唯一 URL 和 canary 凭证的提示，发现至少三家服务商的数据被盗，且在 Dragos 通知之前都没有察觉；推理市场上的多个转售商能用普通日志功能查看并保留客户提示。一家中国 AI 实验室抓取了发给其模型的提示中过半的秘密链接，其中包括约三分之二标记了 Zero Data Retention 的请求。对开发者来说，经路由或转售商调用模型时，提示里的密钥和内部链接都应视为可能外泄，ZDR 标记不能当作保证。

来源：[dragos.com](https://www.dragos.com/blog/ai-supply-chain-security-canary-tokens) · [HN 讨论](https://news.ycombinator.com/item?id=50596511)　`安全` `行业`

### inclusionAI 发布医疗模型 LingSante-3.1-flash：560B 总参数、激活 25B

inclusionAI 发布开放权重的医疗 MoE 模型 LingSante-3.1-flash，基于 Ling-3.1-flash，560B 总参数、每 token 激活 25B，支持 1M token 上下文，面向复杂医学推理、医疗沟通、循证研究和长流程医疗任务；模型卡称它在医疗专业行为基准上总排名第二，仅次于 GPT-6 Astra。模型以 MIT 许可发布，附 vLLM 和 SGLang 部署说明；模型卡同时写明它只用于研究和评测，不是医疗器械，不能单独作为诊断、处方或治疗的依据。

来源：[Hugging Face Trending Models](https://huggingface.co/inclusionAI/LingSante-3.1-flash)　`模型` `开源`

## 🧠 模型

### OVHcloud 开源小模型 Olala-v1.0-mini-7A1B：6.8B 总参数、约 1B 激活

OVHcloud 旗下的 OVHai LLM 发布 Olala-v1.0-mini-7A1B，一个面向聊天、指令遵循和工具调用的小型推理模型，采用 Mamba-3 / attention 混合的 MoE 架构，6.8B 总参数、每 token 约 1B 激活，36 层中只有 7 层保留 KV cache，上下文 32K。模型在三台欧洲超算上用 12.8T token 训练，以 Apache 2.0 开放权重。对开发者来说，这是一个能在笔记本上跑、可商用的小模型，也可以直接走 OVHcloud AI Endpoints 的 OpenAI 兼容 API。

来源：[Hugging Face Trending Models](https://huggingface.co/OVHaiLLM/Olala-v1.0-mini-7A1B)　`模型` `开源`

### KAIST 发布 KORMo-Web-11B：韩英双语、看截图操作网页

KAIST MLP Lab 发布 KORMo-Web-11B，它基于从零训练的 KORMo-10B 语言模型，经 KORMo-VL 扩展成网页 Agent，同时保留原有的 LLM 和 VLM 能力，主要通过截图操作浏览器，不依赖完整 DOM。在 Online-Mind2Web 上，它的英文成功率 31.3%、韩文 33.7%，韩文成绩比表中最强的非 KORMo 开放权重基线高 13.5 个百分点，英文略低于 OpenWebRL-4B 的 32.7。权重以 Apache-2.0 发布，附 vLLM 推理路径和浏览器 harness，适合需要韩语网页自动化的场景。

来源：[Hugging Face Trending Models](https://huggingface.co/KORMo-VL/KORMo-Web-11B)　`模型` `Agent` `多模态`

### tiny-voca：4.5M 参数的英文 TTS，CPU 上约 70x 实时

开发者 n4ze3m 发布英文语音合成模型 tiny-voca，连同波形生成器在内只有 4.5M 参数，用约 18 小时合成语音从零训练，提供 F2（女声）和 M2（男声）两个音色，输出 24 kHz 单声道音频。模型卡称它在四个 CPU 线程上约比实时快 70x，提供 PyTorch 权重和 ONNX 导出，Apache-2.0 许可。需要在端侧或无 GPU 环境做英文 TTS 的开发者可以试试。

来源：[Hugging Face Trending Models](https://huggingface.co/n4ze3m/tiny-voca)　`语音` `开源`

## 📄 论文

### 论文：Grid Robotics 提出 agentic robotics 的评测框架与路线图

Grid Robotics 等作者的立场论文认为，GPT-6 Astra 的发布标志着 agentic robotics 这一新范式出现：由基础模型加 embodied harness 构成的 Embodied System 2 是决策核心，难点在于在有限反应时间、机械限制和不可逆后果等物理约束下，把通用推理变成可验证的动作。论文提出同时衡量模型能力和闭环系统表现的评测框架，并给出走向 sustained autonomy 的研究路线图。对做具身 Agent 的开发者，它提供了一套可以对齐的定义和评测维度。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18359)　`论文` `Agent`

## 🛠 开源与工具

### mod_wsgi 作者推出 AI 辅助开发的 Rust Python 服务器 Muru

mod_wsgi 的作者 Graham Dumpleton 发布 Muru，一个借助 AI 编写的 Rust 服务器，用来在开发和生产环境中运行 ASGI 与 WSGI 的 Python 应用，并在开发过程中持续发文详细记录。他说 AI 表面上承担了大量工作，但判断哪里还不够好仍要靠他自己。对 Python Web 开发者，这是一个值得关注的新部署选项，也是一份资深开发者用 AI 写基础设施的实录。

来源：[simonwillison.net](https://simonwillison.net/2026/Nov/21/muru/) · [HN 讨论](https://news.ycombinator.com/item?id=50597959)　`工具` `代码`
