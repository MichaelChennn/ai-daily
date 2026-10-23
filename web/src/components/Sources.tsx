import { cn } from "cn"
import { ChevronDown, Search, X } from "lucide-react"
import { useState } from "react"
import { flushSync } from "react-dom"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { filterTransition } from "@/lib/filter-transition"

// web/data/sources.json, written by `python -m daily export`.
export type Source = {
  id: string
  name: string
  kind: string
  homepage: string | null
  icon: string | null
  enabled: boolean
  repos: string[]
  stats: { ok: number; runs: number; picked: number; candidates: number } | null
}

export type SourcesData = { runs: number; groups: { label: string; sources: Source[] }[] }

const ALL = "all"

// The whitelist as a grid of cards per group: pick a group with the capsules, narrow it down with
// the search. Changing the group animates the cards like the archive's months (global.css); the
// search filters as you type, without a transition, so the input never freezes mid-word.
export default function Sources({ data }: { data: SourcesData }) {
  const [group, setGroup] = useState(ALL)
  const [query, setQuery] = useState("")
  const [animating, setAnimating] = useState(false)

  const needle = query.trim().toLowerCase()
  const total = data.groups.reduce((n, g) => n + g.sources.length, 0)
  const shown = data.groups
    .filter((g) => group === ALL || g.label === group)
    .map((g) => ({
      label: g.label,
      // The disabled sources go last in their group.
      sources: g.sources
        .filter((s) => !needle || matches(s, needle))
        .sort((a, b) => Number(b.enabled) - Number(a.enabled)),
    }))
    .filter((g) => g.sources.length > 0)

  function selectGroup(next: string) {
    if (!next || next === group) return // clicking the active capsule again keeps it
    // The cards get their view-transition-name only for this transition, so that leaving the
    // page cross-fades it as a whole.
    filterTransition(
      () => flushSync(() => setGroup(next)),
      () => flushSync(() => setAnimating(true)),
      () => setAnimating(false),
    )
  }

  const options = [{ label: ALL, title: "全部", count: total }].concat(
    data.groups.map((g) => ({ label: g.label, title: g.label, count: g.sources.length })),
  )

  return (
    <>
      <h1 className="sr-only">信息源</h1>
      <div className="flex flex-col gap-3 pt-10 sm:flex-row-reverse sm:items-center sm:justify-between">
        <div className="relative sm:w-56">
          <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索信息源或仓库"
            aria-label="搜索信息源或仓库"
            className="rounded-full px-9 shadow-none [&::-webkit-search-cancel-button]:appearance-none"
          />
          {query && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={() => setQuery("")}
              aria-label="清空搜索"
              className="absolute top-1/2 right-1.5 -translate-y-1/2 rounded-full text-muted-foreground"
            >
              <X />
            </Button>
          )}
        </div>
        <ToggleGroup
          type="single"
          value={group}
          onValueChange={selectGroup}
          variant="outline"
          size="sm"
          spacing={1}
          aria-label="按分组筛选"
          className="flex-wrap justify-start"
        >
          {options.map((option) => (
            <ToggleGroupItem
              key={option.label}
              value={option.label}
              className="group/pill rounded-full px-3.5 text-[13px] font-normal data-[state=on]:border-foreground data-[state=on]:bg-foreground data-[state=on]:text-background"
            >
              {option.title}
              <span className="font-rounded text-xs text-muted-foreground tabular-nums group-data-[state=on]/pill:text-background/70">
                {option.count}
              </span>
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>
      <p className="mt-3 text-xs text-muted-foreground">统计最近 {data.runs} 期</p>

      <div className="mt-8 flex flex-col gap-12">
        {shown.map((g) => (
          <section key={g.label}>
            <h2
              className="mb-5 flex items-baseline justify-between gap-4"
              style={{ viewTransitionName: animating ? `sources-${groupIndex(data, g.label)}` : undefined }}
            >
              <span className="text-xl font-semibold tracking-tight">{g.label}</span>
              <span className="text-xs text-muted-foreground tabular-nums">{g.sources.length} 个</span>
            </h2>
            <div className="grid items-start gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {g.sources.map((source) => (
                <SourceCard
                  key={source.id}
                  source={source}
                  needle={needle}
                  transitionName={animating ? `source-${source.id}` : undefined}
                />
              ))}
            </div>
          </section>
        ))}
        {shown.length === 0 && (
          <p className="py-16 text-center text-sm text-muted-foreground">没有匹配的信息源</p>
        )}
      </div>
    </>
  )
}

function matches(source: Source, needle: string) {
  return [source.name, source.id, source.kind, ...source.repos].some((text) => text.toLowerCase().includes(needle))
}

// Stable across filtering, so a heading that stays keeps its transition name.
function groupIndex(data: SourcesData, label: string) {
  return data.groups.findIndex((g) => g.label === label)
}

type SourceCardProps = { source: Source; needle: string; transitionName?: string }

// Logo, name (to the source's homepage) and what it is, then its stats. A source with repos lists
// them behind a toggle; a search that hits one of them opens it.
function SourceCard({ source, needle, transitionName }: SourceCardProps) {
  const [open, setOpen] = useState(false)
  const repoHit = needle !== "" && source.repos.some((r) => r.toLowerCase().includes(needle))
  const { stats } = source
  const name = source.homepage ? (
    <a href={source.homepage} className="truncate hover:underline hover:underline-offset-4">
      {source.name}
    </a>
  ) : (
    <span className="truncate">{source.name}</span>
  )

  return (
    <Card
      className={cn("gap-0 rounded-lg py-0 shadow-none", !source.enabled && "opacity-60")}
      style={{ viewTransitionName: transitionName }}
    >
      <div className="flex flex-col gap-4 p-5">
        <div className="flex items-start gap-3">
          <span className="relative mt-0.5 grid size-5 shrink-0 place-items-center overflow-hidden rounded bg-muted text-[11px] font-semibold uppercase">
            {source.name.charAt(0)}
            {source.icon && (
              <img
                data-logo
                src={source.icon}
                alt=""
                width={20}
                height={20}
                loading="lazy"
                referrerPolicy="no-referrer"
                className="absolute inset-0 size-full bg-background object-cover"
              />
            )}
          </span>
          <div className="min-w-0 flex-1">
            <h3 className="flex items-center gap-2 text-[15px] font-semibold">
              {name}
              {!source.enabled && <Badge variant="outline">已停用</Badge>}
            </h3>
            <p className="mt-0.5 text-xs text-muted-foreground">{source.kind}</p>
          </div>
        </div>
        {stats ? (
          <dl className="grid grid-cols-3 gap-2">
            <Stat label="抓取成功" value={`${stats.ok}/${stats.runs}`} />
            <Stat label="平均候选" value={stats.candidates.toFixed(1)} />
            <Stat label="入选条目" value={stats.picked} />
          </dl>
        ) : (
          <p className="text-xs text-muted-foreground">{source.enabled ? "还没有抓取记录" : "暂不抓取"}</p>
        )}
      </div>
      {source.repos.length > 0 && (
        <Collapsible open={open || repoHit} onOpenChange={setOpen}>
          <Separator />
          <CollapsibleTrigger className="group flex w-full items-center justify-between px-5 py-3 text-xs text-muted-foreground transition-colors hover:text-foreground">
            <span className="tabular-nums">{source.repos.length} 个仓库</span>
            <ChevronDown className="size-4 transition-transform duration-200 group-data-[state=open]:rotate-180" />
          </CollapsibleTrigger>
          <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
            <ul className="flex flex-col gap-1.5 px-5 pb-4 text-[13px]">
              {source.repos.map((repo) => (
                <li key={repo} className="truncate">
                  <a
                    href={`https://github.com/${repo}`}
                    className="text-foreground/80 hover:text-foreground hover:underline hover:underline-offset-4"
                  >
                    <Highlight text={repo} needle={needle} />
                  </a>
                </li>
              ))}
            </ul>
          </CollapsibleContent>
        </Collapsible>
      )}
    </Card>
  )
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center gap-0.5">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="font-rounded text-lg font-bold tabular-nums">{value}</dd>
    </div>
  )
}

function Highlight({ text, needle }: { text: string; needle: string }) {
  const at = needle ? text.toLowerCase().indexOf(needle) : -1
  if (at < 0) return text
  return (
    <>
      {text.slice(0, at)}
      <mark className="rounded-sm bg-foreground/15 text-foreground">{text.slice(at, at + needle.length)}</mark>
      {text.slice(at + needle.length)}
    </>
  )
}
