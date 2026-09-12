"""Offline fault injection for revision-pinned multi-batch writes."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

import httplib2
import pytest
from googleapiclient.errors import HttpError

from gdoc.api.docs import insert_markdown_into_tab, replace_formatted
from gdoc.api.drive import update_doc_content
from gdoc.cli import cmd_push, cmd_write, run_argv
from gdoc.mdparse import utf16_len
from gdoc.notify import ChangeInfo
from gdoc.util import GdocError

MARKDOWN = "Intro\n| Header |\n|---|\n| Value |"


def response(revision):
    return {"writeControl": {"requiredRevisionId": revision}}


def http_error(status=400, message="required revision does not match"):
    return HttpError(
        httplib2.Response({"status": str(status)}),
        ('{"error":{"message":"' + message + '"}}').encode(),
    )


def paragraph(text, start):
    end = start + utf16_len(text)
    return {
        "startIndex": start,
        "endIndex": end,
        "paragraph": {
            "elements": [
                {"startIndex": start, "endIndex": end, "textRun": {"content": text}}
            ],
        },
    }


def snapshot(revision="r1", prefix="Old\n", table=False):
    content = [paragraph(prefix, 1)] if prefix else []
    index = 1 + utf16_len(prefix)
    if table:
        content.append(paragraph("\n", index))
        start = index + 1
        rows = []
        for row in range(2):
            cell_start = start + 2 + 3 * row
            rows.append(
                {
                    "tableCells": [
                        {
                            "startIndex": cell_start,
                            "endIndex": cell_start + 2,
                            "content": [paragraph("\n", cell_start + 1)],
                        }
                    ]
                }
            )
        end = start + 8
        content.append(
            {"startIndex": start, "endIndex": end, "table": {"tableRows": rows}}
        )
        content.append(paragraph("\n", end))
    else:
        content.append(paragraph("\n", index))
    return {
        "revisionId": revision,
        "tabs": [
            {
                "tabProperties": {"tabId": "t1", "title": "Notes"},
                "documentTab": {"body": {"content": content}},
            }
        ],
    }


def body(doc):
    return doc["tabs"][0]["documentTab"]["body"]


@pytest.fixture
def api(mocker):
    service = MagicMock()
    docs = service.documents.return_value
    mocker.patch("gdoc.api.docs.get_docs_service", return_value=service)
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value=snapshot())
    docs.batchUpdate.return_value.execute.side_effect = [
        response("r2"),
        response("r3"),
        response("r4"),
    ]
    docs.get.return_value.execute.return_value = snapshot("r3", "Intro\n", table=True)
    return docs


def batches(api):
    return [c.kwargs["body"] for c in api.batchUpdate.call_args_list]


def write():
    return insert_markdown_into_tab("synthetic", "Notes", MARKDOWN, replace=True)


def test_all_table_stages_use_their_own_revision(api):
    write()
    assert [b["writeControl"] for b in batches(api)] == [
        {"requiredRevisionId": r} for r in ("r1", "r2", "r3")
    ]
    assert "insertTable" in batches(api)[1]["requests"][0]
    assert {
        r["insertText"]["text"]
        for r in batches(api)[2]["requests"]
        if "insertText" in r
    } == {"Header", "Value"}


def test_replacement_table_uses_response_revision(api):
    replace_formatted(
        "synthetic", [{"startIndex": 1, "endIndex": 4}], MARKDOWN, "r1", tab_id="t1"
    )
    assert [b["writeControl"]["requiredRevisionId"] for b in batches(api)] == [
        "r1",
        "r2",
        "r3",
    ]


def test_table_only_empty_tab_pins_the_first_table_batch(api, mocker):
    mocker.patch(
        "gdoc.api.docs.get_document_with_tabs", return_value=snapshot(prefix="")
    )
    api.batchUpdate.return_value.execute.side_effect = [response("r2"), response("r3")]
    api.get.return_value.execute.return_value = snapshot("r2", "", table=True)
    insert_markdown_into_tab(
        "synthetic", "Notes", "| A |\n|---|\n| B |", position="end"
    )
    assert "insertTable" in batches(api)[0]["requests"][0]
    assert [b["writeControl"]["requiredRevisionId"] for b in batches(api)] == [
        "r1",
        "r2",
    ]


@pytest.mark.parametrize("stage", [0, 1, 2])
@pytest.mark.parametrize("failure", ["before_send", "after_apply"])
def test_faults_do_not_replay_acknowledged_or_uncertain_mutations(api, stage, failure):
    applied = []
    count = 0

    def batch_update(**kwargs):
        nonlocal count
        current = count
        count += 1
        if current == stage and failure == "before_send":
            raise OSError("request construction failed")

        def execute():
            applied.append(current)
            if current == stage:
                raise OSError("response lost after server applied write")
            return response(f"r{current + 2}")

        return SimpleNamespace(execute=execute)

    api.batchUpdate.side_effect = batch_update
    with pytest.raises(GdocError) as caught:
        write()
    assert caught.value.exit_code == 1
    message = str(caught.value)
    assert ("Partial completion" if stage else "Write failed") in message
    assert (
        "completion uncertain" if failure == "after_apply" else "not applied"
    ) in message
    assert "remaining stages not attempted" in message
    assert applied == list(range(stage + (failure == "after_apply")))
    assert count == stage + 1
    if stage:
        assert "applied: tab text and formatting applied" in message
    if stage == 2:
        assert "table structure inserted" in message


def test_readback_failure_reports_applied_table_without_claiming_cells(api):
    api.get.return_value.execute.side_effect = OSError("read disconnected")
    with pytest.raises(GdocError, match="Partial completion") as caught:
        write()
    assert caught.value.exit_code == 1
    assert "table structure inserted" in str(caught.value)
    assert "reading inserted table cells: not applied" in str(caught.value)
    assert len(batches(api)) == 2


def test_missing_response_revision_refuses_unpinned_followup(api):
    api.batchUpdate.return_value.execute.side_effect = [{}]
    with pytest.raises(GdocError, match="missing revision") as caught:
        write()
    assert caught.value.exit_code == 3
    assert len(batches(api)) == 1


def test_interleaved_editor_before_table_rejects_then_recomputes_utf16_index(api):
    live_revision = "r1"
    sent_indices = []
    applied = []

    def execute():
        nonlocal live_revision
        batch = batches(api)[-1]
        required = batch["writeControl"]["requiredRevisionId"]
        if "insertTable" in batch["requests"][0]:
            sent_indices.append(
                batch["requests"][0]["insertTable"]["location"]["index"]
            )
        if required != live_revision:
            raise http_error()
        applied.append(batch)
        if len(applied) == 1:
            # Our main batch applies as r2; another editor then prepends text.
            live_revision = "editor"
            return response("r2")
        live_revision = f"r{len(applied) + 2}"
        return response(live_revision)

    api.batchUpdate.return_value.execute.side_effect = execute
    api.get.return_value.execute.side_effect = [
        snapshot("editor", "🙂 Added\nIntro\n"),
        snapshot("r4", "🙂 Added\nIntro\n", table=True),
    ]
    write()
    assert sent_indices == [7, 16]
    assert [b["writeControl"]["requiredRevisionId"] for b in batches(api)] == [
        "r1",
        "r2",
        "editor",
        "r4",
    ]
    assert len(applied) == 3
    assert api.get.call_count == 2


@pytest.mark.parametrize("prefix", ["Intro\n\nIntro\n", "Changed\n", "Intro\nAdded"])
def test_ambiguous_or_changed_insertion_anchor_refuses_after_one_read(api, prefix):
    api.batchUpdate.return_value.execute.side_effect = [response("r2"), http_error()]
    api.get.return_value.execute.return_value = snapshot("editor", prefix)
    with pytest.raises(GdocError, match="cannot uniquely relocate") as caught:
        write()
    assert caught.value.exit_code == 3
    assert len(batches(api)) == 2
    assert api.get.call_count == 1


def test_table_only_conflict_is_not_guessed(api):
    api.batchUpdate.return_value.execute.side_effect = [response("r2"), http_error()]
    api.get.return_value.execute.return_value = snapshot("editor", "Other editor\n")
    with pytest.raises(GdocError, match="conflict") as caught:
        insert_markdown_into_tab(
            "synthetic", "Notes", "| A |\n|---|\n| B |", replace=True
        )
    assert caught.value.exit_code == 3
    assert len(batches(api)) == 2
    assert api.get.call_count == 1


def test_second_revision_rejection_stops_without_replaying_first_batch(api):
    api.batchUpdate.return_value.execute.side_effect = [
        response("r2"),
        http_error(),
        http_error(),
    ]
    api.get.return_value.execute.return_value = snapshot("editor", "Added\nIntro\n")
    with pytest.raises(GdocError, match="conflict") as caught:
        write()
    assert caught.value.exit_code == 3
    assert len(batches(api)) == 3
    assert api.get.call_count == 1


def test_interleaved_editor_before_fill_relocates_unchanged_table(api):
    api.batchUpdate.return_value.execute.side_effect = [
        response("r2"),
        response("r3"),
        http_error(),
        response("r5"),
    ]
    api.get.return_value.execute.side_effect = [
        snapshot("r3", "Intro\n", table=True),
        snapshot("editor", "Added\nIntro\n", table=True),
    ]
    write()
    old, new = batches(api)[2:]
    assert old["writeControl"] == {"requiredRevisionId": "r3"}
    assert new["writeControl"] == {"requiredRevisionId": "editor"}
    old_indices = [
        r["insertText"]["location"]["index"]
        for r in old["requests"]
        if "insertText" in r
    ]
    new_indices = [
        r["insertText"]["location"]["index"]
        for r in new["requests"]
        if "insertText" in r
    ]
    assert new_indices == [i + 6 for i in old_indices]
    assert api.get.call_count == 2


@pytest.mark.parametrize(
    "change", ["cell_edited", "duplicate_table", "deleted_table", "tab_deleted"]
)
def test_fill_recovery_refuses_changed_or_ambiguous_table(api, change):
    original = snapshot("r3", "Intro\n", table=True)
    changed = deepcopy(original)
    changed["revisionId"] = "editor"
    table = body(changed)["content"][2]
    if change == "cell_edited":
        table["table"]["tableRows"][0]["tableCells"][0]["content"][0] = paragraph(
            "Editor\n", 11
        )
    elif change == "duplicate_table":
        body(changed)["content"].append(deepcopy(table))
    elif change == "deleted_table":
        body(changed)["content"].remove(table)
    else:
        changed["tabs"][0]["tabProperties"]["tabId"] = "different-id"
    api.batchUpdate.return_value.execute.side_effect = [
        response("r2"),
        response("r3"),
        http_error(),
    ]
    api.get.return_value.execute.side_effect = [original, changed]
    with pytest.raises(GdocError, match="conflict") as caught:
        write()
    assert caught.value.exit_code == 3
    assert len(batches(api)) == 3
    assert api.get.call_count == 2


def test_editor_between_table_creation_and_readback_is_not_adopted(api):
    api.get.return_value.execute.return_value = snapshot(
        "editor", "Added\nIntro\n", table=True
    )
    with pytest.raises(GdocError, match="changed before the inserted table") as caught:
        write()
    assert caught.value.exit_code == 3
    assert len(batches(api)) == 2


def test_nonrevision_400_is_not_retried(api):
    api.batchUpdate.return_value.execute.side_effect = [
        response("r2"),
        http_error(message="Invalid JSON payload: required_revision_id"),
    ]
    with pytest.raises(GdocError) as caught:
        write()
    assert caught.value.exit_code == 1
    assert len(batches(api)) == 2
    api.get.assert_not_called()


def test_cli_prints_partial_completion_and_exits_one(api, mocker, capsys):
    mocker.patch(
        "gdoc.notify.pre_flight",
        return_value=ChangeInfo(
            current_version=10,
            last_read_version=10,
        ),
    )
    mocker.patch(
        "gdoc.api.docs.get_document",
        return_value={
            "revisionId": "r1",
            "body": {},
        },
    )
    mocker.patch(
        "gdoc.api.docs.find_text_in_document",
        return_value=[
            {"startIndex": 1, "endIndex": 4},
        ],
    )
    mocker.patch(
        "gdoc.api.drive.get_file_version",
        return_value={
            "version": 10,
            "mimeType": "application/vnd.google-apps.document",
        },
    )
    api.batchUpdate.return_value.execute.side_effect = [
        response("r2"),
        OSError("lost response"),
    ]
    assert (
        run_argv(["edit", "synthetic", "Old", MARKDOWN, "--quiet"], check_updates=False)
        == 1
    )
    err = capsys.readouterr().err
    assert "Partial completion" in err and "completion uncertain" in err
    assert "OK" not in err


@pytest.fixture
def drive_api(mocker):
    service = MagicMock()
    mocker.patch("gdoc.api.drive.get_drive_service", return_value=service)
    version = mocker.patch(
        "gdoc.api.drive.get_file_version", return_value={"version": 10}
    )
    read = mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value=snapshot())
    return service.files.return_value, version, read


def test_single_tab_whole_write_uses_guard_snapshot_and_never_uploads(api, drive_api):
    files, version, read = drive_api
    version.side_effect = [{"version": 10}, {"version": 11}]
    assert update_doc_content("synthetic", "New body", expected_version=10) == 11
    files.update.assert_not_called()
    read.assert_called_once_with("synthetic")
    assert batches(api)[0]["writeControl"] == {"requiredRevisionId": "r1"}
    assert len(batches(api)) == 1


def test_single_tab_editor_after_last_version_read_is_caught_atomically(api, drive_api):
    files, _, _ = drive_api
    api.batchUpdate.return_value.execute.side_effect = http_error()
    with pytest.raises(GdocError, match="conflict") as caught:
        update_doc_content("synthetic", "New body", expected_version=10)
    assert caught.value.exit_code == 3
    assert len(batches(api)) == 1
    assert batches(api)[0]["writeControl"] == {"requiredRevisionId": "r1"}
    files.update.assert_not_called()


@pytest.mark.parametrize("command", ["write", "push"])
@pytest.mark.parametrize(
    "quiet,force", [(False, False), (False, True), (True, False), (True, True)]
)
def test_cli_carries_pre_guard_version_even_when_forced(
    api,
    drive_api,
    mocker,
    tmp_path,
    command,
    quiet,
    force,
):
    files, version, _ = drive_api
    mocker.patch(
        "gdoc.notify.pre_flight",
        return_value=ChangeInfo(
            current_version=10,
            last_read_version=10,
        ),
    )
    mocker.patch(
        "gdoc.state.load_state", return_value=SimpleNamespace(last_read_version=10)
    )
    update_state = mocker.patch("gdoc.state.update_state_after_command")
    mocker.patch("gdoc.api.docs.count_document_tabs", return_value=1)
    # The collaborator changes content after preflight and before the write.
    version.side_effect = ([{"version": 10}] if quiet else []) + [{"version": 11}]
    path = tmp_path / "body.md"
    path.write_text("---\ngdoc: synthetic\n---\nNew body")
    args = SimpleNamespace(
        doc="synthetic",
        file=str(path),
        quiet=quiet,
        force=force,
        tab=None,
        force_collapse_tabs=False,
        json=False,
        plain=False,
        verbose=False,
    )
    with pytest.raises(GdocError, match="document changed") as caught:
        (cmd_write if command == "write" else cmd_push)(args)
    assert caught.value.exit_code == 3
    api.batchUpdate.assert_not_called()
    files.update.assert_not_called()
    update_state.assert_not_called()


def multi_tab(read):
    document = snapshot()
    other = deepcopy(document["tabs"][0])
    other["tabProperties"] = {"tabId": "t2", "title": "Other"}
    document["tabs"].append(other)
    read.return_value = document


def test_drive_collapse_checks_version_after_upload_preparation(drive_api):
    files, version, read = drive_api
    multi_tab(read)
    events = []

    def construct(**kwargs):
        events.append("prepare upload")

        def execute():
            events.append("upload")
            return {"version": "11"}

        return SimpleNamespace(execute=execute)

    files.update.side_effect = construct
    version.side_effect = lambda doc_id: (
        events.append("version check") or {"version": 10}
    )
    assert update_doc_content("synthetic", "New body", expected_version=10) == 11
    assert events == ["prepare upload", "version check", "upload"]


@pytest.mark.parametrize("current", [11, None])
def test_drive_collapse_refuses_changed_or_missing_version(drive_api, current):
    files, version, read = drive_api
    multi_tab(read)
    version.return_value = {"version": current}
    with pytest.raises(GdocError, match="content was not uploaded") as caught:
        update_doc_content("synthetic", "New body", expected_version=10)
    assert caught.value.exit_code == 3
    files.update.return_value.execute.assert_not_called()


def test_drive_import_lost_response_is_uncertain_and_not_retried(drive_api):
    files, _, read = drive_api
    multi_tab(read)
    applied = []

    def execute():
        applied.append("New body")
        raise OSError("response lost")

    files.update.return_value.execute.side_effect = execute
    with pytest.raises(
        GdocError, match="whole-document import: completion uncertain"
    ) as caught:
        update_doc_content("synthetic", "New body", expected_version=10)
    assert caught.value.exit_code == 1
    assert applied == ["New body"]
    assert files.update.call_count == 1


def test_native_write_version_read_failure_reports_known_completion(api, drive_api):
    files, version, _ = drive_api
    version.side_effect = [{"version": 10}, OSError("version read failed")]
    with pytest.raises(GdocError, match="applied: document content replaced") as caught:
        update_doc_content("synthetic", "New body", expected_version=10)
    assert caught.value.exit_code == 1
    assert "completion uncertain" not in str(caught.value)
    assert len(batches(api)) == 1
    files.update.assert_not_called()


def test_api_without_preflight_captures_version_before_document_read(api, drive_api):
    files, version, read = drive_api
    events = []
    version.side_effect = lambda doc_id: events.append("version") or {"version": 10}
    read.side_effect = lambda doc_id: events.append("document") or snapshot()
    update_doc_content("synthetic", "New body")
    assert events[:3] == ["version", "document", "version"]
    files.update.assert_not_called()


def test_two_tables_carry_revision_from_previous_cell_fill(api):
    markdown = "First\n| A |\n|---|\n| B |\nSecond\n| C |\n|---|\n| D |"
    api.batchUpdate.return_value.execute.side_effect = [
        response(f"r{i}") for i in range(2, 7)
    ]
    api.get.return_value.execute.side_effect = [
        snapshot("r3", "First\n\nSecond\n", table=True),
        snapshot("r5", "First\n", table=True),
    ]
    insert_markdown_into_tab("synthetic", "Notes", markdown, replace=True)
    assert [b["writeControl"]["requiredRevisionId"] for b in batches(api)] == [
        "r1",
        "r2",
        "r3",
        "r4",
        "r5",
    ]
    assert [
        b["requests"][0]["insertTable"]["location"]["index"]
        for b in batches(api)
        if "insertTable" in b["requests"][0]
    ] == [15, 7]


def test_conflict_reread_failure_refuses_without_retry(api):
    api.batchUpdate.return_value.execute.side_effect = [response("r2"), http_error()]
    api.get.return_value.execute.side_effect = OSError("read failed")
    with pytest.raises(GdocError, match="conflict: cannot safely recompute") as caught:
        write()
    assert caught.value.exit_code == 3
    assert api.get.call_count == 1
    assert len(batches(api)) == 2


def test_fill_retry_second_conflict_stops(api):
    api.batchUpdate.return_value.execute.side_effect = [
        response("r2"),
        response("r3"),
        http_error(),
        http_error(),
    ]
    api.get.return_value.execute.side_effect = [
        snapshot("r3", "Intro\n", table=True),
        snapshot("editor", "Added\nIntro\n", table=True),
    ]
    with pytest.raises(GdocError, match="conflict") as caught:
        write()
    assert caught.value.exit_code == 3
    assert api.get.call_count == 2
    assert len(batches(api)) == 4


@pytest.mark.parametrize("quiet", [False, True])
def test_force_does_not_bypass_missing_preflight_version(mocker, quiet):
    from gdoc.cli import _check_write_conflict

    mocker.patch("gdoc.notify.pre_flight", return_value=ChangeInfo())
    mocker.patch(
        "gdoc.api.drive.get_file_version",
        return_value={
            "mimeType": "application/vnd.google-apps.document",
        },
    )
    with pytest.raises(GdocError, match="cannot verify document version") as caught:
        _check_write_conflict("synthetic", quiet=quiet, force=True)
    assert caught.value.exit_code == 3
