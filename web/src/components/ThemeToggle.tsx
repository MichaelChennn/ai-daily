import { Moon, Sun } from "lucide-react"

import { Button } from "@/components/ui/button"

// The class on <html> is set before the first paint by the script in Layout.astro; this only
// flips it and remembers the choice. Both icons are rendered and CSS shows the right one, so the
// server-rendered markup never has to know the theme.
export default function ThemeToggle({ label }: { label: string }) {
  function toggle() {
    // Switch without animating every transition-colors element through the change.
    const freeze = document.createElement("style")
    freeze.textContent = "*,*::before,*::after{transition:none!important}"
    document.head.append(freeze)
    const dark = document.documentElement.classList.toggle("dark")
    getComputedStyle(document.body).color // apply the new colors before transitions come back
    freeze.remove()
    try {
      localStorage.setItem("theme", dark ? "dark" : "light")
    } catch {
      // Storage blocked: the choice lasts until the next page load.
    }
  }

  return (
    <Button variant="ghost" size="icon-sm" onClick={toggle} aria-label={label}>
      <Sun className="dark:hidden" />
      <Moon className="hidden dark:block" />
    </Button>
  )
}
