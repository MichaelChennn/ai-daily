# 2026-11-08 · AI 科技日报

## 今日要点

- llama.cpp 合并 PR #30966：MoE 缓存未命中的专家可以在 CPU 上执行，还附带自动调参脚本，低显存跑 MoE 的用户可以直接用上。
- Nous Research 发布基于 Qwen3.8-27B 后训练的 Arete-27B；Ai2 开源机器人仿真框架 ToyBlocks。
- 论文方面，D3D 和 DSpine 两篇投机解码工作都以 DFlash 为基线报告了更好的结果。

## 🔥 头条

### llama.cpp 合并 MoE 缓存改进：未命中的专家可在 CPU 上计算

llama.cpp 合并了 PR #30966：按 --moe-cache-cpu-share 设定的比例，MoE 专家缓存未命中时直接在 CPU 上执行这些专家；同时新增 scripts/moe-cache-tune.py，在 llama-server 命令前加上它即可搜索 --moe-cache-mib 和 CPU 份额的最佳组合。一位维护者在 R9700 + 内存、Qwen 3.8 Next IQ3_XXS 的配置上测得约 10% 的解码提升。显存不够、靠专家卸载跑 MoE 模型的本地用户可以直接拿脚本调参。

来源：[GitHub](https://github.com/ggml-org/llama.cpp/pull/30966) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xqacka/llama_moe_cache_run_missed_experts_on_cpu_add/)　`开源` `推理` `工具`

### Nous Research 发布 Arete-27B：对 Qwen3.8-27B 做价值观后训练

Nous Research 以 Qwen3.8-27B 为基础，只用监督微调（没有 RL、偏好优化或架构改动）训练出 Arete-27B，目标是改变模型在政治敏感话题上的立场。在其 803 条提示的评测上，事实分从 2.32 升到 2.98（满分 5），含宣传口径的回答从 22% 降到 0.9%；Hermes Bench 上与基座相差不到 0.2 个百分点。权重采用 apache-2.0 许可，评测提示也已全部公开，可以用来研究后训练如何改变模型的价值取向。

来源：[Hugging Face Trending Models](https://huggingface.co/NousResearch/Arete-27B)　`模型` `开源` `训练`

### Ai2 开源机器人学习仿真框架 ToyBlocks

ToyBlocks 是 Ai2 推出的开放仿真框架，场景是桌面上的机械臂和积木，能自动生成技能和任务示范，不需要耗时的遥操作；在单块 GPU 上并行执行数百个规划，最高达到 24 倍实时速度。首批数据包含 85,336 条长程示范，并用 Molmo 2 做高层规划、ManiFlow 做底层控制训练了分层模型。做 VLA 和具身智能的团队可以用它低成本生成训练数据，并在受控环境里比较方法。

来源：[Ai2](https://allenai.org/blog/toyblocks)　`开源` `训练` `工具`

## 🧠 模型

### 百度发布 Unlimited-OCR-2，主打超长文档解析

Unlimited-OCR-2 以 MIT 许可开放权重，核心是 SR-SWA（Sparse Reference Sliding Window Attention），把超长序列的图文注意力压缩到固定大小的参考集合，使每步解码的延迟和显存几乎不随文档长度增长。百度称它在几十页的 MPDocBench 和上百页的 MarathonDocBench 上都达到 SOTA，并同时发布了 MarathonDocBench。支持 Transformers 和 SGLang，适合需要整本解析长 PDF 的文档处理和 RAG 管线。

来源：[Hugging Face Trending Models](https://huggingface.co/baidu/Unlimited-OCR-2)　`模型` `多模态` `开源`

### Kakao 发布决策模型 Kanana-2-v-decide-3b-2611

这个模型不生成文本，而是回答类型化问题：多选、是/否或有序打分，并为每个可能的答案返回概率；输入可以是文本、JSON 或对话，最多附带 10 张图片、20,480 个 token。它基于 Kanana-2-v-3b，共 3.67B 参数，权重采用 KananaOpenLicense。适合放在 agent 或业务流程里做分类、判断这类需要概率输出的决策环节。

来源：[Hugging Face](https://huggingface.co/kakaocorp/kanana-2-v-decide-3b-2611) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xq6es4/kakaocorpkanana2vdecide3b2611_hugging_face/)　`模型` `多模态`

## 📄 论文

### D3D：独立的扩散草稿模型，让投机解码异步进行

D3D 是一个不需要目标模型隐藏状态的扩散草稿模型，结合分块去噪和辅助自回归监督，因此能在验证期间就起草后续的块，实现异步投机解码。在七个基准上，以 Qwen3-8B 和 Qwen3-32B 为目标模型时平均加速 5.00× 和 5.71×，DFlash 为 4.03× 和 3.67×；代码已公开。做推理服务的开发者可以关注这种起草与验证不再串行的方案。

来源：[arXiv](https://arxiv.org/abs/2611.06425) · [Reddit 讨论](https://www.reddit.com/gallery/1xq1y0y)　`论文` `推理`

### DSpine：在骨干每一层注入因果条件的投机解码草稿模型

并行起草时各位置独立选词，容易产生不一致的续写、缩短被接受的前缀；DSpine 在骨干的每一层把前一位置的预测特征写入后一位置，让因果条件链沿网络深度展开，同时所有位置仍并行更新。在 Qwen3-8B、温度为 0 时，七个基准的平均接受长度从 DFlash 的 3.77 提升到 4.82（+27.8%）；在 SGLang 服务测试中吞吐量平均比 DFlash 高 23.3%。

来源：[arXiv](https://arxiv.org/abs/2609.36173) · [Reddit 讨论](https://www.reddit.com/gallery/1xq9hf6)　`论文` `推理`

### CoworkOS：面向长周期工作的通用 agent harness

CoworkOS 把任务策略和执行管理分开：模型决定行动、委派和验收，运行时负责维护状态和反馈。论文称它在 12 个基准上与 Codex、DeepSeek Harness 等前沿 agent 应用相比很有竞争力；在用 GLM-5.3 作主干、对 Qwen3.6-35B-A3B 做五轮自动后训练的案例中，八个基准的平均分从 33.19 升到 42.95。代码在 GitHub 上，可以作为自建长任务 agent 的参考架构。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.03178)　`论文` `Agent`

### Wave Forcing：多个视频块同时去噪的流式视频生成

Wave Forcing 对生成、训练和执行做协同设计：用分块因果注意力让每个块在去噪完成前就能读取更早、更干净的块，多个块同时处于不同的去噪阶段。在 Wan2.1-T2V-1.3B 上，5 步版本整体质量与 Rolling Forcing 相当；4 步版本在 8×H200 上达到 134.8 的端到端 FPS，是单 GPU 端到端吞吐的 7.07 倍。做实时或长视频生成的团队可以参考它的并行执行思路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.00859)　`论文` `视频`

## 🛠 开源与工具

### Meta 开源设计系统 Astryx，为人和 AI 助手共用而设计

Astryx 在 Meta 内部发展了八年，支撑 13,000+ 个应用，现以 MIT 许可开源：提供 150+ 个无障碍组件、品牌级主题、暗色模式、现成模板和 CLI，基于 React 19+ 和 StyleX。它的 API、文档和 CLI 是一起设计的，让人和 AI 助手按同一份参考来构建。用 coding agent 写 React 前端的团队可以试试。

来源：[GitHub Trending](https://github.com/meta/astryx)　`开源` `工具` `代码`

### NVIDIA 开源 NVKE 预览版：在自有 GPU 机器上运营 Kubernetes 服务

NVKE 是一个管理平面，用来在自有 NVIDIA GPU 基础设施上提供托管 Kubernetes 服务：平台团队用它创建和运营多个工作负载集群，客户通过 Kubernetes API 和 kubectl 使用。项目采用 Apache License 2.0，目前是预览版，官方不建议用于生产。自建 GPU 集群服务的平台团队可以先评估。

来源：[GitHub Trending](https://github.com/dsx-ai-factory/nvke)　`开源` `工具` `硬件`
