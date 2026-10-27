import { type Lang, strings } from "@/lib/i18n"
import type { Item } from "@/lib/issues"

// Publisher logo + name, and the publication time when the data has a real one. The logo sits on
// top of a monogram; when it fails to load, Layout.astro's error listener removes it.
export default function ItemMeta({ item, lang = "zh" }: { item: Item; lang?: Lang }) {
  const { publisher, published } = item
  return (
    <div className="flex min-w-0 items-center gap-2 text-xs text-muted-foreground">
      <span className="relative grid size-4 shrink-0 place-items-center overflow-hidden rounded-[3px] bg-muted text-[10px] font-semibold text-foreground uppercase">
        {publisher.name.charAt(0)}
        <img
          data-logo
          src={publisher.icon}
          alt=""
          width={16}
          height={16}
          loading="lazy"
          referrerPolicy="no-referrer"
          className="absolute inset-0 size-full bg-background object-cover"
        />
      </span>
      <span className="truncate font-medium text-foreground">{publisher.name}</span>
      {published && (
        <>
          <span aria-hidden="true">·</span>
          <time dateTime={published.iso} title={strings[lang].localTime} className="shrink-0 tabular-nums">
            {published.label}
          </time>
        </>
      )}
    </div>
  )
}
