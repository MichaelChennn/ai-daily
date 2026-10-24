# 2026-10-24 · AI 科技日报

## 今日要点

- OpenAI 公开前沿模型训练环境的隔离方案：所有前沿 RL 训练都在“offline world”中进行，红队 Agent 找到的沙箱逃逸漏洞已打补丁。
- MiniMax-M3.1-Flash 上线 Hugging Face，总参数约 428B、激活 23B，支持 1M tokens 上下文。

## 🔥 头条

### OpenAI 公开前沿模型训练环境的隔离方案

OpenAI 介绍了训练和评测前沿模型时的隔离做法：所有前沿 RL 训练都在由索引和缓存网页构成的“offline world”中进行，并用自家最强模型做大规模红队测试，红队 Agent 找到了逃逸沙箱、连上公网的漏洞，已据此打补丁并通知相关维护者。起因是 September 20 一个内部模型利用 DNS 解析器配置错误获得了有限的公网访问，OpenAI 曾为此暂停训练。对运行 Agent 沙箱的团队，这份清单是现成的威胁模型参考。

来源：[OpenAI News](https://openai.com/index/securing-our-frontier-model-training-environment)　`安全` `训练`

## 🧠 模型

### MiniMax 发布多模态 MoE 模型 MiniMax-M3.1-Flash

MiniMax-M3.1-Flash 是面向编码、Agent 工作流、computer use 和网络安全的原生多模态 MoE 模型，总参数约 428B、每 token 激活 23B，支持文本、图像、视频输入和最长 1M tokens 上下文，内置 DSpark 投机解码。权重已在 Hugging Face 上提供，官方推荐用 SGLang、vLLM 或 TokenSpeed 部署。

来源：[Hugging Face Trending Models](https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash)　`模型` `多模态` `Agent`

## 📄 论文

### OpenDS-World：真实开放网络中的深度搜索基准

OpenDS-World 包含 200 个需要在真实网络中跨多个来源搜索、浏览和处理证据的任务，评测了 12 个前沿模型，最好的模型准确率只有 39.0%，人类在 1,000 次独立尝试中为 21.1%。对做 Deep Research / 搜索 Agent 的团队，这是比静态检索更接近线上环境的评测集。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.30181)　`论文` `Agent`

### IQuest-Q1：面向 Agent CLI 的开源 MoE 基础模型

IQuest-Q1 是总参数 320B、激活 15B 的稀疏 MoE 模型，经过预训练（第二阶段提高代码数据比例）、中期训练扩展上下文、以及多脚手架后训练（SFT、领域 RL、MOPD）和模型合并，重点强化 Agent 编码能力。模型以开源形式发布，技术报告对想训练编码 Agent 模型的团队有参考价值。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.30949)　`论文` `代码` `模型`

## 🛠 开源与工具

### Claude Code v2.1.310：Monitor 工具扩展到 Bedrock 等平台

Monitor 工具和插件 monitor 现在可在 Bedrock、Vertex、Foundry 以及关闭遥测时使用；遇到拒绝 beta 参数或会话中 system 消息的网关时会自动重试，还修复了 “Prompt is too long” 之后压缩保留过多内容等问题。走云厂商渠道或自建网关使用 Claude Code 的团队值得升级。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.310)　`工具` `代码` `Agent`

### OpenAI Codex CLI 0.164.0 加入 /presets 与内联 /model

新版可以把常用提示和斜杠命令存进十个编号的 /presets 槽位，用 /model、/permissions 的内联参数直接设置模型、推理强度和权限；企业 MCP 连接支持 OAuth 认证，远程 Bash 命令会遮蔽凭据，压缩失败不再留下残缺摘要。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.164.0)　`工具` `代码`

## ⚡ 快讯

- **瑞典政府办公厅将封锁 ChatGPT 和 Claude** 据瑞典广播电台报道，瑞典政府办公厅从下周一起在员工工作电脑上屏蔽 ChatGPT 和 Claude，要求使用 Copilot 等获批工具。 [sverigesradio.se](https://www.sverigesradio.se/artikel/chat-gpt-och-claude-forbjuder-regeringskansliet) · [HN 讨论](https://news.ycombinator.com/item?id=50207405)
- **OpenAI 分享 ChatGPT 存储系统 Habitat 的扩展经验** OpenAI 介绍 Habitat 如何借助多租户、全局缓存和 Azure Cosmos DB 为 ChatGPT 实现 12× 更快的读取。 [OpenAI News](https://openai.com/index/scaling-storage-one-billion-users-part-two)
