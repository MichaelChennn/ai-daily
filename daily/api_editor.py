"""`daily edit`: the API route, an editor that runs on a cloud model API instead of Claude Code.

The rules stay in one place, .claude/skills/daily-editor/SKILL.md: its editorial sections are the
system prompt, and ROUTE_NOTES says how this route differs. The model picks and writes; opening the
pages, numbering their passages, turning passage numbers into verbatim evidence, the bookkeeping
fields and the validate gate are done here. No tool calls: the answers are JSON in the reply text,
which streams token by token on every provider and needs no tool call parser.

One OpenAI compatible client (chat completions) for every provider: a model is named
"provider:model" (EDITOR_API_MODEL), and PROVIDERS gives each provider's base_url and the
environment variable holding its key. Adding a provider is one line.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass
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
RETRY_DELAY = 15.0  # doubled on each retry, unless the provider says how long (Retry-After)
# Replies stream in, so the limit is on silence, not on the whole reply: NVIDIA NIM may prefill a long
# prompt for minutes before the first token.
CHAT_TIMEOUT = httpx.Timeout(30.0, read=600.0)
MAX_TOKENS = 16384  # reasoning counts too
PICKS = 18  # stories the model shortlists: one page each, inside the webfetch budget
PAGE_CHARS = 8000  # of each page, cut into numbered passages
PASSAGE_MIN = 15  # shorter pieces are menus and buttons
CODE_SHARE = 0.08  # pieces with more of {}[]<>"=|\\ than this are inlined JSON and templates, not prose
SKILL_FILE = Path(__file__).resolve().parent.parent / ".claude/skills/daily-editor/SKILL.md"
RULES = ("## 2.", "## 4.", "## 5.")  # the skill's editorial sections; this module does the other steps

ROUTE_NOTES = """

## 在 API 通道运行（这一节优先于上文）

你通过云端模型 API 运行：没有 shell、工具和网络。准备、浏览候选、打开原文、校验和提交由程序完成。
程序分几步问你，每一步只回答一个 JSON 对象，不要别的文字：

1. 挑选：程序给出候选列表，你按第 2 节挑出值得写的。
2. 写作：程序打开你挑的原文，切成编号的片段；你按第 4、5 节写日报。evidence 只填片段编号，
   程序把原文逐字放进去，你不用复制引文，也不用写 research。
3. 修改：程序按 validate 的规则检查，把不合格的条目和原因发回给你，只有这一次机会；稿子没问题就没有这一步。

没有 WebSearch：不做补漏，只用候选。
"""

WRITE_FORMAT = """\
只回答 JSON：
{"highlights": ["……"], "items": [{"section": "headline", "title": "……", "summary": "……",
  "candidates": ["c_xxx"], "evidence": [3, 17], "tags": ["模型"]}]}

- section：headline | model | paper | tool | brief，按这个顺序排，版块内按重要性排。
- candidates：这一条依据的候选 id，第一个是主来源。一个候选只能用在一条里。
- evidence：支撑关键事实的片段编号，只能用这一条候选的原文片段。标题和 summary 里的每个数字、模型名、
  版本号，都要原样出现在这一条候选的标题 / 摘要或所引的片段里，否则整条会被删掉。"""

FIX_RULES = """\
不合格的条目只能这样改：删掉材料里没有的数字和名称，换用或补充片段编号，或者整条删掉。
不要加入材料里没有的事实。数字和名称只核对这一条候选的标题 / 摘要和所引的片段。"""


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
    text = SKILL_FILE.read_text(encoding="utf-8").split("---", 2)[2]  # without the frontmatter
    parts = re.split(r"(?m)^(?=## )", text)
    rules = [p.strip() for p in parts if not p.startswith("## ") or p.startswith(RULES)]
    return "\n\n".join(rules) + ROUTE_NOTES


def first_hand_url(c: dict[str, Any]) -> str | None:
    """The candidate's first link that is not a discussion thread: the page that is opened."""
    return next((u for u in digest.candidate_urls(c) if not digest.is_discussion(u, c)), None)


_SENTENCE = re.compile(r"(?<=[.!?。！？])\s+")
_CODE = re.compile(r'[{}\[\]<>"=|\\]')


def passages(text: str) -> list[str]:
    """The opening of the page (or its body), cut into lines and sentences of at most QUOTE_MAX
    characters: each is page text as validate matches it, so a quote made of one is found on the page."""
    pieces: list[str] = []
    size = 0
    for line in text.splitlines():
        for sentence in _SENTENCE.split(" ".join(line.split())):
            while sentence and size < PAGE_CHARS:
                piece, sentence = sentence[: digest.QUOTE_MAX].strip(), sentence[digest.QUOTE_MAX :]
                if len(piece) >= PASSAGE_MIN and len(_CODE.findall(piece)) <= CODE_SHARE * len(piece):
                    pieces.append(piece)
                    size += len(piece)
    return pieces


def json_object(text: str | None) -> dict[str, Any]:
    """The JSON object in a reply, which may come in a code fence or after a line of prose."""
    start, end = (text or "").find("{"), (text or "").rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in the reply")
    value = json.loads(text[start : end + 1])  # type: ignore[index]
    if not isinstance(value, dict):
        raise ValueError("the reply is not a JSON object")
    return value


WHOLE = ("id", "type", "role", "name")  # streamed fields that are not text in pieces


def _merge(message: dict[str, Any], delta: dict[str, Any]) -> None:
    """Add one streamed delta to the message: text arrives in pieces, the rest whole."""
    for key, value in delta.items():
        if key == "tool_calls":
            calls = message.setdefault("tool_calls", [])
            for part in value:
                index = part.get("index", len(calls))
                while len(calls) <= index:
                    calls.append({})
                _merge(calls[index], {k: v for k, v in part.items() if k != "index"})
        elif isinstance(value, dict):
            _merge(message.setdefault(key, {}), value)
        elif isinstance(value, str) and isinstance(message.get(key), str) and key not in WHOLE:
            message[key] += value
        elif value is not None:
            message[key] = value


async def _read_stream(response: httpx.Response) -> dict[str, Any]:
    """The assistant message from a chat completions event stream."""
    message: dict[str, Any] = {"role": "assistant", "content": None}
    async for line in response.aiter_lines():
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        if "error" in chunk:
            raise httpx.RemoteProtocolError(f"error in the stream: {str(chunk['error'])[:300]}")
        for choice in chunk.get("choices") or []:
            _merge(message, choice.get("delta") or {})
    return message


class Chat:
    """Chat completions against one provider, paced and retried for the free tiers."""

    def __init__(self, model: str, client: httpx.AsyncClient) -> None:
        self.provider, self.name, self.key = resolve(model)
        self.client = client
        self.last_request = 0.0

    async def send(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        url = self.provider.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.name,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "stream": True,
        }
        for attempt in range(1, RETRIES + 2):
            wait = self.last_request + self.provider.min_interval - time.monotonic()
            if wait > 0:
                await _sleep(wait)
            self.last_request = time.monotonic()
            status, delay = 0, RETRY_DELAY * 2 ** (attempt - 1)
            try:
                headers = {"Authorization": f"Bearer {self.key}"}
                async with self.client.stream(
                    "POST", url, json=payload, headers=headers, timeout=CHAT_TIMEOUT
                ) as response:
                    status = response.status_code
                    if status == 200:
                        return await _read_stream(response)
                    problem = f"HTTP {status}: {(await response.aread()).decode(errors='replace')[:300]}"
                    if response.headers.get("retry-after", "").isdigit():
                        delay = float(response.headers["retry-after"])
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                problem = f"{type(exc).__name__}: {exc}"
            if status not in (0, 200, 429) and status < 500:
                raise EditorError(problem)
            log.warning("chat request %d/%d failed: %s", attempt, RETRIES + 1, problem)
            if attempt > RETRIES:
                raise EditorError(problem)
            await _sleep(delay)
        raise AssertionError("unreachable")


@dataclass(frozen=True)
class Passage:
    url: str
    owner: str  # the candidate whose page it is
    text: str


class Editor:
    """One edit in at most three requests: pick, write, fix. Each request is a full turn on a free
    tier (Gemini's flash allows 20 a day), so the reading is done here and not by the model."""

    def __init__(self, candidates: dict[str, Any], model: str, client: httpx.AsyncClient) -> None:
        self.candidates = candidates
        self.by_id = {c["id"]: c for c in candidates["candidates"]}
        self.model = model
        self.client = client
        self.chat = Chat(model, client)
        self.pages: dict[str, digest.Page] = {}  # by url, fetched once per edit
        self.passages: list[Passage] = []  # numbered from 1 in the write prompt
        self.research: list[dict[str, str]] = []

    async def run(self) -> dict[str, Any]:
        groups = await self._pick()
        await self._read(groups)
        messages = [
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": self._write_prompt(groups)},
        ]
        data = self._draft(await self._ask(messages))
        report = await self._validate(data)
        log.info("write: %d items, %d rejected", len(data["items"]), len(report.item_errors))
        feedback = self._feedback(data, report, groups)
        if feedback:
            messages.append({"role": "user", "content": feedback})
            data = self._draft(await self._ask(messages))
            report = await self._validate(data)
            log.info("fix: %d items, %d rejected", len(data["items"]), len(report.item_errors))
        if report.errors and all(e.startswith("highlight") for e in report.errors):
            # Titles are published text, so they always pass as highlights.
            log.warning("highlights rejected (%s): using the first titles", "; ".join(report.errors))
            surviving = [item for i, item in enumerate(data["items"]) if i not in report.item_errors]
            data["highlights"] = [item["title"] for item in surviving[: digest.HIGHLIGHTS_MAX]]
            report = await self._validate(data)
        if report.errors:
            raise EditorError("; ".join(report.errors))
        return digest.apply_report(data, report, checked_links=True)

    async def _ask(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """One request, its answer as JSON; a reply that is not JSON is asked again once."""
        for attempt in (1, 2):
            content = (await self.chat.send(messages)).get("content") or ""
            messages.append({"role": "assistant", "content": content})
            try:
                return json_object(content)
            except ValueError as exc:
                if attempt == 2:
                    raise EditorError(f"no JSON in the reply: {exc}") from exc
                messages.append(
                    {"role": "user", "content": f"回答不是一个 JSON 对象（{exc}）。只回答 JSON。"}
                )
        raise AssertionError("unreachable")

    async def _pick(self) -> list[list[str]]:
        usable = [c for c in self.candidates["candidates"] if first_hand_url(c)]
        listing = pipeline.candidate_listing({**self.candidates, "candidates": usable}, summary_chars=300)
        prompt = (
            f"期号 {self.candidates['date']}。第一步：挑选。下面是候选，只有讨论帖、没有一手来源的已经去掉。"
            f"按第 2 节打分，挑出最多 {PICKS} 组值得写的，重要的在前；同一事件的几个候选放进同一组，"
            f"第一个是主来源，程序会打开它的原文。"
            f"目标是最后写 {digest.ITEMS_TARGET[0]}–{digest.ITEMS_TARGET[1]} 条，可以多挑几组留余量。"
            '只回答 JSON：{"picks": [["c_xxx", "c_yyy"], ["c_zzz"]]}\n\n' + listing
        )
        answer = await self._ask(
            [{"role": "system", "content": system_prompt()}, {"role": "user", "content": prompt}]
        )
        known = {c["id"] for c in usable}
        groups: list[list[str]] = []
        seen: set[str] = set()
        for group in answer.get("picks") or []:
            ids = [i for i in group if i in known and i not in seen] if isinstance(group, list) else []
            if ids:
                groups.append(ids)
                seen.update(ids)
        if not groups:
            raise EditorError("the model picked no known candidate")
        log.info("pick: %d groups, %d candidates", len(groups[:PICKS]), len(seen))
        return groups[:PICKS]

    async def _read(self, groups: list[list[str]]) -> None:
        """Open each group's first candidate, as research, and number its passages."""
        heads = [(g[0], first_hand_url(self.by_id[g[0]]) or "") for g in groups]
        self.pages.update(await digest.check_links([url for _, url in heads], self.client))
        self.research = [{"via": "webfetch", "url": url} for url in dict.fromkeys(url for _, url in heads)]
        for cid, url in heads:
            text = self.pages[url].body or self.pages[url].text
            self.passages += [Passage(url, cid, p) for p in passages(text)] if text else []
        log.info("read: %d pages, %d passages", len(self.research), len(self.passages))

    def _write_prompt(self, groups: list[list[str]]) -> str:
        blocks = []
        for number, group in enumerate(groups, 1):
            lines = [f"## 第 {number} 组"]
            for cid in group:
                c = self.by_id[cid]
                signals = " ".join(f"{k}={v}" for k, v in c["signals"].items())
                lines += [
                    f"{cid} {c['kind']} [{c.get('source_name') or c['source']}] {c['title']}",
                    f"链接：{c['url']}" + (f"　信号：{signals}" if signals else ""),
                    "摘要：" + " ".join((c["summary"] or "").split())[:1500],
                ]
            url = first_hand_url(self.by_id[group[0]]) or ""
            numbered = [(n, p) for n, p in enumerate(self.passages, 1) if p.owner == group[0]]
            if numbered:
                lines.append(f"原文 {url}：")
                lines += [f"[{n}] {p.text}" for n, p in numbered]
            else:
                page = self.pages[url]
                reason = page.error or (page.status if page.text is None else "没有成句的正文")
                lines.append(f"（原文 {url} 用不了：{reason}。只能依据摘要写。）")
            blocks.append("\n".join(lines))
        head = (
            f"第二步：写作。下面是你挑的 {len(groups)} 组："
            "候选的标题、摘要和信号，以及每组第一个候选的原文片段。"
        )
        return head + "\n\n" + WRITE_FORMAT + "\n\n" + "\n\n".join(blocks)

    def _item(self, raw: Any) -> Any:
        """The model's item, with its sources and evidence spelled out."""
        if not isinstance(raw, dict):
            return raw  # validate says what is wrong
        ids = [i for i in raw.get("candidates") or [] if isinstance(i, str)]
        sources = [
            {"candidate_id": i, "url": self.by_id[i]["url"]} if i in self.by_id else {"candidate_id": i}
            for i in ids
        ]
        evidence = []
        for n in raw.get("evidence") or []:
            n = int(n) if isinstance(n, str) and n.isdigit() else n
            if not isinstance(n, int) or not 1 <= n <= len(self.passages):
                continue
            passage = self.passages[n - 1]
            if passage.owner not in ids:
                continue  # another item's page; validate reports the facts it was meant to back
            if passage.url not in (s.get("url") for s in sources):
                sources.append({"candidate_id": passage.owner, "url": passage.url})
            evidence.append({"url": passage.url, "quote": passage.text})
        fields = {k: raw[k] for k in ("section", "title", "summary", "tags") if k in raw}
        return {**fields, "sources": sources, "evidence": evidence}

    def _draft(self, answer: dict[str, Any]) -> dict[str, Any]:
        items = answer.get("items")
        return {
            "schema_version": digest.SCHEMA_VERSION,
            "date": self.candidates["date"],
            "mode": "full",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "channel": "api",
            "model": self.model,
            "highlights": answer.get("highlights"),
            "items": [self._item(i) for i in items] if isinstance(items, list) else items,
            "research": self.research,
        }

    async def _validate(self, data: dict[str, Any]) -> digest.Report:
        """validate with the links checked."""
        missing = [url for url in digest.digest_urls(data) if url not in self.pages]
        self.pages.update(await digest.check_links(missing, self.client))
        return digest.validate(data, self.candidates, self.pages)

    def _feedback(self, data: dict[str, Any], report: digest.Report, groups: list[list[str]]) -> str | None:
        """What to fix and how many more items to look for; None when the draft is done."""
        items = data["items"] if isinstance(data["items"], list) else []
        titles = [item.get("title") if isinstance(item, dict) else "" for item in items]
        lines = [
            f"- 第 {i + 1} 条「{titles[i]}」：{'; '.join(e)}" for i, e in sorted(report.item_errors.items())
        ]
        lines += [f"- {e}" for e in report.errors]
        used = {s.get("candidate_id") for item in items if isinstance(item, dict) for s in item["sources"]}
        unused = [str(n) for n, group in enumerate(groups, 1) if group[0] not in used]
        good, (low, high) = len(items) - len(report.item_errors), digest.ITEMS_TARGET
        more = good < low and unused
        if not lines and not more:
            return None
        text = "第三步：修改。程序按 validate 检查了你的稿子。\n"
        if lines:
            text += "不合格：\n" + "\n".join(lines) + "\n" + FIX_RULES + "\n"
        if more:
            text += f"合格 {good} 条，目标 {low}–{high} 条。还没用上的组：{'、'.join(unused)}，"
            text += "值得写的可以补上，宁缺毋滥。\n"
        return text + "回答修改后的完整 JSON，格式同上，包括没有问题的条目和 highlights。"


async def edit(candidates: dict[str, Any], model: str, client: httpx.AsyncClient) -> dict[str, Any]:
    """Edit the issue with the model; EditorError if no digest passes validate."""
    return await Editor(candidates, model, client).run()
