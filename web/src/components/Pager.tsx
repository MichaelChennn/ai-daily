import { ArrowLeft, ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import { formatDay, href, issueHref } from "@/lib/issues"

// Previous / next issue at the end of the page, with the archive in between.
export default function Pager({ older, newer }: { older: string | null; newer: string | null }) {
  return (
    <nav data-pager aria-label="翻页" className="mt-16 grid grid-cols-[1fr_auto_1fr] items-center gap-3 border-t pt-6">
      <div>{older && <Step day={older} direction="older" />}</div>
      <Button asChild variant="link" size="sm" className="text-muted-foreground">
        <a href={href("archive/")}>往期归档</a>
      </Button>
      <div className="flex justify-end">{newer && <Step day={newer} direction="newer" />}</div>
    </nav>
  )
}

function Step({ day, direction }: { day: string; direction: "older" | "newer" }) {
  const { monthDay, weekday } = formatDay(day)
  const older = direction === "older"
  return (
    <Button asChild variant="outline" className="h-auto py-2">
      <a href={issueHref(day)} className={older ? "" : "flex-row-reverse"}>
        {older ? <ArrowLeft /> : <ArrowRight />}
        <span className={older ? "flex flex-col items-start" : "flex flex-col items-end"}>
          <span className="text-xs font-normal text-muted-foreground">{older ? "上一期" : "下一期"}</span>
          <span className="tabular-nums">
            {monthDay} {weekday}
          </span>
        </span>
      </a>
    </Button>
  )
}
