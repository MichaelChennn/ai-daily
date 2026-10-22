// Source lists (SourceLinks) keep to one row: the sources that do not fit are hidden behind a
// "+n 更多来源" button that shows them all. Without JS every source shows, wrapped.

const expanded = new WeakSet<HTMLElement>()
const widths = new WeakMap<HTMLElement, number>()

function fit(list: HTMLElement) {
  if (expanded.has(list)) return
  const more = list.querySelector<HTMLElement>("[data-more]")!
  const button = more.querySelector("button")!
  const items = [...list.children].filter((li): li is HTMLElement => li !== more)
  for (const li of items) li.hidden = false
  more.hidden = true
  list.removeAttribute("data-squeezed")
  const top = items[0].offsetTop
  if (items.at(-1)!.offsetTop === top) return // one row already (or the list is not displayed)

  // Hide sources from the end until the last shown one and the button share the first row.
  more.hidden = false
  let shown = items.length
  const count = () => (button.textContent = `+${items.length - shown} 更多来源`)
  count()
  while (shown > 1 && (items[shown - 1].offsetTop !== top || more.offsetTop !== top)) {
    items[--shown].hidden = true
    count()
  }
  // Even the first source alone is too wide: keep the row and let it truncate.
  if (more.offsetTop !== top) list.setAttribute("data-squeezed", "")
}

const resized = new ResizeObserver((entries) => {
  for (const { target, contentRect } of entries) {
    const list = target as HTMLElement
    // Hiding sources changes the height only; refit when the width changes (resize, a filtered
    // section shown again).
    if (widths.get(list) === contentRect.width) continue
    widths.set(list, contentRect.width)
    fit(list)
  }
})

const lists = document.querySelectorAll<HTMLElement>("[data-sources]")
for (const list of lists) {
  fit(list)
  resized.observe(list)
  list.querySelector("[data-more] button")!.addEventListener("click", () => {
    expanded.add(list)
    list.removeAttribute("data-squeezed")
    for (const li of list.children) (li as HTMLElement).hidden = false
    list.querySelector<HTMLElement>("[data-more]")!.hidden = true
  })
}
// Web fonts change the badge widths after the first fit.
document.fonts.ready.then(() => lists.forEach(fit))
