# 2026-11-01 · AI 科技日报

## 今日要点

- DeepSeek-V4.1-Flash-1017 与 MiniMax-M3.1-Flash 都在 Agent 与代码任务上给出新的成绩，MiniMax-M3.1-Flash 支持最高 1M tokens 上下文。
- OCR 模型密集更新：百度 Unlimited-OCR-2 面向超长文档解析，OpenBMB MiniCPM-OCR 1.0 主打速度与部署，LiquidAI d1-2B 用一次前向传播做决策。
- 开发者工具方面，Lightpanda 用 Zig 从头写的无头浏览器面向 AI Agent 与自动化，Microsoft 的 Mage-VL-Cowork 用 4B 模型做混合计算机操作。

## 🔥 头条

### DeepSeek 发布 DeepSeek-V4.1-Flash-1017 小版本更新

DeepSeek-V4.1-Flash-1017 是 DeepSeek-V4.1-Flash 的小版本更新，官方称其在推理、编码、Agent 任务和视觉基准上均有提升，同时缩短任务执行时间与输出长度。该模型权重以 MIT License 发布，开发者可通过 Transformers、vLLM 或 SGLang 直接使用。

来源：[Hugging Face Trending Models](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)　`模型` `开源` `Agent`

### MiniMax 发布 MiniMax-M3.1-Flash 原生多模态 MoE 模型

MiniMax-M3.1-Flash 是面向编码、Agent 工作流、电脑操作与网络安全的原生多模态 MoE 模型，支持文本、图像、视频输入，上下文窗口最高 1M tokens。它用稀疏注意力、量化感知训练和 DSpark 推测解码改进推理效率，官方推荐 SGLang、vLLM 和 TokenSpeed 进行部署。

来源：[Hugging Face Trending Models](https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash)　`模型` `多模态` `Agent`

### 百度 Unlimited-OCR-2 主打无限长文档解析

百度发布 Unlimited-OCR-2，用 Sparse Reference Sliding Window Attention（SR-SWA）把超长序列的文本与视觉注意力压缩为固定大小的参考集合，让每步解码延迟和显存占用基本不随文档长度变化。官方称其在 MPDocBench 与 MarathonDocBench 等几十页到上百页基准上达到领先水平，并同时发布超长文档解析基准 MarathonDocBench。

来源：[Hugging Face Trending Models](https://huggingface.co/baidu/Unlimited-OCR-2)　`模型` `多模态` `开源`

### Lightpanda 用 Zig 从头写无头浏览器面向 AI Agent

Lightpanda 不是 Chromium 分支也不是 WebKit 补丁，而是用 Zig 从头编写的无头浏览器，官方称其比 Chromium 轻 16x、快 9x，并提供 CDP 与 webdriver BiDi 服务。它内置 agent 模式，会把操作记录导出为确定性的 PandaScript 脚本，可直接用 lightpanda run 回放。

来源：[GitHub Trending](https://github.com/lightpanda-io/browser)　`工具` `Agent` `开源`

### 微软发布 4B 混合计算机操作模型 Mage-VL-Cowork

Mage-VL-Cowork 是一个 4B 的视觉语言策略模型，把截图驱动的 GUI 交互（computer_use）与持久化的代码/终端执行（bash）放进同一个策略里，可在两种通道之间自行切换。官方称它在 OSWorld-Verified 上达到 66.0%，在线强化学习相对 Hybrid SFT 提升 +10.16 个百分点，同时减少 13.0% 的模型调用和 25.4% 的输出 token。

来源：[Hugging Face](https://huggingface.co/microsoft/Mage-VL-Cowork)　`模型` `Agent` `多模态`

## 🧠 模型

### LiquidAI d1-2B 用一次前向传播完成决策

LiquidAI d1-2B 是基于 LFM3-VL-2B 的决策模型，面向文本、图片和视频一次性输出带概率的答案，不生成 token，也不提供采样参数。官方称其在 NVIDIA H100 上每次决策 5.7 ms，并可作为路由分流、内容审核、意图分类和结构化抽取等流水线的判断环节。

来源：[Hugging Face Trending Models](https://huggingface.co/LiquidAI/d1-2B)　`模型` `多模态` `工具`

### OpenBMB 发布 MiniCPM-OCR 1.0 文档解析模型

MiniCPM-OCR 1.0 是 MiniCPM-V/o 家族中首个 OCR 专用模型，参数规模 1.3B，基于 MiniCPM-V 4.6 训练，支持中英文文档的文本、表格、公式、图表、印章与关键信息抽取。官方称配合 DSpark 解码加速后端到端处理效率提升 55%，并可通过 vLLM、SGLang、llama.cpp 和 Ollama 部署。

来源：[Hugging Face Trending Models](https://huggingface.co/openbmb/MiniCPM-OCR-1.0)　`模型` `多模态` `开源`

### 小米开源 0.8B 的 Xiaomi-OCR-0 文档解析模型

Xiaomi-OCR-0 是从 Qwen3.5-0.8B-Base 出发训练的 0.8B 统一 OCR 视觉语言模型，同时覆盖文档解析、OCR 导向的视觉问答和关键信息抽取。它使用约 170M 样本的 OCR 语料与渐进式训练配方，官方称在 Real5-OmniDocBench 上取得 95.24 的成绩。

来源：[Hugging Face Trending Models](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0)　`模型` `多模态` `开源`

### Pika 发布 Pika-H3-Flex 视频生成 LoRA

Pika-H3-Flex 是后训练过的 H3 模型，通过 LoRA 方式加载，可在六个采样步内生成带同步音频的视频，并支持最多 12 个参考输入来控制镜头走向。本地开源权重推理支持原生 480p / 768p 视频与混合立体声音轨，Pika 托管 API 则提供 1080p、2K 与 4K 生成。

来源：[Hugging Face Trending Models](https://huggingface.co/Pika-Labs/Pika-H3-Flex)　`模型` `视频` `开源`

### Maya Research 开源 Maya 2 Native 流式语音模型

Maya 2 Native 支持 12 种语言、20 个内置声音和零样本声音克隆，可把 3–10 秒参考音频克隆成跨语言语音，输出 24 kHz 音频并按 80 ms 帧流式返回。发布内容包含开放权重与推理代码，提供 Python API、OpenAI 兼容的语音接口和 WebSocket 流式服务。

来源：[Hugging Face Trending Models](https://huggingface.co/maya-research/maya2-native)　`模型` `语音` `开源`

## 🛠 开源与工具

### Orkas 开源本地优先的多 Agent 桌面应用

Orkas 是一个 MIT 许可的本地优先桌面多 Agent 应用，由 Commander 把目标拆成待办并协调 16 个内置专职 Agent，同时可接入 Claude Code、Codex、OpenCode 等外部编码 Agent。项目会保存目标、规则、记忆与文件，支持待办自动推进和按小时、天、周、月运行的定时自动化，数据留在本机。

来源：[GitHub Trending](https://github.com/Orkas-AI/Orkas)　`工具` `Agent` `开源`

## ⚡ 快讯

- **Open-H3-Regenerate-2K 开源 MiniMax-H3 的 2K 重绘方案** Open-H3-Regenerate-2K 提供三步 MiniMax-H3 精修流程，可把 768P 草稿重绘为 2560×1440 视频，官方称其是对闭源 H3-Regenerate-2K API 的开源替代。 [Hugging Face Trending Models](https://huggingface.co/Efficient-Large-Model/Open-H3-Regenerate-2K)
- **VOLTA 信息窃取木马用 LLM 给受害者排序资产** Talos 披露的 VOLTA 在窃取凭据后，把结构化证据包发给 LLM，要求模型按变现价值给受害者资产分级并评估其安全习惯。模型拒绝时，它会回退到另外两个模型继续请求。 [blog.talosintelligence.com](https://blog.talosintelligence.com/appraisal-by-ai-model-driven-victim-prioritization-in-the-volta-infostealer/)
