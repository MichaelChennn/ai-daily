import json

import pytest

from daily import issue
from daily.issue import IssueDir

MODEL = "nvidia:minimaxai/minimax-m3.1-flash"


def test_an_issue_folder_names_its_files(tmp_path):
    folder = IssueDir.of(tmp_path, "2026-11-07")
    assert folder.date == "2026-11-07"
    names = [folder.candidates, folder.digest, folder.digest_en, folder.markdown, folder.rejected]
    assert [p.name for p in names] == [
        "candidates.json",
        "digest.json",
        "digest.en.json",
        "digest.md",
        "digest.rejected.json",
    ]
    assert folder.edition(en=True) == folder.digest_en
    assert folder.beta("api", MODEL).name == "digest.api.minimax.json"
    assert folder.beta_en(MODEL).name == "digest.en.minimax.json"
    assert folder.keyed("trace", "api.minimax") == folder.route_trace("api", MODEL)
    assert folder.route_trace("claude").name == "trace.claude.json"
    assert folder.trace({"channel": "fallback"}) is None
    with pytest.raises(ValueError):
        folder.route_trace("fallback")


def test_reading_and_writing(tmp_path):
    folder = IssueDir(tmp_path)
    assert folder.read_digest() is None and issue.try_read(folder.digest) is None
    issue.write(folder.digest, {"title": "日报"})
    assert folder.digest.read_text(encoding="utf-8") == '{\n  "title": "日报"\n}\n'
    assert folder.read_digest() == {"title": "日报"}
    folder.digest_en.write_text("[1]")
    assert issue.try_read(folder.digest_en) is None  # not an object
    folder.rejected.write_text("{not json")
    assert issue.try_read(folder.rejected) is None
    with pytest.raises(json.JSONDecodeError):
        issue.read(folder.rejected)
