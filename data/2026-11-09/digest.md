# 2026-11-09 · AI 科技日报

## 今日要点

- 腾讯在 Hugging Face 开源 Qwen3.8-27B 的 DSpine 草稿模型，作者报告在 WorkBuddy Office 上吞吐达到自回归解码的 3.84×。
- llama-modchip 把 284B 的 DeepSeek-V4-Flash 压到 56.56 GiB，在 64 GB 内存、无 GPU 的机器上跑。
- Goldman Sachs 把 Claude Code 收回给工程师，大多数交易员和银行家不能再用 AI 编程工具。

## 🔥 头条

### 腾讯开源 Qwen3.8-27B 投机解码草稿模型 DSpine

腾讯在 Hugging Face 发布 Qwen3.8-27B-DSpine-b16，这是给 Qwen3.8-27B 用的五层草稿模型，用 DSpine 方法并行生成草稿 token，block size 16。作者在 SGLang 上测得，低推理档下 WorkBuddy Code 吞吐是自回归解码的 2.71×，WorkBuddy Office 达 3.84×，均高于官方 DFlash2。本地或自建部署 Qwen3.8-27B 的团队可以直接拿它加速，Apache 2.0 许可，但数字都是作者自测。

来源：[Hugging Face Trending Models](https://huggingface.co/tencent/Qwen3.8-27B-DSpine-b16) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xr2aaa/tencentqwen3827bdspineb16_hugging_face/)　`开源` `推理` `模型`

### llama-modchip：在 64 GB 内存无 GPU 机器上跑 284B DeepSeek

开源项目 llama-modchip（v2.4.0）给 llama.cpp 打补丁并重新量化，把 284B 的 DeepSeek-V4-Flash 压到 56.56 GiB（1.71 bpw），连同 256K 上下文的 KV cache 一起放进 64 GB 内存，不需要 GPU。作者在 16 核 Zen 5 上测得预填充 44.36 tok/s。想在纯 CPU 机器上跑大 MoE 的开发者可以试试，但这些文件只能用它打过补丁的二进制加载，原版 llama.cpp、Ollama、LM Studio 会报错。

来源：[GitHub](https://github.com/synchopate/llama-modchip) · [HN 讨论](https://news.ycombinator.com/item?id=50411961)　`开源` `推理` `工具`

### Goldman Sachs 收回交易员和银行家的 Claude Code 权限

据 Bloomberg 报道，Goldman Sachs 更新内部规定，把 Claude Code 和 Microsoft 的 GitHub 限定给工程师使用，大多数交易员和银行家不能再用 AI 编程工具；限制针对能自己写代码、跑代码的第三方智能体，此前银行对生产力和风险做了审查。这说明在受监管行业，非工程人员用编程智能体自建工具会碰到代码审查和合规的门槛，给企业推这类工具的团队可以参考。

来源：[thestateofai.com](https://www.thestateofai.com/news/goldman-sachs-claude-code-traders-bankers) · [HN 讨论](https://news.ycombinator.com/item?id=50415628)　`行业` `代码` `Agent`

### OpenAI 以 $1.25T 估值完成 $11B 首轮到账

据 24/7 Wall St. 报道，约 $11B 新资金已到账 OpenAI，这是一轮融资的第一部分，投前估值 $1.25T，CFO Sarah Friar 在电视采访中确认了估值，SoftBank 和 MGX 参与。估值低于此前报道的目标，第二部分尚未完成，对依赖 OpenAI API 的团队，这是观察其资金面的一个参考。

来源：[247wallst.com](https://247wallst.com/investing/2026/11/07/openai-just-raised-11-billion-at-a-1-25-trillion-valuation-below-the-1-4-trillion-it-first-sought/) · [HN 讨论](https://news.ycombinator.com/item?id=50413822)　`行业`

## 🧠 模型

### webAI 发布 8.8B 推理模型 TwIL-8B

webAI 基于 ibm-granite/granite-4.2-8b 做全参数 SFT 和 GRPO/DAPO 强化学习，得到面向数学、代码和指令遵循的 TwIL-8B，作者报告 MATH-500 为 98.2，并提供 4.98 GiB 的 Q4_K_M GGUF。模型卡自己说明它不是知识型模型，GPQA Diamond 落后 Qwen3.5-9B；采用 webAI Non-Commercial License，只能用于非商业场景。

来源：[Hugging Face Trending Models](https://huggingface.co/webAI-Official/TwIL-8B)　`模型` `推理`

### Pika Labs 开放 Pika H3 Flex 音视频生成适配器

Pika Labs 在 Hugging Face 发布 Pika H3 Flex，这是基于 MiniMax-H3 后训练的适配器，六步采样生成带同步音频的视频，输出 24 fps，最多支持 12 个参考输入。想本地跑音视频生成的开发者多了一个选项，但它按 MiniMax H3 Community License 分发，作者在 H100 80GB 上测试，大请求可能需要 CPU offload。

来源：[Hugging Face Trending Models](https://huggingface.co/Pika-Labs/Pika-H3-Flex)　`模型` `视频` `多模态`

## 📄 论文

### Route Anything：跨模态模型与策略路由研究

论文构建了覆盖 25 个基准、452 个候选配置、374,401 次打分运行的全模态轨迹矩阵，研究怎样为每个任务挑选模型或策略。逐输入的 oracle 路由比最好的固定候选高 5.4 分，路由平均把效率提高到参考模型的 8.82x。做多模型调度、按成本选模型的团队可以参考它的数据和结论。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.05275) · [arXiv](https://arxiv.org/abs/2611.05275)　`论文` `Agent` `多模态`

### Next-Concept Modeling：由粗到细并行生成文本

论文提出 NCM：用多尺度残差 VQ-VAE 把文本编码成层级离散码，Transformer 逐层生成、同一层内的码并行预测。在 LM1B 上，同参数规模下生成困惑度优于最强的扩散语言模型基线，在 Sudoku 上用更少的函数评估超过自回归和扩散基线。这是扩散语言模型之外另一条并行文本生成路线，值得关注。

来源：[arXiv](https://arxiv.org/abs/2610.14162) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xr6krp/nextconcept_modeling_fast_parallel_coarsetofine/)　`论文` `训练`

### 可灵团队总结视频生成中的多模态理解经验

Kling Team 的报告认为视频生成的瓶颈正从渲染转向语义控制，并沿数据、条件、对齐、评测整条链路逐个模块总结经验，核心是一个统一图像、视频、音频输入的共享多模态基座 Kling-MLLM。报告还讨论了把 caption 当作语义契约、提示词增强和奖励模型的设计，做视频生成管线的团队可以对照参考。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.04916) · [arXiv](https://arxiv.org/abs/2611.04916)　`论文` `视频` `多模态`

## 🛠 开源与工具

### OpenMausBot：自托管的多智能体聊天应用

OpenMausBot 是 Apache-2.0 开源的聊天应用，侧栏里每个 bot 都是在本地运行的 Claude 或 Codex 智能体，各自有自己的模型、云端电脑和连接的应用。今天登上 GitHub Trending，想自建一套“智能体团队”的开发者可以拿来参考或直接部署。

来源：[GitHub Trending](https://github.com/milind-soni/OpenMausBot)　`开源` `Agent` `工具`

### TorchLens：记录并干预神经网络的每一步运算

TorchLens 不改模型代码就能捕获每个激活和梯度、完整计算图和 800+ 个元数据字段，支持 PyTorch、JAX、TensorFlow、MLX、PaddlePaddle 和 tinygrad。做可解释性研究或排查训练问题的开发者可以用它代替手写 hook。

来源：[GitHub](https://github.com/johnmarktaylor91/torchlens) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xrh5iz/github_repo_torchlens_inspect_visualize_and/)　`工具` `开源` `训练`

## ⚡ 快讯

- **vercel-labs/agent-browser 登上 GitHub Trending** Vercel Labs 给 AI 智能体用的浏览器自动化 CLI agent-browser 今天登上 GitHub Trending。 [GitHub Trending](https://github.com/vercel-labs/agent-browser)
