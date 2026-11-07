# 2026-11-07 · AI 科技日报

## 今日要点

- Anthropic 介绍 Agent 记忆的分层和 dreaming 离线整理；Mistral Studio 新增 managed agents、workflows 和 Mistral MCP server。
- Cloudflare 以 MIT 许可开源安全审计 skill；微软 Foundry Local 能在 24 GB 显存的显卡上本地运行 Qwen3.8-27B 并接入 GitHub Copilot。

## 🔥 头条

### Anthropic 详解 Agent 记忆分层与 dreaming

Anthropic 的研究文章介绍了 dreaming：Agent 离线回看日志，修正记忆里的错误、生成新的笔记和表示。实验在 Claude Managed Agents 上进行；在一项测试中，同时用搜索和 wiki 时 Claude 的得分随 wiki 增长从 54% 升到 61%，只用搜索为 53%，每题还省下约 20,000 tokens。构建长期运行 Agent 的开发者可以参考这套记忆分层和定期整理的思路。

来源：[Anthropic Research](https://www.anthropic.com/research/components-of-agent-memory)　`Agent` `产品`

### Mistral Studio 新增托管 Agent、工作流和 MCP 服务器

Mistral 更新 Studio 平台，新增 managed agents、workflows 和 enterprise context 等功能，模型和平台可以部署在云、自有 VPC 或本地环境。新的 Mistral MCP server 让开发者用 Mistral Vibe 或现有编码 Agent 在本地测试，再用一条命令部署到 Studio；OpenTelemetry trace 记录每一步的模型调用、工具调用和审批。需要私有化部署 Agent 的企业团队，在模型之外多了一套运行、部署和排查工具。

来源：[Mistral AI News](https://mistral.ai/news/build-with-studio/)　`Agent` `产品` `工具`

### Cloudflare 开源多阶段安全审计 Agent skill

Cloudflare 发布 security-audit，一个让编码 Agent 做多阶段安全审计的 skill，以 MIT 许可开源。它的原则是核查发现的 Agent 永远不是发现它的那个 Agent，结果写入 findings.json 并按 schema 校验；运行需要支持工具调用和并行子 Agent 的模型。想用编码 Agent 做代码安全审计的团队可以直接装上，得到可机器读取、经过独立核验的结果。

来源：[GitHub Trending](https://github.com/cloudflare/security-audit-skill)　`安全` `Agent` `开源`

### 微软 Foundry Local 支持本地运行 Qwen3.8-27B 写代码

微软 Foundry Local 现在可以在本地运行 Qwen3.8-27B 并接入 GitHub Copilot：4-bit 量化后模型约 18 GB，24 GB 显存的消费级显卡即可运行、支持 64K 上下文，32 GB 以上显存最长可到 262K。推理用 DFlash2 投机解码加速，需要 Foundry Local CLI 0.13.0 或更高版本。有 NVIDIA 显卡、又不想让代码离开本机的开发者可以试一试。

来源：[devblogs.microsoft.com](https://devblogs.microsoft.com/foundry/foundry-local-agentic-coding-qwen3-8-27b/)　`代码` `推理` `工具`

## 🧠 模型

### Nace AI 开放 Drex 决策模型家族

Drex 是四个开放的决策模型，规模为 8B（DLM）、9B（v1.5）、35B with 3B active（v2.0）和 27B（Max）：输入状态和一组选项，直接返回各选项的概率分布，不做自回归解码。论文称 Max 典型请求耗时 183 ms，在 Decision Bench v4 上落后 Claude Opus 5.5 1.6 分。只需在固定选项中做选择的分类、判断、打分场景，可以用它省掉长链推理和输出解析。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.07854) · [i.redd.it](https://i.redd.it/fez7h4dxu00i1.png)　`模型` `开源` `推理`

### Linum 开放训练成本约 $21K 的 2B 文生图模型

Linum AI 发布研究检查点 P-JiT 21K：2B 参数，用 660M 样本训练，算力成本约 $21K，许可为 apache-2.0。训练数据刻意去掉了渲染文字类图片，所以它不能生成文字或海报；官方说明这是通往下一个视频模型的过渡产物，不是生产模型。关注低成本训练的开发者可以拿它作参考。

来源：[Hugging Face](https://huggingface.co/Linum-AI/pjit-21k)　`模型` `图像` `开源`

## 📄 论文

### SLA：在持续预训练中加入空间对齐的 VLA 模型

SLA 从预训练的 pi05 策略出发，在持续预训练中联合优化动作预测，以及中间视觉嵌入与冻结 3D 感知模型空间表示之间的对齐。所有辅助组件只在训练时使用，可以直接复用已有 VLA 权重，推理架构保持不变。做机器人操作的团队可以在不改部署的前提下借鉴这种训练方式。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08373)　`论文` `多模态` `训练`

### VFlash：一次前向生成整段视觉规划

VFlash 让 VLM 不再逐个坐标 token 生成框、轨迹这类视觉规划，而是用轻量 drafter 一次前向生成整个 primitive，并直接接受结构有效的预测。初步测量显示 3D 点运动预测的生成快约 25x；以 VFlash 规划为条件的世界动作模型在 MolmoSpaces 任务套件上平均成功率 70.2%，基线为 62.6%。在机器人和自动驾驶里用 VLM 输出空间规划的系统，可以借此降低解码延迟。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.08449)　`论文` `多模态` `推理`

### Harness-S：用兄弟 harness 救回失败轨迹训练 Agent

Harness-S 从同一基础 harness 演化出一组各自修复不同失败的兄弟 harness；只有基础 harness 下所有初始尝试都失败时，才让同一策略在选中的兄弟 harness 下重新采样，用这些轨迹替换失败组做强化学习。在 AppWorld、SWE-Gym 和 DBBench 上，训练后的策略回到原 harness 时明显优于只训练策略的做法。做 Agent 强化学习的团队可以把 harness 的改进沉淀进模型本身。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.04277)　`论文` `Agent` `训练`

### BestRand：稳定且低成本的基准压缩方法

论文分析了用子集估计完整基准分数的误差分布：多数随机子集误差很小，少数误差很大，呈长尾分布。据此提出的 BestRand 在 70+ 个文本、多模态和 Agent 基准上验证，相比已有方法把高误差风险降低 50.2%、估计误差平均降低 16.4%，构建成本只要 51.3%。评测预算紧张的团队可以用它挑出小子集，代替跑完整基准。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.00883)　`论文` `训练`

## 🛠 开源与工具

### Claude Code v2.1.319 支持后台运行 MCP 任务

新版本中，MCP 服务器以任务方式运行工具调用时，Claude Code 会立即把它移到后台，完成后再把结果告诉 Claude；新增 permissions.denyInsteadOfPrompting 设置，需要等待权限确认的工具调用会直接被拒绝，回合继续。关闭遥测或 feature flag 时 auto mode 也有变化：服务器无法检查的调用会询问或拒绝，不再回退到内置分类器。在网关后面或无人值守运行 Claude Code 的团队，升级前要留意这些行为变化。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.319)　`工具` `代码` `Agent`

### llama.cpp 合并 Kimi-K3.1-Pro 文本模型支持

llama.cpp 合并了 PR #31779，加入 Kimi-K3.1-Pro 文本模型支持：K3.1 复用 K3 的大部分结构，但把全注意力的 MLA 层换成了 DSA。视觉塔和 mm_projector 暂时跳过，目前只支持文本。硬件足够的用户现在可以用 llama.cpp 在本地运行这个模型。

来源：[GitHub](https://github.com/ggml-org/llama.cpp/pull/31779)　`开源` `推理` `工具`

### Apple 用小型神经网络加速 RAG 向量检索

Apple 在 ICML 2026 论文中提出，为固定的 key 数据库离线训练小型神经网络，学会把查询路由到最佳匹配：SupportNet 用于聚类路由，KeyNet 可以作为现有 IVF 索引前面的 query rewriter。实验中，KeyNet 最大模型达到 99% 召回所需时间最多减少约 8×（0.23 ms 对 1.8 ms）。key 库相对固定、查询量大的 RAG 和推荐系统，可以考虑用离线训练换在线延迟。

来源：[Apple Machine Learning Research](https://machinelearning.apple.com/research/faster-retrieval)　`论文` `推理`

## ⚡ 快讯

- **Anthropic 分析科学家如何使用 Claude** Anthropic 分析 207,000 个科研会话发现，科学家主要用 Claude 做数据分析和写作，计算机科学占 Claude Code 会话的 32.7%。 [Anthropic Research](https://www.anthropic.com/research/how-researchers-use-claude)
- **OpenAI 发布湿实验基准 BioBasicsBench** OpenAI 发布 BioBasicsBench，用 100 个任务衡量 AI Agent 解读原始实验数据、处理日常湿实验科学工作的能力。 [OpenAI News](https://openai.com/index/measuring-how-ai-agents-handle-wet-lab-science)
- **WeLM-Image：面向单 GPU 部署的统一图像生成模型** WeLM-Image 把多模态理解融入文生图、指令编辑和多参考合成，共 31.7B 存储参数，每个目标 latent token 约激活 5.4B 生成参数。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.07392)
- **Meta 为 Muse 应用推出 spaces** Meta 为 Muse 推出 spaces：用户描述一个想法，Muse 就构建出对应的定制体验，之后还能边用边调整。 [Meta Newsroom · AI](https://about.fb.com/news/2026/11/introducing-spaces-customize-muse-app/)
