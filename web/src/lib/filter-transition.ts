// The filters (an issue's sections, the archive's months, the sources' groups) animate a change
// with a same-document view transition; the animations are in global.css, under [data-filtering].
// A new transition skips the running one, so only the newest one cleans up after itself.
let running: ViewTransition | undefined
let listening = false

export function filterTransition(update: () => void, setup = () => {}, cleanup = () => {}) {
  if (!document.startViewTransition || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    update()
    return
  }
  if (!listening) {
    addEventListener("click", forwardClick, true)
    listening = true
  }
  setup()
  const root = document.documentElement
  root.dataset.filtering = ""
  const transition = document.startViewTransition(update)
  running = transition
  transition.ready.catch(() => {}) // rejects when the next click skips it
  transition.finished.finally(() => {
    if (running !== transition) return
    running = undefined
    delete root.dataset.filtering
    cleanup()
  })
}

// While a transition runs, clicks land on <html>, not on what is under the pointer. So a click
// mid-animation ends it and goes to the button it was aimed at (starting the next transition),
// instead of being lost until the animation is over.
function forwardClick(event: MouseEvent) {
  if (!running || event.target !== document.documentElement) return
  const { clientX: x, clientY: y } = event
  running.skipTransition()
  running.finished.then(() => document.elementFromPoint(x, y)?.closest("button")?.click())
}
