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
