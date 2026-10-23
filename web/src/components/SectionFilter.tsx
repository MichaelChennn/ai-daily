import { useState } from "react"
import { flushSync } from "react-dom"

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { filterTransition } from "@/lib/filter-transition"

type Props = { sections: { id: string; label: string }[] }

const ALL = "all"

// Shows one section of the issue, or all of them. The sections are server-rendered elements
// with data-section; this hides the others, animated with a view transition where the browser
// has them (the animations are in global.css).
export default function SectionFilter({ sections }: Props) {
  const [value, setValue] = useState(ALL)

  function select(next: string) {
    if (!next) return // clicking the active filter again keeps it
    const sectionEls = [...document.querySelectorAll<HTMLElement>("[data-section]")]
    const update = () => {
      flushSync(() => setValue(next))
      for (const el of sectionEls) el.hidden = next !== ALL && el.dataset.section !== next
    }
    // Each section and the pager move on their own for this transition; the issue body (which
    // slides as one between issues) does not.
    const issue = document.querySelector<HTMLElement>("[data-issue]")
    const moving = [...sectionEls, ...(issue?.querySelectorAll<HTMLElement>("[data-pager]") ?? [])]
    filterTransition(
      update,
      () => {
        issue?.style.setProperty("view-transition-name", "none")
        for (const el of moving) el.style.viewTransitionName = `filter-${el.dataset.section ?? "pager"}`
      },
      () => {
        issue?.style.removeProperty("view-transition-name")
        for (const el of moving) el.style.viewTransitionName = ""
      },
    )
  }

  const options = [{ id: ALL, label: "全部" }, ...sections]
  return (
    <div className="-mx-4 overflow-x-auto px-4 [scrollbar-width:none] sm:mx-0 sm:px-0">
      <ToggleGroup
        type="single"
        value={value}
        onValueChange={select}
        variant="outline"
        size="sm"
        spacing={1}
        aria-label="按分类筛选"
        className="mx-auto"
      >
        {options.map((option) => (
          <ToggleGroupItem
            key={option.id}
            value={option.id}
            className="rounded-full px-3.5 text-[13px] font-normal data-[state=on]:border-foreground data-[state=on]:bg-foreground data-[state=on]:text-background"
          >
            {option.label}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    </div>
  )
}
