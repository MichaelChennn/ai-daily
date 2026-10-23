# 2026-10-22 · AI 科技日报

## 今日要点

- Wiz 用 AI 发现 PHP 核心引擎远程代码执行漏洞 PHP2Shell，PHP 官方已发布补丁；LiteLLM 1.107.0 遭投毒，最新安全版本是 1.106.2，请尽快检查依赖。
- Anthropic 推出研究预览版 Claude Duet；Recursive 开源编程模型 Flint，Ollama 已支持。

## 🔥 头条

### Wiz 用 AI 挖出 PHP 核心引擎远程代码执行漏洞 PHP2Shell

Wiz Research 披露了 PHP 核心引擎里的一组内存安全漏洞（CVE-2026-109618、CVE-2026-109619），可用于未授权远程代码执行和读取进程内存，过去十年发布的 PHP 版本都受至少一个漏洞影响，最早到 5.4；PHP 官方已发布补丁。研究全程使用了 Gemini 4 Argon 和 GPT-5.6 Sol 等前沿模型。漏洞在 PHP 本身，不依赖应用代码，跑 PHP 的服务都应尽快升级。

来源：[wiz.io](https://www.wiz.io/blog/php2shell-php-rce) · [HN 讨论](https://news.ycombinator.com/item?id=50180836)　`安全`

### LiteLLM 1.107.0 遭投毒，窃取云和 AI 密钥

Wiz 报告，PyPI 和 GHCR / Docker Hub 上的 LiteLLM 1.107.0 被植入凭据窃取程序，目标是浏览器、云和 AI 服务的密钥，PyPI 上约 49,000 次下载，最新安全版本是 1.106.2。据 BerriAI 说明，攻击者通过被盗的 GitHub CLI OAuth 令牌控制了三名工程师的账号来触发发布流程。装过这个版本或拉过相关镜像标签的环境，应锁定旧版本并轮换机器上的凭据。

来源：[Wiz Blog](https://www.wiz.io/blog/litellm-compromised-steals-credentials)　`安全` `工具`

### Anthropic 推出主动型 Agent 应用 Claude Duet

Claude Duet 是一个独立应用，Claude 在自己的虚拟机和浏览器里后台干活，每天早上发简报，需要你决定时才发消息，可接入 6,000 多个连接器和插件。发消息、付款、签署或删除之前，它会先展示要做的操作并等待批准。目前是研究预览，面向美国的 Pro 和 Max 订阅用户排队开放，用量计入现有套餐。

来源：[Claude Duet](https://claude.com/product/claude-duet) · [Claude Duet](https://claude.com/resources/articles/claude-duet) · [HN 讨论](https://news.ycombinator.com/item?id=50186037)　`Agent` `产品`

### Anthropic：用 Claude 缩减代码攻击面，在 25 个项目中发现 493 个问题

Anthropic 让 Claude 从三个角度检查代码：默认配置下多余的可达代码、认证前就会执行的代码、悄悄削弱安全控制的配置组合，在 25 个项目中发现 493 个问题。其中 OpenSSH 默认配置下未认证客户端可触达约 4,500 行实验性 ML-DSA-44 代码，约占 sshd 认证前代码的 16%，已经在后续版本中修复。这套方法已打包成可复用的 Claude skill，即使不用这个 skill，开发者也可以照这套思路审查自己的项目。

来源：[anthropic.com](https://www.anthropic.com/research/attack-surface-reduction) · [HN 讨论](https://news.ycombinator.com/item?id=50175779)　`安全` `Agent`

## 🧠 模型

### Recursive 开源编程模型 Flint，40B 总参数、2.5B 激活

Flint 是 Recursive 从头训练的 MoE 模型，面向在代码仓库里工作的编程 Agent，上下文 262K，Apache 2.0 许可；官方评测 Terminal-Bench 2.1 为 54.9%、SWE-bench Verified 为 74.2%。Ollama v0.40.8 已支持 ollama run flint，目前仅限 MacOS。每个 token 只激活约 2.5B 参数，适合拿来测试本地编程 Agent。

来源：[Hugging Face Trending Models](https://huggingface.co/RecursiveSI/flint) · [GitHub Releases](https://github.com/ollama/ollama/releases/tag/v0.40.8)　`模型` `开源` `代码`

### KRAFTON 开源 Raon-1 mini 预览版 30B-A4B

Raon-1 mini 是 KRAFTON AI 从头训练的 30B-A4B MoE 模型，擅长韩语对话和 Agent 任务，原生支持 262,144 token 上下文，Apache 2.0 许可。官方提供 NVFP4 量化版，单张 RTX 5090 就能推理，还附带用于推测解码的 DFlash2 草稿模型。适合需要韩语能力或在单卡上跑 Agent 的开发者试一试。

来源：[Hugging Face](https://huggingface.co/KRAFTON/Raon-1-mini-preview) · [Reddit 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1xbh0ev/kraftonraon1minipreview_hugging_face/)　`模型` `开源`

## 📄 论文

### Agent S4：让电脑操作 Agent 从经验中进化出自己的接口

Agent S4 用元 Agent 分析任务轨迹，自动构建和修订 Agent 使用的接口与用法知识，再用种群进化挑选泛化好的版本。在 OSWorld V2 上，Qwen3.8-27B 配合进化出的接口达到 21.3%，是固定接口的 3.8 倍，高于 Claude Opus 4.8 的 20.6%。代码已开源，说明给 Agent 设计接口这件事本身也可以交给 Agent。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.28601) · [arXiv](https://arxiv.org/abs/2610.28601)　`论文` `Agent`

### Matrix-Game 4.0：游戏引擎加视频模型，实时生成可玩世界

Matrix-Game 4.0 把游戏执行和画面生成分开：轻量游戏引擎维护世界状态和规则，编程 Agent 把玩家想法转成游戏代码，基于自回归视频模型的渲染器把低多边形画面变成精细画面。单张 RTX5090 上可以 480p、60 FPS 运行，按键到显示延迟 112ms。代码、模型权重和资产都已开源，可用于研究可交互的世界模型。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.27999) · [arXiv](https://arxiv.org/abs/2610.27999)　`论文` `视频` `开源`

### PAR：让循环语言模型在更长的问题上也有效

PAR 训练循环模型在第 k 次迭代时对齐前 k 步操作后的状态，并把循环状态缩放回第一次迭代的范数。在 swap-S5 上，用最多 32 步训练的 Qwen2.5-0.5B 在 512 步时达到 95.5% 准确率，是训练长度的 16 倍，同一模型用显式思维链只有 0.8%。对研究测试时扩展计算的人来说，这说明监督中间步骤是长度外推的关键。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2610.27628) · [arXiv](https://arxiv.org/abs/2610.27628)　`论文` `推理` `训练`

## 🛠 开源与工具

### Claude Code v2.1.306 / v2.1.307 发布

v2.1.307 新增 /claude-api api-version 命令，可把 Claude API 代码迁移到 API version 2026-10-21；还新增 claude_code.safety OpenTelemetry 事件，每当权限规则、auto mode、hook 或沙箱拦截工具调用时都会记录。另外修复了 HTTP MCP 工具调用在连接中断时被重复发送等问题，现在只重试只读或幂等的工具。

来源：[anthropics/claude-code v2.1.307](https://github.com/anthropics/claude-code/releases/tag/v2.1.307) · [anthropics/claude-code v2.1.306](https://github.com/anthropics/claude-code/releases/tag/v2.1.306)　`工具` `代码` `Agent`

## ⚡ 快讯

- **OpenAI 模型登陆 Google Cloud** OpenAI 与 Google Cloud 宣布把前沿模型和 Codex 工作流带到 Model Garden，通过 Google Cloud Marketplace 提供。 [OpenAI News](https://openai.com/index/openai-models-google-cloud) · [HN 讨论](https://news.ycombinator.com/item?id=50180079)
- **OpenAI 发起 Patch the Planet 漏洞协同响应计划** 随着 Agent 发现越来越多严重漏洞，OpenAI 发起 Patch the Planet，把安全研究者、维护者和应急响应人员连接起来，协同修复开源项目中的严重漏洞。 [OpenAI News](https://openai.com/index/coordinated-disclosure-of-critical-vulnerabilities)
