# ai-daily

- 术语（期、信源、候选、条目、主版……）：[GLOSSARY.md](GLOSSARY.md)
- 每日时间表、各 workflow 的分工、发布顺序：[docs/operations.md](docs/operations.md)
- 抓取、去重、质量闸门：[docs/pipeline.md](docs/pipeline.md)
- 命令：[docs/cli.md](docs/cli.md)；两条编辑通道的取舍：[docs/adr/](docs/adr/)
- 网页样式（#43 新风格的 token、组件、动效）：[docs/design-system.md](docs/design-system.md)；数值以 `web/src/styles/press.css` 为准，两边一起改
- 架构图、流程图：由 `docs/diagrams/gen_*.py` 生成；改图时改脚本，不要手改 HTML

CLI 的命令与参数、`data/` 下的文件格式由 workflow、daily-editor skill 和网站共用。改动前先跟用户确认。

提交前跑一次 `pre-commit install`，之后每次提交都会跑 ruff 和 pytest，与 CI 一致。
