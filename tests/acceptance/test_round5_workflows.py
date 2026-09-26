"""Round-5 task routes through the CLI and MCP over the native document model.

Each test reads the document through the interface, changes the Markdown and
writes it back, then checks the native paragraphs the request sequence
produced, not only the requests' shape.
"""

import contextlib
import io
import json

import pytest

from gdoc import cli, mcp
from gdoc.api import comment_transport, docs, drive
from tests.native_model import NativeDoc, NativeService, styles

TABLE = [["h"], ["v"]]


class NativeRoute:
    def __init__(self, interface, monkeypatch, tmp_path):
        self.interface, self.tmp_path = interface, tmp_path
        self.service = None
        monkeypatch.setattr(docs, "get_docs_service", lambda: self.service)
        monkeypatch.setattr(comment_transport, "execute_mutation_request",
                            lambda request, **_: request.execute())
        monkeypatch.setattr(drive, "get_file_version", lambda *a, **k: {
            "version": self.service.revision,
            "mimeType": "application/vnd.google-apps.document"})
        monkeypatch.setattr(drive, "get_file_info", lambda *a, **k: {
            "name": "Synthetic", "version": self.service.revision})
        monkeypatch.setattr("gdoc.api.comments.list_comments", lambda *a, **k: [])

    def load(self, doc):
        self.service = NativeService(doc)
        return doc

    def call(self, command, **arguments):
        arguments = {"doc": "synthetic", **arguments}
        if self.interface == "mcp":
            response = mcp.MCPServer().dispatch({
                "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": "gdoc_" + command, "arguments": arguments},
            })
            result = response.get("result", {})
            blocks = result.get("content", [])
            error = (json.dumps(response["error"]) if "error" in response
                     else "\n".join(b["text"] for b in blocks[1:]))
            code = int(bool("error" in response or result.get("isError")))
            return code, blocks[0]["text"] if blocks else "", error
        prepared = dict(arguments)
        argv = [command, prepared.pop("doc")]
        if command in ("write", "insert"):
            path = self.tmp_path / "input.md"
            path.write_text(prepared.pop("text"))
            argv.append(str(path))
        for key in ("old_text", "new_text"):
            if key in prepared:
                argv.append(prepared.pop(key))
        for key, value in prepared.items():
            flag = "--" + key.replace("_", "-")
            argv += [flag] if value is True else [flag, str(value)]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cli.run_argv(argv, check_updates=False)
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
        return code, out.getvalue(), err.getvalue()

    def ok(self, command, **arguments):
        code, output, error = self.call(command, **arguments)
        assert code == 0, output + error
        return output


@pytest.fixture(params=["cli", "mcp"])
def route(request, monkeypatch, tmp_path):
    return NativeRoute(request.param, monkeypatch, tmp_path)


# Which paragraph's style Docs keeps when a deletion removes a mark is not
# probed live, so every route here must hold under both plausible outcomes.
MERGES = pytest.mark.parametrize("merge", ["mark", "first"])


def _bullet(list_id=1, preset="BULLET_DISC_CIRCLE_SQUARE", nest=0):
    return {"preset": preset, "list": list_id, "nest": nest}


NUMBERED = "NUMBERED_DECIMAL_ALPHA_ROMAN"


@MERGES
@pytest.mark.parametrize("layout", [
    "heading-table", "item-table", "table-heading", "table-item",
    "heading-table-end", "empty-heading-table",
])
def test_rewrite_keeps_styles_at_table_boundaries(route, layout, merge, request):
    """F1: exporter-shaped tables directly beside styled paragraphs survive."""
    if layout == "table-item" and merge == "first":
        # The paragraph after the table keeps its restored style either way,
        # but a bullet cannot be re-added to its original list through the
        # API. Only first-paragraph inheritance would drop it; unprobed live.
        request.applymarker(pytest.mark.xfail(
            strict=True,
            reason="list identity after a table under first-paragraph merge"))
    bullet = _bullet()
    blocks = {
        "heading-table": [("p", "Heading", "HEADING_2"), ("t", TABLE),
                          ("p", "after")],
        "item-table": [("p", "item", "NORMAL_TEXT", bullet), ("t", TABLE),
                       ("p", "after")],
        "table-heading": [("p", "before"), ("t", TABLE),
                          ("p", "Following", "HEADING_2"), ("p", "after")],
        "table-item": [("p", "before"), ("t", TABLE),
                       ("p", "item", "NORMAL_TEXT", bullet), ("p", "after")],
        "heading-table-end": [("p", "after"), ("p", "Heading", "HEADING_2"),
                              ("t", TABLE)],
        "empty-heading-table": [("p", "after"), ("p", "", "HEADING_2"),
                                ("t", TABLE), ("p", "tail")],
    }[layout]
    doc = route.load(NativeDoc(*blocks, merge=merge))
    before = styles(doc)
    markdown = route.ok("cat")
    edited = markdown.replace("after", "after edited")
    assert edited != markdown
    route.ok("write", text=edited)
    expected = [(text.replace("after", "after edited"), style, bool(bullet))
                for text, style, bullet in before]
    assert [(t, s, bool(b)) for t, s, b in styles(doc)] == expected
    assert route.ok("cat") == edited


@MERGES
@pytest.mark.parametrize("last", ["heading", "item", "numbered"])
def test_appending_a_leading_table_keeps_the_last_paragraph(route, last, merge):
    """F2: the tab's last paragraph keeps its style when a table is appended."""
    final = {
        "heading": [("p", "Heading", "HEADING_2")],
        "item": [("p", "item", "NORMAL_TEXT", _bullet())],
        "numbered": [("p", "one", "NORMAL_TEXT", _bullet(1, NUMBERED)),
                     ("p", "two", "NORMAL_TEXT", _bullet(1, NUMBERED))],
    }[last]
    doc = route.load(NativeDoc(("p", "intro"), *final, merge=merge))
    before = styles(doc)
    route.ok("cat", tab="Main")
    route.ok("insert", text="| a |\n|---|\n| c |\n\nafter", tab="Main",
             position="end")
    after = styles(doc)
    assert after[:len(before)] == before
    assert after[-1] == ("after", "NORMAL_TEXT", None)


@MERGES
@pytest.mark.parametrize("markdown", [
    "## Heading\n| h |\n| --- |\n| v |\nafter\n",
    "```\ncode\n```\n| h |\n| --- |\n| v |\nafter\n",
    "> quoted\n| h |\n| --- |\n| v |\nafter\n",
    "- item\n| h |\n| --- |\n| v |\n- next\n",
    "before\n| h |\n| --- |\n| v |\n## Heading\n",
    "## Heading\n| h |\n| --- |\n| v |\n",
    "- item\n| h |\n| --- |\n| v |\n## Heading\n",
    # Adjacent tables read back with the blank paragraph Docs keeps between them.
    "**bold end**\n| h |\n| --- |\n| v |\n\n\n| k |\n| --- |\n| w |\n## After\n",
    "## Heading\n\n| h |\n| --- |\n| v |\n\nafter\n",
])
def test_written_table_layouts_read_back_unchanged(route, markdown, merge):
    """F1: a table directly beside a heading, code, quote or list reads back."""
    doc = route.load(NativeDoc(merge=merge))
    route.ok("cat")
    route.ok("write", text=markdown)
    # A tab ending in a table keeps Docs' final paragraph, read as a blank line.
    assert route.ok("cat").rstrip("\n") == markdown.rstrip("\n")
    # gdoc's code and container ranges end at their block, never over the table.
    table = next(i for i, u in enumerate(doc.units) if u.kind == "tstart")
    assert all(not start < table < end for name, start, end in doc.named if name)


@MERGES
@pytest.mark.parametrize("layout", ["final", "before-table", "heading-over-item"])
def test_removing_a_boundary_paragraph_keeps_the_one_before(route, layout, merge):
    """P-1: the paragraph whose mark is borrowed keeps its own style."""
    blocks, expected = {
        "final": ([("p", "Body"), ("p", "Obsolete", "HEADING_2")],
                  [("Body", "NORMAL_TEXT", None)]),
        "before-table": (
            [("p", "Intro"), ("p", "Obsolete", "HEADING_2"), ("t", TABLE),
             ("p", "after")],
            [("Intro", "NORMAL_TEXT", None), ("h", None, None), ("v", None, None),
             ("after", "NORMAL_TEXT", None)]),
        "heading-over-item": (
            [("p", "Title", "HEADING_1"), ("p", "Obsolete", "NORMAL_TEXT", _bullet())],
            [("Title", "HEADING_1", None)]),
    }[layout]
    doc = route.load(NativeDoc(*blocks, merge=merge))
    route.ok("cat")
    route.ok("edit", old_text="Obsolete", new_text="")
    assert styles(doc) == expected


def test_removing_a_paragraph_after_a_list_item_is_refused(route):
    """P-1: a list item's membership cannot be restored, so nothing is sent."""
    doc = route.load(NativeDoc(("p", "item", "NORMAL_TEXT", _bullet()),
                               ("p", "Obsolete", "HEADING_2")))
    before = styles(doc)
    route.ok("cat")
    code, output, error = route.call("edit", old_text="Obsolete", new_text="")
    assert code != 0 and "list item before it" in output + error
    assert route.service.batches == []
    assert styles(doc) == before
