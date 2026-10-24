import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import ItemMeta from "@/components/ItemMeta"
import SourceLinks from "@/components/SourceLinks"
import type { Item } from "@/lib/issues"

export default function ItemCard({ item }: { item: Item }) {
  return (
    <Card
      size="sm"
      className="gap-3 rounded-lg py-5 shadow-[0_1px_3px_0_rgb(0_0_0/0.04)] ring-foreground/6 transition-[box-shadow,translate] duration-200 ease-out hover:-translate-y-0.5 hover:shadow-[0_10px_28px_-8px_rgb(0_0_0/0.16)] motion-reduce:hover:translate-y-0 dark:shadow-none dark:ring-foreground/8 dark:hover:shadow-[0_10px_28px_-8px_rgb(0_0_0/0.6)] dark:hover:ring-foreground/15 sm:[--card-spacing:--spacing(6)]"
    >
      <CardHeader className="gap-2.5">
        <ItemMeta item={item} />
        <h3 className="text-lg leading-snug font-semibold tracking-tight text-pretty sm:text-xl">{item.title}</h3>
      </CardHeader>
      <CardContent>
        <p className="text-[15px] leading-7 text-foreground/80">{item.summary}</p>
      </CardContent>
      <CardFooter className="pt-1">
        <SourceLinks sources={item.sources} />
      </CardFooter>
    </Card>
  )
}
