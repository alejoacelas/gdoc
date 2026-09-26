"""Regressions for the round-2 review of the Markdown contract release."""

import pytest

from gdoc.api.docs import get_tab_text
from gdoc.mdparse import parse_inline, parse_markdown
from tests.test_markdown_roundtrip import _paragraph, _table


def _cells(table):
    return [[parse_inline(cell)[0] for cell in row] for row in table.rows]


@pytest.mark.parametrize("row", [["-", "-"], [":-", "-:"], ["--", ":--:"]])
def test_dash_only_data_row_stays_in_its_table(row):
    rows = [["Name", "Score"], ["Ann", "5"], row, ["Bo", "7"]]
    exported = get_tab_text({"body": {"content": [_table(rows)]}}, markdown=True)
    parsed = parse_markdown(exported)
    assert [_cells(t) for t in parsed.tables] == [rows]
    # Handwritten GFM with such a row is one table too.
    handwritten = parse_markdown(
        "| Name | Score |\n| --- | --- |\n| Ann | 5 |\n| "
        + " | ".join(row) + " |\n"
    )
    assert [_cells(t) for t in handwritten.tables] == [rows[:3]]


@pytest.mark.parametrize("between, blanks", [([], 0), ([None], 1), ([None, None], 2)])
def test_adjacent_tables_use_one_separating_blank_line(between, blanks):
    content = [_table([["A"], ["1"]])]
    content += [_paragraph([]) for _ in between]
    content += [_table([["B"], ["2"]])]
    exported = get_tab_text({"body": {"content": content}}, markdown=True)
    assert exported.count("|\n\n") == 1
    parsed = parse_markdown(exported)
    assert [_cells(t) for t in parsed.tables] == [[["A"], ["1"]], [["B"], ["2"]]]
    # Each table is one paragraph slot; the remaining lines are blank paragraphs.
    assert parsed.plain_text == "\n" * (2 + blanks)


def test_adjacent_quoted_tables_separate_inside_the_quote():
    parsed = parse_markdown("> | A |\n> | - |\n>\n> | B |\n> | - |\n")
    assert [t.prefix for t in parsed.tables] == [(1, 0), (1, 0)]
    assert parsed.plain_text == "\n\n"


@pytest.mark.parametrize("body", [
    "---\nStatus: draft\n---\nBody\n",
    "---\ngdoc: literal\ntitle: x\n---\n",
    "---\n---\nTwo rules\n",
    "---\n",
    "Intro\n---\n",
])
def test_protected_bodies_survive_metadata_parsing(body):
    from gdoc.frontmatter import add_frontmatter, parse_frontmatter, protect_body

    assert parse_frontmatter(protect_body(body)) == ({}, body)
    # A pull file's own metadata block is removed exactly once.
    pulled = add_frontmatter(body, {"gdoc": "DOC", "title": "T"})
    assert parse_frontmatter(pulled) == ({"gdoc": "DOC", "title": "T"}, body)


@pytest.mark.parametrize("markdown, expected", [
    ("- a\n\n  1. x\n\n  2. y", [1, 2]),
    ("- a\n  1. x\n\n  2. y\n\n  3. z", [1, 2, 3]),
    ("- a\n  1. x\n  2. y", [1, 2]),
    ("- a\n  1. x\n     - deep\n  2. y", [1, 2]),
    ("- a\n\n  1. x\n\n     - deep\n\n  2. y", [1, 2]),
    ("- a\n  1. x\n- b\n  1. y", [1, 1]),
    ("- a\n\n  1. x\n\n- b\n\n  1. y\n\n  2. z", [1, 1, 2]),
    ("* a\n\n  1. x\n\n     1. d1\n\n     2. d2\n\n  2. y", [1, 1, 2, 2]),
    ("1. a\n\n   - b\n\n     1. x\n\n     2. y", [1, 1, 2]),
])
def test_loose_numbered_lists_nested_in_mixed_lists_keep_numbering(markdown, expected):
    from gdoc.api.docs import _native_docs_requests, _strip_trailing_newline_unless_hr
    from gdoc.mdparse import to_docs_requests
    from tests.test_list_request_semantics import apply_list_requests

    for builder in (to_docs_requests, _native_docs_requests):
        parsed = parse_markdown(markdown)
        _strip_trailing_newline_unless_hr(parsed)
        counters, numbers = {}, []
        for paragraph in apply_list_requests(builder(parsed, 1, "t")):
            if paragraph["list"] is None:
                continue
            key = paragraph["list"], paragraph["depth"]
            counters[key] = counters.get(key, 0) + 1
            if paragraph["preset"].startswith("NUMBERED"):
                numbers.append(counters[key])
        assert numbers == expected, builder
        assert not parsed.non_default_list_starts


def _indented(text, named_style="NORMAL_TEXT"):
    element = _paragraph([(text, {})], named_style)
    element["paragraph"]["paragraphStyle"].update({
        "indentStart": {"magnitude": 36, "unit": "PT"},
        "indentFirstLine": {"magnitude": 36, "unit": "PT"},
    })
    return element


@pytest.mark.parametrize("text", ["- not a list", "1. not numbered", "# not heading",
                                  "> x", "| a | b |", "+ plus"])
def test_indented_literal_text_stays_literal_inside_its_quote(text):
    exported = get_tab_text({"body": {"content": [_indented(text)]}}, markdown=True)
    parsed = parse_markdown(exported)
    assert parsed.plain_text == text + "\n"
    assert not [s for s in parsed.styles if s.type == "bullets"]
    assert not parsed.tables
    assert [s.style for s in parsed.styles if s.type == "markdown_prefix"] == [
        {"quote": 1, "indent": 0}]
    assert all(s.style.get("namedStyleType", "NORMAL_TEXT") == "NORMAL_TEXT"
               for s in parsed.styles if s.type == "paragraph_style")


@pytest.mark.parametrize("style, expected", [
    ("HEADING_2", "> ## Section\n"),
    ("TITLE", "> <!-- gdoc:TITLE --> Section\n"),
])
def test_indented_heading_keeps_its_style_inside_its_quote(style, expected):
    exported = get_tab_text({"body": {"content": [_indented("Section", style)]}},
                            markdown=True)
    assert exported == expected
    parsed = parse_markdown(exported)
    assert parsed.plain_text == "Section\n"
    assert any(s.style.get("namedStyleType") == style for s in parsed.styles)


def test_numbered_item_containing_a_rule_stays_one_item():
    from gdoc.api.docs import _native_docs_requests, _strip_trailing_newline_unless_hr
    from tests.test_list_request_semantics import apply_list_requests, labels

    bullet = {"listId": "L", "nestingLevel": 0}
    first = _paragraph([("a", {})], bullet=bullet)
    first["paragraph"]["elements"][1:1] = [{"horizontalRule": {}},
                                           {"textRun": {"content": "b"}}]
    lists = {"L": {"listProperties": {"nestingLevels": [{"glyphType": "DECIMAL"}]}}}
    exported = get_tab_text({"body": {"content": [
        first, _paragraph([("c", {})], bullet=bullet)]}, "lists": lists},
        markdown=True)
    assert exported == "1. a\n---\nb\n2. c\n"
    parsed = parse_markdown(exported)
    _strip_trailing_newline_unless_hr(parsed)
    assert labels(apply_list_requests(_native_docs_requests(parsed, 1, "t"))) == [1, 2]
    assert not parsed.non_default_list_starts
