"""Tests for get_document, find_text_in_document, replace_formatted."""

from unittest.mock import MagicMock, patch

import pytest

from gdoc.api.docs import (
    find_text_in_document,
    get_document,
    replace_formatted,
)
from gdoc.util import AuthError, GdocError


def _mock_document(text_runs, revision_id="rev123"):
    """Build a minimal document dict for testing.

    text_runs is a list of (startIndex, content) tuples.
    """
    elements = []
    for start, content in text_runs:
        elements.append({
            "startIndex": start,
            "endIndex": start + len(content),
            "textRun": {"content": content},
        })
    return {
        "revisionId": revision_id,
        "body": {
            "content": [
                {"paragraph": {"elements": elements}},
            ]
        },
    }


def _mock_document_multi_para(paragraphs, revision_id="rev123"):
    """Build a document with multiple paragraphs.

    paragraphs: list of lists of (startIndex, content) tuples.
    """
    content = []
    for para_runs in paragraphs:
        elements = []
        for start, text in para_runs:
            elements.append({
                "startIndex": start,
                "endIndex": start + len(text),
                "textRun": {"content": text},
            })
        content.append({"paragraph": {"elements": elements}})
    return {
        "revisionId": revision_id,
        "body": {"content": content},
    }


def _docs_chain(mock_svc):
    """Shorthand for the mock service call chain."""
    return mock_svc.return_value.documents.return_value


class TestGetDocument:
    @patch("gdoc.api.docs.get_docs_service")
    def test_returns_document(self, mock_svc):
        doc = {"revisionId": "abc", "body": {"content": []}}
        chain = _docs_chain(mock_svc)
        chain.get.return_value.execute.return_value = doc
        result = get_document("doc123")
        assert result == doc
        chain.get.assert_called_once_with(documentId="doc123")

    @patch("gdoc.api.docs.get_docs_service")
    def test_translates_404(self, mock_svc):
        from googleapiclient.errors import HttpError
        resp = MagicMock(status=404)
        chain = _docs_chain(mock_svc)
        chain.get.return_value.execute.side_effect = (
            HttpError(resp, b"not found")
        )
        with pytest.raises(GdocError, match="Document not found"):
            get_document("doc123")

    @patch("gdoc.api.docs.get_docs_service")
    def test_translates_401(self, mock_svc):
        from googleapiclient.errors import HttpError
        resp = MagicMock(status=401)
        chain = _docs_chain(mock_svc)
        chain.get.return_value.execute.side_effect = (
            HttpError(resp, b"unauthorized")
        )
        with pytest.raises(AuthError, match="Authentication expired"):
            get_document("doc123")


class TestFindTextInDocument:
    def test_single_match(self):
        doc = _mock_document([(1, "hello world\n")])
        matches = find_text_in_document(doc, "hello")
        assert len(matches) == 1
        assert matches[0] == {"startIndex": 1, "endIndex": 6}

    def test_multiple_matches(self):
        doc = _mock_document([(1, "hello and hello\n")])
        matches = find_text_in_document(doc, "hello")
        assert len(matches) == 2
        assert matches[0]["startIndex"] == 1
        assert matches[1]["startIndex"] == 11

    def test_no_match(self):
        doc = _mock_document([(1, "hello world\n")])
        matches = find_text_in_document(doc, "zzz")
        assert matches == []

    def test_case_insensitive(self):
        doc = _mock_document([(1, "Hello World\n")])
        result = find_text_in_document(doc, "hello", match_case=False)
        assert len(result) == 1

    def test_case_sensitive_no_match(self):
        doc = _mock_document([(1, "Hello World\n")])
        result = find_text_in_document(doc, "hello", match_case=True)
        assert result == []

    def test_case_sensitive_match(self):
        doc = _mock_document([(1, "Hello World\n")])
        result = find_text_in_document(doc, "Hello", match_case=True)
        assert len(result) == 1

    def test_cross_textrun_match(self):
        """Text spans two textRun elements."""
        doc = _mock_document([(1, "hel"), (4, "lo world\n")])
        matches = find_text_in_document(doc, "hello")
        assert len(matches) == 1
        assert matches[0] == {"startIndex": 1, "endIndex": 6}

    def test_empty_document(self):
        doc = {"body": {"content": []}}
        assert find_text_in_document(doc, "anything") == []

    def test_multi_paragraph(self):
        doc = _mock_document_multi_para([
            [(1, "first paragraph\n")],
            [(18, "second paragraph\n")],
        ])
        matches = find_text_in_document(doc, "paragraph")
        assert len(matches) == 2


class TestReplaceFormatted:
    @patch("gdoc.api.docs.get_docs_service")
    def test_single_plain_replacement(self, mock_svc):
        chain = _docs_chain(mock_svc)
        chain.batchUpdate.return_value.execute = MagicMock()
        matches = [{"startIndex": 5, "endIndex": 10}]
        result = replace_formatted("d1", matches, "hello", "r1")
        assert result == 1
        call_args = chain.batchUpdate.call_args
        body = call_args[1]["body"]
        assert body["writeControl"]["requiredRevisionId"] == "r1"
        assert "deleteContentRange" in body["requests"][0]
        assert "insertText" in body["requests"][1]

    @patch("gdoc.api.docs.get_docs_service")
    def test_multi_match_order(self, mock_svc):
        """Matches processed last-to-first."""
        chain = _docs_chain(mock_svc)
        chain.batchUpdate.return_value.execute = MagicMock()
        matches = [
            {"startIndex": 5, "endIndex": 10},
            {"startIndex": 20, "endIndex": 25},
        ]
        result = replace_formatted("d1", matches, "x", "r1")
        assert result == 2
        body = chain.batchUpdate.call_args[1]["body"]
        first_del = body["requests"][0]
        assert first_del["deleteContentRange"]["range"]["startIndex"] == 20

    @patch("gdoc.api.docs.get_docs_service")
    def test_overlapping_matches_are_rejected(self, mock_svc):
        """`aa` in `aaa` matches [1,3) and [2,4): the last-to-first plan
        would land on shifted text, so refuse — same guard as suggest."""
        chain = _docs_chain(mock_svc)
        matches = [
            {"startIndex": 1, "endIndex": 3},
            {"startIndex": 2, "endIndex": 4},
        ]
        with pytest.raises(GdocError, match="overlap each other") as exc:
            replace_formatted("d1", matches, "b", "r1")
        assert exc.value.exit_code == 3
        chain.batchUpdate.assert_not_called()

    @patch("gdoc.api.docs.get_docs_service")
    def test_formatted_replacement(self, mock_svc):
        """Markdown generates style requests."""
        chain = _docs_chain(mock_svc)
        chain.batchUpdate.return_value.execute = MagicMock()
        matches = [{"startIndex": 5, "endIndex": 10}]
        result = replace_formatted("d1", matches, "**bold**", "r1")
        assert result == 1
        body = chain.batchUpdate.call_args[1]["body"]
        req_types = [list(r.keys())[0] for r in body["requests"]]
        assert "deleteContentRange" in req_types
        assert "insertText" in req_types
        assert "updateTextStyle" in req_types

    @patch("gdoc.api.docs.get_docs_service")
    def test_empty_matches_returns_zero(self, mock_svc):
        result = replace_formatted("d1", [], "text", "r1")
        assert result == 0
        chain = _docs_chain(mock_svc)
        chain.batchUpdate.assert_not_called()

    @patch("gdoc.api.docs.get_docs_service")
    def test_translates_http_error(self, mock_svc):
        from googleapiclient.errors import HttpError
        resp = MagicMock(status=403)
        chain = _docs_chain(mock_svc)
        chain.batchUpdate.return_value.execute.side_effect = (
            HttpError(resp, b"forbidden")
        )
        matches = [{"startIndex": 5, "endIndex": 10}]
        with pytest.raises(GdocError, match="Permission denied"):
            replace_formatted("d1", matches, "text", "r1")


def _segment_scope():
    return {
        "tabProperties": {"tabId": "tab-one", "title": "First"},
        "documentTab": {
            "body": _mock_document([(1, "Body TOKEN\n")])["body"],
            "headers": {"header-one": {
                "headerId": "header-one",
                **_mock_document([(0, "Header TOKEN\n")])["body"],
            }},
            "footers": {"footer-one": {
                "footerId": "footer-one",
                **_mock_document([(0, "Footer TOKEN\n")])["body"],
            }},
            "footnotes": {"note-one": {
                "footnoteId": "note-one",
                **_mock_document([(0, "Footnote TOKEN\n")])["body"],
            }},
        },
    }


def test_find_all_selected_tab_containers():
    from gdoc.api.docs import flatten_tabs

    raw = _segment_scope()
    tab = flatten_tabs([raw])[0]
    for kind in ("headers", "footers", "footnotes"):
        assert tab[kind] == raw["documentTab"][kind]
    assert find_text_in_document(tab, "TOKEN") == [
        {"startIndex": 6, "endIndex": 11, "tabId": "tab-one",
         "container": "body"},
        {"startIndex": 7, "endIndex": 12, "tabId": "tab-one",
         "container": "header", "segmentId": "header-one"},
        {"startIndex": 7, "endIndex": 12, "tabId": "tab-one",
         "container": "footer", "segmentId": "footer-one"},
        {"startIndex": 9, "endIndex": 14, "tabId": "tab-one",
         "container": "footnote", "segmentId": "note-one"},
    ]


def test_find_raw_document_uses_only_first_tab():
    first = _segment_scope()
    sibling = _segment_scope()
    sibling["tabProperties"]["tabId"] = "tab-two"
    expected = find_text_in_document(
        {"id": "tab-one", **first["documentTab"]}, "TOKEN",
    )
    assert len(expected) == 4
    assert find_text_in_document({"tabs": [first, sibling]}, "TOKEN") == expected


def test_legacy_body_range_shape_is_unchanged():
    assert find_text_in_document(_mock_document([(1, "TOKEN")]), "TOKEN") == [
        {"startIndex": 1, "endIndex": 6},
    ]


def _mixed_matches():
    # Identical numerical ranges are independent across containers.
    return [
        {"startIndex": 1, "endIndex": 6, "tabId": "tab-one",
         "container": "footnote", "segmentId": "note-one"},
        {"startIndex": 1, "endIndex": 6, "tabId": "tab-one",
         "container": "header", "segmentId": "header-one"},
        {"startIndex": 1, "endIndex": 6, "tabId": "tab-one",
         "container": "body"},
    ]


def _expected_mixed_requests(body_paragraph=False):
    requests = []
    for segment in (None, "header-one", "note-one"):
        coordinates = {"tabId": "tab-one"}
        if segment:
            coordinates["segmentId"] = segment
        requests.extend([
            {"deleteContentRange": {"range": {
                "startIndex": 1, "endIndex": 6, **coordinates,
            }}},
            {"insertText": {"location": {"index": 1, **coordinates},
                            "text": "REPLACED"}},
        ])
        if body_paragraph and segment is None:
            requests.append({"updateParagraphStyle": {
                "range": {"startIndex": 1, "endIndex": 9, **coordinates},
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType",
            }})
        requests.extend([
            {"updateTextStyle": {
                "range": {"startIndex": 1, "endIndex": 9, **coordinates},
                "textStyle": {"bold": True}, "fields": "bold",
            }},
            {"updateTextStyle": {
                "range": {"startIndex": 1, "endIndex": 9, **coordinates},
                "textStyle": {"italic": True}, "fields": "italic",
            }},
        ])
    return requests


def test_segment_replacement_builder_exact_requests():
    from gdoc.api.docs import _build_replacement_requests
    from gdoc.mdparse import ParsedMarkdown, StyleRange

    parsed = ParsedMarkdown("REPLACED", styles=[
        StyleRange(0, 8, {"bold": True}, "text_style"),
        StyleRange(0, 8, {"italic": True}, "text_style"),
    ])
    ordered, requests = _build_replacement_requests(parsed, _mixed_matches())
    assert [m["container"] for m in ordered] == ["body", "header", "footnote"]
    assert requests == _expected_mixed_requests()


def test_segment_edit_exact_batch_and_body_only_cleanup(mocker):
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    chain = service.documents.return_value
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "tabs": [_segment_scope()],
    })
    cleanup = mocker.patch("gdoc.api.docs._build_cleanup_requests", return_value=[])
    assert replace_formatted(
        "doc-one", _mixed_matches(), "***REPLACED***", "revision-one",
        tab_id="tab-one",
    ) == 3
    chain.batchUpdate.assert_called_once_with(documentId="doc-one", body={
        "requests": _expected_mixed_requests(body_paragraph=True),
        "writeControl": {"requiredRevisionId": "revision-one"},
    })
    cleanup.assert_called_once_with(
        _segment_scope()["documentTab"]["body"], 9, "tab-one",
    )


@pytest.mark.parametrize("markdown", [
    "# Heading", "- Item", "1. Item", "> Quote", "---",
    "| A |\n| --- |\n| B |", "```\ncode\n```", "First\n\nSecond",
])
def test_segment_structural_markdown_rejected_before_batch(mocker, markdown):
    service = mocker.patch("gdoc.api.docs.get_docs_service")
    with pytest.raises(GdocError) as error:
        replace_formatted("doc-one", [_mixed_matches()[0]], markdown, "revision-one")
    assert error.value.exit_code == 3
    service.assert_not_called()


def test_segment_sort_descends_only_inside_each_container():
    from gdoc.api.docs import _build_replacement_requests
    from gdoc.mdparse import ParsedMarkdown

    matches = _mixed_matches()
    matches.extend([
        {**matches[1], "startIndex": 20, "endIndex": 25},
        {**matches[2], "startIndex": 10, "endIndex": 15},
    ])
    ordered, _ = _build_replacement_requests(ParsedMarkdown("R"), matches)
    assert [(m["container"], m["startIndex"]) for m in ordered] == [
        ("body", 10), ("body", 1), ("header", 20), ("header", 1),
        ("footnote", 1),
    ]
