import json

import httpx
import pytest

from daily import api_editor, cli
from tests.test_digest import CANDIDATES, DATE, _digest

CHAT = "integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia:deepseek-ai/deepseek-v4.1-flash"
PAGES = {
    "openai.com/index/gpt-6/": "<p>GPT-6 has a <b>1M token</b> context window.</p>",
    "github.com/vllm-project/vllm/releases/tag/v0.12.0": "ok",
    "huggingface.co/Qwen/Qwen3.5-72B": "ok",
    "huggingface.co/papers/2610.00001": "ok",
}


def _call(id_, name, **arguments):
    return {"id": id_, "type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}


def _reply(*calls, content=None):
    message = {"role": "assistant", "content": content}
    if calls:
        message["tool_calls"] = list(calls)
    return httpx.Response(200, json={"choices": [{"message": message}]})


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
            return self.replies.pop(0)
        if key in PAGES:
            return httpx.Response(200, html=PAGES[key])
        return httpx.Response(404)

    def messages(self, index):
        return json.loads(self.chats[index].content)["messages"]


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


def _edit(issue_dir, web, monkeypatch, *extra):
    monkeypatch.setattr(cli.pipeline, "make_client", web.client)
    return cli.main(["edit", "--date", DATE, "--data-dir", str(issue_dir.parent), "--model", MODEL, *extra])


def test_edit_runs_the_tools_and_writes_the_validated_digest(issue_dir, slept, monkeypatch, capsys):
    draft = _digest()
    draft["items"][1]["summary"] = "新版本速度提升 40%。"  # dropped by validate
    web = FakeWeb(
        [
            httpx.Response(429, json={"error": "rate limited"}),
            _reply(
                _call("a", "list_candidates", kind=["blog"]),
                _call("b", "fetch_page", url="https://openai.com/index/gpt-6/", grep=["1M token"]),
            ),
            _reply(_call("c", "submit_digest", digest={"highlights": draft["highlights"], "items": []})),
            _reply(
                _call(
                    "d", "submit_digest", digest={"highlights": draft["highlights"], "items": draft["items"]}
                )
            ),
        ]
    )
    assert _edit(issue_dir, web, monkeypatch) == 0

    path = issue_dir / "digest.api.deepseek.json"
    assert capsys.readouterr().out.strip() == str(path)
    written = json.loads(path.read_text())
    assert (written["channel"], written["model"], written["mode"], written["date"]) == (
        "api",
        MODEL,
        "full",
        DATE,
    )
    assert written["research"] == [{"via": "webfetch", "url": "https://openai.com/index/gpt-6/"}]
    assert len(written["items"]) == 3 and written["validation"]["checked_links"] is True

    assert len(web.chats) == 4  # the 429 was retried
    assert 15 in slept
    first = json.loads(web.chats[0].content)
    assert first["model"] == "deepseek-ai/deepseek-v4.1-flash"
    assert web.chats[0].headers["authorization"] == "Bearer nvapi-test"
    assert "宁缺毋滥" in first["messages"][0]["content"]  # the skill is the system prompt
    assert {t["function"]["name"] for t in first["tools"]} == {
        "list_candidates",
        "show_candidate",
        "fetch_page",
        "submit_digest",
    }

    results = {m["tool_call_id"]: m["content"] for m in web.messages(3) if m["role"] == "tool"}
    assert "c_gpt" in results["a"] and "c_vllm" not in results["a"]  # only the blog kind
    assert "GPT-6 has a 1M token context window." in results["b"]
    assert "items must be a non-empty list" in results["c"]


def test_edit_fails_without_a_submission(issue_dir, slept, monkeypatch):
    web = FakeWeb([_reply(content="我写好了。")] * 3)
    assert _edit(issue_dir, web, monkeypatch, "--max-turns", "3") == 1
    assert not (issue_dir / "digest.api.deepseek.json").exists()


def test_edit_needs_a_known_provider_and_its_key(issue_dir, monkeypatch):
    web = FakeWeb([])
    monkeypatch.setattr(cli.pipeline, "make_client", web.client)
    base = ["edit", "--date", DATE, "--data-dir", str(issue_dir.parent), "--model"]
    assert cli.main([*base, "acme:some-model"]) == 2
    monkeypatch.delenv("NVIDIA_API_KEY")
    assert cli.main([*base, MODEL]) == 2
    assert web.chats == []
