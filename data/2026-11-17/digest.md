# 2026-11-17 · AI 晨报

## 今日要点

- Hugging Face 语言模型推理改由 OpenRouter 路由
- vLLM v0.34.0 默认启用可扩展 KV cache
- TokenEconomizer 用历史会话给编码 Agent 降本

## 🔥 头条

### Hugging Face 语言模型推理改由 OpenRouter 路由

Hugging Face 把 Inference Providers 从自建路由切换到 OpenRouter：每次请求按实时价格、速度和可靠性挑选供应商，失败时在同一次调用内重试，代码和 Hugging Face token 不变。需要注意，语言模型请求不再支持自定义供应商 API key，改为记在 Hugging Face 账户上；图像、视频和音频生成仍走原有路径。

来源：[Hugging Face Blog](https://huggingface.co/blog/openrouter) · [Hugging Face](https://huggingface.co/blog/openrouter)　`工具` `产品` `推理`

### vLLM v0.34.0 默认启用可扩展 KV cache

vLLM v0.34.0 把可扩展 KV cache 设为默认，按预热后实际空闲显存来定 cache 大小，并在 Blackwell 与 MI355X 上带来最高 1.95× 的解码提升和 1.6× 的吞吐提升。升级前需注意 Model Runner V1 已移除、默认 --block-size 改为 64、ROCm 7.2 镜像下线，并要求 huggingface_hub >= 2.0.0。

来源：[GitHub Releases](https://github.com/vllm-project/vllm/releases/tag/v0.34.0)　`开源` `工具` `推理`

### TokenEconomizer 用历史会话给编码 Agent 降本

UC Berkeley、Microsoft Research 与 Microsoft Security 推出开源插件 TokenEconomizer，它从仓库的历史会话中提炼微技能、裁剪无用工具并介入失败循环，无需修改 Agent 或底层模型。在 277 个真实修复任务上，它把成本降低 18.4–30.9%，且各测试仓库的成本都有下降、成功率基本稳定。

来源：[Microsoft Research](https://www.microsoft.com/en-us/research/blog/tokeneconomizer-learning-from-experience-to-make-ai-coding-agents-more-efficient/)　`Agent` `开源` `工具`

### miHoYo 团队开源 Gamer 游戏智能体模型

miHoYo 崩坏：星穹铁道 AI 团队推出通用视觉-语言-动作模型 Gamer，只通过截图、键盘和鼠标与 2D、3D 环境交互，不需要特权状态或游戏专用 API。项目用 10K+ 小时轨迹做持续预训练，配套 Streaming-vLLM 推理引擎在基准设置下把推理延迟降低 20× 以上，并在《崩坏：星穹铁道》主线挑战中处理超过 95% 的关卡。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18397) · [arXiv](https://arxiv.org/abs/2611.18397) · [mihoyo-gamer.github.io](https://mihoyo-gamer.github.io/)　`模型` `Agent` `开源` `视频`

## 🧠 模型

### MIRIX-2.0：六类记忆 Agent 的多智能体记忆系统

MIRIX-2.0 用六个分类型的记忆 Agent 保留完整记录，并用溯源超图索引情景与语义记忆，检索在明确预算下进行，因此证据量不随历史增长。它在 LoCoMo 上达到 91.4%、在 LongMemEval-S 上达到 72.6%，领先最强基线 14.3 分，且无需微调、代码公开。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.12068)　`论文` `Agent`

### V-JEPA-LM 读懂视频动态而非静态画面

V-JEPA-LM 把冻结的 V-JEPA 世界模型编码器接到 Qwen3 与 Llama（1B–8B）上，用反事实监督让语言模型去读像素变换带来的动态信息。作者报告其在十一个视频基准的各尺寸档位平均分领先，4B 模型得分 72.1，对比最佳开源 4B 的 61.1 和最佳开源 8B 的 64.8，代码与全部 6 个 checkpoint 已开放。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17831)　`论文` `模型` `视频` `多模态`

### Bonbon：仅用序列训练的分子交互基础模型

Output Labs 的 Bonbon 在约 3.2 万亿 token 的蛋白-配体序列对上训练，不含结构坐标和任务监督，却涌现出功能、结合位点和成键方式三类零样本能力。作者在 42M 到 1.6B 参数的六个规模上观察到能力在最大规模上出现跳变，而预训练损失是平滑下降的。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.14504)　`论文` `模型` `训练`

### Mobile AI Factory 自动为手机构建专用小模型

Mobile AI Factory 是一个智能体系统，给定任务和目标手机后，它自动微调并量化小模型，用真实设备测量来选择模型、精度、推理引擎和后端。作者在十项任务和四台 Android 手机上评测，端侧模型在五项任务上超过两个五-shot 前沿模型、另三项打平，最优配置也会随手机而变，代码已开放。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.13509)　`论文` `模型` `硬件` `Agent`

## 📄 论文

### Agentic Robotics：具身智能体评测框架与路线图

这篇论文提出以「Embodied System 2」（基础模型加具身 harness）作为 agentic robotics 的决策核心，并给出同时衡量模型能力与闭环系统表现的评测框架。作者认为社区尚缺统一定义、可靠评测和研究路线图，并梳理了通向持续自主的路线。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18359)　`论文` `Agent` `行业`

### VibePrevisBench：Blender 4D 场景生成的编码 Agent 基准

Kling-Keye 推出 VibePrevisBench，要求 Agent 把一句需求变成可执行的 4D 场景并渲染出代理视频，共 242 个任务、覆盖四类输入。评测分两层：规则式 Scene Check 重跑代码并按九个维度对照隐藏事实，VLM 式 Screen Check 判断通过的���实能否在代理视频中被识别。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15789)　`论文` `Agent` `代码` `视频`

### MMFlash：面向视觉语言模型的推测解码加速

MMFlash 先用 KL 散度定义 token 级视觉依赖度，发现接受率会从最低依赖四分位的 46% 降到最高四分位的 22%，据此自适应上调视觉相关 token 的权重，并在长视频上用稀疏注意力降低冗余计算。作者报告在多个多模态基准上取得最高 3.58× 的无损解码加速。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18482) · [arXiv](https://arxiv.org/abs/2611.18482)　`论文` `推理` `多模态` `视频`

### WebArena-Pro：支持音视频的可复现 Web Agent 基准

WebArena-Pro 包含 300 个任务和 20 个自托管 Web 应用，覆盖六个领域类别，并把音频和视频与文本、视觉一起作为核心观测对象。最佳成绩由 Codex 搭配 GPT 6.1 Sol、Claude Code 搭配 Claude Opus 5.5 取得，均为 62.3%，OpenCode 搭配 Kimi 3.1 Pro 为 60.7%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17955)　`论文` `Agent` `评测`

## 🛠 开源与工具

### Claude Code v2.1.326 支持团队模式下的 Code Mode

Claude Code v2.1.326 允许在启用 agent teams 时开启 Code Mode，已开启时带团队的会话会直接以 Code Mode 启动。该版本还修复了后台会话丢失 LLM gateway、误报「Dangerous rm operation」、/rewind 恢复不完整等问题。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.326)　`工具` `Agent` `代码`

### MEM-SQL：用已验证 SQL 历史改进 Text-to-SQL

MEM-SQL 存储整条查询模板、可复用 SQL 片段和领域概念到 schema 元素的映射，只有当某层的所有要求都超过阈值时才启用，并在没有可用层时才按需查询 schema。作者在自建的 HARE 基准上用六个语言模型评测，平均执行准确率从直接生成的 37.1% 升到 50.0%，平均输入 token 减少 76.6%、延迟降低 68.8%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.18338)　`论文` `工具` `Agent`

## ⚡ 快讯

- **OpenAI 启动第三方嵌入式对齐评估** OpenAI 宣布第一阶段嵌入式评估，与 Apollo Research、METR、Transluce 和 Goodfire 合作，由外部机构独立评估模型对齐、安全护栏与监控系统。 [OpenAI News](https://openai.com/index/our-first-phase-of-embedded-assessments)
- **Continual-ARC：harness 持久化很少换来记忆能力** Continual-ARC 用 ARC-AGI 任务构造终身任务流，在相同预算下比较记忆式与权重式持续学习。作者报告多数 harness 方法不如单纯缓存示例的基线，也未在未见任务上带来提升，而权重式学习在泛化上表现更好。 [Hugging Face Daily Papers](https://huggingface.co/papers/2611.14505)
