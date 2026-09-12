"""Offline paragraph-boundary regressions using synthetic Docs API bodies."""

from copy import deepcopy
from io import StringIO
from types import SimpleNamespace

import pytest

from gdoc.api.docs import (
    _build_cleanup_requests,
    find_text_in_document,
    insert_markdown_into_tab,
    replace_formatted,
)
from gdoc.cli import _resolve_replacement_text
from gdoc.mdparse import parse_inline, utf16_len
from gdoc.util import GdocError


def _body(*paragraphs):
    """Build native paragraph ranges with optional list membership."""
    content = []
    index = 1
    for text, style, bullet in paragraphs:
        end = index + utf16_len(text + "\n")
        paragraph = {
            "elements": [{"startIndex": index, "endIndex": end,
                          "textRun": {"content": text + "\n"}}],
            "paragraphStyle": {"namedStyleType": style, "alignment": "CENTER"},
        }
        if bullet:
            paragraph["bullet"] = {"listId": "synthetic-list", "nestingLevel": 2}
        content.append({"startIndex": index, "endIndex": end,
                        "paragraph": paragraph})
        index = end
    return {"content": content}


def _requests(mocker, body, old, new, **kwargs):
    """Run the real search and edit planner with only the service mocked."""
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    matches = find_text_in_document(None, old, body=body)
    assert matches
    result = replace_formatted("synthetic-doc", matches, new, "synthetic-rev",
                               tab_id="synthetic-tab", body=body, **kwargs)
    assert result == len(matches)
    chain = service.documents.return_value
    chain.get.assert_not_called()
    chain.batchUpdate.assert_called_once()
    batch = chain.batchUpdate.call_args.kwargs["body"]
    assert batch["writeControl"] == {"requiredRevisionId": "synthetic-rev"}
    return batch["requests"]


@pytest.mark.parametrize("source", ["positional", "old-stdin", "new-stdin", "files"])
@pytest.mark.parametrize("terminator", ["", "\n", "\n\n"])
def test_replacement_transport_strips_exactly_one_newline(
    mocker, tmp_path, source, terminator,
):
    """Edit and suggest share one resolver; transport cannot change its text."""
    old, new = "Original" + terminator, "Revised" + terminator
    args = SimpleNamespace(old_text=old, new_text=new)
    if source == "old-stdin":
        args.old_text = "-"
        mocker.patch("sys.stdin", StringIO(old))
    elif source == "new-stdin":
        args.new_text = "-"
        mocker.patch("sys.stdin", StringIO(new))
    elif source == "files":
        old_file, new_file = tmp_path / "old.md", tmp_path / "new.md"
        old_file.write_text(old)
        new_file.write_text(new)
        args.old_file, args.new_file = str(old_file), str(new_file)
    assert _resolve_replacement_text(args, None) == (
        old.removesuffix("\n"), new.removesuffix("\n"),
    )


@pytest.mark.parametrize("styles", [
    ("NORMAL_TEXT", "HEADING_2", "NORMAL_TEXT"),
    ("TITLE", "SUBTITLE", "HEADING_1"),
    ("NORMAL_TEXT", "NORMAL_TEXT", "NORMAL_TEXT"),
])
@pytest.mark.parametrize("in_cell", [False, True])
def test_multiline_wording_preserves_each_paragraph_mark(mocker, styles, in_cell):
    """Different named styles and nested list IDs survive without restyling."""
    body = _body(("Alpha", styles[0], False), ("Beta", styles[1], True),
                 ("Gamma", styles[2], False))
    if in_cell:
        body = {"content": [{"table": {"tableRows": [{"tableCells": [body]}]}}]}
    original = deepcopy(body)
    requests = _requests(mocker, body, "Alpha\nBeta\nGamma",
                         "😀Long alpha\nRevised beta\nShort")
    assert body == original
    assert [next(iter(req)) for req in requests] == [
        "deleteContentRange", "insertText",
        "deleteContentRange", "insertText",
        "deleteContentRange", "insertText",
    ]
    assert [req["deleteContentRange"]["range"] for req in requests[::2]] == [
        {"startIndex": 12, "endIndex": 17, "tabId": "synthetic-tab"},
        {"startIndex": 7, "endIndex": 11, "tabId": "synthetic-tab"},
        {"startIndex": 1, "endIndex": 6, "tabId": "synthetic-tab"},
    ]
    assert [req["insertText"]["text"] for req in requests[1::2]] == [
        "Short", "Revised beta", "😀Long alpha",
    ]


def test_partial_multiline_context_keeps_prefix_suffix_and_marks(mocker):
    """A context spanning partial endpoints never deletes either separator."""
    body = _body(("Prefix alpha", "TITLE", False),
                 ("beta suffix", "SUBTITLE", True))
    requests = _requests(mocker, body, "alpha\nbeta", "longer alpha\nshort")
    assert [req["deleteContentRange"]["range"] for req in requests[::2]] == [
        {"startIndex": 14, "endIndex": 18, "tabId": "synthetic-tab"},
        {"startIndex": 8, "endIndex": 13, "tabId": "synthetic-tab"},
    ]
    assert not any("updateParagraphStyle" in req for req in requests)


def test_extra_old_file_newline_does_not_consume_next_paragraph(mocker):
    """Even an explicitly matched terminal mark belongs to its paragraph."""
    body = _body(("Label", "HEADING_2", False), ("Neighbor", "NORMAL_TEXT", False))
    requests = _requests(mocker, body, "Label\n", "Renamed")
    assert requests == [
        {"deleteContentRange": {"range": {
            "startIndex": 1, "endIndex": 6, "tabId": "synthetic-tab",
        }}},
        {"insertText": {"location": {"index": 1, "tabId": "synthetic-tab"},
                        "text": "Renamed"}},
    ]


def test_multiline_explicit_heading_changes_only_that_paragraph(mocker):
    """Explicit heading Markdown clears that paragraph's old bullet only."""
    body = _body(("Alpha", "TITLE", False), ("Beta", "NORMAL_TEXT", True))
    requests = _requests(mocker, body, "Alpha\nBeta", "Revised\n## Heading")
    styles = [req["updateParagraphStyle"] for req in requests
              if "updateParagraphStyle" in req]
    assert len(styles) == 1
    assert styles[0]["paragraphStyle"]["namedStyleType"] == "HEADING_2"
    assert styles[0]["paragraphStyle"]["indentStart"]["magnitude"] == 0
    assert styles[0]["range"] == {
        "startIndex": 7, "endIndex": 14, "tabId": "synthetic-tab",
    }
    bullets = [req["deleteParagraphBullets"]["range"] for req in requests
               if "deleteParagraphBullets" in req]
    assert bullets == [styles[0]["range"]]


def test_multiline_count_mismatch_refuses_before_service_access(mocker):
    """Ambiguous paragraph removal cannot silently merge a heading or list."""
    body = _body(("Alpha", "TITLE", False), ("Beta", "SUBTITLE", True))
    service = mocker.patch("gdoc.api.docs.get_docs_service")
    matches = find_text_in_document(None, "Alpha\nBeta", body=body)
    with pytest.raises(GdocError, match="paragraph count mismatch") as exc:
        replace_formatted("synthetic-doc", matches, "Combined", "rev", body=body)
    assert exc.value.exit_code == 3
    service.assert_not_called()


@pytest.mark.parametrize("new", ["Plain", "## Heading", "", "- item"])
def test_explicit_cell_replacement_clears_previous_list(mocker, new):
    """Whole-cell intent removes inherited list membership before restyling."""
    body = _body(("Old", "NORMAL_TEXT", True))
    body = {"content": [{"table": {"tableRows": [{"tableCells": [body]}]}}]}
    requests = _requests(mocker, body, "Old", new, replace_paragraphs=True)
    resets = [req for req in requests if "deleteParagraphBullets" in req]
    assert len(resets) == 1
    if new == "- item":
        assert any("createParagraphBullets" in req for req in requests)
    else:
        assert not any("createParagraphBullets" in req for req in requests)
    assert all(req["deleteContentRange"]["range"]["endIndex"] == 4
               for req in requests if "deleteContentRange" in req)


@pytest.mark.parametrize("neighbor", ["normal", "list", "table", "image"])
@pytest.mark.parametrize("last", [False, True])
def test_empty_heading_does_not_mutate_neighbor(mocker, neighbor, last):
    """Heading deletion never promotes a neighbor or deletes the final mark."""
    body = _body(("Neighbor", "NORMAL_TEXT", neighbor == "list"),
                 ("Heading", "HEADING_2", False))
    if neighbor == "table":
        body["content"][0] = {"startIndex": 1, "endIndex": 10, "table": {}}
    elif neighbor == "image":
        body["content"][0]["paragraph"]["elements"].insert(0, {
            "startIndex": 1, "endIndex": 2,
            "inlineObjectElement": {"inlineObjectId": "synthetic-image"},
        })
    if not last:
        following = _body(("Following", "NORMAL_TEXT", False))["content"][0]
        following["startIndex"], following["endIndex"] = 18, 28
        following["paragraph"]["elements"][0].update(startIndex=18, endIndex=28)
        body["content"].append(following)
    requests = _requests(mocker, body, "Heading", "")
    assert requests == [{"deleteContentRange": {"range": {
        "startIndex": 10, "endIndex": 17, "tabId": "synthetic-tab",
    }}}]


@pytest.mark.parametrize("position", ["start", "end"])
@pytest.mark.parametrize("markdown", ["Inserted", "Inserted\n", "😀Inserted"])
@pytest.mark.parametrize("bullet", [False, True])
def test_insertion_styles_only_new_paragraphs(mocker, position, markdown, bullet):
    """Start/end insertion separates old headings and never styles their marks."""
    body = _body(("Existing", "HEADING_1", bullet))
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "synthetic-rev", "tabs": [{
            "documentTab": {"body": body},
            "tabProperties": {"tabId": "synthetic-tab", "title": "Notes"},
        }],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    insert_markdown_into_tab("synthetic-doc", "Notes", markdown, position=position)
    requests = service.documents.return_value.batchUpdate.call_args.kwargs[
        "body"]["requests"]
    inserts = [req["insertText"] for req in requests if "insertText" in req]
    text = markdown.removesuffix("\n")
    if position == "start":
        assert inserts == [{"location": {"index": 1, "tabId": "synthetic-tab"},
                            "text": text + "\n"}]
        lower, upper = 1, 1 + utf16_len(text + "\n")
    else:
        assert inserts == [
            {"location": {"index": 9, "tabId": "synthetic-tab"}, "text": "\n"},
            {"location": {"index": 10, "tabId": "synthetic-tab"}, "text": text},
        ]
        lower, upper = 10, 10 + utf16_len(text)
    for req in requests:
        if "insertText" in req:
            continue
        target = next(iter(req.values()))["range"]
        assert lower <= target["startIndex"] < target["endIndex"] <= upper


def test_cleanup_cannot_delete_image_only_paragraph():
    """An object plus newline is not an empty disposable paragraph."""
    body = _body(("", "HEADING_1", False), ("After", "NORMAL_TEXT", False))
    body["content"][0]["paragraph"]["elements"].insert(0, {
        "inlineObjectElement": {"inlineObjectId": "synthetic-image"},
    })
    assert _build_cleanup_requests(body, 1) == []


def test_code_span_closer_ignores_backslash_inside_span():
    """Escapes outside code must not hide a raw backtick closer inside code."""
    text, styles = parse_inline("`a\\`b`")
    assert text == "a\\b`"
    assert [(s.start, s.end, s.style) for s in styles] == [
        (0, 2, {"weightedFontFamily": {"fontFamily": "Courier New"}}),
    ]


@pytest.mark.parametrize("markdown,expected", [
    ("```unclosed", "```unclosed"),
    ("```code```", "code"),
    ("| H |\n|---|\n| x |", "| H |\n|---|\n| x |"),
])
def test_single_paragraph_never_uses_block_renderer(mocker, markdown, expected):
    """Whole-paragraph code spans and table source stay on the inline path."""
    body = _body(("Original", "HEADING_2", False))
    table = mocker.patch("gdoc.api.docs._insert_table")
    requests = _requests(mocker, body, "Original", markdown)
    assert requests[1]["insertText"]["text"] == expected
    assert not any("updateParagraphStyle" in req for req in requests)
    table.assert_not_called()


def test_multiple_multiline_matches_keep_reverse_order_and_occurrence_count(mocker):
    """--all counts original matches while each paragraph edit uses old indexes."""
    body = _body(("Alpha", "TITLE", False), ("Beta", "SUBTITLE", True),
                 ("Alpha", "HEADING_1", False), ("Beta", "HEADING_2", True))
    requests = _requests(mocker, body, "Alpha\nBeta", "Longer alpha\nShort")
    starts = [req["deleteContentRange"]["range"]["startIndex"] for req in requests
              if "deleteContentRange" in req]
    assert starts == [18, 12, 7, 1]
    assert not any("updateParagraphStyle" in req for req in requests)


def test_empty_multiline_replacement_keeps_each_mark(mocker):
    """Deleting wording from several paragraphs does not delete their marks."""
    body = _body(("Alpha", "TITLE", False), ("Beta", "HEADING_1", True))
    requests = _requests(mocker, body, "Alpha\nBeta", "")
    assert requests == [
        {"deleteContentRange": {"range": {
            "startIndex": 7, "endIndex": 11, "tabId": "synthetic-tab",
        }}},
        {"deleteContentRange": {"range": {
            "startIndex": 1, "endIndex": 6, "tabId": "synthetic-tab",
        }}},
    ]


def test_explicit_multiline_cell_can_remove_paragraphs(mocker):
    """An explicit whole-cell target can replace several list items with prose."""
    body = _body(("Alpha", "NORMAL_TEXT", True), ("Beta", "NORMAL_TEXT", True))
    body = {"content": [{"table": {"tableRows": [{"tableCells": [body]}]}}]}
    requests = _requests(mocker, body, "Alpha\nBeta", "Prose", replace_paragraphs=True)
    assert requests[0]["deleteContentRange"]["range"] == {
        "startIndex": 1, "endIndex": 11, "tabId": "synthetic-tab",
    }
    assert requests[2]["deleteParagraphBullets"]["range"] == {
        "startIndex": 1, "endIndex": 6, "tabId": "synthetic-tab",
    }
    style = requests[3]["updateParagraphStyle"]["paragraphStyle"]
    assert style["namedStyleType"] == "NORMAL_TEXT"
    assert style["indentStart"] == {"magnitude": 0, "unit": "PT"}


def test_cell_blockquote_keeps_explicit_indent(mocker):
    """Clearing inherited list indents must not overwrite blockquote intent."""
    body = _body(("Old", "NORMAL_TEXT", True))
    requests = _requests(mocker, body, "Old", "> Quote", replace_paragraphs=True)
    style = next(req["updateParagraphStyle"]["paragraphStyle"] for req in requests
                 if "updateParagraphStyle" in req)
    assert style["indentStart"] == {"magnitude": 36, "unit": "PT"}
