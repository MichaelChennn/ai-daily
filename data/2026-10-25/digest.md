# 2026-10-25 · AI 科技日报

## 今日要点

- Block 发布纯语音训练的全双工语音模型 Dessa，号称可在 MacBook Pro M4 Max 上本地运行。
- llama.cpp 合入 DeepSeek-V4.1-Flash 支持，本地可用 GGUF 运行。

## 🔥 头条

### Block 发布全双工语音模型 Dessa，只用语音从零训练

Block 的 AI 研究实验室发布 Dessa：一个全双工的语音到语音模型，能边听边说，不使用任何文本或预训练模型、只用人类对话录音从零训练，训练只用了一台 NVIDIA GB200 NVL72，并可在 MacBook Pro M4 Max 或更高配置上本地运行。目前只公开了演示录音和候补名单，并向少量 AI 安全研究者提供早期访问；对做语音 Agent 的开发者来说，这是“绕开 ASR→LLM→TTS 级联”路线的一个新样本，值得关注后续开放情况。

来源：[Block: Dessa](https://block.xyz/dessa) · [Unite.AI](https://unite.ai/block-unveils-dessa-a-full-duplex-speech-model-trained-on-conversation)　`语音` `模型`

## 🛠 开源与工具

### llama.cpp 合入 DeepSeek-V4.1-Flash 支持

llama.cpp 合并了 PR #31086，新增 DeepSeek-V4.1-Flash（deepseek41 架构）的模型转换与推理支持，其中 Engram 表转为 BF16。想在本地用 GGUF 跑 DeepSeek-V4.1-Flash 的开发者，可以更新到包含该提交的版本试用。

来源：[GitHub](https://github.com/ggml-org/llama.cpp/pull/31086) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xeqf7k/model_dsv41_flash_by_am17an_pull_request_31086/)　`开源` `推理` `工具`

### Together AI 开源反“AI 味”设计技能 Hallmark

Together AI 开源 Hallmark，一个适用于 Claude Code、Codex、Cursor 和 OpenCode 的网页设计 skill：从主题库中挑选三个主题，围绕访客要完成的任务搭页面，并在真实浏览器里检查“每个标题上方都有 eyebrow 标签”之类的机器生成痕迹。和 Impeccable 定位相近，想让 Agent 生成的页面少点模板感可以对比试用。

来源：[GitHub Trending](https://github.com/Nutlope/hallmark)　`工具` `开源` `代码`

### 开源桌面 Agent Cindy：在本地组合 Claude Code 与 Codex

makecindy/cindy 是一个在本机运行、使用真实文件和已登录应用的开源 AI Agent 客户端，首批支持的 harness 是 Claude Code 和 Codex，任务中途可切换模型和 harness，工作区、记忆、skills 和工具保持不变。注意开源的是客户端，后端服务在另一个未包含在此仓库中的代码库里。

来源：[GitHub Trending](https://github.com/makecindy/cindy)　`Agent` `开源` `工具`

## ⚡ 快讯

- **Apollo 首席经济学家：科技行业之外尚无 AI 回报迹象** Apollo 的 Torsten Slok 指出，Mag 7 的人均收入和利润率在上升，S&P 493 却持平，生产率增长也未见 AI 带动。 [apollo.com](https://www.apollo.com/wealth/insights-news/insights/daily-spark/no-signs-of-ai-payoff-outside-the-tech-sector) · [HN 讨论](https://news.ycombinator.com/item?id=50224463)
