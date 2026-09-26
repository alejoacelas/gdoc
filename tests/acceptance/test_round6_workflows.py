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
