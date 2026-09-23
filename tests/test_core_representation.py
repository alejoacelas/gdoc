"""Invented Markdown/native examples for the core representation contract."""

import time

import pytest

from gdoc.api.docs import _style_run_markdown, get_tab_text
from gdoc.mdparse import parse_inline, parse_markdown


def test_crlf_and_lone_cr_are_line_endings_in_code():
    assert parse_inline('`one\r\ntwo\rthree`')[0] == 'one two three'
    assert parse_markdown('```\r\n a\t \r\nb\r```\r\n').plain_text == ' a\t \nb\n'


def test_only_bare_long_enough_fence_closes_block():
    source = '```` python example\n```\n````not a closer\n x  \n`````\nnext\n'
    assert parse_markdown(source).plain_text == '```\n````not a closer\n x  \nnext\n'


def test_many_unfinished_links_are_bounded():
    source = '[word](' * 15000
    start = time.monotonic()
    assert parse_markdown(source).plain_text == source + '\n'
    assert time.monotonic() - start < 2


@pytest.mark.parametrize('text', ['a`b', '`', '  x  ', '\\*literal*', '   '])
def test_inline_code_export_preserves_literal_whitespace(text):
    style = {'weightedFontFamily': {'fontFamily': 'Courier New'}}
    rendered = _style_run_markdown(text, style)
    plain, styles = parse_inline(rendered)
    assert plain == text
    assert any(s.style == style and s.start == 0 and s.end == len(text)
               for s in styles)


def test_empty_mixed_list_items_survive_export():
    tab = {'body': {'content': [
        {'paragraph': {'bullet': {'listId': list_id, 'nestingLevel': level},
                       'elements': [{'textRun': {'content': '\n'}}]}}
        for list_id, level in [('bullet', 0), ('ordered', 1), ('bullet', 0)]
    ]}, 'lists': {'ordered': {'listProperties': {'nestingLevels': [
        {'glyphType': 'DECIMAL'}, {'glyphType': 'DECIMAL'},
    ]}}}}
    rendered = get_tab_text(tab, markdown=True)
    assert rendered == '- \n  1. \n- \n'
    parsed = parse_markdown(rendered)
    assert parsed.plain_text == '\n\t\n\n'
    assert len([s for s in parsed.styles if s.type == 'bullets']) == 3


def test_literal_image_opener_is_escaped_on_export():
    rendered = _style_run_markdown('![example](https://example.org/x)', {})
    assert parse_markdown(rendered).plain_text == '![example](https://example.org/x)\n'
