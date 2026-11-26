# 2026-11-26 · AI 晨报

## 今日要点

- grh-lean 仓库公开了 GRH 的 Lean 4 证明精简版，基于 Levent Alpöge 与 Claude 的证明，目前只通过了机器检查。
- Anthropic 把 Messages API 从 Python 迁到 Rust，每个请求的 CPU 用量降低约 70%；百度放出 ERNIE 5.5 Flash Preview，280B 总参数、14B 激活。

## 🔥 头条

### grh-lean 公开广义黎曼猜想的 Lean 4 证明精简版

这个仓库给出黎曼猜想和狄利克雷 L 函数广义黎曼猜想（GRH）的 Lean 4 证明，基于 Mathlib；证明以 Levent Alpöge 与 Claude 的版本为基础，由作者和 Anthropic 的同事及 Claude 合作缩短，可读版约 300,000 行，紧凑版约 76,000 行。README 说明它目前只通过了机器检查，还没有数学家通读，也没有配套论文。对关注 AI 做形式化数学的开发者，这是一个可以在本地构建复现的完整工程样本。

来源：[GitHub](https://github.com/lsernau/grh-lean) · [HN 讨论](https://news.ycombinator.com/item?id=50648050)　`推理` `行业`

### Anthropic 把 Messages API 从 Python 迁到 Rust

Anthropic 介绍了 Messages API 的迁移：新版每个请求的 CPU 用量降低约 70%，首 token 中位延迟降低约 20%，过程中服务没有下线、功能开发也没有冻结。做法是在生产流量上对比新旧版本、找出差异并自动派 agent 修复，文章的结论是验证取代写代码成了瓶颈。想用 AI 做大型重写的团队，可以参考它“以生产系统为对照”的验证方法。

来源：[Anthropic Research](https://www.anthropic.com/research/migrating-api-to-rust)　`工具` `代码` `Agent`

### 百度发布 ERNIE 5.5 Flash Preview：280B 总参数、14B 激活

ERNIE 5.5 Flash Preview 是基于 ERNIE 5.5 Flash Base 的首个后训练模型，MoE 架构，上下文窗口 1M token，mid-training 把训练上下文从 128K 扩展到 1M，并加了 DSpark 草稿头做投机解码。官方说明它是后训练的中间检查点，训练还没结束。架构和 tokenizer 与 Base 相同，基于 Base 的工具链可以直接沿用。

来源：[Hugging Face Trending Models](https://huggingface.co/baidu/ERNIE-5.5-Flash-Preview)　`模型` `开源`

## 🧠 模型

### LlamaIndex 发布文档解析模型 OCRia-1 与 CPU 版 OCRia-nano-1

OCRia-1 从 Qwen3.5-4B 起步训练，是 4B 文档解析 VLM，把页面图像转成 Markdown（表格用 HTML），ParseBench 2 得分 85.24；OCRia-nano-1 是从它蒸馏出的 8.1M 参数 CPU 流水线，在 LiteParse 里运行，ParseBench-2 得分 59.2，16 vCPU 上每秒 27.8 页。OCRia-1 用基于 Open RAIL-M 的自有许可，年营收或融资总额达到 $2M 的机构商用需要另购授权。

来源：[llamaindex/OCRia-1](https://huggingface.co/llamaindex/OCRia-1) · [llamaindex/OCRia-nano-1](https://huggingface.co/llamaindex/OCRia-nano-1)　`模型` `多模态` `工具`

### KRAFTON 放出 Raon-1 mini 权重：30B-A4B MoE

继预览版之后，KRAFTON AI 在 Hugging Face 放出 Raon-1 mini：从头训练的 30B-A4B MoE 模型，Apache 2.0 许可，原生支持 262,144 token 上下文，训练语言包括韩语、英语、日语、中文等。官方给出 AIME 2026 96.7、GPQA Diamond 86.0。需要可商用、韩语能力强的中等规模开放模型时可以考虑。

来源：[Hugging Face Trending Models](https://huggingface.co/KRAFTON/Raon-1-mini)　`模型` `开源`

## 📄 论文

### RLVB：用可验证的信念奖励治 agent“偷懒”抢答

长任务 agent 常在证据不足时就给出答案；RLVB 在训练时由模拟器算出答案的精确后验，证据不够时奖励继续探索、足够时奖励作答，不需要裁判、critic 或奖励模型。在三个 VLM、三个基准的九组设置里平均提升 17.1%，比用 LLM 裁判过程奖励的 PPO 高 9.3%，GPU 时少 1.6 倍。给 agent 训练提供了一种不靠 LLM 裁判的过程信号。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.32884)　`论文` `Agent` `训练`

### NightWatch：给电脑操作 agent 加一个 0.8B 的实时“看守”

电脑操作 agent 靠离散截图感知屏幕，推理延迟会让动作基于过时状态；NightWatch 用轻量的 NightWatch-0.8B 持续监控界面，不改 agent 的模型、提示词和动作空间。在 OSWorld 上非推理耗时减少 33%、浪费时间减少 53%，成功率持平；DynaCU-Bench 成功率从 39.5% 提到 44.2%。它是即插即用的，可以直接挂到现有 agent 上。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.28947)　`论文` `Agent` `多模态`

### LoomFormer：让注意力头逐 token 重连回路

loom attention 让每个头先对前面各头的输出做“纵向”注意力，再对 token 做常规注意力，用逐 token 的矩阵记忆当第二条残差流。论文称 LoomFormer 能追平多用 3 倍以上算力训练的 Transformer；同样 300B tokens、只多 2% FLOPs，LoomPythia-2.8B 在 0-shot 上追平、5-shot 上超过 Pythia-12B。是值得关注的架构改动方向。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.30634)　`论文` `训练`

### Qwen-Image-HD：分块自回归生成 4K 图像

Qwen-Image-HD 把 Qwen-Image 2.0 改成按 1K 分块、以上方和左侧高清块及历史缩略图为条件逐块生成，避免整图高分辨率微调的高算力和重复条纹。在 Qwen-Image-Bench 4K 上整体优于 FLUX-3-Image-Klein 直接出 4K，训练算力也比整图 4K 微调更低。另有 Wavefront-AutoRegressive 调度，把同一反对角线上的块分到多卡并行，降低单图延迟。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.32736)　`论文` `图像`

## 🛠 开源与工具

### Hugging Face 用编码 agent 把 Inkling 2 Mini 单卡解码提速 40%

Hugging Face 让一个带 inference-optimisation skill 的编码 agent 在单张 RTX PRO 6000 96 GB 上调参一下午，单用户解码从 136 提到 190.6 tok/s，8 用户总吞吐从约 570 提到 716 tok/s，用的是 vLLM nightly 加 DSpark 投机解码。官方服务配方针对 sm100，这篇补上了 sm120 显卡的做法，日志和脚本都已公开，可以照着复现。

来源：[Hugging Face Blog](https://huggingface.co/blog/inkling-2-mini-inference-hillclimb)　`推理` `工具` `Agent`

## ⚡ 快讯

- **Google 开源社交推理评测框架，考 AI 助手能否透过用户叙述推断真相** 框架用多智能体模拟生成带隐藏动机的场景，测了 12 个 LLM，发现模型当助手时明显不如直接旁观准确；框架和 20K 多条样本已开源。 [Google Research](https://research.google/blog/verifiable-social-reasoning-for-llm-assistants/)
- **langchain-anthropic 1.7.13 支持传入自定义 HTTP 和 SDK 客户端** langchain-anthropic 1.7.13 现在可以接收自定义的 HTTP 客户端和 SDK 客户端，同时刷新了模型档案数据。 [GitHub Releases](https://github.com/langchain-ai/langchain/releases/tag/langchain-anthropic%3D%3D1.7.13)
- **SpecEngineeringBench：编码 agent 写的测试能跑通，却很少抓到缺陷** 基准含 78 个 Python 仓库的 100 个实例，七个前沿编码 agent 的 Head Pass Rate 达 91.47%，Fail-to-Pass Rate 只有 26.36%。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.32973)
- **ACAP：把一台机器人拆成多个异步编码 agent 来控制** 由一个 hyper-agent 分配任务、协调依赖，72 次真机实验中任务时间比单 agent 方案减少 28.2%。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.31205)
- **CUA-SEE：随 agent 一起进化的电脑操作评测环境** 根据 rollout 证据同时演化任务和可执行验证器，缓解静态基准难度封顶、诊断粒度粗的问题。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.30962)
