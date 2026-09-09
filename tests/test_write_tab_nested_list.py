"""`gdoc write --tab` with a nested Markdown list must nest in the Doc.

The Docs API sets a paragraph's bullet nesting level from its leading tabs
relative to the shallowest paragraph in the createParagraphBullets range. A
request per paragraph therefore flattened every child to level 0 (and the
child under a numbered parent became its own list). These tests pin the shape
the tab-write path must send: the child's tab is in the inserted text and one
bullet request covers the whole block.

Live record: written to a test tab, `gdoc structure --tab` then reports the
child with ``nestingLevel: 1`` in the parent's ``listId``.
"""
from unittest.mock import MagicMock, patch

MARKDOWN = "## Two spaces\n- parent two\n  - child two [x](https://example.com)\n"


def _capture_batch_updates(mock_svc):
    captured = []

    def batch_update(**kwargs):
        captured.append(kwargs["body"])
        return MagicMock()

    mock_svc.return_value.documents.return_value.batchUpdate.side_effect = batch_update
    return captured


def _tabs_doc():
    return {
        "revisionId": "rev-1",
        "tabs": [{
            "tabProperties": {"tabId": "t.dev", "title": "Developments", "index": 1},
            "documentTab": {"body": {"content": [{
                "startIndex": 1, "endIndex": 6,
                "paragraph": {
                    "elements": [{"startIndex": 1, "endIndex": 6,
                                  "textRun": {"content": "Seed\n", "textStyle": {}}}],
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                },
            }]}},
        }],
    }


def _bullets(reqs):
    return [r["createParagraphBullets"] for r in reqs if "createParagraphBullets" in r]


class TestNestedListOnTabWrite:
    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_child_keeps_tab_and_shares_parent_bullet_range(self, mock_get, mock_svc):
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = _tabs_doc()
        captured = _capture_batch_updates(mock_svc)

        insert_markdown_into_tab("doc1", "Developments", MARKDOWN, replace=True)

        reqs = captured[0]["requests"]
        insert = next(r["insertText"] for r in reqs if "insertText" in r)
        # The child's nesting tab is still in the text the API receives.
        assert insert["text"] == "Two spaces\nparent two\n\tchild two x\n"
        assert insert["location"] == {"index": 1, "tabId": "t.dev"}

        bullets = _bullets(reqs)
        assert len(bullets) == 1, "parent and child must share one request"
        # "Two spaces\n" is 11 chars from index 1, so the list starts at 12 and
        # runs to the end of the inserted text: 12 + len("parent two\n\tchild two x\n").
        assert bullets[0]["range"] == {
            "startIndex": 12, "endIndex": 36, "tabId": "t.dev",
        }
        assert bullets[0]["bulletPreset"] == "BULLET_DISC_CIRCLE_SQUARE"
        # The bullet request comes after every text/paragraph style request.
        last_style = max(i for i, r in enumerate(reqs)
                         if "updateTextStyle" in r or "updateParagraphStyle" in r)
        assert reqs.index({"createParagraphBullets": bullets[0]}) > last_style

    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_bullet_child_under_numbered_parent_is_one_numbered_range(
        self, mock_get, mock_svc,
    ):
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = _tabs_doc()
        captured = _capture_batch_updates(mock_svc)

        insert_markdown_into_tab(
            "doc1", "Developments", "1. parent num\n    - child num\n", replace=True,
        )

        bullets = _bullets(captured[0]["requests"])
        assert len(bullets) == 1
        assert bullets[0]["bulletPreset"] == "NUMBERED_DECIMAL_ALPHA_ROMAN"
        # "parent num\n" (11) + "\t\tchild num\n" (12) from index 1.
        assert bullets[0]["range"] == {
            "startIndex": 1, "endIndex": 24, "tabId": "t.dev",
        }
