// The issues written by `python -m daily export` (web/data/issues/*.json). Only issues that pass
// the Python validate gate are there; this side just lays them out.

export type Source = { label: string; url: string; discussion: boolean }

export type Item = {
  title: string
  summary: string
  compact: boolean
  publisher: { name: string; icon: string; host: string }
  published: { iso: string; label: string } | null
  sources: Source[]
}

export type Section = { id: string; label: string; items: Item[] }

export type Issue = {
  date: string
  fallback: boolean
  notice: string | null
  description: string
  sections: Section[]
}

const files = import.meta.glob<Issue>("../../data/issues/*.json", { eager: true, import: "default" })

/** Every published issue, newest first. */
export const issues: Issue[] = Object.values(files).sort((a, b) => b.date.localeCompare(a.date))

const WEEKDAYS = "日一二三四五六"

function parse(day: string): Date {
  const [y, m, d] = day.split("-").map(Number)
  return new Date(Date.UTC(y, m - 1, d))
}

/** YYYY-MM-DD, `offset` days from `day`. */
export function addDays(day: string, offset: number): string {
  const date = parse(day)
  date.setUTCDate(date.getUTCDate() + offset)
  return date.toISOString().slice(0, 10)
}

export function formatDay(day: string) {
  const date = parse(day)
  return {
    year: date.getUTCFullYear(),
    monthDay: `${date.getUTCMonth() + 1}月${date.getUTCDate()}日`,
    weekday: `周${WEEKDAYS[date.getUTCDay()]}`,
  }
}

/** A path under the site's base URL ("" is the home page). */
export function href(path: string): string {
  const base = import.meta.env.BASE_URL
  return (base.endsWith("/") ? base : `${base}/`) + path
}

export const issueHref = (day: string) => href(`${day}/`)

export const SITE_TITLE = "AI 科技日报"
export const REPO_URL = "https://github.com/MichaelChennn/ai-daily"
