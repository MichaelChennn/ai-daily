# 2026-10-26 · AI 科技日报

## 今日要点

- Nanbeige 开源 33B 教师模型 Nanbeige4.3-33B，Apache 2.0 许可，自测 Terminal-Bench 2.1 得分 80.9。
- 皮肤科医生实测：微调的 Inception v3 在 200 个活检病灶上首选诊断正确率 62%，GPT-6 Astra 和 Claude Fable 5.1 均为 42%。
- llama.cpp 合入两项性能优化：CUDA 后端的 prompt 处理和 Qwen 模型推理都有提速。

## 🔥 头条

### Nanbeige 开源 33B 教师模型 Nanbeige4.3-33B

Nanbeige 发布 Nanbeige4.3-33B，定位为 Nanbeige4.3 系列的旗舰教师模型，后续用它把 Agent 能力蒸馏到更小的模型；权重采用 Apache 2.0 许可，上下文最长 512K。团队自测 Terminal-Bench 2.1 得分 80.9（Qwen3.8-27B 为 73.0），但 SWE-Bench Pro 上 60.3 略低于后者的 61.7。模型卡建议多轮工具调用和代码 Agent 场景开启 preserve_thinking、普通对话关闭，想在本地跑编程 Agent 的开发者可以一试。

来源：[Hugging Face Trending Models](https://huggingface.co/Nanbeige/Nanbeige4.3-33B) · [Nanbeige releases Nanbeige4.3-33B, an Apache 2.0 teacher model for smaller agents [N]](https://www.reddit.com/r/MachineLearning/comments/1xf6x35/nanbeige_releases_nanbeige4333b_an_apache_20/) · [Hugging Face](https://huggingface.co/AtomicChat/Nanbeige4.3-33B-GGUF) · [Nanbeige/Nanbeige4.3-33B](https://www.reddit.com/r/LocalLLaMA/comments/1xf0kz4/nanbeigenanbeige4333b_hugging_face/)　`模型` `开源` `Agent`

### 皮肤科医生实测：十年前的 CNN 识别皮肤癌胜过前沿大模型

Guy's Hospital 皮肤科医生 Magnus Lynch 用 MILK10k 中 200 个经活检确诊的病灶做测试，微调后的 Inception v3 首选诊断正确 125 例（62%），GPT-6 Astra 和 Claude Fable 5.1 分别为 84 和 85 例（42%）。作者也指出样本量小、每个 LLM 病例只跑了一次、数据集公开可能已被模型训练见过。对做医疗 AI 的开发者来说，这提醒在窄领域视觉任务上专用小模型仍可能胜过通用大模型，选型前值得先做针对性评测。

来源：[lynchlab.net](https://lynchlab.net/llm-skin-cancer) · [HN 讨论](https://news.ycombinator.com/item?id=50233779)　`多模态` `图像` `行业`

## 🧠 模型

### MemTensor 开源记忆原生模型 MemT-1.0-Nano

MemT-1.0-Nano 基于 Qwen3.6-35B-A3B，把动态局部记忆和可训练的超记忆融入模型计算，推理时无需访问原始上下文就能利用历史信息；在 128K 历史长度下，存储比全上下文 KV cache 减少约 66 倍。权重采用 Apache License 2.0，模型卡提供了保存和恢复记忆状态的 Transformers 示例，适合想给 Agent 加长期记忆、又不想一直堆上下文的开发者研究。

来源：[Hugging Face Trending Models](https://huggingface.co/MemTensor/MemT-1.0-Nano) · [Reddit 讨论](https://www.reddit.com/r/MachineLearning/comments/1xeu0ht/memt10_architecture_breakdown_gated_deltanet2/)　`模型` `开源` `Agent`

## 📄 论文

### Gandalf：按注意力类型筛选 KV cache 写入，延长 SSD 寿命

论文指出，在多轮对话和 Agent 等生产负载中，卸载到 SSD 的 KV cache 写入量远超 SSD 容量，会把 SSD 寿命从数年缩短到数月。Gandalf 优先把全注意力（full attention）产生的 KV cache 写入 SSD，评测显示 SSD 寿命平均延长 7.3 倍，对缓存命中率的影响可以忽略。对用 SSD 扩展 KV cache 的推理服务和本地部署来说，这是控制硬件损耗的一个思路。

来源：[Gandalf: Flash Shall Not Die! Increasing Flash Storage Lifetime for KV Cache Offloading in LLM Serving](https://arxiv.org/html/2610.30791v1) · [arXiv](https://arxiv.org/abs/2610.30791) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xfiu75/gandalf_flash_shall_not_die_increasing_flash/)　`论文` `推理` `硬件`

## 🛠 开源与工具

### llama.cpp CUDA 后端把 gate/up 与 GLU 融合扩展到 prompt 处理

llama.cpp 合入 PR #29948，把原本只覆盖小批量的 FFN gate/up 矩阵乘与 GLU 融合扩展到 MMQ 路径的 prompt 处理批量，支持 NVIDIA Turing 及更新架构上的 Q4_K、Q5_K、Q6_K、Q8_0、IQ4_XS。作者在 DGX Spark (GB10) 上测得 Qwen3.8-27B Q4_K_M 的 prompt 处理速度 +7.1%，困惑度与关闭融合时逐位一致。用 CUDA 跑量化模型、经常处理长 prompt 的用户更新后即可受益。

来源：[GitHub](https://github.com/ggml-org/llama.cpp/pull/29948) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xey0uw/cuda_fuse_ffn_gateup_matmuls_and_glu_in_mmq_with/)　`开源` `推理` `工具`

## ⚡ 快讯

- **llama.cpp 转换 Qwen 模型时合并共享激活的小张量** llama.cpp 合入 PR #31028，转换时把 Qwen 计算图中共享同一激活的权重合并，作者实测新 GGUF 生成速度 +7%、预填充 +5%。 [GitHub](https://github.com/ggml-org/llama.cpp/pull/31028) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xf716t/qwen_merge_tensors_on_convert_by_am17an_pull/)
- **llama.cpp 披露 CVE-2026-116096：恶意 mmproj 可致越界写** 漏洞位于 Pocket-TTS 组件，恶意 mmproj 会触发越界写，需本地访问；披露建议升级到 b11796，从设计上防止越界的 PR 29360 仍未合入。 [llama.cpp PR #29360](https://github.com/ggml-org/llama.cpp/pull/29360) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xfizft/psa_llamacpp_cve2026116096/)
- **minimaxir 分析 OpenAI 与 Anthropic 为何连续降价** 文章梳理两家数月内最高 80% 的降价，认为模型切换成本低、缺乏护城河，开源权重模型等替代品带来了价格压力。 [minimaxir.com](https://minimaxir.com/2026/10/cheap-llms/) · [HN 讨论](https://news.ycombinator.com/item?id=50236102)
