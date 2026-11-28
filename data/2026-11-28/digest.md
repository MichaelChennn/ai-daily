# 2026-11-28 · AI 晨报

## 今日要点

- GigaChat 4 开放权重：708B 总参数、每 token 激活 41B，支持一百万 token 上下文，另有 37B（4B 激活）版本。
- 弗吉尼亚州和俄勒冈州总检察长起诉 SpaceX，指控 Grok 生成未经同意的性化图像和 CSAM。
- OS-Omni 跨 Windows、macOS、iOS、Android 等平台测试电脑操作 agent，最强的 Claude Opus 5.5 平均成功率 68.5%，仍低于人类的 77.3%。

## 🔥 头条

### GigaChat 4 开放权重：708B 总参数、激活 41B

ai-sage 在 Hugging Face 发布 GigaChat 4，旗舰版 708B 总参数、每 token 激活 41B，结合 MoE、DeepSeek Sparse Attention（DSA）和 Gated DeltaNet（GDN），支持一百万 token 上下文；即时和推理两种模式合在同一个模型里，按请求切换，另有 37B（4B 激活）的小尺寸版本。708B 版本采用 MIT License，需要长上下文、多语言或 agent 任务的开源大模型时多了一个可选项。

来源：[ai-sage/GigaChat4-708B-A41B](https://huggingface.co/ai-sage/GigaChat4-708B-A41B) · [ai-sage/GigaChat4-37B-A4B](https://huggingface.co/ai-sage/GigaChat4-37B-A4B)　`模型` `开源`

### 两州总检察长起诉 SpaceX，指控 Grok 生成未经同意的性化图像

弗吉尼亚州总检察长 Jay Jones 起诉 X、xAI 和 Grok 的母公司 SpaceX，俄勒冈州总检察长 Dan Rayfield 提起了一起类似的独立诉讼，指控 Grok 生成 CSAM 和未经同意的私密图像，而公司公开宣称有防护措施；公告引用 CCDH 的研究估计，Grok 在 X 上生成并发布了约三百万张性化图像。对做图像和视频生成产品的团队来说，这类诉讼把“宣传过的安全措施是否真的到位”变成了法律问题。

来源：[oag.state.va.us](https://www.oag.state.va.us/media-center/news-releases/jay-jones/3162-attorneys-general-jones-and-rayfield-file-suit-against-spacex-parent-company-of-x-xai-and-grok-over-creation-and-promotion-of-child-exploitation-and-non-consensual-images-on-platform)　`安全` `行业`

### Kimi 推出 Kimi for Science，向科研团队发放 API 额度

Kimi 面向自然科学、工程和交叉学科的研究者推出 Kimi for Science 计划，入选者可获得最高 $20,000 的 Kimi API 额度（约 7B tokens），以及技术支持和新模型的抢先体验；第一批申请截止到 Dec 8。用 LLM 做文献综述、数据分析或实验辅助的科研团队可以申请，额度只能用于调用模型，不是现金资助。

来源：[kimi.ai](https://www.kimi.ai/news/kimi-for-science-program)　`产品` `行业`

## 🧠 模型

### inclusionAI 开源设计图生成模型 Ming-Image-0.2-Design

inclusionAI 开源 6B（DiT）的设计图生成模型 Ming-Image-0.2-Design，改进了复杂构图、光影和文字渲染，可用于电商主图、UI 设计稿和空间效果图，采用 MIT License。模型卡称在 Artificial Analysis 文生图榜（AA-Image-T2I v2.1）上暂列开放权重模型第一；需要能渲染文字的开源出图模型时可以试一试。

来源：[Hugging Face Trending Models](https://huggingface.co/inclusionAI/Ming-Image-0.2-Design)　`模型` `开源` `图像`

### MemTensor 发布记忆基座模型 MemT-1.0-Pro

MemTensor 发布 MemT-1.0-Pro，基于 NVIDIA-Nemotron-3-Ultra-550B-A55B，总参数 554B、激活 59B，另加 4.23B 可训练的记忆参数；模型把持续演化的记忆放进计算本身，推理时不必访问原始上下文。官方称在 128K 历史长度下，存储比完整 KV cache 少约 66×，适合关注长期记忆和长会话成本的 agent 开发者关注。

来源：[Hugging Face Trending Models](https://huggingface.co/MemTensor/MemT-1.0-Pro)　`模型` `Agent`

## 📄 论文

### OS-Omni：跨桌面、手机和 Web 的长流程电脑操作 agent 基准

OS-Omni 是覆盖 Windows、Ubuntu、macOS、iOS、Android 和 Web 的实时基准，v1 每个平台 48 个任务，另有 12 个桌面加 Android 手机的跨平台流程；人工研究显示任务需要 67.54 步交互，远多于 OSWorld 的 15.0 步。最强的 Claude Opus 5.5 平均成功率 68.5%，比人类的 77.3% 低 8.8 个点，做电脑操作 agent 的团队可以用它测长流程和跨设备能力。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34232)　`论文` `Agent`

### Stable GDN-2：修复 Gated DeltaNet-2 长上下文训练失稳

论文发现 Gated DeltaNet-2（GDN-2）长上下文训练失败的原因是擦除操作中读写方向不对称，导致循环状态指数增长；提出的 Stable GDN-2 改用对称擦除和带衰减调节的残差写入，保留分块并行计算。在约 1.6B 参数的模型上训练稳定，循环设置下 128K RULER 平均分比 GDN-2 高 6.80 分，用线性注意力做长序列模型的人值得一读。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34051)　`论文` `训练`

### 编码 agent 写程序做视觉推理，胜过视频生成模型

研究把同样的视觉推理任务交给视频生成模型和编码 agent：后者写程序渲染答案视频，用同一个评估器打分。在 VBVR-Pro-Bench 上，Codex、Claude Code 和 Gemini CLI 分别得 0.923、0.894 和 0.893，都比最强的视频模型高出 0.22 以上；对能从首帧和提示算出答案的任务，程序合成目前是更可靠的路线。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34813)　`论文` `代码` `视频`

### DRBench Pro：按知识覆盖度评测深度研究 agent

DRBench Pro 从 Wikipedia 构建知识树，自动生成研究问题和逐条评分细则，衡量报告覆盖了哪些研究方向、挖得多深，共 144 个案例、24 个领域、44,102 条细则。评测多个深度研究 agent，表现最好的总覆盖率为 57.04%，做研究类 agent 的团队可以拿它看广度和深度上的短板。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34852)　`论文` `Agent`

## 🛠 开源与工具

### Hugging Face 在 Trainium3 上用 LTX-2.5 生成带声音的视频

Hugging Face 的博客用 diffusers 在 AWS Trainium3 上运行 Lightricks 的 LTX-2.5，用一个 JSON 镜头列表串起多段视频；模型加载后，用半台机器生成一段 10 秒 2048×1024 带声音的片段需要 22 到 23 s，与 LTX 官方 API 相当。代码在 dacorvo/video-generation，想在 Trainium 上部署视频生成的开发者可以参考其中的并行和内存优化。

来源：[Hugging Face Blog](https://huggingface.co/blog/video-trainium3)　`工具` `视频` `硬件`
