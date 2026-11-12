// The theme toggle and the language switch in the bottom-left corner, on every page in the
// issue #43 design. Inlined before the page's own script.
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
})()
