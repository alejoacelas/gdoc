"""R7-5, R7-6, R7-12, R7-13: insert keeps the tab's boundary content.

Inserting Markdown at the start or end of a tab must produce the same native
document as writing the concatenated Markdown: the tab's last or only
paragraph keeps its quote, list, rule or code membership, appended content
does not inherit it, and an appended numbered list is its own list. Through
CLI and MCP under both merge models, checking native paragraph styles, list
identity and gdoc ranges, not only the Markdown readback.
"""

import pytest

from gdoc.frontmatter import parse_frontmatter
from tests.acceptance.test_round5_workflows import MERGES, NativeRoute
from tests.native_model import NativeDoc


@pytest.fixture(params=["cli", "mcp"])
def route(request, monkeypatch, tmp_path):
    return NativeRoute(request.param, monkeypatch, tmp_path)


TABLE = "| a |\n| --- |\n| b |\n"


def _read(route):
    return parse_frontmatter(route.ok("cat"))[1]


def _native(doc):
    """Paragraph texts with named style, list shape (lists numbered by first
    appearance), indent, rule border and the text each gdoc range holds."""
    lists, paragraphs = {}, []
    for start, mark in doc.paragraphs():
        unit = doc.units[mark]
        text = "".join(u.ch for u in doc.units[start:mark] if not u.cont)
        bullet = unit.bullet and (lists.setdefault(unit.bullet["list"], len(lists)),
                                  unit.bullet["nest"], unit.bullet["preset"])
        paragraphs.append((text, unit.ps.get("namedStyleType"), bullet,
                           unit.ps.get("indentStart", {}).get("magnitude", 0),
                           "borderBottom" in unit.ps))
    # A range ending at the tab's retained final mark may stop before that
    # mark and still hold the paragraph, so one final newline is not compared.
    ranges = sorted(
        (name, "".join(u.ch for u in doc.units[a:b] if u.kind == "text")
         .removesuffix("\n"))
        for name, a, b in doc.named if name)
    return paragraphs, ranges


def _written(route, merge, markdown):
    doc = route.load(NativeDoc(merge=merge))
    route.ok("cat")
    route.ok("write", text=markdown)
    return doc


CASES = [
    # R7-5: an appended table after a quote, rule or item content.
    ("> q\n", "text\n\n" + TABLE, "end"),
    ("p\n\n---\n", "text\n\n" + TABLE, "end"),
    ("- x\n\n  para\n", "text\n\n" + TABLE, "end"),
    ("> q\n", "x\n\n", "end"),
    ("---\n", "x\n\n", "end"),
    # R7-5: a table alone after a final code block.
    ("```\ncode\n```\n", TABLE, "end"),
    # R7-6: a final empty-mark paragraph keeps its container or code line.
    ("> ---\n", "x\n", "end"),
    ("1. a\n\n   ---\n", "x\n", "end"),
    ("```\na\n\n```\n", "x\n", "end"),
    ("```\n\n```\n", "x\n", "end"),
    ("> ---\n", TABLE, "end"),
    ("1. a\n\n   ---\n", TABLE, "end"),
    ("```\na\n\n```\n", TABLE, "end"),
    ("```\n\n```\n", TABLE, "end"),
    # R7-12: an appended numbered list is its own list.
    ("1. x\n2. y\n", "1. n1\n2. n2\n", "end"),
    ("> 1. g\n", "1. n1\n2. n2\n", "end"),
    # R7-13: a tab holding only an empty code line is not empty.
    ("```\n\n```\n", "x\n", "start"),
    ("> ---\n\nz\n", "x\n", "start"),
]


@MERGES
@pytest.mark.parametrize("base,inserted,position", CASES)
def test_insert_matches_writing_the_concatenation(
    route, merge, base, inserted, position,
):
    expected_doc = _written(route, merge, base)
    base_read = _read(route)
    concatenated = (base_read + inserted if position == "end"
                    else inserted + base_read)
    expected_doc = _written(route, merge, concatenated)
    expected = (_read(route), _native(expected_doc))

    doc = _written(route, merge, base)
    assert _read(route) == base_read
    batches = len(route.service.batches)
    route.ok("insert", text=inserted, tab="t.0", position=position)
    assert len(route.service.batches) > batches
    assert (_read(route), _native(doc)) == expected
