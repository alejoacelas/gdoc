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


def _styled_body(prefix="Status: ", text="2. Archive the sample", left=None):
    start = 1 + len(prefix)
    elements = []
    if prefix:
        elements.append({"startIndex": 1, "endIndex": start,
                         "textRun": {"content": prefix, "textStyle": left or {}}})
    elements.append({"startIndex": start, "endIndex": start + len(text) + 1,
                     "textRun": {"content": text + "\n", "textStyle": {}}})
    return {"content": [{"startIndex": 1, "endIndex": start + len(text) + 1,
                         "paragraph": {"elements": elements, "paragraphStyle": {
                             "namedStyleType": "HEADING_2", "alignment": "END",
                         }}}]}


@pytest.mark.parametrize("replacement,inserted,baseline,extra", [
    ("closed", "closed", True, []),
    ("1. Archive the sample", "1. Archive the sample", False, []),
    ("# label", "# label", False, []),
    ("- note", "- note", False, []),
    ("**closed**", "closed", True, [({"bold": True}, "bold")]),
    # Partial replacements are inline Markdown only: a fence is a CommonMark
    # code span when closed by an equal backtick string, literal otherwise.
    ("``closed``", "closed", False,
     [({"weightedFontFamily": {"fontFamily": "Courier New"}}, "weightedFontFamily")]),
    ("``` closed", "``` closed", False, []),
])
def test_inline_exact_batch(mocker, replacement, inserted, baseline, extra):
    svc = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    chain = svc.documents.return_value
    body = _styled_body(left={"bold": True} if baseline else {})
    match = {"startIndex": 9, "endIndex": 30}
    target = {"startIndex": 9, "endIndex": 9 + len(inserted), "tabId": "tab-a"}
    requests = [
        {"deleteContentRange": {"range": {**match, "tabId": "tab-a"}}},
        {"insertText": {"location": {"index": 9, "tabId": "tab-a"}, "text": inserted}},
    ]
    if baseline:
        requests.append({"updateTextStyle": {
            "range": target, "textStyle": {}, "fields": "bold",
        }})
    requests.extend({"updateTextStyle": {
        "range": target, "textStyle": style, "fields": fields,
    }} for style, fields in extra)
    assert replace_formatted("sample-doc", [match], replacement, "rev-a",
                             tab_id="tab-a", body=body) == 1
    chain.batchUpdate.assert_called_once_with(documentId="sample-doc", body={
        "requests": requests, "writeControl": {"requiredRevisionId": "rev-a"},
    })


@pytest.mark.parametrize("replacement,inserted,structural", [
    ("New label", "New label", False),
    ("1. Archive the sample", "Archive the sample", True),
])
def test_complete_heading_exact_batch(mocker, replacement, inserted, structural):
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    chain = service.documents.return_value
    chain.get.return_value.execute.return_value = {"body": {"content": []}}
    body = _styled_body(prefix="", text="Old label")
    target = {"startIndex": 1, "endIndex": 1 + len(inserted)}
    requests = [
        {"deleteContentRange": {"range": {"startIndex": 1, "endIndex": 10}}},
        {"insertText": {"location": {"index": 1}, "text": inserted}},
    ]
    if structural:
        requests.extend([
            {"updateParagraphStyle": {"range": target,
                                      "paragraphStyle": {
                                          "namedStyleType": "NORMAL_TEXT"},
                                      "fields": "namedStyleType"}},
            {"createParagraphBullets": {"range": target,
                                        "bulletPreset":
                                            "NUMBERED_DECIMAL_ALPHA_ROMAN"}},
        ])
    replace_formatted("sample-doc", [{"startIndex": 1, "endIndex": 10}],
                      replacement, "rev-a", body=body)
    chain.batchUpdate.assert_called_once_with(documentId="sample-doc", body={
        "requests": requests, "writeControl": {"requiredRevisionId": "rev-a"},
    })


@pytest.mark.parametrize("decor,fields", [
    ({}, "link"),
    ({"underline": True,
      "foregroundColor": {"color": {"rgbColor": {"red": 0.5}}}},
     "foregroundColor,link,underline"),
])
def test_inline_reapplies_link_shared_with_neighbour(mocker, decor, fields):
    # Docs does not guarantee inserted text inherits a neighbour's link, so a
    # homogeneously linked target must get its link restored explicitly, and
    # setting a link resets colour/underline unless sent in the same request.
    link = {"link": {"url": "https://example.com/spec"}, **decor}
    body = _styled_body(left=dict(link))
    body["content"][0]["paragraph"]["elements"][1]["textRun"]["textStyle"] = dict(link)
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    match = {"startIndex": 9, "endIndex": 30}
    replace_formatted("sample-doc", [match], "done", "rev-a", body=body)
    service.documents.return_value.batchUpdate.assert_called_once_with(
        documentId="sample-doc", body={
            "requests": [
                {"deleteContentRange": {"range": match}},
                {"insertText": {"location": {"index": 9}, "text": "done"}},
                {"updateTextStyle": {
                    "range": {"startIndex": 9, "endIndex": 13},
                    "textStyle": link, "fields": fields,
                }},
            ],
            "writeControl": {"requiredRevisionId": "rev-a"},
        },
    )


def test_inline_reapplies_link_decorations_after_replacement_link(mocker):
    # A Markdown link in the replacement sets only `link`, which resets colour
    # and underline to the link defaults, so the restored decorations must be
    # applied again after the parsed style requests.
    decor = {"underline": False,
             "foregroundColor": {"color": {"rgbColor": {"red": 1}}}}
    style = {"link": {"url": "https://example.com/old"}, **decor}
    body = _styled_body(left=dict(style))
    body["content"][0]["paragraph"]["elements"][1]["textRun"]["textStyle"] = dict(style)
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    match = {"startIndex": 9, "endIndex": 30}
    whole = {"startIndex": 9, "endIndex": 17, "tabId": "tab-a"}
    replace_formatted("sample-doc", [match], "[new](https://x.example) done",
                      "rev-a", tab_id="tab-a", body=body)
    service.documents.return_value.batchUpdate.assert_called_once_with(
        documentId="sample-doc", body={
            "requests": [
                {"deleteContentRange": {"range": {**match, "tabId": "tab-a"}}},
                {"insertText": {"location": {"index": 9, "tabId": "tab-a"},
                                "text": "new done"}},
                {"updateTextStyle": {
                    "range": whole, "textStyle": style,
                    "fields": "foregroundColor,link,underline",
                }},
                {"updateTextStyle": {
                    "range": {"startIndex": 9, "endIndex": 12, "tabId": "tab-a"},
                    "textStyle": {"link": {"url": "https://x.example"}},
                    "fields": "link",
                }},
                {"updateTextStyle": {
                    "range": whole, "textStyle": decor,
                    "fields": "foregroundColor,underline",
                }},
            ],
            "writeControl": {"requiredRevisionId": "rev-a"},
        },
    )


def test_empty_whole_paragraph_replacement_still_cleans_up_heading(mocker):
    # Deleting all of a heading's text is not an inline edit: the block path
    # runs so the leftover empty heading paragraph is removed as before.
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    chain = service.documents.return_value
    chain.get.return_value.execute.return_value = {"body": {"content": [{
        "startIndex": 1, "endIndex": 2, "paragraph": {
            "elements": [{"startIndex": 1, "endIndex": 2,
                          "textRun": {"content": "\n", "textStyle": {}}}],
            "paragraphStyle": {"namedStyleType": "HEADING_2"},
        },
    }]}}
    body = _styled_body(prefix="", text="Old label")
    assert replace_formatted("sample-doc", [{"startIndex": 1, "endIndex": 10}],
                             "", "rev-a", body=body) == 1
    assert chain.batchUpdate.call_args_list == [
        mocker.call(documentId="sample-doc", body={
            "requests": [{"deleteContentRange": {
                "range": {"startIndex": 1, "endIndex": 10}}}],
            "writeControl": {"requiredRevisionId": "rev-a"},
        }),
        mocker.call(documentId="sample-doc", body={
            "requests": [{"deleteContentRange": {
                "range": {"startIndex": 1, "endIndex": 2}}}],
        }),
    ]


@pytest.mark.parametrize("in_cell", [False, True])
def test_inline_restores_direct_fields_with_utf16_range(mocker, in_cell):
    body = _styled_body(left={"bold": True, "italic": True})
    body["content"][0]["paragraph"]["elements"][1]["textRun"]["textStyle"] = {
        "italic": True, "fontSize": {"magnitude": 22, "unit": "PT"},
    }
    if in_cell:
        body = {"content": [{"table": {"tableRows": [{"tableCells": [body]}]}}]}
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    match = {"startIndex": 9, "endIndex": 30}
    replace_formatted("sample-doc", [match], "😀done", "rev-a", body=body)
    service.documents.return_value.batchUpdate.assert_called_once_with(
        documentId="sample-doc", body={
            "requests": [
                {"deleteContentRange": {"range": match}},
                {"insertText": {"location": {"index": 9}, "text": "😀done"}},
                {"updateTextStyle": {
                    "range": {"startIndex": 9, "endIndex": 15},
                    "textStyle": {"fontSize": {"magnitude": 22, "unit": "PT"}},
                    "fields": "bold,fontSize",
                }},
            ],
            "writeControl": {"requiredRevisionId": "rev-a"},
        },
    )


def test_all_can_mix_inline_and_complete_paragraphs(mocker):
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    chain = service.documents.return_value
    chain.get.return_value.execute.return_value = {"body": {"content": []}}
    body = _styled_body(prefix="Status: ", text="old")
    body["content"].append({"paragraph": {"elements": [{
        "startIndex": 13, "endIndex": 17,
        "textRun": {"content": "old\n", "textStyle": {}},
    }]}})
    matches = [{"startIndex": 9, "endIndex": 12},
               {"startIndex": 13, "endIndex": 16}]
    replace_formatted("sample-doc", matches, "1. item", "rev-a", body=body)
    chain.batchUpdate.assert_called_once_with(documentId="sample-doc", body={
        "requests": [
            {"deleteContentRange": {"range": matches[1]}},
            {"insertText": {"location": {"index": 13}, "text": "item"}},
            {"updateParagraphStyle": {
                "range": {"startIndex": 13, "endIndex": 17},
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType",
            }},
            {"createParagraphBullets": {
                "range": {"startIndex": 13, "endIndex": 17},
                "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN",
            }},
            {"deleteContentRange": {"range": matches[0]}},
            {"insertText": {"location": {"index": 9}, "text": "1. item"}},
        ],
        "writeControl": {"requiredRevisionId": "rev-a"},
    })


def test_paragraph_start_restores_style_from_deleted_run(mocker):
    body = {"content": [{"paragraph": {"elements": [
        {"startIndex": 1, "endIndex": 4,
         "textRun": {"content": "Old", "textStyle": {"bold": True}}},
        {"startIndex": 4, "endIndex": 11,
         "textRun": {"content": " label\n", "textStyle": {}}},
    ]}}]}
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    match = {"startIndex": 1, "endIndex": 4}
    replace_formatted("sample-doc", [match], "New", "rev-a", body=body)
    service.documents.return_value.batchUpdate.assert_called_once_with(
        documentId="sample-doc", body={
            "requests": [
                {"deleteContentRange": {"range": match}},
                {"insertText": {"location": {"index": 1}, "text": "New"}},
                {"updateTextStyle": {"range": match, "textStyle": {"bold": True},
                                     "fields": "bold"}},
            ],
            "writeControl": {"requiredRevisionId": "rev-a"},
        },
    )
