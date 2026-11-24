# 2026-11-24 · AI 晨报

## 今日要点

- Anthropic 推出 Claude Ship beta，由 Code Review、PR Steward 和 Claude Approvals 接手 PR 的审查、修复和按策略批准。
- OpenAI 与 Cisco 开源 Shirudo，用 eBPF shield 在补丁就绪前保护运行中的 Linux 服务。
- Google DeepMind 用 Gemini 4 agent 团队加 Lean 形式化验证改进量子算法，并开源了 Lean 库。

## 🔥 头条

### Anthropic 推出 Claude Ship：agent 审 PR、修 PR、按策略批准

Claude Ship 今天以 beta 上线，由已正式可用的 Code Review 和两个新 agent 组成：PR Steward 处理失败的 CI、合并冲突和评审意见，但不会批准或合并 PR；Claude Approvals 按团队写在仓库里的策略文件，决定哪些常规改动可以自动批准、哪些必须有人签字。开发者可以在 Claude Code 里用新的 /ship 命令推送改动、开 PR 并跟进到可合并；团队也可以按仓库开启，官方建议先在 observe-only 模式下试运行，再接入分支保护。

来源：[Claude Blog](https://claude.com/resources/articles/introducing-claude-ship)　`Agent` `代码` `产品`

### OpenAI 与 Cisco 开源 Shirudo：用 eBPF 给运行中的 Linux 加临时护盾

Shirudo 是 OpenAI 和 Cisco 推出的开源运行时，用 eBPF 在系统运行时加载临时防护（shield），拦住漏洞的利用路径，补丁就绪前不必重启服务；shield 加载前要通过签名校验，并借助 TPM 留下加载和移除的可验证记录。在受控测试中，Codex 生成的 shield 拦下了针对运行中 Elasticsearch 服务的 Java4Shell 攻击。项目采用 BSD 2-Clause 许可，给安全和运维团队提供了一个让 agent 起草防护、由人审批部署的开源方案。

来源：[OpenAI News](https://openai.com/index/introducing-shirudo)　`安全` `开源` `Agent`

### DeepMind 用 Gemini 4 agent 团队加 Lean 证明改进量子算法

Google DeepMind 让多支独立的 Gemini 4 agent 团队分头改进已知量子算法，每个想法都先用 Lean 形式化验证，再进入共享笔记本。结果包括：惯性约束聚变相关电路的计算成本降低 11.8×，所需纠错量子比特从 5,650 降到 4,338；Cytochrome P450 模拟提升 2.5×；arcsin 例程加速 290x。DeepMind 开源了 Lean 库、问题定义和已验证的解，“agent 搜索 + 形式化验证”的做法对想让 agent 产出可信研究结果的团队有参考价值。

来源：[Google DeepMind Blog](https://deepmind.google/blog/finding-faster-quantum-algorithms-with-agents-and-formal-verification/)　`Agent` `推理` `开源`

## 🧠 模型

### inclusionAI 开放 Ling-3.2-air：124B 总参数、激活 5.5B

Ling-3.2-air 是 inclusionAI 的开放权重模型，沿用 Ling-3.0-flash-VL 的原生多模态架构，采用 Hybrid-linear MoE，总参数 124B、每 token 激活 5.5B，MIT 许可。相比前代，它在工作流自动化和专业文档推理上明显变强：AutomationBench-AA 从 15.7% 升到 61%，Terminal-Bench 4.0 通过率从 0% 升到 27%。官方推荐用 SGLang 部署，256K 上下文的参考配置是 4 张 141GB 级 GPU。

来源：[Hugging Face Trending Models](https://huggingface.co/inclusionAI/Ling-3.2-air)　`模型` `开源` `多模态`

### Thinking Machines 开放可变循环研究模型 TML-d24-varloop-research

它是 Inkling 2 Mini 的可变循环版本：24 层里中间的 12 层共享权重，循环次数在推理时选，训练时用了 1 到 5 遍；总参数 26.4B，激活 3.4B，每多一遍约增加 1.0B 有效激活参数。权重约 20GB，原生 NVFP4 和 MXFP8 精度，一台有 32GB 显存或统一内存的机器就能跑，Apache 2.0 许可，只提供开放权重、不上 API。同一套权重可以改循环次数，适合研究额外的循环计算如何影响模型能力。

来源：[Hugging Face Trending Models](https://huggingface.co/thinkingmachines/TML-d24-varloop-research)　`模型` `开源` `推理`

## 📄 论文

### MemOnce：1M 上下文下把记忆缓存缩小 1313 倍

MemOnce 只把一小部分末层隐状态缓存为紧凑的记忆表示，需要时再解码回各注意力层的 KV cache，并用只计算一次、跨层共享的稀疏索引检索相关记忆，从而做到线性时间复杂度。用 MemOnce 改造 Qwen3.5-4B 后，在 1M 上下文下记忆状态缓存缩小 1313 倍、prefill 延迟降低 6.9 倍，吞吐提升 3.5 倍。对做长程 agent 和持续对话的开发者，这是一条在已有模型上通过后训练适配压缩 KV cache 的路线。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.27973) · [arXiv](https://arxiv.org/abs/2611.27973)　`论文` `推理`

### NoPeWorld：读 DiT 隐状态，防止视频世界模型“穿模”

论文提出 NoPeBench，发现现有开源交互式视频世界模型都无法可靠避免物体穿过障碍物，但扩散 Transformer（DiT）的隐状态其实已经能预测某个动作会不会穿模。NoPeWorld 在冻结的 DiT 上训练一个小预测头，把不安全的动作换成最接近原意的安全动作，在六个视频世界模型上把平均物理违规率从 74% 降到 16%。代码、基准和权重都会公开，做世界模型或具身仿真的团队可以把它当作轻量的物理约束补丁。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.27963) · [arXiv](https://arxiv.org/abs/2611.27963)　`论文` `视频`

### Duopra：让全双工语音模型边对话边调用工具

全双工模型擅长接话、附和和打断，但完成任务还要及时调用工具、在用户纠正后修改参数；论文发现在 Full-Duplex-Bench v3 上，Realtime-Venus-Audio + Harness 的多数失败发生在领域工具执行之前。Duopra 把后端当作接收自然语言请求的工具，经过协议 SFT、奖励及时完整执行的全双工 RL 等三阶段训练，在同一后端下 Pass@1 从 4.7% 升到 44.7%。对做实时语音 agent 的开发者，这说明对话控制和任务执行可以放进同一个模型。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.25773) · [arXiv](https://arxiv.org/abs/2611.25773)　`论文` `语音` `Agent`

### cmHC：用几何收缩平衡超连接的残差流混合

流形约束超连接（mHC）把残差流的混合矩阵限制在 Birkhoff 多面体内，论文指出混合不足会让多条流退化成近乎独立，混合过度又会让流难以区分。cmHC 把多面体向内部几何收缩，不引入新的参数化，并在浅层用适度收缩防止过度混合，让超大规模预训练的梯度传播保持稳定；作者还在 Ascend NPU 上实现了融合算子，超连接执行延迟最多降低 44.8%。对在训练栈里尝试多流残差连接的团队，这提供了一个带可证明混合界的调节方法。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.27193) · [arXiv](https://arxiv.org/abs/2611.27193)　`论文` `训练`

## 🛠 开源与工具

### Ai2 发布 RoboTrack：机器人操作点追踪的基准、数据和模型

RoboTrack-Bench 收录 307 段人工标注的真实操作视频，主流追踪器在它上面的得分明显低于现有机器人基准；配套的 RoboTrack-15M 是用 MolmoSpaces 仿真生成的合成训练集。Ai2 同时放出 RoboTracker 和 RoboTracker-Warp 两个点追踪模型，在湿实验室移液任务中，点追踪在 20 次试验里完成 17 次，物体掩码只有 8 次。用现成追踪器给机器人视频自动标注的团队，可以先拿这个基准检验效果。

来源：[Ai2](https://allenai.org/blog/robotrack) · [Hugging Face Blog](https://huggingface.co/blog/allenai/robotrack)　`开源` `多模态` `工具`

## ⚡ 快讯

- **Anthropic 企业安全监测 EFS 进入公开 beta，兼容零数据保留** EFS 在客户自己控制的存储上做跨请求的滥用检测，Anthropic 和云厂商都不保留数据，支持 Claude Platform、Amazon Bedrock、Claude on Google Cloud 等平台。 [Claude Blog](https://claude.com/resources/articles/zero-data-retention-with-enterprise-frontier-safeguards)
- **Anthropic 访谈 58 家企业：AI 很少带来裁员，但减少了招聘** 三分之二的受访公司表示因 AI 减少了招聘，价值最高的用法往往是围绕 AI 重组岗位和工作方式。 [Anthropic Research](https://www.anthropic.com/research/working-with-ai)
- **Hugging Face 发布 agentic 评测的构建与维护指南** 指南建议从现有任务改起、按保存的输出或最终环境状态打分、逐条读 trace，并同时报告 pass@k 和 pass^k。 [Hugging Face Blog](https://huggingface.co/blog/agentic-evals)
