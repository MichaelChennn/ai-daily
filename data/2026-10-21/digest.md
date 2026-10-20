# 2026-10-21 · AI 科技日报

## 今日要点

- DeepSeek 开源生产级推理框架 DeepInfer，并更新 DeepSeek-V4.1-Flash-1017 权重。
- Google 开源 TorchTPU，PyTorch 可以把 TPU 当作普通设备使用；PyTorch 2.15 也大幅提升了 Mac 上的推理速度。

## 🔥 头条

### DeepSeek 开源生产级推理框架 DeepInfer

DeepSeek 开源了支撑其线上大规模服务的推理框架 DeepInfer。此次开源版本提供离线推理，支持 DeepSeek-V4.1-Flash，硬件覆盖 NVIDIA SM100 GPU 和华为 Ascend 950 NPU，采用 Apache License 2.0。对自建推理服务的团队，这是一份难得的生产级一手参考实现；HN 上获得 2022 分。

来源：[GitHub](https://github.com/deepseek-ai/DeepInfer) · [HN 讨论](https://news.ycombinator.com/item?id=50163277)　`开源` `推理`

### Google 开源 TorchTPU：TPU 成为 PyTorch 原生设备

TorchTPU 是新的 PyTorch 后端，让 TPU 像普通设备一样使用，自带针对 TPU 调优的 Pallas 内核、分布式训练支持和 torch.compile 集成。Hugging Face 同步支持，在 TPU VM 上安装后，加载模型时传入 device_map="tpu" 即可。对已有 PyTorch 代码的团队，迁移到 TPU 的成本明显降低。

来源：[Hugging Face Blog](https://huggingface.co/blog/hf-torchtpu) · [GitHub](https://github.com/google-pytorch/torch_tpu)　`开源` `硬件` `训练`

### Anthropic：Claude 主导设计出可结合蝎毒素的蛋白

Anthropic 让内部研究版 Claude 针对蝎子神经毒素设计微型结合蛋白，Claude 生成了 318,484 个设计并选出 180 个送测；在评估的 211 个设计中，有 17 个达到结合标准。作者强调尚未确认它们能在细胞环境中中和蝎毒，也不声称做出了抗毒血清。这是模型较为自主地承担科研设计工作的一个具体案例。

来源：[Anthropic Research](https://www.anthropic.com/research/claude-scorpion-toxin-binder-design) · [HN 讨论](https://news.ycombinator.com/item?id=50170021)　`研究` `Agent`

## 🧠 模型

### DeepSeek-V4.1-Flash-1017 更新权重

DeepSeek-V4.1-Flash 的小版本更新，763B 参数，支持图文输入，推荐上下文 1M tokens，MIT 许可开放权重。官方称推理、编程、Agent 和视觉基准都有明显提升（厂商自测）。目前位列 HF 趋势榜第 1。

来源：[Hugging Face Trending Models](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)　`模型` `开源`

### Black Forest Labs 开放 FLUX 3 Image Klein 权重

FLUX 3 Image Klein 是 5.6B 参数的开放权重模型，支持文生图和图像编辑，另有 Base 版和 ComfyUI 版本。官方要求必须配合 prompt upsampler 使用。许可为 FLUX Kommunity License，只允许非商业使用以及符合条件用户的商业出图，商用前要看清条款。

来源：[black-forest-labs/flux-3-image-klein](https://huggingface.co/black-forest-labs/flux-3-image-klein) · [black-forest-labs/flux-3-image-klein-base](https://huggingface.co/black-forest-labs/flux-3-image-klein-base) · [black-forest-labs/flux-3-image-klein-comfy](https://huggingface.co/black-forest-labs/flux-3-image-klein-comfy)　`模型` `图像`

### Liquid AI 发布端侧推理模型 LFM2.5-24B-A2B

面向本地 Agent 的 MoE 推理模型，总参数 24.0B、激活 2.45B，上下文 131,072 tokens。官方称在 Apple M5 Max 上可达 184 tok/s，Agent 任务上与 Qwen3.6-35B-A3B 相当，但部分基准仍落后（厂商自测）。许可为 lfm1.0，需要在端侧跑 Agent 时值得一试。

来源：[Hugging Face Trending Models](https://huggingface.co/LiquidAI/LFM2.5-24B-A2B)　`模型` `Agent` `推理`

## 📄 论文

### Self-HPO：让编程 Agent 交替优化 harness 和模型

论文提出 Self-HPO，交替进行 harness（Agent 脚手架）优化和强化学习策略训练，由模型根据自己的失败案例提出新的 harness。在编程基准上，Qwen3.5-35B-A3B 的平均解决率从 57.8% 提升到 64.8%，并能泛化到分布外场景。启示是调 Agent 时 harness 和模型应一起迭代。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.22791)　`论文` `代码` `Agent`

### OR-License：用真实咨询项目评测 Agent 的运筹优化能力

OR-License 基于付费工业咨询项目构建，包含 10 个工业场景中的 31 个实例，要求 Agent 从客户的原始材料出发交付可执行的运筹优化方案。表现最好的 Claude Code 配置达到 88.39% 的严格可行率，但没有模型在整体得分上追上专家。它比自包含题目更接近真实交付场景。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.24087)　`论文` `Agent`

## 🛠 开源与工具

### PyTorch 2.15 大幅提速 Apple Silicon 上的模型推理

PyTorch 2.15 的 MPS 后端加入 FP8，MoE 模型解码比 2.14 快 5–6.5 倍，Qwen3.6-35B-A3B 在 M3 Ultra 上从 9.4 提升到 61.3 tokens/s，词表 softmax 约快 8 倍。在 Mac 上本地跑模型的开发者升级即可受益。

来源：[Hugging Face Blog](https://huggingface.co/blog/mps-pytorch-2-15)　`工具` `推理` `硬件`

### Claude Code v2.1.304 / v2.1.305 发布

v2.1.305 新增 sandbox.allowNestedUserNamespaces，让 Linux 沙箱内的命令可以创建 user namespace（如 Chromium、rootless podman），官方提示这会让它们绕过沙箱的文件保护；同时修复了 Vertex、Bedrock 等提供方在网关拒绝 tool search 时所有请求失败的问题。v2.1.304 新增引导式配置命令 /auto-mode-setup。

来源：[anthropics/claude-code v2.1.305](https://github.com/anthropics/claude-code/releases/tag/v2.1.305) · [anthropics/claude-code v2.1.304](https://github.com/anthropics/claude-code/releases/tag/v2.1.304)　`工具` `代码`

## ⚡ 快讯

- **OpenAI 宣布收购 Orchestra Bio** OpenAI 将收购 Orchestra Bio，把 AI 驱动的运营能力带入生命科学研发，帮助药企加速药物开发。 [OpenAI News](https://openai.com/index/openai-to-acquire-orchestra-bio)
