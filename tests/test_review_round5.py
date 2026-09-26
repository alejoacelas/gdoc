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


SECTIONED = [
    {"startIndex": 0, "endIndex": 1, "sectionBreak": {"sectionStyle": {}}},
    {"startIndex": 1, "endIndex": 6, "paragraph": {"elements": [
        {"startIndex": 1, "endIndex": 6, "textRun": {"content": "Page\n"}}]}},
    {"startIndex": 6, "endIndex": 7, "sectionBreak": {
        "sectionStyle": {"sectionType": "NEXT_PAGE"}}},
    {"startIndex": 7, "endIndex": 12, "paragraph": {"elements": [
        {"startIndex": 7, "endIndex": 12, "textRun": {"content": "Land\n"}}]}},
]


@pytest.mark.parametrize("consent", [False, True])
def test_section_breaks_flatten_only_with_consent(mocker, consent):
    """F9: the advertised --allow-lossy route rewrites the tab as one section."""
    from gdoc.api.docs import insert_markdown_into_tab
    from gdoc.util import GdocError

    doc = {"revisionId": "r1", "tabs": [{
        "tabProperties": {"tabId": "t1", "title": "Tab 1"},
        "documentTab": {"body": {"content": SECTIONED}}}]}
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    batch = service.documents.return_value.batchUpdate
    batch.return_value.execute.return_value = {
        "writeControl": {"requiredRevisionId": "r2"}}
    mocker.patch("gdoc.api.comment_transport.execute_mutation_request",
                 side_effect=lambda request, **_: request.execute())
    if not consent:
        with pytest.raises(GdocError, match="--allow-lossy") as error:
            insert_markdown_into_tab("d", "t1", "Page\n\nLand\n", replace=True,
                                     document=doc)
        assert error.value.exit_code == 3
        batch.assert_not_called()
        return
    insert_markdown_into_tab("d", "t1", "Page\n\nLand\n", replace=True,
                             allow_lossy=True, document=doc)
    requests = batch.call_args.kwargs["body"]["requests"]
    # One deletion spans the break and the newline before it (Docs deletes a
    # section break only together with that newline).
    assert requests[0] == {"deleteContentRange": {"range": {
        "startIndex": 1, "endIndex": 11, "tabId": "t1"}}}
    assert batch.call_args.kwargs["body"]["writeControl"] == {
        "requiredRevisionId": "r1"}


@pytest.mark.parametrize("text", ["--", "---", "- -", "-", "- - -"])
@pytest.mark.parametrize("nest", [0, 1])
def test_a_bullet_of_dashes_stays_a_list_item(text, nest):
    """F11: an item whose text is dashes never reads back as a rule."""
    paragraph = _paragraph((text + "\n", {}))
    paragraph["paragraph"]["bullet"] = {"listId": "L", "nestingLevel": nest}
    tab = _tab([paragraph])
    tab["lists"] = {"L": {"listProperties": {"nestingLevels": [
        {"glyphSymbol": "●"}] * 3}}}
    parsed = parse_markdown(get_tab_text(tab, markdown=True))
    assert parsed.plain_text.lstrip("\t") == text + "\n"
    assert [s.type for s in parsed.styles].count("bullets") == 1
    assert not any("borderBottom" in s.style for s in parsed.styles)
