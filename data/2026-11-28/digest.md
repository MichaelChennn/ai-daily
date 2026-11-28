# 2026-11-28 · AI 晨报

## 今日要点

- FLUX 3 Image Klein 开放权重，主打图像编辑、文本生图与最多 10 张参考图合成，并提供 ComfyUI 打包版本。
- MemT-1.0-Pro 把动态记忆做成模型原生能力，在 128K 历史长度下相对完整上下文 KV cache 省下约 66× 存储。
- 智谱系开源医疗多模态模型 LingSante-3.1-air-VL 采用 MoE，124B 总参数、每 token 激活 5.5B，支持 256K 上下文。

## 🔥 头条

### FLUX 3 Image Klein 发布开放权重图像模型

Black Forest Labs 推出 FLUX 3 Image Klein，一个 5.6B 开放权重模型，可在同一模型里完成图像编辑、文本生图与最多 10 张参考图合成，并支持用 bounding box 引导布局，文本编码器为 Qwen3-VL-4B-Instruct。官方同时提供面向 ComfyUI 的重打包仓库，包含 BF16、int8 与 NVFP4 版本，int8 文件可在 8 GB 显存的 RTX 3070 上运行。

来源：[Hugging Face Trending Models](https://huggingface.co/black-forest-labs/flux-3-image-klein-comfy)　`图像` `开源` `工具`

### MemT-1.0-Pro 发布，记忆成为模型原生能力

MemTensor 发布 MemT-1.0-Pro，将动态本地记忆与可训练的超记忆整合进模型计算，在推理时无需访问原始上下文即可保留并利用历史信息。其持久状态大小恒定，在 128K 历史长度下相比完整上下文 KV cache 减少约 66× 存储。该模型基于 NVIDIA Nemotron 骨干，权重规模为 565B params，可通过 Transformers、vLLM 与 SGLang 使用。

来源：[Hugging Face Trending Models](https://huggingface.co/MemTensor/MemT-1.0-Pro)　`模型` `推理` `Agent`

### LingSante-3.1-air-VL 开源医疗多模态 MoE 模型

蚂蚁集团医疗团队开源 LingSante-3.1-air-VL，这是其首个开源的大型多模态医疗模型，基于 Ling-3.0-flash-VL，拥有 124B 参数、每 token 激活 5.5B，支持 256K-token 上下文。模型面向影像报告生成、多模态健康评估、医学检索与证据综合、医疗 GUI 代理四类场景，官方同时给出 SGLang 与 vLLM 部署方式，并强调其为研究模型、不可独立诊断。

来源：[Hugging Face Trending Models](https://huggingface.co/inclusionAI/LingSante-3.1-air-VL)　`模型` `多模态` `开源`

### GigaChat 4 开放 37B-A4B 混合架构 MoE 权重

GigaChat 4-37B-A4B 权重上线 Hugging Face，采用 MoE 架构并融合 DeepSeek Sparse Attention 与 Gated DeltaNet，总参数 37B、每 token 激活 4B，上下文窗口达 1,048,576 tokens。该模型在同一 checkpoint 内支持 instant 与 reasoning 两种模式，可按请求切换，并提供递归 MTP 与 DFlash2 两种推测解码方式，官方给出基于 SGLang 的部署脚本。

来源：[Hugging Face Trending Models](https://huggingface.co/ai-sage/GigaChat4-37B-A4B)　`模型` `推理` `开源`

## 🧠 模型

### Ming-Image-0.2-Design 开源升级版设计生图模型

inclusionAI 升级并开源 Ming-Image-0.2-Design，新版本改善了复杂构图、光照与文字渲染，可用于电商主图、UI 设计草稿与空间渲染。相比上一代分层模型，它把设计图分解进一步细化到角色部件层级，为下游编辑与动画提供素材，官方建议配合结构化提示词与 prompt enhancer 使用。

来源：[Hugging Face Trending Models](https://huggingface.co/inclusionAI/Ming-Image-0.2-Design)　`图像` `开源` `多模态`

### Haru-4B 开源全双工语音对话基础模型

Haru-4B 是一个低延迟、多语言的全双工连续语音对话基础模型，可同时听与说，每 133 ms 处理一帧用户音频并生成自己的音频与文本，采样频率为 7.5 Hz。音频以每帧 64 维隐变量表示，由 MLP head 以 MeanFlow 一步采样得到，没有独立音频 Transformer，也不用离散音频 token；模型基于 Qwen3.5-4B 文本骨干，约 12 GB 显存即可运行。

来源：[Hugging Face Trending Models](https://huggingface.co/higurashi-ai/Haru-4B)　`语音` `开源` `多模态`

### Inworld 开源 48 kHz 人声分离模型

Inworld 开放 Apache-2.0 协议的 Voice Isolator v1，面向嘈杂录音与实时音频做人声隔离，提供离线与实时两个 checkpoint 共用一套架构：离线版按 8 s 分块处理，实时版为因果流式，带 20 ms 前瞻、算法延迟 63 ms。模型可从输入中减去分离出的人声以提取背景噪声或伴奏残差，但不能做说话人挑选，也不修复录音中已丢失的频段。

来源：[Hugging Face Trending Models](https://huggingface.co/inworld/voice-isolator)　`语音` `开源` `工具`

## 📄 论文

### Stable GDN-2 解决线性注意力长上下文训练状态爆炸

论文 Stable Gated DeltaNet-2 把 GDN-2 长上下文训练失败归因于擦除操作在读取与修改方向上的不对称，导致非正态擦除算子的方向增益跨 token 累积，触发状态指数增长。论文提出对称擦除与衰减调节的残差写入方案，在保留分块并行计算的同时给出 O(T) 的状态增长上界；在约 1.6B 参数模型上，128K RULER 平均分较 GDN-2 提升 6.80 分。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34051)　`论文` `训练` `推理`

### OS-Omni 评测跨平台长程计算机操作智能体

OS-Omni 是一个跨平台计算机操作智能体基准与执行环境，覆盖 Windows、Ubuntu、macOS、iOS、Android 与 Web，首版 v1 包含每个平台 48 个任务以及 12 个桌面与 Android 手机配对的跨平台工作流。人工研究显示任务平均需要 67.54 次交互，显著高于 OSWorld 参考的 15.0 次；v1 上最强的 Claude Opus 5.5 平均成功率为 68.5%，落后 77.3% 的人类参考 8.8 分。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34232)　`论文` `Agent` `评测`

### 编码智能体在视觉推理上超过视频生成模型

论文让编码智能体与视频生成模型在完全相同的第一帧、提示词与评测器下回答同一批视觉推理任务，前者用程序渲染答案视频而非去噪像素。在 VBVR-Pro-Bench 的 500 个实例上，Codex 搭配 gpt-6-astra 得 0.923，Claude Code 搭配 Fable 5.1 得 0.894，Gemini CLI 搭配 Gemini 3.1 Pro 得 0.893，均比最强视频模型高出 0.22 以上；23 个可运行开放权重模型中最好的 GLM-5 得分 0.572。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34813)　`论文` `Agent` `视频` `评测`

### ShowNow 让交互式世界模型提前备好候选未来

ShowNow 提出细粒度推测式流式框架，在播放期间利用空闲算力预先准备动作条件化的未来视频，把输入到显示的延迟从响应路径上移开。论文报告在单张 H100 上其 5B 模型可维持 480p、16 fps 并准备八个未来；ViZDoom 环境下完整部署将输入到显示的中位延迟从 620 ms 降至 208 ms，重启空帧比例从 1.56% 降到 0.09%。代码、权重与数据集均以 Apache 2.0 发布。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34693)　`论文` `视频` `开源`

### DRBench Pro 按知识覆盖评测深度研究智能体

DRBench Pro 是一个以结构化知识覆盖为核心目标的深度研究智能体基准，自动化流程从 Wikipedia 构建本地知识树并采样子图来生成研究问题与带证据的 rubric，每条 rubric 对应树中的一条关系，从而同时衡量广度与深度。基准包含 24 个领域共 144 个案例、44,102 条 rubric；评测 16 个深度研究智能体后，最好者的总体覆盖率为 57.04%。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34852)　`论文` `Agent` `评测`

### Vernier 揭示时序预测榜单的分辨率不足

论文提出榜单分辨率这一概念：它衡量一个榜单的数据集能分辨多小的分数差距，并据此发布工具 Vernier，可基于榜单已公开的文件计算该指标。GIFT-Eval 能分辨 6.8 个名次，而相邻名次分差为 0.91，其前十名跨度不足两个可分辨步长；四个榜单上按全体参赛者排名的规则翻转了 43 对前十名组合，且没有任何一项被重新评测。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.31619)　`论文` `工具` `评测`

### ProxyGenBench 评测结构代理引导的视频生成

ProxyGenBench 研究视频生成器跟随动画化 3D blockout 的能力，把要求拆成保留结构、补全缺失内容并纠正代理伪影、把文本图像音频条件绑定到正确实体与事件三类。基准包含来自 60 个场景、三类场景任务的 312 个评测用例，控制代理保真度、文本细节与多模态输入的变化，并使用逐例核对的 checklist 评测五个视频生成器。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.34457)　`论文` `视频` `评测`

## 🛠 开源与工具

### Hugging Face 用 Trainium3 跑通 LTX-2.5 视频生成

Hugging Face 团队借助 AWS 的 Trainium3 机器，用 diffusers 把 Lightricks 的 LTX-2.5 跑上 NeuronCore：通过张量并行与序列并行在 32 个核心上完成推理，模型加载后生成一段带声音的 10 秒片段用时 22 到 23 s，分辨率为 2048×1024。其为影片编排的 Python 代码约 160 行，示例工程与样片已放在 dacorvo/video-generation。

来源：[Hugging Face Blog](https://huggingface.co/blog/video-trainium3)　`工具` `视频` `硬件`

### ollama v0.40.19 发布，更新推理与历史缓冲

ollama 发布 v0.40.19，主要变更包括 inkling2 面向短历史的加速、draft proposals 与 conv snapshots，以及 mlxrunner 精简 Engram 历史缓冲，另有 llama-server 版本更新。

来源：[GitHub Releases](https://github.com/ollama/ollama/releases/tag/v0.40.19)　`工具` `推理`

## ⚡ 快讯

- **Latent Space 播客讨论 AI 训练数据市场** G2i 创始人 Gabe Greenberg 讲前沿实验室如何决定购买训练数据：独家数据更贵，竞争对手也能买到的数据则走折扣；好任务应略微超出模型当前能力，需资深工程师设计任务、挑选起始数据并构建 verifier。 [Latent Space](https://latent.space/p/inside_the_ai_training_data_market_gabe_greenberg_g2i/)
