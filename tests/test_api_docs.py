"""Tests for gdoc.api.docs: Docs API v1 wrapper functions with mocked service."""

from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from gdoc.api.docs import _translate_http_error, replace_all_text
from gdoc.util import AuthError, GdocError


def _make_http_error(status: int, reason: str = "") -> HttpError:
    """Create a mock HttpError with the given status and reason."""
    resp = httplib2.Response({"status": str(status)})
    error = HttpError(resp, b"")
    error.reason = reason
    return error


class TestTranslateHttpError:
    def test_401_raises_auth_error(self):
        err = _make_http_error(401)
        with pytest.raises(AuthError, match="Authentication expired"):
            _translate_http_error(err, "abc123")

    def test_403_raises_gdoc_error(self):
        err = _make_http_error(403, reason="forbidden")
        with pytest.raises(GdocError, match="Permission denied: abc123"):
            _translate_http_error(err, "abc123")

    def test_404_raises_gdoc_error(self):
        err = _make_http_error(404)
        with pytest.raises(GdocError, match="Document not found: abc123"):
            _translate_http_error(err, "abc123")

    def test_500_raises_gdoc_error(self):
        err = _make_http_error(500, reason="Internal Server Error")
        with pytest.raises(
            GdocError, match=r"API error \(500\): Internal Server Error"
        ):
            _translate_http_error(err, "abc123")


@patch("gdoc.api.docs.get_docs_service")
class TestReplaceAllText:
    def test_success(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.return_value = {
            "replies": [{"replaceAllText": {"occurrencesChanged": 3}}]
        }

        result = replace_all_text("abc123", "old", "new")
        assert result == 3

    def test_correct_request_body(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.return_value = {
            "replies": [{"replaceAllText": {"occurrencesChanged": 1}}]
        }

        replace_all_text("abc123", "hello", "world", match_case=False)

        mock_service.documents().batchUpdate.assert_called_with(
            documentId="abc123",
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {
                                "text": "hello",
                                "matchCase": False,
                            },
                            "replaceText": "world",
                        }
                    }
                ]
            },
        )

    def test_case_sensitive(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.return_value = {
            "replies": [{"replaceAllText": {"occurrencesChanged": 1}}]
        }

        replace_all_text("abc123", "Hello", "World", match_case=True)

        mock_service.documents().batchUpdate.assert_called_with(
            documentId="abc123",
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {
                                "text": "Hello",
                                "matchCase": True,
                            },
                            "replaceText": "World",
                        }
                    }
                ]
            },
        )

    def test_zero_occurrences(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.return_value = {
            "replies": [{"replaceAllText": {"occurrencesChanged": 0}}]
        }

        result = replace_all_text("abc123", "nonexistent", "new")
        assert result == 0

    def test_empty_replies(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.return_value = {
            "replies": []
        }

        result = replace_all_text("abc123", "old", "new")
        assert result == 0

    def test_http_error_401(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.side_effect = _make_http_error(
            401
        )

        with pytest.raises(AuthError, match="Authentication expired"):
            replace_all_text("abc123", "old", "new")

    def test_http_error_403(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.side_effect = _make_http_error(
            403, reason="forbidden"
        )

        with pytest.raises(GdocError, match="Permission denied: abc123"):
            replace_all_text("abc123", "old", "new")

    def test_http_error_404(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.side_effect = _make_http_error(
            404
        )

        with pytest.raises(GdocError, match="Document not found: abc123"):
            replace_all_text("abc123", "old", "new")

    def test_http_error_500(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.documents().batchUpdate().execute.side_effect = _make_http_error(
            500, reason="Internal Server Error"
        )

        with pytest.raises(GdocError, match=r"API error \(500\)"):
            replace_all_text("abc123", "old", "new")


class TestGetDocsServiceCaches:
    def test_caches_service(self):
        """The per-account @lru_cache lives on _docs_service; the public
        get_docs_service is a thin wrapper that resolves the account."""
        from gdoc.api.docs import _docs_service
        assert hasattr(_docs_service, "cache_info")


class TestGetDocumentWithTabs:
    @patch("gdoc.api.docs.get_docs_service")
    def test_returns_full_doc(self, mock_svc):
        from gdoc.api.docs import get_document_with_tabs

        mock_doc = {"revisionId": "rev1", "tabs": []}
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = mock_doc

        result = get_document_with_tabs("doc1")
        assert result == mock_doc
        mock_svc.return_value.documents.return_value.get.assert_called_with(
            documentId="doc1", includeTabsContent=True,
        )

    @patch("gdoc.api.docs.get_docs_service")
    def test_404_translated(self, mock_svc):
        from gdoc.api.docs import get_document_with_tabs

        resp = MagicMock()
        resp.status = 404
        err = HttpError(resp, b"not found", uri="")
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.side_effect = err

        with pytest.raises(GdocError, match="Document not found"):
            get_document_with_tabs("doc1")

    @patch("gdoc.api.docs.get_docs_service")
    def test_401_translated(self, mock_svc):
        from gdoc.api.docs import get_document_with_tabs

        resp = MagicMock()
        resp.status = 401
        err = HttpError(resp, b"unauthorized", uri="")
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.side_effect = err

        with pytest.raises(AuthError):
            get_document_with_tabs("doc1")


class TestBuildCleanupRequests:
    def test_empty_heading_produces_requests(self):
        from gdoc.api.docs import _build_cleanup_requests

        body = {"content": [
            {
                "paragraph": {
                    "elements": [{"textRun": {"content": "text\n"}}],
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                },
                "startIndex": 1,
                "endIndex": 6,
            },
            {
                "paragraph": {
                    "elements": [{"textRun": {"content": "\n"}}],
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                },
                "startIndex": 6,
                "endIndex": 7,
            },
        ]}
        reqs = _build_cleanup_requests(body, 6)
        assert len(reqs) == 2
        # First: transfer style to preceding paragraph
        assert "updateParagraphStyle" in reqs[0]
        style = reqs[0]["updateParagraphStyle"]["paragraphStyle"]
        assert style["namedStyleType"] == "HEADING_1"
        # Second: delete the empty heading
        assert "deleteContentRange" in reqs[1]
        assert reqs[1]["deleteContentRange"]["range"]["startIndex"] == 6

    def test_normal_text_noop(self):
        from gdoc.api.docs import _build_cleanup_requests

        body = {"content": [{
            "paragraph": {
                "elements": [{"textRun": {"content": "\n"}}],
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            },
            "startIndex": 1,
            "endIndex": 2,
        }]}
        assert _build_cleanup_requests(body, 1) == []

    def test_no_element_at_position_noop(self):
        from gdoc.api.docs import _build_cleanup_requests

        body = {"content": []}
        assert _build_cleanup_requests(body, 99) == []

    def test_non_empty_heading_noop(self):
        from gdoc.api.docs import _build_cleanup_requests

        body = {"content": [{
            "paragraph": {
                "elements": [{"textRun": {"content": "Title\n"}}],
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
            },
            "startIndex": 1,
            "endIndex": 7,
        }]}
        assert _build_cleanup_requests(body, 1) == []

    def test_tab_id_included(self):
        from gdoc.api.docs import _build_cleanup_requests

        body = {"content": [
            {
                "paragraph": {
                    "elements": [{"textRun": {"content": "x\n"}}],
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                },
                "startIndex": 1,
                "endIndex": 3,
            },
            {
                "paragraph": {
                    "elements": [{"textRun": {"content": "\n"}}],
                    "paragraphStyle": {"namedStyleType": "HEADING_2"},
                },
                "startIndex": 3,
                "endIndex": 4,
            },
        ]}
        reqs = _build_cleanup_requests(body, 3, tab_id="tab1")
        assert reqs[0]["updateParagraphStyle"]["range"]["tabId"] == "tab1"
        assert reqs[1]["deleteContentRange"]["range"]["tabId"] == "tab1"

    def test_style_transferred_from_heading(self):
        from gdoc.api.docs import _build_cleanup_requests

        body = {"content": [
            {
                "paragraph": {
                    "elements": [{"textRun": {"content": "text\n"}}],
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                },
                "startIndex": 1,
                "endIndex": 6,
            },
            {
                "paragraph": {
                    "elements": [{"textRun": {"content": "\n"}}],
                    "paragraphStyle": {"namedStyleType": "HEADING_3"},
                },
                "startIndex": 6,
                "endIndex": 7,
            },
        ]}
        reqs = _build_cleanup_requests(body, 6)
        ups = reqs[0]["updateParagraphStyle"]
        assert ups["paragraphStyle"]["namedStyleType"] == "HEADING_3"


class TestReplaceFormattedCleanupPositions:
    """Verify cleanup positions account for multi-match replacement delta."""

    @patch("gdoc.api.docs._build_cleanup_requests", return_value=[])
    @patch("gdoc.api.docs.get_docs_service")
    def test_single_match_cleanup_position(self, mock_svc, mock_cleanup):
        """Single match: cleanup pos = startIndex + len(new_text)."""
        from gdoc.api.docs import replace_formatted

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.return_value = {}
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {"body": {"content": []}}

        matches = [{"startIndex": 10, "endIndex": 13}]  # 3-char match
        replace_formatted("doc1", matches, "foobar", "rev1")  # 6-char plain_text

        mock_cleanup.assert_called_once()
        # cleanup pos = 10 + 6 = 16 (trailing \n stripped in replace context)
        assert mock_cleanup.call_args[0][1] == 16

    @patch("gdoc.api.docs._build_cleanup_requests", return_value=[])
    @patch("gdoc.api.docs.get_docs_service")
    def test_multi_match_cleanup_positions(self, mock_svc, mock_cleanup):
        """Multiple matches: higher-index matches get delta shift from
        lower-index replacements that occur before them in the document."""
        from gdoc.api.docs import replace_formatted

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.return_value = {}
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {"body": {"content": []}}

        # 3 matches of 3-char text, replaced with "foobar" (plain_text
        # is "foobar" = 6 chars after trailing \n strip, delta = 6 - 3 = 3)
        matches = [
            {"startIndex": 10, "endIndex": 13},
            {"startIndex": 50, "endIndex": 53},
            {"startIndex": 100, "endIndex": 103},
        ]
        replace_formatted("doc1", matches, "foobar", "rev1")

        positions = [c[0][1] for c in mock_cleanup.call_args_list]
        # sorted_matches descending: [100, 50, 10]; delta=3
        # j=0 (100): 100 + 6 + (3-1-0)*3 = 100 + 6 + 6 = 112
        # j=1 (50):  50  + 6 + (3-1-1)*3 = 50  + 6 + 3 = 59
        # j=2 (10):  10  + 6 + (3-1-2)*3 = 10  + 6 + 0 = 16
        assert positions == [112, 59, 16]

    @patch("gdoc.api.docs._build_cleanup_requests", return_value=[])
    @patch("gdoc.api.docs.get_docs_service")
    def test_cleanup_position_counts_emoji_as_two_units(self, mock_svc, mock_cleanup):
        """Docs indexes are UTF-16: a non-BMP emoji in the replacement
        grows the document by 2, so the cleanup position must reflect it."""
        from gdoc.api.docs import replace_formatted

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.return_value = {}
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {"body": {"content": []}}

        matches = [{"startIndex": 10, "endIndex": 13}]
        replace_formatted("doc1", matches, "\U0001F600ab", "rev1")  # 3 chars, 4 units

        pos = mock_cleanup.call_args[0][1]
        assert pos == 14

    @patch("gdoc.api.docs._insert_table")
    @patch("gdoc.api.docs._build_cleanup_requests", return_value=[])
    @patch("gdoc.api.docs.get_docs_service")
    def test_table_index_after_emoji_is_utf16(
        self, mock_svc, _cleanup, mock_table,
    ):
        from gdoc.api.docs import replace_formatted

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.return_value = {}
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {"body": {"content": []}}

        md = "\U0001F600 x\n| a | b |\n|---|---|\n| 1 | 2 |"
        replace_formatted("doc1", [{"startIndex": 5, "endIndex": 6}], md, "rev1")

        # plain text before the table placeholder is "😀 x\n" = 4 code
        # points but 5 UTF-16 units.
        assert mock_table.call_args[0][1] == 5 + 5

    @patch("gdoc.api.docs._build_cleanup_requests", return_value=[])
    @patch("gdoc.api.docs.get_docs_service")
    def test_same_length_replacement_no_drift(self, mock_svc, mock_cleanup):
        """When replacement is same length as original, delta=0."""
        from gdoc.api.docs import replace_formatted

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.return_value = {}
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {"body": {"content": []}}

        # 3-char match, "bar" -> plain_text "bar" (3 chars), delta=0
        matches = [
            {"startIndex": 10, "endIndex": 13},
            {"startIndex": 50, "endIndex": 53},
        ]
        replace_formatted("doc1", matches, "bar", "rev1")

        positions = [c[0][1] for c in mock_cleanup.call_args_list]
        # j=0 (50): 50 + 3 + (2-1-0)*0 = 53
        # j=1 (10): 10 + 3 + (2-1-1)*0 = 13
        assert positions == [53, 13]


class TestFindTextBody:
    def test_find_text_with_explicit_body(self):
        from gdoc.api.docs import find_text_in_document

        body = {"content": [{
            "paragraph": {
                "elements": [{
                    "startIndex": 1,
                    "textRun": {"content": "hello world\n"},
                }],
            },
        }]}
        matches = find_text_in_document(None, "world", body=body)
        assert len(matches) == 1
        assert matches[0]["startIndex"] == 7

    def test_both_none_returns_empty(self):
        from gdoc.api.docs import find_text_in_document

        assert find_text_in_document(None, "text") == []

    @staticmethod
    def _cell(text, start):
        return {"content": [{
            "paragraph": {
                "elements": [{"startIndex": start, "textRun": {"content": text}}],
            },
        }]}

    def test_find_text_in_table_cell(self):
        from gdoc.api.docs import find_text_in_document

        body = {"content": [{
            "table": {"tableRows": [{"tableCells": [
                self._cell("Label\n", 5),
                self._cell("Answer here\n", 20),
            ]}]},
        }]}
        matches = find_text_in_document(None, "Answer", body=body)
        assert len(matches) == 1
        assert matches[0]["startIndex"] == 20
        assert matches[0]["endIndex"] == 26

    def test_find_text_in_nested_table(self):
        from gdoc.api.docs import find_text_in_document

        inner = {"table": {"tableRows": [{"tableCells": [
            self._cell("deep value\n", 50),
        ]}]}}
        body = {"content": [{
            "table": {"tableRows": [{"tableCells": [
                {"content": [inner]},
            ]}]},
        }]}
        matches = find_text_in_document(None, "deep", body=body)
        assert len(matches) == 1
        assert matches[0]["startIndex"] == 50

    def test_match_does_not_span_cells(self):
        from gdoc.api.docs import find_text_in_document

        body = {"content": [{
            "table": {"tableRows": [{"tableCells": [
                self._cell("foo\n", 10),
                self._cell("bar\n", 30),
            ]}]},
        }]}
        # Neither a plain concatenation ("foobar") nor a newline-spanning
        # anchor ("foo\nbar") may match across the cell boundary \u2014 that would
        # yield an invalid cross-cell delete range.
        assert find_text_in_document(None, "foobar", body=body) == []
        assert find_text_in_document(None, "foo\nbar", body=body) == []
        # Each cell is still searchable on its own.
        assert find_text_in_document(None, "foo", body=body)[0]["startIndex"] == 10
        assert find_text_in_document(None, "bar", body=body)[0]["startIndex"] == 30

    def test_paragraph_and_table_coexist(self):
        from gdoc.api.docs import find_text_in_document

        body = {"content": [
            {"paragraph": {"elements": [
                {"startIndex": 1, "textRun": {"content": "hello world\n"}},
            ]}},
            {"table": {"tableRows": [{"tableCells": [
                self._cell("world\n", 20),
            ]}]}},
        ]}
        matches = find_text_in_document(None, "world", body=body)
        assert [m["startIndex"] for m in matches] == [7, 20]

    def test_normalize_matches_smart_quotes(self):
        from gdoc.api.docs import find_text_in_document

        body = {"content": [{
            "paragraph": {"elements": [{
                "startIndex": 1, "textRun": {"content": "JP\u2019s job\n"},
            }]},
        }]}
        assert find_text_in_document(None, "JP's job", body=body) == []
        m = find_text_in_document(None, "JP's job", body=body, normalize=True)
        assert len(m) == 1 and m[0]["startIndex"] == 1


class TestDiagnoseNoMatch:
    @staticmethod
    def _para_body(text):
        return {"content": [{
            "paragraph": {"elements": [{
                "startIndex": 1, "textRun": {"content": text},
            }]},
        }]}

    def test_suggests_normalize_on_quote_mismatch(self):
        from gdoc.api.docs import diagnose_no_match

        reason = diagnose_no_match(
            None, "JP's job", body=self._para_body("JP\u2019s job\n")
        )
        assert reason is not None and "--normalize" in reason

    def test_reports_whitespace_difference(self):
        from gdoc.api.docs import diagnose_no_match

        reason = diagnose_no_match(
            None, "a b", body=self._para_body("a\nb\n"),
        )
        assert reason is not None and "whitespace" in reason

    def test_no_near_match_returns_none(self):
        from gdoc.api.docs import diagnose_no_match

        assert diagnose_no_match(None, "zzz", body=self._para_body("abc\n")) is None

    def test_already_normalized_skips_quote_suggestion(self):
        from gdoc.api.docs import diagnose_no_match

        reason = diagnose_no_match(
            None, "JP's job", body=self._para_body("JP\u2019s job\n"),
            already_normalized=True,
        )
        assert reason is None or "--normalize" not in reason


class TestAddTab:
    @patch("gdoc.api.docs.get_docs_service")
    def test_add_tab_success(self, mock_svc):
        from gdoc.api.docs import add_tab

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.return_value = {
                "replies": [{"addDocumentTab": {"tabProperties": {
                    "tabId": "t99", "title": "Notes", "index": 1,
                }}}],
            }

        result = add_tab("doc1", "Notes")
        assert result == {"tabId": "t99", "title": "Notes", "index": 1}
        mock_svc.return_value.documents.return_value.batchUpdate.assert_called_with(
            documentId="doc1",
            body={"requests": [{"addDocumentTab": {
                "tabProperties": {"title": "Notes"},
            }}]},
        )

    @patch("gdoc.api.docs.get_docs_service")
    def test_add_tab_404(self, mock_svc):
        from gdoc.api.docs import add_tab

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.side_effect = _make_http_error(404)

        with pytest.raises(GdocError, match="Document not found: doc1"):
            add_tab("doc1", "Notes")

    @patch("gdoc.api.docs.get_docs_service")
    def test_add_tab_401(self, mock_svc):
        from gdoc.api.docs import add_tab

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.side_effect = _make_http_error(401)

        with pytest.raises(AuthError, match="Authentication expired"):
            add_tab("doc1", "Notes")

    @patch("gdoc.api.docs.get_docs_service")
    def test_add_tab_malformed_response(self, mock_svc):
        from gdoc.api.docs import add_tab

        mock_svc.return_value.documents.return_value \
            .batchUpdate.return_value.execute.return_value = {"replies": []}

        with pytest.raises(GdocError, match="Unexpected API response"):
            add_tab("doc1", "Notes")


def _capture_batch_updates(mock_svc):
    """Wire mock_svc so every documents().batchUpdate(...) is captured.

    Returns a list that accumulates each call's body kwarg.
    """
    captured: list = []

    def _bu(documentId, body):  # noqa: N803 - matches the Google API keyword
        captured.append(body)
        inner = MagicMock()
        inner.execute.return_value = {}
        return inner

    mock_svc.return_value.documents.return_value \
        .batchUpdate.side_effect = _bu
    return captured


class TestCountDocumentTabs:
    """count_document_tabs requests tab content and counts nested tabs."""

    @patch("gdoc.api.docs.get_docs_service")
    def test_flat_tab_list(self, mock_svc):
        from gdoc.api.docs import count_document_tabs

        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {
                "tabs": [
                    {"tabProperties": {"tabId": "t1"}},
                    {"tabProperties": {"tabId": "t2"}},
                ],
            }
        assert count_document_tabs("doc1") == 2

    @patch("gdoc.api.docs.get_docs_service")
    def test_nested_child_tabs_counted(self, mock_svc):
        from gdoc.api.docs import count_document_tabs

        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {
                "tabs": [
                    {
                        "tabProperties": {"tabId": "t1"},
                        "childTabs": [
                            {"tabProperties": {"tabId": "t1a"}},
                            {"tabProperties": {"tabId": "t1b"}},
                        ],
                    },
                    {"tabProperties": {"tabId": "t2"}},
                ],
            }
        assert count_document_tabs("doc1") == 4

    @patch("gdoc.api.docs.get_docs_service")
    def test_requests_tabs_content_without_fields_mask(self, mock_svc):
        from gdoc.api.docs import count_document_tabs

        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {"tabs": []}
        count_document_tabs("doc1")
        call_kwargs = mock_svc.return_value.documents.return_value \
            .get.call_args.kwargs
        assert call_kwargs.get("includeTabsContent") is True
        assert "fields" not in call_kwargs


class TestZeroWidthReplace:
    """Zero-width matches in replace_formatted act as pure inserts \u2014 no
    deleteContentRange is emitted (Docs API rejects empty ranges)."""

    @patch("gdoc.api.docs._build_cleanup_requests", return_value=[])
    @patch("gdoc.api.docs.get_docs_service")
    def test_zero_width_match_skips_delete(self, mock_svc, _cleanup):
        from gdoc.api.docs import replace_formatted

        captured = _capture_batch_updates(mock_svc)
        mock_svc.return_value.documents.return_value \
            .get.return_value.execute.return_value = {"body": {"content": []}}

        matches = [{"startIndex": 1, "endIndex": 1}]
        replace_formatted("doc1", matches, "hello", "rev1")

        assert captured, "batchUpdate not called"
        reqs = captured[0]["requests"]
        delete_reqs = [r for r in reqs if "deleteContentRange" in r]
        insert_reqs = [r for r in reqs if "insertText" in r]
        assert delete_reqs == []
        assert len(insert_reqs) == 1
        assert insert_reqs[0]["insertText"]["text"] == "hello"


class TestInsertMarkdownIntoTab:
    @pytest.fixture(autouse=True)
    def _comments(self, mocker):
        mocker.patch("gdoc.api.comments.list_comments", return_value=[])

    def _tabs_doc(self, body_content=None):
        return {
            "revisionId": "rev-xyz",
            "tabs": [{
                "tabProperties": {
                    "tabId": "t.todo", "title": "TODO", "index": 0,
                },
                "documentTab": {
                    "body": {"content": body_content or []},
                },
            }],
        }

    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_insert_empty_tab_start(self, mock_get, mock_svc):
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = self._tabs_doc()
        captured = _capture_batch_updates(mock_svc)

        result = insert_markdown_into_tab(
            "doc1", "TODO", "hello\n", position="start", replace=False,
        )

        assert result["tab_id"] == "t.todo"
        assert result["insert_index"] == 1
        assert len(captured) == 1
        reqs = captured[0]["requests"]
        delete_reqs = [r for r in reqs if "deleteContentRange" in r]
        insert_reqs = [r for r in reqs if "insertText" in r]
        assert delete_reqs == []
        assert len(insert_reqs) == 1
        # parse_markdown emits "hello\n\n" for "hello\n"; single trailing
        # \n strip matches replace_formatted's behavior, leaving one \n as
        # the paragraph marker.
        assert insert_reqs[0]["insertText"]["text"] == "hello\n"
        assert captured[0]["writeControl"] == {
            "requiredRevisionId": "rev-xyz",
        }
        assert insert_reqs[0]["insertText"]["location"]["tabId"] == "t.todo"

    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_insert_nonempty_tab_end(self, mock_get, mock_svc):
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = self._tabs_doc(body_content=[
            {"startIndex": 1, "endIndex": 20, "paragraph": {}},
        ])
        captured = _capture_batch_updates(mock_svc)

        result = insert_markdown_into_tab(
            "doc1", "TODO", "tail", position="end", replace=False,
        )

        assert result["insert_index"] == 19
        reqs = captured[0]["requests"]
        insert_reqs = [r for r in reqs if "insertText" in r]
        assert insert_reqs[0]["insertText"]["location"]["index"] == 19
        assert insert_reqs[0]["insertText"]["text"] == "tail"

    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_replace_tab_body(self, mock_get, mock_svc):
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = self._tabs_doc(body_content=[
            {"startIndex": 1, "endIndex": 30, "paragraph": {}},
        ])
        captured = _capture_batch_updates(mock_svc)

        insert_markdown_into_tab(
            "doc1", "TODO", "new content", replace=True,
        )

        reqs = captured[0]["requests"]
        delete_reqs = [r for r in reqs if "deleteContentRange" in r]
        assert len(delete_reqs) == 1
        d_range = delete_reqs[0]["deleteContentRange"]["range"]
        assert d_range["startIndex"] == 1
        assert d_range["endIndex"] == 29
        assert d_range["tabId"] == "t.todo"

    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_replace_empty_tab_no_delete(self, mock_get, mock_svc):
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = self._tabs_doc()
        captured = _capture_batch_updates(mock_svc)

        insert_markdown_into_tab(
            "doc1", "TODO", "content", replace=True,
        )

        reqs = captured[0]["requests"]
        delete_reqs = [r for r in reqs if "deleteContentRange" in r]
        assert delete_reqs == []

    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_missing_tab_errors(self, mock_get):
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = self._tabs_doc()

        with pytest.raises(GdocError, match="tab not found"):
            insert_markdown_into_tab("doc1", "Not A Real Tab", "hi")


def _element(kind):
    """A paragraph holding one ParagraphElement of the given kind."""
    return {'body': {'content': [{'paragraph': {'elements': [
        {'startIndex': 1, 'endIndex': 2, kind: {}}]}}]}}


def _tab_map(kind):
    return {kind: {'id': {'content': []}}}


# Every structural, paragraph-element and tab-level kind in the Docs API
# schema other than the allowlist, plus one kind the API does not have yet.
_SCHEMA_BLOCKERS = [
    ({'body': {'content': [{'sectionBreak': {}}, {'paragraph': {}},
                           {'sectionBreak': {}}]}}, 'sectionBreak'),
    ({'body': {'content': [{'sectionBreak': {'sectionStyle': {
        'columnProperties': [{}, {}]}}}]}}, 'columnProperties'),
    ({'body': {'content': [{'tableOfContents': {'content': []}}]}},
     'tableOfContents'),
    ({'body': {'content': [{'table': {'rows': 1, 'columns': 1}}]}}, 'table'),
    (_element('pageBreak'), 'pageBreak'),
    (_element('columnBreak'), 'columnBreak'),
    (_element('inlineObjectElement'), 'inlineObjectElement'),
    (_element('richLink'), 'richLink'),
    (_element('person'), 'person'),
    (_element('horizontalRule'), 'horizontalRule'),
    (_element('footnoteReference'), 'footnoteReference'),
    (_element('equation'), 'equation'),
    (_element('autoText'), 'autoText'),
    (_element('dateElement'), 'dateElement'),
    (_element('elementAddedNextYear'), 'elementAddedNextYear'),
    ({'body': {'content': [{'paragraph': {
        'positionedObjectIds': ['kix.p']}}]}}, 'positionedObjectIds'),
    ({'body': {'content': [{'paragraph': {'elements': [{'textRun': {
        'content': 'x', 'suggestedInsertionIds': ['s']}}]}}]}},
     'suggestedInsertionIds'),
    ({'body': {'content': [{'paragraph': {'elements': [{'textRun': {
        'content': 'x', 'suggestedTextStyleChanges': {'s': {}}}}]}}]}},
     'suggestedTextStyleChanges'),
    ({'body': {'content': [{'paragraph': {
        'suggestedBulletChanges': {'s': {}}}}]}}, 'suggestedBulletChanges'),
    (_tab_map('headers'), 'headers'),
    (_tab_map('footers'), 'footers'),
    (_tab_map('footnotes'), 'footnotes'),
    ({'namedRanges': {'Reference': {'namedRanges': []}}}, 'namedRanges'),
    (_tab_map('inlineObjects'), 'inlineObjects'),
    (_tab_map('positionedObjects'), 'positionedObjects'),
    ({'suggestedDocumentStyleChanges': {'s': {}}},
     'suggestedDocumentStyleChanges'),
    ({'documentStyle': {'defaultHeaderId': 'h'}}, 'defaultHeaderId'),
    ({'documentStyle': {'firstPageFooterId': 'f'}}, 'firstPageFooterId'),
]


@pytest.mark.parametrize(('native', 'reason'), _SCHEMA_BLOCKERS)
def test_rebuild_blocks_every_kind_outside_the_allowlist(native, reason):
    from gdoc.api.docs import classify_markdown_rebuild

    assert classify_markdown_rebuild(native) == ([reason], [])


def test_rebuild_reports_each_blocked_field_name():
    from gdoc.api.docs import classify_markdown_rebuild

    native = {'body': {'content': [
        {'paragraph': {'elements': [{'footnoteReference': {}},
                                    {'inlineObjectElement': {}}]}},
        {'table': {}},
    ]}}
    assert classify_markdown_rebuild(native)[0] == [
        'footnoteReference', 'inlineObjectElement', 'table']


def test_rebuild_ignores_empty_native_maps():
    from gdoc.api.docs import classify_markdown_rebuild

    assert classify_markdown_rebuild({'headers': {}, 'footnotes': {},
                                      'inlineObjects': {}}) == ([], [])


def test_rebuild_allowlist_passes_silently():
    """Everything the importer round-trips: named styles, lists, inline styles."""
    from gdoc.api.docs import classify_markdown_rebuild

    code = {'weightedFontFamily': {'fontFamily': 'Courier New', 'weight': 400}}
    native = {'documentId': 'd', 'title': 'T', 'revisionId': 'r',
              'suggestionsViewMode': 'DEFAULT_FOR_CURRENT_ACCESS', 'tabs': [{
        'tabProperties': {'tabId': 't', 'title': 'Tab'}, 'childTabs': [],
        'documentTab': {
            'lists': {'l': {'listProperties': {}}},
            'namedStyles': {'styles': [{'namedStyleType': 'NORMAL_TEXT'}]},
            'body': {'content': [
                {'sectionBreak': {'sectionStyle': {'columnProperties': [{}]}}},
                {'startIndex': 1, 'endIndex': 9, 'paragraph': {
                    'paragraphStyle': {'namedStyleType': 'HEADING_1',
                                       'headingId': 'h.1',
                                       'direction': 'LEFT_TO_RIGHT'},
                    'elements': [{'startIndex': 1, 'endIndex': 9, 'textRun': {
                        'content': 'Heading\n', 'textStyle': {}}}]}},
                {'paragraph': {
                    'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT',
                                       'indentFirstLine': {'magnitude': 18},
                                       'indentStart': {'magnitude': 36}},
                    'bullet': {'listId': 'l', 'nestingLevel': 0,
                               'textStyle': {}},
                    'elements': [
                        {'textRun': {'content': 'bold ',
                                     'textStyle': {'bold': True}}},
                        {'textRun': {'content': 'italic ',
                                     'textStyle': {'italic': True}}},
                        {'textRun': {'content': 'gone ',
                                     'textStyle': {'strikethrough': True}}},
                        {'textRun': {'content': 'code ', 'textStyle': code}},
                        {'textRun': {'content': 'link\n', 'textStyle': {
                            'link': {'url': 'https://example.com'}}}},
                    ]}},
            ]},
        }}]}
    assert classify_markdown_rebuild(native) == ([], [])


@pytest.mark.parametrize(('native', 'reason'), [
    ({'textStyle': {'foregroundColor': {'color': {}}}}, 'colour'),
    ({'textStyle': {'smallCaps': True}}, 'small caps'),
    ({'textStyle': {'styleAddedNextYear': True}}, 'text style'),
    ({'textStyle': {'weightedFontFamily': {'fontFamily': 'Courier New',
                                           'weight': 700}}}, 'font'),
    ({'textStyle': {'backgroundColor': {'color': {}}}}, 'highlight'),
    ({'textStyle': {'underline': True}}, 'underline'),
    ({'textStyle': {'weightedFontFamily': {'fontFamily': 'Arial'}}}, 'font'),
    ({'textStyle': {'fontSize': {'magnitude': 16, 'unit': 'PT'}}}, 'font'),
    ({'textStyle': {'baselineOffset': 'SUPERSCRIPT'}}, 'baseline'),
    ({'paragraphStyle': {'alignment': 'END'}}, 'alignment'),
    ({'paragraphStyle': {'spaceAbove': {'magnitude': 8}}}, 'spacing'),
    ({'paragraphStyle': {'indentStart': {'magnitude': 8}}}, 'indents'),
    ({'paragraphStyle': {'keepWithNext': True}}, 'layout'),
    ({'textStyle': {'link': {'headingId': 'h'}}}, 'internal links'),
])
def test_rebuild_style_classes_warn(native, reason):
    from gdoc.api.docs import classify_markdown_rebuild

    assert classify_markdown_rebuild(native) == ([], [reason])


def test_rebuild_normal_text_and_generated_defaults_are_safe():
    from gdoc.api.docs import classify_markdown_rebuild

    assert classify_markdown_rebuild({
        'namedStyles': {'styles': [{'textStyle': {'fontSize': {}}}]},
        'body': {'content': [{'paragraph': {
            'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'},
            'elements': [{'textRun': {'content': 'Project notes\n',
                                     'textStyle': {'bold': True}}}],
        }}]},
    }) == ([], [])


_IMPORT_STYLE = {
    'documentFormat': {'documentMode': 'PAGES'},
    'pageSize': {'width': {'magnitude': 612, 'unit': 'PT'},
                 'height': {'magnitude': 792, 'unit': 'PT'}},
    'marginTop': {'magnitude': 72, 'unit': 'PT'},
    'marginBottom': {'magnitude': 72, 'unit': 'PT'},
    'marginLeft': {'magnitude': 72, 'unit': 'PT'},
    'marginRight': {'magnitude': 72, 'unit': 'PT'},
    'background': {'color': {}},
}


@pytest.mark.parametrize('override', [
    {'documentFormat': {'documentMode': 'PAGELESS'}},
    {'flipPageOrientation': True},
    {'background': {'color': {'color': {'rgbColor': {'red': 1}}}}},
    {'pageSize': {'width': {'magnitude': 595.28, 'unit': 'PT'},
                  'height': {'magnitude': 841.89, 'unit': 'PT'}}},
    {'marginTop': {'magnitude': 144, 'unit': 'PT'}},
])
def test_rebuild_warns_on_explicit_page_setup(override):
    from gdoc.api.docs import classify_markdown_rebuild

    style = {**_IMPORT_STYLE, **override}
    assert classify_markdown_rebuild({'documentStyle': style}) == ([], ['page setup'])


def _opening_section(style):
    return {'body': {'content': [{'sectionBreak': {'sectionStyle': style}},
                                 {'paragraph': {}}]}}


def test_rebuild_ignores_the_default_opening_section_break():
    from gdoc.api.docs import classify_markdown_rebuild

    style = {'columnSeparatorStyle': 'NONE', 'contentDirection': 'LEFT_TO_RIGHT',
             'sectionType': 'CONTINUOUS', 'columnProperties': [{'width': {}}]}
    assert classify_markdown_rebuild(_opening_section(style)) == ([], [])


@pytest.mark.parametrize('style,expected', [
    ({'marginTop': {'magnitude': 144, 'unit': 'PT'}}, ([], ['section layout'])),
    ({'flipPageOrientation': True}, ([], ['section layout'])),
    ({'defaultHeaderId': 'h'}, (['defaultHeaderId'], [])),
    ({'columnProperties': [{}, {}]}, (['columnProperties'], [])),
])
def test_rebuild_inspects_the_opening_section_style(style, expected):
    from gdoc.api.docs import classify_markdown_rebuild

    assert classify_markdown_rebuild(_opening_section(style)) == expected


def test_rebuild_silent_on_import_default_page_setup():
    from gdoc.api.docs import classify_markdown_rebuild

    assert classify_markdown_rebuild({'documentStyle': _IMPORT_STYLE}) == ([], [])


def test_page_setup_warning_is_whole_document_only(mocker, capsys):
    from gdoc.api.docs import check_markdown_rebuild

    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    doc = _rebuild_doc()
    doc['tabs'][0]['documentTab']['documentStyle'] = {
        **_IMPORT_STYLE, 'documentFormat': {'documentMode': 'PAGELESS'}}
    check_markdown_rebuild('doc', document=doc, tab_id='notes')
    assert capsys.readouterr().err == ''
    check_markdown_rebuild('doc', document=doc)
    assert 'reset page setup' in capsys.readouterr().err


def _rebuild_doc(unsafe=False):
    native = {'body': {'content': [
        {'startIndex': 1, 'endIndex': 15, 'paragraph': {
            'elements': [{'textRun': {'content': 'Project notes\n'}}],
        }},
    ]}}
    if unsafe:
        native['namedRanges'] = {'Reference': {'namedRanges': []}}
    return {'revisionId': 'revision', 'tabs': [{
        'tabProperties': {'tabId': 'notes', 'title': 'Notes'},
        'documentTab': native,
    }]}


def test_rebuild_unsafe_tab_never_batches(mocker):
    from gdoc.api.docs import insert_markdown_into_tab

    mocker.patch(
        "gdoc.api.docs.get_document_with_tabs", return_value=_rebuild_doc(True)
    )
    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    service = mocker.patch('gdoc.api.docs.get_docs_service').return_value
    with pytest.raises(GdocError, match='namedRanges') as error:
        insert_markdown_into_tab('doc', 'Notes', 'Summary', replace=True)
    assert error.value.exit_code == 3
    service.documents.return_value.batchUpdate.assert_not_called()


def _headed_doc():
    """Single tab whose header/footer segments sit outside the body range."""
    doc = _rebuild_doc()
    tab = doc['tabs'][0]['documentTab']
    tab['headers'] = {'header': {'content': [{'paragraph': {}}]}}
    tab['footers'] = {'footer': {'content': [{'paragraph': {}}]}}
    tab['documentStyle'] = {'defaultHeaderId': 'header',
                            'defaultFooterId': 'footer'}
    return doc


def test_tab_rebuild_ignores_untouched_headers_and_footers(mocker):
    """A tab replacement deletes only the body, so segments outside it pass."""
    from gdoc.api.docs import check_markdown_rebuild

    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    check_markdown_rebuild('doc', document=_headed_doc(), tab_id='notes')


def test_rebuild_ignores_unanchored_quoted_comments(mocker):
    """`comment --quote` fallbacks carry quotedFileContent but no anchor."""
    from gdoc.api.docs import check_markdown_rebuild

    mocker.patch('gdoc.api.comments.list_comments', return_value=[
        {'id': 'c', 'quotedFileContent': {'value': 'Reference'}},
        {'id': 'd', 'anchor': ''},
    ])
    check_markdown_rebuild('doc', document=_rebuild_doc())


def _image_doc():
    doc = _rebuild_doc()
    doc['tabs'][0]['documentTab']['inlineObjects'] = {'kix.img': {
        'inlineObjectProperties': {'embeddedObject': {'imageProperties': {
            'contentUri': 'https://lh3.googleusercontent.com/img'}}}}}
    return doc


def test_tab_rebuild_blocks_images(mocker):
    """parse_markdown emits no images, so a tab replacement would drop them."""
    from gdoc.api.docs import check_markdown_rebuild

    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    with pytest.raises(GdocError, match='inlineObjects') as error:
        check_markdown_rebuild('doc', document=_image_doc(), tab_id='notes')
    assert error.value.exit_code == 3


def test_whole_document_rebuild_blocks_images_too(mocker):
    """Nothing proves Drive's import keeps images, so deny by default."""
    from gdoc.api.docs import check_markdown_rebuild

    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    with pytest.raises(GdocError, match='inlineObjects'):
        check_markdown_rebuild('doc', document=_image_doc())


def test_whole_document_rebuild_still_blocks_headers_and_footers(mocker):
    from gdoc.api.docs import check_markdown_rebuild

    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    with pytest.raises(GdocError, match='defaultFooterId.*footers.*headers') as error:
        check_markdown_rebuild('doc', document=_headed_doc())
    assert error.value.exit_code == 3


@pytest.mark.parametrize('allow_lossy', [False, True])
def test_rebuild_exact_tab_batch(mocker, allow_lossy):
    from gdoc.api.docs import insert_markdown_into_tab

    mocker.patch('gdoc.api.docs.get_document_with_tabs',
                 return_value=_rebuild_doc(allow_lossy))
    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    service = mocker.patch('gdoc.api.docs.get_docs_service').return_value
    insert_markdown_into_tab('doc', 'Notes', 'Summary', replace=True,
                             allow_lossy_rebuild=allow_lossy)
    service.documents.return_value.batchUpdate.assert_called_once_with(
        documentId='doc', body={
            'requests': [
                {'deleteContentRange': {'range': {
                    'startIndex': 1, 'endIndex': 14, 'tabId': 'notes'}}},
                {'insertText': {'location': {'index': 1, 'tabId': 'notes'},
                                'text': 'Summary'}},
                {'updateParagraphStyle': {
                    'range': {'startIndex': 1, 'endIndex': 8, 'tabId': 'notes'},
                    'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'},
                    'fields': 'namedStyleType'}},
            ],
            'writeControl': {'requiredRevisionId': 'revision'},
        },
    )


@pytest.mark.parametrize('anchor', [{'anchor': 'kix.xhdvo21465'},
                                  {'anchor': '{"region":"reference"}',
                                   'quotedFileContent': {'value': 'Reference'}}])
def test_rebuild_protects_comment_anchors(mocker, anchor):
    from gdoc.api.docs import check_markdown_rebuild

    comments = mocker.patch('gdoc.api.comments.list_comments', return_value=[anchor])
    with pytest.raises(GdocError, match='comment anchors') as error:
        check_markdown_rebuild('doc', document=_rebuild_doc())
    assert error.value.exit_code == 3
    comments.assert_called_once_with('doc', include_anchor=True)


def test_rebuild_tab_scope_excludes_unsafe_sibling_and_child(mocker):
    from gdoc.api.docs import check_markdown_rebuild

    doc = _rebuild_doc()
    unsafe = {'tabProperties': {'tabId': 'other', 'title': 'Other'},
              'documentTab': {'footnotes': {'note': {}}}}
    doc['tabs'][0]['childTabs'] = [unsafe]
    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    check_markdown_rebuild('doc', document=doc, tab_id='notes')
    with pytest.raises(GdocError, match='footnotes'):
        check_markdown_rebuild('doc', document=doc, tab_id='other')
    with pytest.raises(GdocError, match='multiple tabs'):
        check_markdown_rebuild('doc', document=doc, allow_lossy_rebuild=True)
    with pytest.raises(GdocError, match='footnotes'):
        check_markdown_rebuild('doc', document=doc, force_collapse_tabs=True)
    check_markdown_rebuild('doc', document=doc, force_collapse_tabs=True,
                           allow_lossy_rebuild=True)


def test_rebuild_styles_emit_one_warning(mocker, capsys):
    from gdoc.api.docs import check_markdown_rebuild

    mocker.patch('gdoc.api.comments.list_comments', return_value=[])
    check_markdown_rebuild('doc', document={
        'paragraphStyle': {'namedStyleType': 'HEADING_1', 'alignment': 'END'},
        'bullet': {'listId': 'list'},
        'textStyle': {'foregroundColor': {}, 'backgroundColor': {}},
    })
    assert capsys.readouterr().err == (
        'WARN: Markdown rebuild will rebuild: alignment, colour, highlight\n'
    )
