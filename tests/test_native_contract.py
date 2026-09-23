"""Synthetic request-level checks for native Markdown replacement."""

from gdoc.api.docs import (
    _code_range_requests,
    _strip_trailing_newline_unless_hr,
    _table_cell_requests,
    insert_markdown_into_tab,
    replace_formatted,
)
from gdoc.mdparse import parse_markdown


def snapshot():
    return {"revisionId": "before", "tabs": [{
        "tabProperties": {"tabId": "tab-one", "title": "Notes"},
        "documentTab": {"body": {"content": [{
            "startIndex": 1, "endIndex": 5, "paragraph": {
                "elements": [{"startIndex": 1, "endIndex": 5,
                              "textRun": {"content": "Old\n"}}],
            },
        }]}},
    }]}


def service(mocker):
    chain = mocker.patch("gdoc.api.docs.get_docs_service").return_value.documents.return_value
    chain.batchUpdate.return_value.execute.return_value = {
        "writeControl": {"requiredRevisionId": "after"},
    }
    return chain


def test_targeted_revision_is_from_acknowledgment(mocker):
    service(mocker)
    details = {}
    result = replace_formatted("doc", [{"startIndex": 1, "endIndex": 4}],
                               "New", "before", result_details=details)
    assert result == 1
    assert (details["input_revision_id"], details["acknowledged_revision_id"],
            details["rebased"]) == ("before", "after", False)


def test_general_split_and_reorder_are_native(mocker):
    chain = service(mocker)
    result = insert_markdown_into_tab("doc", "Notes", "## Moved\n\nSplit\n\nApart",
                                      replace=True, document=snapshot())
    batch = chain.batchUpdate.call_args.kwargs["body"]
    assert batch["writeControl"] == {"requiredRevisionId": "before"}
    assert [r["insertText"]["text"] for r in batch["requests"] if "insertText" in r] == [
        "Moved\n\nSplit\n\nApart",
    ]
    assert result["input_revision_id"] == "before"
    assert result["acknowledged_revision_id"] == "after"
    assert result["rebased"] is False


def test_table_alignment_and_explicit_emphasis_only():
    table = parse_markdown("| Plain | **Bold** |\n| :--- | ---: |\n| a | b |").tables[0]
    requests = _table_cell_requests([[5, 7], [11, 13]], table, "tab-one")
    styles = [r["updateTextStyle"] for r in requests if "updateTextStyle" in r]
    assert len(styles) == 1
    assert styles[0]["range"] == {"startIndex": 12, "endIndex": 16, "tabId": "tab-one"}
    alignments = [r["updateParagraphStyle"]["paragraphStyle"]["alignment"]
                  for r in requests if "updateParagraphStyle" in r]
    assert alignments == ["START", "END", "START", "END"]


def test_code_markers_include_final_mark_and_ignore_code_tabs():
    parsed = parse_markdown("- parent\n  - child\n\n```\n\tliteral 😀\n```")
    _strip_trailing_newline_unless_hr(parsed)
    requests = _code_range_requests(parsed, 1, "tab-one")
    assert requests == [{"createNamedRange": {"name": "gdoc:code:v1", "range": {
        "startIndex": 15, "endIndex": 27, "tabId": "tab-one",
    }}}]


def test_non_default_start_is_explicit_best_effort(mocker, capsys):
    chain = service(mocker)
    insert_markdown_into_tab("doc", "Notes", "7. Seven", replace=True,
                             document=snapshot())
    assert "will start at 1" in capsys.readouterr().err
    assert any("createParagraphBullets" in r for r in
               chain.batchUpdate.call_args.kwargs["body"]["requests"])


def test_multi_tab_default_preserves_siblings_and_uses_native_revision(mocker):
    from copy import deepcopy

    from gdoc.api.drive import update_doc_content

    document = snapshot()
    sibling = deepcopy(document["tabs"][0])
    sibling["tabProperties"] = {"tabId": "sibling", "title": "Other"}
    document["tabs"].append(sibling)
    chain = service(mocker)
    drive = mocker.patch("gdoc.api.drive.get_drive_service")
    mocker.patch("gdoc.api.drive.require_write_version")
    mocker.patch("gdoc.api.drive.get_file_version", return_value={"version": 99})
    details = {}
    assert update_doc_content("doc", "New", document=document, expected_version=1,
                              result_details=details) == 99
    drive.assert_not_called()
    chain.batchUpdate.assert_called_once()
    assert details["acknowledged_revision_id"] == "after"
    assert not any("deleteTab" in r for r in
                   chain.batchUpdate.call_args.kwargs["body"]["requests"])


def test_authorized_collapse_pins_sibling_deletion_to_ack(mocker):
    from copy import deepcopy

    from gdoc.api.drive import update_doc_content

    document = snapshot()
    sibling = deepcopy(document["tabs"][0])
    sibling["tabProperties"] = {"tabId": "sibling", "title": "Other"}
    document["tabs"].append(sibling)
    chain = service(mocker)
    chain.batchUpdate.return_value.execute.side_effect = [
        {"writeControl": {"requiredRevisionId": "after"}},
        {"writeControl": {"requiredRevisionId": "collapsed"}},
    ]
    mocker.patch("gdoc.api.drive.require_write_version")
    mocker.patch("gdoc.api.drive.get_file_version", return_value={"version": 99})
    details = {}
    update_doc_content("doc", "New", document=document, expected_version=1,
                       collapse_tabs=True, result_details=details)
    assert chain.batchUpdate.call_args.kwargs["body"] == {
        "requests": [{"deleteTab": {"tabId": "sibling"}}],
        "writeControl": {"requiredRevisionId": "after"},
    }
    assert details["acknowledged_revision_id"] == "collapsed"
