# 2026-11-17 · AI 晨报

## 今日要点

- Hugging Face 把 Inference Providers 的语言模型请求改由 OpenRouter 路由，代码不用改，但语言模型不能再用自己的 provider API key。
- vLLM v0.34.0 默认启用 Extensible KV cache 并移除 Model Runner V1，升级前要看破坏性变更。
- Anthropic 把漏洞披露期限从 90 天缩短到 30 天和 45 天，适用于 2027 年 1 月 1 日及之后报告的漏洞。

## 🔥 头条

### Hugging Face 把语言模型推理路由切换到 OpenRouter

Hugging Face 宣布，Inference Providers 上的语言模型请求现在经由 OpenRouter 路由：按实时测量在 80+ 家 provider 之间分配请求，某家失败时在同一次调用内重试下一家，Hugging Face 不在 provider 价格上加价。仍可在模型 id 后加 :fastest、:cheapest 或 provider 名指定策略；语言模型不能再用自己的 provider API key，图像、视频和音频生成照旧直接走 Hugging Face。用 HF token 调开放权重模型的代码不用改，自带 provider key 的用户需要检查配置和账单。

来源：[Hugging Face Blog](https://huggingface.co/blog/openrouter) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xy9o6j/hugging_face_switched_its_language_model/)　`产品` `推理` `开源`

### vLLM v0.34.0 发布：默认启用 Extensible KV cache，移除 Model Runner V1

vLLM v0.34.0 新增 10 个模型（包括 Mistral Large 4、MiniMax-M3.1-Flash、Nemotron-3.5-Transcribe），默认启用 Extensible KV cache，按 warmup 后实际空闲的显存确定 KV cache 大小；Model Runner V2 成为唯一的 GPU runner，Blackwell 和 MI355X 上 decode 最高快 1.95×。升级前注意破坏性变更：默认 --block-size 从 16 改为 64，gpu memory utilization 默认变为 1.0，不再发布 ROCm 7.2 镜像，并要求 huggingface hub 2.0.0。生产环境部署 vLLM 的团队应先对照 release notes 里的升级清单再升级。

来源：[GitHub Releases](https://github.com/vllm-project/vllm/releases/tag/v0.34.0)　`开源` `推理`

### Anthropic 把漏洞协调披露期限从 90 天缩短到 30 天和 45 天

Anthropic 更新协调漏洞披露（CVD）政策：高危和严重漏洞的披露期限从 90 天缩短到 30 天，其他漏洞缩短到 45 天，适用于 2027 年 1 月 1 日及之后报告的漏洞；维护者不回应时 15 天（原为 30 天）后升级到外部协调方，补丁发布后 30 天（原为 45 天）公开完整技术细节。Anthropic 的理由是现有披露规范形成于 AI 能发现漏洞之前，默认修复按人的速度推进。收到 Anthropic 漏洞报告的厂商和开源维护者需要按更短的期限安排修复。

来源：[Anthropic Research](https://www.anthropic.com/research/coordinated-vulnerability-disclosure-timelines)　`安全` `行业`

## 🧠 模型

### NVIDIA 发布连续扩散语言模型 Nemotron-Labs-Sigma 8B/3B

Nemotron-Labs-Sigma-8B-instruct 是 8B 参数的连续扩散语言模型：不逐个 token 生成，而是在 16-D 连续 token 嵌入空间里对高斯噪声去噪，按块并行解码并复用 KV cache，同系列还有 3B 版本。模型卡给出的速度是单张 H100 上、DDPM 采样每个 64-token 块 32 步时，生成 256 个 token 约 120-140 tokens/s；最大上下文 8,192 tokens，只支持英文，采用 NVIDIA Nemotron Open Model License。想研究扩散式并行解码的开发者可以直接拿它做实验。

来源：[nvidia/Nemotron-Labs-Sigma-8B-instruct](https://huggingface.co/nvidia/Nemotron-Labs-Sigma-8B-instruct) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xxwg6w/nvidianemotronlabssigma_8b3b/)　`模型` `开源`

### 上海人工智能实验室开源科学多模态模型 Sage S2.1 Flash

Sage S2.1 Flash 是上海人工智能实验室面向多轮分析与验证类科研任务的多模态模型，结合科学数据理解、信息检索、编程和工具调用，支持分子图、晶体结构、蛋白质序列与 3D 结构等十多种科学输入。模型 321B 参数，代码和权重以 MIT License 发布；在 MLE-bench Lite 上得 90.3，高于 DeepSeek-V4.1-Flash-1017 的 89.2。做科研或机器学习工程 Agent 的团队多了一个可以自己部署的开放权重选项。

来源：[Hugging Face](https://huggingface.co/internlm/Sage-S2.1-Flash)　`模型` `开源` `多模态`

### Liquid AI 发布决策模型 d1.2 与 d1.2-ultra，新增音频输入

Liquid AI 推出决策模型新版本 d1.2 和 d1.2-ultra，支持音频输入并新增五类任务，例如从输入中读取数值；d1.2-ultra 在 Artificial Analysis Decision Index v2.1 上得 75，比此前最好的决策模型高两分。两个模型已上线 Liquid API，只按输入 token 计费，d1.2 为 $0.02，d1.2-ultra 为每百万输入 token $0.042。需要带概率输出的分类、抽取类调用，可以拿它和通用 LLM 比一比效果和成本。

来源：[Liquid AI](https://www.liquid.ai/blog/d1-2)　`模型` `多模态` `语音`

## 📄 论文

### miHoYo 提出通用游戏智能体模型 Gamer

miHoYo Honkai AI 研发团队提出 Gamer，一个面向长时程、实时游戏交互的通用视觉-语言-动作基础模型：先在数万小时设备级键鼠交互数据上继续预训练，再做稀疏思考指令微调和多轮强化学习，并用 Streaming-vLLM 推理引擎支撑实时控制。论文称它在多款 3D 开放世界游戏中展现出与熟练玩家相当的操作效率，在 2D 游戏基准上也有竞争力。做 GUI 或游戏 Agent 的开发者可以参考它用键鼠轨迹扩展数据的思路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18397) · [i.redd.it](https://i.redd.it/iyknzc0chy1i1.png) · [mihoyo-gamer.github.io](https://mihoyo-gamer.github.io/)　`论文` `Agent` `多模态`

### MIRIX-2.0：多智能体记忆系统，LongMemEval-S 领先最强基线 14.3 分

MIRIX-2.0 是给 LLM Agent 用的多智能体记忆系统，在参与比较的五个问答基准中有四个准确率最高：LoCoMo 91.4%、LongMemEval-S 72.6%，后者比最强基线高 14.3 分。它不需要微调，闭源和开源模型都能用，代码已公开。给 Agent 加长期记忆的开发者可以把它加进对比清单。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12068)　`论文` `Agent` `开源`

### MMFlash：视觉语言模型的扩散式投机解码，最高 3.58× 无损加速

论文发现视觉依赖越强的 token 越难被草稿模型猜中：接受率从视觉依赖最低四分位的 46% 降到最高四分位的 22%。MMFlash 在 DFlash 基础上，训练时加权这些视觉依赖 token，长视频输入再用稀疏注意力，在多个多模态基准上实现最高 3.58× 的无损解码加速，比 EAGLE-3 和 DFlash 分别高出最多 195.4% 和 17.1%。部署视觉语言模型的团队可以关注这类专门针对多模态的 drafter。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18482) · [i.redd.it](https://i.redd.it/hiysxawefy1i1.gif)　`论文` `推理` `多模态`

### WebArena-Pro：覆盖音频与视频的可复现 Web Agent 基准

WebArena-Pro 包含 20 个自托管应用、六个领域的 300 个人工校验任务，模态覆盖文本、视觉、音频和视频，每个任务隔离执行，便于可复现的并行评测。基准支持 BrowserGym 和 Harbor 等 harness 接入，可以运行 MCP 和编程 Agent。做浏览器 Agent 的团队可以用它测试涉及多媒体内容的网页任务。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17955)　`论文` `Agent` `多模态`

## 🛠 开源与工具

### Microsoft Research 开源 TokenEconomizer，降低编程 Agent 成本

TokenEconomizer 是 UC Berkeley、Microsoft Research 和 Microsoft Security 推出的开源插件，不修改 Agent 和模型，而是从仓库里过去的会话中学习：用一行式的仓库笔记（micro-skills）补充上下文、裁剪用不到的工具、在 Agent 反复失败时介入。在 SWE-Bench 上，它让五种 Agent–模型组合的单任务平均成本降低 18.4–30.9%，其中四种的 Pass@1 还有提升。每天在同一个代码库里用 Claude Code 这类 Agent 的开发者可以试试。

来源：[Microsoft Research](https://www.microsoft.com/en-us/research/blog/tokeneconomizer-learning-from-experience-to-make-ai-coding-agents-more-efficient/)　`工具` `Agent` `代码`

### Coral：让 Agent 写 TypeScript 程序调用工具的开源网关

Coral 是部署在 Agent 和业务系统之间的开源自托管网关：Agent 通过编写简短的 TypeScript 程序调用工具，每个程序在没有网络、凭据和 import 的全新 V8 isolate 中运行，Coral 按工作区策略检查每次调用后再注入凭据转发。跑通的程序可以存成自定义工具复用；核心代码采用 Apache License 2.0。想让 Agent 接入内部系统又要收紧权限的团队可以看看。

来源：[GitHub](https://github.com/withcoral/coral)　`工具` `Agent` `安全`

## ⚡ 快讯

- **腾讯发布 Hy4 flash：224B 总参数、每 token 激活 12B** 腾讯称 Hy4 flash 是迄今最具性价比的 Hy 模型，总参数 224B（含 64B Engram 参数）、每 token 激活 12B，和 Hy4 一样原生多模态、支持 1M token 上下文，API 价格显著更低。 [hy.tencent.ai](https://hy.tencent.ai/research/hy4-flash)
- **Claude Code v2.1.326：agent teams 下也可开启 Code Mode** Claude Code v2.1.326 支持在启用 agent teams 时打开 Code Mode，并在 --allowedTools、--disallowedTools 或 --tools 里有不完整规则时给出启动警告。 [GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.326)
- **OpenAI 启动第一阶段嵌入式安全评估** OpenAI 与 Apollo Research、METR、Transluce 和 Goodfire 四家独立评估机构签约，让外部专家长期深入访问其内部模型和系统，评估模型对齐和安全措施的有效性。 [OpenAI News](https://openai.com/index/our-first-phase-of-embedded-assessments)
- **Cohere Compass 推出视频检索 Video Intelligence** Cohere 在 Compass 中推出 Video Intelligence，可按语音和画面内容检索视频库，返回带时间戳的片段、转写和画面描述，Agent 可通过 Compass MCP server 接入，目前在招募设计合作伙伴。 [Cohere](https://cohere.com/blog/video-intelligence-preview)
- **逆向分析：Windows 11 会记录用户用了哪些编程 Agent** 一篇逆向分析发现，作者测试的 Windows 11 中 MissionControlAggregator.dll 会记录用过哪些编程 Agent 和开发工具，允许可选诊断数据时排队上传给 Microsoft。 [xusheng.dev](https://xusheng.dev/posts/windows-coding-agent-telemetry/)
- **Gemma 4 小模型 tokenizer 修复 219 个 glitch token** gemma-4-E4B-it 合并了一个只改 tokenizer.json、不动权重的补丁，修复 219 个会导致模型行为异常的 glitch token；据社区帖，E2B 和 12B 也做了同样修复。 [Hugging Face](https://huggingface.co/google/gemma-4-E4B-it/discussions/50)
