"""`daily edit`: the API route, an editor that runs on a cloud model API instead of Claude Code.

The rules stay in one place, .claude/skills/daily-editor/SKILL.md: its body is the system prompt,
and ROUTE_NOTES maps its commands to the tools below. The model only browses and writes; fetching,
recording research, filling in the digest's bookkeeping fields and the validate gate are done here.

One OpenAI compatible client (chat completions with tools) for every provider: a model is named
"provider:model" (EDITOR_API_MODEL), and PROVIDERS gives each provider's base_url and the
environment variable holding its key. Adding a provider is one line.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from daily import digest, pipeline

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Provider:
    base_url: str
    key_env: str
    min_interval: float  # seconds between requests, to stay under the free tier's requests per minute


PROVIDERS = {
    "gemini": Provider("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", 13.0),
    "nvidia": Provider("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY", 2.0),
}
RETRIES = 3  # after the first attempt
RETRY_DELAY = 15.0
CHAT_TIMEOUT = 300.0
MAX_TOKENS = 16384  # a whole digest goes out as one tool call
MAX_TURNS = 30
MAX_SUBMISSIONS = 3
PAGE_CHARS = 12000
SKILL_FILE = Path(__file__).resolve().parent.parent / ".claude/skills/daily-editor/SKILL.md"

ROUTE_NOTES = """

## 在 API 通道运行（这一节优先于上文）

你现在通过云端模型 API 运行，没有 shell、git、WebFetch、WebSearch。上文的命令对应下面的工具：

- `daily list` → `list_candidates`；看某一条候选的全部字段 → `show_candidate`。
- WebFetch 和 `daily page` → `fetch_page`。不带 grep 时返回页面正文的前 12000 字符；
  带 grep 时返回每个关键词前后的原文。这和 validate 核对引文用的是同一份页面文本，
  evidence 直接从这里逐字复制。每次调用由程序自动记进 research，你不用写 research。预算 20 次。
- 没有 WebSearch：不做补漏，只用候选。
- `validate`、render 和提交 → `submit_digest`。只传 highlights 和 items；
  schema_version、date、mode、generated_at、research 由程序补上，
  然后按 `validate --check-links --drop-invalid` 校验。返回 ERROR 时按第 6 步修改后重新提交
  （最多 3 次）；返回通过就结束，不要再调用任何工具。
- 跳过第 0 步和第 7 步（准备、git 提交），也不要运行 degrade：实在不合格就停下，程序会处理。
- 请求次数有限：一轮里可以同时调用多个工具，例如一次打开几个页面。
"""

_STRINGS = {"type": "array", "items": {"type": "string"}}
# Spelled out (Gemini rejects an object schema without properties); validate is the real check.
ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "section": {"type": "string", "enum": list(digest.SECTIONS)},
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "candidate_id": {"type": "string"},
                    "url": {"type": "string"},
                    "title": {"type": "string"},
                },
            },
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"url": {"type": "string"}, "quote": {"type": "string"}},
                "required": ["url", "quote"],
            },
        },
        "tags": _STRINGS,
    },
    "required": ["section", "title", "summary", "sources"],
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_candidates",
            "description": "每条候选一行：id、类型、信源、标题、热度信号，下面是摘要的开头。",
            "parameters": {
                "type": "object",
                "properties": {
                    "kind": {"type": "array", "items": {"type": "string"}, "description": "只看这些类型"},
                    "summary_chars": {"type": "integer", "description": "摘要截断长度，0 不显示，默认 160"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_candidate",
            "description": "一条候选的全部字段（JSON）。",
            "parameters": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": "打开一个网页，返回正文（前 12000 字符），或者 grep 的每个关键词前后的原文。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "grep": {"type": "array", "items": {"type": "string"}, "description": "关键词"},
                    "context": {"type": "integer", "description": "关键词前后各多少字符，默认 200"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_digest",
            "description": "提交日报并校验。digest 只需要 highlights 和 items（schema 见上文）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "digest": {
                        "type": "object",
                        "properties": {
                            "highlights": _STRINGS,
                            "items": {"type": "array", "items": ITEM_SCHEMA},
                        },
                        "required": ["highlights", "items"],
                    }
                },
                "required": ["digest"],
            },
        },
    },
]


class EditorError(Exception):
    pass


async def _sleep(seconds: float) -> None:  # replaced in tests
    await asyncio.sleep(seconds)


def resolve(model: str) -> tuple[Provider, str, str]:
    """ "provider:model" -> (provider, model name, API key); EditorError when unknown or unset."""
    name, _, model_name = model.partition(":")
    provider = PROVIDERS.get(name)
    if provider is None or not model_name:
        raise EditorError(f"model must be provider:model with provider one of {list(PROVIDERS)}: {model!r}")
    key = os.environ.get(provider.key_env)
    if not key:
        raise EditorError(f"{provider.key_env} is not set")
    return provider, model_name, key


def slug(model: str) -> str:
    """The beta's slug, from the model's family: nvidia:deepseek-ai/deepseek-v4.1-flash -> deepseek.
    So EDITOR_API_MODEL holds at most one model per family."""
    return model.partition(":")[2].rsplit("/", 1)[-1].split("-", 1)[0].lower()


def system_prompt() -> str:
    text = SKILL_FILE.read_text(encoding="utf-8")
    if text.startswith("---"):
        text = text.split("---", 2)[2]  # drop the frontmatter
    return text.strip() + ROUTE_NOTES


@dataclass
class Session:
    """One edit: the tools' state and the result."""

    candidates: dict[str, Any]
    model: str
    client: httpx.AsyncClient
    research: list[dict[str, str]] = field(default_factory=list)
    submissions: int = 0
    result: dict[str, Any] | None = None

    async def call(self, name: str, arguments: dict[str, Any]) -> str:
        if name == "list_candidates":
            kinds = arguments.get("kind")
            return pipeline.candidate_listing(
                self.candidates,
                kinds if isinstance(kinds, list) else None,
                int(arguments.get("summary_chars", 160)),
            )
        if name == "show_candidate":
            found = [c for c in self.candidates["candidates"] if c["id"] == arguments.get("id")]
            return json.dumps(found[0], ensure_ascii=False, indent=1) if found else "没有这个 id"
        if name == "fetch_page":
            return await self._fetch_page(arguments)
        if name == "submit_digest":
            return await self._submit(arguments.get("digest"))
        return f"没有这个工具：{name}"

    async def _fetch_page(self, arguments: dict[str, Any]) -> str:
        url = arguments.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            return "url 必须是 http(s) 链接"
        if len(self.research) >= digest.BUDGET["webfetch"]:
            return "fetch_page 的预算已经用完，请依据已有材料写。"
        self.research.append({"via": "webfetch", "url": url})
        page = (await digest.check_links([url], self.client))[url]
        if page.text is None:
            return f"拿不到页面文本（{page.error or page.status}）：只能依据候选摘要写。"
        grep = arguments.get("grep")
        if grep:
            return digest.grep_page(page.text, [str(g) for g in grep], int(arguments.get("context", 200)))
        text = " ".join(page.text.split())
        if len(text) > PAGE_CHARS:
            return text[:PAGE_CHARS] + f"\n…（截断，全文 {len(text)} 字符；后面的内容用 grep 找）"
        return text

    async def _submit(self, draft: Any) -> str:
        self.submissions += 1
        if not isinstance(draft, dict):
            return "ERROR digest 必须是一个对象"
        data = {
            "schema_version": digest.SCHEMA_VERSION,
            "date": self.candidates["date"],
            "mode": "full",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "channel": "api",
            "model": self.model,
            "highlights": draft.get("highlights"),
            "items": draft.get("items"),
            "research": self.research,
        }
        report = digest.validate(data, self.candidates)
        if not report.errors:
            pages = await digest.check_links(digest.digest_urls(data), self.client)
            report = digest.validate(data, self.candidates, pages)
        lines = [f"ERROR {e}" for e in report.errors]
        lines += [f"DROP  item {i + 1}: {'; '.join(e)}" for i, e in sorted(report.item_errors.items())]
        lines += [f"WARN  {w}" for w in report.warnings]
        if report.errors:
            left = MAX_SUBMISSIONS - self.submissions
            lines.append(f"不合格，还可以再提交 {left} 次。" if left else "不合格，提交次数已用完。")
            return "\n".join(lines)
        self.result = digest.apply_report(data, report, checked_links=True)
        kept = len(data["items"]) - len(report.item_errors)
        return "\n".join(lines + [f"通过：保留 {kept} 条。编辑结束。"])


class Chat:
    """Chat completions against one provider, paced and retried for the free tiers."""

    def __init__(self, model: str, client: httpx.AsyncClient) -> None:
        self.provider, self.name, self.key = resolve(model)
        self.client = client
        self.last_request = 0.0

    async def send(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        url = self.provider.base_url.rstrip("/") + "/chat/completions"
        payload = {"model": self.name, "messages": messages, "tools": TOOLS, "max_tokens": MAX_TOKENS}
        for attempt in range(1, RETRIES + 2):
            wait = self.last_request + self.provider.min_interval - time.monotonic()
            if wait > 0:
                await _sleep(wait)
            self.last_request = time.monotonic()
            try:
                response = await self.client.post(
                    url, json=payload, headers={"Authorization": f"Bearer {self.key}"}, timeout=CHAT_TIMEOUT
                )
            except httpx.HTTPError as exc:
                problem = f"{type(exc).__name__}: {exc}"
            else:
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]
                problem = f"HTTP {response.status_code}: {response.text[:300]}"
                if response.status_code != 429 and response.status_code < 500:
                    raise EditorError(problem)
            log.warning("chat request %d/%d failed: %s", attempt, RETRIES + 1, problem)
            if attempt > RETRIES:
                raise EditorError(problem)
            await _sleep(RETRY_DELAY)
        raise AssertionError("unreachable")


async def edit(
    candidates: dict[str, Any], model: str, client: httpx.AsyncClient, max_turns: int = MAX_TURNS
) -> dict[str, Any]:
    """Run the editor until a digest passes validate; EditorError if it does not within max_turns."""
    chat = Chat(model, client)
    session = Session(candidates, model, client)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": f"期号 {candidates['date']}。开始编辑这一期。"},
    ]
    for turn in range(1, max_turns + 1):
        message = await chat.send(messages)
        messages.append(message)  # as returned: some providers need their extra fields back
        calls = message.get("tool_calls") or []
        log.info("turn %d: %s", turn, ", ".join(c["function"]["name"] for c in calls) or "no tool call")
        if not calls:
            messages.append({"role": "user", "content": "请用 submit_digest 提交日报。"})
            continue
        for call in calls:
            try:
                arguments = json.loads(call["function"].get("arguments") or "{}")
                if not isinstance(arguments, dict):
                    raise ValueError("arguments must be a JSON object")
                result = await session.call(call["function"]["name"], arguments)
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                result = f"参数有误：{exc}"
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        if session.result is not None:
            return session.result
        if session.submissions >= MAX_SUBMISSIONS:
            raise EditorError(f"no valid digest after {MAX_SUBMISSIONS} submissions")
    raise EditorError(f"no valid digest after {max_turns} turns")
