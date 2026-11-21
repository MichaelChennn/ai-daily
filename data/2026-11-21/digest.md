# 2026-11-21 · AI 晨报

## 今日要点

- Thinking Machines 以 Apache 2.0 开放 Inkling 2 Mini 权重：26.4B 总参数、3.4B 激活，约 20GB 的检查点可以在本地运行。
- OpenAI 公布对抗性蒸馏防护，推理提取的平均攻击成功率从 54.0% 降到 0.2%；Hugging Face 用 RL 给 Qwen3.8-27B 训练 harness 适配器，pi 下 Terminal-Bench 2.1 从 39% 升到 55%。
- Signal 开始阻止 iOS 27 和 Android 上的系统级 AI 读取聊天屏幕。

## 🔥 头条

### Thinking Machines 开放 Inkling 2 Mini 权重：26.4B 总参数、3.4B 激活

Inkling 2 Mini 是 Thinking Machines Lab 的多模态 MoE 模型，用循环 Transformer 结构：部分层循环三遍以增加容量，模型卡给出 26.4B 总参数、3.4B 激活，支持 1M token 上下文和图文输入，许可证为 Apache 2.0。检查点约 20GB（NVFP4 与 MXFP8 混合精度），官方支持单台 DGX Spark 和 32GB 以上内存的 Apple silicon 设备，llama.cpp 侧提供 IQ4_NL 和 Q8_0 的 GGUF。想在本地跑长上下文多模态模型的开发者今天就能下载试用。

来源：[Hugging Face Blog](https://huggingface.co/blog/inkling2mini) · [Hugging Face Trending Models](https://huggingface.co/thinkingmachines/Inkling-2-Mini)　`模型` `开源` `多模态`

### OpenAI 公布对抗性蒸馏防护：推理提取成功率降到 0.2%

OpenAI 介绍了防范对抗性蒸馏的做法：结合对抗测试、模型训练、分类器和 API 层防护，并调查有组织的提取活动；API 会把 GPT‑6.2 Astra 和 Sol 的受保护推理绑定到产生它的对话历史，改写前面的消息就会丢弃其后的推理。在自动化红队测试中，提取早先请求推理的平均攻击成功率从 GPT‑6 Astra 原有防护下的 54.0% 降到 GPT‑6.2 Astra 的 0.2%。会改写对话历史的 API 应用要留意推理被丢弃带来的行为变化；OpenAI 还称一次提取活动的核心部分与 Moonshot AI 相关人员有关。

来源：[OpenAI News](https://openai.com/index/combatting-adversarial-distillation)　`安全` `模型` `行业`

### MiniMax 用内部模型 MIM 做自动密码分析，攻破多个 NIST 候选方案

MiniMax 研究团队用内部研究模型 MIM 对现代密码方案做自动化密码分析，例如为 NIST SHA-3 候选 Waterfall-256 构造出首个实际可行的碰撞攻击，并在 TII McEliece 挑战中恢复了 94 个实例的密钥，其中 55 个此前未被解出。MiniMax 称这些工作针对学术设计、往届竞赛候选和公开挑战参数，不影响已部署的密码标准，结果已提前告知方案作者。MIM 不公开发布，做密码实现审计的研究者和开发者可以申请测试权限。

来源：[MiniMax Blog](https://www.minimax.io/blog/practical-cryptanalysis-with-minimaxs-latest-internal-model)　`安全` `模型`

### Architect Labs 发布由 AI 设计的新指令集 CPU Frostbite

Architect Labs 推出 Frostbite：一款从零设计新指令集的通用 CPU，基于交互网（interaction nets），其 AI 系统自主迭代了编译器、ISA、架构、微架构、RTL、验证直到最终 GDS。在 7 nm 工艺上，一个 Frostbite quad 加四个 L3 节点面积 0.792 mm²，对比一款未公开型号的传统 CPU（TCPU），平均每面积性能 8.77x，25 个负载上每瓦性能几何平均 4.59x。对比对象未公开，RTL 和 ISA 也还没发布（列在后续计划里），这些自报数字暂时无法独立核对，但它是 AI 系统参与芯片全流程设计的一个具体案例。

来源：[architectlabs.com](https://architectlabs.com/blog/frostbite) · [HN 讨论](https://news.ycombinator.com/item?id=50572503)　`硬件` `Agent`

### Signal 阻止 iOS 27 和 Android 的系统级 AI 读取聊天屏幕

Signal 宣布在 iOS 27 上禁止应用内截屏，在能检测到 AI 助手读取屏幕的 Android 版本上自动开启 “Screen security”，以阻止系统内置的 Agent 捕获聊天内容，做法和此前在 Windows 11 上屏蔽 Microsoft Recall 类似；用户可以在设置里关闭这项保护。Signal 同时呼吁平台方给开发者一个简单、有文档的方式，让应用退出 AI 数据访问和处理。做隐私敏感应用的移动开发者，需要开始考虑系统级 Agent 读屏的问题。

来源：[signal.org](https://signal.org/blog/protecting-your-privacy/) · [HN 讨论](https://news.ycombinator.com/item?id=50572348)　`安全` `Agent` `产品`

## 🧠 模型

### 腾讯开源全模态视频理解模型 WeMM-Video

WeMM-Video 是中英双语全模态模型家族，有 2B、4B、9B 和 35B-A3B 四个规格，统一处理文本、图像、音频和视频，支持非思考和思考两种模式，训练语料约 1.2 trillion tokens。论文称旗舰 WeMM-Video-35B-A3B 在全模态视频评测上达到开源模型中的最好水平，WeMM-Video-9B 超过更大的 Qwen3-Omni-30B-A3B-Instruct，模型和评测、复现流程一并公开。需要同时理解视频画面和音频的应用可以拿来试。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26409)　`模型` `开源` `多模态`

## 📄 论文

### 论文：扩散 Transformer 的 RL 后训练，多半只是固定的激活偏移

作者在冻结的基础模型各 block 输出上加一组对所有提示、token 和随机种子都相同的 steering vector，只拟合 RL 调优模型的速度预测、目标里不含奖励，就找回了六个 RL 调优图像模型 90.0-96.3% 的奖励提升；在 SD3.5-M 上参数比 RL 调优的 LoRA 少 65x。从零开始用在线 RL 训练这些向量，在文字渲染（OCR）和 PickScore 上甚至超过基于权重的 RL。给扩散模型做 RL 对齐时，可以先试成本低得多的激活引导。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26627)　`论文` `训练` `图像`

### LightningMoBA：MoBA 稀疏注意力端到端提速 1.20 到 1.60x

LightningMoBA 把 Mixture of Block Attention 的块选择和执行放在一起设计：用阈值动态路由替代固定 Top-k，按 KV 块组织任务以复用已加载的 KV，并在 Hopper 上让数据搬运与 Tensor Core 计算重叠。在五个 checkpoint 上、相同的 Top-16 保留率下，端到端生成提速 1.20 到 1.60x，平均 RULER 分从 74.42 升到 75.28。做长上下文推理优化的团队可以参考，代码在 GitHub 上。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26268)　`论文` `推理`

### AutoMaster：让 LLM Agent 自己设计后训练的教师干预

AutoMaster 是一个自主后训练系统：LLM Agent 分析轨迹、设计自然语言技能（Skill-FT），在教师采样时抑制不良习惯、引出缺少的有效行为，再筛选数据微调目标模型。在 Terminal、Search 和 SWE 类基准上用 4B 和 9B 模型测试，在教师、任务池、训练集规模和 SFT 配方都不变的情况下，比普通 SFT 高 1.42–8.99 个百分点。做 Agent 蒸馏的团队可以借鉴：用技能提示改善示范轨迹，而不只按任务成功筛数据。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.26510)　`论文` `Agent` `训练`

## 🛠 开源与工具

### Hugging Face 推出 harness adapters：为每个 Agent 框架训练专属 LoRA

Hugging Face 为 Qwen3.8-27B 在 pi、Hermes Agent、OpenCode 三个 harness 里分别用 RL 训练 LoRA 适配器，再合并成一个三者通用的 super adapter，适配器、GGUF、RL 任务和完整配方都在 Hub 上公开。在 pi 下，Terminal-Bench 2.1 从 39% 升到 55% pass@1，平均每个任务的 token 从 2.9K 降到 1.5K；SWE-bench Pro（hard 51）上 pi 从 39.2% 升到 64.7%。用开源模型跑编码 Agent 的团队，可以照这套配方给自己的 harness 训练适配器，同时提分和省 token。

来源：[Hugging Face Blog](https://huggingface.co/blog/harness-adapters-at-scale) · [harness-hub/Qwen3.8-27B-pi-adapted](https://huggingface.co/harness-hub/Qwen3.8-27B-pi-adapted) · [harness-hub/Qwen3.8-27B-opencode-adapted](https://huggingface.co/harness-hub/Qwen3.8-27B-opencode-adapted)　`工具` `Agent` `训练`

### Claude Code v2.1.330：支持企业组织登录，新增画图 mod easel

Claude Code v2.1.330 支持登录由 Anthropic Enterprise Admin Console 管理的组织，claude auth login 之后会应用组织设置，并使用组织的云服务商或网关；新增内置 mod easel，按需画图表，也会在 MCP 指标结果下自动画图，可在 /config 关闭自动图表。自托管 runner 新增 --start-dir，可以让 Claude 从仓库里的某个子目录开始工作。用企业管理后台或自建 runner 的团队值得升级。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.330)　`工具` `代码` `Agent`

## ⚡ 快讯

- **OpenAI 发布药物化学基准 MedChemBench** MedChemBench 含 99 道取自已发表研究的题目，xhigh 推理设置下 GPT‑6.2 Astra 拿到 84.5% 的分数，GPT‑5.6 Sol 为 58.2%。 [OpenAI News](https://openai.com/index/introducing-medchembench)
- **Google 把 Duplex 接入 Tasks in Gemini，替用户给商家打电话** Gemini App 的 Tasks in Gemini 现在可以用 Duplex 给商家打电话预约、办事，每通电话开头都会说明是 AI，商家可以选择退出。 [Google Research](https://research.google/blog/how-google-duplex-evolved-to-also-call-businesses-for-you-in-gemini/)
- **开发者让编码 Agent 在 AWS F2 FPGA 上跑通三值权重 LLM** 作者用 Codex 等编码 Agent 在 AWS F2 FPGA 上实现三值权重 LLM 推理，吞吐达 213.13 tok/s（基线的 33.13×），约 $10,000 token 花费，比价格相近的 CPU 实例快 1.65×。 [ankitg.me](https://ankitg.me/blog/vibecoding-inference-chip/) · [HN 讨论](https://news.ycombinator.com/item?id=50579297)
