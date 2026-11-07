import json

import httpx
import pytest

from daily import api_editor, cli, digest, edit, llm, pipeline, process, publish
from daily.issue import IssueDir
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

    monkeypatch.setattr(llm, "_sleep", sleep)
    return seconds


def _edit(issue_dir, web, monkeypatch):
    monkeypatch.setattr(pipeline, "make_client", web.client)
    monkeypatch.setattr(edit, "_write_en", lambda *args: None)  # the English edition: test_edit_runs_*
    return edit.run(IssueDir(issue_dir), [MODEL])


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
    assert request["response_format"] == {"type": "json_object"}
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


def test_few_items_are_not_sent_back_for_more(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written(count=3)])  # all clean, fewer than ITEMS_TARGET: no fix round
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert len(web.chats) == 2 and len(_result(issue_dir)["items"]) == 3


def test_the_fix_round_does_not_talk_about_item_counts(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written(count=3, **FASTER), _written({1: [VLLM]}, count=3, **FASTER)])
    assert _edit(issue_dir, web, monkeypatch) == 0
    feedback = web.prompt(2)
    assert "第 2 条" in feedback  # what to fix
    for padding in ("目标", "还没用上", "合格 2 条", "valid items"):
        assert padding not in feedback


def test_too_few_clean_items_fail_without_a_fix_round(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written(count=2)])
    assert _edit(issue_dir, web, monkeypatch) == 1
    assert len(web.chats) == 2


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
    monkeypatch.setattr(pipeline, "make_client", web.client)
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
    monkeypatch.setattr(pipeline, "make_client", web.client)
    return edit.write_en_for(IssueDir(issue_dir), path)


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


def _trace(issue_dir):
    return json.loads((issue_dir / "trace.api.deepseek.json").read_text())


def test_edit_records_its_steps_and_scores_in_the_trace(issue_dir, slept, monkeypatch):
    scores = {"c_gpt": [3, 2, 2], "c_vllm": [2, 3, 1], "c_qwen": [9, 0, 0], "c_nope": [1, 1, 1]}
    picks = _reply(json.dumps({"scores": scores, "picks": GROUPS}))
    web = FakeWeb([picks, _written(**FASTER), _written({0: [GPT], 1: [VLLM]}, **FASTER)])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "scores" in web.prompt(0)

    trace = _trace(issue_dir)
    assert (trace["channel"], trace["model"], trace["date"], trace["failure"]) == ("api", MODEL, DATE, None)
    assert trace["scores"] == {"c_gpt": [3, 2, 2], "c_vllm": [2, 3, 1]}  # out of range or unknown: left out
    steps = trace["steps"]
    assert [s["step"] for s in steps] == ["no_first_hand", "pick", "read", "draft", "fix"]
    assert steps[0]["candidates"] == ["c_hn"] and steps[1]["groups"] == GROUPS
    draft, fix = steps[3], steps[4]
    assert draft["checked_links"] is True
    assert [i["candidates"] for i in draft["items"]] == [["c_gpt"], ["c_vllm"], ["c_qwen"], ["c_paper"]]
    assert draft["items"][1]["reasons"] and not draft["items"][0]["reasons"]  # 40% unsupported
    assert not any(i["reasons"] for i in fix["items"])


def test_picks_over_the_limit_are_recorded(issue_dir, slept, monkeypatch):
    monkeypatch.setattr(api_editor, "PICKS", 3)
    web = FakeWeb([_picks(), _written(count=3)])
    assert _edit(issue_dir, web, monkeypatch) == 0
    over = next(s for s in _trace(issue_dir)["steps"] if s["step"] == "over_picks")
    assert over["groups"] == [["c_paper"]]


def test_a_failed_edit_still_writes_its_trace(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _reply("写好了。"), _reply("还是没有。")])
    assert _edit(issue_dir, web, monkeypatch) == 1
    trace = _trace(issue_dir)
    assert trace["failure"]["step"] == "draft" and "JSON" in trace["failure"]["error"]
    assert [s["step"] for s in trace["steps"]] == ["no_first_hand", "pick", "read"]

    monkeypatch.delenv("NVIDIA_API_KEY")
    assert _edit(issue_dir, FakeWeb([]), monkeypatch) == 2
    assert _trace(issue_dir)["failure"] == {"step": "setup", "error": "NVIDIA_API_KEY is not set"}


def test_edit_en_adds_its_round_to_the_trace(issue_dir, slept, monkeypatch):
    path = _api_digest(issue_dir)
    web = FakeWeb([_reply(json.dumps(ENGLISH))])
    assert _edit_en(issue_dir, web, monkeypatch, path) == 0
    (step,) = _trace(issue_dir)["steps"]
    assert step["step"] == "en" and step["checked_links"] is False
    assert [bool(i["reasons"]) for i in step["items"]] == [False, False, False, True]  # GPT-7

    web = FakeWeb([_reply("no JSON"), _reply("still none")])
    assert _edit_en(issue_dir, web, monkeypatch, path) == 1
    assert "JSON" in _trace(issue_dir)["steps"][-1]["error"]


# --- #51: A1-A6 -------------------------------------------------------------------------------


def test_picks_and_prompts_carry_the_item_targets(issue_dir, slept, monkeypatch):
    assert api_editor.PICKS == 22
    web = FakeWeb([_picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    for index in (0, 1):
        assert f"{digest.ITEMS_EXPECTED} 条" in web.prompt(index)
        assert f"最多 {digest.ITEMS_TARGET[1]} 条" in web.prompt(index)


def test_a1_a_made_up_number_means_the_item_goes(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written(**FASTER), _written({0: [GPT], 1: [VLLM]}, **FASTER)])
    assert _edit(issue_dir, web, monkeypatch) == 0
    feedback = web.prompt(2)
    assert "整条删掉" in feedback and "片段编号" in feedback
    assert "删掉材料里没有的数字" not in feedback


def test_a2_rejected_highlights_are_told_where_their_numbers_may_come_from(issue_dir, slept, monkeypatch):
    wrong = ["OpenAI 发布 GPT-7。"]
    web = FakeWeb([_picks(), _written(highlights=wrong), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    feedback = web.prompt(2)
    assert "已入选条目的标题和 summary" in feedback and "哪一条" in feedback
    assert "第 1 条「OpenAI 发布 GPT-6」" in feedback  # the items it may draw on


def test_a2_rejected_items_get_no_highlight_note(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written(**FASTER), _written({0: [GPT], 1: [VLLM]}, **FASTER)])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "已入选条目的标题和 summary" not in web.prompt(2)


REDDIT_POST = "https://www.reddit.com/r/LocalLLaMA/comments/9/tool/"


def _with_post(issue_dir, links):
    """Adds a Reddit post that has no first-hand page of its own, its body linking to links."""
    data = json.loads((issue_dir / "candidates.json").read_text())
    data["candidates"].append(
        {
            **data["candidates"][4],
            "id": "c_post",
            "title": "I made vLLM faster",
            "url": REDDIT_POST,
            "discussion_url": REDDIT_POST,
            "links": links,
        }
    )
    (issue_dir / "candidates.json").write_text(json.dumps(data))


def test_a3_a_link_in_the_post_body_is_its_first_hand_source(issue_dir, slept, monkeypatch):
    _with_post(issue_dir, ["https://github.com/vllm-project/vllm/releases/tag/v0.12.0"])
    answer = {
        "highlights": ["有人让 vLLM 更快了。"],
        "items": [
            {
                "section": "tool",
                "title": "有人让 vLLM 更快了",
                "summary": "投机解码快了 40%。",
                "candidates": ["c_post"],
                "evidence": [1],
                "tags": ["工具"],
            },
        ],
    }
    web = FakeWeb([_picks([["c_post"]]), _reply(json.dumps(answer, ensure_ascii=False))])
    _edit(issue_dir, web, monkeypatch)  # too few items: the point is what was offered and opened
    assert "c_post" in web.prompt(0)
    assert "[1] Speculative decoding is now 40% faster." in web.prompt(1)
    (step,) = [s for s in _trace(issue_dir)["steps"] if s["step"] == "draft"]
    assert step["items"][0]["reasons"] == []
    (no_first_hand,) = [s for s in _trace(issue_dir)["steps"] if s["step"] == "no_first_hand"]
    assert no_first_hand["candidates"] == ["c_hn"]


def test_a3_the_body_link_is_the_items_source_even_without_evidence(issue_dir, slept, monkeypatch):
    link = "https://github.com/vllm-project/vllm/releases/tag/v0.12.0"
    _with_post(issue_dir, [link])
    data = json.loads((issue_dir / "candidates.json").read_text())
    editor = api_editor.Editor(data, MODEL, FakeWeb([]).client())
    item = editor._item({"section": "tool", "title": "t", "summary": "s", "candidates": ["c_post"]})
    assert item["sources"] == [{"candidate_id": "c_post", "url": link}]


def test_a3_a_post_without_links_is_still_left_out(issue_dir, slept, monkeypatch):
    _with_post(issue_dir, [])
    web = FakeWeb([_picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "c_post" not in web.prompt(0)
    assert "c_post" in _trace(issue_dir)["steps"][0]["candidates"]


def test_a4_the_trace_says_how_each_page_opened(issue_dir, slept, monkeypatch):
    monkeypatch.setitem(PAGES, "huggingface.co/papers/2610.00001", "<p>{}</p>")
    data = json.loads((issue_dir / "candidates.json").read_text())
    data["candidates"][1]["url"] = "https://github.com/gone"
    (issue_dir / "candidates.json").write_text(json.dumps(data))
    web = FakeWeb([_picks(), _written(count=1), _written(count=1)])
    _edit(issue_dir, web, monkeypatch)
    (read,) = [s for s in _trace(issue_dir)["steps"] if s["step"] == "read"]
    pages = {p["candidate"]: p for p in read["pages"]}
    assert pages["c_gpt"]["state"] == "ok" and pages["c_gpt"]["status"] == 200
    assert pages["c_gpt"]["passages"] == 1 and pages["c_gpt"]["url"] == "https://openai.com/index/gpt-6/"
    assert pages["c_vllm"]["state"] == "failed" and pages["c_vllm"]["status"] == 404
    assert pages["c_paper"]["state"] == "no_prose" and pages["c_paper"]["passages"] == 0


def test_a5_the_groups_the_model_skipped_go_into_the_trace(issue_dir, slept, monkeypatch):
    written = json.loads(_written_json())
    written["skipped"] = [
        {"group": 2, "reason": "页面打不开"},
        {"group": "3", "reason": "不重要"},
        {"group": 99, "reason": "没有这一组"},
        {"group": 4},
        "乱写",
    ]
    web = FakeWeb([_picks(), _reply(json.dumps(written, ensure_ascii=False))])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "skipped" in web.prompt(1)
    (step,) = [s for s in _trace(issue_dir)["steps"] if s["step"] == "skipped"]
    assert step["round"] == "draft"
    assert step["skipped"] == [
        {"group": 2, "candidates": ["c_vllm"], "reason": "页面打不开"},
        {"group": 3, "candidates": ["c_qwen"], "reason": "不重要"},
    ]


def test_a5_no_skipped_answer_records_no_step(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert not [s for s in _trace(issue_dir)["steps"] if s["step"] == "skipped"]


def _written_json():
    return "".join(
        json.loads(line[5:])["choices"][0]["delta"].get("content", "")
        for line in _written().content.decode().splitlines()
        if line.startswith("data:") and "[DONE]" not in line
    )


def test_a6_the_pick_prompt_has_score_examples(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    prompt = web.prompt(0)
    assert api_editor.SCORE_EXAMPLES in prompt
    for score in ("[0, 0, 0]", "[1, 1, 1]", "[3, 2, 2]"):
        assert score in prompt
    system = json.loads(web.chats[0].content)["messages"][0]["content"]
    assert api_editor.SCORE_EXAMPLES not in system


def test_a6_groups_are_ranked_by_score_before_the_pages_are_chosen(issue_dir, slept, monkeypatch):
    monkeypatch.setattr(api_editor, "PICKS", 2)
    scores = {"c_gpt": [1, 0, 0], "c_vllm": [0, 1, 1], "c_qwen": [2, 2, 2], "c_paper": [3, 3, 1]}
    picks = _reply(json.dumps({"scores": scores, "picks": [["c_gpt"], ["c_vllm"], ["c_qwen"], ["c_paper"]]}))
    web = FakeWeb([picks, _written(count=1), _written(count=1)])
    _edit(issue_dir, web, monkeypatch)
    steps = {s["step"]: s for s in _trace(issue_dir)["steps"]}
    assert steps["pick"]["groups"] == [["c_paper"], ["c_qwen"]]
    assert steps["over_picks"]["groups"] == [["c_vllm"], ["c_gpt"]]
    assert [p["candidate"] for p in steps["read"]["pages"]] == ["c_paper", "c_qwen"]


def test_a6_a_group_counts_as_its_best_member_and_ties_keep_the_models_order():
    groups = [["c_a"], ["c_b", "c_c"], ["c_d"], ["c_e"]]
    scores = {"c_a": [1, 1, 1], "c_b": [0, 0, 0], "c_c": [2, 2, 2], "c_d": [1, 1, 1]}
    assert api_editor.rank_groups(groups, scores) == [["c_b", "c_c"], ["c_a"], ["c_d"], ["c_e"]]


def test_commentary_rules_are_in_the_write_prompt(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "commentary" in web.prompt(1) and "brief" in web.prompt(1)
    system = json.loads(web.chats[0].content)["messages"][0]["content"]
    assert "commentary" in system  # SKILL.md section 2


def test_the_process_page_leaves_out_the_read_and_skipped_steps():
    steps = [
        {"step": "read", "pages": []},
        {"step": "skipped", "skipped": []},
        {"step": "pick", "groups": []},
    ]
    assert [s["step"] for s in process.visible_steps(steps)] == ["pick"]


@pytest.mark.parametrize("reply", ["{}", '{"items": []}', '{"items": "没有修改"}'])
def test_a_fix_reply_without_items_keeps_the_draft(issue_dir, slept, monkeypatch, reply):
    web = FakeWeb([_picks(), _written(**FASTER), _reply(reply)])
    assert _edit(issue_dir, web, monkeypatch) == 0
    written = _result(issue_dir)
    assert len(written["items"]) == 3  # the draft, without the item it failed on
    assert [d["title"] for d in written["validation"]["dropped"]] == [_digest()["items"][1]["title"]]


def test_a_fix_reply_without_items_is_noted_in_the_trace(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _written(**FASTER), _reply("{}")])
    assert _edit(issue_dir, web, monkeypatch) == 0
    trace = _trace(issue_dir)
    assert trace["failure"] is None
    assert [s["step"] for s in trace["steps"]][-2:] == ["draft", "fix_ignored"]
    assert "items" in trace["steps"][-1]["error"]


def test_a_draft_without_items_fails_the_edit_when_the_fix_has_none_either(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _reply("{}"), _reply("{}")])
    assert _edit(issue_dir, web, monkeypatch) == 1
    failure = _trace(issue_dir)["failure"]
    assert failure["step"] == "fix" and "items must be a non-empty list" in failure["error"]


def test_a_draft_without_items_is_sent_back(issue_dir, slept, monkeypatch):
    web = FakeWeb([_picks(), _reply("{}"), _written()])
    assert _edit(issue_dir, web, monkeypatch) == 0
    assert "items must be a non-empty list" in web.prompt(2)
    assert len(_result(issue_dir)["items"]) == 4
