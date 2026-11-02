import { Fragment, useState } from "react"
import { cn } from "cn"

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { type Cell, reasonZh, type Row } from "@/lib/process"

type Props = {
  rows: Row[]
  /** The routes, in column order. */
  channels: { id: string; label: string; main: boolean; scored: boolean }[]
}

const FILTERS = [
  { id: "differs", label: "有分歧", test: (r: Row) => r.differs },
  { id: "dropped", label: "被删", test: (r: Row) => r.dropped },
  { id: "high", label: "高分未选", test: (r: Row) => r.high_unpicked },
  { id: "all", label: "全部", test: () => true },
] as const

const STATES: Record<Cell["state"], string> = { published: "发布", dropped: "被删", unpicked: "未选" }
const SYMBOLS: Record<Cell["state"], string> = { published: "●", dropped: "✕", unpicked: "·" }
const DIMENSIONS = ["重要性", "实用性", "新颖性"]

// Every candidate against every editor route: what each route did with it and the score it gave.
// The pills pick which candidates show; a row opens to the reasons and the three scores.
export default function ProcessMatrix({ rows, channels }: Props) {
  const [filter, setFilter] = useState<string>("differs")
  const [open, setOpen] = useState<Set<string>>(new Set())
  const test = FILTERS.find((f) => f.id === filter)!.test
  const scored = channels.some((c) => c.scored)
  // Without scores there is nothing to call 高分.
  const filters = scored ? FILTERS : FILTERS.filter((f) => f.id !== "high")
  const shown = sorted(rows).filter(test)

  function toggle(id: string) {
    setOpen((was) => {
      const next = new Set(was)
      if (!next.delete(id)) next.add(id)
      return next
    })
  }

  return (
    <div>
      <div className="-mx-4 overflow-x-auto px-4 [scrollbar-width:none] sm:mx-0 sm:px-0">
        <ToggleGroup
          type="single"
          value={filter}
          onValueChange={(next) => next && setFilter(next)}
          variant="outline"
          size="sm"
          spacing={1}
          aria-label="筛选候选"
        >
          {filters.map((f) => (
            <ToggleGroupItem
              key={f.id}
              value={f.id}
              className="rounded-full px-3.5 text-[13px] font-normal data-[state=on]:border-foreground data-[state=on]:bg-foreground data-[state=on]:text-background"
            >
              {f.label}
              <span className="tabular-nums opacity-60">{rows.filter(f.test).length}</span>
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      <Legend scored={scored} />

      <table className="mt-4 w-full table-fixed border-collapse text-sm">
        <thead>
          <tr className="text-xs text-muted-foreground">
            <th className="pb-2 text-left font-normal">候选</th>
            {channels.map((c) => (
              <th key={c.id} className="w-14 pb-2 text-center font-normal sm:w-20">
                <span className={cn(c.main && "font-semibold text-foreground")}>{c.label}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {shown.map((row) => {
            const expanded = open.has(row.id)
            return (
              <Fragment key={row.id}>
                <tr
                  onClick={() => toggle(row.id)}
                  className="cursor-pointer border-t border-foreground/5 align-top hover:bg-muted/60"
                >
                  <td className="py-2.5 pr-3">
                    <button
                      type="button"
                      aria-expanded={expanded}
                      className="block w-full text-left leading-snug text-foreground/80"
                    >
                      {row.title}
                    </button>
                    <span className="mt-0.5 block text-xs text-muted-foreground">{row.source}</span>
                  </td>
                  {channels.map((c) => (
                    <td key={c.id} className="py-2.5 text-center">
                      <Mark cell={row.cells[c.id]} />
                    </td>
                  ))}
                </tr>
                {expanded && (
                  <tr>
                    <td colSpan={channels.length + 1} className="pb-4">
                      <Detail row={row} channels={channels} />
                    </td>
                  </tr>
                )}
              </Fragment>
            )
          })}
        </tbody>
      </table>
      {shown.length === 0 && <p className="mt-6 text-center text-sm text-muted-foreground">没有这样的候选。</p>}
    </div>
  )
}

/** Published by more routes first, then the higher score. */
function sorted(rows: Row[]): Row[] {
  const key = (r: Row) => {
    const cells = Object.values(r.cells)
    return [
      cells.filter((c) => c.state === "published").length,
      Math.max(0, ...cells.map((c) => c.total ?? 0)),
    ]
  }
  return [...rows].sort((a, b) => {
    const [pa, sa] = key(a)
    const [pb, sb] = key(b)
    return pb - pa || sb - sa
  })
}

function Mark({ cell }: { cell: Cell | undefined }) {
  if (!cell) return null
  const label = cell.total ?? SYMBOLS[cell.state]
  return (
    <span
      title={STATES[cell.state] + (cell.step ? ` · ${cell.step}` : "")}
      className={cn(
        "inline-flex h-6 min-w-6 items-center justify-center rounded-full px-1.5 text-xs tabular-nums",
        cell.state === "published" && "bg-foreground font-medium text-background",
        cell.state === "dropped" && "text-foreground/70 line-through ring-1 ring-foreground/30",
        cell.state === "unpicked" && "text-muted-foreground",
      )}
    >
      {label}
    </span>
  )
}

function Legend({ scored }: { scored: boolean }) {
  const total = scored ? 6 : null
  return (
    <p className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
      <span className="flex items-center gap-1.5">
        <Mark cell={{ state: "published", step: null, reasons: [], score: null, total }} /> 发布
      </span>
      <span className="flex items-center gap-1.5">
        <Mark cell={{ state: "dropped", step: null, reasons: [], score: null, total }} /> 被删
      </span>
      <span className="flex items-center gap-1.5">
        <Mark cell={{ state: "unpicked", step: null, reasons: [], score: null, total }} /> 未选
      </span>
      <span>{scored ? "数字是三项打分之和（0–8）。" : "这期当时没有打分。"}点一行看详情。</span>
    </p>
  )
}

function Detail({ row, channels }: { row: Row; channels: Props["channels"] }) {
  return (
    <div className="rounded-lg bg-muted px-4 py-3 text-xs leading-relaxed">
      <a href={row.url} target="_blank" rel="noreferrer" className="break-all text-muted-foreground underline underline-offset-2">
        {row.url}
      </a>
      <dl className="mt-2 flex flex-col gap-1.5">
        {channels.map((c) => {
          const cell = row.cells[c.id]
          if (!cell) return null
          return (
            <div key={c.id} className="grid grid-cols-[4.5rem_1fr] gap-2">
              <dt className="font-medium">{c.label}</dt>
              <dd className="text-foreground/80">
                {STATES[cell.state]}
                {cell.step && ` · ${cell.step}`}
                {cell.reasons.length > 0 && `：${cell.reasons.map(reasonZh).join("；")}`}
                {cell.score ? (
                  <span className="block text-muted-foreground tabular-nums">
                    {cell.score.map((s, i) => `${DIMENSIONS[i]} ${s}`).join(" · ")}
                  </span>
                ) : (
                  !c.scored && <span className="block text-muted-foreground">当时未记录打分</span>
                )}
              </dd>
            </div>
          )
        })}
      </dl>
    </div>
  )
}
