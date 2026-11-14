// The theme toggle and the language switch in the bottom-left corner, on every page in the
// issue #43 design, and the ⓘ toolbar in the bottom-right corner of an issue page. Inlined before the page's own script.
;(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches
  const root = document.documentElement
  const $ = (s) => document.querySelector(s)

  /* ---------- 日夜切换 (the first paint's theme is set in PressLayout.astro) ---------- */
  const darkMQ = matchMedia("(prefers-color-scheme: dark)")
  let savedTheme = null
  try {
    savedTheme = localStorage.getItem("theme")
  } catch {}
  darkMQ.addEventListener("change", (e) => {
    if (!savedTheme) root.dataset.theme = e.matches ? "dark" : "light"
  })
  $("#theme").addEventListener("click", () => {
    savedTheme = root.dataset.theme === "dark" ? "light" : "dark"
    root.dataset.theme = savedTheme
    try {
      localStorage.setItem("theme", savedTheme)
    } catch {}
  })

  // The language switch remembers the choice, which then outranks the browser's language, and
  // tells the next page to swap 文 and A from where they were here.
  const langBtn = $("#lang")
  langBtn.addEventListener("click", () => {
    try {
      localStorage.setItem("lang", langBtn.dataset.lang)
      sessionStorage.setItem("press-lang", "1")
    } catch {}
  })
  let swapLang = false
  try {
    swapLang = sessionStorage.getItem("press-lang") === "1"
    sessionStorage.removeItem("press-lang")
  } catch {}
  if (swapLang && !reduce) {
    langBtn.classList.add("from", "moving")
    requestAnimationFrame(() => requestAnimationFrame(() => langBtn.classList.remove("from")))
    setTimeout(() => langBtn.classList.remove("moving"), 600)
  }

  /* ---------- ⓘ: opens the toolbar to its left; a click elsewhere or Esc closes it ---------- */
  const info = $("#info")
  const tools = $("#tools")
  if (info) {
    const open = (on) => {
      tools.classList.toggle("open", on)
      info.setAttribute("aria-expanded", String(on))
    }
    info.addEventListener("click", (e) => {
      e.stopPropagation()
      open(!tools.classList.contains("open"))
    })
    document.addEventListener("click", (e) => {
      if (!tools.contains(e.target)) open(false)
    })
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && tools.classList.contains("open")) {
        open(false)
        info.focus()
      }
    })
  }
})()
