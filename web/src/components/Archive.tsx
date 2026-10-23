import { cn } from "cn"
import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { flushSync } from "react-dom"

import { Badge } from "@/components/ui/badge"
import { buttonVariants } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { formatDay, issueHref } from "@/lib/issues"

export type Entry = { date: string; fallback: boolean; description: string; items: number }

type Props = { entries: Entry[] }

/** A span of months, both ends included. */
type Range = [number, number]

const ALL_MONTHS: Range = [1, 12]
const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1)

const yearOf = (day: string) => Number(day.slice(0, 4))
const monthOf = (day: string) => Number(day.slice(5, 7))

// Every issue, newest first, grouped by month: pick one year and a span of its months. Changing
// the selection animates the month groups with a view transition, like the section filter on an
// issue page (the animations are in global.css).
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

  return (
    <>
      <header className="pt-10 pb-8">
        <h1 className="text-2xl font-semibold tracking-tight">往期归档</h1>
        <p className="mt-1 text-sm text-muted-foreground tabular-nums">共 {shown.length} 期</p>
      </header>

      <MonthRangeCard
        years={years}
        year={year}
        onYear={selectYear}
        available={new Set(inYear.map((e) => monthOf(e.date)))}
        range={range}
        onChange={selectMonths}
      />

      <div className="mt-10 flex flex-col gap-8">
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

type MonthRangeCardProps = {
  /** Years with issues, oldest first. */
  years: number[]
  year: number
  onYear: (year: number) => void
  /** Months of the selected year that have issues; the others cannot be picked. */
  available: Set<number>
  range: Range
  onChange: (range: Range) => void
}

// A month range picker after gr3enk/shadcn-ui-monthpicker, cut down to one year in one row. The
// first click shows that month alone and starts a span; the second click closes it, and hovering
// in between previews it. Escape or a click elsewhere leaves the single month.
function MonthRangeCard({ years, year, onYear, available, range, onChange }: MonthRangeCardProps) {
  const [start, setStart] = useState<number | null>(null)
  const [hovered, setHovered] = useState<number | null>(null)
  const card = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (start === null) return
    const cancel = (event: Event) => {
      if (event instanceof KeyboardEvent ? event.key === "Escape" : !card.current?.contains(event.target as Node))
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

  function step(by: number) {
    setStart(null)
    onYear(years[years.indexOf(year) + by])
  }

  // While a span is open, it runs from its first month to the one under the pointer.
  const shown: Range =
    start === null ? range : hovered === null ? [start, start] : [Math.min(start, hovered), Math.max(start, hovered)]
  // The ends that show are the first and last month with issues inside the span.
  const picked = MONTHS.filter((m) => available.has(m) && m >= shown[0] && m <= shown[1])
  const from = picked[0] ?? 0
  const to = picked[picked.length - 1] ?? 0

  const chevron = cn(buttonVariants({ variant: "outline", size: "icon" }), "size-7")

  return (
    <div ref={card} className="rounded-xl border bg-card p-3 text-card-foreground shadow-md">
      <div className="relative flex h-7 items-center justify-center">
        <button
          type="button"
          onClick={() => step(-1)}
          disabled={year === years[0]}
          aria-label="上一年"
          className={cn(chevron, "absolute left-0")}
        >
          <ChevronLeft className="opacity-50" />
        </button>
        <span className="font-rounded text-base font-bold tabular-nums">{year}</span>
        <button
          type="button"
          onClick={() => step(1)}
          disabled={year === years[years.length - 1]}
          aria-label="下一年"
          className={cn(chevron, "absolute right-0")}
        >
          <ChevronRight className="opacity-50" />
        </button>
      </div>
      <div className="mt-3 grid grid-cols-12" onPointerLeave={() => setHovered(null)}>
        {MONTHS.map((m) => {
          const inside = m >= from && m <= to
          const end = m === from || m === to
          return (
            <div
              key={m}
              onPointerEnter={() => available.has(m) && setHovered(m)}
              className={cn(
                "h-9",
                inside && "bg-foreground/10 dark:bg-accent",
                m === from && "rounded-l-md",
                m === to && "rounded-r-md",
              )}
            >
              <button
                type="button"
                disabled={!available.has(m)}
                aria-pressed={inside && available.has(m)}
                aria-label={`${m} 月`}
                onClick={() => pick(m)}
                onFocus={() => start !== null && setHovered(m)}
                className={cn(
                  buttonVariants({ variant: end ? "default" : "ghost" }),
                  "h-full w-full px-0 font-rounded text-sm font-semibold tabular-nums",
                  inside && !end && "hover:bg-background/60",
                )}
              >
                {m}
                <span className="hidden sm:inline">月</span>
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function MonthGroup({ month, entries, transitionName }: { month: string; entries: Entry[]; transitionName?: string }) {
  const [y, m] = month.split("-").map(Number)
  return (
    <Collapsible defaultOpen asChild>
      <section style={{ viewTransitionName: transitionName }}>
        <h2>
          <CollapsibleTrigger className="group flex w-full items-center justify-between gap-4 py-1 text-left">
            <span className="text-base font-semibold tracking-tight">
              {y} 年 {m} 月
              <span className="ml-2 text-sm font-normal text-muted-foreground tabular-nums">· {entries.length} 期</span>
            </span>
            <ChevronDown className="size-4 text-muted-foreground transition-transform duration-200 group-data-[state=open]:rotate-180" />
          </CollapsibleTrigger>
        </h2>
        <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
          <ol className="flex flex-col gap-1 pt-3">
            {entries.map((entry) => (
              <li key={entry.date}>
                <ArchiveRow entry={entry} />
              </li>
            ))}
          </ol>
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
      className="-mx-3 grid grid-cols-[1fr_auto] items-baseline gap-x-4 gap-y-1 rounded-lg px-3 py-3 transition-colors hover:bg-muted sm:grid-cols-[7.5rem_1fr_auto]"
    >
      <span className="col-start-1 row-start-1 flex items-baseline gap-2 font-rounded whitespace-nowrap">
        <span className="font-bold tabular-nums">{monthDay}</span>
        <span className="text-xs text-muted-foreground">{weekday}</span>
      </span>
      <span className="col-span-2 row-start-2 line-clamp-2 text-sm text-foreground/80 sm:col-span-1 sm:col-start-2 sm:row-start-1 sm:line-clamp-1">
        {entry.description}
      </span>
      <span className="col-start-2 row-start-1 flex items-center gap-2 sm:col-start-3">
        {entry.fallback && <Badge variant="outline">降级版</Badge>}
        <span className="text-xs text-muted-foreground tabular-nums">{entry.items} 条</span>
      </span>
    </a>
  )
}
