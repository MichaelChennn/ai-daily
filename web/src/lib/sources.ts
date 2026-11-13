// web/data/sources.json (the English site's in web/data/en/), written by `python -m daily export`.
import sourcesEn from "../../data/en/sources.json"
import sourcesZh from "../../data/sources.json"
import type { Lang } from "./i18n"

export type Source = {
  id: string
  name: string
  kind: string
  homepage: string | null
  icon: string | null
  enabled: boolean
  repos: string[]
  stats: { ok: number; runs: number; picked: number; candidates: number } | null
}

export type SourceGroup = { label: string; sources: Source[] }

export type SourcesData = { runs: number; groups: SourceGroup[] }

export const sourcesIn = (lang: Lang): SourcesData => (lang === "en" ? sourcesEn : sourcesZh)

/** A source's kind as its group shows it: "官方博客 · RSS" is just "RSS" when every source in the
 * group starts with "官方博客", which the group's heading already says. */
export function kindIn(group: SourceGroup): (kind: string) => string {
  const heads = new Set(group.sources.map((s) => s.kind.split(" · ")[0]))
  return heads.size === 1 ? (kind) => kind.split(" · ").slice(1).join(" · ") || kind : (kind) => kind
}
