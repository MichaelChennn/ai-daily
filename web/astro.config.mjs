// @ts-check
import { defineConfig } from "astro/config"

import react from "@astrojs/react"
import tailwindcss from "@tailwindcss/vite"

// Where the site is served. The Pages workflow passes the address configure-pages reports;
// `daily export` (npm run data) reads it too, for the feed's links. For a local preview of the
// build, use SITE_URL=http://localhost:8000/.
const siteUrl = new URL(process.env.SITE_URL ?? "https://michaelchennn.github.io/ai-daily/")

// https://astro.build/config
export default defineConfig({
  site: siteUrl.origin,
  base: siteUrl.pathname,
  trailingSlash: "always",
  integrations: [react()],

  vite: {
    plugins: [tailwindcss()],
  },
})
