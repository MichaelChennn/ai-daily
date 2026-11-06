# 命令行

所有命令都在仓库根目录通过 `uv run python -m daily <命令>` 运行。先 `uv sync` 建好 `.venv`（按 `uv.lock` 装依赖、dev 工具和本项目）。

```bash
uv run python -m daily fetch                       # 今天这一期 → data/YYYY-MM-DD/candidates.json
uv run python -m daily fetch --date 2026-10-20     # 指定期号（柏林时间日期）
uv run python -m daily fetch --only hackernews     # 只跑某个信源，调试用（可重复）

uv run python -m daily list --date 2026-10-21      # 精简列出候选（给编辑看）
uv run python -m daily page <url> --grep 关键词     # 打印原始页面里关键词附近的原文，用来逐字摘录 evidence
uv run python -m daily validate --date 2026-10-21 --check-links --drop-invalid   # 程序闸门
uv run python -m daily degrade --date 2026-10-21   # digest.json 缺失或不合格时，写入“标题 + 链接”降级版
uv run python -m daily render --date 2026-10-21    # digest.json → digest.md
uv run python -m daily adopt --date 2026-10-21 --from x.json   # 按规则并入一份 digest.json（--en 并入英文版，--trace 带上那次运行的生成记录）
uv run python -m daily ingest --ref FETCH_HEAD     # 并入编辑分支这次提交改过的全部 digest 和生成记录（ingest.yml 用）
uv run python -m daily ingest --from-dir run/      # 并入 edit --out 留下的一次 API 通道运行（editor-api.yml 用）
uv run python -m daily edit --model nvidia:minimaxai/minimax-m3.1-flash   # API 通道：逐个模型编辑（逗号分隔，默认取 EDITOR_API_MODEL），写 digest.api.<slug>.json；会成为主版的那份再写英文版 digest.en.<slug>.json（需要对应的 API key）
uv run python -m daily edit --model … --out run/   # 同上，另把 digest、英文版、生成记录和顺序清单 run.json 留在 run/
uv run python -m daily edit --en data/2026-10-21/digest.api.deepseek.json   # 只补写这一份的英文版（它会成为主版时）
uv run python -m daily export                      # 已发布各期 → web/data/（JSON）和 web/public/feed.xml，给前端用，不提交

uv run pytest -q && uv run ruff check . && uv run ruff format --check .
```

Claude 通道的编辑环节在 Claude Code 里运行 skill：`/daily-editor 2026-10-21`（[.claude/skills/daily-editor/SKILL.md](../.claude/skills/daily-editor/SKILL.md)）。

## 环境变量

| 变量 | 用途 |
|---|---|
| `GITHUB_TOKEN` | 可选，用于 GitHub Releases（不设置时限额 60 次/小时） |
| `NVIDIA_API_KEY` | `daily edit` 调用 NVIDIA NIM 的模型时需要 |

本地运行时把 key 写进 `.env`（已忽略），`set -a; . ./.env; set +a` 后再跑。

## 退出码

`fetch`：`0` 成功（个别信源失败只记录在输出里）；`1` 所有信源都没有拿到内容；`2` 参数错误。
