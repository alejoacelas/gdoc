"""Offline checks of the list compiler against the specified request semantics.

The small runner below implements only text edits and the preceding-list join /
leading-tab removal rules needed by these regressions, not a Docs emulator.
These checks do not establish backend fidelity.
"""

import pytest

from gdoc.api.docs import (
    _code_range_requests,
    _native_docs_requests,
    _strip_trailing_newline_unless_hr,
)
from gdoc.lossy import _numbered_list_hazards
from gdoc.mdparse import parse_markdown, to_docs_requests, utf16_len


def apply_list_requests(requests):
    paragraphs = []
    serial = 0

    def coordinates():
        start = 1
        for paragraph in paragraphs:
            end = start + utf16_len(paragraph['text'])
            yield start, end, paragraph
            start = end

    def position(text, units):
        for index in range(len(text) + 1):
            if utf16_len(text[:index]) == units:
                return index
        raise AssertionError('Invalid UTF-16 boundary')

    for request in requests:
        if 'insertText' in request:
            data = request['insertText']
            if not paragraphs:
                # The document contributes its retained terminal newline.
                paragraphs = [{'text': line, 'list': None, 'depth': 0}
                              for line in (data['text'] + '\n').splitlines(True)]
                continue
            index = data['location']['index']
            for start, end, paragraph in coordinates():
                if start <= index < end:
                    at = position(paragraph['text'], index - start)
                    paragraph['text'] = (paragraph['text'][:at] + data['text']
                                         + paragraph['text'][at:])
                    break
            else:
                raise AssertionError('Insert outside paragraphs')
        elif 'deleteContentRange' in request:
            target = request['deleteContentRange']['range']
            for start, end, paragraph in coordinates():
                if start <= target['startIndex'] < end:
                    a = position(paragraph['text'], target['startIndex'] - start)
                    b = position(paragraph['text'], target['endIndex'] - start)
                    paragraph['text'] = paragraph['text'][:a] + paragraph['text'][b:]
                    break
        elif 'createParagraphBullets' in request:
            data = request['createParagraphBullets']
            target = data['range']
            selected = [p for start, end, p in coordinates()
                        if end > target['startIndex'] and start < target['endIndex']]
            assert selected
            first = next(i for i, p in enumerate(paragraphs) if p is selected[0])
            prior = paragraphs[first - 1] if first else {}
            preset = data['bulletPreset']
            serial += 1
            identity = (prior['list'] if prior.get('preset') == preset
                        and prior.get('list') else serial)
            for paragraph in selected:
                text = paragraph['text']
                paragraph['depth'] = len(text) - len(text.lstrip('\t'))
                paragraph['text'] = text.lstrip('\t')
                paragraph['list'] = identity
                paragraph['preset'] = preset
        elif 'deleteParagraphBullets' in request:
            target = request['deleteParagraphBullets']['range']
            for start, end, paragraph in coordinates():
                if end > target['startIndex'] and start < target['endIndex']:
                    paragraph['list'] = None
    return paragraphs


def labels(paragraphs):
    counters = {}
    result = []
    for paragraph in paragraphs:
        if paragraph['list'] is not None:
            key = paragraph['list'], paragraph['depth']
            counters[key] = counters.get(key, 0) + 1
            result.append(counters[key])
    return result


@pytest.mark.parametrize('builder', [to_docs_requests, _native_docs_requests])
@pytest.mark.parametrize('gap', ['', '\n', '\n\n'])
def test_adjacent_and_separated_restarts_remain_independent(builder, gap):
    parsed = parse_markdown('1. A😀\n2. B\n' + gap + '1. C\n2. D')
    _strip_trailing_newline_unless_hr(parsed)
    paragraphs = apply_list_requests(builder(parsed, 1, 't'))
    assert labels(paragraphs) == [1, 2, 1, 2]
    assert not parsed.non_default_list_starts


@pytest.mark.parametrize('builder', [to_docs_requests, _native_docs_requests])
@pytest.mark.parametrize('gap', ['\n', '\n\n'])
def test_continuation_spans_then_unbullets_blank_paragraphs(builder, gap):
    parsed = parse_markdown('1. A\n2. B\n' + gap + '3. C\n4. D')
    _strip_trailing_newline_unless_hr(parsed)
    paragraphs = apply_list_requests(builder(parsed, 1, 't'))
    assert labels(paragraphs) == [1, 2, 3, 4]
    assert all(p['list'] is None for p in paragraphs if p['text'] == '\n')
    assert not parsed.non_default_list_starts


@pytest.mark.parametrize('builder', [to_docs_requests, _native_docs_requests])
@pytest.mark.parametrize('indent', ['', '  '])
@pytest.mark.parametrize('tabs', ['\t', '\t\t'])
def test_literal_tabs_survive_without_becoming_nesting(builder, indent, tabs):
    parsed = parse_markdown('- Parent😀\n' + indent + '- ' + tabs + '**Cargo**\n'
                            '\n1. Later\n2. Last')
    _strip_trailing_newline_unless_hr(parsed)
    paragraphs = apply_list_requests(builder(parsed, 1, 't'))
    assert ''.join(p['text'] for p in paragraphs) == (
        'Parent😀\n' + tabs + 'Cargo\n\nLater\nLast\n')
    assert paragraphs[1]['depth'] == bool(indent)
    assert parsed.removed_tabs == bool(indent)


def test_literal_tabs_keep_following_image_table_and_code_coordinates():
    parsed = parse_markdown('- Parent😀\n  - \tCargo\n\n'
                            '![](https://example.org/image.png)\n\n'
                            '```\ncode\n```\n\n| A |\n| --- |\n| B |')
    requests = _native_docs_requests(parsed, 1, 't')
    image_at = next(r['insertInlineImage']['location']['index'] for r in requests
                    if 'insertInlineImage' in r)
    image_phase = next(i for i, r in enumerate(requests) if 'insertInlineImage' in r)
    # Stop before the image placeholder is deleted.
    paragraphs = apply_list_requests(requests[:image_phase - 1])
    text = ''.join(p['text'] for p in paragraphs)
    assert image_at == 1 + utf16_len(text[:text.index(' \n')])
    table = parsed.tables[0]
    assert table.removed_tabs_before == 1
    table_at = text.index('code\n') + len('code\n\n')
    assert (1 + utf16_len(parsed.plain_text[:table.plain_text_offset])
            - table.removed_tabs_before) == 1 + utf16_len(text[:table_at])
    code = _code_range_requests(parsed, 1, 't')[0]['createNamedRange']['range']
    assert code['startIndex'] == 1 + utf16_len(text[:text.index('code')])
    assert code['endIndex'] == code['startIndex'] + len('code\n')


def test_only_blank_continuation_and_root_restarts_stop_warning():
    def paragraph(identity=None, text='item\n'):
        result = {'elements': [{'textRun': {'content': text}}]}
        if identity:
            result['bullet'] = {'listId': identity}
        return {'paragraph': result}

    lists = {key: {'listProperties': {'nestingLevels': [{'glyphType': 'DECIMAL'}]}}
             for key in ['a', 'b']}
    assert not _numbered_list_hazards([paragraph('a'), paragraph('b')], lists)
    assert not _numbered_list_hazards(
        [paragraph('a'), paragraph(text='\n'), paragraph('a')], lists)
    assert _numbered_list_hazards(
        [paragraph('a'), paragraph(text='Prose\n'), paragraph('a')], lists)
    assert _numbered_list_hazards(
        [paragraph('a'), paragraph('b'), paragraph('a')], lists)


@pytest.mark.parametrize('builder', [to_docs_requests, _native_docs_requests])
def test_final_empty_item_includes_retained_paragraph_mark(builder):
    parsed = parse_markdown('1. First\n2. ')
    _strip_trailing_newline_unless_hr(parsed)
    paragraphs = apply_list_requests(builder(parsed, 1, 't'))
    assert labels(paragraphs) == [1, 2]
    assert paragraphs[-1]['text'] == '\n'


def test_mixed_child_restores_literal_tab_after_both_bullet_operations():
    parsed = parse_markdown('1. Parent\n  - \tChild\n2. Sibling')
    _strip_trailing_newline_unless_hr(parsed)
    paragraphs = apply_list_requests(_native_docs_requests(parsed, 1, 't'))
    assert paragraphs[1]['text'] == '\tChild\n'
    assert paragraphs[1]['depth'] == 1
    assert paragraphs[0]['list'] == paragraphs[2]['list']
