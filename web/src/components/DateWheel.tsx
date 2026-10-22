import { ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "cn"

import { Button } from "@/components/ui/button"
import { addDays, formatDay, issueHref } from "@/lib/issues"

type Props = {
  date: string
  /** Dates that have an issue page. */
  published: Set<string>
  older: string | null
  newer: string | null
}

// Five calendar days centred on this issue. Days with an issue link to it; days without one
// (gaps, the future) stay as faded labels. The arrows skip to the nearest issue either way.
export default function DateWheel({ date, published, older, newer }: Props) {
  const current = formatDay(date)
  return (
    <nav aria-label="切换期数" className="flex items-center justify-between gap-2 pt-10 pb-8">
      <StepButton target={older} label="上一期">
        <ChevronLeft />
      </StepButton>
      <ol className="flex items-center justify-center gap-3 font-rounded [view-transition-name:date-wheel] sm:gap-6">
        {[-2, -1, 0, 1, 2].map((offset) => {
          if (offset === 0) {
            return (
              <li
                key={offset}
                aria-current="date"
                className="flex flex-col items-center rounded-2xl bg-muted px-4 py-2.5 ring-1 ring-foreground/5"
              >
                <span className="text-xs font-medium text-muted-foreground">
                  {current.year} · {current.weekday}
                </span>
                <span className="text-base leading-6 font-bold tabular-nums whitespace-nowrap">{current.monthDay}</span>
              </li>
            )
          }
          const day = addDays(date, offset)
          const { monthDay, weekday } = formatDay(day)
          const far = Math.abs(offset) === 2
          const label = (
            <>
              <span className="text-[11px]">{weekday}</span>
              <span className="text-xs font-semibold tabular-nums whitespace-nowrap">{monthDay}</span>
            </>
          )
          const className = cn(
            "flex flex-col items-center text-muted-foreground",
            far && "hidden sm:flex",
          )
          return (
            <li key={offset} className={className}>
              {published.has(day) ? (
                <a
                  href={issueHref(day)}
                  className={cn(
                    "flex flex-col items-center transition-opacity hover:text-foreground hover:opacity-100",
                    far ? "opacity-50" : "opacity-80",
                  )}
                >
                  {label}
                </a>
              ) : (
                <span className="flex flex-col items-center opacity-25" title="这一天没有日报">
                  {label}
                </span>
              )}
            </li>
          )
        })}
      </ol>
      <StepButton target={newer} label="下一期">
        <ChevronRight />
      </StepButton>
    </nav>
  )
}

function StepButton({ target, label, children }: { target: string | null; label: string; children: React.ReactNode }) {
  if (!target) {
    return (
      <Button size="icon" className="rounded-full" disabled aria-label={label}>
        {children}
      </Button>
    )
  }
  return (
    <Button asChild size="icon" className="rounded-full">
      <a href={issueHref(target)} aria-label={`${label}：${formatDay(target).monthDay}`}>
        {children}
      </a>
    </Button>
  )
}
