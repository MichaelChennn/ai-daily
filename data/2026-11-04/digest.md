# 2026-11-04 · AI 科技日报

## 今日要点

- Postman 桌面版被报告在启动时自动给 Claude Code 和 Codex 安装插件和 SessionStart hook，Postman 回应会让老用户的 opt-in 更清楚。
- Revolut 用 56 张 Nvidia B200 自托管 GLM-5.3 做编码；开放权重的 Qwen3.8-Flash-Next 借助 uni-robot-agent 在 RoboDojo 上超过了已发表的 GPT-6 Astra-RoboProbe 结果。
- GPT-6 Astra 读写权重的论文被指把不同技术混为一谈，Simon Willison 则用笔记本上的 Qwen 3.8 27B 复现了“看权重猜游戏”的实验。

## 🔥 头条

### Postman 桌面版被指自动给 Claude Code 和 Codex 装插件

GitHub 上的一份报告显示，Postman 桌面版 12.33.4 在已登录的老用户启动时自动安装了 Claude Code 和 Codex 插件，并注册 SessionStart hook，让 Agent 在处理任何“非平凡”的 API 工程任务前先加载 Postman 的 skill；报告者也说明，这份报告不能证明数据被上传。Postman 回复称插件是有意和桌面版捆绑的，会让老用户的 opt-in 更清楚，并复查 hook 审批和 session-start 行为。用 AI 编码工具的开发者值得检查一下全局配置里有没有自己没装过的插件和 hook。

来源：[GitHub](https://github.com/postmanlabs/postman-app-support/issues/14370) · [HN 讨论](https://news.ycombinator.com/item?id=50354960)　`安全` `工具` `Agent`

### Revolut 自托管 GLM-5.3 写代码，减少对 Claude 的依赖

据 The Register 报道，英国金融科技公司 Revolut 用 56 张 Nvidia B200 自托管 GLM-5.3，用于内部 AI 编码，标题称成本降低 10x。最大的性能提升不是靠加 GPU，而是调超参、改用 NVFP4 量化、拆分 prefill 和 decode、调整上下文长度，最终在约 256,000 token 的上下文下做到首 token 延迟低于 3 秒、生成约 200 tokens/s。GLM 只支持文本，视觉请求仍通过模型路由交给 Gemini 或 GPT Luna；对考虑自建编码模型的团队，这是一份带具体指标的参考。

来源：[theregister.com](https://www.theregister.com/ai-and-ml/2026/11/03/british-fintech-revolut-slashes-ai-coding-costs-10x-by-cutting-out-claude-and-going-self-hosted/5307345) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xn568h/british_fintech_revolut_slashes_ai_coding_costs/)　`行业` `推理` `代码`

### “权重空间编程”论文遭质疑，本地 Qwen 3.8 27B 也能看权重猜游戏

spaCy 作者 Matthew Honnibal 撰文指出，GPT-6 Astra 读写权重的论文里，“只看原始权重”的设定只出现在 17K–172K 权重的小网络上，涉及真实语言模型的实验都用了 Python，头条的 Qwen 结果（MATH-500 从 7.9% 到 48.1%）还能把模型在最多 50 批练习题上跑起来，因此不该和直接读权重的实验当成同一种能力。Simon Willison 则在笔记本上用 17GB 的 Qwen 3.8 27B 跑了论文里“看权重猜游戏”的实验，在不给任何工具的情况下认出了 Pac-Man、Pong 和 Breakout，Freeway 没认出来。这项结果值得关注，但“模型能直接改权重”的说法要回到具体实验设定去看。

来源：[honnibal.dev](https://honnibal.dev/blog/astra-read-write-misleading) · [simonwillison.net](https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/) · [The 'Astra can read and write weights to improve Qwen' post is misleading](https://news.ycombinator.com/item?id=50351111) · [Qwen 3.8 27B on my laptop can interpret model weights, too](https://news.ycombinator.com/item?id=50355251)　`模型` `训练` `行业`

### 开源 harness 让 Qwen3.8-Flash-Next 操作机器人

uni-robot-agent 是一个让通用大模型通过工具调用操作机器人的统一 harness，面向开放权重模型，并支持后续训练。论文报告，不用特权输入、开箱即用的 Qwen3.8-Flash-Next 在 RoboDojo 上得分 31.39，超过已发表的 GPT-6 Astra-RoboProbe 结果 28.97，在 19 个真实任务上也有竞争力。想用开放模型做机器人 Agent 研究或继续训练的团队，可以直接拿它当基线。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.01560) · [GitHub](https://github.com/Open-RUA/uni-robot-agent)　`Agent` `开源` `论文`

## 🧠 模型

### NVIDIA 开放通用语音增强模型 NemotronLabs RE-USE

NVIDIA NemotronLabs RE-USE 是一个只有 9.6 million 参数的多语言通用语音增强模型，能修复噪声、混响、削波、带宽受限、编解码失真、丢包和低质量麦克风等问题，支持 8 到 48 kHz 的多种输入采样率。模型卡写明可以商用，许可是 OpenMDW License Agreement, version 1.1。它体量小、与语言无关，适合放在 ASR 或语音 Agent 前面做音频清洗。

来源：[Hugging Face](https://huggingface.co/nvidia/NVIDIA-NemotronLabs-RE-USE) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xmorim/nvidianvidianemotronlabsreuse_hugging_face/)　`语音` `模型` `开源`

## 📄 论文

### CrossSWE：跨仓库协同开发基准，最强模型 Pass@1 仅 58.48%

CrossSWE 收录 171 个真实实例，覆盖 165 个仓库、20 个技术领域和 13 种编程语言，要求 Agent 在多个相互依赖的仓库里协同修改代码，只改其中一部分无法通过测试。评测的五个模型里，最强的 GPT-6.1 Sol 也只有 58.48% Pass@1，跨仓库不一致是最常见的失败类型（44.2%）。在多仓库项目里用编码 Agent 的开发者，接口一致性仍需要重点把关。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.01484)　`论文` `代码` `Agent`

### CUA-Master-27B：从教学视频挖任务，训练电脑操作 Agent

CUA-Master 提出嵌套双循环的递归改进框架：外循环持续引入开放世界语料，并根据模型当前的弱点指导下一轮数据构造；内循环从教学视频中挖掘真实工作流作为种子任务，再合成多样、可验证的复杂任务，采集轨迹时用带反馈的快照回滚重试。CUA-Master-27B 在 OSWorld Verified 上得 80.2，OSWorld 2.0 上 36.9，WeaveBench 上 43.9。做 GUI Agent 数据管线的团队可以参考这套数据飞轮。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03126)　`论文` `Agent` `训练`

### 协作智能基准：测 AI Agent 当队友的能力

Collaborative Intelligence Benchmark 用 240 个任务、8 个团队协作维度衡量 AI Agent 作为队友的表现，任务来自真实记录或现有基准，结果可程序化验证，而且只在模型单独能解的任务上计分。评测 18 个模型后，得分最高的 Gemini 4 Argon（high effort）也只有 82.2 分；前沿模型几乎都会拒绝不安全的捷径，但在冲突中只有 14% 达成最佳整体结果，接手被弱模型作弊过的任务时通过率从 97% 降到 81%。搭多 Agent 系统时，交接和施压场景值得单独测试。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.02633)　`论文` `Agent` `安全`

## 🛠 开源与工具

### colibri：在普通电脑上跑超大 MoE 模型的 C 推理引擎

colibri 是用 C 写的分层推理引擎：热专家放 GPU（CUDA、Vulkan），温专家放内存，冷专家从 NVMe 流式读取，支持 GLM-5.2/5.3、Kimi K3、DeepSeek V4 Flash、Qwen3.8-Flash-Next 等模型，采用 Apache 2.0 许可。最低 8 GB 内存即可运行，GPU 可选；作者在 RTX PRO 4000 上跑 Qwen3.6-35B-A3B 的解码速度为 104.8 tok/s。它内置 OpenAI 和 Anthropic 兼容的 API，Claude Code 等现有客户端可以直接连到本地模型。

来源：[GitHub Trending](https://github.com/JustVugg/colibri)　`推理` `开源` `工具`

### llama.cpp 合并 Nemotron 3.5 Transcribe 支持

llama.cpp 合并了 PR #31471，支持 NVIDIA 的开放权重语音模型 Nemotron 3.5 Transcribe，可以离线转写 40 种语言，支持 prompt 上下文和说话人标注。目前只接受 BF16 检查点，FP8 和 NVFP4 版本还不能转换，词级时间戳和流式也不在这次范围内；用 llama-server 时要加 --reasoning off，否则只返回推理内容、没有转写结果。本地离线转写多语言长录音多了一个开源选项。

来源：[GitHub](https://github.com/ggml-org/llama.cpp/pull/31471) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xmu0iz/mtmd_add_nemotron_35_transcribe_support_by/)　`语音` `开源` `推理`

### Claude Code v2.1.318：可查看登录到期时间

Claude Code v2.1.318 在 claude auth status 和 claude -p 的 JSON 结果里加入 claude.ai 登录的到期时间，并在到期前 10 天给 claude -p 的文本输出加一行 stderr 警告；mod 的 $.model.fork 新增 effort 选项。这一版还修复了畸形工具调用重试耗尽后 --continue 丢失之前对话的问题（2.1.314 引入的回归）。在 CI 里跑 claude -p 的团队可以借此提前发现凭据过期。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.318)　`工具` `代码` `Agent`

## ⚡ 快讯

- **Ai2 发布 StateBench，测长文档里的状态追踪** Ai2 的 StateBench 显示，前沿模型在最长的 general finite 问题上准确率降到 13% 或更低；从头训练时 Transformer 始终学不会 general finite 问题。 [Hugging Face Blog](https://huggingface.co/blog/allenai/statebench)
