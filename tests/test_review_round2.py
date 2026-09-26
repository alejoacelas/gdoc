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
