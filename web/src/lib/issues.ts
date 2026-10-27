import { getRelativeLocaleUrl } from "astro:i18n"

import { type Lang, strings } from "@/lib/i18n"

// The issues written by `python -m daily export` (web/data/issues/*.json, the English site's in
// web/data/en/issues/). Only issues that pass
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

/** An API route edition shown beside the main issue, at YYYY-MM-DD/beta/<slug>/. */
export type Beta = { slug: string; label: string }

export type Issue = {
  date: string
  fallback: boolean
  notice: string | null
  description: string
  /** Who edited it: "Claude" or the API route's model; null for a fallback. */
  editor: string | null
  betas: Beta[]
  /** Set on a beta's own page. */
  beta: Beta | null
  sections: Section[]
}

const files = import.meta.glob<Issue>("../../data/issues/*.json", {
  eager: true,
  import: "default",
})
const enFiles = import.meta.glob<Issue>("../../data/en/issues/*.json", {
  eager: true,
  import: "default",
})
const betaFiles = import.meta.glob<Issue>("../../data/beta/*/*.json", {
  eager: true,
  import: "default",
})

/** Every published issue, newest first. */
export const issues: Issue[] = Object.values(files).sort((a, b) => b.date.localeCompare(a.date))

/** The English site's issues, newest first: the same dates as `issues`. */
export const enIssues: Issue[] = Object.values(enFiles).sort((a, b) => b.date.localeCompare(a.date))

export const issuesIn = (lang: Lang) => (lang === "en" ? enIssues : issues)

/** Every beta page. */
export const betas: Issue[] = Object.values(betaFiles)

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

export function formatDay(day: string, lang: Lang = "zh") {
  return strings[lang].day(parse(day))
}

/** A file under the site's base URL, such as "feed.xml". */
export function href(path: string): string {
  const base = import.meta.env.BASE_URL
  return (base.endsWith("/") ? base : `${base}/`) + path
}

/** A page in one language ("" is the home page): "archive/" is en/archive/ on the English site. */
export const pageHref = (path: string, lang: Lang = "zh") => getRelativeLocaleUrl(lang, path)

export const issueHref = (day: string, lang: Lang = "zh") => pageHref(`${day}/`, lang)

export const betaHref = (day: string, slug: string) => pageHref(`${day}/beta/${slug}/`)

/** The page at `pathname` without the base and the language: "archive/", "" for the home page.
 * The 404 page, served at any missing path, counts as the home page. */
export function pagePath(pathname: string, lang: Lang): string {
  const home = pageHref("", lang)
  const page = pathname.startsWith(home) ? pathname.slice(home.length) : ""
  return /^404\b/.test(page) ? "" : page
}

export const SITE_TITLE = strings.zh.siteTitle
export const REPO_URL = "https://github.com/MichaelChennn/ai-daily"
