// The 生成过程 page's flow chart (issue #63): one issue's process (process.ts) as the steps the
// page draws, from the sources to the editions it published. The page only lays these out; every
// count and every line of copy is decided here. Chinese only for now.
//
// The shared line: 信息来源 → 过滤 → 合并重复网址 → 去掉已发布. Then one lane per editor route,
// each step in the order its trace has them, then 选定正式版 and one end card per edition.
// A route without a trace keeps only its digest's last validation; the steps before it are drawn
// dashed and marked 当时未记录. A route that failed stops at the failed step.

import { betaHref, betas, issueHref } from "@/lib/issues"
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

export type End = { slug: string; href: string; logo: string | null; initial: string; title: string; sub: string }

export type Flow = {
  source: { href: string; num: string; cuts: Cut[] }
  spine: FlowNode[]
  lanes: Lane[]
  adopt: { rule: string; story: { at: string; text: string }[] }
  ends: End[]
  matrix: Matrix
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

const UNRECORDED = "当时未记录"
const count = (frm: number | null | undefined, n: number) => (frm != null && frm !== n ? `${frm} 条 → ${n} 条` : `${n} 条`)
const NUMERALS = ["零", "一", "两", "三", "四", "五", "六"]
const howMany = (n: number) => `${NUMERALS[n] ?? n}个`

const slugOf = (c: Channel) => (c.id.startsWith("api.") ? c.id.slice("api.".length) : c.id)
const logoOf = (c: Channel) => editionLogo(c.id === "claude" ? "main" : slugOf(c))
const initialOf = (c: Channel) => c.label.charAt(0)
const modelOf = (c: Channel) => (c.model ? modelName(c.model.replace(/^\w+:/, "")) : c.label)
const HOW: [RegExp, string][] = [
  [/^nvidia:/, "NVIDIA NIM API"],
  [/^gemini:/, "Gemini API"],
]
const howOf = (c: Channel) => (c.id === "claude" ? "Claude Schedule Task" : (HOW.find(([re]) => re.test(c.model ?? ""))?.[1] ?? ""))

const FAILURE: [RegExp, string][] = [[/^no JSON in the reply/, "模型的回复里没有可用的 JSON"]]
const failureZh = (error: string) => FAILURE.find(([re]) => re.test(error))?.[1] ?? reasonZh(error)

// A fetch error as the reader sees it: 「抓取出错（429 Too Many Requests）」.
function fetchError(error: string | null) {
  const m = (error ?? "").match(/'(\d{3}) ([^']*)'/)
  return m ? `抓取出错（${m[1]} ${m[2]}）` : "抓取出错"
}

const reasons = (rs: string[]) => rs.filter(Boolean).map(reasonZh).join("；")

export function buildFlow(p: Process): Flow {
  const f = p.funnel
  const fetched = f.raw != null && f.filtered != null ? f.raw + f.filtered : null
  const rows = new Map(p.rows.map((r) => [r.id, r]))

  const failedSources = p.sources.filter((s) => s.status && s.status !== "ok")
  const source = {
    href: "sources/",
    num: `${p.sources.length} 个信源` + (fetched != null ? ` · 共 ${fetched} 条候选` : ""),
    cuts: failedSources.length
      ? [{ label: `${failedSources.length} 个信源出错`, items: failedSources.map((s) => ({ title: s.name, why: fetchError(s.error) })) }]
      : [],
  }

  const filtered = (p.filtered ?? []).flatMap((g) =>
    g.items.map((it) => ({ title: it.title, why: it.reason, source: g.name, group: it.reason })),
  )
  const old = [...p.already_published]
    .sort((a, b) => b.published_on.localeCompare(a.published_on))
    .map((d) => ({
      title: d.title,
      why: `${d.published_on} 那期写过`,
      href: issueHref(d.published_on),
      group: `${d.published_on.slice(5)} 期`,
    }))
  const merged = f.raw != null && f.after_url_merge != null ? f.raw - f.after_url_merge : 0
  const spine: FlowNode[] = [
    {
      id: "f1",
      name: "脚本抓取信息后过滤",
      num: f.raw == null ? UNRECORDED : count(fetched, f.raw),
      rule: "过滤掉：点赞、星数不够，太旧，或者和 AI 无关的。",
      cuts:
        f.filtered == null
          ? []
          : f.filtered
            ? [
                {
                  label: `${f.filtered} 条被过滤`,
                  items: filtered,
                  groups: "原因",
                  note: "Hacker News 的分数门槛在服务器端过滤，没有记录，不在下面。",
                },
              ]
            : [],
      flat: f.filtered == null ? `过滤掉的${UNRECORDED}` : undefined,
      unrecorded: f.filtered == null,
    },
    {
      id: "f2",
      name: "合并重复网址",
      num: f.after_url_merge == null ? UNRECORDED : count(f.raw, f.after_url_merge),
      rule: "几个信源抓到同一个网址时，去掉重复的。",
      cuts: merged ? [{ label: `${merged} 条重复` }] : [],
    },
    {
      id: "f3",
      name: "去掉已发布",
      num: f.candidates == null ? UNRECORDED : count(f.after_url_merge, f.candidates),
      rule: "去掉以前几期已经写过的。",
      cuts: f.already_published
        ? [
            {
              label: `${f.already_published} 条以前几期写过`,
              items: old.length === f.already_published ? old : undefined,
              groups: "期号",
            },
          ]
        : [],
    },
  ]

  const chans = [...p.channels].sort((a, b) => Number(b.main) - Number(a.main))
  const lanes = chans.map((c) => lane(c, p, rows))

  // the editions this issue published: the main one, then each route's Beta page
  const betaOf = (c: Channel) => betas.some((b) => b.date === p.date && b.beta?.slug === slugOf(c))
  const published = (c: Channel) => c.funnel.find((s) => s.label === "发布")?.value ?? 0
  const main = chans.find((c) => c.main)
  const beta = chans.filter((c) => !c.main && betaOf(c))
  const failed = chans.filter((c) => c.failure)
  const unpublished = chans.filter((c) => !c.main && !c.failure && !betaOf(c))
  const label = (cs: Channel[]) => cs.map((c) => `${c.label} 版`).join("、")
  const rule = [
    !main
      ? "没有一个通道交出合格的稿子：本期发布降级版，未经编辑。"
      : chans.length === 1
        ? `只有 ${main.label} 一个通道：它写的这一版就是正式版。`
        : `${howMany(chans.length)}通道都写完了：正式版用 ${main.label} 写的这一版` +
          (beta.length ? `，${label(beta)}作为 Beta 版。` : "。"),
    failed.length ? `${failed.map((c) => c.label).join("、")} 通道中途出错，没有交出稿子。` : "",
    unpublished.length ? `${label(unpublished)}没有发布。` : "",
  ]
    .filter(Boolean)
    .join("<br>")
  const story = chans
    .flatMap((c) => c.adopt.filter((a) => a.edition === "zh").map((a) => ({ a, c })))
    .sort((x, y) => x.a.at.localeCompare(y.a.at))
    .map(({ a, c }) => ({
      at: hm(a.at),
      text:
        `${c.label} 版` +
        (c.main ? "通过校验，作为正式版。" : a.adopted ? "先发出：当时还没有正式版。" : betaOf(c) ? "留作 Beta 版。" : "没有发布。"),
    }))

  const ends: End[] = [
    ...(main || p.main === "fallback"
      ? [
          {
            slug: "main",
            href: issueHref(p.date),
            logo: main ? logoOf(main) : null,
            initial: main ? initialOf(main) : "降",
            title: main ? "正式版" : "降级版",
            sub: `本期日报${main ? ` · 发布 ${published(main)} 条` : ""}`,
          },
        ]
      : []),
    ...beta.map((c) => ({
      slug: slugOf(c),
      href: betaHref(p.date, slugOf(c)),
      logo: logoOf(c),
      initial: initialOf(c),
      title: `${c.label} 版`,
      sub: `Beta · 发布 ${published(c)} 条`,
    })),
  ]

  return { source, spine, lanes, adopt: { rule, story }, ends, matrix: matrix(p, chans) }
}

// One route's steps. MiniMax and the other API routes: 去掉无官方来源的 → 打分、挑选 → 写稿 →
// 预检 (its draft round) → 预检修改 → 正式校验 (its fix round) → 写英文版. Claude: 打分、挑选 →
// 写稿 → 自检 → 预检 → 预检修改 → 正式校验 → 写英文版. Each check round starts from the count
// its trace says it was handed, not from the step before.
function lane(c: Channel, p: Process, rows: Map<string, Row>): Lane {
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
    nodes.push({ id: id(), name: "打分、挑选、写稿", num: UNRECORDED, cuts: [], unrecorded: true })
  }

  let pool = p.rows.map((r) => r.id)
  const gone = steps.find((s) => s.step === "no_first_hand")
  if (gone) {
    const dropped = new Set(gone.candidates ?? [])
    const before = pool.length
    pool = pool.filter((i) => !dropped.has(i))
    nodes.push({
      id: id(),
      name: "去掉无官方来源的",
      at: hm(gone.at),
      num: count(before, pool.length),
      rule: "使用脚本完成模型没有的网页搜索功能。<br>去掉只有论坛讨论、没有原始网页链接，打不开原文的候选。",
      cuts: dropped.size
        ? [
            {
              label: `${dropped.size} 条只有讨论帖`,
              items: [...dropped].filter((i) => rows.has(i)).map((i) => ({ title: row(i)!.title, source: row(i)!.source })),
            },
          ]
        : [],
    })
  }

  const fail = (name: string) => {
    nodes.push({ id: id(), name, num: "出错", rule: `${failureZh(c.failure!.error)}，这个通道到这里停下。`, cuts: [], failed: true })
    return out
  }
  if (c.failure?.step === "pick") return fail("模型进行打分、挑选")

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
        return { title: row(i)!.title, why: total != null ? `${total} 分` : undefined, source: row(i)!.source }
      })
    const groups = pick?.kept && pick.kept !== picked.length ? `，合成 ${pick.kept} 组` : ""
    nodes.push({
      id: id(),
      name: "模型进行打分、挑选",
      at: hm(gone ? pick?.at : (c.started_at ?? pick?.at)),
      num: count(pool.length, picked.length),
      rule: `每条候选打分因素：<a class="dim" href="#mx">重要性、实用性、新颖性</a>。<br>按分数和当天的分量挑选${groups}。`,
      cuts: unpicked.length ? [{ label: `${unpicked.length} 条没选`, items: unpicked }] : [],
    })

    if (c.failure?.step === "draft" || c.failure?.step === "read") return fail("参考原文写稿")
    const first = rounds[0]
    // what was written: the first check round's items, plus what a self-check took out before it
    const before = selfChecks.filter((s) => !first || steps.indexOf(s) < steps.indexOf(first))
    const writtenCount = (first?.fed ?? 0) + before.reduce((n, s) => n + (s.dropped?.length ?? 0), 0)
    const over = steps.find((s) => s.step === "over_picks")
    nodes.push({
      id: id(),
      name: "参考原文写稿",
      num: count(picked.length, writtenCount),
      rule: api
        ? "脚本打开每组的原始网页交给模型，模型照原文写，同一件事的几个来源并成一条。"
        : "打开每条的原始网页，照原文写，同一件事的几个来源并成一条。",
      cuts: over?.groups?.length ? [{ label: `${over.groups.length} 组超出挑选上限，没有写` }] : [],
    })
    checks(c, steps, writtenCount, nodes, id, api)
  } else {
    checks(c, steps, null, nodes, id, api)
  }
  if (c.failure && !nodes.at(-1)?.failed) {
    const NAMES: Record<string, string> = { fix: "预检修改", en: "写英文版", en_highlights: "写英文版" }
    return fail(NAMES[c.failure.step] ?? c.failure.label)
  }
  return out
}

const CHECK_RULES = {
  self_check: "逐条对照原文检查。",
  precheck: "程序查一遍：引文、数字和专有名词都要在原文里找得到，摘要不能太长。只报告，不删。",
  draft: "程序查第一稿：引文、数字和专有名词都要在原文里找得到，摘要不能太长。只报告，不删。",
  fixClaude: "按预检报告补上原文引用，或者整条删掉，不许改写正文。",
  fixApi: "把没过的条目连同原因发回模型，模型改完交回整份稿子。",
  final: "程序再查一次，仍不合格的整条删掉。",
  highlights: "日报简介里有原文找不到的内容：改用条目标题写简介，又查了一次。",
  en: "中文版通过后，照同一批原文另写英文版（不是翻译），再检查一次。<br>英文版删掉的不影响中文版。",
}

// The check rounds, in the order they ran. 预检 (Claude's precheck, an API route's draft round)
// only reports; 预检修改 shows only when it found something; 正式校验 (final, or the fix round)
// deletes what still fails. English rounds do not change the Chinese count.
function checks(c: Channel, steps: Step[], start: number | null, nodes: FlowNode[], id: () => string, api: boolean) {
  let prev = start
  let pre: Step | null = null
  let selfChecks = 0
  const drops = (s: Step) =>
    (s.dropped ?? []).map((d) => ({ title: d.title, why: reasons(d.reasons) || undefined }))
  for (const s of steps) {
    const d = drops(s)
    const flat = d.length ? undefined : "全部通过"
    const at = hm(s.at)
    switch (s.step) {
      case "self_check": {
        const n = prev == null ? null : prev - d.length
        nodes.push({
          id: id(),
          name: selfChecks++ ? "再次自检" : "自检",
          at,
          num: n == null ? undefined : count(prev, n),
          rule: CHECK_RULES.self_check,
          cuts: d.length ? [{ label: `${d.length} 条自检时删掉`, items: d }] : [],
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
          name: "预检",
          at,
          num: count(null, s.fed!),
          rule: s.step === "draft" ? CHECK_RULES.draft : CHECK_RULES.precheck,
          cuts: d.length ? [{ label: `${d.length} 条没过`, items: d }] : [],
          flat,
        })
        prev = s.fed
        break
      case "final":
      case "fix": {
        if (pre?.dropped?.length && c.recorded) {
          nodes.push({
            id: id(),
            name: "预检修改",
            num: count(prev, s.fed!),
            rule: api ? CHECK_RULES.fixApi : CHECK_RULES.fixClaude,
            cuts: [],
          })
        }
        const kept = s.kept ?? s.fed! - d.length
        nodes.push({
          id: id(),
          name: "正式校验",
          at,
          num: count(s.fed, kept),
          rule: CHECK_RULES.final,
          cuts: d.length ? [{ label: `${d.length} 条被删`, items: d }] : [],
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
        last.num = count(s.fed, kept)
        last.rule += `<br>${CHECK_RULES.highlights}`
        last.cuts = d.length ? [{ label: `${d.length} 条${s.step === "en_highlights" ? "英文版删掉" : "被删"}`, items: d }] : []
        last.flat = flat
        if (s.step === "highlights") prev = kept
        break
      }
      case "en": {
        const kept = s.kept ?? s.fed! - d.length
        nodes.push({
          id: id(),
          name: "写英文版",
          at,
          num: count(s.fed, kept),
          rule: CHECK_RULES.en,
          cuts: d.length ? [{ label: `${d.length} 条英文版删掉`, items: d }] : [],
          flat,
        })
        break
      }
    }
  }
}

const STATE = { published: "发布", dropped: "被删", unpicked: "没选" } as const

function matrix(p: Process, chans: Channel[]): Matrix {
  const several = chans.length > 1
  const tests: [string, string, (r: Row) => boolean][] = [
    ...(several ? ([["differs", "有分歧", (r: Row) => r.differs]] as [string, string, (r: Row) => boolean][]) : []),
    ["dropped", "被删", (r) => r.dropped],
    ["high", "高分没选", (r) => r.high_unpicked],
    ["all", "全部", () => true],
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
    filters: tests.map(([key, label, t]) => ({ key, label, count: p.rows.filter(t).length, on: key === first })),
    rows: rows.map((r) => ({
      title: r.title,
      url: r.url,
      source: r.source,
      filters: tests.filter(([, , t]) => t(r)).map(([key]) => key),
      marks: chans.map((c) => {
        const cell = r.cells[c.id]
        return cell ? { state: cell.state, total: cell.total } : null
      }),
      details: chans.flatMap((c) => {
        const cell = r.cells[c.id]
        if (!cell) return []
        const why = cell.reasons.length ? `：${reasons(cell.reasons)}` : ""
        const step = cell.step ? ` · ${cell.step}` : ""
        return [{ logo: logoOf(c), initial: initialOf(c), head: `${c.label} · ${STATE[cell.state]}${step}${why}`, scores: cell.score }]
      }),
    })),
  }
}
