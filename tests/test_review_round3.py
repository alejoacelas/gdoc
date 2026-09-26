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
