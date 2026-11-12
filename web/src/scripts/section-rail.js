// The pages without an issue (the archive, the sources), ported from their issue #43 prototypes:
// SectionRail (the issue pages' rail with a tick per section: the same window, dock, wheel and
// phone scrubber), the section in view lit on the rail, the arrow back to the issue the reader came
// from, the GitHub repos' popover on the sources page, and the entrance.
//
// Both pages inline this at the end of <body>, after controls.js.
;(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches
  const finePointer = matchMedia("(hover: hover) and (pointer: fine)").matches
  const root = document.documentElement
  const $ = (s) => document.querySelector(s)

  const rail = $("#rail")
  const inner = $("#ticksInner")
  const ticksBox = $("#ticks")
  const ticks = [...inner.querySelectorAll(".tick")]
  const ICONS = [...rail.querySelectorAll(".icon-btn")]
  const ret = $("#ret")
  const KEYS = ticks.map((t) => t.hash.slice(1)) // rail order: the archive's oldest month first
  const sections = [...document.querySelectorAll("#main > section[id]")] // page order
  const TOP = sections[0]?.id // the section at the top of the page
  const W = Math.min(20, KEYS.length)
  const EDGE = 4
  const LAND = 7
  const L = 0.1
  const I = 0.4
  const PITCH = 13
  const SWITCH = "press-switch" // set when going between an issue and the archive, either way
  // the window opens on the top section's end of the rail: its start, or the archive's bottom
  let start = KEYS.indexOf(TOP) < W ? 0 : KEYS.length - W

  /* ---------- where the arrow goes: the issue the reader came from, else the newest ---------- */
  // #ret links to the home page (the newest issue) and lists every issue's date, newest first.
  let from = null
  let switched = false
  try {
    from = sessionStorage.getItem("press-from")
    switched = Date.now() - Number(sessionStorage.getItem(SWITCH)) < 10000
    sessionStorage.removeItem(SWITCH)
  } catch {}
  const issues = ret.dataset.issues.split(" ")
  if (from && from !== issues[0] && issues.includes(from)) ret.href = new URL(`${from}/`, ret.href).href
  // Leaving for an issue or the other page with a rail: it plays only the rail's entrance, as this
  // one did.
  const plainClick = (e) => e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey
  document.addEventListener("click", (e) => {
    if (!plainClick(e) || !e.target.closest(".arc, #ret, #logo, .icon-btn:not([aria-current])")) return
    try {
      sessionStorage.setItem(SWITCH, String(Date.now()))
    } catch {}
  })

  /* ---------- the rail's window ---------- */
  function place(animate) {
    inner.style.transition = animate && !reduce ? "" : "none"
    inner.style.transform = `translateY(${-start * PITCH}px)`
  }
  function reveal(i, jump) {
    const p = i - start
    let s = start
    if (p < EDGE) s = i - (jump ? LAND : EDGE)
    else if (p > W - 1 - EDGE) s = i - (W - 1 - (jump ? LAND : EDGE))
    s = Math.max(0, Math.min(KEYS.length - W, s))
    if (s !== start) {
      start = s
      place(true)
    }
  }
  function scrollBy(n) {
    const s = Math.max(0, Math.min(KEYS.length - W, start + n))
    if (s !== start) {
      start = s
      place(true)
      return true
    }
    return false
  }
  let wheelAcc = 0
  rail.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault()
      wheelAcc += e.deltaY
      while (Math.abs(wheelAcc) >= 40) {
        scrollBy(Math.sign(wheelAcc))
        wheelAcc -= Math.sign(wheelAcc) * 40
      }
    },
    { passive: false },
  )

  // Stripe Press: scale = max(1, cos(|e-i|/N*PI)*2 + 2.5)
  function dock(e) {
    if (!finePointer && !touching) return
    document.body.classList.add("rail-hover")
    rail.classList.add("labels-on")
    ticks.forEach((t, i) => {
      const o = (Math.abs(e - i) / (W + ICONS.length)) * Math.PI
      t.firstElementChild.style.transform = `scaleX(${Math.max(1, Math.cos(o) * 2 + 2.5)})`
    })
  }
  function undock() {
    document.body.classList.remove("rail-hover")
    rail.classList.remove("labels-on")
    ticks.forEach((t) => (t.firstElementChild.style.transform = "scaleX(1)"))
  }
  ticks.forEach((t, i) => {
    t.addEventListener("mouseenter", () => dock(i))
    t.addEventListener("mouseleave", undock)
    t.addEventListener("click", (e) => {
      if (!plainClick(e)) return
      e.preventDefault()
      reveal(i, true)
      jumpTo(KEYS[i])
    })
  })
  ICONS.forEach((a, k) => {
    a.addEventListener("mouseenter", () => dock(start + W + k))
    a.addEventListener("mouseleave", undock)
  })
  ret.addEventListener("mouseenter", () => dock(start - 1))
  ret.addEventListener("mouseleave", undock)
  // this page's own icon goes back to the top
  const self = rail.querySelector(".icon-btn[aria-current]")
  self.addEventListener("click", (e) => {
    if (!plainClick(e)) return
    e.preventDefault()
    jumpTo(TOP)
  })

  /* ---------- sections: jump to one, light the one in view ---------- */
  let lock = 0
  let activeK = null
  function setActive(k) {
    if (k === activeK) return
    activeK = k
    ticks.forEach((t, i) => {
      const on = KEYS[i] === k
      t.classList.toggle("active", on)
      if (on) t.setAttribute("aria-current", "true")
      else t.removeAttribute("aria-current")
    })
    reveal(KEYS.indexOf(k), false)
  }
  function jumpTo(k) {
    const sec = document.getElementById(k)
    // the first section is the top of the page
    const y = k === TOP ? 0 : sec.getBoundingClientRect().top + scrollY - 32
    window.scrollTo({ top: y, behavior: reduce ? "auto" : "smooth" })
    setActive(k) // lit now; the scroll spy agrees once the page lands
    lock = Date.now() + 900
  }
  // the section whose heading last passed 30% of the viewport; at the very bottom, the last one
  function spy() {
    if (Date.now() < lock || !sections.length) return
    let k = sections[0].id
    for (const s of sections) if (s.getBoundingClientRect().top <= innerHeight * 0.3) k = s.id
    if (innerHeight + scrollY >= root.scrollHeight - 2) k = sections.at(-1).id
    setActive(k)
  }
  let raf = 0
  addEventListener(
    "scroll",
    () => {
      if (!raf)
        raf = requestAnimationFrame(() => {
          raf = 0
          spy()
        })
    },
    { passive: true },
  )

  /* ---------- phone: press and drag like an index scrubber ---------- */
  let touching = false
  let hit = -1
  let edgeTimer = 0
  let lastY = 0
  const bubble = $("#bubble")
  function tickAt(y) {
    const r = ticksBox.getBoundingClientRect()
    const p = Math.floor((y - r.top) / PITCH)
    return p < 0 || p >= W ? -1 : start + p
  }
  function scrub(y) {
    lastY = y
    const r = ticksBox.getBoundingClientRect()
    const dir = y < r.top - 6 ? -1 : y > r.bottom + 6 ? 1 : 0
    clearInterval(edgeTimer)
    if (dir)
      edgeTimer = setInterval(() => {
        if (scrollBy(dir)) {
          hit = -2
          scrub(lastY)
        }
      }, 90)
    const i = tickAt(Math.max(r.top, Math.min(r.bottom - 1, y)))
    if (i === hit) return
    ticks.forEach((t) => t.classList.remove("touch-hit"))
    hit = i
    if (i < 0) {
      bubble.hidden = true
      return
    }
    const t = ticks[i]
    t.classList.add("touch-hit")
    dock(i)
    const span = document.createElement("span")
    span.className = "t"
    span.textContent = t.getAttribute("aria-label")
    bubble.replaceChildren(span)
    bubble.style.top = r.top + (i - start) * PITCH + PITCH / 2 + "px"
    bubble.hidden = false
    if (navigator.vibrate) navigator.vibrate(4)
  }
  ticksBox.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "mouse") return
    touching = true
    e.preventDefault()
    ticksBox.setPointerCapture(e.pointerId)
    scrub(e.clientY)
  })
  ticksBox.addEventListener("pointermove", (e) => {
    if (touching) scrub(e.clientY)
  })
  const endScrub = (e) => {
    if (!touching) return
    touching = false
    clearInterval(edgeTimer)
    bubble.hidden = true
    undock()
    const t = ticks[hit]
    ticks.forEach((t) => t.classList.remove("touch-hit"))
    hit = -1
    if (t && e.type === "pointerup") jumpTo(KEYS[ticks.indexOf(t)])
  }
  ticksBox.addEventListener("pointerup", endScrub)
  ticksBox.addEventListener("pointercancel", endScrub)
  ticksBox.addEventListener("click", (e) => {
    if (e.pointerType && e.pointerType !== "mouse") e.preventDefault()
  })

  /* ---------- the sources page's repo stack: the issue pages' source stack popover ---------- */
  document.querySelectorAll(".srcs").forEach((b) => {
    const pop = b.querySelector(".pop")
    const button = b.querySelector("button")
    let timer
    const open = () => {
      clearTimeout(timer)
      document.querySelectorAll(".pop.open").forEach((p) => p !== pop && p.classList.remove("open"))
      pop.classList.add("open")
      button.setAttribute("aria-expanded", "true")
    }
    const close = () => {
      timer = setTimeout(() => {
        pop.classList.remove("open")
        button.setAttribute("aria-expanded", "false")
      }, 120)
    }
    if (finePointer) {
      b.addEventListener("mouseenter", open)
      b.addEventListener("mouseleave", close)
    }
    b.addEventListener("click", (e) => {
      if (e.target.closest(".pop a")) return
      e.preventDefault()
      e.stopPropagation()
      pop.classList.contains("open") ? close() : open()
    })
  })
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".srcs")) document.querySelectorAll(".pop.open").forEach((p) => p.classList.remove("open"))
  })
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") document.querySelectorAll(".pop.open").forEach((p) => p.classList.remove("open"))
  })

  /* ---------- boot: the issue pages' entrance; from an issue, only the rail's ---------- */
  const navType = performance.getEntriesByType("navigation")[0]?.type
  const intro = !reduce && navType !== "back_forward"
  const pageIntro = intro && !switched
  place(false)
  spy()
  if (!intro) {
    rail.classList.add("still", "ready")
    ret.style.animationDuration = "0s"
    requestAnimationFrame(() => requestAnimationFrame(() => rail.classList.remove("still")))
    return
  }
  const els = pageIntro
    ? [...document.querySelectorAll("#main .drop")].filter((el) => el.getBoundingClientRect().top <= innerHeight)
    : []
  if (pageIntro) document.body.classList.add("intro")
  const span = (W + ICONS.length - 1) * L
  // one beat per row: the sources page's cards in a row drop together
  const top = (el) => Math.round(el.getBoundingClientRect().top)
  const rows = [...new Set(els.map(top))]
  const step = rows.length > 1 ? Math.max(L, span / (rows.length - 1)) : 0
  els.forEach((el) => el.style.setProperty("--d", I + rows.indexOf(top(el)) * step + "s"))
  root.style.setProperty("--logo-d", I - L + "s")
  ret.style.animationDelay = I - L + "s"
  ticks.forEach((t, i) => {
    const p = i - start
    t.style.transitionDelay = p < 0 || p >= W ? "0s" : `${p * L + I}s`
  })
  ICONS.forEach((a, k) => (a.style.transitionDelay = `${(W + k) * L + I}s`))
  requestAnimationFrame(() => requestAnimationFrame(() => rail.classList.add("ready")))
  const end = I + Math.max(span + 0.3, (rows.length - 1) * step + 0.9) + 0.1
  setTimeout(() => {
    ticks.forEach((t) => (t.style.transitionDelay = "0s"))
    ICONS.forEach((a) => (a.style.transitionDelay = "0s"))
    document.body.classList.remove("intro")
  }, end * 1000)
})()
