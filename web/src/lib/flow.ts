// The 生成过程 page's flow chart (issue #63): one issue's process (process.ts) as the steps the
// page draws, from the sources to the editions it published. The page only lays these out; every
// count and every line of copy is decided here, in Chinese or English (the copy at the end).
//
// The shared line: 信息来源 → 过滤 → 合并重复网址 → 去掉已发布. Then one lane per editor route,
// each step in the order its trace has them, then 选定正式版 and one end card per edition.
// A route without a trace keeps only its digest's last validation; the steps before it are drawn
// dashed and marked 当时未记录. A route that failed stops at the failed step.

import type { Lang } from "@/lib/i18n"
import { betaHref, betas, enIssues, issueHref } from "@/lib/issues"
import { editionLogo, modelName } from "@/lib/models"
import type { Channel, Process, Row, Step } from "@/lib/process"
import { reasonZh } from "@/lib/process"

/** One row of an opened list: a title, and under it why (a link when `href`). */
export type ListItem = { title: string; why?: string; href?: string; source?: string; group?: string }

/** 「N 条被过滤 ›」: what a step removed. With items it opens to the list; without, a plain pill. */
export type Cut = { label: string; items?: ListItem[]; groups?: string; note?: string }

export type FlowNode = {
  id: string
  name: string
  /** Berlin time, HH:MM. */
  at?: string
  /** 「255 条 → 145 条」, 「17 条」 or 「当时未记录」. */
  num?: string
  /** The step's rule in plain words; may hold <br> and the link to the table. */
  rule?: string
  cuts: Cut[]
  /** A state pill that does not open: 「全部通过」. */
  flat?: string
  /** Not recorded at the time: its lines are dashed. */
  unrecorded?: boolean
  /** The route failed here: the line ends at this step. */
  failed?: boolean
}

export type Lane = {
  slug: string
  main: boolean
  logo: string | null
  initial: string
  model: string
  how: string
  nodes: FlowNode[]
  failed: boolean
}

export type End = { slug: string; href: string; hreflang?: string; logo: string | null; initial: string; title: string; sub: string }

export type Flow = {
  source: { href: string; num: string; cuts: Cut[] }
  spine: FlowNode[]
  lanes: Lane[]
  adopt: { rule: string; story: { at: string; text: string }[] }
  ends: End[]
  matrix: Matrix
  /** The page's own words. */
  t: Copy["page"]
}

export type Mark = { state: Row["cells"][string]["state"]; total: number | null } | null
export type MatrixRow = {
  title: string
  url: string
  source: string
  filters: string[]
  marks: Mark[]
  details: { logo: string | null; initial: string; head: string; scores: number[] | null }[]
}
export type Matrix = {
  channels: { label: string; logo: string | null; initial: string }[]
  filters: { key: string; label: string; count: number; on: boolean }[]
  rows: MatrixRow[]
}

const BERLIN = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Berlin", hour: "2-digit", minute: "2-digit", hourCycle: "h23" })
export const hm = (iso: string | null | undefined) => (iso ? BERLIN.format(new Date(iso)) : "")

const slugOf = (c: Channel) => (c.id.startsWith("api.") ? c.id.slice("api.".length) : c.id)
const logoOf = (c: Channel) => editionLogo(c.id === "claude" ? "main" : slugOf(c))
const initialOf = (c: Channel) => c.label.charAt(0)
const modelOf = (c: Channel) => (c.model ? modelName(c.model.replace(/^\w+:/, "")) : c.label)
const HOW: [RegExp, string][] = [
  [/^nvidia:/, "NVIDIA NIM API"],
  [/^gemini:/, "Gemini API"],
]
const howOf = (c: Channel) => (c.id === "claude" ? "Claude Schedule Task" : (HOW.find(([re]) => re.test(c.model ?? ""))?.[1] ?? ""))

export function buildFlow(p: Process, lang: Lang = "zh"): Flow {
  const t = COPY[lang]
  const f = p.funnel
  const fetched = f.raw != null && f.filtered != null ? f.raw + f.filtered : null
  const rows = new Map(p.rows.map((r) => [r.id, r]))

  const failedSources = p.sources.filter((s) => s.status && s.status !== "ok")
  const source = {
    href: "sources/",
    num: t.sources(p.sources.length, fetched),
    cuts: failedSources.length
      ? [{ label: t.sourcesFailed(failedSources.length), items: failedSources.map((s) => ({ title: s.name, why: t.fetchError(s.error) })) }]
      : [],
  }

  const filtered = (p.filtered ?? []).flatMap((g) =>
    g.items.map((it) => ({ title: it.title, why: t.filterReason(it.reason), source: g.name, group: t.filterReason(it.reason) })),
  )
  const old = [...p.already_published]
    .sort((a, b) => b.published_on.localeCompare(a.published_on))
    .map((d) => ({
      title: d.title,
      why: t.coveredOn(d.published_on),
      href: issueHref(d.published_on, lang),
      group: t.issueChip(d.published_on),
    }))
  const merged = f.raw != null && f.after_url_merge != null ? f.raw - f.after_url_merge : 0
  const spine: FlowNode[] = [
    {
      id: "f1",
      name: t.f1.name,
      num: f.raw == null ? t.unrecorded : t.count(fetched, f.raw, "c"),
      rule: t.f1.rule,
      cuts:
        f.filtered == null
          ? []
          : f.filtered
            ? [{ label: t.f1.cut(f.filtered), items: filtered, groups: t.f1.groups, note: t.f1.note }]
            : [],
      flat: f.filtered == null ? t.f1.unrecorded : undefined,
      unrecorded: f.filtered == null,
    },
    {
      id: "f2",
      name: t.f2.name,
      num: f.after_url_merge == null ? t.unrecorded : t.count(f.raw, f.after_url_merge, "c"),
      rule: t.f2.rule,
      cuts: merged ? [{ label: t.f2.cut(merged) }] : [],
    },
    {
      id: "f3",
      name: t.f3.name,
      num: f.candidates == null ? t.unrecorded : t.count(f.after_url_merge, f.candidates, "c"),
      rule: t.f3.rule,
      cuts: f.already_published
        ? [
            {
              label: t.f3.cut(f.already_published),
              items: old.length === f.already_published ? old : undefined,
              groups: t.f3.groups,
            },
          ]
        : [],
    },
  ]

  const chans = [...p.channels].sort((a, b) => Number(b.main) - Number(a.main))
  const lanes = chans.map((c) => lane(c, p, rows, t))

  // the editions this issue published: the main one, then each route's Beta page (Chinese only)
  const betaOf = (c: Channel) => betas.some((b) => b.date === p.date && b.beta?.slug === slugOf(c))
  const published = (c: Channel) => c.funnel.find((s) => s.label === "发布")?.value ?? 0
  const main = chans.find((c) => c.main)
  const beta = chans.filter((c) => !c.main && betaOf(c))
  const failed = chans.filter((c) => c.failure)
  const unpublished = chans.filter((c) => !c.main && !c.failure && !betaOf(c))
  const rule = [
    !main
      ? t.adopt.none
      : chans.length === 1
        ? t.adopt.one(main.label)
        : t.adopt.many(
            chans.length,
            main.label,
            beta.map((c) => c.label),
          ),
    failed.length ? t.adopt.failed(failed.map((c) => c.label)) : "",
    unpublished.length ? t.adopt.unpublished(unpublished.map((c) => c.label)) : "",
  ]
    .filter(Boolean)
    .join("<br>")
  // which route became the main edition is decided on the Chinese edition; the English one follows
  const story = chans
    .flatMap((c) => c.adopt.filter((a) => a.edition === "zh").map((a) => ({ a, c })))
    .sort((x, y) => x.a.at.localeCompare(y.a.at))
    .map(({ a, c }) => ({
      at: hm(a.at),
      text: t.story(c.label, c.main ? "main" : a.adopted ? "first" : betaOf(c) ? "beta" : "unpublished"),
    }))

  // the English main edition can have fewer items: its own check removes some
  const enIssue = enIssues.find((i) => i.date === p.date)
  const mainCount = !main ? null : lang === "en" && enIssue ? enIssue.sections.reduce((n, s) => n + s.items.length, 0) : published(main)
  const ends: End[] = [
    ...(main || p.main === "fallback"
      ? [
          {
            slug: "main",
            href: issueHref(p.date, lang),
            logo: main ? logoOf(main) : null,
            initial: main ? initialOf(main) : t.ends.fallbackInitial,
            title: main ? t.ends.main : t.ends.fallback,
            sub: t.ends.mainSub(mainCount),
          },
        ]
      : []),
    ...beta.map((c) => ({
      slug: slugOf(c),
      href: betaHref(p.date, slugOf(c)),
      hreflang: lang === "zh" ? undefined : "zh",
      logo: logoOf(c),
      initial: initialOf(c),
      title: t.edition(c.label),
      sub: t.ends.betaSub(published(c)),
    })),
  ]

  return { source, spine, lanes, adopt: { rule, story }, ends, matrix: matrix(p, chans, t), t: t.page }
}

// One route's steps. MiniMax and the other API routes: 去掉无官方来源的 → 打分、挑选 → 写稿 →
// 预检 (its draft round) → 预检修改 → 正式校验 (its fix round) → 写英文版. Claude: 打分、挑选 →
// 写稿 → 自检 → 预检 → 预检修改 → 正式校验 → 写英文版. Each check round starts from the count
// its trace says it was handed, not from the step before.
function lane(c: Channel, p: Process, rows: Map<string, Row>, t: Copy): Lane {
  const slug = slugOf(c)
  const api = c.id !== "claude"
  const nodes: FlowNode[] = []
  const id = () => `${slug}-${nodes.length + 1}`
  const steps = c.steps
  const cell = (cid: string) => rows.get(cid)?.cells[c.id]
  const row = (cid: string) => rows.get(cid)

  const out: Lane = {
    slug,
    main: c.main,
    logo: logoOf(c),
    initial: initialOf(c),
    model: modelOf(c),
    how: howOf(c),
    nodes,
    failed: !!c.failure,
  }

  if (!c.recorded) {
    nodes.push({ id: id(), name: t.lane.unrecorded, num: t.unrecorded, cuts: [], unrecorded: true })
  }

  let pool = p.rows.map((r) => r.id)
  const gone = steps.find((s) => s.step === "no_first_hand")
  if (gone) {
    const dropped = new Set(gone.candidates ?? [])
    const before = pool.length
    pool = pool.filter((i) => !dropped.has(i))
    nodes.push({
      id: id(),
      name: t.lane.firstHand.name,
      at: hm(gone.at),
      num: t.count(before, pool.length, "c"),
      rule: t.lane.firstHand.rule,
      cuts: dropped.size
        ? [
            {
              label: t.lane.firstHand.cut(dropped.size),
              items: [...dropped].filter((i) => rows.has(i)).map((i) => ({ title: row(i)!.title, source: row(i)!.source })),
            },
          ]
        : [],
    })
  }

  const fail = (name: string) => {
    nodes.push({ id: id(), name, num: t.lane.failed, rule: t.lane.stops(t.failure(c.failure!.error)), cuts: [], failed: true })
    return out
  }
  if (c.failure?.step === "pick") return fail(t.lane.pick.name)

  const pick = steps.find((s) => s.step === "pick")
  const rounds = steps.filter((s) => s.fed != null)
  const selfChecks = steps.filter((s) => s.step === "self_check")
  if (c.recorded && (pick || !api)) {
    const picked = pool.filter((i) => cell(i)?.state !== "unpicked")
    const unpicked = [...pool]
      .filter((i) => !picked.includes(i))
      .sort((a, b) => (cell(b)?.total ?? 0) - (cell(a)?.total ?? 0))
      .map((i) => {
        const total = cell(i)?.total
        return { title: row(i)!.title, why: total != null ? t.points(total) : undefined, source: row(i)!.source }
      })
    nodes.push({
      id: id(),
      name: t.lane.pick.name,
      at: hm(gone ? pick?.at : (c.started_at ?? pick?.at)),
      num: t.count(pool.length, picked.length, "c"),
      rule: t.lane.pick.rule(pick?.kept && pick.kept !== picked.length ? pick.kept : null),
      cuts: unpicked.length ? [{ label: t.lane.pick.cut(unpicked.length), items: unpicked }] : [],
    })

    if (c.failure?.step === "draft" || c.failure?.step === "read") return fail(t.lane.write.name)
    const first = rounds[0]
    // what was written: the first check round's items, plus what a self-check took out before it
    const before = selfChecks.filter((s) => !first || steps.indexOf(s) < steps.indexOf(first))
    const writtenCount = (first?.fed ?? 0) + before.reduce((n, s) => n + (s.dropped?.length ?? 0), 0)
    const over = steps.find((s) => s.step === "over_picks")
    nodes.push({
      id: id(),
      name: t.lane.write.name,
      num: t.count(picked.length, writtenCount, "i"),
      rule: api ? t.lane.write.api : t.lane.write.claude,
      cuts: over?.groups?.length ? [{ label: t.lane.write.over(over.groups.length) }] : [],
    })
    checks(c, steps, writtenCount, nodes, id, api, t)
  } else {
    checks(c, steps, null, nodes, id, api, t)
  }
  if (c.failure && !nodes.at(-1)?.failed) {
    const names: Record<string, string> = { fix: t.check.fix.name, en: t.check.en.name, en_highlights: t.check.en.name }
    return fail(names[c.failure.step] ?? t.stepLabel(c.failure.label))
  }
  return out
}

// The check rounds, in the order they ran. 预检 (Claude's precheck, an API route's draft round)
// only reports; 预检修改 shows only when it found something; 正式校验 (final, or the fix round)
// deletes what still fails. English rounds do not change the Chinese count.
function checks(c: Channel, steps: Step[], start: number | null, nodes: FlowNode[], id: () => string, api: boolean, t: Copy) {
  const k = t.check
  let prev = start
  let pre: Step | null = null
  let selfChecks = 0
  const drops = (s: Step) => (s.dropped ?? []).map((d) => ({ title: d.title, why: t.reasons(d.reasons) || undefined }))
  for (const s of steps) {
    const d = drops(s)
    const flat = d.length ? undefined : k.passed
    const at = hm(s.at)
    switch (s.step) {
      case "self_check": {
        const n = prev == null ? null : prev - d.length
        nodes.push({
          id: id(),
          name: selfChecks++ ? k.self.again : k.self.name,
          at,
          num: n == null ? undefined : t.count(prev, n, "i"),
          rule: k.self.rule,
          cuts: d.length ? [{ label: k.self.cut(d.length), items: d }] : [],
          flat,
        })
        prev = n
        break
      }
      case "precheck":
      case "draft":
        pre = s
        nodes.push({
          id: id(),
          name: k.pre.name,
          at,
          num: t.count(null, s.fed!, "i"),
          rule: s.step === "draft" ? k.pre.draft : k.pre.rule,
          cuts: d.length ? [{ label: k.pre.cut(d.length), items: d }] : [],
          flat,
        })
        prev = s.fed
        break
      case "final":
      case "fix": {
        if (pre?.dropped?.length && c.recorded) {
          nodes.push({
            id: id(),
            name: k.fix.name,
            num: t.count(prev, s.fed!, "i"),
            rule: api ? k.fix.api : k.fix.claude,
            cuts: [],
          })
        }
        const kept = s.kept ?? s.fed! - d.length
        nodes.push({
          id: id(),
          name: k.final.name,
          at,
          num: t.count(s.fed, kept, "i"),
          rule: k.final.rule,
          cuts: d.length ? [{ label: k.final.cut(d.length), items: d }] : [],
          flat,
        })
        prev = kept
        break
      }
      // The same draft checked again once its 日报简介 was rewritten from the titles: part of the
      // step before, which now shows this round's result.
      case "highlights":
      case "en_highlights": {
        const last = nodes.at(-1)
        if (!last) break
        const kept = s.kept ?? s.fed! - d.length
        last.num = t.count(s.fed, kept, "i")
        last.rule += `<br>${k.highlights}`
        last.cuts = d.length ? [{ label: (s.step === "en_highlights" ? k.en.cut : k.final.cut)(d.length), items: d }] : []
        last.flat = flat
        if (s.step === "highlights") prev = kept
        break
      }
      case "en": {
        const kept = s.kept ?? s.fed! - d.length
        nodes.push({
          id: id(),
          name: k.en.name,
          at,
          num: t.count(s.fed, kept, "i"),
          // only the main edition is published in English: say so on the other routes
          rule: c.main ? k.en.rule : `${k.en.rule}<br>${k.en.notMain(!!c.adopt.find((a) => a.edition === "en")?.adopted)}`,
          cuts: d.length ? [{ label: k.en.cut(d.length), items: d }] : [],
          flat,
        })
        break
      }
    }
  }
}

function matrix(p: Process, chans: Channel[], t: Copy): Matrix {
  const m = t.matrix
  const tests: [string, string, (r: Row) => boolean][] = [
    ...(chans.length > 1 ? ([["differs", m.differs, (r: Row) => r.differs]] as [string, string, (r: Row) => boolean][]) : []),
    ["dropped", m.dropped, (r) => r.dropped],
    ["high", m.high, (r) => r.high_unpicked],
    ["all", m.all, () => true],
  ]
  const sortKey = (r: Row) => {
    const cs = Object.values(r.cells)
    return [-cs.filter((c) => c.state === "published").length, -Math.max(0, ...cs.map((c) => c.total ?? 0))]
  }
  const rows = [...p.rows].sort((a, b) => {
    const [x, y] = [sortKey(a), sortKey(b)]
    return x[0] - y[0] || x[1] - y[1]
  })
  const first = tests[0][0]
  return {
    channels: chans.map((c) => ({ label: c.label, logo: logoOf(c), initial: initialOf(c) })),
    filters: tests.map(([key, label, test]) => ({ key, label, count: p.rows.filter(test).length, on: key === first })),
    rows: rows.map((r) => ({
      title: r.title,
      url: r.url,
      source: r.source,
      filters: tests.filter(([, , test]) => test(r)).map(([key]) => key),
      marks: chans.map((c) => {
        const cell = r.cells[c.id]
        return cell ? { state: cell.state, total: cell.total } : null
      }),
      details: chans.flatMap((c) => {
        const cell = r.cells[c.id]
        if (!cell) return []
        const head = m.head(c.label, m.state[cell.state], cell.step ? t.stepLabel(cell.step) : null, t.reasons(cell.reasons))
        return [{ logo: logoOf(c), initial: initialOf(c), head, scores: cell.score }]
      }),
    })),
  }
}

// ---------------------------------------------------------------------------------------------
// The copy. Chinese from the 2026-11-15 grilling (memory process-flow-63), English agreed on
// 2026-11-16. In English the counts name what they count: candidates before writing, items after.

type Unit = "c" | "i"
type Fate = "main" | "first" | "beta" | "unpublished"

// The step labels process.json keeps in Chinese (a cell's step, a failure's label), named as the
// flow chart names its steps. The English keys are without punctuation.
const STEP_ZH: Record<string, string> = { 第一稿校验: "预检", 修改稿校验: "正式校验" }
const STEP_EN: Record<string, string> = {
  无一手来源预先去掉: "Dropped beforehand: no first-hand source",
  挑选: "Pick",
  第一稿校验: "Precheck",
  预检: "Precheck",
  修改稿校验: "Final check",
  正式校验: "Final check",
  自检: "Self-check",
  超出挑选上限截掉: "Over the pick limit, cut",
  未发布: "Not published",
}
// the fetchers' filter reasons (candidates.json), also kept in Chinese
const FILTER_EN: Record<string, string> = {
  "与 AI 无关": "Not about AI",
  点赞不够: "Too few upvotes",
  衍生权重: "Derived model weights",
  模型发布太久: "Model released too long ago",
  标题命中排除规则: "Title matches an exclude rule",
  "今日 star 不够": "Too few stars today",
}

const NUMERALS = ["零", "一", "两", "三", "四", "五", "六"]
const WORDS = ["zero", "one", "two", "three", "four", "five", "six"]
const MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" ")
/** 1 item, 2 items. */
const nOf = (n: number, one: string, many = `${one}s`) => `${n} ${n === 1 ? one : many}`
/** A, B and C. */
const and = (xs: string[]) => (xs.length < 2 ? (xs[0] ?? "") : `${xs.slice(0, -1).join(", ")} and ${xs.at(-1)}`)
const fetchCode = (error: string | null) => (error ?? "").match(/'(\d{3}) ([^']*)'/)

const zh = {
  unrecorded: "当时未记录",
  count: (frm: number | null | undefined, n: number, _unit: Unit) => (frm != null && frm !== n ? `${frm} 条 → ${n} 条` : `${n} 条`),
  points: (n: number) => `${n} 分`,
  sources: (n: number, fetched: number | null) => `${n} 个信源` + (fetched != null ? ` · 共 ${fetched} 条候选` : ""),
  sourcesFailed: (n: number) => `${n} 个信源出错`,
  // 「抓取出错（429 Too Many Requests）」
  fetchError: (error: string | null) => {
    const m = fetchCode(error)
    return m ? `抓取出错（${m[1]} ${m[2]}）` : "抓取出错"
  },
  failure: (error: string) => (/^no JSON in the reply/.test(error) ? "模型的回复里没有可用的 JSON" : reasonZh(error)),
  reasons: (rs: string[]) => rs.filter(Boolean).map(reasonZh).join("；"),
  filterReason: (r: string) => r,
  stepLabel: (s: string) => STEP_ZH[s] ?? s,
  coveredOn: (day: string) => `${day} 那期写过`,
  issueChip: (day: string) => `${day.slice(5)} 期`,
  edition: (label: string) => `${label} 版`,
  f1: {
    name: "脚本抓取信息后过滤",
    rule: "过滤掉：点赞、星数不够，太旧，或者和 AI 无关的。",
    cut: (n: number) => `${n} 条被过滤`,
    groups: "原因",
    note: "Hacker News 的分数门槛在服务器端过滤，没有记录，不在下面。",
    unrecorded: "过滤掉的当时未记录",
  },
  f2: { name: "合并重复网址", rule: "几个信源抓到同一个网址时，去掉重复的。", cut: (n: number) => `${n} 条重复` },
  f3: { name: "去掉已发布", rule: "去掉以前几期已经写过的。", cut: (n: number) => `${n} 条以前几期写过`, groups: "期号" },
  lane: {
    unrecorded: "打分、挑选、写稿",
    failed: "出错",
    stops: (why: string) => `${why}，这个通道到这里停下。`,
    firstHand: {
      name: "去掉无官方来源的",
      rule: "使用脚本完成模型没有的网页搜索功能。<br>去掉只有论坛讨论、没有原始网页链接，打不开原文的候选。",
      cut: (n: number) => `${n} 条只有讨论帖`,
    },
    pick: {
      name: "模型进行打分、挑选",
      rule: (groups: number | null) =>
        `每条候选打分因素：<a class="dim" href="#mx">重要性、实用性、新颖性</a>。<br>按分数和当天的分量挑选${groups ? `，合成 ${groups} 组` : ""}。`,
      cut: (n: number) => `${n} 条没选`,
    },
    write: {
      name: "参考原文写稿",
      api: "脚本打开每组的原始网页交给模型，模型照原文写，同一件事的几个来源并成一条。",
      claude: "打开每条的原始网页，照原文写，同一件事的几个来源并成一条。",
      over: (n: number) => `${n} 组超出挑选上限，没有写`,
    },
  },
  check: {
    passed: "全部通过",
    self: { name: "自检", again: "再次自检", rule: "逐条对照原文检查。", cut: (n: number) => `${n} 条自检时删掉` },
    pre: {
      name: "预检",
      rule: "程序查一遍：引文、数字和专有名词都要在原文里找得到，摘要不能太长。只报告，不删。",
      draft: "程序查第一稿：引文、数字和专有名词都要在原文里找得到，摘要不能太长。只报告，不删。",
      cut: (n: number) => `${n} 条没过`,
    },
    fix: {
      name: "预检修改",
      claude: "按预检报告补上原文引用，或者整条删掉，不许改写正文。",
      api: "把没过的条目连同原因发回模型，模型改完交回整份稿子。",
    },
    final: { name: "正式校验", rule: "程序再查一次，仍不合格的整条删掉。", cut: (n: number) => `${n} 条被删` },
    highlights: "日报简介里有原文找不到的内容：改用条目标题写简介，又查了一次。",
    en: {
      name: "写英文版",
      rule: "中文版通过后，照同一批原文另写英文版（不是翻译），再检查一次。<br>英文版删掉的不影响中文版。",
      cut: (n: number) => `${n} 条英文版删掉`,
      /** On a route that did not end up the main edition; `first`: it went out first, then was replaced. */
      notMain: (first: boolean) =>
        `只有成为正式版时才会发布英文版，${first ? "这一版先发出过，正式版通过后被换掉。" : "这次没有用上。"}`,
    },
  },
  adopt: {
    none: "没有一个通道交出合格的稿子：本期发布降级版，未经编辑。",
    one: (main: string) => `只有 ${main} 一个通道：它写的这一版就是正式版。`,
    many: (n: number, main: string, beta: string[]) =>
      `${NUMERALS[n] ?? n}个通道都写完了：正式版用 ${main} 写的这一版` +
      (beta.length ? `，${beta.map((b) => `${b} 版`).join("、")}作为 Beta 版。` : "。"),
    failed: (names: string[]) => `${names.join("、")} 通道中途出错，没有交出稿子。`,
    unpublished: (names: string[]) => `${names.map((b) => `${b} 版`).join("、")}没有发布。`,
  },
  story: (label: string, fate: Fate) =>
    `${label} 版` +
    { main: "通过校验，作为正式版。", first: "先发出：当时还没有正式版。", beta: "留作 Beta 版。", unpublished: "没有发布。" }[fate],
  ends: {
    main: "正式版",
    fallback: "降级版",
    fallbackInitial: "降",
    mainSub: (n: number | null) => `本期日报${n != null ? ` · 发布 ${n} 条` : ""}`,
    betaSub: (n: number) => `Beta · 发布 ${n} 条`,
  },
  matrix: {
    differs: "有分歧",
    dropped: "被删",
    high: "高分没选",
    all: "全部",
    state: { published: "发布", dropped: "被删", unpicked: "没选" },
    head: (route: string, state: string, step: string | null, why: string) =>
      `${route} · ${state}${step ? ` · ${step}` : ""}${why ? `：${why}` : ""}`,
  },
  page: {
    title: "生成过程",
    description: (date: string) => `${date} 这期日报从抓取到发布，每一步留下和去掉了什么。`,
    sources: "信息来源",
    adopt: "选定正式版",
    table: "每条候选的打分和去向",
    filterLabel: "筛选候选",
    legend: ["发布", "被删", "没选", " · 数字是三项分数之和（0–8），点一行看每项分数和原因"],
    dims: ["重要性", "实用性", "新颖性"],
    unscored: "没有打分",
    close: "关闭",
    none: "没有符合的条目",
    search: "搜索标题或信源",
    searchLabel: "搜索",
    expand: "展开",
    expandAll: (n: number) => `展开全部 ${n} 条`,
    collapse: "收起",
    all: (n: number) => `全部 ${n}`,
    groupBy: (g: string) => `按${g}筛`,
  },
}

type Copy = typeof zh

const en: Copy = {
  unrecorded: "Not recorded at the time",
  count: (frm, n, unit) => {
    const noun = unit === "c" ? (n === 1 ? "candidate" : "candidates") : n === 1 ? "item" : "items"
    return frm != null && frm !== n ? `${frm} → ${n} ${noun}` : `${n} ${noun}`
  },
  points: (n) => nOf(n, "point"),
  sources: (n, fetched) => nOf(n, "source") + (fetched != null ? ` · ${nOf(fetched, "candidate")}` : ""),
  sourcesFailed: (n) => `${nOf(n, "source")} failed`,
  fetchError: (error) => {
    const m = fetchCode(error)
    return m ? `Fetch failed (${m[1]} ${m[2]})` : "Fetch failed"
  },
  failure: (error) => (/^no JSON in the reply/.test(error) ? "The model's reply had no usable JSON" : error),
  // validate's own messages, as it writes them
  reasons: (rs) => rs.filter(Boolean).join("; "),
  filterReason: (r) => FILTER_EN[r] ?? r,
  stepLabel: (s) => STEP_EN[s.replace(/[，,\s]/g, "")] ?? s,
  coveredOn: (day) => `Covered on ${day}`,
  issueChip: (day) => `${MONTHS[Number(day.slice(5, 7)) - 1]} ${Number(day.slice(8))}`,
  edition: (label) => `${label} edition`,
  f1: {
    name: "Fetch and filter",
    rule: "Filtered out: too few upvotes or stars, too old, or not about AI.",
    cut: (n) => `${n} filtered out`,
    groups: "reason",
    note: "Hacker News filters by score on its own server, so those aren't recorded or listed here.",
    unrecorded: "What was filtered out wasn't recorded at the time",
  },
  f2: {
    name: "Merge duplicate links",
    rule: "When several sources fetch the same link, the duplicates are dropped.",
    cut: (n) => nOf(n, "duplicate"),
  },
  f3: { name: "Drop what's been covered", rule: "Drop what earlier issues already covered.", cut: (n) => `${n} covered before`, groups: "issue" },
  lane: {
    unrecorded: "Score, pick and write",
    failed: "Failed",
    stops: (why) => `${why}, so this route stops here.`,
    firstHand: {
      name: "Drop those without an official source",
      rule: "A script does the web search the model can't.<br>Drops candidates with only a forum thread and no link to the original page.",
      cut: (n) => `${n} only ${n === 1 ? "has" : "have"} a thread`,
    },
    pick: {
      name: "Score and pick",
      rule: (groups) =>
        `Every candidate is scored on <a class="dim" href="#mx">importance, usefulness and novelty</a>.<br>Picked by score and by how much news the day has${groups ? `, merged into ${groups} groups` : ""}.`,
      cut: (n) => `${n} not picked`,
    },
    write: {
      name: "Write from the originals",
      api: "A script opens each group's original pages for the model, which writes from them; several sources on one story become one item.",
      claude: "Opens each item's original pages and writes from them; several sources on one story become one item.",
      over: (n) => `${nOf(n, "group")} over the pick limit, not written`,
    },
  },
  check: {
    passed: "All passed",
    self: { name: "Self-check", again: "Self-check again", rule: "Each item checked against its original.", cut: (n) => `${n} removed in self-check` },
    pre: {
      name: "Precheck",
      rule: "A program checks that quotes, numbers and names all appear in the original, and that summaries aren't too long. It only reports; nothing is removed.",
      draft:
        "A program checks the first draft: quotes, numbers and names must all appear in the original, and summaries can't be too long. It only reports; nothing is removed.",
      cut: (n) => `${n} didn't pass`,
    },
    fix: {
      name: "Fix after precheck",
      claude: "Add the quotes the precheck asked for, or remove the item. The text may not be rewritten.",
      api: "The failing items go back to the model with the reasons; it returns the whole revised draft.",
    },
    final: { name: "Final check", rule: "The program checks again and removes any item that still fails.", cut: (n) => `${n} removed` },
    highlights: "The issue summary had something not in the originals, so it was rewritten from the item titles and checked again.",
    en: {
      name: "Write the English edition",
      rule: "Once the Chinese edition passed, an English one was written from the same originals (not translated) and checked again.<br>What it removes doesn't change the Chinese edition.",
      cut: (n) => `${n} removed from the English edition`,
      notMain: (first) =>
        `Only the main edition is published in English; ${first ? "this one went out first and was replaced once the main edition passed." : "this one wasn't used."}`,
    },
  },
  adopt: {
    none: "No route turned in a passing draft, so this issue is the fallback edition, unedited.",
    one: (main) => `${main} was the only route, so its edition is the main edition.`,
    many: (n, main, beta) =>
      `${n === 2 ? "Both" : `All ${WORDS[n] ?? n}`} routes finished. The main edition is ${main}'s` +
      (beta.length ? `; the ${and(beta)} ${beta.length === 1 ? "edition is a Beta" : "editions are Betas"}.` : "."),
    failed: (names) => `The ${and(names)} ${names.length === 1 ? "route" : "routes"} failed partway and turned in no draft.`,
    unpublished: (names) => `The ${and(names)} ${names.length === 1 ? "edition wasn't" : "editions weren't"} published.`,
  },
  story: (label, fate) =>
    `The ${label} edition ` +
    {
      main: "passed its checks and became the main edition.",
      first: "went out first, as there was no main edition yet.",
      beta: "was kept as a Beta.",
      unpublished: "wasn't published.",
    }[fate],
  ends: {
    main: "Main edition",
    fallback: "Fallback",
    fallbackInitial: "F",
    mainSub: (n) => `This issue${n != null ? ` · ${nOf(n, "item")}` : ""}`,
    betaSub: (n) => `Beta · ${nOf(n, "item")}`,
  },
  matrix: {
    differs: "Routes disagree",
    dropped: "Removed",
    high: "High score, not picked",
    all: "All",
    state: { published: "Published", dropped: "Removed", unpicked: "Not picked" },
    head: (route, state, step, why) => `${route} · ${state}${step ? ` · ${step}` : ""}${why ? `: ${why}` : ""}`,
  },
  page: {
    title: "How it was made",
    description: (date) => `How the ${date} issue went from fetching to publishing: what each step kept and what it removed.`,
    sources: "Sources",
    adopt: "Choose the main edition",
    table: "Every candidate: its scores and where it went",
    filterLabel: "Filter the candidates",
    legend: ["Published", "Removed", "Not picked", " · The number is the three scores added up (0–8). Click a row for each score and the reasons."],
    dims: ["Importance", "Usefulness", "Novelty"],
    unscored: "Not scored",
    close: "Close",
    none: "Nothing matches",
    search: "Search titles or sources",
    searchLabel: "Search",
    expand: "Expand",
    expandAll: (n) => `Expand all ${n}`,
    collapse: "Collapse",
    all: (n) => `All ${n}`,
    groupBy: (g) => `Filter by ${g}`,
  },
}

const COPY: Record<Lang, Copy> = { zh, en }
