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

from daily import digest, pipeline, trace

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Provider:
    base_url: str
    key_env: str
    min_interval: float  # seconds between requests, to stay under the free tier's requests per minute


CHANNEL = "api"  # its row in daily.routes
PROVIDERS = {
    "nvidia": Provider("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY", 2.0),
}
RETRIES = 3  # after the first attempt
RETRY_DELAY = 15.0  # doubled on each retry, unless the provider says how long (Retry-After)
# Replies stream in, so the limit is on silence, not on the whole reply: NVIDIA NIM may prefill a long
# prompt for minutes before the first token.
CHAT_TIMEOUT = httpx.Timeout(30.0, read=600.0)
MAX_TOKENS = 16384  # reasoning counts too
PICKS = 22  # stories the model shortlists: one page each, inside the webfetch budget
PAGE_CHARS = 8000  # of each page, cut into numbered passages
PASSAGE_MIN = 15  # shorter pieces are menus and buttons
CODE_SHARE = 0.08  # pieces with more of {}[]<>"=|\\ than this are inlined JSON and templates, not prose
SKILL_FILE = Path(__file__).resolve().parent.parent / ".claude/skills/daily-editor/SKILL.md"
RULES = ("## 2.", "## 4.", "## 5.")  # the skill's editorial sections; this module does the other steps
EN_RULES = ("## 4.", "## 5.", "## 7.")  # and those for the English edition

ROUTE_NOTES = """

## 在 API 通道运行（这一节优先于上文）

你通过云端模型 API 运行：没有 shell、工具和网络。准备、浏览候选、打开原文、校验和提交由程序完成。
程序分几步问你，每一步只回答一个 JSON 对象，不要别的文字：

1. 挑选：程序给出候选列表，你按第 2 节给每个候选打分，挑出值得写的。
2. 写作：程序打开你挑的原文，切成编号的片段；你按第 4、5 节写日报。evidence 只填片段编号，
   程序把原文逐字放进去，你不用复制引文，也不用写 research。
3. 修改：程序按 validate 的规则检查，把不合格的条目和原因发回给你，只有这一次机会；稿子没问题就没有这一步。

没有 WebSearch：不做补漏，只用候选。程序打不开的页面，只能依据候选的标题和摘要写。
生成记录也由程序记：第 2、5 节里的 `daily trace` 命令不用管，
分数写在挑选那一步的回答里。
"""

WRITE_FORMAT = """\
只回答 JSON：
{"highlights": ["……"], "items": [{"section": "headline", "title": "……", "summary": "……",
  "candidates": ["c_xxx"], "evidence": [3, 17], "tags": ["模型"]}],
 "skipped": [{"group": 5, "reason": "原文打不开，摘要写不出是什么"}]}

- section：headline | model | paper | tool | brief，按这个顺序排，版块内按重要性排。
- candidates：这一条依据的候选 id，第一个是主来源。一个候选只能用在一条里。
- evidence：支撑关键事实的片段编号，只能用这一条候选的原文片段。标题和 summary 里的每个数字、模型名、
  版本号，都要原样出现在这一条候选的标题 / 摘要或所引的片段里，否则整条会被删掉。
- skipped：你挑了却没有写的组，group 是组号，reason 用一句话说明原因。每一组要么写成条目，要么写在这里。
- kind 是 commentary 的候选（博主和周报）：只有作者的原创分析才能单独成条，只放进 brief，每期最多 2 条；
  评论别人发布的内容时，这一条不要写。"""

EN_ROUTE_NOTES = """

## 在 API 通道写英文版（这一节优先于上文）

你通过云端模型 API 运行：没有 shell、工具和网络。中文版已经通过校验，程序给出它的每一条：版块、
候选的标题和摘要、evidence 原文。你按第 7 步为每一条写英文的 title 和 summary，再写英文 highlights；
复制 digest.json、校验和提交由程序完成，第 5 节里的 `daily trace` 命令也不用管。只回答一个 JSON 对象，
不要别的文字。
"""

EN_FORMAT = """\
只回答 JSON：
{"highlights": ["……"], "items": [{"n": 1, "title": "……", "summary": "……"}]}

- n：条目编号。写不好的条目不要放进 items，程序会删掉它。
- 标题和 summary 里的每个数字、模型名、版本号，都要原样出现在这一条的候选标题 / 摘要或 evidence 里，
  否则整条会被删掉。"""

FIX_RULES = """\
数字或名称在这一条候选的标题 / 摘要和原文片段里都找不到：说明这一条写了材料之外的内容，整条删掉，
不要只删掉那个数字或名称后保留这一条。数字或名称在原文片段里、只是没有引用：补上片段编号。
其他错误（片段编号、长度之类）可以改。不要加入材料里没有的事实。"""

HIGHLIGHT_RULES = """\
今日要点的数字和名称只能来自已入选条目的标题和 summary，每句要点都要说得清引用的是哪一条。"""

# Claude's scores from earlier issues, to calibrate the pick step. They stay here, not in the skill:
# the Claude route does not need them, and the API route's scores are not used for statistics.
SCORE_EXAMPLES = """\
打分例子（[重要性, 实用性, 新颖性]）：
- [0, 0, 0]「OBLITERATUS/DeepSeek-V4.1-Flash-1017-obliterated」：别人做的去审查衍生权重。
- [0, 0, 0]「Running UNCENSORED DeepSeek-V4.1-Flash-1017 on a 12 Gb VRAM」：衍生权重的讨论帖。
- [1, 0, 1]「Preparing our next security sprint to harden OpenAI」：公司内部事务，和开发无关。
- [1, 1, 0]「The latest AI news we announced in October 2026」：月度汇总，没有新内容。
- [1, 1, 1]「langchain-ai/langchain langchain-core==1.7.4」：常规小版本。
- [2, 3, 2]「vllm-project/vllm v0.33.0」：主流工具的重要版本，开发者今天就能用上。
- [3, 2, 2]「China's First Frontier AI Export Controls: Mofcom Announcement No. 48」：行业格局变化。
多数候选的重要性和实用性都是 0 或 1；3 分每期只有几个。"""


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


def system_prompt(rules: tuple[str, ...] = RULES, notes: str = ROUTE_NOTES) -> str:
    text = SKILL_FILE.read_text(encoding="utf-8").split("---", 2)[2]  # without the frontmatter
    parts = re.split(r"(?m)^(?=## )", text)
    kept = [p.strip() for p in parts if not p.startswith("## ") or p.startswith(rules)]
    return "\n\n".join(kept) + notes


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
            # Every reply is a JSON object: JSON mode has the provider hold the model to valid JSON.
            "response_format": {"type": "json_object"},
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


async def _ask(chat: Chat, messages: list[dict[str, Any]]) -> dict[str, Any]:
    """One request, its answer as JSON; a reply that is not JSON is asked again once."""
    for attempt in (1, 2):
        content = (await chat.send(messages)).get("content") or ""
        messages.append({"role": "assistant", "content": content})
        try:
            return json_object(content)
        except ValueError as exc:
            if attempt == 2:
                raise EditorError(f"no JSON in the reply: {exc}") from exc
            messages.append({"role": "user", "content": f"回答不是一个 JSON 对象（{exc}）。只回答 JSON。"})
    raise AssertionError("unreachable")


def rank_groups(groups: list[list[str]], scores: dict[str, list[int]]) -> list[list[str]]:
    """Best total score first; a group counts as its best candidate, ties keep the model's order."""
    return sorted(groups, key=lambda group: -max(sum(scores.get(cid, [0])) for cid in group))


def _titles_as_highlights(data: dict[str, Any], report: digest.Report) -> bool:
    """Titles are published text, so they always pass as highlights: use the first ones when the
    highlights are what failed. False when something else failed too."""
    if not report.errors or not all(e.startswith("highlight") for e in report.errors):
        return False
    log.warning("highlights rejected (%s): using the first titles", "; ".join(report.errors))
    surviving = [item for i, item in enumerate(data["items"]) if i not in report.item_errors]
    data["highlights"] = [item["title"] for item in surviving[: digest.HIGHLIGHTS_MAX]]
    return True


class Editor:
    """One edit in at most three requests: pick, write, fix. Each request is a full turn on a free
    tier, so the reading is done here and not by the model.
    What each step kept and dropped goes into self.trace, whether or not the edit succeeds."""

    def __init__(self, candidates: dict[str, Any], model: str, client: httpx.AsyncClient) -> None:
        self.candidates = candidates
        self.trace = trace.new(candidates["date"], CHANNEL, model)
        self.step = "pick"
        self.by_id = {c["id"]: c for c in candidates["candidates"]}
        self.model = model
        self.client = client
        self.chat = Chat(model, client)
        self.pages: dict[str, digest.Page] = {}  # by url, fetched once per edit
        self.passages: list[Passage] = []  # numbered from 1 in the write prompt
        self.research: list[dict[str, str]] = []

    async def run(self) -> dict[str, Any]:
        try:
            return await self._run()
        except EditorError as exc:
            self.trace["failure"] = {"step": self.step, "error": str(exc)}
            raise

    async def _run(self) -> dict[str, Any]:
        groups = await self._pick()
        self.step = "read"
        await self._read(groups)
        messages = [
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": self._write_prompt(groups)},
        ]
        self.step = "draft"
        first = await self._ask(messages)
        data = self._draft(first)
        report = await self._validate(data)
        written = len(data["items"]) if isinstance(data["items"], list) else 0
        log.info("write: %d items, %d rejected", written, len(report.item_errors))
        self._record_skipped(first, groups, "draft")
        feedback = self._feedback(data, report)
        if feedback:
            self.step = "fix"
            messages.append({"role": "user", "content": feedback})
            second = await self._ask(messages)
            self._record_skipped(second, groups, "fix")
            if isinstance(second.get("items"), list) and second["items"]:
                data = self._draft(second)
                report = await self._validate(data)
                log.info("fix: %d items, %d rejected", len(data["items"]), len(report.item_errors))
            else:
                # Nothing to go on, and the draft may well be publishable without what it failed on.
                problem = "the fix reply has no items: keeping the draft"
                log.warning(problem)
                self._record({"step": "fix_ignored", "error": problem})
        if _titles_as_highlights(data, report):
            self.step = "highlights"
            report = await self._validate(data)
        if report.errors:
            raise EditorError("; ".join(report.errors))
        return digest.apply_report(data, report, checked_links=True)

    async def _ask(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        return await _ask(self.chat, messages)

    async def _pick(self) -> list[list[str]]:
        usable = [c for c in self.candidates["candidates"] if first_hand_url(c)]
        unusable = [c["id"] for c in self.candidates["candidates"] if not first_hand_url(c)]
        self._record({"step": "no_first_hand", "candidates": unusable})
        listing = pipeline.candidate_listing({**self.candidates, "candidates": usable}, summary_chars=300)
        prompt = (
            f"期号 {self.candidates['date']}。第一步：挑选。下面是候选，只有讨论帖、没有一手来源的已经去掉。"
            "按第 2 节给下面每一个候选打分，scores 里写 [重要性, 实用性, 新颖性]，一个都不要漏；"
            f"再挑出最多 {PICKS} 组值得写的，重要的在前；同一事件的几个候选放进同一组，"
            f"第一个是主来源，程序会打开它的原文。"
            f"期望最后写约 {digest.ITEMS_EXPECTED} 条，最多 {digest.ITEMS_TARGET[1]} 条，"
            "可以多挑几组留余量；值得写的不够时少写，不要凑数。\n" + SCORE_EXAMPLES + "\n"
            '只回答 JSON：{"scores": {"c_xxx": [3, 2, 2], "c_yyy": [1, 0, 1]}, '
            '"picks": [["c_xxx", "c_yyy"], ["c_zzz"]]}\n\n' + listing
        )
        answer = await self._ask(
            [{"role": "system", "content": system_prompt()}, {"role": "user", "content": prompt}]
        )
        known = {c["id"] for c in usable}
        self.trace["scores"] = trace.scores(answer.get("scores"), known)
        groups: list[list[str]] = []
        seen: set[str] = set()
        for group in answer.get("picks") or []:
            ids = [i for i in group if i in known and i not in seen] if isinstance(group, list) else []
            if ids:
                groups.append(ids)
                seen.update(ids)
        if not groups:
            raise EditorError("the model picked no known candidate")
        groups = rank_groups(groups, self.trace["scores"])
        log.info("pick: %d groups, %d candidates", len(groups[:PICKS]), len(seen))
        self._record({"step": "pick", "groups": groups[:PICKS]})
        if groups[PICKS:]:
            self._record({"step": "over_picks", "groups": groups[PICKS:]})
        return groups[:PICKS]

    def _record(self, step: dict[str, Any]) -> None:
        self.trace["steps"].append({"step": step.pop("step"), "at": trace.now(), **step})

    async def _read(self, groups: list[list[str]]) -> None:
        """Open each group's first candidate, as research, and number its passages."""
        heads = [(g[0], first_hand_url(self.by_id[g[0]]) or "") for g in groups]
        self.pages.update(await digest.check_links([url for _, url in heads], self.client))
        self.research = [{"via": "webfetch", "url": url} for url in dict.fromkeys(url for _, url in heads)]
        states = []
        for cid, url in heads:
            page = self.pages[url]
            text = page.body or page.text
            found = [Passage(url, cid, p) for p in passages(text)] if text else []
            self.passages += found
            state = "failed" if page.text is None else "ok" if found else "no_prose"
            states.append(
                {
                    "candidate": cid,
                    "url": url,
                    "state": state,
                    "status": page.status,
                    "error": page.error,
                    "passages": len(found),
                }
            )
        self._record({"step": "read", "pages": states})
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
            f"期望写约 {digest.ITEMS_EXPECTED} 条，最多 {digest.ITEMS_TARGET[1]} 条，超过时先写总分高的。"
        )
        return head + "\n\n" + WRITE_FORMAT + "\n\n" + "\n\n".join(blocks)

    def _item(self, raw: Any) -> Any:
        """The model's item, with its sources and evidence spelled out."""
        if not isinstance(raw, dict):
            return raw  # validate says what is wrong
        ids = [i for i in raw.get("candidates") or [] if isinstance(i, str)]
        sources = [
            {"candidate_id": i, "url": first_hand_url(self.by_id[i]) or self.by_id[i]["url"]}
            if i in self.by_id
            else {"candidate_id": i}
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
            "channel": CHANNEL,
            "model": self.model,
            "highlights": answer.get("highlights"),
            "items": [self._item(i) for i in items] if isinstance(items, list) else items,
            "research": self.research,
        }

    async def _validate(self, data: dict[str, Any]) -> digest.Report:
        """validate with the links checked."""
        missing = [url for url in digest.digest_urls(data) if url not in self.pages]
        self.pages.update(await digest.check_links(missing, self.client))
        report = digest.validate(data, self.candidates, self.pages)
        self.trace["steps"].append(trace.validate_step(self.step, data, report, checked_links=True))
        return report

    def _record_skipped(self, answer: dict[str, Any], groups: list[list[str]], round_: str) -> None:
        """The groups the model says it did not write, and why; what is malformed is left out."""
        raw = answer.get("skipped")
        if not isinstance(raw, list):
            return
        skipped = []
        for entry in raw:
            if not isinstance(entry, dict) or not isinstance(entry.get("reason"), str):
                continue
            group = entry.get("group")
            group = int(group) if isinstance(group, str) and group.isdigit() else group
            if isinstance(group, int) and 1 <= group <= len(groups):
                skipped.append({"group": group, "candidates": groups[group - 1], "reason": entry["reason"]})
        self._record({"step": "skipped", "round": round_, "skipped": skipped})

    def _feedback(self, data: dict[str, Any], report: digest.Report) -> str | None:
        """What to fix, None when nothing failed. Never how many items there are: that would ask for
        padding, and an issue with few good items is fine (too few to publish fails the edit)."""
        items = data["items"] if isinstance(data["items"], list) else []
        titles = [item.get("title") if isinstance(item, dict) else "" for item in items]
        lines = [
            f"- 第 {i + 1} 条「{titles[i]}」：{'; '.join(e)}" for i, e in sorted(report.item_errors.items())
        ]
        errors = [e for e in report.errors if not e.endswith(f"valid items (minimum {digest.MIN_ITEMS})")]
        lines += [f"- {e}" for e in errors]
        if not lines:
            return None
        text = "第三步：修改。程序按 validate 检查了你的稿子。\n不合格：\n" + "\n".join(lines) + "\n"
        text += FIX_RULES + "\n"
        if any(e.startswith("highlight:") for e in errors):
            good = [f"第 {i + 1} 条「{t}」" for i, t in enumerate(titles) if i not in report.item_errors]
            text += HIGHLIGHT_RULES + "目前通过校验的条目：" + "、".join(good) + "。\n"
        return text + "回答修改后的完整 JSON，格式同上，包括没有问题的条目和 highlights。"


async def write_en(
    main: dict[str, Any],
    candidates: dict[str, Any],
    model: str,
    client: httpx.AsyncClient,
    steps: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """The English edition of the validated API digest `main`, in one request: the model writes the
    titles, summaries and highlights from the same material, the rest is copied (SKILL.md step 7).
    EditorError if it does not pass validate --en. Its validate rounds are appended to steps, the
    trace's, and so is the error of a request that fails."""
    steps = [] if steps is None else steps
    recorded = len(steps)
    try:
        return await _write_en(main, candidates, model, client, steps)
    except EditorError as exc:
        if len(steps) == recorded:  # the request failed: no validate round says why
            steps.append({"step": "en", "at": trace.now(), "error": str(exc)})
        raise


async def _write_en(
    main: dict[str, Any],
    candidates: dict[str, Any],
    model: str,
    client: httpx.AsyncClient,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    by_id = {c["id"]: c for c in candidates["candidates"]}
    blocks = []
    for number, item in enumerate(main["items"], 1):
        lines = [f"## 第 {number} 条（{item['section']}）"]
        shown: set[str] = set()
        for source in item["sources"]:
            c = by_id.get(source.get("candidate_id") or "")
            if c is None:
                lines.append(f"{source.get('title') or ''} {source['url']}".strip())
            elif c["id"] not in shown:
                shown.add(c["id"])
                lines += [
                    f"{c['id']} {c['kind']} [{c.get('source_name') or c['source']}] {c['title']}",
                    "摘要：" + " ".join((c["summary"] or "").split())[:1500],
                ]
        lines += ["evidence："] + [f"- {e['quote']}" for e in item.get("evidence") or []]
        blocks.append("\n".join(lines))
    prompt = (
        f"期号 {main['date']}，写英文版。下面是中文版的 {len(blocks)} 条，"
        "每条给出候选的标题、摘要和 evidence 原文，不给中文正文：依据原文写，不要翻译。\n\n"
        + EN_FORMAT
        + "\n\n"
        + "\n\n".join(blocks)
    )
    messages = [
        {"role": "system", "content": system_prompt(EN_RULES, EN_ROUTE_NOTES)},
        {"role": "user", "content": prompt},
    ]
    answer = await _ask(Chat(model, client), messages)

    written: dict[int, dict[str, Any]] = {}
    for raw in answer.get("items") or []:
        n = raw.get("n") if isinstance(raw, dict) else None
        n = int(n) if isinstance(n, str) and n.isdigit() else n
        if isinstance(n, int) and n not in written:
            written[n] = raw
    data = {key: value for key, value in main.items() if key != "validation"}
    data.update(
        lang="en",
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        highlights=answer.get("highlights"),
        items=[
            {**item, "title": written[n].get("title"), "summary": written[n].get("summary")}
            for n, item in enumerate(main["items"], 1)
            if n in written
        ],
    )
    # Evidence was checked against the pages with the main issue (step 7: one offline round).
    report = digest.validate(data, candidates)
    steps.append(trace.validate_step("en", data, report, checked_links=False))
    written_count, rejected = len(data["items"]), len(report.item_errors)
    log.info("english: %d of %d items written, %d rejected", written_count, len(blocks), rejected)
    if _titles_as_highlights(data, report):
        report = digest.validate(data, candidates)
        steps.append(trace.validate_step("en_highlights", data, report, checked_links=False))
    if report.errors:
        raise EditorError("; ".join(report.errors))
    return digest.apply_report(data, report, checked_links=False)
