# 2026-11-01 · AI 科技日报

## 今日要点

- Cisco Talos 披露信息窃取木马 VOLTA：窃取数据后通过 OpenRouter 调用大模型给受害者“估价”，默认模型是 anthropic/claude-opus-4.6。
- 微软开源 4B 电脑操作模型 Mage-VL-Cowork，在 OSWorld-Verified 上达到 66.0%；Opera 推出本地 AI 网页标准提案 WebAI 的早期预览。

## 🔥 头条

### Talos：信息窃取木马 VOLTA 用大模型给受害者“估价”

Cisco Talos 分析了名为 VOLTA-AUTODOXER 的信息窃取木马：它把窃取并补全的身份信息打包，通过 OpenRouter 发给大模型，让模型扮演“法证情报分析师”，输出按变现价值分高中低档排序的“WHAT THEY'RE WORTH”和受害者安全习惯评估；默认模型为 anthropic/claude-opus-4.6，被拒绝时依次换用 moonshotai/kimi-k2 和 google/gemini-2.5-flash。对开发者而言，这说明攻击者已把通用大模型 API 当成分拣赃数据的工具，提供模型网关或 Agent 服务的团队需要关注这类滥用模式。

来源：[blog.talosintelligence.com](https://blog.talosintelligence.com/appraisal-by-ai-model-driven-victim-prioritization-in-the-volta-infostealer/) · [HN 讨论](https://news.ycombinator.com/item?id=50316531)　`安全` `行业`

### 微软开源 4B 电脑操作模型 Mage-VL-Cowork

微软在 Hugging Face 发布 Mage-VL-Cowork，这是一个 4B 的视觉语言模型，在单一策略里同时使用截图驱动的 GUI 操作（computer_use）和持久化终端（bash），不依赖外部编排器；在 50 步预算下 OSWorld-Verified 达到 66.0%，模型卡称这是 4B 模型中的最好成绩，采用 Apache-2.0 许可。对开发者来说，这是一个可以本地部署、研究电脑操作 Agent 的小模型基线，模型卡附带了 SGLang 部署和 OSWorld 评测流程。

来源：[Hugging Face](https://huggingface.co/microsoft/Mage-VL-Cowork) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xk6blw/microsoftmagevlcowork_hugging_face/)　`模型` `Agent` `开源`

### Opera 推出本地 AI 网页标准提案 WebAI 预览

Opera 在 Opera One、Opera GX 和 Opera Neon 中推出 WebAI 早期预览，让网站和浏览器扩展直接调用在用户设备上运行的模型；WebAI 是 Google、Microsoft 等公司支持的网页标准提案，提供 Prompt、Decision 和 Semantic Embeddings 三类 API，默认关闭、需在设置中开启。对前端和扩展开发者来说，这意味着无需自建推理服务、也不按请求付云端费用就能给页面加上生成、分类和语义检索能力，目前支持 64 位 Intel/AMD 的 Windows PC 和 Apple silicon Mac。

来源：[Opera](https://blogs.opera.com/news/2026/10/webai-local-ai-for-the-web-now-in-opera/) · [alternativeto.net](https://alternativeto.net/news/2026/10/opera-introduces-webai-a-proposed-web-standard-to-run-ai-models-locally-in-the-browser/) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xk70qu/standard_for_websites_extensions_to_use_local/)　`产品` `工具`

## 🧠 模型

### Liquid AI 发布决策模型 d1-2B

Liquid AI 发布基于 LFM3-VL-2B 的 d1-2B，它不是聊天模型，而是一次前向计算就返回带概率的结构化答案，面向路由分流、内容审核、意图分类、信息抽取、重排序和视觉检测等决策环节；官方给出的速度是 NVIDIA H100 上每次决策 5.7 ms，许可为 LFM Open License v1.0。对需要在流水线里做大量判断的开发者来说，它可以替代用生成式大模型做分类，省去采样参数和输出解析。

来源：[Hugging Face Trending Models](https://huggingface.co/LiquidAI/d1-2B)　`模型` `多模态`

### 小米开源 0.8B OCR 模型 Xiaomi-OCR-0

小米研究团队开源 Xiaomi-OCR-0，这是基于 Qwen3.5-0.8B-Base、用约 170M 条 OCR 样本训练的 0.8B 视觉语言模型，同时覆盖文档解析和 OCR 问答，在 OmniDocBench v1.6 上得到 96.83，采用 Apache-2.0 许可。对做文档解析和信息抽取的开发者来说，这是一个体积很小、可以用 vLLM 或 SGLang 部署的候选模型。

来源：[Hugging Face Trending Models](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0)　`模型` `开源` `多模态`

## 🛠 开源与工具

### KoboldCpp v1.124 集成 audio.cpp 音乐与 TTS 模型

本地推理工具 KoboldCpp 发布 v1.124，集成了 audio.cpp 中的一部分模型，新增 YuE2 音乐生成和 Qwen3-TTS、VoxCPM2 等 TTS 模型；AI Horde 开始支持 Chat Completions workers，还新增 --paralleltotalcontext 参数让并发请求共享 KV 上下文池。对本地部署用户来说，一个程序里可用的文本、图像、语音和音乐生成能力又多了一批。

来源：[GitHub](https://github.com/LostRuins/koboldcpp/releases/tag/v1.124) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xk1vyk/koboldcpp_v1124_released/)　`工具` `开源` `语音`

### Orkas：开源本地多 Agent 桌面应用

Orkas 是 MIT 许可、本地优先的多 Agent 桌面应用：由 Commander 把目标拆成待办，协调 16 个内置专业 Agent，并可调度 Claude Code、Codex、OpenCode 等外部 Agent，支持项目记忆、定时自动化和各类连接器，可用内置模型或自带 API Key。对想把多个编码 / 办公 Agent 放在同一个界面里管理的开发者，它值得一试，也可以参考其编排设计。

来源：[GitHub Trending](https://github.com/Orkas-AI/Orkas)　`Agent` `开源` `工具`

## ⚡ 快讯

- **GPT-5.6 Sol 在 Codex 中自主通关 Factorio 和平模式** Ryan Madden 让 GPT-5.6 Sol 在 Codex 中以低思考档位通过 Python 库操控游戏，用 13.5 小时游戏时间完成了无敌人的 Factorio 通关。 [ryanmadden.net](https://ryanmadden.net/gpt-56-beats-factorio/) · [HN 讨论](https://news.ycombinator.com/item?id=50318871)
- **bootgpt：装进引导扇区的语言模型** 开源项目 bootgpt 把一个字符级神经网络的推理引擎塞进 510 bytes 的 MBR，开机后会不停生成 Linux 启动日志。 [GitHub](https://github.com/kerlenton/bootgpt) · [HN 讨论](https://news.ycombinator.com/item?id=50315782)
