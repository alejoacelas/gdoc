"""`gdoc write --tab` into a tab whose terminal paragraph carries a bullet.

Docs keeps a tab's final newline when the body is replaced, so the paragraph that owns
it survives `deleteContentRange` with its `bullet` and indents; the inserted markdown
ends inside that paragraph and every new paragraph inherits the list. Seen on a tab
edited in the Docs UI (a list typed last leaves its bullet on the terminal paragraph);
gdoc's own list output never does, which is why a gdoc-seeded tab does not reproduce.

Live record: fidelity-tests/repros.md#write-v01-write-tab-inherits-terminal-bullet and
fidelity-tests/write/v01/runs/20260904-rewrite-tab-after-ui-bullet. Issue:
https://github.com/LucaDeLeo/gdoc/issues/59.

A fix must clear the bullet (and the list indents) on the surviving terminal paragraph
before the new text lands, or otherwise keep the new paragraphs out of that list. The
first test fails until then; the second pins that a plain tab gets no extra requests.
"""
from unittest.mock import MagicMock, patch


def _capture_batch_updates(mock_svc):
    captured = []

    def batch_update(documentId, body):
        captured.append(body)
        return MagicMock()

    mock_svc.return_value.documents.return_value.batchUpdate.side_effect = batch_update
    return captured


def _para(start, end, text, bullet=None, indents=False, style="NORMAL_TEXT"):
    p = {
        "elements": [{"startIndex": start, "endIndex": end,
                      "textRun": {"content": text, "textStyle": {}}}],
        "paragraphStyle": {"namedStyleType": style},
    }
    if indents:
        p["paragraphStyle"].update({
            "indentFirstLine": {"magnitude": 18, "unit": "PT"},
            "indentStart": {"magnitude": 36, "unit": "PT"},
        })
    if bullet:
        p["bullet"] = {"listId": bullet, "textStyle": {}}
    return {"startIndex": start, "endIndex": end, "paragraph": p}


def _tabs_doc(body_content):
    return {
        "revisionId": "rev-1",
        "tabs": [{
            "tabProperties": {"tabId": "t.repro", "title": "Repro", "index": 1},
            "documentTab": {"body": {"content": body_content}},
        }],
    }


# The gdt-write-v01 fixture, as captured: heading, prose, two items, and an EMPTY
# terminal paragraph that is itself a list item (indices from baseline/structure.json).
UI_BULLETED_TAIL = [
    _para(1, 6, "Seed\n", style="HEADING_1"),
    _para(6, 34, "Placeholder paragraph one.\n"),
    _para(34, 45, "alpha item\n", bullet="kix.list", indents=True),
    _para(45, 55, "beta item\n", bullet="kix.list", indents=True),
    _para(55, 56, "\n", bullet="kix.list", indents=True),
]

PLAIN_TAIL = [
    _para(1, 6, "Seed\n", style="HEADING_1"),
    _para(6, 17, "alpha item\n", bullet="kix.list", indents=True),
    _para(17, 18, "\n"),
]

MARKDOWN = "# Rewritten heading\n\nPlain paragraph.\n\n* first\n* second\n\nClosing.\n"


def _bullet_clearing_requests(reqs):
    """Requests that remove list membership from a range in the Repro tab."""
    return [r for r in reqs if "deleteParagraphBullets" in r
            and r["deleteParagraphBullets"]["range"].get("tabId") == "t.repro"]


class TestReplaceTabWithBulletedTerminalParagraph:
    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_replace_clears_bullet_on_surviving_paragraph(self, mock_get, mock_svc):
        """Fails today: no request touches the terminal paragraph's bullet, so the
        rewritten tab comes back with every paragraph as a list item."""
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = _tabs_doc(UI_BULLETED_TAIL)
        captured = _capture_batch_updates(mock_svc)

        insert_markdown_into_tab("doc1", "Repro", MARKDOWN, replace=True)

        assert captured, "batchUpdate not called"
        reqs = captured[0]["requests"]
        delete_idx = next(i for i, r in enumerate(reqs) if "deleteContentRange" in r)
        insert_idx = next(i for i, r in enumerate(reqs) if "insertText" in r)
        clearing = _bullet_clearing_requests(reqs)
        assert clearing, (
            "expected a deleteParagraphBullets over the surviving terminal paragraph "
            "(index 1 after the delete, or 55–56 before it); the markdown's own "
            "createParagraphBullets for `first`/`second` are not it"
        )
        clear_idx = reqs.index(clearing[0])
        assert delete_idx < clear_idx < insert_idx or clear_idx < delete_idx, (
            "the bullet must be cleared before the new text is inserted into that paragraph"
        )
        rng = clearing[0]["deleteParagraphBullets"]["range"]
        assert rng["startIndex"] <= 1 < rng["endIndex"] or (
            rng["startIndex"] <= 55 and rng["endIndex"] >= 56
        ), f"clearing range {rng} does not cover the terminal paragraph"

    @patch("gdoc.api.docs.get_docs_service")
    @patch("gdoc.api.docs.get_document_with_tabs")
    def test_replace_plain_terminal_paragraph_adds_no_clearing(self, mock_get, mock_svc):
        """Passing counterpart: a tab whose terminal paragraph is plain (every tab gdoc
        itself wrote) needs no bullet clearing; the fix must not add requests here."""
        from gdoc.api.docs import insert_markdown_into_tab

        mock_get.return_value = _tabs_doc(PLAIN_TAIL)
        captured = _capture_batch_updates(mock_svc)

        insert_markdown_into_tab("doc1", "Repro", MARKDOWN, replace=True)

        reqs = captured[0]["requests"]
        clearing = _bullet_clearing_requests(reqs)
        # createParagraphBullets for the markdown list is allowed; deleteParagraphBullets is not
        assert clearing == []
        assert any("deleteContentRange" in r for r in reqs)
