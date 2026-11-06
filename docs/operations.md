# 定时任务、发布与网站

每天无人值守地抓取、编辑、发布一期日报。两条编辑通道的取舍见 [adr/0001-two-editor-routes.md](adr/0001-two-editor-routes.md)。

## 每天的时间表

| 柏林时间 | 谁 | 做什么 |
|---|---|---|
| 05:07 | Actions `fetch.yml` | 抓取，把 `candidates.json` 提交到 main |
| 05:30 | Claude 定时任务（每次新开一个 cloud session） | 运行 daily-editor skill，写中文版和英文版，推到本会话的 `claude/` 分支 |
| 05:30 | Actions `editor-api.yml` | API 通道：`EDITOR_API_MODEL` 里的每个模型各编一份 `digest.api.<slug>.json`（Beta 版）和生成记录 `trace.api.<slug>.json`（模型失败时也提交）；Claude 还没出结果时，第一份合格的成为主版，同一个模型再写一份英文版。谁写英文版由 `daily.publish` 决定，workflow 只调 `daily edit --out` 和 `daily ingest --from-dir` |
| 推送后 | Actions `ingest.yml` | `daily ingest --ref`：用 main 上的候选重新校验，按规则并入 main，启动 `pages.yml` |
| 06:30 | Actions `fallback.yml` | 当天没有合格的 digest 就发布降级版，提交并启动 `pages.yml` |
| 之后 | Actions `pages.yml` | `web/` 构建（含 `daily export`）→ GitHub Pages |

**为什么抓取放在 Actions**：Claude cloud session 访问不了其他仓库的 GitHub API，Reddit 也会拒绝它的请求；Actions 自带 `GITHUB_TOKEN`，网络不受限制。05:30 的 Claude 编辑任务直接从仓库读取候选。`fetch.yml` 也可以在 Actions 页面手动触发，指定期号日期补抓。

**为什么要 ingest**：cloud session 只能推送到它自己的 `claude/` 分支。ingest（`daily/ingest.py`）只从分支拿 `data/*/digest.json`、`data/*/digest.en.json` 和生成记录 `data/*/trace.claude.json`（日报被采用时替换 main 上的，没被采用时只在 main 上的记录里记一笔），`digest.md` 在 main 上重新渲染，其他改动不会进入 main。也可以在 Actions 页面手动运行 ingest，指定分支名，补收没有触发它的分支。已经并入的 `claude/` 分支两天后由 `prune-branches.yml` 删除。

**为什么用 workflow_dispatch 串起来**：用 `GITHUB_TOKEN` 推送的提交不会触发其他 workflow（workflow_dispatch 除外），所以 ingest 和兜底提交之后用 `gh workflow run pages.yml --ref main` 启动构建。人推到 main（合并 PR）会直接触发 `pages.yml`。

## 并入规则

`daily/publish.py`（`daily adopt`）：

- 正式版替换降级版（编辑在 06:30 之后才完成），降级版不会覆盖正式版，正式版只会被更新的正式版替换（重做）。
- 主版的优先级是 Claude 通道 > API 通道 > 降级版：Claude 的版本总会替换 API 通道的版本，API 通道的版本不替换任何正式版。
- 英文版跟着主版走：写主版的那条通道负责写英文版。

## API 通道配置

- secrets：`NVIDIA_API_KEY`。
- variable `EDITOR_API_MODEL`：`厂商:模型`，逗号分隔，顺序就是成为主版的优先级。同一个模型家族只放一个，文件名按家族取，如 `deepseek`、`minimax`。
- 可选模型和免费额度的调研见 [research/nvidia-nim-models.md](research/nvidia-nim-models.md)。

## 告警

Actions 失败时 GitHub 会发通知：

- `fetch` 没有拿到任何内容；
- 06:30 时连 `candidates.json` 都没有；
- 连续两天都是降级版。

## 时区

Actions 的 cron 只认 UTC，柏林有夏令时（CEST UTC+2 / CET UTC+1），所以 `fetch.yml`、`editor-api.yml` 和 `fallback.yml` 各写了冬夏两条 cron，每天都会触发两次。第一个 job `due` 调用可复用 workflow `due.yml`，只传柏林时间（如 `at: "05:07"`）：这次触发的 UTC 时刻换算成今天的柏林时间等于 `at` 才放行，手动触发总是放行。改时间时只改 `on.schedule` 的两条 cron 和 `at`。Claude 定时任务的 cron 直接写 `CRON_TZ=Europe/Berlin`。

## 共用的 action

- `.github/actions/setup`：checkout 之后装 uv、Python 3.12 和锁定的依赖，所有跑 `daily` 的 workflow 都用它。
- `.github/actions/publish`：把 `data/` 提交到 main 并推送，有人先推了就重试，最多 3 次，然后启动 `pages.yml`。传 `run` 时（ingest、editor-api、fallback）每次尝试都先回到最新的 main 再执行它，判断总是基于 main 上现有的稿子，不需要 rebase；不传时（fetch，不能重抓）只提交一次，重试时 rebase。提交信息里的 `{dates}` 换成这次改动的期号日期。

## 一次性设置

仓库 Settings → Pages → Source 选 **GitHub Actions**（下面推荐的 “GitHub Pages Jekyll” / “Static HTML” 都不用点，仓库里已经有 `pages.yml`）。

## 网站

`web/`：Astro + React + Tailwind + [shadcn/ui](https://ui.shadcn.com/)，黑白配色，页面都是预渲染的静态 HTML。中文在根路径，英文版在 `/en/` 下，页面一一对应。打开页面时按读者的语言跳到对应版本：在语言菜单里选过的以所选为准，否则浏览器首选语言是中文就看中文版，其他一律看英文版；只有中文的 Beta 版和生成过程页不跳。首页就是最新一期（canonical 指向它的日期页），每期一页（`YYYY-MM-DD/`），Beta 版在 `YYYY-MM-DD/beta/`，往期归档按年份和月份筛选，信息源页用卡片列出白名单和最近 30 期的抓取成功次数、平均候选数、入选条目数。降级版在正文顶部和 RSS 标题里都有标注。

- **数据**：`daily export` 把能通过 `validate`（离线部分）的各期写成 `web/data/issues/*.json`，内容是分区、条目、来源链接、发布方（GitHub / Hugging Face 的 owner 头像，其他站点用 favicon）和发布时间；信息源写成 `web/data/sources.json`；全文 RSS 写成 `web/public/feed.xml`（英文 `feed.en.xml`），链接用 `SITE_URL`（默认线上地址）。这些都在构建时重新生成，不提交。前端只负责排版，发布规则都留在 Python。只有一手来源的时间才算发布时间（HN、Reddit 的时间是发帖时间，不显示），只精确到天的来源只显示日期。
- **RSS**：最近 30 天，全文，只发主版。guid 带上 mode，降级版被正式版替换后，阅读器会把正式版当作新条目收到。
- **交互**：分类、年月和信息源分组筛选、日夜模式切换（选择存在 localStorage）；换页和筛选用 View Transitions 过渡。

```bash
cd web && npm ci
npm run dev                  # 先自动跑 daily export（需要能 import daily 的 python），然后打开 http://localhost:4321/ai-daily/
npm run check                # 类型检查

# 预览构建结果
SITE_URL=http://localhost:8000/ npm run build
python -m http.server -d dist
```
