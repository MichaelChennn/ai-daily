# 2026-11-14 · AI 晨报

## 今日要点

- OpenAI 推出 ChatGPT Wallet，Agent 付款时拿不到用户的真实卡号，每笔购买都要用户做一次安全验证。
- llama.cpp 发布 v1.0.0，今后 API 和 ABI 不兼容的改动都会通过主版本号体现。

## 🔥 头条

### OpenAI 推出 ChatGPT Wallet，让 Agent 代用户付款

ChatGPT Wallet 与 American Express、Mastercard、Visa 合作打造，Agent 付款时拿不到用户的真实卡号，每笔购买都要用户做一次安全验证；首批在 dots 中面向美国的 ChatGPT Pro 订阅用户上线。OpenAI 同时发布 Commerce Partner Playbook，商家可以上传商品 feed、构建插件或给网站加 WebMCP 工具，让 Agent 在现有系统里完成下单，做电商和支付集成的开发者可以先看这份指南。

来源：[OpenAI News](https://openai.com/index/introducing-chatgpt-wallet)　`产品` `Agent`

### llama.cpp 发布 v1.0.0，今后按主版本号标示 API 变更

llama.cpp 和 ggml 的库版本同时升到 v1.0.0，今后 API 和 ABI 不兼容的改动都会通过主版本号体现；项目目前支持超过 150 种架构变体。这一版移除了废弃的公共 API，把 NextN/speculative API 提升进 llama.h，加入 OCP FP8 KV cache 和主机内存 MoE 专家缓存，并给 llama-server 加了 /v1/audio/speech 接口和 SSRF、CORS 等方面的加固。基于 llama.cpp 做集成的项目，可以把主版本号当作升级时要不要改代码的信号。

来源：[Hugging Face Blog](https://huggingface.co/blog/ggml-org/llama-cpp-v1) · [GitHub Releases](https://github.com/ggml-org/llama.cpp/releases/tag/v1.0.0) · [v.redd.it](https://v.redd.it/ulqil3yfud1i1)　`开源` `推理` `工具`

### DeepSeek API 开放 App 同款搜索、文件解析和语音能力

DeepSeek 把 App 背后的能力搬到了 API：V4.1-Flash（deepseek-flash）在 Messages、Responses 和 Chat Completions 接口里支持联网搜索、URL 读取、文件解析和安全检查，工具调用和上下文拼装在服务端完成；OCR、ASR、TTS、Search 和 Fetch 也能作为独立 API 调用。这些扩展能力在 token 费用之外另收工具费，面向公众的应用必须开启安全检查。想做带搜索和文件问答的应用，可以少自己搭一层工具链。

来源：[DeepSeek News](https://api-docs.deepseek.com/news/news261113)　`产品` `Agent`

### Claude Code 项目改版：协调者调度多个并行线程

在新版 Claude Code 项目里，用户只需描述要做的事，由协调者拆分任务、调度多个线程并汇总结果；每个线程都是一个 Claude Code 云端会话，在自己的分支和仓库副本上工作，线程之间共享记忆，改到同一处代码时按普通 PR 的合并冲突处理。目前以 beta 形式向部分 Pro 和 Max 订阅用户开放，并行线程会更快用完额度，可以分别给协调者和工作线程选择模型与 effort。跨多个仓库的迁移这类多步骤任务，可以整体交给它拆分。

来源：[claude.com](https://claude.com/resources/articles/projects-redesigned) · [HN 讨论](https://news.ycombinator.com/item?id=50492141)　`Agent` `代码` `产品`

## 🧠 模型

### Perplexity 发布决策模型 Decider v1.3 和 Decider Flash v1.3

这两个模型是由生成式 LLM 改成的通用分类器：输入一段状态和若干问题，直接返回各选项的概率分布，而不是逐 token 生成文本。pplx-decider-v1.3 基于 Qwen3.8-27B 微调，pplx-decider-flash-v1.3 是从它蒸馏出的 Qwen3.5-4B 版本，均采用 Apache 2.0 许可、支持文本和图像，新增的 locate 题型可以抽取原文片段并给出字符偏移。做 NER、PII 检测这类封闭式判断时，可以用它代替让通用 LLM 输出标签。

来源：[Hugging Face: perplexity-ai/pplx-decider-v1.3](https://huggingface.co/perplexity-ai/pplx-decider-v1.3) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xv7fku/perplexity_releases_decider_v13_26b_and_decider/)　`模型` `开源`

## 📄 论文

### 论文：动作做不好的决策模型，也能当好 RL 教师

研究者比较了三个决策模型和三个通用 LLM 在 ALFWorld 上当行动者和评判者的表现，再用 JEV 当教师给 GRPO 提供逐步打分。JEV 让 Qwen2.5-1.5B 策略在 ALFWorld 上的成功率从 72.8% 升到 82.9%，在 WebShop 上从 56.8% 升到 71.4%；作者的解释是事后评判能看到行动的后果。给 Agent 训练挑奖励模型时，不必只看它自己会不会做任务。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17167)　`论文` `Agent` `训练`

### SimpleHC：只多 2.4% 训练开销的 Hyper-Connections

论文系统拆解了 Hyper-Connections 架构，发现不做残差混合、只保留可学习的读写门控，效果就能与 mHC 相当，据此提出 SimpleHC，并通过共享内存访问减少对扩展残差状态的重复读取。在最大测试规模下，SimpleHC 比普通残差基线只多 2.4% 的端到端训练时间，从 15B 扩到 30B MoE 模型时性能与 mHC 相当，梯度也更平稳。想在自己模型里加 HC 的团队，可以先参考这个低开销版本。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.05984)　`论文` `训练`

### SO-Arena：评测 System One 决策模型的能力与可靠性

SO-Arena 覆盖 11 个领域、五类能力，除了准确率，还测选项集变化时决策是否稳定，以及没有正确选项时模型能否识别出来。对 21 个模型的评测显示，扩大规模和增加推理的收益因领域差异很大，综合表现最好的 System One 模型可靠性只排第七。选用决策模型时，除了看总分，也要单独看稳定性。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15777)　`论文` `Agent`

### Open Vision Banana：用公开数据把图像生成模型改成感知模型

Vision Banana 把视觉任务当作条件图像编辑来做，但数据、权重和代码都没有公开；OVB 给出完全开放、可复现的配方，从 4B 和 9B 的开放权重基础模型出发，只用公开数据集的 2.1M-3.8M 训练对。它在 Cityscapes 零样本分割上超过 Vision Banana 报告的成绩（73.9 vs. 69.9 mIoU），同时基本保留了基础模型的图像编辑能力。想复现“生成模型做感知”这条路线的研究者有了公开的起点。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15844)　`论文` `图像` `多模态`

## 🛠 开源与工具

### 阿里开源代码审查 CLI Open Code Review

Open Code Review 原是阿里巴巴内部的 AI 代码审查助手，用确定性流水线加 LLM Agent 的混合架构给出行级评论，内置 NPE、线程安全、XSS、SQL 注入等多语言规则，兼容 OpenAI 和 Anthropic，采用 Apache-2.0 许可。项目称在同一底层模型下，它的 Precision 和 F1 明显高于 Claude Code，只用约 1/9 的 token，但 Recall 更低。想在 CI 里接一个噪音少的审查工具，可以用 npm 安装后直接试。

来源：[GitHub Trending](https://github.com/alibaba/open-code-review)　`开源` `代码` `工具`

### Google 在 Antigravity 开放多 Agent 协作功能 /teamwork

/teamwork 把并行探索和专门的“证伪器”（如 Lean 4 证明检查器、未改动的测试套件）配对，自动验证哪些候选解成立；Google 用它把 AV1 解码器 libgav1 改写成 Rust，并调到比原来的 C++ 快 20-30%。外部科学家和开发者现在就能在 Antigravity 里配合 Gemini 4 模型使用 /teamwork 和 /boost，Google 还开放申请，给 10,000 名学术研究者六个月最高用量档的免费使用。

来源：[Google Research](https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/)　`Agent` `工具` `代码`

### Transformers v5.23.0 支持 Inkling 2 Small 和决策头 JEV

新版加入 Thinking Machines Lab 的多模态模型 Inkling 2 Small：语言骨干有 48 层 MoE 解码层，总参数 594B、激活 17B，接受文本和图像输入。另外加入实验性的决策头 JEV 和 decision pipeline，同一个头也能读取 pplx-decider 和 d3 的 255 个答案编码。已经在用 Transformers 的团队可以直接试这两类模型。

来源：[GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.23.0)　`开源` `模型` `工具`

### Modern Web Guidance：给编码 Agent 补上现代 Web 写法

Modern Web Guidance 是一组 skill，把 Web 平台的最佳实践和浏览器兼容性数据直接放进编码 Agent，引导它避开过时写法，由 Google Chrome、Microsoft Edge、Mozilla Firefox 和 MDN 团队共同维护。用 npx modern-web-guidance@latest install 安装，也可以不装直接 search、retrieve 指南，或用 legacy-scan 扫描代码库里的旧写法。

来源：[GitHub Trending](https://github.com/GoogleChrome/modern-web-guidance-src)　`工具` `代码` `Agent`

## ⚡ 快讯

- **Anthropic 分享安全评测建议：先用人工判断校验评分器** Anthropic 总结设计、运行和报告安全评测的经验：先写清要测什么、用人工判断校验评分器、报告不确定性，复杂多轮评测至少 100 条样本。 [Anthropic Research](https://www.anthropic.com/research/building-strong-safety-evaluations)
- **XYBench：测模型能否看出用户问题背后的误解** XYBench 收录 8,115 个编程和日常问题，评测发现每个模型都更倾向于回答用户字面上的请求，而不是背后的真实目标。 [Hugging Face Blog](https://huggingface.co/blog/allenai/xybench) · [Ai2](https://allenai.org/blog/xybench)
- **Brave Search API 支持 Agent 用 x402 按次付费** 不用注册账号：请求先收到 HTTP 402 和报价，Agent 用 Base 链上的 USDC 签名付款后重试，LLM Context 和网页搜索等接口每次 $0.005。 [brave.com](https://brave.com/blog/search-api-agentic-payments/) · [HN 讨论](https://news.ycombinator.com/item?id=50477649)
- **langchain-openai 1.8.0 新增 OpenAIClassifier，停止支持 Python 3.10** 新版加入对接正式版 Decisions API 的 OpenAIClassifier，最低要求改为 Python 3.11 和 langchain-core 1.8.0，3.10 用户会继续装到 1.7.x。 [GitHub Releases](https://github.com/langchain-ai/langchain/releases/tag/langchain-openai%3D%3D1.8.0)
