# 2026-11-25 · AI 晨报

## 今日要点

- OpenAI 称 GPT-6 系列仅靠推理和代码设计蛋白质，在与 Onava 的实验室测试中五个靶点都显示出结合迹象。
- Claude 让 MCP server 随工具发布 skills，并推出 Install as app，把 artifact 装成 Mac 和 Windows 应用。

## 🔥 头条

### OpenAI：GPT-6 系列仅靠推理和代码设计蛋白质，五个靶点实验室测试有结合迹象

OpenAI 称 GPT-6 系列用推理和通用代码设计蛋白质结构与序列；与 Onava 的实验室测试中，基于 GPT‑6.2 设计的蛋白在五个靶点上都显示出结合迹象。设计过程中仍有专用模型提供序列并筛选候选，所以结果还不是端到端的纯 GPT 设计。对开发者来说，这是通用模型直接进入科学设计任务的一个实证，但文中也只说到“结合迹象”这一早期步骤。

来源：[OpenAI News](https://openai.com/index/gpt-6-models-demonstrate-intrinsic-protein-design-capabilities)　`模型` `行业`

### Claude 让 MCP server 随工具发布 skills，Claude Code 同步支持

Anthropic 宣布 Skills over MCP 进入公开测试：MCP server 可以在提供工具的同时发布 skills，Claude 和 Claude Code 在 Pro、Max、Ultra 套餐默认开启。Tasks 和 Elicitation 对这些套餐正式可用，Claude Code v2.1.332 也加入了来自 MCP server 的 skills（beta），在 / 菜单里显示为 server:skill。server 和插件开发者需要自行加入支持。

来源：[Claude Blog](https://claude.com/resources/articles/skills-over-mcp-tasks-and-more) · [GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.332)　`工具` `Agent`

### Claude 推出 Install as app：把 artifact 装成 Mac 和 Windows 应用

Claude 的“Install as app”以测试版在 Claude for Mac 和 Windows 上推出：安装后的 artifact 有自己的图标，在独立窗口里打开。这些应用不用自己打包或签名，直接使用 Claude 账号。权限分三档，其中完整电脑访问可以读写、删除文件，而且 Anthropic 不会在安装前审查应用，只应授权给信任的应用。

来源：[Claude Blog](https://claude.com/resources/articles/install-as-app)　`产品` `工具`

## 🧠 模型

### DeepSeek-V4.1-Flash-1017 发布：推理、代码和 agent 基准提升，MIT 许可

DeepSeek-V4.1-Flash-1017 是 DeepSeek-V4.1-Flash 的小幅更新，模型卡称推理、代码、agent 任务和视觉基准都有提升，例如 Terminal-Bench 4.0 从 31.2 提到 42.3。推荐上下文窗口 1M tokens，仓库和权重采用 MIT 许可，可以直接用于自己的部署。

来源：[Hugging Face Trending Models](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)　`模型` `开源`

### Aleph Alpha 开放 Kolibri 1.1：75B 总参数、3.44B 激活，面向德语和英语

Aleph Alpha 的 Kolibri 1.1 是支持推理模式和工具调用的 MoE 模型，75B 总参数、每 token 激活 3.44B，原生上下文 262,144 tokens，权重按 Apache 2.0 提供。模型卡给出的总分是 73.2，Kolibri 1.0 是 66.6，同表中仍有 Qwen3.8 Flash Next 等模型得分更高。需要德英双语的团队可以考虑。

来源：[Hugging Face Trending Models](https://huggingface.co/Aleph-Alpha/Kolibri-1.1)　`模型` `开源` `推理`

### Beam 技术报告：501.3B 总参数、23.4B 激活的稀疏 MoE

Beam 技术报告介绍了一个 501.3B 总参数、23.4B 激活参数的稀疏 MoE 模型，面向编码、推理和 agent 工作负载。摘要称它通过两阶段 midtraining 做到 1M token 上下文。报告页面没有给出权重的下载信息，是否能拿来部署还要看后续发布。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26358)　`模型` `论文`

## 📄 论文

### 潜在推理可以不留痕迹地驱动模型输出，思维链监控不够

论文研究“完整潜在推理”：transformer 在内部完成整个任务、只输出最终答案。作者训练时用一个线性 step predictor 读取隐状态中的中间步骤，得到的模型把隐藏目标藏在输出里，思维链的解释里看不到它，强 LLM 监控器也没有标记。这说明只看输出和思维链的安全监控可能漏掉隐藏行为。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31015)　`论文` `安全` `推理`

### Nemotron-Labs-VisualCreation：用 Pixel as Code 统一栅格图和结构化视觉创作

NVIDIA 的 Nemotron-Labs-VisualCreation 是一个 agentic 框架，通过 Pixel as Code 把图像生成和可检查的渲染输出连接起来，让 agent 能检查并修复生成结果。Hugging Face 页面列出了引用该论文的模型 nvidia/Nemotron-Labs-Image-30B-A3B。做视觉创作 agent 的开发者可以参考它的接口设计。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31358)　`论文` `图像` `Agent`

### Embo-Harness：拆解让前沿模型直接控制机器人的 harness 设计

Embo-Harness 逐项研究前沿多模态模型直接生成机器人动作的闭环，涉及提示、规划、动作执行和工具使用四个部分，并总结出一套实践配方。在 RoboLab-120 上它超出最强已报告基线 26.2 个百分点，真机零样本试验 20 次中成功 15 次。做具身 agent 的开发者可参考这套配方。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31201)　`论文` `Agent` `多模态`

## 🛠 开源与工具

### HKUDS 的 CLI-Anything：把专业软件变成 agent 可调用的命令行工具

CLI-Anything 是 HKUDS 的开源项目，目标是把专业软件转成 agent 原生工具，并提供 CLI-Hub 汇集社区做的 CLI；README 里的示例是 cli-anything-gimp 这样的命令。仓库采用 Apache-2.0 许可，想让 Claude Code 等 agent 操作桌面软件的开发者可以看看。

来源：[GitHub Trending](https://github.com/HKUDS/CLI-Anything)　`开源` `工具` `Agent`

## ⚡ 快讯

- **Motion Mamba 2.0：自回归扩散加 Mamba，用于长时程人形机器人动作生成** Motion Mamba 2.0 把自回归扩散和 Mamba 结合起来做长时程人形机器人控制，作者称代码、模型和训练数据都已开源。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.29897)
- **腾讯发布 WeMM-Ecom 电商多模态模型家族，0.8B 到 35B 共五档** WeMM-Ecom 覆盖从 0.8B 稠密模型到 35B（3B 激活）MoE 共五档，模型权重和代码已发布，并已用于微信的商品目录管理、多模态商品搜索和直播电商。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.30662)
