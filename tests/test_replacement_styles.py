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


def _units(*runs):
    result = []
    for text, style in runs:
        raw = text.encode("utf-16-le")
        result.extend((raw[i:i + 2], deepcopy(style)) for i in range(0, len(raw), 2))
    return result


def _project_suggestion(runs, requests, view):
    """Small offline contract model: pending deletions retain their old style.

    Only inserted units may be restyled by this batch. This checks our ranges
    and projections, but cannot establish the preview server's behavior.
    """
    units = [(char, style, "original") for char, style in _units(*runs)]
    for request in requests:
        if "deleteContentRange" in request:
            span = request["deleteContentRange"]["range"]
            lo, hi = span["startIndex"] - 1, span["endIndex"] - 1
            units[lo:hi] = [(char, style, "deleted") for char, style, _ in units[lo:hi]]
        elif "insertText" in request:
            insert = request["insertText"]
            pos = insert["location"]["index"] - 1
            inherited = units[pos - 1][1] if pos else units[pos][1]
            units[pos:pos] = [(char, style, "inserted")
                              for char, style in _units((insert["text"], inherited))]
        elif "updateTextStyle" in request:
            update = request["updateTextStyle"]
            lo = update["range"]["startIndex"] - 1
            hi = update["range"]["endIndex"] - 1
            for _, style, status in units[lo:hi]:
                assert status == "inserted", "style request touched pre-existing text"
                for field in update["fields"].split(","):
                    if field in update["textStyle"]:
                        style[field] = deepcopy(update["textStyle"][field])
                    else:
                        style.pop(field, None)
    hidden = {"pending": None, "accepted": "deleted", "rejected": "inserted"}[view]
    return [(char, style) for char, style, status in units if status != hidden]


@pytest.mark.parametrize("view", ["pending", "accepted", "rejected"])
@pytest.mark.parametrize("target", [{}, {"italic": True, **RED}])
def test_suggestion_projection_contract_preserves_target_and_neighbours(
    mocker, view, target,
):
    left = ("Bold 🌿 ", {"bold": True, "underline": True})
    old = ("TOKEN", target)
    right = (" right\n", {"strikethrough": True})
    runs = (left, old, right)
    requests = _batch(mocker, _body(*runs), "TOKEN", "R🌿", "suggest")
    new = ("R🌿", target)
    expected = {"pending": (left, new, old, right),
                "accepted": (left, new, right), "rejected": runs}
    assert _project_suggestion(runs, requests, view) == _units(*expected[view])


@pytest.mark.parametrize("command", ["edit", "suggest"])
def test_link_only_follows_retained_label_with_utf16_offsets(mocker, command):
    body = _body(("Left ", {}), ("Label🌿", LINK), (" right\n", {}))
    requests = _batch(mocker, body, "Label🌿", "🌿 New Label🌿 suffix", command)
    styles = _replacement_styles(requests, {})
    assert styles[:7] == [RED] * 7
    assert styles[7:14] == [LINK] * 7
    assert styles[14:] == [RED] * len(" suffix")


@pytest.mark.parametrize("command", ["edit", "suggest"])
def test_explicit_emphasis_wins_after_target_baseline(mocker, command):
    body = _body(("Left ", {"bold": True}), ("TOKEN", RED), (" right\n", {}))
    requests = _batch(mocker, body, "TOKEN", "**R🌿**", command)
    assert _replacement_styles(requests, {"bold": True}) == [{**RED, "bold": True}] * 3


@pytest.mark.parametrize("command", ["edit", "suggest"])
def test_same_colour_neighbour_does_not_hide_markdown_link_reset(mocker, command):
    body = _body(("A TOKEN Z\n", RED))
    requests = _batch(mocker, body, "TOKEN", "[Revised](https://example.test/new)",
                      command)
    assert _replacement_styles(requests, RED) == [
        {**RED, "link": {"url": "https://example.test/new"}},
    ] * len("Revised")


def test_collapsing_cell_removes_link_but_preserves_target_colour(mocker):
    first = _body(("Old", LINK), ("\n", LINK))
    second = _body(("Value", LINK), ("\n", LINK))
    for element in second["content"]:
        element["startIndex"] += 4
        element["endIndex"] += 4
        for run in element["paragraph"]["elements"]:
            run["startIndex"] += 4
            run["endIndex"] += 4
    cell = {"content": first["content"] + second["content"]}
    body = {"content": [{"table": {"tableRows": [{"tableCells": [cell]}]}}]}
    requests = _batch(mocker, body, "Old\nValue", "Confirmed", replace_paragraphs=True)
    assert _replacement_styles(requests, LINK) == [RED] * len("Confirmed")


@pytest.mark.parametrize("command", ["edit", "suggest"])
def test_duplicate_retained_label_does_not_guess_which_link_to_restore(mocker, command):
    body = _body(("A ", {}), ("Label", LINK), (" Z\n", {}))
    requests = _batch(mocker, body, "Label", "Label and Label", command)
    assert _replacement_styles(requests, {}) == [RED] * len("Label and Label")


@pytest.mark.parametrize("command", ["edit", "suggest"])
def test_fenced_inline_text_uses_target_style_before_explicit_code_font(
    mocker, command,
):
    body = _body(("A ", {"bold": True}), ("TOKEN", RED), (" Z\n", {}))
    requests = _batch(mocker, body, "TOKEN", "```\nRevised\n```", command)
    assert _replacement_styles(requests, {"bold": True}) == [{
        **RED, "weightedFontFamily": {"fontFamily": "Courier New"},
    }] * len("Revised")


def test_cell_list_reset_precedes_target_style_restoration(mocker):
    body = _body(("Old value", LINK), ("\n", LINK))
    paragraph = body["content"][0]["paragraph"]
    paragraph["bullet"] = {"listId": "synthetic-list"}
    body = {"content": [{"table": {"tableRows": [{"tableCells": [body]}]}}]}
    requests = _batch(mocker, body, "Old value", "Confirmed", replace_paragraphs=True)
    kinds = [next(iter(request)) for request in requests]
    assert kinds.index("updateParagraphStyle") < kinds.index("updateTextStyle")
    baseline = requests[kinds.index("updateTextStyle")]["updateTextStyle"]
    assert baseline["textStyle"] == RED
    assert baseline["fields"] == "foregroundColor,link,underline"
    assert _replacement_styles(requests, LINK) == [RED] * len("Confirmed")
