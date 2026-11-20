# 2026-11-20 · AI 晨报

## 今日要点

- Gemini API 预览 Tool Retrieval：工具参数 schema 按需加载，支持 Gemini 3.6 及之后的模型。
- 微软发布 Windows 端侧小模型 Aion 1.0 Instruct；OpenAI 公开用 Codex Agent 自动排查性能回归的 Performance Factory。
- 论文 Resolution Hypothesis 指出，Agent 自我进化的瓶颈在于噪声评估分辨不出更好的候选。

## 🔥 头条

### Gemini API 预览 Tool Retrieval：按需加载工具 schema

Google 在 Gemini Interactions API 中预览 Tool Retrieval：请求里加入 tool_search 工具、给工具设置 defer_loading 后，模型只看到工具的名称和描述，需要时再按名字加载参数 schema；对 mcp_server 工具设置 defer_loading，整个远程 MCP 服务器的工具也会按需加载。功能不单独收费，支持 Gemini 3.6 及之后的模型。工具库很大的 Agent 可以借此减少输入 token，而且已加载的 schema 追加在对话后部，提示前缀保持不变，便于缓存。

来源：[Google AI Blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/)　`Agent` `工具` `产品`

### 微软发布 Windows 端侧小模型 Aion 1.0 Instruct

微软 Windows Applied Sciences Group 在 Hugging Face 发布 2.3B 参数的 Aion 1.0 Instruct，定位为 Windows 生态的基础小语言模型（SLM），针对端侧 AI、文本和操作系统场景优化，上下文 32,768 tokens，MIT 许可。模型卡称，进一步优化的版本将配合微软的内容审核模型，于 2027 年一月底前成为 Windows 系统的 SLM；目前先发布未量化版本，量化版随后推出。为 Windows 做端侧功能的开发者可以提前用它评估效果。

来源：[Hugging Face Trending Models](https://huggingface.co/microsoft/Aion-1.0-Instruct-2.3B)　`模型` `开源` `产品`

### OpenAI 公开 Performance Factory：用 Codex Agent 排查性能回归

OpenAI 介绍了内部的 Performance Factory：工程师为重复性工作定义 workflow，性能告警触发后由云端的 Codex Agent 调查回归、找出根因，另一个 Codex 会话做对抗式审查、尝试推翻诊断；通过后由 Codex 实现修复并开 PR，工程师审阅后决定是否合并。人工复核 100 条根因建议，70% 被评为准确。想把编码 Agent 用到线上运维的团队，可以参考它拆分任务、加入对抗式审查和人工把关的做法。

来源：[OpenAI News](https://openai.com/index/how-openai-performance-factory-keeps-chatgpt-fast)　`Agent` `代码` `工具`

## 🧠 模型

### Cloudflare 发布 27B 多模态结构化抽取模型 Clairic

Clairic 基于 Qwen3.8-27B，输入文本或 JSON 状态（可附图片）和一组字段定义，输出带类型的值、列表、空值、估计值和预测路径，并给出抽取置信度和空值概率，以 Apache-2.0 许可发布。需要从文档或图片中抽取结构化字段的开发者，可以按每个字段的置信度决定哪些结果要人工复核。

来源：[Hugging Face Trending Models](https://huggingface.co/Cloudflare/clairic)　`模型` `开源` `多模态`

### Inworld 开源 48 kHz 人声分离模型 Voice Isolator

Inworld Voice Isolator v1 包含离线和实时两个模型，去除人声周围的噪声、只保留前景人声；实时版 58.2M 参数，在 20 ms look-ahead 下算法延迟为 63 ms，可用于通话和直播。模型以 Apache-2.0 许可发布，第一版只做降噪，不修复录音丢失的内容，修复计划在 version 2 推出。做语音 Agent 或音频处理管线的开发者可以把它用作人声前处理。

来源：[Hugging Face Trending Models](https://huggingface.co/inworld/voice-isolator)　`语音` `开源` `模型`

### Bria 发布 RMBG 3.0：用 8B 生成模型做背景移除

RMBG 3.0 是 Bria 第三代背景移除模型，也是第一个基于生成式基础模型的版本：在 Fibo 2.0 上微调并蒸馏，4 步生成 alpha matte。在 Bria 自己对 234 张困难图片的对比中，它平均排名 1.51，相对 RMBG-2.0 的偏好率为 60.9%。权重采用 CC BY-NC 4.0 非商用许可，商用需另签协议或改用 Bria API；处理毛发、运动模糊等难例的开发者可以先用它评估效果。

来源：[Hugging Face Trending Models](https://huggingface.co/briaai/RMBG-3.0)　`图像` `模型`

## 📄 论文

### Resolution Hypothesis：Agent 自我进化卡在分不清哪个更好

上海科技大学的论文提出 Resolution Hypothesis：Agent 进化（提出候选的提示词、skill、记忆并择优保留）停滞，往往不是因为提不出更好的候选，而是噪声评估分辨不出来。在七种进化方法、六个模型、超过 10M 次 LLM 调用的实验中，候选层面的选择不比随机好；方法层面几个百分点的领先，小于同一方法两次独立运行之间的差距。做提示词或 skill 自动优化的团队，在相信小幅提升之前应先确认它超过了运行间的波动。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.23068)　`论文` `Agent`

### AnyS1：用 4B 小模型替大模型做 Agent 流程里的选择

AnyS1 从超过 1,000 个公开 skill 中挖掘可枚举的决策点，在隔离容器里收集真实执行状态，训练一个 4B 的 pointer System-1 模型；运行时常规选择一次前向完成，置信度低于校准阈值时再交给大模型（System-2）。在三个未见过的基准上，它保持任务可靠性，同时比未编译的 System-2 Agent 降低 75-91% 的 episode 成本和 63-92% 的模型调用时间。按 skill 组织流程的 Agent 可以借此把大量常规决策下放给小模型。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.23751)　`论文` `Agent` `推理`

### Jeveration：单次前向生成 512x512 图像只需 78 ms

论文把 System One 式的并行预测用于图像生成：基于冻结的视觉语言模型，一次前向传播生成整张图，并让所有位置共享一个随机状态来协调并行预测、保证整体一致。同一个 checkpoint 支持文生图、图生图和稠密预测，生成 512x512 图像用时 78 ms，比现有统一模型最多快 122x。对需要低延迟出图的应用，这是一条单步生成的思路。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.24738)　`论文` `图像` `多模态`

### Game2Player：让 Agent 自己搭游戏环境、收集训练数据

Game2Player 由 Builder Agent 改造现有网页游戏、暴露内部状态并定义带进度度量和成功检查的任务，Coding Player 和 VLM Player 尝试完成任务、把问题反馈给 Builder 修复。由此得到 568 个网页游戏、3,436 个任务和 307 小时游戏经验；用这些轨迹训练后，9B 模型在留出的 PlayerBench 游戏上的进度从 14.3% 提升到 31.2%。做视觉 Agent 的团队可以参考这种环境与玩家共同迭代的数据生产方式。

来源：[Hugging Face Daily Papers](https://huggingface.co/papers/2611.24154)　`论文` `Agent` `多模态`

## 🛠 开源与工具

### Codex 0.171.0：加入 GPT-6.2 Sol 和 Astra，默认开启 TUI 工作区

OpenAI Codex 0.171.0 把 GPT-6.2 Sol 和 Astra 加入模型目录，并把 Sol 设为默认选择；TUI 工作区默认开启，可在主对话旁查看文档预览、图片预览和 subagent 记录。新版还加入 codex exec --remote，可在已有 app server 上启动或恢复非交互会话，并新增 /rc 和 /remote 管理远程控制。

来源：[GitHub Releases](https://github.com/openai/codex/releases/tag/rust-v0.171.0)　`工具` `代码` `Agent`

## ⚡ 快讯

- **Claude Code v2.1.329：/tasks 可管理定时任务和 fork** 新版在信任对话框中提示文件夹的 hooks 在哪里声明，/tasks 加入本会话的定时任务、/loop 唤醒和 fork，并修复 ~/.claude.json 偶尔被重置为默认值的问题。 [GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.329)
