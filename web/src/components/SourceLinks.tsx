import { ArrowUpRight, MessageSquare } from "lucide-react"
import { cn } from "cn"

import { Badge, badgeVariants } from "@/components/ui/badge"
import { type Lang, strings } from "@/lib/i18n"
import type { Source } from "@/lib/issues"

// The item's sources as compact filled links: first-hand pages carry an arrow, discussions (HN, Reddit) a speech bubble.
// scripts/source-overflow.ts keeps the list to one row and fills in the "+n 更多来源" button.
export default function SourceLinks({
  sources,
  lang = "zh",
  className,
}: {
  sources: Source[]
  lang?: Lang
  className?: string
}) {
  return (
    <ul data-sources className={cn("flex flex-wrap gap-1.5 data-squeezed:flex-nowrap", className)}>
      {sources.map((source) => (
        <li key={source.url} className="max-w-full min-w-0">
          <Badge
            asChild
            variant="secondary"
            className="h-6 max-w-full rounded-md px-2 font-normal"
          >
            <a href={source.url} target="_blank" rel="noopener noreferrer">
              {source.discussion && <MessageSquare aria-hidden="true" />}
              <span className="truncate">{source.label}</span>
              {!source.discussion && <ArrowUpRight aria-hidden="true" className="text-muted-foreground" />}
            </a>
          </Badge>
        </li>
      ))}
      <li data-more hidden className="shrink-0">
        <button
          type="button"
          data-label={strings[lang].moreSources}
          className={cn(badgeVariants({ variant: "ghost" }), "h-6 cursor-pointer rounded-md px-2 font-normal text-muted-foreground")}
        />
      </li>
    </ul>
  )
}
