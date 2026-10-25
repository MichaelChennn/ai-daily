"""Blog index pages without a feed (Anthropic, Mistral...).

Layout-agnostic on purpose, because every site arranges its cards differently (date before the
link, after it, inside it; <article>, table rows, carousels):

1. Every <a> whose href matches `link_pattern` is a link to a post. Links whose text is short and
   holds no heading are category chips or "Read more" and do not define a post; an empty link
   with an aria-label is a card overlay and does.
2. A post's card is the largest element around one of its links that contains no other post
   (nor any other link wrapping a heading): the first such card that holds a date, else the
   first link's card (nav menus and hero images often link to a post before its dated card).
3. The title is a heading in the post's links (else in the card, else the longest link text);
   the date is the first <time> / written date in the card; the summary is its longest <p>.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, get
from daily.models import Candidate
from daily.text import clean_text, clean_title, find_date, parse_datetime, truncate
from daily.window import Window

MIN_TITLE_CHARS = 15
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP = {"script", "style", "svg", "noscript", "template"}


@dataclass(eq=False)
class Node:
    tag: str
    attrs: dict[str, str]
    parent: Node | None = None
    children: list[Node | str] = field(default_factory=list)

    def text(self) -> str:
        return " ".join(c if isinstance(c, str) else c.text() for c in self.children)

    def iter(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.iter()

    def find_all(self, tags: set[str]) -> list[Node]:
        return [n for n in self.iter() if n.tag in tags]


class _TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {})
        self.current = self.root
        self.skipping = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skipping or tag in SKIP:
            self.skipping += tag in SKIP
            return
        node = Node(tag, {k: v or "" for k, v in attrs}, parent=self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP:
            self.skipping = max(0, self.skipping - 1)
            return
        if self.skipping:
            return
        node: Node | None = self.current
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:  # ignore stray closing tags
            self.current = node.parent

    def handle_data(self, data: str) -> None:
        if not self.skipping and data.strip():
            self.current.children.append(data)


def parse_html(html: str) -> Node:
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    return builder.root


async def fetch_html_listing(
    client: httpx.AsyncClient, source: SourceConfig, window: Window
) -> list[Candidate]:
    """Options: url; link_pattern (regex on the href, required); exclude_pattern (optional)."""
    page_url = source.options["url"]
    link_pattern = re.compile(source.options["link_pattern"])
    exclude = re.compile(source.options["exclude_pattern"]) if source.options.get("exclude_pattern") else None
    root = parse_html((await get(client, page_url)).text)

    links: dict[str, list[Node]] = {}  # href -> its <a> nodes, in page order
    for a in root.find_all({"a"}):
        href = a.attrs.get("href", "")
        if link_pattern.search(href) and not (exclude and exclude.search(href)):
            links.setdefault(href, []).append(a)
    posts = {href: anchors for href, anchors in links.items() if _defines_post(anchors)}
    if not posts:
        raise ValueError("no post links found; page layout may have changed")

    # Card boundaries: links to other posts, plus any titled link (a featured card may point
    # outside link_pattern, e.g. anthropic.com/claude-opus-5-5).
    owner = {id(a): a.attrs.get("href", "") for a in root.find_all({"a"}) if a.find_all(HEADINGS)}
    owner.update({id(a): href for href, anchors in posts.items() for a in anchors})
    items: list[Candidate] = []
    for href, anchors in posts.items():
        card, published, precision = _dated_card(anchors, href, owner)
        if not window.contains(published, precision):
            continue
        title = _title(anchors, card)
        paragraphs = [clean_text(p.text()) for p in card.find_all({"p"})]
        paragraphs = [p for p in paragraphs if len(p) >= MIN_TITLE_CHARS and p != title and not _is_byline(p)]
        items.append(
            candidate(
                source,
                title=title,
                url=urljoin(page_url, href),
                summary=truncate(max(paragraphs, key=len, default=""), SUMMARY_MAX_CHARS),
                published_at=published,
                published_precision=precision,
            )
        )
    return items


def _defines_post(anchors: list[Node]) -> bool:
    return any(
        a.find_all(HEADINGS)
        or len(clean_title(a.text())) >= MIN_TITLE_CHARS
        or (not clean_title(a.text()) and a.attrs.get("aria-label"))
        for a in anchors
    )


def _dated_card(anchors: list[Node], href: str, owner: dict[int, str]) -> tuple[Node, datetime | None, str]:
    for anchor in anchors:
        card = _card(anchor, href, owner)
        published, precision = _date(card)
        if published is not None:
            return card, published, precision
    card = _card(anchors[0], href, owner)
    return card, *_date(card)


def _card(anchor: Node, href: str, owner: dict[int, str]) -> Node:
    card = anchor
    while card.parent is not None and card.parent.tag != "#root":
        others = {owner.get(id(a)) for a in card.parent.find_all({"a"})} - {None, href}
        if others:
            break
        card = card.parent
    return card


def _title(anchors: list[Node], card: Node) -> str:
    for scope in [*anchors, card]:
        for heading in scope.find_all(HEADINGS):
            if title := clean_title(heading.text()):
                return title
    return max((clean_title(a.text() or a.attrs.get("aria-label")) for a in anchors), key=len)


def _date(card: Node) -> tuple[datetime | None, str]:
    for node in card.find_all({"time"}):
        raw = node.attrs.get("datetime", "")
        if raw and (parsed := parse_datetime(raw)):
            return parsed, "day" if len(raw) <= 10 else "second"
        if parsed := find_date(clean_text(node.text())):
            return parsed, "day"
    return find_date(clean_text(card.text())), "day"


def _is_byline(text: str) -> bool:
    """Short paragraphs that are only a date or an author line."""
    return len(text) < 60 and (find_date(text) is not None or text.lower().startswith("by "))
