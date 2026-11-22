# 2026-11-22 · AI 晨报

## 今日要点

- 腾讯开源 Hy4 旗舰模型：770B 总参数、每 token 激活 49B，上下文长度 1M。
- Apple 发布 Depth Pro 2，开放代码和多个尺寸的权重，仅限非商业研究。
- Transformers v5.24.0 加入 Inkling 2 Mini、Apertus 1.5 和 NVIDIA 的 Dory。

## 🔥 头条

### 腾讯开源 Hy4：770B 总参数、每 token 激活 49B

腾讯 Hy 团队开放了新一代 MoE 旗舰模型 Hy4 的权重，同时提供 Hy4-FP8 和预训练 base 模型，支持文本、图像和视频理解，上下文长度 1M。模型卡称它在 579 个真实金融任务上排在开放权重模型第一，但也承认与顶级闭源模型仍有明显差距。许可是 Tencent Hy License，商用前要先读条款；需要自部署长上下文大模型的团队多了一个开放权重选项。

来源：[Hugging Face Trending Models](https://huggingface.co/tencent/Hy4)　`模型` `开源` `多模态`

### Apple 发布 Depth Pro 2：一个网络同时做图片和视频的度量深度

Apple 机器学习研究团队发布 Depth Pro 2，从普通相机拍摄的照片、视频或实时画面逐像素估计以米为单位的深度，按输入的完整分辨率输出。作者指出以往方法要在时间一致性和边缘锐利度之间取舍，Depth Pro 2 用单个网络同时做到度量准确、锐利和时间一致，并开放代码和从 24M 到 872M 参数的多个尺寸权重。权重采用 Apple Machine Learning Research Model license，仅限非商业研究；需要视频深度的研究项目可以按速度和质量在几个尺寸里选。

来源：[Apple Machine Learning Research](https://machinelearning.apple.com/research/depth-pro-2-monocular) · [Hugging Face Trending Models](https://huggingface.co/apple/DepthPro2)　`模型` `图像` `视频`

## 🧠 模型

### pi-H3：MiniMax H3 音视频生成只要 2 到 4 步

斯坦福等作者在 Hugging Face 发布 pi-H3，为 MiniMax H3 提供 2 步和 4 步适配器，结合 pi-Flow v2 少步蒸馏和 DWD（Decoding Without a Decoder），在最后一步直接预测视频帧，跳过 VAE 解码器。作者称这是生成带同步音频的 MiniMax H3 视频最快的方式；适配器支持文本、首帧和尾帧条件，另有 ComfyUI 用的 INT8 版本，使用受 MiniMax H3 Community License Agreement 约束。

来源：[Hugging Face Trending Models](https://huggingface.co/Lakonik/pi-H3)　`视频` `开源`

## 📄 论文

### InclusionMed：按医疗角色和能力评测，前沿模型总分 17.5 到 49.1

InclusionMed 是一个开放的医疗 AI 评测项目，按三种医疗角色和三种 AI 能力组织基准；首版从 388 个候选里筛出四个公开基准，加上私有诊断推理基准 InclusionMed-DxFiles，覆盖九个格子中的三个。前沿 LLM 总分在 17.5 到 49.1（满分 100）之间，排名随角色和能力变化，排名前十的模型在患者沟通上的得分都高于临床决策。做医疗应用的开发者应按具体场景选模型，分数相近的模型推理成本也可能差很多。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.21218)　`论文`

### VibePrevisBench：评测编码 Agent 在 Blender 里搭 4D 场景

VibePrevisBench 让 Agent 根据需求在 Blender 中写出可执行的 4D 场景并渲染代理视频，共 242 个任务，输入包括脚本、照片、续写和参考视频；评分分为重跑代码、对照隐藏事实的 Scene Check 和由 VLM 判断的 Screen Check。作者分析了 11 个前沿编码 Agent，发现多模态理解（尤其是空间和镜头运动）拉开差距，Agent 会检查自己的渲染却改不掉错误。做创意工具类 Agent 时，逐项对照需求核验渲染结果是目前的短板。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.15789) · [arXiv](https://arxiv.org/abs/2611.15789)　`论文` `Agent` `代码`

### AscendGYM：评测 Agent 在昇腾 NPU 上优化 kernel

AscendGYM 是面向 Ascend NPU 的 kernel 优化基准，首批 48 个 kernel 分三个难度，测试用例的数据类型和张量形状取自真实训练和推理任务；支持只评模型和评“模型加 harness”两种模式。论文还提出 Speedup-Token Score（STS），把加速幅度和 token 成本放在一起算。在昇腾上做训练或推理优化的团队，可以用它衡量编码 Agent 在预算内的实际优化能力。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.17621)　`论文` `硬件` `Agent`

## 🛠 开源与工具

### Transformers v5.24.0 加入 Inkling 2 Mini、Apertus 1.5 和 Dory

Hugging Face Transformers v5.24.0 新增一批模型：Thinking Machines Lab 的 Inkling 2 Mini（第 6 到 17 层循环运行三次）、Swiss AI Initiative 的多模态模型 Apertus 1.5 及其音频分词器 WavTokenizer、NVIDIA 的循环语言模型 Dory，以及 HY4-VL 和 Meta FAIR 覆盖 1,600 多种语言的 Omnilingual ASR。Dory 可以在同一个 checkpoint 上于推理时调整循环次数、用速度换质量；升级后即可直接用 Transformers 加载这些模型。

来源：[GitHub Releases](https://github.com/huggingface/transformers/releases/tag/v5.24.0)　`工具` `开源` `模型`
