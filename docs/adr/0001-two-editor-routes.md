# 两条编辑通道并行，按优先级选主版

除了 Claude Code 定时会话（Claude 通道），我们在 GitHub Actions 里加了一条调用免费云端模型 API 的 API 通道，两条每天都跑。主版的优先级是 Claude 通道 > API 通道 > 降级版，API 通道的结果另外作为 Beta 版展示。Claude 通道目前质量稳定，所以继续做主版；API 通道不需要在 claude.ai 上维护定时任务，可以用免费额度，Claude 失败时它来顶上，降级版就很少出现了。没有选“用一个开关二选一”，因为两份并排放着，才能持续比较 API 通道的质量。

英文版由写主版的那条通道来写（2026-10-27 补）：主版来自 Claude 通道时，同一个会话写完中文版后接着写英文版，不交给 API 通道。主版来自 API 通道时，由成为主版的那个模型多发一次请求写英文版（2026-10-28 补）。英文版是正式内容，质量应当和主版对齐；它沿用主版的条目和 evidence，只多出写作这一步，额度增加有限。

通道表（2026-11-06 补，#35）：每条通道的属性集中写在 `daily/routes.py` 的通道表里：digest 的 `channel`、它写的 `mode`、优先级、同一通道更新的稿子能不能替换旧稿、是否每个模型各一份 Beta 版、有没有生成记录、Beta 版的标签。主版的选择、validate、生成记录和 Beta 版的文件名、网站和「生成过程」页都查这张表，加一条通道只需加一行。降级版也在表里占一行，优先级最低，这样主版的排序规则只有一套。`channel` 改为必填：没写或不在表里的 digest 不合格，不再默认当作 Claude 通道。之前没有 `channel` 的历史日报已一次性补上。

ingest 挪进 Python（2026-11-06 补，#35）：两条通道把稿子交给 main 的方式不同，规则都在 `daily/ingest.py` 和 `daily.publish`。Claude 通道推到 `claude/` 分支，`daily ingest --ref` 取这次提交改过的 digest 和生成记录；分支上只收按 SKILL.md 编辑的通道（及其放弃时写的降级版），API 通道的稿子不从分支进来。API 通道由 `daily edit --out` 跑完所有模型，`publish.main_of` 判断哪一份会成为主版并由它写英文版，`daily ingest --from-dir` 按 `run.json` 里的优先级顺序并入。`claude/` 这个分支前缀是 Claude 云端会话的限制（它只能推到自己的 `claude/` 分支），不是通道的属性，所以不进通道表，`ingest.yml` 的触发条件和 `prune-branches.yml` 照旧写死它。
