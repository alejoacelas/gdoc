"""R6-6 and R6-17: reads say what they leave out and which tabs exist.

A Markdown read of a tab with footnotes, chips or other richer content is
reported as incomplete, with the omitted content named, through CLI and MCP.
It still pins the revision it saw, so a rewrite needs explicit --allow-lossy
consent to discard that content and stays revision-protected.
"""

import contextlib
import io
import json

import pytest

from gdoc import cli
from gdoc.frontmatter import parse_frontmatter
from tests.acceptance.test_round5_workflows import NativeRoute
from tests.native_model import NativeDoc


@pytest.fixture(params=["cli", "mcp"])
def route(request, monkeypatch, tmp_path):
    return NativeRoute(request.param, monkeypatch, tmp_path)


def with_rich(service, where):
    """Add a footnote reference to the first paragraph, or a person chip to
    the first table cell."""
    snapshot = service.snapshot
    written = len(service.batches)

    def rich():
        value = snapshot()
        if len(service.batches) > written:
            return value  # a consented rewrite discarded the rich element
        content = value["tabs"][0]["documentTab"]["body"]["content"]
        if where == "cell":
            table = next(e["table"] for e in content if "table" in e)
            paragraph = table["tableRows"][0]["tableCells"][0]["content"][0]
            paragraph["paragraph"]["elements"].insert(0, {"person": {
                "personProperties": {"email": "a@example.org"}}})
        else:
            paragraph = next(e for e in content if "paragraph" in e)
            paragraph["paragraph"]["elements"].insert(0, {
                "footnoteReference": {"footnoteId": "f1"}})
        return value

    service.snapshot = rich


CASES = [("body", ("p", "See it."), "footnotes"),
         ("cell", ("t", [["h"], ["v"]]), "people chips")]


@pytest.mark.parametrize("where,block,label", CASES)
def test_cat_reports_omitted_rich_content(route, where, block, label):
    route.load(NativeDoc(block, ("p", "After.")))
    with_rich(route.service, where)
    scope = json.loads(route.ok("cat", json=True))["scope"]
    assert scope["complete"] is False
    assert scope["omitted"] == [label]
    code, output, notes = route.call("cat")
    assert code == 0 and f"leaves out native content: {label}" in notes


@pytest.mark.parametrize("where,block,label", CASES)
def test_omitting_read_needs_consent_and_keeps_revision_protection(
    route, where, block, label,
):
    route.load(NativeDoc(block, ("p", "After.")))
    with_rich(route.service, where)
    text = parse_frontmatter(route.ok("cat"))[1]
    changed = text.replace("After.", "After, changed.")
    code, output, error = route.call("write", text=changed)
    assert code == 1 or code == 3
    assert "--allow-lossy" in output + error and label in output + error
    batches = len(route.service.batches)
    route.ok("write", text=changed, allow_lossy=True)
    assert len(route.service.batches) > batches
    # A collaborator edit after the read still blocks, consent or not.
    route.ok("cat")
    route.service.doc.apply({"insertText": {"location": {"index": 1},
                                            "text": "X"}})
    route.service.revision += 1
    code, output, error = route.call(
        "write", text=changed.replace("changed", "again"), allow_lossy=True)
    assert code != 0 and "changed since last read" in output + error


def test_complete_read_has_no_omissions(route):
    route.load(NativeDoc(("p", "Plain."), ("t", [["h"], ["v"]])))
    scope = json.loads(route.ok("cat", json=True))["scope"]
    assert scope["complete"] is True and "omitted" not in scope


def test_json_scope_counts_all_tabs(route):
    """R6-17: JSON reads carry the tab count that the stderr note gives."""
    route.load(NativeDoc(("p", "Main text.")))
    route.service.extra_tabs = [{
        "tabProperties": {"tabId": "t.1", "title": "Notes", "index": 1},
        "documentTab": {"body": {"content": [
            {"startIndex": 0, "endIndex": 1, "sectionBreak": {}}]}}}]
    scope = json.loads(route.ok("cat", json=True))["scope"]
    assert scope["tab_ids"] == ["t.0"] and scope["tab_count"] == 2


def _run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.run_argv(list(argv), check_updates=False)
    return code, out.getvalue(), err.getvalue()


@pytest.mark.parametrize("where,block,label", CASES)
def test_pull_and_markdown_export_report_omissions(
    monkeypatch, tmp_path, where, block, label,
):
    route = NativeRoute("cli", monkeypatch, tmp_path)
    route.load(NativeDoc(block, ("p", "After.")))
    with_rich(route.service, where)
    path = tmp_path / "doc.md"
    code, out, err = _run("--json", "pull", "synthetic", str(path))
    assert code == 0 and label in err
    result = json.loads(out)
    assert result["complete"] is False and result["omitted"] == [label]
    code, out, err = _run("export", "synthetic", "--out", str(tmp_path / "x.md"))
    assert code == 0 and f"leaves out native content: {label}" in err
