"""Regressions for the round-3 review of the Markdown contract release."""

import pytest

from gdoc.api.docs import get_tab_text
from gdoc.mdparse import parse_inline, parse_markdown
from tests.test_markdown_roundtrip import _paragraph

CODE = {"weightedFontFamily": {"fontFamily": "Courier New"}}


def _cell_table(runs_by_cell):
    return {"table": {"tableRows": [
        {"tableCells": [{"content": [_paragraph([("H", {})])]}
                        for _ in runs_by_cell]},
        {"tableCells": [{"content": [_paragraph(runs)]} for runs in runs_by_cell]},
    ]}}


@pytest.mark.parametrize("runs", [
    [("a\\|b", CODE)],
    [("a\\\\|b", CODE)],
    [("x", {}), ("|", CODE)],
    [("C:\\", CODE)],
    [("grep 'a|b' \\| wc", CODE), (" and a\\|b", {})],
])
def test_table_cell_code_with_backslash_pipes_round_trips(runs):
    exported = get_tab_text({"body": {"content": [
        _cell_table([runs, [("z", {})]])]}}, markdown=True)
    table = parse_markdown(exported).tables[0]
    assert len(table.rows[1]) == 2, exported
    text, styles = parse_inline(table.rows[1][0])
    assert text == "".join(t for t, _ in runs)
    code = [(s.start, s.end) for s in styles if "weightedFontFamily" in s.style]
    starts = [0]
    for t, _ in runs:
        starts.append(starts[-1] + len(t))
    assert code == [(starts[i], starts[i + 1]) for i, (_, style) in enumerate(runs)
                    if style]
    assert parse_inline(table.rows[1][1])[0] == "z"


def test_linked_image_in_a_table_cell_keeps_its_link():
    from gdoc.api.docs import _table_cell_requests

    table = parse_markdown(
        "| Pic |\n| --- |\n"
        "| [![](https://example.invalid/i.png)](https://example.invalid/t) |\n"
    ).tables[0]
    requests = _table_cell_requests([[5], [9]], table, "tab-one")
    image = next(i for i, r in enumerate(requests) if "insertInlineImage" in r)
    placed = requests[image]["insertInlineImage"]["location"]["index"]
    assert requests[image + 1] == {"updateTextStyle": {
        "range": {"startIndex": placed, "endIndex": placed + 1, "tabId": "tab-one"},
        "textStyle": {"link": {"url": "https://example.invalid/t"}},
        "fields": "link",
    }}


@pytest.mark.parametrize("markdown, depths", [
    ("- a\n  - b\n    - c\n", [0, 1, 2]),
    ("10. a\n  - b\n", [0, 1]),
    ("1. a\n   - b\n", [0, 1]),
])
def test_documented_list_nesting_spelling(markdown, depths):
    parsed = parse_markdown(markdown)
    assert [s.list_depth for s in parsed.styles if s.type == "bullets"] == depths


def test_documented_emphasis_and_line_break_spellings_round_trip():
    parsed = parse_markdown("**bold _italic_** a\x0bb\n")
    assert parsed.plain_text == "bold italic a\x0bb\n"
    styles = {(s.start, s.end): s.style for s in parsed.styles
              if s.type == "text_style"}
    assert styles == {(0, 11): {"bold": True}, (5, 11): {"italic": True}}
    exported = get_tab_text({"body": {"content": [_paragraph([
        ("bold ", {"bold": True}), ("italic", {"bold": True, "italic": True}),
        (" a\x0bb", {}),
    ])]}}, markdown=True)
    again = parse_markdown(exported)
    assert again.plain_text == parsed.plain_text
    # Export keeps the boundary space outside the delimiters.
    assert {(s.start, s.end) for s in again.styles if s.type == "text_style"} == {
        (0, 4), (5, 11)}


def test_paragraph_before_a_table_is_removed_with_the_preceding_mark(mocker):
    from gdoc.api.docs import find_text_in_document, replace_formatted
    from gdoc.util import GdocError
    from tests.test_paragraph_edits import _body, _requests

    body = _body(("Intro", "NORMAL_TEXT", False), ("Obsolete", "HEADING_2", False))
    body["content"].append({"startIndex": 16, "endIndex": 30, "table": {}})
    requests = _requests(mocker, body, "Obsolete", "")
    # Docs refuses to delete the mark before a table; the preceding one goes.
    assert requests == [{"deleteContentRange": {"range": {
        "startIndex": 6, "endIndex": 15, "tabId": "synthetic-tab"}}}]

    first = _body(("Obsolete", "HEADING_2", False))
    first["content"].append({"startIndex": 10, "endIndex": 20, "table": {}})
    service = mocker.patch("gdoc.api.docs.get_docs_service")
    with pytest.raises(GdocError, match="directly before a table") as error:
        replace_formatted("synthetic-doc",
                          find_text_in_document(None, "Obsolete", body=first), "",
                          "synthetic-rev", tab_id="synthetic-tab", body=first)
    assert error.value.exit_code == 3
    service.assert_not_called()
