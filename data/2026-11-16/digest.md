# 2026-11-16 · AI 晨报

## 今日要点

- Qwen 发布基于新 Qwen4 架构的 Qwen4-Max，主干 2.4-trillion 参数、上下文窗口 one-million-token。
- OpenAI 开设科学博客，物理学家 Nathaniel Craig 介绍与 GPT-6 Astra 合作给出标准模型的候选格点定义。
- 论文开源 30B-A3B MoE 基座 801-30B-A3B-Base，把递归自我改进用到整次预训练。

## 🔥 头条

### Qwen 发布 Qwen4-Max，基于新的 Qwen4 架构

Qwen 发布 Qwen4-Max，基于新的 Qwen4 架构，采用 2.4-trillion 参数主干，原生支持视觉，上下文窗口为 one-million-token；官方称它更熟练地使用专业工具、更擅长执行长程任务。此前上线的只是预览版，这次是正式介绍。对开发者来说，这是 Qwen 新一代旗舰，做长上下文、多模态和 Agent 类任务的模型选型时值得重新评测。

来源：[Qwen](https://qwen.ai/blog?id=qwen4-max)　`模型` `多模态` `Agent`

### 物理学家借 GPT-6 Astra 构造标准模型的格点定义候选

OpenAI 新开的科学博客发布首篇客座文章：加州大学圣塔芭芭拉分校物理学家 Nathaniel Craig 介绍他与 GPT-6 Astra 合作，给出标准模型的一个候选非微扰格点定义；Astra 把他的思路变成具体构造，并主导了详细证明，格点场论专家审阅了证明。作者强调还需要专家讨论来判断这个方案是否具备所需的全部性质。对开发者来说，这是前沿模型参与理论物理证明的一个具体案例：模型负责构造和推导，人类专家负责审阅把关。

来源：[A step toward defining the Standard Model on a lattice](https://openai.com/index/step-toward-defining-the-standard-model) · [Our new blog for science](https://openai.com/index/our-new-blog-for-science)　`推理` `行业`

### 腾讯开源 LoopForge：自托管的编码 Agent 交付工作流

腾讯开源 LoopForge，一个自托管的工作空间，用脚本和人工审批关卡编排 CodeBuddy、Codex 和 Claude Code 等编码 Agent：在聊天里描述需求，它会开 Docker 沙箱、检出仓库并分派给项目角色；不想跑服务器的话，LoopForge Local 可以把内置工作流直接装进现有的编码助手。对团队来说，这是把“多个编码 Agent + 人工把关”落到自己基础设施上的现成方案。

来源：[GitHub Trending](https://github.com/Tencent/LoopForge)　`开源` `Agent` `代码`

## 🧠 模型

### 美团开源 LongCat-Video-Avatar 1.6，音频驱动数字人视频

美团 LongCat 发布 LongCat-Video-Avatar 1.6，是其开源音频驱动人物视频生成框架的升级版：口型更自然、更稳定，减少自回归续写中的误差累积，可生成超过 10 分钟的视频，并做了端到端推理优化；权重采用 MIT License。需要做数字人播报、长视频口播的开发者可以直接拿来试。

来源：[Hugging Face](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.6)　`开源` `视频` `模型`

### Villanova2：欧洲五语种开放权重与数据模型家族

VillanovaAI 发布 Villanova2 家族，面向英语、意大利语、德语、西班牙语和法语，包括 15.5B 总参数 / 3.9B 激活的 MoE 模型 Villanova2-15B-A3B 及其 VL 版本，以及 2.4B 的稠密小模型，均为 Apache-2.0；基座从零在 4.7T tokens 上预训练，训练数据逐项公开来源。需要欧洲语言、又看重权重和数据都开放的场景，可以把它放进候选；同一合集里有 GGUF。

来源：[Villanova2 - a VillanovaAI Collection](https://huggingface.co/collections/VillanovaAI/villanova2) · [Villanova2 - a VillanovaAI Collection](https://huggingface.co/VillanovaAI/Villanova2-15B-A3B)　`模型` `开源`

### Vimoo 1.0 开源文生视频与图生视频模型

Vimoo-AI 开源 Vimoo 1.0 视频生成模型，文生视频（T2V）和图生视频（I2V）各用一个约 11.7B 的模型，另有更轻的 Vimoo 1.0 - Lite；代码和权重采用 Apache License 2.0，示例输出 1280 × 720、121 帧、24 fps。它同时提供 Diffusers、ComfyUI 和 MLX（Apple Silicon）的用法，本地跑视频生成的开发者可以对比试用。

来源：[Vimoo 1.0 - a Vimoo-AI Collection - Open-source video generation model family for text-to-video (T2V) and image-to-video (I2V)](https://huggingface.co/collections/Vimoo-AI/vimoo-10) · [Vimoo 1.0 - a Vimoo-AI Collection - Open-source video generation model family for text-to-video (T2V) and image-to-video (I2V)](https://huggingface.co/Vimoo-AI/Vimoo-1.0)　`开源` `视频` `模型`

### Axiomic Labs 发布 150M 参数提示词护栏模型 X3Guard

Axiomic Labs 发布 X3Guard-150M，对每条用户提示同时给出“有害”和“对抗”（越狱或提示注入）两个独立分数，团队称在他们评测的能同时给出两类判断的模型中，它最小且表现最好；它只检查提示词，不评估模型回复，许可为 Apache-2.0。体量小，适合放在网关或端侧做第一道输入过滤，但阈值应在自己的流量上验证。

来源：[Hugging Face](https://huggingface.co/AxiomicLabs/X3Guard-150M)　`安全` `模型` `开源`

## 📄 论文

### 801-30B-A3B-Base：把递归自我改进用到整个预训练

论文《No Second Run》把递归自我改进（RSI）应用到一次从零开始的前沿预训练上，把无法重跑的整次训练拆成多个可以闭环的小循环，结果是 801-30B-A3B-Base：一个在 11.8T tokens 上训练三个月的 30B-A3B MoE。作为基座，它超过 Qwen3-30B-A3B 和 Nemotron-3.5-Lightning-30B-A3B，只落后于更大的 Qwen3.5-35B-A3B；只做轻量 SFT（6B tokens，无 RL）就在四个 Agent 基准上取得最高平均分。基座和 SFT 数据都已开源，适合想在 30B-A3B 量级上自己做后训练的团队。

来源：[arXiv](https://arxiv.org/abs/2611.10719) · [Reddit 讨论](https://www.reddit.com/gallery/1xwt3ri)　`论文` `训练` `开源`

### APEX：用条件偏移做少步流式视频生成

论文把 APEX 扩展到流式视频生成：用条件偏移在生成器内部估计生成分布的速度场，去掉了 DMD 需要的独立 fake-score 网络。在 180 秒视频上，APEX 在指令遵循上相对 S2-Avatar 获得 +30.0% 的净人类偏好；同等训练设置下，峰值显存比 DMD 低 4.4%，平均迭代时间短 9.2%。对做少步蒸馏的团队，这是一种省掉额外网络、降低训练开销的做法。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.14033)　`论文` `视频`

## 🛠 开源与工具

### Univer：给产品和 Agent 用的开源 Office SDK

Univer 是一套嵌入式 Office SDK，把表格、文档的编辑、计算、协作和文件处理带进自己的产品；AI SDK 把这些能力接到现有的 Agent 和工作流里，Agent 可以直接调用同一套开源 API。开源核心为 Apache-2.0，Server SDK 和商业 AI SDK 扩展单独授权。需要让 Agent 读写表格和文档的产品可以参考，今天登上 GitHub Trending 榜首。

来源：[GitHub Trending](https://github.com/dream-num/univer)　`开源` `工具` `Agent`

### AG-UI：把 Agent 接进前端的事件协议

AG-UI 是一个开放、轻量、基于事件的协议，规范 AI Agent 与用户界面应用之间的连接：Agent 后端在运行中发出约 16 种标准事件，前端据此渲染；社区集成里已支持 Claude Agent SDK 等框架。做 Agent 产品前端的开发者可以用它代替自定义的流式协议。

来源：[GitHub Trending](https://github.com/ag-ui-protocol/ag-ui)　`开源` `Agent` `工具`

### google-labs-code 发布 Stitch 设计工具的 Agent Skills 库

google-labs-code/stitch-skills 是一组配合 Stitch MCP 服务器使用的 Agent Skills，遵循 Agent Skills 开放标准，可用于 Antigravity、Gemini CLI、Claude Code、Cursor 等编码 Agent，Claude Code 一条 npx 命令即可装进项目。注意项目声明它不是 Google 官方支持的产品。用 Stitch 做 UI 设计的开发者可以借它把设计和代码生成串起来。

来源：[GitHub Trending](https://github.com/google-labs-code/stitch-skills)　`工具` `Agent` `代码`

### NVIDIA 开源 SkillEvaluator，评估 Agent Skills 的质量和效果

NVIDIA 开源 SkillEvaluator，按三层评估 Agent Skills：校验格式与安全、检测重复或重叠的指导、在沙箱里对比用和不用这个 skill 时 Agent 的表现；pip 安装后，第一层检查无需 API key 即可运行。它是 NVIDIA Verified Skills 流程的一部分，维护 skill 库的团队可以用它给 skill 做质量门禁。

来源：[GitHub Trending](https://github.com/NVIDIA/SkillEvaluator)　`开源` `Agent` `工具`

## ⚡ 快讯

- **Domyn 在 JUPITER 超算上试训欧盟开放模型 EUROPA** 据 MACCUS 报道，Domyn 在公共超算 JUPITER 上试训欧盟开放模型 EUROPA，测试配置为 951.9 billion 参数的 MoE，每个 token 只激活 32.8 billion。 [maccus.fr](https://maccus.fr/en/eu-open-ai-model-europa/)
- **Sebastian Raschka 长文讲解现代 LLM 的位置编码** Sebastian Raschka 发表长文，用图示、少量数学和一个小型 PyTorch 实现讲解 RoPE 等位置编码方法，以及现代架构如何调整或省略显式位置编码。 [Sebastian Raschka](https://magazine.sebastianraschka.com/p/understanding-positional-embeddings) · [HN 讨论](https://news.ycombinator.com/item?id=50506376)
