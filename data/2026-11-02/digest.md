# 2026-11-02 · AI 科技日报

## 今日要点

- JetBrains 发布 Mellum2.1-12B-A2.5B-Thinking-MTP，借助 MTP 头做推测解码，输出不变、解码快 1.4–1.8x。
- DeepSeek 放出 dsh-superagent 研究原型，展示面向单个 GitHub 仓库的主动式编码 Agent 设计。

## 🔥 头条

### JetBrains 发布带 MTP 头的 Mellum2.1 思考模型

JetBrains 在 Hugging Face 发布 Mellum2.1-12B-A2.5B-Thinking-MTP，即 Mellum2.1 Thinking 加上一层多 token 预测（MTP）头，采用 Apache 2.0 许可，上下文长度 131,072。MTP 头作为推测解码的草稿，输出不变而解码快 1.4–1.8x，需要 vLLM 0.33 或 transformers 5.20 及以上版本。模型面向在仓库里工作、运行命令和调用工具的 Agent 任务，想在本地部署小型编码模型的开发者可以直接试用。

来源：[Hugging Face](https://huggingface.co/JetBrains/Mellum2.1-12B-A2.5B-Thinking-MTP) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xln8f2/jetbrainsmellum2112ba25bthinkingmtp_hugging_face/)　`模型` `代码` `推理`

### DeepSeek 放出主动式编码 Agent 原型 dsh-superagent

DeepSeek 在 X 上发表《Exploring Super-agent Design》一文，并公开部分实现 dsh-superagent-prototype：一个面向单个 GitHub 仓库的主动式编码 Agent，以 DeepSeek Harness 插件包的形式提供。它监听 GitHub（可选飞书），收到授权用户的请求后开一个工作项、在独立的 Agent 会话中处理，再回到原对话答复，例如提交 pull request。仓库明确说明这只是研究原型、不是 DeepSeek 官方产品，且与内部版本不完全相同；想搭建团队级自治 Agent 的开发者可以把它当参考设计。

来源：[GitHub](https://github.com/deepseek-ai/dsh-superagent-prototype) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xl1zn3/deepseek_exploring_superagent_design_towards_a/)　`Agent` `代码` `开源`

## 🧠 模型

### Nace.AI 开源 27B 多模态决策模型 Drex Max v1

Drex Max v1 不生成文本：把文本、JSON 或图像作为上下文，再给出一个或多个具名问题，一次前向计算就返回每个候选答案的概率。它是 dense 27B 模型，带 255 路 readout 头，上下文窗口最高 262,144 token，采用 Nace.AI Open RAIL-M 许可，可在 NVIDIA GPU 上用 Python 运行，也能通过 llama.cpp 和 Ollama 分支在 Apple Silicon 上运行。对只需在固定选项中做选择的场景，它省去了逐 token 解码和解析 JSON 输出的步骤。

来源：[Hugging Face](https://huggingface.co/nace-ai/drex-max-v1) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xl5yfs/release_drex_max_v1_openweight_27b_multimodal/)　`模型` `多模态` `开源`

## 🛠 开源与工具

### Heretic 2.0 发布：从去审查扩展为通用模型修改工具

Heretic 是无需训练即可修改语言模型行为的开源工具，依据对比提示和相应的打分器来引导模型。2.0 版把它从专门的去审查工具扩展为通用的模型修改工具，仓库提供了减少 slop、谄媚、幽默以及调整情绪倾向的配置预设，1.x 的配置文件与 2.x 不兼容。想在不重新训练的前提下调整开源模型风格的开发者，可以用它的预设或自定义打分器上手。

来源：[GitHub](https://github.com/p-e-w/heretic) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xl2tcm/heretic_20_released_model_modification_for/)　`工具` `开源`

### 开源 AI 安全运营中心 AiSOC

AiSOC 是可自托管的开源 AI 安全运营中心：接入安全遥测数据、检测并关联威胁，由推理过程可审计的 AI Agent 展开调查，再提出由人批准的响应方案。项目采用 MIT 许可，无需 API key 即可运行，并自带面向 Claude、Cursor 和 Continue 的 MCP 服务器。想把 LLM Agent 引入告警分诊、又要保留每一步决策记录的安全团队可以参考。

来源：[GitHub Trending](https://github.com/beenuar/AiSOC)　`安全` `Agent` `开源`

## ⚡ 快讯

- **实测：用 AI 写前端，框架选择影响成本** Nolan Lawson 让 Opus 5.5 用多种框架构建同一应用，Hono+htmx 中位成本最低（$2.67），SvelteKit、Gracile+Lit 和 Angular 明显更贵。 [nolanlawson.com](https://nolanlawson.com/2026/10/28/the-ai-cost-of-javascript-frameworks/)
