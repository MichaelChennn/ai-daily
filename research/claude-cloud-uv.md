# Claude 云端会话的 uv 可用性调研（#17）

检索日期：2026-10-25。一手来源只用 Anthropic 官方文档：

- [CE] Cloud environments：https://code.claude.com/docs/en/cloud-environments
- [WEB] Use Claude Code in the cloud：https://code.claude.com/docs/en/claude-code-on-the-web
- [RT] Cloud scheduled tasks（原 routines）：https://code.claude.com/docs/en/routines

## 结论

**用户什么都不用做。** 默认环境（**Default**，网络级别 **Trusted**）的镜像已经预装 `uv`，不需要 setup script。
daily-editor 第 0 步直接写 `uv sync` 即可，另加一行兜底（见下文），防止哪天镜像变了。

## 1. 默认镜像是否预装 uv，什么版本

- 预装。[CE]「Installed tools」表格的 Python 一行原文：
  `Python 3.x with pip, poetry, uv, black, mypy, pytest, ruff`。
- 镜像是 Ubuntu 24.04、x86_64，每个会话一台新 VM：
  "each session gets a fresh virtual machine (VM) running Ubuntu 24.04 on x86_64 … with your repository cloned and common toolchains pre-installed" [CE]。
- **版本文档里没写**，Python 也只写了 "3.x"。官方给的查法是在云端会话里让 Claude 运行 `check-tools`：
  "To get the versions of most of the tools in this table, ask Claude to run `check-tools` in a cloud session. It's a shell command installed on the session VM" [CE]。
  本调研是在本地跑的，没法执行 `check-tools`，所以没有具体版本号。下一次定时任务里让 skill 打一行 `uv --version` 进日志就能看到（见第 3 节）。
- **Default** 环境没有 setup script，也没有环境变量："**Default** defines no environment variables or setup script, so sessions start with just the pre-installed tools" [CE]。
- 定时任务用的也是这些环境：每个 scheduled task 都绑一个 cloud environment，"The **Default** environment uses **Trusted** network access" [RT]。

## 2. setup script：在哪配、限制是什么

**在哪配**
- 新建会话页面（claude.ai/code）消息框下方的环境选择器里新增或编辑环境，在弹窗里点 **Setup script** 那一行，粘贴脚本或用 **Choose file** 载入（≤ 64 KB），再点 **Add environment** 或 **Save changes** [CE]。
- 定时任务的编辑页里也能进：**Advanced settings > General > Cloud environment**，点显示环境名（如 **Default**）的云图标 [RT]。

**怎么运行**
- 会话启动时、Claude Code 启动之前运行，以 root 身份跑在 Ubuntu 24.04 上："Scripts run as root on Ubuntu 24.04, so `apt install` and most language package managers work" [CE]。
- 脚本退出码非 0 时会话起不来，不重要的命令要加 `|| true` [CE]。
- 脚本运行时环境变量还没注入，需要的值要写在脚本里 [CE]。

**运行时长与缓存**
- 大约 5 分钟内跑完，Anthropic 会给文件系统做快照，之后的会话直接用快照、跳过脚本；超过约 5 分钟就不缓存 [CE]。
- 改脚本或改允许的域名时缓存会重建，缓存大约 7 天过期 [CE]。
- 会话里 Bash 命令默认等 2 分钟，最多 10 分钟；SessionStart hook 默认 600 秒超时 [CE]。

**网络**
- 四个级别：None / Trusted / Full / Custom。Default 是 **Trusted**，只能访问白名单域名 [CE]。
- 白名单包括 `pypi.org`、`files.pythonhosted.org`、`github.com`、`objects.githubusercontent.com`、`release-assets.githubusercontent.com` [CE]。
- **`astral.sh` 不在白名单里**（全文检索无结果）。所以 issue 里提的 `curl -LsSf https://astral.sh/uv/install.sh | sh` 在 Trusted 级别下会被拦（[RT]：白名单外的请求返回 `403`、`x-deny-reason: host_not_allowed`）。
- 白名单外的请求失败；`pip install uv` 走 PyPI，可以用。

**setup script 和 SessionStart hook 的区别** [CE]
- setup script：在环境弹窗里配，只在云端跑，有缓存时跳过。
- SessionStart hook：写在仓库 `.claude/settings.json`，本地和云端都跑，每次会话（包括 resume）都跑。

## 3. 如果没有 uv：安装方式和第 0 步的兜底

按第 1 节，目前不会走到这一步。只是防镜像变动：

- 最简单、在 Trusted 下能用的装法：`python -m pip install -q uv`（走 PyPI）。不要用 astral.sh 的 curl 脚本，原因见上。
- 用 `python -m pip` 而不是 `pip`，避开 #9 里提到的 pip 和 python 指向不同解释器的问题。

建议 #9 把 daily-editor 第 0 步写成：

```bash
command -v uv >/dev/null || python -m pip install -q uv   # 云端镜像已预装 uv；这一行只是兜底
uv --version                                             # 日志里留一份版本号
uv sync
```

如果之后真想放进 setup script（例如镜像不再预装），环境弹窗的 **Setup script** 里粘贴：

```bash
#!/bin/bash
command -v uv >/dev/null || python3 -m pip install -q uv || true
```

## 4. 给 #9 的附注（不在本题范围，顺带发现）

- `pyproject.toml` 现在的 dev 依赖写在 `[project.optional-dependencies] dev`。`uv sync` 默认只装 `[dependency-groups]` 里的 `dev` 组，不装 optional extras。要满足 #9 的「`uv sync` 默认装上 dev」，得把 dev 改成 `[dependency-groups]`，或者命令写成 `uv sync --extra dev`。这一条依据是 uv 自己的行为，不是 Anthropic 文档，#9 实现时请到 https://docs.astral.sh/uv/concepts/projects/dependencies/ 核对。

## 用户操作步骤

不需要任何操作。不用改环境，也不用加 setup script。
