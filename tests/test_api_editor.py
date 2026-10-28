import json

import httpx
import pytest

from daily import api_editor, cli, digest, publish
from tests.test_digest import CANDIDATES, DATE, _digest

CHAT = "integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia:deepseek-ai/deepseek-v4.1-flash"
PAGES = {
    "openai.com/index/gpt-6/": (
        "<header>Sign in to read the whole announcement today.</header>\n"
        "<main><p>GPT-6 has a <b>1M token</b> context window.</p>\n"
        '<div>{"downloads":2787,"id":"openai/gpt-6","gated":false}</div>\n<nav>Menu</nav></main>'
    ),
    "github.com/vllm-project/vllm/releases/tag/v0.12.0": "<p>Speculative decoding is now 40% faster.</p>",
    "huggingface.co/Qwen/Qwen3.5-72B": "ok",
    "huggingface.co/papers/2610.00001": "ok",
}
GROUPS = [["c_gpt"], ["c_vllm"], ["c_qwen"], ["c_paper"]]
GPT, VLLM = 1, 2  # their pages' passages, numbered in the order of GROUPS


def _reply(content):
    """A streamed reply: the content arrives in pieces, as on the wire."""
    deltas = [{"role": "assistant"}] + [{"content": content[i : i + 7]} for i in range(0, len(content), 7)]
    events = [json.dumps({"choices": [{"index": 0, "delta": d}]}) for d in deltas] + ["[DONE]"]
    body = "".join(f"data: {e}\n\n" for e in events)
    return httpx.Response(200, content=body.encode(), headers={"content-type": "text/event-stream"})


def _picks(groups=GROUPS):
    return _reply("```json\n" + json.dumps({"picks": groups}) + "\n```")


def _written(evidence=None, highlights=None, count=4, **changes):
    """The model's answer to the write prompt: _digest()'s first items, changed by index."""
    draft = _digest()
    items = []
    for index, item in enumerate(draft["items"][:count]):
        item = {**item, **changes.get(f"item{index}", {})}
        items.append(
            {
                "section": item["section"],
                "title": item["title"],
                "summary": item["summary"],
                "candidates": [s["candidate_id"] for s in item["sources"]],
                "evidence": (evidence or {}).get(index, []),
                "tags": item["tags"],
            }
        )
    return _reply(
        json.dumps({"highlights": highlights or draft["highlights"], "items": items}, ensure_ascii=False)
    )


FASTER = {"item1": {"summary": "新版本的投机解码快了 40%。"}}  # only the vLLM page says 40%


class FakeWeb:
    """The model API answers from a script; every other host serves PAGES."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.chats = []

    def client(self):
        return httpx.AsyncClient(transport=httpx.MockTransport(self.handle))

    def handle(self, request):
        key = f"{request.url.host}{request.url.path}"
        if key == CHAT:
            self.chats.append(request)
            reply = self.replies.pop(0)
            if isinstance(reply, Exception):
                raise reply
            return reply
        if key in PAGES:
            return httpx.Response(200, html=PAGES[key])
        return httpx.Response(404)

    def prompt(self, index):
        """The last user message of a request."""
        return json.loads(self.chats[index].content)["messages"][-1]["content"]


@pytest.fixture
def issue_dir(tmp_path, monkeypatch):
    folder = tmp_path / DATE
    folder.mkdir()
    (folder / "candidates.json").write_text(json.dumps({**CANDIDATES, "clusters": [], "sources": []}))
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test")
    return folder


@pytest.fixture
def slept(monkeypatch):
    seconds = []

    async def sleep(value):
        seconds.append(value)

    monkeypatch.setattr(api_editor, "_sleep", sleep)
    return seconds


def _edit(issue_dir, web, monkeypatch):
    monkeypatch.setattr(cli.pipeline, "make_client", web.client)
    return cli.main(["edit", "--date", DATE, "--data-dir", str(issue_dir.parent), "--model", MODEL])


def _result(issue_dir):
    return json.loads((issue_dir / "digest.api.deepseek.json").read_text())


def test_edit_picks_writes_and_fixes_in_three_requests(issue_dir, slept, monkeypatch, capsys):
    web = FakeWeb(
        [
            _picks([*GROUPS, ["c_hn", "c_nope"]]),  # not offered, and unknown: ignored
            _written(**FASTER),  # 40% without the passage that says so: sent back
            _written({0: [GPT], 1: [VLLM]}, **FASTER),
        ]
    )
    assert _edit(issue_dir, web, monkeypatch) == 0

    path = issue_dir / "digest.api.deepseek.json"
    assert capsys.readouterr().out.strip() == str(path)
    written = _result(issue_dir)
    assert (written["channel"], written["model"], written["mode"], written["date"]) == (
        "api",
        MODEL,
        "full",
        DATE,
    )
    assert len(written["items"]) == 4 and written["validation"]["checked_links"] is True
    assert written["items"][1]["evidence"] == [
        {
            "url": "https://github.com/vllm-project/vllm/releases/tag/v0.12.0",
            "quote": "Speculative decoding is now 40% faster.",  # verbatim from the page
        }
    ]
    assert [r["url"] for r in written["research"]] == [
        "https://openai.com/index/gpt-6/",
        "https://github.com/vllm-project/vllm/releases/tag/v0.12.0",
        "https://huggingface.co/Qwen/Qwen3.5-72B",
        "https://huggingface.co/papers/2610.00001",
    ]

    assert len(web.chats) == 3
    request = json.loads(web.chats[0].content)
    assert request["model"] == "deepseek-ai/deepseek-v4.1-flash" and request["stream"] is True
    assert "tools" not in request
    assert web.chats[0].headers["authorization"] == "Bearer nvapi-test"
    system = request["messages"][0]["content"]
    assert "宁缺毋滥" in system and "写作规范" in system  # the skill's editorial rules
    assert "git push" not in system  # its steps that run commands are done here

    assert "c_gpt" in web.prompt(0) and "c_hn" not in web.prompt(0)  # a discussion thread alone is no story
    assert f"[{GPT}] GPT-6 has a 1M token context window." in web.prompt(1)
    assert "Sign in" not in web.prompt(1)  # outside the page's main body
    assert "Menu" not in web.prompt(1)  # too short to be a passage
    assert "downloads" not in web.prompt(1)  # inlined JSON is no passage either
    assert "40" in web.prompt(2) and "第 2 条" in web.prompt(2)  # what to fix, item by item


def test_a_clean_draft_takes_two_requests(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert len(web.chats) == 2 and len(_result(issue_dir)["items"]) == 4


def test_too_few_items_asks_for_the_unused_picks(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written(count=3), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "还没用上的组：4" in web.prompt(2)
    assert len(_result(issue_dir)["items"]) == 4


def test_highlights_that_still_fail_become_the_first_titles(issue_dir, slept, monkeypatch):
    wrong = ["OpenAI 发布 GPT-7。"]  # GPT-7 is in no item
    web = FakeWeb([_picks(), _written(highlights=wrong), _written(highlights=wrong)])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "highlight" in web.prompt(2)
    titles = [item["title"] for item in _digest()["items"]]
    assert _result(issue_dir)["highlights"] == titles[:3]


def test_edit_fails_when_the_reply_is_not_json(issue_dir, slept, monkeypatch):
    web = FakeWeb([_reply("我挑好了。"), _reply("还是没有 JSON。")])
    assert _edit(issue_dir, web, monkeypatch) == 1
    assert "JSON" in web.prompt(1)  # asked once more
    assert not (issue_dir / "digest.api.deepseek.json").exists()


def test_edit_retries_a_stream_that_goes_quiet(issue_dir, slept, monkeypatch):
    web = FakeWeb([httpx.ReadTimeout("no data for a while"), _picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert len(web.chats) == 3


def test_rate_limits_are_waited_out_longer_each_time(issue_dir, slept, monkeypatch):
    limited = httpx.Response(429, json={"status": 429})
    told = httpx.Response(429, headers={"retry-after": "42"}, json={"status": 429})
    web = FakeWeb([limited, limited, told, _picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert [s for s in slept if s >= 15] == [15, 30, 42]


def test_edit_needs_a_known_provider_and_its_key(issue_dir, monkeypatch):
    web = FakeWeb([])
    monkeypatch.setattr(cli.pipeline, "make_client", web.client)
    base = ["edit", "--date", DATE, "--data-dir", str(issue_dir.parent), "--model"]
    assert cli.main([*base, "acme:some-model"]) == 2
    monkeypatch.delenv("NVIDIA_API_KEY")
    assert cli.main([*base, MODEL]) == 2
    assert web.chats == []


def _api_digest(issue_dir):
    """The API digest that `edit` wrote, validated as it would be."""
    data = _digest(channel="api", model=MODEL, generated_at="2026-10-20T03:40:00+00:00")
    report = digest.validate(data, CANDIDATES)
    path = issue_dir / "digest.api.deepseek.json"
    path.write_text(json.dumps(digest.apply_report(data, report, checked_links=True), ensure_ascii=False))
    return path


ENGLISH = {
    "highlights": ["OpenAI releases GPT-6 with a 1M token context."],
    "items": [
        {"n": 1, "title": "OpenAI releases GPT-6", "summary": "GPT-6 has a 1M token context window."},
        {"n": "2", "title": "vLLM v0.12.0 supports GPT-6", "summary": "The release adds GPT-6 support."},
        {"n": 3, "title": "Qwen3.5-72B goes open source", "summary": "Released under Apache-2.0."},
        # GPT-7 is not in the material
        {"n": 4, "title": "Scaling laws for agents", "summary": "Agents scale like GPT-7."},
    ],
}


def _edit_en(issue_dir, web, monkeypatch, path):
    monkeypatch.setattr(cli.pipeline, "make_client", web.client)
    return cli.main(["edit", "--date", DATE, "--data-dir", str(issue_dir.parent), "--en", str(path)])


def test_edit_en_writes_the_english_edition_in_one_request(issue_dir, slept, monkeypatch, capsys):
    path = _api_digest(issue_dir)
    web = FakeWeb([_reply(json.dumps(ENGLISH))])
    assert _edit_en(issue_dir, web, monkeypatch, path) == 0

    out = issue_dir / "digest.en.deepseek.json"
    assert capsys.readouterr().out.strip() == str(out)
    en, zh = json.loads(out.read_text()), json.loads(path.read_text())
    assert (en["lang"], en["channel"], en["model"]) == ("en", "api", MODEL)
    assert en["generated_at"] > zh["generated_at"]
    assert [item["title"] for item in en["items"]] == [i["title"] for i in ENGLISH["items"][:3]]
    assert en["items"][0]["sources"] == zh["items"][0]["sources"]  # only the writing changes
    assert en["items"][0]["tags"] == zh["items"][0]["tags"]
    assert en["highlights"] == ENGLISH["highlights"]
    assert en["validation"]["checked_links"] is False
    assert [d["title"] for d in en["validation"]["dropped"]] == ["Scaling laws for agents"]
    assert publish.goes_with(zh, en, CANDIDATES) is None

    assert len(web.chats) == 1
    request = json.loads(web.chats[0].content)
    assert request["model"] == "deepseek-ai/deepseek-v4.1-flash"
    assert "英文版" in request["messages"][0]["content"] and "打分" not in request["messages"][0]["content"]
    prompt = web.prompt(0)
    assert "OpenAI 发布 GPT-6" not in prompt  # written from the material, not translated
    assert "c_gpt" in prompt and "第 4 条（paper）" in prompt


def test_edit_en_skips_a_digest_that_would_not_be_the_main_issue(issue_dir, slept, monkeypatch, capsys):
    path = _api_digest(issue_dir)
    (issue_dir / "digest.json").write_text(json.dumps(_digest(), ensure_ascii=False))  # a Claude edit
    web = FakeWeb([])
    assert _edit_en(issue_dir, web, monkeypatch, path) == 0
    assert "would not be the main issue" in capsys.readouterr().err
    assert web.chats == [] and not (issue_dir / "digest.en.deepseek.json").exists()


def test_edit_en_fails_without_writing_when_validate_rejects_it(issue_dir, slept, monkeypatch):
    path = _api_digest(issue_dir)
    english = {**ENGLISH, "items": ENGLISH["items"][3:]}  # too few items left
    web = FakeWeb([_reply(json.dumps(english))])
    assert _edit_en(issue_dir, web, monkeypatch, path) == 1
    assert not (issue_dir / "digest.en.deepseek.json").exists()


def test_edit_en_highlights_that_fail_become_the_first_titles(issue_dir, slept, monkeypatch):
    path = _api_digest(issue_dir)
    web = FakeWeb([_reply(json.dumps({**ENGLISH, "highlights": ["OpenAI ships GPT-7."]}))])
    assert _edit_en(issue_dir, web, monkeypatch, path) == 0
    en = json.loads((issue_dir / "digest.en.deepseek.json").read_text())
    assert en["highlights"] == [i["title"] for i in ENGLISH["items"][:3]]
