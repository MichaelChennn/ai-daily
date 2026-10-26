# 两条编辑通道并行，按优先级选主版

除了 Claude Code 定时会话（Claude 通道），我们在 GitHub Actions 里加了一条调用免费云端模型 API 的 API 通道，两条每天都跑。主版的优先级是 Claude 通道 > API 通道 > 降级版，API 通道的结果另外作为 Beta 版展示。Claude 通道目前质量稳定，所以继续做主版；API 通道不需要在 claude.ai 上维护定时任务，可以用免费额度，Claude 失败时它来顶上，降级版就很少出现了。没有选“用一个开关二选一”，因为两份并排放着，才能持续比较 API 通道的质量。
