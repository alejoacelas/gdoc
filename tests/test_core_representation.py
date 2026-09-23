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


def test_code_block_marker_preserves_blank_paragraphs_and_literal_syntax():
    code = '  *literal*\t \n\n``` inside\n'
    offset = 1
    paragraphs = []
    for line in code.splitlines(keepends=True):
        paragraphs.append({'startIndex': offset, 'endIndex': offset + len(line),
                           'paragraph': {'elements': [
                               {'textRun': {'content': line}},
                           ]}})
        offset += len(line)
    tab = {'body': {'content': paragraphs}, 'namedRanges': {
        'gdoc:code:v1': {'namedRanges': [{'name': 'gdoc:code:v1', 'ranges': [
            {'startIndex': 1, 'endIndex': offset},
        ]}]},
    }}
    rendered = get_tab_text(tab, markdown=True)
    assert rendered.startswith('````\n')
    parsed = parse_markdown(rendered)
    assert parsed.plain_text == code
    assert [(b.start, b.end) for b in parsed.code_blocks] == [(0, len(code))]


def test_empty_fenced_code_has_a_marked_native_paragraph():
    parsed = parse_markdown('```\n```\n')
    assert parsed.plain_text == '\n'
    assert [(block.start, block.end) for block in parsed.code_blocks] == [(0, 1)]


def test_heading_list_and_content_whitespace_survive():
    paragraph = {'bullet': {'listId': 'bullets'}, 'paragraphStyle': {
        'namedStyleType': 'HEADING_2',
    }, 'elements': [{'textRun': {'content': '  leading\t \n'}}]}
    rendered = get_tab_text({'body': {'content': [{'paragraph': paragraph}]}}, True)
    assert rendered == '- ##   leading\t \n'
    parsed = parse_markdown(rendered)
    assert parsed.plain_text == '  leading\t \n'
    assert parsed.styles[0].style == {'namedStyleType': 'HEADING_2'}


def test_table_alignment_and_quote_rule_recognition():
    parsed = parse_markdown('| A | B | C |\n| :--- | :---: | ---: |\n| x | y | z |\n')
    assert parsed.tables[0].alignments == ['START', 'CENTER', 'END']
    content = [
        {'paragraph': {'paragraphStyle': {
            'indentStart': {'magnitude': 36, 'unit': 'PT'},
            'indentFirstLine': {'magnitude': 36, 'unit': 'PT'},
        }, 'elements': [{'textRun': {'content': 'quotation\n'}}]}},
        {'paragraph': {'elements': [{'horizontalRule': {}},
                                    {'textRun': {'content': '\n'}}]}},
    ]
    assert get_tab_text({'body': {'content': content}}, True) == '> quotation\n---\n'


def test_image_offsets_after_nested_lists_and_surrounding_unicode():
    parsed = parse_markdown(
        '- root\n  - 😀 ![map](https://example.org/a_(b).png) done\n'
    )
    image = parsed.images[0]
    assert image.uri == 'https://example.org/a_(b).png'
    assert image.alt == 'map'
    assert image.removed_tabs_before == 1
    offset = image.plain_text_offset
    assert parsed.plain_text[offset - 2:offset] == '😀 '
    assert parsed.plain_text[image.plain_text_offset:] == '  done\n'


def test_existing_image_exports_snapshot_reference_and_alt_without_mutation():
    paragraph = {'elements': [
        {'textRun': {'content': 'Look '}},
        {'inlineObjectElement': {'inlineObjectId': 'synthetic-image'}},
        {'textRun': {'content': '\n'}},
    ]}
    tab = {'body': {'content': [{'paragraph': paragraph}]}, 'inlineObjects': {
        'synthetic-image': {'inlineObjectProperties': {'embeddedObject': {
            'description': 'A [map]', 'imageProperties': {
                'contentUri': 'https://example.org/temporary',
            },
        }}},
    }}
    rendered = get_tab_text(tab, True)
    assert 'temporary' not in rendered
    image = parse_markdown(rendered).images[0]
    assert (image.uri, image.alt) == ('gdoc-image:synthetic-image', 'A [map]')
    assert '_markdown_image_alt' not in paragraph['elements'][1]


def test_code_span_ending_backslash_does_not_hide_image():
    parsed = parse_markdown('`path\\` ![drawing](https://example.org/d.png)\n')
    assert parsed.plain_text == 'path\\  \n'
    assert parsed.images[0].alt == 'drawing'
