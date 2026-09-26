"""Round-5 review regressions: export/parse round trips of supported Markdown."""

import pytest

from gdoc.api.docs import flatten_tabs, get_tab_text
from gdoc.mdparse import parse_markdown

CODE = {"weightedFontFamily": {"fontFamily": "Courier New"}}


def _tab(content, inline_objects=None):
    tab = {"tabProperties": {"tabId": "t.0", "title": "Main"},
           "documentTab": {"body": {"content": content},
                           "inlineObjects": inline_objects or {}}}
    return flatten_tabs([tab])[0]


def _paragraph(*elements, style=None):
    index, built = 1, []
    for element in elements:
        if isinstance(element, tuple):
            text, text_style = element
            built.append({"startIndex": index, "endIndex": index + len(text),
                          "textRun": {"content": text, "textStyle": text_style}})
            index += len(text)
        else:
            built.append({"startIndex": index, "endIndex": index + 1,
                          "inlineObjectElement": {"inlineObjectId": element}})
            index += 1
    return {"startIndex": 1, "endIndex": index, "paragraph": {
        "elements": built,
        "paragraphStyle": {"namedStyleType": style or "NORMAL_TEXT"}}}


@pytest.mark.parametrize("description", [
    "Press ` key", "Chart.\nSource: finance", "tick `a` and\x0bbreak", "a b",
])
def test_image_alt_text_cannot_hide_the_image(description):
    """F3: an image whose alt text has a backtick or line break stays an image."""
    objects = {"obj": {"inlineObjectProperties": {"embeddedObject": {
        "description": description,
        "imageProperties": {"contentUri": "https://example.test/i.png"}}}}}
    tab = _tab([_paragraph(("See ", {}), "obj", (" and ", {}), ("ls", CODE),
                           ("\n", {}))], objects)
    markdown = get_tab_text(tab, markdown=True)
    assert markdown.count("\n") == 1
    parsed = parse_markdown(markdown)
    assert [image.uri for image in parsed.images] == ["gdoc-image:obj"]
    assert parsed.images[0].alt == " ".join(description.split())
    assert parsed.plain_text == "See   and ls\n"
    code = [s for s in parsed.styles if s.type == "text_style"
            and "weightedFontFamily" in s.style]
    assert [(s.start, s.end) for s in code] == [(10, 12)]


def _table(*rows):
    """A native table whose cells each hold one paragraph of styled runs."""
    return {"startIndex": 1, "endIndex": 2, "table": {
        "rows": len(rows), "columns": len(rows[0]),
        "tableRows": [{"tableCells": [{"content": [_paragraph(*cell)]}
                                      for cell in row]} for row in rows]}}


@pytest.mark.parametrize("cell,text", [
    ((("Type ` then ", {}), ("a|b", CODE), ("\n", {})), "Type ` then a|b"),
    ((("a`b\x0bc`d", {}), ("\n", {})), "a`b\x0bc`d"),
])
def test_table_cell_backtick_stays_literal(cell, text):
    """F4: an escaped backtick in a cell never opens a code span.

    The cell must parse back to exactly its native text, so a write sends no
    extra backslash or literal ``<br>`` that the next read would grow.
    """
    from gdoc.mdparse import parse_inline

    tab = _tab([_table([(("H", {}), ("\n", {}))], [cell]), _paragraph(("\n", {}))])
    parsed = parse_markdown(get_tab_text(tab, markdown=True))
    (only,) = parsed.tables[0].rows[1]
    assert parse_inline(only)[0] == text
