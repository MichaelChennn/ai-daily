# 2026-10-31 · AI 科技日报

## 今日要点

- Cursor Marketplace 上的官方 Claude Code for VS Code 扩展 2.1.312 和 2.1.313 被植入 SSH 后门，仅卸载扩展无法清除，用过的开发者需要排查清理。
- 开源模型方面，SenseNova-Loop-9B-Preview 以 Apache License 2.0 开放，腾讯公开了 5B 全模态解析模型 Youtu-Parsing-Omni 的代码和权重。
- Claude Code v2.1.316 弃用 Opus 4.8 的 fast mode，官方建议迁移到 Opus 5.5。

## 🔥 头条

### Cursor 市场上的 Claude Code 扩展被植入 SSH 后门

安全公司 Phorion 发现，Cursor Marketplace 分发的官方 Claude Code for VS Code 扩展 2.1.312 和 2.1.313 被植入后门：它会向 ~/.ssh/authorized_keys 追加攻击者的 Ed25519 公钥（注释为 svc-telemetry）并建立持久化，Cursor 已下架这两个版本。Phorion 提醒仅卸载扩展无法清除后门，用过这两个版本的开发者应按通报删除公钥和持久化项，并在有入侵迹象时轮换凭据。

来源：[phorion.io](https://phorion.io/blog/offical-claude-code-vsx-compromise/) · [HN 讨论](https://news.ycombinator.com/item?id=50300683) · [doublepulsar.com](https://doublepulsar.com/anthropic-hacked-to-deliver-remote-access-trojan-to-claude-developer-laptops-worldwide-1148a92baae2) · [cyberplace.social](https://cyberplace.social/@GossiTheDog/117528831681803563)　`安全` `代码` `工具`

### SenseNova 开源循环解码多模态模型 SenseNova-Loop-9B-Preview

SenseNova-Loop-9B-Preview 是面向长上下文和 Agent 工作流的多模态模型，接受文本和图像、输出文本：24 层解码器共享权重执行两次，用 32 个不同的层得到 56 次层执行，并配合双流 mHC，训练最大序列长度 262,144 tokens，采用 Apache License 2.0。它展示了不复制参数也能加深计算路径的做法，做文档理解、代码和工具调用的开发者可以拿来对比同尺寸模型。

来源：[Hugging Face](https://huggingface.co/sensenova/SenseNova-Loop-9B-Preview) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xje5oo/sensenovasensenovaloop9bpreview_hugging_face/)　`模型` `开源` `多模态`

### 腾讯开源 5B 全模态解析模型 Youtu-Parsing-Omni

Youtu-Parsing-Omni 把文档、图像、音频和视频统一解析成带时空定位的结构化记录，所有模态共用一个编码器，OmniSchema 统一了十项解析任务的输出。单个 5B 检查点在 OmniDocBench v1.6 上达到 96.96 Overall，在 OmniParsingBench 上以 75.08 领先所有开放权重模型，代码和权重均已公开，可以给需要跨模态定位和引用证据的 Agent 当感知层。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.39301)　`多模态` `开源` `论文`

## 🧠 模型

### Datalab 发布 689M 参数的 Surya OCR 2.5

Surya OCR 2.5 支持版面分析和阅读顺序、把表格输出为 HTML，OmniParseBench 得分 85.9、olmOCR-bench 83.7%，单张 H100 在 192 DPI 下吞吐 4.5 pages/s。代码采用 Apache 2.0，权重是修改版 AI Pubs Open Rail-M 许可，对研究、个人和融资/收入低于 $5M 的初创免费，更大规模商用前要先看许可。

来源：[Hugging Face](https://huggingface.co/datalab-to/surya-ocr-2.5) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xjmfxb/datalabtosuryaocr25_hugging_face/)　`模型` `多模态` `工具`

### speridlabs 开源单图生成 3D 高斯模型 Idol

Idol 输入一张物体图片（渲染图、生成图或照片），自动去背景、取景，生成最多 1,048,576 个 Gaussian 并写成标准 3DGS .ply，图片里看不到的侧面也会补全。它在消费级 GPU 上占用 7.2 GB 显存、采用 apache-2.0 许可，适合直接接进 3D 资产生成流程。

来源：[Hugging Face Trending Models](https://huggingface.co/speridlabs/idol)　`模型` `开源` `图像`

## 📄 论文

### Soft-MTP：一行代码改进多 Token 预测训练

麻省理工学院的研究指出，标准 MTP 的交叉熵梯度可以精确分解为 KL 自蒸馏项和一个低信噪比的残差项，后者会干扰学习；Soft-MTP 只回传 KL 信号，是一行代码改动，不增加参数，兼容 DeepSeek 和 Meta 两种 MTP。在 167M 到 1.2B 参数的各个规模上，它的 NTP 困惑度、投机解码速度和零样本准确率都优于标准 MTP，预训练里用 MTP 的团队可以低成本试一试。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.38331) · [Multi-Token Prediction Done Right [R]](https://i.redd.it/pdz8voy3inyh1.png) · [[Paper] Multi-Token Prediction Done Right - Soft-MTP](https://i.redd.it/28dgjexv5lyh1.png)　`论文` `训练`

### 基准的难度分布会误导排行榜结论

伊利诺伊大学香槟分校等团队把基准看作难度上的经验测度，形式化了“测度失配”和“覆盖缺口”两种失效模式并给出诊断指标；分析 7 个领域的 25 个常用基准后发现，很多基准偏重某些难度区间，另一些留下大片难度空白，难以反映训练进展。作者还提出按难度定向改写题目的 BenchFill 来补缺口，用基准追踪模型进展前值得先看看它的难度覆盖。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.29927) · [i.redd.it](https://i.redd.it/0tb53de34oyh1.jpeg)　`论文`

## 🛠 开源与工具

### Claude Code v2.1.316 弃用 Opus 4.8 的 fast mode

新版宣布 Opus 4.8 的 fast mode 自 October 30, 2026 起弃用、November 30, 2026 移除，移除后这类请求会直接报错，不会回落到标准 Opus 4.8，官方建议迁移到 Opus 5.5 以保留加速。同时新增了关闭 ultrathink 关键词、为子 Agent 设定默认 effort 级别的环境变量；依赖 Opus 4.8 fast mode 的脚本和工作流需要尽快迁移。

来源：[GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.316)　`工具` `代码` `Agent`

### vLLM 合入 Qwen4Exp 的 PLE 磁盘卸载

vLLM 已合并的 PR 为 Qwen4Exp 新增 disk_offload 选项：PLE n-gram 表留在 checkpoint 文件里，每步只在主机端读取需要的行。在 DGX Spark (GB10) 上，Qwen3.8-Flash-Next NVFP4 加载内存少 27.0 GiB，解码速度与常驻表相差在 3.5% 以内，代价是 TTFT 升高约 11%，内存紧张的本地部署可以在 nightly 版本里试用。

来源：[GitHub](https://github.com/vllm-project/vllm/pull/59958) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xjpbcg/vllm_now_has_ple_disk_offload_support_on_nightly/)　`工具` `推理` `开源`

## ⚡ 快讯

- **Blackstone 预计 Anthropic IPO 后获“高垃圾级”评级** 据 FT 报道，Blackstone 预计 Anthropic IPO 后获双 B 区间评级（投机级最高档），此前它曾预计 2027 年前获投资级评级。 [techcrunch.com](https://techcrunch.com/2026/10/30/anthropic-expected-to-receive-high-junk-rating-from-credit-agencies-following-ipo-report-says/) · [ft.com](https://www.ft.com/content/59383c7f-8d82-493f-bf01-d2e862a1018f)
- **OpenAI 将遵循共享的 robots.txt 训练偏好信号** OpenAI 表示将遵循一个共享的 robots.txt 信号，方便网站运营者向参与的 AI 提供商表达训练偏好。 [OpenAI News](https://openai.com/index/helping-websites-express-ai-training-preferences)
- **NVIDIA 发布实时动作生成模型 MotionBricks** MotionBricks 根据角色近期姿态和目标姿态实时生成过渡动作，提供 SOMA 和 Unitree G1 两套权重，只生成动作、不是机器人控制器。 [Hugging Face Trending Models](https://huggingface.co/nvidia/MotionBricks)
