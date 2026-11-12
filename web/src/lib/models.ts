// A model id as the reader sees it: "claude-opus-5-5" → "Claude Opus 5.5",
// "minimaxai/minimax-m3.1-flash" → "MiniMax M3.1 Flash", "gemini-3.5-flash-lite" → "Gemini 3.5 Flash Lite".
// Display only: data/ keeps the raw id. Words are capitalized by rule; BRANDS holds the names
// whose casing a rule cannot guess. A value that is not an id (such as "Claude") is kept as is.

const BRANDS: Record<string, string> = {
  minimax: "MiniMax",
  openai: "OpenAI",
  deepseek: "DeepSeek",
  gpt: "GPT",
  glm: "GLM",
  xai: "xAI",
}

export function modelName(id: string): string
export function modelName(id: string | null): string | null
export function modelName(id: string | null): string | null {
  if (!id) return id
  const name = id.split("/").pop()!
  if (!/^[a-z0-9.-]+$/.test(name)) return id
  const words: string[] = []
  for (const token of name.split("-")) {
    const last = words.at(-1)
    // "5-5" is version 5.5
    if (/^\d+$/.test(token) && last && /^\d+$/.test(last)) words[words.length - 1] = `${last}.${token}`
    else words.push(token)
  }
  return words
    .map((w) => BRANDS[w] ?? (/^([a-z]\d|\d)/.test(w) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)))
    .join(" ")
}
