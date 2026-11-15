// The 生成过程 page's behaviour (#63): the metro lines follow the scroll both ways, their tip 60%
// down the screen; a step drops in when the line reaches it and stays. The lists open in place
// and in a dialog; the table at the end filters and opens a row. The rail is press.js's.
;(() => {
  const flow = document.getElementById("flow")
  const svg = document.getElementById("wires")
  if (!flow || !svg) return
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches
  const NS = "http://www.w3.org/2000/svg"
  const GAP = 14 // between a line and the text it stops at
  let inks = [] // {el, len, ys, ls, to, y1, stop}
  let flowTop = 0
  let masks = 0
  const $ = (id) => document.getElementById(id)

  // Positions from the layout, not the screen: a step mid-Drop is still where it will land.
  function box(el) {
    let x = 0
    let y = 0
    const w = el.offsetWidth
    const h = el.offsetHeight
    while (el && el !== flow) {
      x += el.offsetLeft
      y += el.offsetTop
      el = el.offsetParent
    }
    return { t: y, b: y + h, cx: x + w / 2 }
  }

  // Right angles with rounded corners. Going out to a lane it turns just below the step above;
  // coming back (`late`) it turns just above the step below.
  function route(a, b, late) {
    if (Math.abs(a.x - b.x) < 3) return `M${a.x},${a.y} V${b.y}` // a pixel or two off centre: no turn
    const m = late ? b.y - Math.min(32, (b.y - a.y) / 2) : a.y + Math.min(32, (b.y - a.y) / 2)
    const r = Math.min(16, Math.abs(b.x - a.x) / 2, (b.y - a.y) / 4)
    const d = b.x > a.x ? 1 : -1
    return `M${a.x},${a.y} V${m - r} Q${a.x},${m} ${a.x + d * r},${m} H${b.x - d * r} Q${b.x},${m} ${b.x},${m + r} V${b.y}`
  }

  const path = (d, cls) => {
    const el = document.createElementNS(NS, "path")
    el.setAttribute("d", d)
    if (cls) el.setAttribute("class", cls)
    return el
  }

  function link(from, to, late) {
    const f = box(from)
    const t = box(to)
    const a = { x: f.cx, y: f.b + GAP }
    const b = { x: t.cx, y: t.t - GAP }
    const d = route(a, b, late)
    // 当时未记录: dashed into such a step, and out of one inside a lane
    const dashed = to.classList.contains("unrec") || (from.classList.contains("unrec") && !!from.closest(".lane"))
    let el
    if (dashed) {
      // A dashed line cannot also use its dashes to grow: it grows through a solid mask instead.
      const id = `wm${masks++}`
      const mask = document.createElementNS(NS, "mask")
      mask.setAttribute("id", id)
      mask.setAttribute("maskUnits", "userSpaceOnUse")
      el = path(d)
      mask.append(el)
      const ink = path(d, "ink dash")
      ink.setAttribute("mask", `url(#${id})`)
      svg.append(path(d, "track dash"), mask, ink)
    } else {
      el = path(d, "ink")
      svg.append(path(d, "track"), el)
    }
    let stop = null
    if (to.classList.contains("fail")) {
      // the route ends here: a bar across the end of its line
      stop = path(`M${b.x - 8},${b.y} H${b.x + 8}`, "ink stop")
      svg.append(stop)
    }
    const len = el.getTotalLength()
    const ys = []
    const ls = []
    for (let i = 0; i <= 60; i++) {
      const l = (len * i) / 60
      ys.push(el.getPointAtLength(l).y)
      ls.push(l)
    }
    el.style.strokeDasharray = `${len} ${len}`
    inks.push({ el, len, ys, ls, to, y1: b.y, stop })
  }

  // How much of a line is drawn with the tip at height y (the lines only go down).
  function lengthAt(k, y) {
    if (y <= k.ys[0]) return 0
    for (let i = 1; i < k.ys.length; i++) {
      if (k.ys[i] >= y) {
        const t = (y - k.ys[i - 1]) / Math.max(1e-6, k.ys[i] - k.ys[i - 1])
        return k.ls[i - 1] + t * (k.ls[i] - k.ls[i - 1])
      }
    }
    return k.len
  }

  function build() {
    svg.replaceChildren()
    inks = []
    masks = 0
    flowTop = flow.getBoundingClientRect().top + scrollY
    const chain = [$("src"), ...flow.querySelectorAll(":scope > .node:not(#src):not(#adopt)")]
    for (let i = 1; i < chain.length; i++) link(chain[i - 1], chain[i])
    const fork = chain.at(-1)
    for (const ln of flow.querySelectorAll(".lane")) {
      const ns = [...ln.children]
      link(fork, ns[0])
      for (let i = 1; i < ns.length; i++) link(ns[i - 1], ns[i])
      if (!ln.classList.contains("failed")) link(ns.at(-1), $("adopt"), true)
    }
    for (const e of flow.querySelectorAll(".end")) link($("adopt"), e)
    draw()
  }

  // The tip sits 60% down the screen, and moves to the bottom over the last stretch of the page
  // so the last step is reached.
  let intro = reduce ? Infinity : 0
  function tip() {
    const max = document.documentElement.scrollHeight - innerHeight
    const near = Math.min(1, Math.max(0, 1 - (max - scrollY) / (innerHeight * 0.4)))
    return Math.min(scrollY + innerHeight * (0.6 + 0.4 * near) - flowTop, intro)
  }

  const reach = (n) => n.classList.add("on")

  function draw() {
    const t = reduce ? Infinity : tip()
    for (const k of inks) {
      const l = lengthAt(k, t)
      k.el.style.strokeDashoffset = k.len - l
      k.el.style.opacity = l > 0.5 ? 1 : 0 // a round cap leaves a dot even at length 0
      if (t >= k.y1) reach(k.to)
      k.stop?.classList.toggle("on", t >= k.y1)
    }
  }

  let raf = 0
  addEventListener(
    "scroll",
    () => {
      if (!raf)
        raf = requestAnimationFrame(() => {
          raf = 0
          draw()
        })
    },
    { passive: true },
  )
  // When one lane's list closes the flow may keep its height (the other lane is longer), so
  // every step is watched, not just the flow.
  let rb = 0
  const ro = new ResizeObserver(() => {
    if (!rb)
      rb = requestAnimationFrame(() => {
        rb = 0
        build()
      })
  })
  ro.observe(flow)
  for (const n of flow.querySelectorAll(".node, .lane-h")) ro.observe(n)

  reach($("src"))
  // On arrival the line draws from the sources down to where the tip is.
  if (!reduce) {
    const t0 = performance.now() + 400
    const start = scrollY + innerHeight * 0.6 - (flow.getBoundingClientRect().top + scrollY)
    const step = (now) => {
      const k = Math.min(1, Math.max(0, (now - t0) / 1600))
      intro = k >= 1 ? Infinity : box($("src")).b + (1 - Math.pow(1 - k, 3)) * (start - box($("src")).b)
      draw()
      if (k < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }
  document.fonts?.ready.then(build)
  build()

  const page = flow.parentElement
  const dlg = $("dlg")
  page.addEventListener("click", (ev) => {
    // to the table at the end: a glide, not a jump
    const j = ev.target.closest('a[href^="#"]')
    if (j) {
      const t = document.querySelector(j.getAttribute("href"))
      if (t) {
        ev.preventDefault()
        glide(t)
        history.replaceState(null, "", j.getAttribute("href"))
        return
      }
    }
    const c = ev.target.closest(".cut[aria-expanded]")
    if (c) return c.setAttribute("aria-expanded", c.getAttribute("aria-expanded") === "true" ? "false" : "true")
    // in the dialog: by reason (or by issue)
    const g = ev.target.closest(".dlg .chips .g")
    if (g) {
      for (const x of g.parentElement.children) x.setAttribute("aria-pressed", String(x === g))
      return sift(dlg)
    }
    // 收起 under a list: close it; if its 「N 条…」 has gone off the top of the screen, glide back
    const up = ev.target.closest(".bx-up")
    if (up) {
      const cut = up.closest(".fold").previousElementSibling
      cut.setAttribute("aria-expanded", "false")
      cut.focus({ preventScroll: true })
      if (cut.getBoundingClientRect().top < 80) glide(cut, innerHeight / 3)
      return
    }
    // 展开: the box's whole list in the dialog
    const x = ev.target.closest(".bx-x")
    if (x) {
      const bx = x.closest(".bx")
      dlg.querySelector(".dlg-t").textContent = bx.closest(".fold").previousElementSibling.querySelector("span").textContent
      dlg.querySelector(".bx-h").innerHTML = bx.querySelector(".bx-h").innerHTML
      dlg.querySelector(".list").innerHTML = bx.querySelector(".list").innerHTML
      const n = bx.querySelector(".bx-n")
      const dn = dlg.querySelector(".bx-n")
      dn.textContent = n?.textContent || ""
      dn.hidden = !n
      dlg.querySelector(".list").scrollTop = 0
      sift(dlg)
      document.documentElement.classList.add("dlg-on")
      dlg.showModal()
      if (matchMedia("(pointer:fine)").matches) dlg.querySelector(".bx-q").focus()
      else dlg.querySelector(".dlg-c").focus()
      return
    }
    if (ev.target.closest(".dlg-c") || ev.target === dlg) return dlg.close()
    // the table: filter
    const f = ev.target.closest(".mx .seg button")
    if (f) {
      for (const b of page.querySelectorAll(".mx .seg button")) b.setAttribute("aria-pressed", String(b === f))
      for (const tb of page.querySelectorAll(".mx tbody.r")) tb.hidden = !tb.dataset.f.split(" ").includes(f.dataset.f)
      return
    }
    // the table: a row opens to its scores and reasons
    const r = ev.target.closest(".mx .row")
    if (r && !ev.target.closest("a")) r.setAttribute("aria-expanded", r.getAttribute("aria-expanded") === "true" ? "false" : "true")
  })
  // Glide somewhere: fast then slow, longer for a longer way (1.4 s at most).
  function glide(t, off = 24) {
    const y0 = scrollY
    const y1 = Math.max(0, Math.min(t.getBoundingClientRect().top + scrollY - off, document.documentElement.scrollHeight - innerHeight))
    if (reduce) return scrollTo(0, y1)
    const dur = Math.min(1400, 500 + Math.abs(y1 - y0) * 0.15)
    const t0 = performance.now()
    const ease = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2)
    const step = (now) => {
      const k = Math.min(1, (now - t0) / dur)
      scrollTo(0, y0 + (y1 - y0) * ease(k))
      if (k < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }
  dlg.addEventListener("close", () => document.documentElement.classList.remove("dlg-on"))
  // the search box: keeps the rows whose title, source or reason has these words
  function sift(bx) {
    const q = bx.querySelector(".bx-q").value.trim().toLowerCase()
    const g = bx.querySelector(".chips .g[aria-pressed=true]")?.dataset.g || ""
    let n = 0
    for (const li of bx.querySelectorAll("li")) {
      li.hidden = (g && li.dataset.g !== g) || (q && !li.textContent.toLowerCase().includes(q))
      li.classList.toggle("f", !li.hidden && !n)
      n += !li.hidden
    }
    bx.querySelector(".bx-none").hidden = n > 0
  }
  page.addEventListener("input", (ev) => {
    if (ev.target.classList.contains("bx-q")) sift(dlg)
  })
  page.addEventListener("keydown", (ev) => {
    const r = ev.target.closest?.(".mx .row")
    if (r && (ev.key === "Enter" || ev.key === " ")) {
      ev.preventDefault()
      r.click()
    }
  })
  // a scrolling box: no fade once it is scrolled to the end
  page.addEventListener(
    "scroll",
    (ev) => {
      const ul = ev.target
      if (ul.classList?.contains("list")) ul.closest(".bx").classList.toggle("at-end", ul.scrollTop + ul.clientHeight >= ul.scrollHeight - 2)
    },
    { capture: true, passive: true },
  )
})()
