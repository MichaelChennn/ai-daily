import { ArrowLeft, ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import { type Lang, strings } from "@/lib/i18n"
import { formatDay, issueHref, pageHref } from "@/lib/issues"

// Previous / next issue at the end of the page, with the archive in between.
export default function Pager({
  older,
  newer,
  lang = "zh",
}: {
  older: string | null
  newer: string | null
  lang?: Lang
}) {
  const t = strings[lang]
  return (
    <nav
      data-pager
      aria-label={t.pager}
      className="mt-16 grid grid-cols-[1fr_auto_1fr] items-center gap-3 border-t pt-6"
    >
      <div>{older && <Step day={older} direction="older" lang={lang} />}</div>
      <Button asChild variant="link" size="sm" className="text-muted-foreground">
        <a href={pageHref("archive/", lang)}>{t.nav.archive}</a>
      </Button>
      <div className="flex justify-end">{newer && <Step day={newer} direction="newer" lang={lang} />}</div>
    </nav>
  )
}

function Step({ day, direction, lang }: { day: string; direction: "older" | "newer"; lang: Lang }) {
  const { monthDay, weekday } = formatDay(day, lang)
  const older = direction === "older"
  return (
    <Button asChild variant="outline" className="h-auto py-2">
      <a href={issueHref(day, lang)} className={older ? "" : "flex-row-reverse"}>
        {older ? <ArrowLeft /> : <ArrowRight />}
        <span className={older ? "flex flex-col items-start" : "flex flex-col items-end"}>
          <span className="text-xs font-normal text-muted-foreground">
            {older ? strings[lang].older : strings[lang].newer}
          </span>
          <span className="tabular-nums">
            {monthDay} {weekday}
          </span>
        </span>
      </a>
    </Button>
  )
}
