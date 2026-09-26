"""Round-3 review regressions through the real CLI and MCP task routes."""

import json

import pytest

from gdoc.mdparse import parse_markdown, utf16_len
from tests.acceptance.conftest import paragraph
from tests.acceptance.test_workflows import existing_image, read, requests


def _reply_with_image_ids(scenario):
    """Answer each batch as Docs does: one reply per request, new image IDs."""
    counter = iter(range(1, 1000))
    execute = scenario.service.documents.return_value.batchUpdate.return_value.execute
    batch = scenario.service.documents.return_value.batchUpdate

    def respond(*args, **kwargs):
        body = batch.call_args.kwargs["body"]
        return {
            "writeControl": {"requiredRevisionId": "r2"},
            "replies": [
                {"insertInlineImage": {"objectId": f"copy{next(counter)}"}}
                if "insertInlineImage" in request else {}
                for request in body["requests"]
            ],
        }

    execute.side_effect = respond


def _inserted_text(scenario):
    return "".join(r["insertText"]["text"] for r in requests(scenario)
                   if "insertText" in r)


def test_repeated_image_and_literal_token_survive_successive_writes(scenario):
    existing_image(scenario)
    source = read(scenario)
    assert "![Map](gdoc-image:map)" in source
    _reply_with_image_ids(scenario)
    literal = [
        "```\nsee ![](gdoc-image:map)\n```\n",
        "> ```\n> ![](gdoc-image:map)\n> ```\n",
        "1. Step\n\n   ```\n   ![](gdoc-image:map)\n   ```\n",
        "Inline `![](gdoc-image:map)` and \\![](gdoc-image:map) stay text.\n",
    ]
    revised = (source.replace("Before", "Revised")
               + "![Map](gdoc-image:map)\n\n" + "\n".join(literal))
    scenario.ok("write", tab="draft", text=revised)
    assert sum("insertInlineImage" in r for r in requests(scenario)) == 2

    # Google replaced the original object with the two copies.
    native = scenario.document["tabs"][0]["documentTab"]
    embedded = native["inlineObjects"].pop("map")
    native["inlineObjects"] = {"copy1": embedded, "copy2": embedded}
    for element in native["body"]["content"][1]["paragraph"]["elements"]:
        if "inlineObjectElement" in element:
            element["inlineObjectElement"]["inlineObjectId"] = "copy1"
    scenario.document["revisionId"] = "r2"
    scenario.service.documents.return_value.batchUpdate.reset_mock()

    # The agent keeps editing its own text, which still names the old object,
    # including a linked copy and a reference-style copy.
    again = (revised.replace("Revised", "Again")
             + "\n[![Map](gdoc-image:map)](https://example.invalid/site)\n"
             + "\n![Map][map]\n\n[map]: gdoc-image:map\n")
    scenario.ok("write", tab="draft", text=again)
    images = [r["insertInlineImage"] for r in requests(scenario)
              if "insertInlineImage" in r]
    assert len(images) == 4
    assert {image["uri"] for image in images} == {
        "https://example.invalid/temporary-map.png"}
    # Literal code and escaped syntax keep the token the agent wrote.
    inserted = _inserted_text(scenario)
    assert "see ![](gdoc-image:map)" in inserted
    assert inserted.count("![](gdoc-image:map)") == 4
    # Nothing but real image destinations resolves through the alias.
    assert "gdoc-image:copy" not in json.dumps(requests(scenario))


def test_quoted_soft_line_break_round_trips_through_cat(scenario):
    quoted = paragraph("line one\x0bline two\n")
    native = scenario.document["tabs"][0]["documentTab"]
    native["body"]["content"] = [quoted]
    native["namedRanges"] = {"gdoc:prefix:v1:1:0": {"namedRanges": [{
        "name": "gdoc:prefix:v1:1:0",
        "ranges": [{"startIndex": 1, "endIndex": quoted["endIndex"]}],
    }]}}
    source = read(scenario)
    assert source == "> line one\x0bline two\n"
    scenario.ok("write", tab="draft", text=source + "\nAdded\n")
    assert "> " not in _inserted_text(scenario)
    assert "line one\x0bline two" in _inserted_text(scenario)


def test_rename_image_references_changes_only_image_destinations():
    from gdoc.mdparse import parse_markdown, rename_image_references

    source = (
        "```\n![](gdoc-image:old)\n```\n"
        "![](gdoc-image:old) prose gdoc-image:old `![](gdoc-image:old)` "
        "\\![](gdoc-image:old)\n"
        "> ```\n> ![](gdoc-image:old)\n> ```\n"
        "| ![a](gdoc-image:old) | [x](gdoc-image:old) |\n"
        "[![i](gdoc-image:old)](https://example.invalid/a)\n"
    )
    renamed = rename_image_references(source, {"old": "new"})
    listed = "- ```\n  ![](gdoc-image:old)\n  ```\n"
    # gdoc reads a fence on a list marker line as item text, so this
    # destination is an image, as the writer also treats it.
    assert parse_markdown(listed).images[0].uri == "gdoc-image:old"
    assert "gdoc-image:new" in rename_image_references(listed, {"old": "new"})
    assert renamed == (
        "```\n![](gdoc-image:old)\n```\n"
        "![](gdoc-image:new) prose gdoc-image:old `![](gdoc-image:old)` "
        "\\![](gdoc-image:old)\n"
        "> ```\n> ![](gdoc-image:old)\n> ```\n"
        "| ![a](gdoc-image:new) | [x](gdoc-image:old) |\n"
        "[![i](gdoc-image:new)](https://example.invalid/a)\n"
    )
    assert json.dumps(renamed)  # stays plain text


@pytest.mark.parametrize("markdown", [
    "1. Step\n   - detail\n2. Next\n",
    "- a\n  1. b\n",
    "Plain 😀 text\n",
])
def test_insert_at_start_keeps_code_marker_on_its_paragraph(scenario, markdown):
    native = scenario.document["tabs"][0]["documentTab"]
    native["body"]["content"] = [paragraph("code\n"), paragraph("after\n", 6)]
    native["namedRanges"] = {"gdoc:code:v1": {"namedRanges": [{
        "namedRangeId": "code", "name": "gdoc:code:v1",
        "ranges": [{"startIndex": 1, "endIndex": 6, "tabId": "draft"}],
    }]}}
    read(scenario)
    scenario.ok("insert", tab="draft", text=markdown)
    parsed = parse_markdown(markdown)
    inserted = utf16_len(parsed.plain_text) - parsed.removed_tabs
    rebuilt = [r["createNamedRange"]["range"] for r in requests(scenario)
               if r.get("createNamedRange", {}).get("name") == "gdoc:code:v1"]
    assert rebuilt == [{"startIndex": 1 + inserted, "endIndex": 6 + inserted,
                        "tabId": "draft"}]


@pytest.fixture
def cli_scenario(request, monkeypatch, tmp_path):
    """File commands (pull, push, hooks) exist only in the CLI."""
    from tests.acceptance.conftest import Scenario

    return Scenario(monkeypatch, tmp_path, "cli", request.node.nodeid)


def _run(argv, stdin=None):
    import contextlib
    import io
    import sys

    from gdoc import cli

    out, err = io.StringIO(), io.StringIO()
    old = sys.stdin
    sys.stdin = io.StringIO(stdin or "")
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.run_argv(argv, check_updates=False)
    finally:
        sys.stdin = old
    return code, out.getvalue(), err.getvalue()


def _two_tab_files(scenario, tmp_path):
    from tests.acceptance.conftest import tab

    scenario.document["tabs"] = [
        tab("t1", "One", [paragraph("Alpha.\n")]),
        tab("t2", "Two", [paragraph("Beta.\n")]),
    ]
    files = tmp_path / "a.md", tmp_path / "b.md"
    for path, title in zip(files, ("One", "Two")):
        assert _run(["pull", "synthetic", str(path), "--tab", title])[0] == 0
    for path, old in zip(files, ("Alpha.", "Beta.")):
        path.write_text(path.read_text().replace(old, old[:-1] + " edited."))
    return files


def _push_first(scenario, path, via_hook):
    if via_hook:
        code, _, err = _run(["_sync-hook"], json.dumps(
            {"tool_input": {"file_path": str(path)}}))
        assert code == 0 and "SYNC: pushed" in err, err
    else:
        assert _run(["push", str(path)])[0] == 0
    # Google now serves the acknowledged revision; tab Two is untouched.
    scenario.document["revisionId"] = "r2"
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = [
        paragraph("Alpha edited.\n")]
    scenario.service.documents.return_value.batchUpdate.reset_mock()


@pytest.mark.parametrize("via_hook", [False, True])
def test_sibling_tab_file_stays_pushable_after_own_push(
    cli_scenario, tmp_path, via_hook,
):
    scenario = cli_scenario
    a, b = _two_tab_files(scenario, tmp_path)
    _push_first(scenario, a, via_hook)
    if via_hook:
        code, _, err = _run(["_sync-hook"], json.dumps(
            {"tool_input": {"file_path": str(b)}}))
        assert code == 0 and "SYNC: pushed" in err, err
    else:
        code, out, err = _run(["push", str(b)])
        assert code == 0, out + err
    assert scenario.batches[-1]["writeControl"] == {"requiredRevisionId": "r2"}
    assert "Beta edited." in _inserted_text(scenario)
    assert all(r.get("insertText", {}).get("location", {}).get("tabId", "t2") == "t2"
               for r in requests(scenario))
    assert "gdoc-revision: r2" in b.read_text()


def test_changed_target_tab_still_blocks_stale_file_after_fresh_read(
    cli_scenario, tmp_path,
):
    scenario = cli_scenario
    a, b = _two_tab_files(scenario, tmp_path)
    _push_first(scenario, a, via_hook=False)
    # Someone else edits tab Two; a fresh read of it must not bless b.md.
    scenario.document["revisionId"] = "r3"
    scenario.document["tabs"][1]["documentTab"]["body"]["content"] = [
        paragraph("Beta by a colleague.\n")]
    assert _run(["cat", "synthetic", "--tab", "Two"])[0] == 0
    code, _, err = _run(["push", str(b)])
    assert code == 3 and "stale" in err
    assert not scenario.batches


def test_markdown_export_selects_a_tab_and_other_formats_refuse_tab(
    cli_scenario, tmp_path,
):
    from tests.acceptance.conftest import tab

    scenario = cli_scenario
    scenario.document["tabs"] = [
        tab("t1", "One", [paragraph("Alpha.\n")]),
        tab("t2", "Two", [paragraph("Beta ✓.\n")]),
    ]
    code, out, err = _run(["export", "synthetic", "--format", "md"])
    assert (code, out) == (0, "Alpha.\n")
    assert "Use --tab to read others" in err
    code, out, err = _run(["export", "synthetic", "--format", "md", "--tab", "Two"])
    assert (code, out) == (0, "Beta ✓.\n"), err
    target = tmp_path / "two.md"
    code, out, _ = _run(["--json", "export", "synthetic", "--out", str(target),
                         "--tab", "t2"])
    assert code == 0 and json.loads(out)["tab_id"] == "t2"
    assert target.read_text() == "Beta ✓.\n"
    code, _, err = _run(["export", "synthetic", "--out", str(tmp_path / "x.pdf"),
                         "--tab", "Two"])
    assert code == 3 and "every tab" in err


def test_comment_annotation_is_scoped_to_the_selected_tab(scenario, monkeypatch):
    from tests.acceptance.conftest import tab

    scenario.document["tabs"] = [
        tab("t1", "One", [paragraph("First tab prose.\n")]),
        tab("t2", "Two", [paragraph("Second tab  prose here.\n")]),
    ]
    comments = [
        {"id": "c1", "content": "Is this right?", "author": {"displayName": "Ann"},
         "quotedFileContent": {"value": "Second tab  prose"}},
        {"id": "c2", "content": "Typo", "author": {"displayName": "Bo"},
         "quotedFileContent": {"value": "First tab"}},
        {"id": "c3", "content": "Gone", "author": {"displayName": "Cy"},
         "quotedFileContent": {"value": "removed sentence"}},
        {"id": "c4", "content": "Which?", "author": {"displayName": "Di"},
         "quotedFileContent": {"value": "prose"}},
    ]
    monkeypatch.setattr("gdoc.api.comments.list_comments", lambda *a, **kw: comments)
    first = scenario.ok("cat", comments=True)
    assert "[#c1 open] [anchor in another tab]" in first
    assert '[#c2 open] Bo on "First tab"' in first
    assert "[#c3 open] [anchor deleted]" in first
    assert "[#c4 open] [anchor ambiguous]" in first
    second = scenario.ok("cat", comments=True, tab="Two")
    assert '[#c1 open] Ann on "Second tab  prose"' in second
    assert "[#c2 open] [anchor in another tab]" in second


def test_file_diff_compares_the_same_tab_markdown_as_cat_and_pull(
    cli_scenario, tmp_path,
):
    from tests.acceptance.conftest import tab

    scenario = cli_scenario
    scenario.document["tabs"] = [
        tab("t1", "One", [paragraph("Alpha * one.\n"),
                          paragraph("- literal dash\n", 14)]),
        tab("t2", "Two", [paragraph("Beta ✓.\n")]),
    ]
    scenario.export = "Something Drive renders differently\n"
    catted = tmp_path / "cat.md"
    catted.write_text(_run(["cat", "synthetic"])[1])
    assert _run(["diff", "synthetic", str(catted)])[:2] == (0, "OK identical\n")
    pulled = tmp_path / "two.md"
    assert _run(["pull", "synthetic", str(pulled), "--tab", "Two"])[0] == 0
    # The pulled file's own tab and metadata are honored.
    assert _run(["diff", "synthetic", str(pulled)])[:2] == (0, "OK identical\n")
    pulled.write_text(pulled.read_text().replace("Beta", "Gamma"))
    code, out, _ = _run(["diff", "synthetic", str(pulled)])
    assert code == 1 and "-Beta ✓." in out and "+Gamma ✓." in out
    assert "gdoc:" not in out.split("\n", 2)[2]


def test_linked_image_keeps_its_link_through_read_and_rewrite(scenario):
    existing_image(scenario)
    image = scenario.document["tabs"][0]["documentTab"]["body"]["content"][1]
    image["paragraph"]["elements"][0]["inlineObjectElement"]["textStyle"] = {
        "link": {"url": "https://example.invalid/site_(a)"}}
    source = read(scenario)
    assert "[![Map](gdoc-image:map)](https://example.invalid/site_\\(a\\))" in source
    scenario.ok("write", tab="draft", text=source.replace("Before", "Revised"))
    sent = requests(scenario)
    for url in ("https://example.invalid/site_(a)",):
        link = next(i for i, r in enumerate(sent)
                    if r.get("updateTextStyle", {}).get("textStyle")
                    == {"link": {"url": url}}
                    and r["updateTextStyle"]["fields"] == "link"
                    and i > 0 and "insertInlineImage" in sent[i - 1])
        placed = sent[link - 1]["insertInlineImage"]["location"]["index"]
        assert sent[link]["updateTextStyle"]["range"]["startIndex"] == placed


def _cell_table_document(scenario):
    def cell(start, text):
        return {"startIndex": start - 1, "endIndex": start + len(text),
                "content": [paragraph(text, start)]}

    table = {"startIndex": 8, "endIndex": 18, "table": {
        "rows": 1, "columns": 2, "tableRows": [{
            "startIndex": 9, "endIndex": 18,
            "tableCells": [cell(10, "k\n"), cell(13, "old\n")]}]}}
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = [
        paragraph("Intro\n"), table, paragraph("\n", 18)]


@pytest.mark.parametrize("replacement", [
    "| a | b |\n| - | - |\n| 1 | 2 |\n",
    "Lead\n\n| a |\n| - |\n| 1 |\n",
])
def test_table_markdown_into_a_cell_is_refused_before_any_write(
    scenario, replacement,
):
    _cell_table_document(scenario)
    read(scenario)
    if scenario.interface == "cli":
        code, out, error = _run(["edit", "synthetic", "--tab", "draft", "--cell",
                                 "0,1", replacement])
    else:
        code, out, error = scenario.call("edit", old_text=replacement, cell="0,1",
                                         tab="draft")
    assert code != 0 and "nested tables are not supported" in out + error
    assert not scenario.batches
    # Ordinary cell text edits still work.
    if scenario.interface == "cli":
        code, out, error = _run(["edit", "synthetic", "--tab", "draft", "--cell", "0,1",
                                  "**new**"])
    else:
        code, out, error = scenario.call("edit", old_text="**new**", cell="0,1",
                                           tab="draft")
    assert code == 0, out + error
    assert "new" in _inserted_text(scenario)
