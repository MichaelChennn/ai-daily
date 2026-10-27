import { Fragment } from "react"

import { Card } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import ItemMeta from "@/components/ItemMeta"
import SourceLinks from "@/components/SourceLinks"
import type { Lang } from "@/lib/i18n"
import type { Item } from "@/lib/issues"

// Items without a summary (快讯, and every item of a fallback issue) as rows of one card.
export default function BriefList({ items, lang = "zh" }: { items: Item[]; lang?: Lang }) {
  return (
    <Card className="gap-0 rounded-lg py-0 shadow-[0_1px_3px_0_rgb(0_0_0/0.04)] ring-foreground/6 dark:shadow-none dark:ring-foreground/8">
      {items.map((item, i) => (
        <Fragment key={item.title}>
          {i > 0 && <Separator />}
          <div className="group/card flex flex-col gap-2 px-4 py-4 sm:px-6">
            <ItemMeta item={item} lang={lang} />
            <p className="text-[15px] leading-7">
              <span className="font-medium">{item.title}</span>
              {item.summary && <span className="text-foreground/80"> {item.summary}</span>}
            </p>
            <SourceLinks sources={item.sources} lang={lang} />
          </div>
        </Fragment>
      ))}
    </Card>
  )
}
