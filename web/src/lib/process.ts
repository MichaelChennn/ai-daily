import { pageHref } from "@/lib/issues"

// How each issue was made, for its 生成过程 page: web/data/process/*.json, written by
// `python -m daily export` (daily/process.py documents the fields).

export type Cell = {
  state: "unpicked" | "dropped" | "published"
  /** The step that dropped it, or kept it out. */
  step: string | null
  reasons: string[]
  /** [重要性, 实用性, 新颖性], null where the route did not score. */
  score: [number, number, number] | null
  total: number | null
}

export type Row = {
  id: string
  title: string
  url: string
  source: string
  kind: string
  cells: Record<string, Cell>
  differs: boolean
  dropped: boolean
  high_unpicked: boolean
}

export type Passed = { title: string; candidates: string[] }

export type Dropped = { title: string; candidates: string[]; reasons: string[] }

export type Step = {
  step: string
  label: string
  at: string | null
  kept?: number | null
  /** The items that passed this round, with the candidates each was written from. */
  passed?: Passed[]
  /** The 日报简介 (digest highlights) sentences with words no passing item has; text null when the sentence is unknown. */
  highlights?: { text: string | null; missing: string[] }[]
  dropped?: Dropped[]
  errors?: string[]
  groups?: string[][]
  candidates?: string[]
  error?: string
}

export type Adopt = { at: string; edition: "zh" | "en"; run: string; adopted: boolean; reason: string }

export type Channel = {
  id: string
  label: string
  model: string | null
  main: boolean
  recorded: boolean
  scored: boolean
  failure: { step: string; label: string; error: string } | null
  funnel: { label: string; value: number }[]
  steps: Step[]
  adopt: Adopt[]
}

export type Process = {
  date: string
  main: string | null
  funnel: {
    filtered: number | null
    raw: number | null
    after_url_merge: number | null
    already_published: number | null
    candidates: number | null
  }
  sources: {
    id: string
    name: string
    status: string | null
    count: number | null
    error: string | null
    filtered: Record<string, number> | null
  }[]
  filtered: { source: string; name: string; items: { title: string; url: string; reason: string; value: unknown }[] }[] | null
  channels: Channel[]
  rows: Row[]
}

const files = import.meta.glob<Process>("../../data/process/*.json", { eager: true, import: "default" })

/** Every issue's process, newest first. */
export const processes: Process[] = Object.values(files).sort((a, b) => b.date.localeCompare(a.date))

export const processHref = (day: string) => pageHref(`${day}/process/`)

// validate's messages (daily/digest.py), in Chinese. One it does not know stays as written.
const REASONS: [RegExp, (...m: string[]) => string][] = [
  [/^evidence quote must be 1-\d+ characters$/, () => "缺少原文引文"],
  [/^evidence quote not found on (\S+): (.*)$/, (_url, quote) => `引文在原文里找不到：${quote}`],
  [/^'(.+)' does not appear in the (?:cited material|published items)$/, (token) => `「${token}」在原文里找不到`],
  [/^number (.+) does not appear in the (?:cited material|published items)$/, (n) => `数字 ${n} 在原文里找不到`],
  [/^summary longer than (\d+) characters$/, (n) => `摘要超过 ${n} 字`],
  [/^title longer than (\d+) characters$/, (n) => `标题超过 ${n} 字`],
  [/^summary is empty$/, () => "摘要为空"],
  [/^title is empty$/, () => "标题为空"],
  [/^unknown candidate_id (.+)$/, (id) => `候选 ${id} 不存在`],
  [/^sources must be a non-empty list$/, () => "没有来源"],
  [/^the paper section needs a paper as its main source, not (\S+)$/, () => "论文版块的主来源不是论文"],
  [/^a commentary item belongs in the brief section, not (\S+)$/, () => "博主和周报文章只能放进快讯"],
  [/^at most (\d+) commentary items per issue$/, (n) => `博主和周报文章每期最多 ${n} 条`],
  [/^only (\d+) valid items \(minimum (\d+)\)$/, (n, min) => `只有 ${n} 条有效条目，至少要 ${min} 条`],
  [/^highlights must have 1-(\d+) sentences$/, (n) => `日报简介的句数不对：只能写 1–${n} 句`],
  [/^highlight: (.+)$/, (rest) => `日报简介里：${reasonZh(rest)}`],
]

export function reasonZh(reason: string): string {
  for (const [pattern, say] of REASONS) {
    const m = reason.match(pattern)
    if (m) return say(...m.slice(1))
  }
  return reason
}
