# 2026-11-11 · AI 科技日报

## 今日要点

- Google 向开发者、企业和普通用户开放 Gemini 4 Carbon；DeepMind 同时发布 AlphaProof Code，用 AI 代理形式化验证了 Signal 协议的实际代码。
- Anthropic 启动 IPO 路演，申请以代码 ANT 在 Nasdaq 上市；Claude 推出 Whiteboards、Sheets 和 Data，合作方应用也能基于 MCP Apps 直接在 Claude 里打开。
- MiniMax 发布并开放 H3-Image 权重，可在 10 秒内生成 4K 图像。

## 🔥 头条

### Google 全面开放 Gemini 4 Carbon，API 引入期与 Argon 同价

两周前只向网络安全防御者开放的 Gemini 4 Carbon，现在面向开发者、企业、科研人员和普通用户开放：付费开发者可在 Google AI Studio 通过 API 调用，引入期价格与 Gemini 4 Argon 相同（每百万输入 token 2 美元、输出 10 美元），引入期结束后为输入 4 美元、输出 20 美元。Google 称它在 CursorBench 4.0 等真实工作流评测中排名第一，且单任务成本比次优外部模型低一半以上。对开发者来说，这是一个可以直接接入编码和长程 Agent 任务的新前沿模型选项，但要留意引入期结束后的涨价。

来源：[Google DeepMind Blog](https://deepmind.google/blog/gemini-4-carbon-is-now-available/) · [blog.google](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-carbon-now-available/) · [HN 讨论](https://news.ycombinator.com/item?id=50442303)　`模型` `产品`

### DeepMind 发布 AlphaProof Code，用 AI 代理形式化验证 Signal 协议代码

Google DeepMind 的 AlphaProof Code 是结合人类专家与 AI 代理的形式化验证框架：研究人员借助多个模型把 Signal 的安全目标转写成形式化规约并由人类专家逐条审核，再由 Gemini Carbon 驱动的代理生成了超过六百万行 Lean 证明，只有约百分之一的代码需要人工复查，整个验证用时四周。验证对象是 Signal 协议的实际代码而不只是设计，DeepMind 还开源了这些形式化验证产物。对做安全关键软件的团队来说，这说明用 Agent 做大规模形式化证明已经开始走向真实代码库。

来源：[Google DeepMind Blog](https://deepmind.google/blog/introducing-alphaproof-code/)　`Agent` `安全` `代码`

### Anthropic 启动 IPO 路演，拟以代码 ANT 在 Nasdaq 上市

Anthropic 宣布为其 A 类普通股的首次公开发行启动路演，拟发行 825,000,000 股，预计发行价在每股 $70.00 到 $78.00 之间，已申请在 Nasdaq Global Select Market 以代码 ANT 上市。WSJ 报道称其目标估值为 $1.3T。这是头部模型厂商走向公开市场的一步，后续财务披露会让外界更清楚地看到前沿模型业务的成本与收入结构。

来源：[Anthropic News](https://www.anthropic.com/news/roadshow-launch) · [wsj.com](https://www.wsj.com/finance/stocks/anthropic-to-seek-1-3-trillion-valuation-in-ipo-8337b669) · [HN 讨论](https://news.ycombinator.com/item?id=50439616)　`行业`

### Claude 推出 Whiteboards、Sheets 和 Data

Claude Whiteboards 和 Claude Sheets 以 beta 形式上线，Claude Dashboards 转为正式版并更名为 Claude Data：Whiteboards 是团队和 Claude 一起头脑风暴的共享白板，Sheets 是 Claude 与你一起搭建和编辑的电子表格，Data 增加了数据故事、认证查询和实时共享，面向所有付费方案开放。以前要把 Claude 的产出搬到别的工具里继续做，现在文档、白板和表格可以留在 Claude 里持续协作。

来源：[Introducing Claude Whiteboards, Claude Sheets, and Claude Data](https://claude.com/resources/articles/sheets-whiteboards-data) · [More ways to work with Claude: Sheets, Whiteboards, and Interactive Connectors](https://claude.com/resources/articles/more-ways-to-work-with-claude-sheets-whiteboards-and-interactive-connectors) · [HN 讨论](https://news.ycombinator.com/item?id=50443716)　`产品`

### 微软研究院披露 Lazarus：改写少数休眠神经元即可给 Agent 植入后门

微软研究人员发现，只需改写 LLM 中不到 10 个休眠神经元就能给基于它的 Agent 植入后门，无需重新训练；模型能通过常规安全评测、表现正常，直到隐藏的触发条件出现，再去下载运行攻击者代码或窃取密钥。对使用开放权重模型搭建带工具或终端权限 Agent 的开发者来说，模型来源和权重完整性变成了安全问题，作者建议把模型当作潜在的内部风险：不默认信任、限制权限、监控其行为。

来源：[Microsoft Research](https://www.microsoft.com/en-us/research/blog/lazare-veni-foras-reprogramming-dormant-neurons-to-backdoor-ai-agents/)　`安全` `Agent`

## 🧠 模型

### MiniMax 发布开放权重图像模型 H3-Image，10 秒内出 4K 图

MiniMax 基于 H3 推出图像生成模型 H3-Image，支持文生图、参考图生成和图像编辑，可在 10 秒内生成 4K（4096 × 4096）图像，最多支持 16 张参考图。权重已发布在 Hugging Face（采用 MiniMax 自己的社区许可），也可通过 MiniMax API Platform 使用。需要本地部署高分辨率图像生成的开发者可以用 Diffusers、SGLang、vLLM-Omni 或 ComfyUI 来跑。

来源：[MiniMax Blog](https://www.minimax.io/blog/minimax-h3-image) · [MiniMaxAI/MiniMax-H3-Image](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image) · [Comfy-Org/MiniMax-H3-Image](https://huggingface.co/Comfy-Org/MiniMax-H3-Image) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xso1ie/minimax_h3image_released_an_openweight_image/)　`模型` `开源` `图像`

### Adventists AI 开源全双工语音模型 Sophon-Realtime v1

Sophon-Realtime v1 是一组全双工语音模型，同一个 32B 模型负责听、决定何时接话和写回复，三个版本（Tag、Flash、E2E）只在发声方式上不同；Flash 版首包音频 0.31 s。Tag 和 Flash 一张 80 GB GPU 即可用 vLLM-Omni 一条命令部署，单卡分别支持最多 16 和 40 个并发用户，代码和权重采用 Apache-2.0。想自建实时语音助手、客服的开发者多了一个可商用的开放选项。

来源：[Hugging Face](https://huggingface.co/adventists-ai/Sophon-Realtime-v1)　`语音` `开源` `模型`

## 📄 论文

### Deletion Tuning：只删不到 0.05% 的权重就能追平全量微调

论文发现，只把预训练 LLM 中不到 0.05% 的权重置零、不做其他修改，就能在 RLVR、SFT 和在线蒸馏三种后训练中追平全量微调；方法是在 Transformer 块的 gate projection 上学习一个二值掩码。掩码比全量微调的 checkpoint 小几百到几千倍，而且遗忘更少：RL 下旧任务准确率基本保持，而全量微调、LoRA 等最多掉 5.4 个点。对需要频繁做小规模后训练、又怕灾难性遗忘的团队，这是一个值得试的轻量方案。

来源：[arXiv](https://arxiv.org/abs/2611.10866) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xswmb7/the_surprising_effectiveness_of_deleting_weights/)　`论文` `训练`

### Flide：面向决策模型的精确推理引擎，最高比 vLLM 快 9.5 倍

Flide 是专为 Jev 这类决策模型设计的推理引擎，把决策请求的逻辑树结构和物理执行解耦，放进一条扁平的 token 流里，并通过 ForkAttention 保证每个分支的结果与单独前向计算完全一致，同时支持标准注意力和 Gated DeltaNet 层。论文称它回答查询最高比 vLLM 和 SGLang 快 9.5 倍。在 Agent 里大量用决策模型做快速分类判断时，可以考虑用它替代通用生成式推理引擎。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.42148)　`论文` `推理`

### Longtail-SWE：覆盖 13 种冷门语言的仓库级编码基准

Longtail-SWE 收录来自 129 个仓库的 202 个 issue 修复任务，覆盖 Clojure、Elixir、Haskell、OCaml、Swift 等 13 种现有基准很少覆盖的语言，用 solver–judge–repairer 流水线修正有缺陷的测试和描述，而不是直接丢弃难题。作者在社区帖中称，Qwen3.8 27B 能解决 43% 的任务，Qwen3.6 只有 17%。用这些语言开发、在挑选编码模型或 Agent 的团队，可以拿它补上主流基准的盲区。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.10304) · [longtail-swe.com](https://longtail-swe.com/) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xsorsx/we_tested_qwen36_27b_qwen38_27b_and_glm53_flash/)　`论文` `代码` `Agent`

### LingBot-Touch：跨传感器的触觉基础模型

LingBot-Touch 是一个触觉基础模型，为压阻、磁性和视触觉等不同类型的触觉传感器学习统一表示，并可扩展到新的传感器类型。它产出的触觉 token 即插即用，可以接入从 diffusion policy 到 LingBot-VLA 等 VLA 模型的策略中。做灵巧操作的机器人团队可以借此复用不同传感器采集的触觉数据。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12806) · [Hugging Face](https://huggingface.co/collections/robbyant/lingbot-touch)　`论文` `多模态`

## 🛠 开源与工具

### 合作方应用可直接在 Claude 中打开，基于 MCP Apps 构建

Claude 的交互式连接器现在可以把合作方应用整个嵌进对话旁边或全屏打开，由 Claude 直接在里面修改，首批包括 Asana、Canva、Carta、Dropbox、monday.com、Smartsheet、Vercel 和 Webflow，Figma、Harvey 和 Shopify 也在接入。这些连接器运行在 MCP Apps 之上，这是 Model Context Protocol 的开放扩展，Claude 现在支持其中更多能力（如 app tools 和嵌入网站）。开发者做的 MCP App 不只限于 Claude，可以在任何支持该扩展的 AI 应用里运行。

来源：[Claude Blog](https://claude.com/resources/articles/interactive-connectors-full-tool)　`工具` `Agent` `产品`

### Hugging Face 为决策模型加入 Transformers 和 Hub 支持

Hugging Face 介绍了决策模型：不逐 token 生成文本，而是直接给应用预先定义好的答案打概率。Transformers 新增 DecisionPipeline、AutoModelForDecision 和 DecisionConfig，llama.cpp 也通过同样的 /v1/systemone API 支持决策模型，Hub 上新增 decision-model 标签方便查找。需要让 Agent 做结构化分类、路由判断的开发者，可以直接用这套接口拿到可用于程序的概率输出。

来源：[Hugging Face Blog](https://huggingface.co/blog/decision)　`工具` `开源` `Agent`

### Chrome 团队发布 Modern Web Guidance，让编码 Agent 用上现代 Web 写法

Google Chrome 团队联合 Firefox、MDN 和 Edge 发布 Modern Web Guidance 1.0，以 Agent skill 的形式向编码 Agent 提供 200 多篇现代 Web 平台最佳实践和浏览器兼容数据，引导它们不再默认生成冗长的 div+JS 旧写法。用 npx modern-web-guidance@latest install 即可安装，CLI 还能扫描代码库中的旧模式，项目采用 Apache-2.0 开源。用 Agent 写前端的开发者可以直接装上试试。

来源：[GitHub](https://github.com/GoogleChrome/modern-web-guidance) · [HN 讨论](https://news.ycombinator.com/item?id=50443812)　`工具` `代码` `Agent`

### Cursor Projects 支持多人协作

Cursor 的 Projects（通过一个协调者指挥一组 Agent 完成大型任务）现在支持多人：可以邀请队友加入同一个 Project，共享需求文档、设计稿等上下文，进行中的工作也能直接交接给另一个人的 Agent。该功能今天起以 beta 形式向所有 Cursor 用户推送。团队用多 Agent 开发时，可以少一些各自为战的上下文重复搭建。

来源：[Cursor](https://cursor.com/blog/projects-multiplayer)　`工具` `代码` `Agent`

## ⚡ 快讯

- **Fireworks AI 安全事件波及 Notion AI 对话记录** Notion 称其供应商 Fireworks AI 的安全事件影响不到 1% 的工作区，涉及 Notion AI 对话记录，且对方违背零数据保留承诺留存了数据。 [notion.com](https://www.notion.com/help/security-incident-involving-a-third-party-ai-vendor) · [HN 讨论](https://news.ycombinator.com/item?id=50437106)
- **9to5Mac：苹果在做本地推理应用 Harbor** 据 9to5Mac 引述爆料，苹果正在 Claris 品牌下私测 Harbor，可在 Apple silicon 上本地运行开放权重模型，并通过 Thunderbolt 5 把多台 Mac 的统一内存组成集群。 [9to5mac.com](https://9to5mac.com/2026/11/10/apple-has-new-mac-app-coming-to-make-running-local-ai-models-easy/) · [HN 讨论](https://news.ycombinator.com/item?id=50446520)
- **Qwen4-Max Preview 上线阿里 Token Plan** 通义千问称下一代 Qwen4 即将到来，Qwen4-Max Preview 已上线 Alibaba Token Plan（限时最高 90% 折扣），并接入 Qwen Office、Qoder、Qwen App 和 QwenStudio。 [mp.weixin.qq.com](https://mp.weixin.qq.com/s/J_zbVHa2R3mmY5KD4v3-bw) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xt5q27/qwen4_is_coming_preview_now_live_on_alibaba_token/)
