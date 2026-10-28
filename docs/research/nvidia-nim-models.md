# NVIDIA NIM 免费模型调研

结论：API 路线在 NIM 上继续用 `minimaxai/minimax-m3.1-flash`。`stepfun-ai/step-5-preview` 可以作为第二备选，其他模型都不建议用（#27，2026-10-28）。

## 怎么查模型

`GET https://integrate.api.nvidia.com/v1/models`（OpenAI 兼容，用 `NVIDIA_API_KEY`）返回 85 个 id。它只是目录：

- 不给上下文长度，也不标免费或付费；
- 列表里有的模型不一定能调用，见下面的 404。

所以要先给每个模型发一条很短的请求（`max_tokens=8`），确认能不能调用。

## 能否调用（2026-10-28，单次探针）

| 模型 | 结果 | 说明 |
|---|---|---|
| `minimaxai/minimax-m3.1-flash` | ✅ 200，0.6s | 目前在用 |
| `stepfun-ai/step-5-preview` | ✅ 200，0.5s | |
| `nvidia/nemotron-3-ultra-550b-a55b` | ✅ 200，0.7s | |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | ✅ 200，0.3s | |
| `google/gemma-4-31b-it` | ⚠️ 529，30s | 服务过载 |
| `poolside/laguna-xs-2.1` | ⚠️ 503 | `Worker local total request limit reached` |
| `z-ai/glm-5.3`、`z-ai/glm-5.3-flash` | ⏱ 90s 无响应 | |
| `openai/gpt-oss-20b` | ⏱ 90s 无响应 | |
| `deepseek-ai/deepseek-v4.1-flash` | ⏱ 90s 无响应 | 10-26 完整测试时 4 次都在 600s 内没返回 token |
| `moonshotai/kimi-k2.6`、`nvidia/nemotron-3-super-120b-a12b`、`nvidia/llama-3.1-nemotron-ultra-253b-v1`、`mistralai/mistral-large-2-instruct` | ❌ 404 | `Function ... Not found for account` |

超时和过载可能只是当时那个时段的情况。GLM 和 DeepSeek 以后可以换个时间再试。

没测的模型多半不适合写日报：

- 老的或小的通用模型：yi-large、jamba、dbrx、mixtral、nemotron-4、phi-3.5、gemma-3 等；
- 专用模型：代码、视觉、embedding/rerank、安全审核、翻译、文档解析、金融/医疗。

### 404 "Not found for account"

- NVIDIA 官方没有解释过这个错误，论坛上 2026 年 7 月到 10 月一直有人报。
- 我们的账号能调用其他模型，所以不是缺少 "Public API Endpoints" 权限：缺这个权限的人是所有模型都 404。
- 更可能的原因是这几个模型的免费托管实例已经下线，或者改成按组织授权了，而 `/v1/models` 没有同步更新。
- 没有自助提权的方法。唯一的渠道是发邮件给 help@build.nvidia.com，附上注册邮箱和完整的错误内容。
- 想区分两种原因，可以先在 build.nvidia.com 的 playground 里试同一个模型：
  - 网页上能用、API 却 404：是账号授权的问题，值得发邮件；
  - 网页上也不能用：是模型下线了。

参考：

- [kimi-k2.6 / deepseek-v4-pro hang or 404](https://forums.developer.nvidia.com/t/newer-nim-models-kimi-k2-6-deepseek-v4-pro-hang-indefinitely-or-404-possible-missing-public-api-endpoints-permission/377777)
- [404 for some models](https://forums.developer.nvidia.com/t/404-error-function-not-found-for-some-models-how-to-list-supported-models-via-api/341923)

## 完整日报测试（2026-10-26 这一期，三次请求流程）

| | 条目 | 耗时 | 写稿阶段被拒 | validate 警告 | 和 Claude 版重合 |
|---|---|---|---|---|---|
| Claude（正式版） | 8 | – | – | – | – |
| **minimax-m3.1-flash** | **12** | 19 分钟 | – | 无 | **7** |
| step-5-preview | 8 | 16 分钟 | 2，修正后 0 | 0 篇论文 | 4 |
| nemotron-3-ultra | 6 | **4.6 分钟** | 5，修正后仍 5 | 不足 8 条、0 篇论文 | 2 |
| nemotron-3.5-lightning | 失败 | 15 分钟 | – | – | – |
| deepseek-v4.1-flash | 失败 | 42 分钟 | – | – | – |

### 各模型的优缺点

| 模型 | 好处 | 坏处 |
|---|---|---|
| minimax-m3.1-flash | 条目最多，和 Claude 版选题最接近，头条和论文都有，没有警告 | 慢（约 19 分钟）；HF 页面开头的元数据会让模型条目像在念配置 |
| step-5-preview | 写法紧凑、数字多，比如"128K 历史存储约省 66×"；修正之后没有被拒的条目 | 选题偏新模型发布，漏了皮肤癌 CNN、llama.cpp CVE、降价分析这几条新闻；highlights 写成一整句长句；把 Nanbeige 的 SWE-Bench Pro 成绩写成"领先"，实际是 60.3，低于 Qwen3.8-27B 的 61.7 |
| nemotron-3-ultra | 最快；摘要详细，选题有独到之处（Timestral、Hy-Memory、Cloudflare 安全审计 skill） | 被拒的条目多，最后只有 6 条；同样夸大了 Nanbeige 的成绩；highlights 提到了被拒掉的 Indra OCR 那一条 |
| nemotron-3.5-lightning | 探针响应最快 | 写稿那一步回复里没有 JSON，30B-A3B 的模型撑不住这么长的结构化输出 |
| deepseek-v4.1-flash | – | 迟迟不返回 token，没法用 |

### 共同问题

step 和 ultra 都把 Nanbeige 的跑分写成了全面领先。修正那一步只按 validate 退回的原因改格式和引文，不核对数字比较的方向。这对所有 API 模型都可能发生。

## 后续

- Gemini 路线改用 Jules 的事放在另一个 issue 里。
- NIM 上只保留 MiniMax；step-5-preview 作为备选，需要时加进 `EDITOR_API_MODEL`。
