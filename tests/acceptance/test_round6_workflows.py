"""Round-6 task routes through the CLI and MCP over the native document model.

Each test drives the real handlers, rereads through the same interface and
checks the native paragraphs the requests produced.
"""

import pytest

from gdoc.frontmatter import parse_frontmatter
from tests.acceptance.test_round5_workflows import MERGES, NativeRoute
from tests.native_model import NativeDoc, styles


@pytest.fixture(params=["cli", "mcp"])
def route(request, monkeypatch, tmp_path):
    return NativeRoute(request.param, monkeypatch, tmp_path)


def _read(route):
    return parse_frontmatter(route.ok("cat"))[1]


def _written(route, markdown, merge="mark"):
    doc = route.load(NativeDoc(merge=merge))
    route.ok("cat")
    route.ok("write", text=markdown)
    return doc


FENCE = "before\n\n```\nfoo = 1\nbar = 2\n```\n\nafter\n"


@pytest.mark.parametrize("old,new", [
    ("foo = 1", "total = a*b + c*d"),
    ("1", "a*b*c"),
    ("foo = 1", "see [x](y)"),
    ("foo = 1", "**kw** = `y`"),
    ("foo = 1", "# not a heading"),
])
def test_code_line_replacement_is_literal(route, old, new):
    """R5-1: wording typed into a code line stays literal code."""
    _written(route, FENCE)
    route.ok("edit", old_text=old, new_text=new)
    assert _read(route) == FENCE.replace(old, new, 1)


@pytest.mark.parametrize("new,expected", [
    ("a*b*c", "Call `a*b*c` now\n"),
    ("`g_y`", "Call `g_y` now\n"),
    ("[x](y)", "Call `[x](y)` now\n"),
    ("`😀_y`", "Call `😀_y` now\n"),
    ("😀*y*", "Call `😀*y*` now\n"),
])
def test_inline_code_replacement_is_literal(route, new, expected):
    """R5-1: inside inline code, only a whole code span is Markdown."""
    _written(route, "Call `fn_x` now\n")
    route.ok("edit", old_text="fn_x", new_text=new)
    assert _read(route) == expected


def test_prose_replacement_is_still_markdown(route):
    """A match that covers prose keeps inline Markdown formatting."""
    _written(route, "Call `fn_x` now\n")
    route.ok("edit", old_text="now", new_text="*soon*")
    assert _read(route) == "Call `fn_x` *soon*\n"


@MERGES
@pytest.mark.parametrize("markdown", [
    "1. a\n\n   ```\n   \tx\n   ```\n2. b\n",
    "- a\n\n  ```\n  \tt\n  \t\tu\n  ```\n- b\n  - c\n",
    "1. a\n\n   ```\n   \tx\n   ```\n2. b\n  1. c\n\n"
    "      | h |\n      | --- |\n      | v |\n",
])
def test_list_contained_code_keeps_its_tabs(route, markdown, merge):
    """R5-3: bullet requests spanning code never consume its leading tabs."""
    _written(route, markdown, merge)
    first = _read(route)
    assert first.strip("\n") == markdown.strip("\n")
    route.ok("write", text=first.replace("a\n", "a2\n", 1))
    assert _read(route) == first.replace("a\n", "a2\n", 1)


def _model_after_delete(start, end):
    doc = NativeDoc(("p", "a", "HEADING_2"), ("p", ""), ("p", ""),
                    ("p", "b", "NORMAL_TEXT", {"preset": "NUMBERED", "list": 1,
                                               "nest": 0}), merge="first")
    doc.op_delete_content_range({"range": {"startIndex": start, "endIndex": end}})
    return styles(doc)


def test_first_merge_model_is_narrowed_only_to_the_observed_shape():
    """R5-10: only one whole empty paragraph per deletion keeps its successor."""
    # Units: 1 'a', 2 LF(H2), 3 LF, 4 LF, 5 'b', 6 LF(list).
    assert _model_after_delete(3, 4)[-1] == ("b", "NORMAL_TEXT", (1, 0))
    # Two empty paragraphs at once, or a deletion starting mid-paragraph,
    # still take the first paragraph's style under the adversarial model.
    assert _model_after_delete(3, 5)[-1] == ("b", "NORMAL_TEXT", None)
    assert _model_after_delete(2, 5)[-1] == ("ab", "HEADING_2", None)


@MERGES
@pytest.mark.parametrize("markdown", [
    "```\nx c\n```\n\n| h |\n| --- |\n| x v |\n- x item\n",
    "- x a\n\n  ```\n  x c\n  ```\n\n  | h |\n  | --- |\n  | x v |\n- x b\n",
    "> x q\n> \n> | h |\n> | --- |\n> | x v |\n- x item\n",
    "x p\n\n| h |\n| --- |\n| x v |\n1. x one\n2. x two\n",
])
def test_blank_line_between_a_container_and_a_table_stays_outside(
        route, markdown, merge):
    """R5-2: the blank paragraph before a table never joins a code range."""
    _written(route, markdown, merge)
    text = markdown
    for turn in ("y", "z"):
        assert _read(route) == text
        text = text.replace("x" if turn == "y" else "y", turn)
        route.ok("write", text=text)
    assert _read(route) == text


TABLE_MD = "| a |\n| --- |\n| b |\n"


@MERGES
@pytest.mark.parametrize("existing,inserted,expected", [
    ("## H\n", TABLE_MD, "## H\n" + TABLE_MD + "\n"),
    ("- item\n", TABLE_MD, "- item\n" + TABLE_MD + "\n"),
    ("> q\n", TABLE_MD, "> q\n" + TABLE_MD + "\n"),
    ("1. x\n", "para\n\n", "1. x\npara\n\n"),
    ("- b2\n", "# top\n\n", "- b2\n# top\n\n"),
    ("1. x\n", "- y\n\n", "1. x\n- y\n\n"),
    ("## H\n", TABLE_MD + "after\n", "## H\n" + TABLE_MD + "after\n"),
])
def test_appending_leaves_no_stray_styled_paragraph(route, existing, inserted,
                                                    expected, merge):
    """R5-8: the retained final mark takes the Markdown's style, not the old."""
    _written(route, existing, merge)
    route.ok("cat", tab="Main")
    route.ok("insert", text=inserted, tab="Main", position="end")
    assert _read(route) == expected


@MERGES
@pytest.mark.parametrize("markdown,old,expected", [
    ("first\n## H\nx\n", "first", "## H\nx\n"),
    ("x\n## H\n- a\n", "H", "x\n- a\n"),
    ("x\n## H\n1. a\n2. b\n", "H", "x\n1. a\n2. b\n"),
    ("- a\n- gone\n1. b\n", "gone", "- a\n1. b\n"),
])
def test_removing_a_middle_paragraph_keeps_its_successor(route, markdown, old,
                                                         expected, merge):
    """R5-10: a middle paragraph is emptied, then its empty paragraph removed."""
    _written(route, markdown, merge)
    route.ok("edit", old_text=old, new_text="")
    assert _read(route) == expected


@MERGES
@pytest.mark.parametrize("markdown,old,expected", [
    ("Hello\n## world\ntail\n", "lo\nwor", "Helld\ntail\n"),
    ("## Hello\nworld\ntail\n", "lo\nwor", "## Helld\ntail\n"),
    ("Hello\nmid\n## world\n", "lo\nmid\nwor", "Helld\n"),
    ("Hello\n- world\n", "Hello\nwor", "ld\n"),
    ("- a b\n- c d\n", "b\nc", "- a  d\n"),
])
def test_empty_replacement_across_paragraphs_joins_them(route, markdown, old,
                                                        expected, merge):
    """R5-6: the joined paragraph keeps the first paragraph's style."""
    _written(route, markdown, merge)
    route.ok("edit", old_text=old, new_text="")
    assert _read(route) == expected


def test_join_that_would_move_a_list_item_is_refused(route):
    """R5-6: the API cannot give the joined text the item's list back."""
    _written(route, "- a b\nc d\n")
    batches = len(route.service.batches)
    code, output, error = route.call("edit", old_text="b\nc", new_text="")
    assert code != 0 and "list item" in output + error
    assert len(route.service.batches) == batches
    assert _read(route) == "- a b\nc d\n"


def _run(text, start, **extra):
    end = start + len(text.encode("utf-16-le")) // 2
    return {"startIndex": start, "endIndex": end,
            "textRun": {"content": text, "textStyle": {}, **extra}}


def _suggested_tab():
    """'The cat ran' with 'cat' suggested for deletion and 'dog' inserted,
    a suggested paragraph break, and a wholly suggested paragraph."""
    runs = [_run("The ", 1), _run("cat", 5, suggestedDeletionIds=["s1"]),
            _run("dog", 8, suggestedInsertionIds=["s1"]), _run(" ran", 11),
            _run("\n", 15)]
    split = [_run("one", 16), _run("\n", 19, suggestedInsertionIds=["s2"])]
    joined = [_run("two\n", 20)]
    added = [_run("new\n", 24, suggestedInsertionIds=["s3"])]
    content = [{"startIndex": 1, "endIndex": 16, "paragraph": {"elements": runs}},
               {"startIndex": 16, "endIndex": 20, "paragraph": {"elements": split}},
               {"startIndex": 20, "endIndex": 24, "paragraph": {"elements": joined}},
               {"startIndex": 24, "endIndex": 28, "paragraph": {"elements": added},
                "suggestedInsertionIds": ["s3"]}]
    return {"documentId": "synthetic", "revisionId": "r1", "tabs": [{
        "tabProperties": {"tabId": "t.0", "title": "Main", "index": 0},
        "documentTab": {"body": {"content": [
            {"startIndex": 0, "endIndex": 1, "sectionBreak": {}}, *content]}},
    }]}


def test_reads_show_text_without_pending_suggestions(route, monkeypatch):
    """R5-5: suggested insertions never read as ordinary text."""
    from gdoc.api import docs

    route.load(NativeDoc())
    monkeypatch.setattr(docs, "get_document_with_tabs",
                        lambda *a, **k: _suggested_tab())
    code, output, error = route.call("cat")
    assert code == 0
    assert parse_frontmatter(output)[1] == "The cat ran\nonetwo\n"
    assert "3 pending suggestions" in output + error
    code, output, _ = route.call("cat", json=True)
    assert '"pending_suggestions": 3' in output
    assert "dog" not in output and "new" not in output


def test_unchanged_write_after_a_suggestion_read_sends_nothing(route, monkeypatch):
    """R5-5: writing the read back keeps the suggestions pending."""
    from gdoc.api import docs

    route.load(NativeDoc())
    monkeypatch.setattr(docs, "get_document_with_tabs",
                        lambda *a, **k: _suggested_tab())
    read = route.ok("cat")
    code, output, error = route.call("write", text=read)
    assert code == 0, output + error
    assert route.service.batches == []
    code, output, error = route.call("write", text=read.replace("ran", "sat"))
    assert code != 0 and "pending suggestions" in output + error
    assert route.service.batches == []


DOCS_LINK = {"link": {"url": "https://example.test/"}, "underline": True,
             "foregroundColor": {"color": {"rgbColor": {
                 "red": 0.06666667, "green": 0.33333334, "blue": 0.8}}}}


@pytest.mark.parametrize("old,new,expected", [
    ("here", "there", "click there now\n"),
    ("click here now", "click here here now", "click here here now\n"),
    ("k he", "k the", "click the[re](https://example.test/) now\n"),
    ("here", "[here](https://new.test/)", "click [here](https://new.test/) now\n"),
])
def test_unlinked_wording_loses_the_link_appearance(route, old, new, expected):
    """R5-7: wording that loses its link also loses Docs' link blue/underline."""
    doc = route.load(NativeDoc(("p", "click here now"), ("p", "x")))
    for unit in doc.units[7:11]:
        unit.ts.update(DOCS_LINK)
    route.ok("cat")
    route.ok("edit", old_text=old, new_text=new)
    assert _read(route) == expected + "x\n"
    plain = [u for u in doc.units if u.kind == "text" and "link" not in u.ts]
    assert not any(u.ts.get("underline") or "foregroundColor" in u.ts
                   for u in plain)


@MERGES
@pytest.mark.parametrize("markdown", [
    "1. item\n\n   > quoted\n2. next\n",
    "- item\n\n  > quoted\n- next\n",
    "- item\n  > quoted\n",
    "- a\n  - b\n\n    > deep\n",
    "1. a\n  1. b\n\n     > q\n2. c\n",
    "- a\n\n  > one\n  > \n  > two\n- b\n",
    "- a\n\n  > > deep\n- b\n",
    "1. a\n\n   > 1. x\n   > 2. y\n2. b\n",
    "- a\n\n  > 1. x\n  > 2. y\n- b\n",
    "1. a\n\n   > ```\n   > code\n   > ```\n2. b\n",
    "1. a\n\n   > | h |\n   > | --- |\n   > | v |\n2. b\n",
])
def test_quote_inside_a_list_item_stays_in_the_item(route, markdown, merge):
    """R5-4: a quote nested in a list item keeps the item's indent and list."""
    doc = _written(route, markdown, merge)
    assert _read(route) == markdown
    shape = _list_shape(doc)
    route.ok("write", text=markdown.replace("q", "Q"))
    assert _read(route) == markdown.replace("q", "Q")
    assert _list_shape(doc) == shape


def _list_shape(doc):
    """Each paragraph's list, numbered by first appearance, and nesting."""
    lists = {}
    return [bullet and (lists.setdefault(bullet[0], len(lists)), bullet[1])
            for _, _, bullet in styles(doc)]


def test_quote_in_item_numbering_is_one_list(route):
    """The item's list continues around the quote; the quoted list is its own."""
    doc = _written(route, "1. a\n\n   > 1. x\n   > 2. y\n2. b\n")
    lists = {text: bullet[0] for text, _, bullet in styles(doc) if bullet}
    assert lists["a"] == lists["b"] != lists["x"] == lists["y"]
