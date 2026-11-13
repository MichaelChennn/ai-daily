// The issue page's behaviour, ported from the issue #43 prototype: the timeline (Stripe Press's
// rail), the entrance, cards folding into a stack of spines, briefs opening as they scroll in and
// the source popovers. The theme and language buttons are in controls.js.
//
// IssuePage.astro inlines this at the end of <body>, before the element the first paint waits
// for, so everything here is in place before anything shows. Each issue is its own page: going
// to another one hands the rail's window over in sessionStorage, and the new page then skips
// the entrance and slides the window the way the prototype did in place.
;(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches
  const finePointer = matchMedia("(hover: hover) and (pointer: fine)").matches
  const root = document.documentElement
  const $ = (s) => document.querySelector(s)
  const css = (n) => parseFloat(getComputedStyle(root).getPropertyValue(n))

  /* ================= rail ================= */
  const rail = $("#rail")
  const inner = $("#ticksInner")
  const ticksBox = $("#ticks")
  const ticks = [...inner.querySelectorAll(".tick")]
  const ICONS = [...rail.querySelectorAll(".icon-btn")]
  const ret = $("#ret")
  const DAYS = ticks.map((t) => t.dataset.iso)
  const current = rail.dataset.current
  const latest = rail.dataset.latest
  const W = Math.min(20, DAYS.length) // visible ticks, fixed like Stripe's book count
  const EDGE = 4 // clicking one of the 4 ticks nearest an edge scrolls the window
  const LAND = 7 // ...so that tick lands 7 from that edge
  const L = 0.1
  const I = 0.4 // Stripe: transitionDelay = i*L + I (cards and rail start together here)
  const PITCH = 13
  const KEY = "press-nav"
  const SWITCH = "press-switch" // set when going between an issue and the archive, either way
  let start = Math.max(0, DAYS.length - W)

  // Arriving from another issue page through the rail: where its window was and where it goes.
  let arrived = null
  try {
    arrived = JSON.parse(sessionStorage.getItem(KEY) || "null")
    sessionStorage.removeItem(KEY)
  } catch {}
  if (arrived && (Date.now() - arrived.t > 10000 || arrived.n !== DAYS.length)) arrived = null
  const navType = performance.getEntriesByType("navigation")[0]?.type
  const intro = !reduce && !arrived && navType !== "back_forward"
  // Arriving from the archive: the rail's ticks mean something else now, so only the rail plays
  // its entrance; the logo and the cards stay put (the page cross-fades in).
  let switched = false
  try {
    switched = Date.now() - Number(sessionStorage.getItem(SWITCH)) < 10000
    sessionStorage.removeItem(SWITCH)
  } catch {}
  const pageIntro = intro && !switched

  // Without the entrance the ticks are just there: no scale-in, no fade.
  if (!intro) {
    rail.classList.add("still", "ready")
    requestAnimationFrame(() => requestAnimationFrame(() => rail.classList.remove("still")))
  }

  function place(animate) {
    inner.style.transition = animate && !reduce ? "" : "none"
    inner.style.transform = `translateY(${-start * PITCH}px)`
  }
  // Where the window goes to keep tick i away from the edges; `jump` = it was clicked inside the
  // edge zone, so move it well inside.
  function target(i, jump) {
    const p = i - start
    let s = start
    if (p < EDGE) s = i - (jump ? LAND : EDGE)
    else if (p > W - 1 - EDGE) s = i - (W - 1 - (jump ? LAND : EDGE))
    return Math.max(0, Math.min(DAYS.length - W, s))
  }
  function reveal(i, jump) {
    const s = target(i, jump)
    if (s !== start) {
      start = s
      place(true)
    }
  }
  function scrollBy(n) {
    const s = Math.max(0, Math.min(DAYS.length - W, start + n))
    if (s !== start) {
      start = s
      place(true)
      return true
    }
    return false
  }

  // Go to an issue: the same one scrolls back to the top, another is a page load that carries
  // the window over.
  function go(link, to) {
    if (link.dataset.iso === current || (link === ret && current === latest)) {
      window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" })
      if (to !== start) {
        start = to
        place(true)
      }
      return
    }
    try {
      sessionStorage.setItem(
        KEY,
        JSON.stringify({ t: Date.now(), n: DAYS.length, from: start, to, off: rail.classList.contains("off-latest") }),
      )
    } catch {}
    location.href = link.href
  }
  const plainClick = (e) => e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey

  ticks.forEach((t, i) => {
    t.addEventListener("mouseenter", () => dock(i))
    t.addEventListener("mouseleave", undock)
    t.addEventListener("click", (e) => {
      if (t.classList.contains("empty") || !plainClick(e)) return
      e.preventDefault()
      go(t, target(i, true))
    })
  })
  // icon rows sit right after the visible window in Stripe's indicator list
  ICONS.forEach((a, k) => {
    a.addEventListener("mouseenter", () => dock(start + W + k))
    a.addEventListener("mouseleave", undock)
    // the archive's arrow comes back to this issue
    a.addEventListener("click", () => {
      try {
        sessionStorage.setItem("press-from", current)
        sessionStorage.setItem(SWITCH, String(Date.now()))
      } catch {}
    })
  })
  // Stripe: returnButton mouseenter -> handleMouseEnterIndicator(-1), docked just above the first tick
  ret.addEventListener("mouseenter", () => dock(start - 1))
  ret.addEventListener("mouseleave", undock)
  // back to the newest issue, with the window scrolled so it sits at the bottom again
  const goLatest = (e) => {
    if (!plainClick(e)) return
    e.preventDefault()
    go(ret, Math.max(0, DAYS.length - W))
  }
  ret.addEventListener("click", goLatest)
  $("#logo").addEventListener("click", goLatest)

  // wheel over the rail scrolls the window a day at a time
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

  // Stripe Press: scale = max(1, cos(|e-i|/N*PI)*2 + 2.5), fill transition transform .2s
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

  /* --- phone: press and drag like an index scrubber; holding past either end keeps scrolling --- */
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
    const label = t.querySelector(".label")
    bubble.innerHTML = ""
    for (const s of label.children) {
      const span = document.createElement("span")
      span.className = s.classList.contains("d") ? "d" : "t"
      span.textContent = s.textContent
      bubble.append(span)
    }
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
    if (t && !t.classList.contains("empty") && e.type === "pointerup") go(t, target(ticks.indexOf(t), false))
  }
  ticksBox.addEventListener("pointerup", endScrub)
  ticksBox.addEventListener("pointercancel", endScrub)
  // the scrub handles taps itself; keep the tap's synthetic click from following the link too
  ticksBox.addEventListener("click", (e) => {
    if (e.pointerType && e.pointerType !== "mouse") e.preventDefault()
  })

  /* ---------- spine stack (scroll-linked) ---------- */
  let stacks = []
  function setupStacks() {
    stacks = [...document.querySelectorAll(".stack")].map((st) => [...st.querySelectorAll(".stack-card")])
    measure()
  }
  function measure() {
    const T = css("--stick-top")
    const S = css("--strip-h")
    const G = css("--gap")
    stacks.forEach((cards) =>
      cards.forEach((c, i) => {
        const f = c.querySelector(".face")
        f.style.height = ""
        if (!c.classList.contains("sticky")) return
        const h = f.querySelector(".full").offsetHeight + 2
        c._full = h
        c.style.top = T + i * (S + G) + "px"
        // element box is only strip-high so sticky releases when the section ends
        c.style.height = S + "px"
        c.style.marginBottom = "0px"
        // a separate spacer keeps the flow: a margin would count toward sticky's limit and push spines out early
        let sp = c.nextElementSibling
        if (!sp || !sp.classList.contains("spacer")) {
          sp = document.createElement("div")
          sp.className = "spacer"
          c.after(sp)
        }
        sp.style.height = h - S + G + "px"
        f.style.height = h + "px"
      }),
    )
    onScroll()
  }
  // briefs: open once the item's top passes 80% of the viewport, close again below 86% (gap stops flicker)
  function updateBriefs() {
    const maxS = root.scrollHeight - innerHeight
    document.querySelectorAll(".briefs li").forEach((li) => {
      const top = li.getBoundingClientRect().top
      // reach: how high this item (folded) can get with the page scrolled to the bottom. The last
      // few never reach the 80% line, so their line moves to 12% of a screen below their reach.
      const bs = li.querySelector(".bs")
      const reach = top + scrollY - (maxS - (bs ? bs.getBoundingClientRect().height : 0))
      const line = Math.max(innerHeight * 0.8, reach + innerHeight * 0.12)
      if (top < line) li.classList.add("open")
      else if (top > line + innerHeight * 0.06) li.classList.remove("open")
    })
  }
  function onScroll() {
    updateBriefs()
    const T = css("--stick-top")
    const S = css("--strip-h")
    const G = css("--gap")
    stacks.forEach((cards) =>
      cards.forEach((c, i) => {
        if (!c.classList.contains("sticky")) return
        const f = c.querySelector(".face")
        const next = cards[i + 1]
        const top = T + i * (S + G)
        // the last card is pushed by whatever follows it: the brief list, or the end of the section
        const after = c.parentElement.nextElementSibling
        const nextTop = next
          ? next.getBoundingClientRect().top
          : after
            ? after.getBoundingClientRect().top
            : c.closest("section").getBoundingClientRect().bottom + G
        const h = Math.max(S, Math.min(c._full, nextTop - top - G))
        f.style.height = h + "px"
        const p = 1 - (h - S) / (c._full - S) // 0 = open, 1 = spine
        c._p = p
        const full = f.querySelector(".full")
        full.style.opacity = Math.max(0, 1 - p * 1.8)
        const strip = f.querySelector(".strip")
        strip.style.opacity = Math.max(0, (p - 0.55) / 0.45)
        strip.style.pointerEvents = p > 0.9 ? "auto" : "none"
        full.style.pointerEvents = p > 0.5 ? "none" : "auto"
        if (p > 0.02) f.classList.remove("hov")
      }),
    )
  }
  let raf = 0
  addEventListener(
    "scroll",
    () => {
      if (!raf)
        raf = requestAnimationFrame(() => {
          raf = 0
          onScroll()
        })
    },
    { passive: true },
  )
  addEventListener("resize", () => measure())
  // clicking a spine scrolls back to that card
  document.addEventListener("click", (e) => {
    const strip = e.target.closest(".strip")
    if (!strip) return
    const c = strip.closest(".stack-card")
    const sec = c.closest("section")
    const cards = [...sec.querySelectorAll(".stack-card")]
    const i = cards.indexOf(c)
    // position where this card is stuck but fully open = next card sits just below it
    let y = sec.getBoundingClientRect().top + scrollY + sec.querySelector(".sec-h").offsetHeight + 18
    for (let k = 0; k < i; k++) y += cards[k]._full + css("--gap")
    window.scrollTo({
      top: y - css("--stick-top") - i * (css("--strip-h") + css("--gap")),
      behavior: reduce ? "auto" : "smooth",
    })
  })

  /* ---------- hover lift ---------- */
  function setupLift() {
    if (!finePointer || reduce) return
    document.querySelectorAll(".face").forEach((f) => {
      const c = f.closest(".stack-card")
      // not while folded into a spine
      f.addEventListener("pointermove", (e) => {
        if (e.pointerType === "mouse" && (c._p || 0) <= 0.02) f.classList.add("hov")
      })
      f.addEventListener("pointerleave", () => f.classList.remove("hov"))
    })
  }

  /* ---------- source stack popover ---------- */
  function setupSources() {
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
  }
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".srcs")) document.querySelectorAll(".pop.open").forEach((p) => p.classList.remove("open"))
  })
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") document.querySelectorAll(".pop.open").forEach((p) => p.classList.remove("open"))
  })

  /* ---------- boot ---------- */
  if (pageIntro) document.body.classList.add("intro")
  setupStacks()
  setupLift()
  setupSources()

  let introEnd = 0
  if (intro) {
    // top to bottom, only what is on the first screen. The first card starts with the first tick and
    // the last card with the last rail item, so both sweep down the page at the same pace.
    const els = pageIntro
      ? [...document.querySelectorAll("#main .drop, #main .stack-card")].filter(
          (el) => el.getBoundingClientRect().top <= innerHeight,
        )
      : []
    const span = (W + ICONS.length - 1) * L
    const step = els.length > 1 ? Math.max(L, span / (els.length - 1)) : 0
    els.forEach((el, k) => {
      el.classList.add("drop")
      el.style.setProperty("--d", I + k * step + "s")
    })
    root.style.setProperty("--logo-d", I - L + "s")
    introEnd = I + Math.max(span + 0.3, (els.length - 1) * step + 0.9) + 0.1
  }

  if (arrived) {
    // the window as the last page left it, then on to where the click sends it
    const clamp = (s) => Math.max(0, Math.min(DAYS.length - W, s))
    start = clamp(arrived.to)
    const end = target(DAYS.indexOf(current), false)
    start = clamp(arrived.from)
    place(false)
    if (end !== start) {
      start = end
      requestAnimationFrame(() => requestAnimationFrame(() => place(true)))
    }
    // the arrow was already showing on the last page
    if (arrived.off) ret.style.animationDuration = "0s"
  } else {
    reveal(DAYS.indexOf(current), false)
    place(false)
  }

  if (intro) {
    // Stripe entrance: each visible tick scaleX 0 -> 1 with delay p*.1 + I
    ticks.forEach((t, i) => {
      const p = i - start
      t.style.transitionDelay = p < 0 || p >= W ? "0s" : `${p * L + I}s`
    })
    ICONS.forEach((a, k) => (a.style.transitionDelay = `${(W + k) * L + I}s`))
    // opened straight on an older issue: the arrow comes in just before the first tick
    ret.style.animationDelay = `${I - L}s`
    requestAnimationFrame(() => requestAnimationFrame(() => rail.classList.add("ready")))
    // clear delays afterwards so hover/scroll aren't delayed
    setTimeout(() => {
      ticks.forEach((t) => (t.style.transitionDelay = "0s"))
      ret.style.animationDelay = "0s"
      document.body.classList.remove("intro")
    }, introEnd * 1000)
  }
  document.fonts.ready.then(measure)
})()
