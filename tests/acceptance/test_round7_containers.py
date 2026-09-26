"""R6-2..R6-5, R6-20b: container context and separator accounting.

Every block below sits in a list item or quote container that the parser
tracks as a path of quote markers and item indents. Each case is written
through CLI and MCP, must read back byte for byte, and must survive several
successive real wording changes with its native structure intact.
"""

import pytest

from gdoc.frontmatter import parse_frontmatter
from gdoc.mdparse import parse_markdown
from tests.acceptance.test_round5_workflows import MERGES, NativeRoute
from tests.native_model import NativeDoc


@pytest.fixture(params=["cli", "mcp"])
def route(request, monkeypatch, tmp_path):
    return NativeRoute(request.param, monkeypatch, tmp_path)


def _read(route):
    return parse_frontmatter(route.ok("cat"))[1]


def _shape(doc):
    """Named style, list shape (lists numbered by first appearance), container
    indent and gdoc range names: what a wording change must leave alone."""
    lists, paragraphs = {}, []
    for start, mark in doc.paragraphs():
        unit = doc.units[mark]
        bullet = unit.bullet and (lists.setdefault(unit.bullet["list"], len(lists)),
                                  unit.bullet["nest"])
        indent = unit.ps.get("indentStart", {}).get("magnitude", 0)
        paragraphs.append((unit.ps.get("namedStyleType"), bullet, indent))
    return paragraphs, sorted(name for name, *_ in doc.named if name)


def _check(route, merge, markdown, edits, tables=None):
    doc = route.load(NativeDoc(merge=merge))
    route.ok("cat")
    route.ok("write", text=markdown)
    assert _read(route) == markdown
    if tables is not None:
        assert len(parse_markdown(markdown).tables) == tables
    text = markdown
    for old, new in edits:
        changed = text.replace(old, new, 1)
        assert changed != text, (old, text)
        shape = _shape(doc)
        batches = len(route.service.batches)
        route.ok("write", text=changed)
        assert len(route.service.batches) > batches
        assert _read(route) == changed
        assert _shape(doc) == shape
        text = changed
    return doc


ADJACENT_IN_QUOTED_ITEM = (
    "- x\n\n  > - y\n  > \n  >   | a |\n  >   | --- |\n  >   | va |\n"
    "  > \n  > \n  >   | b |\n  >   | --- |\n  >   | vb |\n"
    "\n"  # a tab ending in a table keeps Docs' final paragraph
)


@MERGES
def test_adjacent_tables_in_a_quoted_list_inside_an_item(route, merge):
    """R6-2: the paragraph Docs keeps between the tables stays in their quote."""
    _check(route, merge, ADJACENT_IN_QUOTED_ITEM,
           [("x", "x2"), ("vb", "vb😀"), ("y", "y3")], tables=2)


@MERGES
@pytest.mark.parametrize("markdown", [
    "> - a\n> \n>   > q\n> \n>   | t |\n>   | --- |\n>   | vt |\n\n",
    "> - a\n> \n>   > q\n> \n>   ```\n>   code  x\n>   ```\n",
    "> - a\n> \n>   > q\n> - b\n",
    "- x\n\n  > - a\n  > \n  >   > deep\n  > - b\n- z\n",
])
def test_quote_inside_a_quoted_list_item(route, merge, markdown):
    """R6-3: a quote in a quoted item keeps the item's later content inside."""
    doc = _check(route, merge, markdown, [("a", "a1"), ("q" if "q" in markdown
                                                         else "deep", "Q2")])
    names = sorted(name for name, *_ in doc.named if name)
    assert any(name.startswith("gdoc:prefix:v3:") for name in names)


@MERGES
@pytest.mark.parametrize("markdown,tables", [
    ("- a\n\n  para\n\n  | t |\n  | --- |\n  | vt |\n- b\n", 1),
    ("1. a\n\n   para\n\n   > q\n2. b\n", 0),
    ("1. a\n\n   para\n\n   ```\n   code\n   ```\n2. b\n", 0),
    ("- a\n\n  first\n  second\n- b\n", 0),
    ("> - a\n> \n>   para\n> - b\n", 0),
    ("- a\n\n  ## Heading in item\n- b\n", 0),
])
def test_plain_paragraphs_inside_list_items(route, merge, markdown, tables):
    """R6-4: item paragraphs keep the item open for later blocks."""
    _check(route, merge, markdown, [("a", "a1"), ("b\n", "b2\n")], tables=tables)


@MERGES
@pytest.mark.parametrize("blanks", [0, 1, 2])
def test_blank_paragraphs_between_tables_in_an_item(route, merge, blanks):
    """R6-5: user blank paragraphs between item tables survive every write."""
    markdown = ("- a\n\n  | t |\n  | --- |\n  | vt |\n\n\n" + "\n" * blanks
                + "  | u |\n  | --- |\n  | vu |\n- b\n")
    # Two blank lines are the paragraph Docs keeps plus the separator; each
    # further blank line is a user paragraph, and the exact readback keeps it.
    _check(route, merge, markdown, [("vt", "vt2"), ("vu", "vu3"), ("a\n", "a4\n")],
           tables=2)


@MERGES
@pytest.mark.parametrize("markdown", [
    "1. a\n\n   ---\n\n2. b\n",
    "- a\n\n  ---\n- b\n",
    "> 1. a\n> \n>    ---\n> 2. b\n",
])
def test_rules_inside_list_items(route, merge, markdown):
    """R6-20b: a rule written inside an item stays inside it."""
    _check(route, merge, markdown, [("a", "a1"), ("b", "b2")])


@MERGES
@pytest.mark.parametrize("markdown", [
    "- a\n&#32; literal spaces\n",
    "1. a\n&#9;tabbed text\n2. b\n",
    "&#32; top level\n",
])
def test_literal_leading_whitespace_after_a_list_is_text(route, merge, markdown):
    """Raw indentation means item content; literal whitespace is an entity."""
    _check(route, merge, markdown, [("a\n", "a5\n")] if "a\n" in markdown
           else [("top", "top6")])
