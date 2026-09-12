"""Synthetic target-style regressions; all Docs transport is mocked."""

from copy import deepcopy

import pytest

from gdoc.api.docs import find_text_in_document, replace_formatted, suggest_replacement
from gdoc.mdparse import utf16_len

RED = {"foregroundColor": {"color": {"rgbColor": {"red": 0.7}}},
       "underline": False}
LINK = {"link": {"url": "https://example.test/old"}, **RED}


def _body(*runs, cell=False):
    elements = []
    index = 1
    for text, style in runs:
        end = index + utf16_len(text)
        elements.append({"startIndex": index, "endIndex": end,
                         "textRun": {"content": text, "textStyle": style}})
        index = end
    body = {"content": [{"startIndex": 1, "endIndex": index,
                         "paragraph": {"elements": elements}}]}
    if cell:
        return {"content": [{"table": {"tableRows": [{"tableCells": [body]}]}}]}
    return body


def _batch(mocker, body, old, new, command="edit", **kwargs):
    original = deepcopy(body)
    chain = mocker.patch("gdoc.api.docs.get_docs_service").return_value.documents()
    matches = find_text_in_document(None, old, body=body)
    assert len(matches) == 1
    if command == "suggest":
        mocker.patch("gdoc.api.docs.check_suggest_preview_access")
        mocker.patch("gdoc.api.docs._token_identity", return_value=("client", "token"))
        chain.batchUpdate.return_value.execute.return_value = {
            "commentUpdateState": "ALL_SAVED",
            "suggestionResponses": [{"createdSuggestionIds": ["synthetic"]}],
        }
        mocker.patch("gdoc.api.docs.get_document_structure", return_value={
            "body": {"content": [{"paragraph": {"elements": [{"textRun": {
                "content": "replacement", "suggestedInsertionIds": ["synthetic"],
            }}]}}]},
        })
        suggest_replacement("doc", matches, new, "revision", tab_id="tab",
                            body=body)
    else:
        replace_formatted("doc", matches, new, "revision", tab_id="tab",
                          body=body, **kwargs)
    chain.batchUpdate.assert_called_once()
    batch = chain.batchUpdate.call_args.kwargs["body"]
    assert batch["writeControl"] == {
        "requiredRevisionId": "revision",
        **({"writeMode": "SUGGEST"} if command == "suggest" else {}),
    }
    assert body == original
    return batch["requests"]


def _replacement_styles(requests, inherited):
    """Apply named-field masks to inserted UTF-16 units, including link resets.

    This models the request contract, not Google's suggestion backend.
    Reject out-of-insertion style ranges so original/neighbor runs stay intact.
    """
    insert = next(r["insertText"] for r in requests if "insertText" in r)
    start = insert["location"]["index"]
    styles = [deepcopy(inherited) for _ in range(utf16_len(insert["text"]))]
    for request in requests:
        if "updateTextStyle" not in request:
            continue
        update = request["updateTextStyle"]
        lo, hi = (update["range"][key] - start for key in ("startIndex", "endIndex"))
        assert 0 <= lo < hi <= len(styles)
        assert update["range"]["tabId"] == "tab"
        for style in styles[lo:hi]:
            fields = update["fields"].split(",")
            if "link" in fields and "link" in update["textStyle"]:
                style.update({"underline": True, "foregroundColor": "link-default"})
            for field in fields:
                if field in update["textStyle"]:
                    style[field] = deepcopy(update["textStyle"][field])
                else:
                    style.pop(field, None)
    return styles


@pytest.mark.parametrize("command", ["edit", "suggest"])
@pytest.mark.parametrize("neighbour", [{"bold": True}, {"underline": True}])
@pytest.mark.parametrize("target", [{}, RED])
def test_target_overrides_neighbour(mocker, command, neighbour, target):
    body = _body(("Left ", neighbour), ("TOKEN", target), (" right\n", {}))
    requests = _batch(mocker, body, "TOKEN", "R🌿", command)
    assert _replacement_styles(requests, neighbour) == [target] * 3


@pytest.mark.parametrize("command", ["edit", "suggest"])
def test_mixed_retained_phrase_preserves_colour_and_plain_suffix(mocker, command):
    body = _body(("Prefix ", {"bold": True}), ("Red label", LINK),
                 (" plus ordinary words.\n", {}))
    replacement = "[Red label](https://example.test/new) plus ordinary words."
    requests = _batch(mocker, body, "Red label plus ordinary words.",
                      replacement, command)
    styles = _replacement_styles(requests, {"bold": True})
    assert styles[:9] == [{**RED, "link": {"url": "https://example.test/new"}}] * 9
    assert styles[9:] == [{}] * len(" plus ordinary words.")


@pytest.mark.parametrize("command", ["edit", "suggest"])
@pytest.mark.parametrize("cell", [False, True])
def test_unrelated_plain_replacement_removes_stale_link(mocker, command, cell):
    body = _body(("Obsolete value", LINK), ("\n", LINK), cell=cell)
    requests = _batch(mocker, body, "Obsolete value", "Confirmed", command,
                      replace_paragraphs=cell)
    assert _replacement_styles(requests, LINK) == [RED] * len("Confirmed")


@pytest.mark.parametrize("command", ["edit", "suggest"])
def test_mixed_unmappable_replacement_uses_dominant_styled_target(mocker, command):
    body = _body(("L ", {"bold": True}), ("red label", LINK),
                 (" short", {"italic": True}), (" plain suffix\n", {}))
    requests = _batch(mocker, body, "red label short plain suffix", "Revised", command)
    assert _replacement_styles(requests, {"bold": True}) == [RED] * len("Revised")


@pytest.mark.parametrize("command", ["edit", "suggest"])
@pytest.mark.parametrize("style", [{}, {"bold": True}, RED])
def test_same_style_wording_needs_no_style_requests(mocker, command, style):
    body = _body(("A TOKEN Z\n", style))
    requests = _batch(mocker, body, "TOKEN", "Revised", command)
    assert [next(iter(r)) for r in requests] == ["deleteContentRange", "insertText"]
