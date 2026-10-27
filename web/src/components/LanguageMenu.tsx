import { Check, Languages } from "lucide-react"

import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import type { Lang } from "@/lib/i18n"

interface Props {
  /** The language of this page. */
  lang: Lang
  label: string
  /** This page in each language. */
  zh: string
  en: string
}

// The language icon in the header opens a menu of the two editions; each item goes to this same
// page in that language.
export default function LanguageMenu({ lang, label, zh, en }: Props) {
  const options = [
    { lang: "zh", label: "中文", href: zh },
    { lang: "en", label: "English", href: en },
  ] as const

  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label={label}>
          <Languages />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-auto">
        {options.map((option) => (
          <DropdownMenuItem key={option.lang} asChild>
            <a href={option.href} hrefLang={option.lang} lang={option.lang}>
              {option.label}
              {option.lang === lang && <Check className="ml-auto" />}
            </a>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
