import { cn } from "cn"
import { ChevronDown, ChevronLeft, ChevronRight, X } from "lucide-react"
import { Fragment, useEffect, useRef, useState } from "react"
import { flushSync } from "react-dom"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Separator } from "@/components/ui/separator"
import { formatDay, issueHref } from "@/lib/issues"

export type Entry = { date: string; fallback: boolean; description: string; items: number }

type Props = { entries: Entry[] }

/** A span of months, both ends included. */
type Range = [number, number]

const ALL_MONTHS: Range = [1, 12]
const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1)

const yearOf = (day: string) => Number(day.slice(0, 4))
const monthOf = (day: string) => Number(day.slice(5, 7))

// Every issue, newest first, grouped by month: pick one year and a span of its months. The top
// mirrors an issue page (a year wheel like the date wheel, then the months like the section
// filter), and changing the selection animates the month groups the same way (global.css).
export default function Archive({ entries }: Props) {
  // Years with issues, oldest first.
  const years = [...new Set(entries.map((e) => yearOf(e.date)))].reverse()
  const latestYear = years[years.length - 1]

  const [year, setYear] = useState(latestYear)
  const [range, setRange] = useState<Range>(ALL_MONTHS)
  const [animating, setAnimating] = useState(false)

  const inYear = entries.filter((e) => yearOf(e.date) === year)
  const shown = inYear.filter((e) => monthOf(e.date) >= range[0] && monthOf(e.date) <= range[1])
  const months = Map.groupBy(shown, (e) => e.date.slice(0, 7))

  function apply(update: () => void) {
    if (!document.startViewTransition || matchMedia("(prefers-reduced-motion: reduce)").matches) {
      update()
      return
    }
    // The month groups get their view-transition-name only for this transition, so that leaving
    // the page cross-fades it as a whole.
    flushSync(() => setAnimating(true))
    const root = document.documentElement
    root.dataset.filtering = ""
    document.startViewTransition(() => flushSync(update)).finished.finally(() => {
      delete root.dataset.filtering
      setAnimating(false)
    })
  }

  function selectYear(next: number) {
    apply(() => {
      setYear(next)
      setRange(ALL_MONTHS)
    })
  }

  function selectMonths(next: Range) {
    if (next[0] !== range[0] || next[1] !== range[1]) apply(() => setRange(next))
  }

  const counts = Map.groupBy(entries, (e) => yearOf(e.date))
  const filtered = range[0] !== ALL_MONTHS[0] || range[1] !== ALL_MONTHS[1]

  return (
    <>
      <h1 className="sr-only">往期归档</h1>
      <YearWheel years={years} counts={counts} year={year} shown={shown.length} onYear={selectYear} />
      <MonthRange
        key={year} // a span left open does not carry over to another year
        available={new Set(inYear.map((e) => monthOf(e.date)))}
        range={range}
        onChange={selectMonths}
      />
      <div className="mt-3 flex h-7 justify-center">
        {filtered && (
          <Button
            variant="outline"
            size="xs"
            onClick={() => apply(() => setRange(ALL_MONTHS))}
            aria-label="显示全年"
            className="rounded-full px-3 font-rounded text-xs font-semibold tabular-nums"
          >
            {range[0] === range[1] ? `${range[0]}月` : `${range[0]}月–${range[1]}月`}
            <X />
          </Button>
        )}
      </div>

      <div className="mt-8 flex flex-col gap-12">
        {[...months].map(([month, monthEntries]) => (
          <MonthGroup
            key={month}
            month={month}
            entries={monthEntries}
            transitionName={animating ? `archive-${month}` : undefined}
          />
        ))}
        {shown.length === 0 && (
          <p
            className="py-16 text-center text-sm text-muted-foreground"
            style={{ viewTransitionName: animating ? "archive-empty" : undefined }}
          >
            这个区间没有日报
          </p>
        )}
      </div>
    </>
  )
}

type YearWheelProps = {
  /** Years with issues, oldest first. */
  years: number[]
  counts: Map<number, Entry[]>
  year: number
  /** Issues shown for the selected year and months. */
  shown: number
  onYear: (year: number) => void
}

// The selected year between its neighbours, like the date wheel on an issue page: years with
// issues can be picked, the others stay as faded labels.
function YearWheel({ years, counts, year, shown, onYear }: YearWheelProps) {
  const at = years.indexOf(year)
  return (
    <nav aria-label="切换年份" className="flex items-center justify-between gap-2 pt-10 pb-8">
      <StepButton target={years[at - 1]} label="上一年" onYear={onYear}>
        <ChevronLeft />
      </StepButton>
      <ol className="flex items-center justify-center gap-3 font-rounded sm:gap-6">
        {[-2, -1, 0, 1, 2].map((offset) => {
          if (offset === 0) {
            return (
              <li
                key={offset}
                aria-current="true"
                className="flex flex-col items-center rounded-2xl bg-muted px-5 py-2.5 ring-1 ring-foreground/5"
              >
                <span className="text-xs font-medium text-muted-foreground tabular-nums">共 {shown} 期</span>
                <span className="text-base leading-6 font-bold tabular-nums">{year}</span>
              </li>
            )
          }
          const y = year + offset
          const count = counts.get(y)?.length
          const far = Math.abs(offset) === 2
          const label = (
            <>
              <span className="text-[11px] tabular-nums">{count ? `${count} 期` : "无"}</span>
              <span className="text-xs font-semibold tabular-nums">{y}</span>
            </>
          )
          return (
            <li key={offset} className={cn("flex flex-col items-center text-muted-foreground", far && "hidden sm:flex")}>
              {count ? (
                <button
                  type="button"
                  onClick={() => onYear(y)}
                  className={cn(
                    "flex flex-col items-center transition-opacity hover:text-foreground hover:opacity-100",
                    far ? "opacity-50" : "opacity-80",
                  )}
                >
                  {label}
                </button>
              ) : (
                <span className="flex flex-col items-center opacity-25" title="这一年没有日报">
                  {label}
                </span>
              )}
            </li>
          )
        })}
      </ol>
      <StepButton target={years[at + 1]} label="下一年" onYear={onYear}>
        <ChevronRight />
      </StepButton>
    </nav>
  )
}

type StepButtonProps = { target?: number; label: string; onYear: (year: number) => void; children: React.ReactNode }

function StepButton({ target, label, onYear, children }: StepButtonProps) {
  return (
    <Button
      size="icon"
      className="rounded-full"
      disabled={target === undefined}
      onClick={() => target !== undefined && onYear(target)}
      aria-label={target === undefined ? label : `${label}：${target}`}
    >
      {children}
    </Button>
  )
}

type MonthRangeProps = {
  /** Months of the selected year that have issues; the others cannot be picked. */
  available: Set<number>
  range: Range
  onChange: (range: Range) => void
}

// The months in one row, picked as a range after gr3enk/shadcn-ui-monthpicker. The first click
// shows that month alone and starts a span; the second click closes it, and hovering in between
// previews it. Escape or a click elsewhere leaves the single month.
function MonthRange({ available, range, onChange }: MonthRangeProps) {
  const [start, setStart] = useState<number | null>(null)
  const [hovered, setHovered] = useState<number | null>(null)
  const row = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (start === null) return
    const cancel = (event: Event) => {
      if (event instanceof KeyboardEvent ? event.key === "Escape" : !row.current?.contains(event.target as Node))
        setStart(null)
    }
    document.addEventListener("pointerdown", cancel)
    document.addEventListener("keydown", cancel)
    return () => {
      document.removeEventListener("pointerdown", cancel)
      document.removeEventListener("keydown", cancel)
    }
  }, [start])

  function pick(m: number) {
    if (start === null) {
      setStart(m)
      onChange([m, m])
    } else {
      setStart(null)
      onChange([Math.min(start, m), Math.max(start, m)])
    }
  }

  // While a span is open, it runs from its first month to the one under the pointer.
  const shown: Range =
    start === null ? range : hovered === null ? [start, start] : [Math.min(start, hovered), Math.max(start, hovered)]
  // The ends that show are the first and last month with issues inside the span.
  const picked = MONTHS.filter((m) => available.has(m) && m >= shown[0] && m <= shown[1])
  const from = picked[0] ?? 0
  const to = picked[picked.length - 1] ?? 0

  return (
    <div
      ref={row}
      role="group"
      aria-label="选择月份：先点起始月，再点结束月"
      onPointerLeave={() => setHovered(null)}
      className="mx-auto grid max-w-2xl grid-cols-12"
    >
      {MONTHS.map((m) => {
        const inside = m >= from && m <= to
        const end = m === from || m === to
        return (
          <div
            key={m}
            onPointerEnter={() => available.has(m) && setHovered(m)}
            className={cn(
              "h-8",
              inside && "bg-foreground/10 dark:bg-accent",
              m === from && "rounded-l-full",
              m === to && "rounded-r-full",
            )}
          >
            <Button
              variant={end ? "default" : "ghost"}
              disabled={!available.has(m)}
              aria-pressed={inside && available.has(m)}
              aria-label={`${m} 月`}
              onClick={() => pick(m)}
              onFocus={() => start !== null && setHovered(m)}
              className={cn(
                "h-full w-full rounded-full px-0 font-rounded text-sm font-semibold tabular-nums",
                inside && !end && "hover:bg-background/60",
              )}
            >
              {m}
              <span className="-ml-1 hidden sm:inline">月</span>
            </Button>
          </div>
        )
      })}
    </div>
  )
}

// Headed like a section of an issue: the year small and muted, then the month, the count on the
// right. Its issues are rows of one card, like the brief list.
function MonthGroup({ month, entries, transitionName }: { month: string; entries: Entry[]; transitionName?: string }) {
  const [y, m] = month.split("-").map(Number)
  return (
    <Collapsible defaultOpen asChild>
      <section style={{ viewTransitionName: transitionName }}>
        <h2>
          <CollapsibleTrigger className="group mb-5 flex w-full items-baseline justify-between gap-4 text-left">
            <span className="flex items-baseline gap-3 text-xl font-semibold tracking-tight">
              <span className="font-rounded text-sm font-medium text-muted-foreground tabular-nums">{y}</span>
              <span>{m} 月</span>
            </span>
            <span className="flex items-center gap-1.5 text-xs text-muted-foreground tabular-nums">
              {entries.length} 期
              <ChevronDown className="size-4 transition-transform duration-200 group-data-[state=open]:rotate-180" />
            </span>
          </CollapsibleTrigger>
        </h2>
        <CollapsibleContent className="-m-px overflow-hidden p-px data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
          <Card className="gap-0 overflow-hidden rounded-lg py-0 shadow-none">
            {entries.map((entry, i) => (
              <Fragment key={entry.date}>
                {i > 0 && <Separator />}
                <ArchiveRow entry={entry} />
              </Fragment>
            ))}
          </Card>
        </CollapsibleContent>
      </section>
    </Collapsible>
  )
}

// On a phone the description goes under the date; from sm up it sits between date and count.
function ArchiveRow({ entry }: { entry: Entry }) {
  const { monthDay, weekday } = formatDay(entry.date)
  return (
    <a
      href={issueHref(entry.date)}
      className="grid grid-cols-[1fr_auto] items-baseline gap-x-4 gap-y-1 px-4 py-4 transition-colors hover:bg-muted/50 sm:grid-cols-[7.5rem_1fr_auto] sm:px-6"
    >
      <span className="col-start-1 row-start-1 flex items-baseline gap-2 font-rounded whitespace-nowrap">
        <span className="font-bold tabular-nums">{monthDay}</span>
        <span className="text-xs text-muted-foreground">{weekday}</span>
      </span>
      <span className="col-span-2 row-start-2 line-clamp-2 text-[15px] text-foreground/80 sm:col-span-1 sm:col-start-2 sm:row-start-1 sm:line-clamp-1">
        {entry.description}
      </span>
      <span className="col-start-2 row-start-1 flex items-center gap-2 sm:col-start-3">
        {entry.fallback && <Badge variant="outline">降级版</Badge>}
        <span className="text-xs text-muted-foreground tabular-nums">{entry.items} 条</span>
      </span>
    </a>
  )
}
