// The two editions of the site: Chinese at the root, English under en/ with the same pages.
// Everything a page says that is not issue data comes from here.

export type Lang = "zh" | "en"

const WEEKDAYS_ZH = "日一二三四五六"
const WEEKDAYS_EN = "Sun Mon Tue Wed Thu Fri Sat".split(" ")
const pad = (n: number) => String(n).padStart(2, "0")
const MONTHS_EN = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" ")
const MONTH_NAMES_EN =
  "January February March April May June July August September October November December".split(" ")

export const strings = {
  zh: {
    siteTitle: "AI 晨报",
    nav: { today: "今日日报", archive: "往期归档", sources: "信息源" },
    github: "GitHub 上的源代码",
    beta: "Beta 版",
    backToMain: "回到正式版",
    theme: "切换日间 / 夜间模式",
    language: "切换语言",
    issues: "切换期数",
    noIssue: "这一天没有日报",
    older: "上一期",
    newer: "下一期",
    pager: "翻页",
    filter: "按分类筛选",
    betaModels: "切换 Beta 版本",
    count: (n: number) => `${n} 条`,
    moreSources: "+{n} 更多来源",
    localTime: "柏林时间",
    fallbackTitle: "（降级版）",
    description: (date: string) => `${date} 的 AI 晨报。`,
    credit: (editor: string | null, fallback: boolean) => (fallback ? "本期降级版，未经编辑" : `本期由 ${editor} 编辑`),
    schedule: "每天柏林时间 06:00 更新",
    rss: "RSS 订阅",
    license: "内容采用 CC BY-NC 4.0 许可",
    licenseUrl: "https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans",
    feed: "feed.xml",
    empty: "还没有发布任何一期",
    notFound: "页面不存在",
    notFoundHint: "链接可能写错了，或者这一页已经移走。",
    archive: {
      description: (site: string) => `${site}的全部往期，按月份浏览。`,
    },
    sources: {
      description: (site: string) => `${site}抓取的信息源白名单，和每个源的抓取与入选统计。`,
      groups: "按分组跳转",
      runs: (n: number) => `统计最近 ${n} 期`,
      disabled: "已停用",
      ok: "抓取成功",
      candidates: "平均候选",
      picked: "入选条目",
      neverFetched: "还没有抓取记录",
      notFetched: "暂不抓取",
      repos: (n: number) => `${n} 个仓库`,
    },
    // The issue pages (issue #43 design): the timeline on the left, the cards, the footer.
    press: {
      rail: "日报时间轴",
      latest: "回到最新一期",
      months: "按月份跳转",
      back: "回到日报",
      month: (year: number, month: number) => `${year}年${month}月`,
      archive: "归档",
      sources: "信源",
      noIssue: "这天没有日报",
      tickDay: (day: Date) => `${pad(day.getUTCMonth() + 1)}.${pad(day.getUTCDate())} 周${WEEKDAYS_ZH[day.getUTCDay()]}`,
      allSources: (n: number) => `全部 ${n} 个来源`,
      original: "原文",
      discussion: "讨论",
      process: "生成过程",
      main: "正式版",
      edition: (label: string) => `${label} 版`,
      theme: "切换日间/夜间",
      languages: "Switch to English",
      github: "GitHub",
    },
    day: (date: Date) => ({
      year: date.getUTCFullYear(),
      monthDay: `${date.getUTCMonth() + 1}月${date.getUTCDate()}日`,
      weekday: `周${WEEKDAYS_ZH[date.getUTCDay()]}`,
    }),
  },
  en: {
    siteTitle: "AI Daily",
    nav: { today: "Today", archive: "Archive", sources: "Sources" },
    github: "Source code on GitHub",
    beta: "Beta",
    backToMain: "Back to the main edition",
    theme: "Toggle light / dark mode",
    language: "Language",
    issues: "Issues",
    noIssue: "No issue this day",
    older: "Previous",
    newer: "Next",
    pager: "Pages",
    filter: "Filter by section",
    betaModels: "Beta editions",
    count: (n: number) => `${n} ${n === 1 ? "item" : "items"}`,
    moreSources: "+{n} more",
    localTime: "Berlin time",
    fallbackTitle: " (fallback)",
    description: (date: string) => `AI Daily for ${date}.`,
    // An issue without its English edition yet has neither an editor nor a fallback.
    credit: (editor: string | null, fallback: boolean) =>
      fallback ? "Fallback edition, unedited" : editor ? `Edited by ${editor}` : "Original titles only",
    schedule: "Updated daily at 06:00 Berlin time",
    rss: "RSS",
    license: "Content licensed under CC BY-NC 4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-nc/4.0/",
    feed: "feed.en.xml",
    empty: "No issues published yet",
    notFound: "Page not found",
    notFoundHint: "The link may be mistyped, or the page has moved.",
    archive: {
      description: (site: string) => `Every issue of ${site}, by month.`,
    },
    sources: {
      description: (site: string) => `The sources ${site} fetches, with fetch and pick stats for each.`,
      groups: "Jump to a group",
      runs: (n: number) => `Stats over the last ${n} issues`,
      disabled: "Paused",
      ok: "Fetched",
      candidates: "Avg. candidates",
      picked: "Picked",
      neverFetched: "Not fetched yet",
      notFetched: "Not fetched",
      repos: (n: number) => `${n} ${n === 1 ? "repo" : "repos"}`,
    },
    press: {
      rail: "Issue timeline",
      latest: "Back to the latest issue",
      months: "Jump to a month",
      back: "Back to reading",
      month: (year: number, month: number) => `${MONTH_NAMES_EN[month - 1]} ${year}`,
      archive: "Archive",
      sources: "Sources",
      noIssue: "No issue this day",
      tickDay: (day: Date) => `${pad(day.getUTCMonth() + 1)}.${pad(day.getUTCDate())} ${WEEKDAYS_EN[day.getUTCDay()]}`,
      allSources: (n: number) => `All ${n} sources`,
      original: "Original",
      discussion: "Discussion",
      process: "How it was made",
      main: "Main edition",
      edition: (label: string) => `${label} edition`,
      theme: "Toggle light / dark",
      languages: "切换到中文版",
      github: "GitHub",
    },
    day: (date: Date) => ({
      year: date.getUTCFullYear(),
      monthDay: `${MONTHS_EN[date.getUTCMonth()]} ${date.getUTCDate()}`,
      weekday: WEEKDAYS_EN[date.getUTCDay()],
    }),
  },
} satisfies Record<Lang, unknown>

export type Strings = (typeof strings)[Lang]

/** The language of the page being rendered, from Astro.currentLocale. */
export const langOf = (locale: string | undefined): Lang => (locale === "en" ? "en" : "zh")
