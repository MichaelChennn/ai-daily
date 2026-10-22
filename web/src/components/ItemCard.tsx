import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import ItemMeta from "@/components/ItemMeta"
import SourceLinks from "@/components/SourceLinks"
import type { Item } from "@/lib/issues"

export default function ItemCard({ item }: { item: Item }) {
  return (
    <Card
      size="sm"
      className="gap-3 rounded-lg py-5 shadow-none transition-shadow hover:ring-foreground/25 sm:[--card-spacing:--spacing(6)]"
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
