"""Independent human-task probes. Failures are release gaps, never xfailed."""

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest
from conftest import paragraph, tab

from gdoc.api.docs import get_tab_text
from gdoc.mdparse import parse_markdown, utf16_len


def existing_helper(module, name):
    """Reuse small existing test helpers without importing their test cases."""
    path = Path(__file__).parents[1] / (module + ".py")
    spec = importlib.util.spec_from_file_location("acceptance_" + module, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return getattr(loaded, name)


def requests(scenario):
    return [r for batch in scenario.batches for r in batch["requests"]]


def read(scenario):
    return json.loads(scenario.ok("cat", tab="draft", json=True))["content"]


def write(scenario, markdown):
    scenario.ok("write", tab="draft", text=markdown)
    assert scenario.batches
    assert scenario.batches[-1]["writeControl"] == {"requiredRevisionId": "r1"}


def replay_text(scenario, original):
    return existing_helper("test_paragraph_edits", "_apply_text_requests")(
        original, requests(scenario)
    )


def test_t01_targeted_edit_preserves_neighbors(scenario):
    content = [
        paragraph("Harbor plan\n", style="HEADING_2"),
        paragraph("Original sentence.\n", 13),
        paragraph("Linked guide\n", 32),
        paragraph("Nested item\n", 45, bullet={"listId": "list", "nestingLevel": 1}),
    ]
    content[2]["paragraph"]["elements"][0]["textRun"]["textStyle"] = {
        "link": {"url": "https://example.invalid/guide"}
    }
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = content
    before = deepcopy(scenario.document["tabs"][0]["documentTab"]["body"])
    read(scenario)
    scenario.ok(
        "edit", tab="draft", old_text="Original sentence.", new_text="Revised sentence."
    )
    assert (
        replay_text(scenario, before)
        == "Harbor plan\nRevised sentence.\nLinked guide\nNested item\n"
    )
    for request in requests(scenario):
        data = next(iter(request.values()))
        address = data.get("range", data.get("location", {}))
        assert 13 <= address.get("startIndex", address.get("index", 13)) < 32
        assert address.get("endIndex", 31) <= 31
    scenario.record["evidence"] = "text_replay_and_untouched_neighbor_ranges"


def test_t02_split_and_merge_general_route(scenario):
    read(scenario)
    before = deepcopy(scenario.document["tabs"][0]["documentTab"]["body"])
    write(scenario, "Original\nsentence.\n")
    assert replay_text(scenario, before) == "Original\nsentence.\n"
    # Reread the simulated text result through the same public interface.
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = [
        paragraph("Original\n"),
        paragraph("sentence.\n", 10),
    ]
    assert read(scenario) == "Original\nsentence.\n"
    scenario.service.documents.return_value.batchUpdate.reset_mock()
    before = deepcopy(scenario.document["tabs"][0]["documentTab"]["body"])
    write(scenario, "Original sentence.\n")
    assert replay_text(scenario, before) == "Original sentence.\n"
    scenario.record["evidence"] = "text_replay_only_paragraph_style_not_simulated"


def test_t03_move_section_insert_section_request_order(scenario):
    read(scenario)
    write(
        scenario,
        "# Second\nMoved paragraph\n- Cargo\n# New\nNew paragraph\n# First\nTail\n",
    )
    inserted = "".join(
        r["insertText"]["text"] for r in requests(scenario) if "insertText" in r
    )
    assert inserted == "Second\nMoved paragraph\nCargo\nNew\nNew paragraph\nFirst\nTail"
    assert sum("createParagraphBullets" in r for r in requests(scenario)) == 1
    scenario.record["gap"] = (
        "Section containing a table needs integrated structural readback"
    )


@pytest.mark.parametrize("changed", [False, True], ids=["unchanged", "changed"])
def test_t04_combined_roundtrip_preserves_link_heading_list(scenario, changed):
    p = paragraph("Compass\n", style="HEADING_2")
    q = paragraph("Original sentence.\n", p["endIndex"])
    q["paragraph"]["elements"][0]["textRun"]["textStyle"] = {
        "bold": True,
        "italic": True,
        "link": {"url": "https://example.invalid/a_(b)"},
    }
    r = paragraph("Cargo\n", q["endIndex"], bullet={"listId": "l"})
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = [p, q, r]
    source = read(scenario)
    write(scenario, source.replace("Original", "Revised") if changed else source)
    reqs = requests(scenario)
    inserted = next(r["insertText"]["text"] for r in reqs if "insertText" in r)
    assert (
        inserted == f"Compass\n{'Revised' if changed else 'Original'} sentence.\nCargo"
    )
    styles = [r["updateTextStyle"]["textStyle"] for r in reqs if "updateTextStyle" in r]
    assert any(s.get("bold") for s in styles)
    assert any(s.get("italic") for s in styles)
    assert any(
        s.get("link", {}).get("url") == "https://example.invalid/a_(b)" for s in styles
    )
    assert any(
        r.get("updateParagraphStyle", {})
        .get("paragraphStyle", {})
        .get("namedStyleType")
        == "HEADING_2"
        for r in reqs
    )
    assert any("createParagraphBullets" in r for r in reqs)
    scenario.record["gap"] = (
        "Request assertions do not establish native combined roundtrip; "
        "code/table/image combination remains unverified"
    )


@pytest.mark.parametrize(
    "replacement",
    [
        "***[Revised](https://example.invalid/b_(c))***",
        "Revised *literal punctuation?*",
    ],
)
def test_t05_restyle_retarget_and_remove_stale_link(scenario, replacement):
    run = scenario.document["tabs"][0]["documentTab"]["body"]["content"][0][
        "paragraph"
    ]["elements"][0]
    run["textRun"]["textStyle"] = {
        "link": {"url": "https://example.invalid/old"},
        "bold": True,
    }
    read(scenario)
    scenario.ok(
        "edit", tab="draft", old_text="Original sentence.", new_text=replacement
    )
    styles = [
        r["updateTextStyle"] for r in requests(scenario) if "updateTextStyle" in r
    ]
    assert any("link" in s["fields"] for s in styles)
    normalized = deepcopy(requests(scenario))
    for request in normalized:
        data = next(iter(request.values()))
        address = data.get("range", data.get("location", {}))
        if "tabId" in address:
            address["tabId"] = "tab"
    result = existing_helper("test_replacement_styles", "_replacement_styles")(
        normalized, run["textRun"]["textStyle"]
    )
    assert all(
        s.get("link", {}).get("url") != "https://example.invalid/old" for s in result
    )
    if "https://example.invalid/b_(c)" in replacement:
        assert all(
            s.get("link", {}).get("url") == "https://example.invalid/b_(c)"
            for s in result
        )
        assert all(s.get("bold") and s.get("italic") for s in result)
    scenario.record["evidence"] = "text_style_mask_replay"


def test_t06_mixed_lists_empty_item_and_number_start(scenario):
    read(scenario)
    write(scenario, "3. Cargo\n   - Fragile\n4. Dock\n\n7. Restart\n- \n")
    reqs = requests(scenario)
    assert any("createParagraphBullets" in r for r in reqs)
    scenario.record["gap"] = (
        "Displayed starts/restarts require agreed API "
        "best-effort contract and native readback"
    )


def test_t07_table_reorder_styled_cells_request_content(scenario):
    read(scenario)
    # A fixed post-insert empty 2x2 table snapshot; no table emulator.
    make_table = existing_helper("test_native_targets", "table")
    blank = make_table([["\n", "\n"], ["\n", "\n"]], start=2)
    snapshot = deepcopy(scenario.document)
    snapshot["revisionId"] = "r2"
    snapshot["tabs"][0]["documentTab"]["body"]["content"] = [
        paragraph("\n"),
        blank,
        paragraph("\n", blank["endIndex"]),
    ]
    get = scenario.service.documents.return_value.get.return_value.execute
    get.side_effect = lambda **kw: deepcopy(
        snapshot if len(scenario.batches) >= 2 else scenario.document
    )
    scenario.ok(
        "write",
        tab="draft",
        text="| Port | **Load** |\n|:---|---:|\n| East | *Seven* |\n",
    )
    reqs = requests(scenario)
    assert any("insertTable" in r for r in reqs)
    inserted = [r["insertText"]["text"] for r in reqs if "insertText" in r]
    assert {"Port", "Load", "East", "Seven"} <= set(inserted)
    # Alignment is semantic, not merely successful insertion of cell text.
    alignments = {
        r["updateParagraphStyle"]["paragraphStyle"].get("alignment")
        for r in reqs
        if "updateParagraphStyle" in r
    }
    assert {"START", "END"} <= alignments


def test_t08_literal_fence_quote_rule(scenario):
    read(scenario)
    write(
        scenario, "> Harbor note\n\n```text\n`closed`\n# literal\n\nnext\n```\n\n---\n"
    )
    inserted = "".join(
        r["insertText"]["text"] for r in requests(scenario) if "insertText" in r
    )
    assert "`closed`\n# literal\n\nnext\n" in inserted
    assert "Harbor note" in inserted
    assert any(
        "borderBottom" in r.get("updateParagraphStyle", {}).get("paragraphStyle", {})
        for r in requests(scenario)
    )


def test_t09_tab_id_precedes_title_for_read_and_edit(scenario):
    scenario.document["tabs"].insert(
        0, tab("decoy", "draft", [paragraph("Decoy sentence.\n")])
    )
    assert "Original sentence." in read(scenario)
    scenario.ok("edit", tab="draft", old_text="Original", new_text="Revised")
    assert all(
        next(iter(r.values()))
        .get("range", next(iter(r.values())).get("location", {}))
        .get("tabId")
        == "draft"
        for r in requests(scenario)
    )


def test_t10_successive_writes_use_acknowledged_revision(scenario):
    read(scenario)
    write(scenario, "First revision\n")
    scenario.version = 2
    scenario.document["revisionId"] = "r2"
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = [
        paragraph("First revision\n")
    ]
    scenario.ok("write", tab="draft", text="Second revision\n")
    assert scenario.batches[-1]["writeControl"] == {"requiredRevisionId": "r2"}


def test_t10_collaborator_change_refuses(scenario):
    read(scenario)
    scenario.version = 2
    scenario.document["revisionId"] = "foreign"
    code, out, err = scenario.call("write", tab="draft", text="Overwrite\n")
    assert code != 0, out + err
    assert not scenario.batches


def test_t10_lost_response_is_not_replayed(scenario):
    read(scenario)
    execute = scenario.service.documents.return_value.batchUpdate.return_value.execute
    execute.side_effect = TimeoutError("synthetic lost response")
    code, out, err = scenario.call("write", tab="draft", text="Uncertain\n")
    assert code != 0
    assert len(scenario.batches) == 1
    assert "uncertain" in (out + err).lower()


def test_t11_raw_and_selected_structure_burden(scenario):
    scenario.document["tabs"].append(
        tab(
            "archive",
            "Archive",
            [
                paragraph("Archive " + str(i) + " " + "x" * 120 + "\n", 1 + i * 140)
                for i in range(400)
            ],
        )
    )
    raw = json.loads(scenario.ok("structure", json=True))
    scoped = json.loads(scenario.ok("structure", tab="draft", json=True))
    assert len(raw["document"]["tabs"]) == 2
    assert scoped["document"]["tab"]["tabProperties"]["tabId"] == "draft"
    assert "Original sentence." in json.dumps(scoped)
    scenario.record["evidence"] = "public_output_comparison"
    scenario.record["gap"] = (
        "Within-one-long-tab target selection still needs candidate comparison"
    )


@pytest.mark.parametrize("scope", ["prefix", "tab", "metadata"])
def test_t12_partial_read_cannot_authorize_whole_overwrite(scenario, scope):
    if scope == "prefix":
        output = scenario.ok("cat", max_bytes=8, json=True)
        # A partial-output marker must be visible to the agent.
        scenario.record["partial_output_marked"] = any(
            word in output.lower() for word in ("truncat", "partial")
        )
    elif scope == "tab":
        scenario.document["tabs"].append(
            tab("unseen", "Unseen", [paragraph("Private sibling\n")])
        )
        read(scenario)
    else:
        scenario.ok("structure", fields="documentId,title,revisionId", json=True)
    code, out, err = scenario.call("write", text="Replacement\n")
    assert code != 0, out + err
    assert not scenario.batches
    # A refusal for lack of read coverage, not incidental tab-collapse protection.
    assert any(word in (out + err).lower() for word in ("baseline", "read", "scope"))


@pytest.mark.parametrize("native", ["inlineObjectElement", "footnoteReference"])
def test_t13_local_edit_beside_native_object(scenario, native):
    p = paragraph("Original sentence.\n")
    p["paragraph"]["elements"].insert(
        0,
        {
            "startIndex": 1,
            "endIndex": 2,
            native: {"inlineObjectId": "image"}
            if native == "inlineObjectElement"
            else {"footnoteId": "note"},
        },
    )
    p["paragraph"]["elements"][1].update(startIndex=2, endIndex=21)
    p["endIndex"] = 21
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = [p]
    scenario.ok("edit", tab="draft", old_text="Original", new_text="Revised")
    for r in requests(scenario):
        if "deleteContentRange" in r:
            assert r["deleteContentRange"]["range"]["startIndex"] >= 2
    if native == "inlineObjectElement":
        return  # Explicit image removal belongs to T14, not rich-loss consent.
    count = len(scenario.batches)
    read(scenario)
    code, out, err = scenario.call("write", tab="draft", text="Discard image\n")
    assert code != 0 and len(scenario.batches) == count, out + err


@pytest.mark.parametrize(
    "operation,markdown",
    [
        ("insert", "Before\n![Map](https://example.invalid/map.png)\nAfter\n"),
        ("move", "![Map](https://example.invalid/map.png)\nBefore\nAfter\n"),
        ("replace", "Before\n![Map](https://example.invalid/new-map.png)\nAfter\n"),
    ],
)
def test_t14_image_markdown_route(scenario, operation, markdown):
    read(scenario)
    write(scenario, markdown)
    assert any(
        "insertInlineImage" in r or "replaceImage" in r for r in requests(scenario)
    )
    scenario.record["gap"] = (
        "Request-level only; source retrieval, move/removal "
        "and durable references need integrated native result evidence"
    )


def test_t15_unicode_space_fallback_visible_in_read(scenario, monkeypatch):
    scenario.export = "Harbor\u00a0cargo\u2009ready\n"
    comment = {
        "id": "c1",
        "content": "Check manifest",
        "resolved": False,
        "quotedFileContent": {"value": "Harbor cargo ready"},
        "author": {"displayName": "Reviewer"},
        "replies": [],
    }
    monkeypatch.setattr("gdoc.api.comments.list_comments", lambda *a, **kw: [comment])
    output = scenario.ok("cat", comments=True)
    assert "Check manifest" in output
    assert "[anchor deleted]" not in output
    assert "[UNANCHORED]" not in output


def test_t15_invalid_occurrence_is_local(scenario):
    code, out, err = scenario.call(
        "comment", text="Check manifest", quote="Original", occurrence=0
    )
    assert code != 0, out + err
    assert not scenario.service.documents.return_value.get.called
    assert not scenario.batches


def test_d01_code_crlf_normalization():
    parsed = parse_markdown("```\r\nalpha\r\nbeta\r\n```\r\n")
    assert "\r" not in parsed.plain_text
    assert "alpha\nbeta\n" in parsed.plain_text


def test_d12_closed_span_inside_fence_stays_literal():
    parsed = parse_markdown("```\n`closed`\n# literal\n```\n")
    assert parsed.plain_text == "`closed`\n# literal\n"


def test_d08_literal_list_whitespace_survives_export():
    item = paragraph("  Cargo\n", bullet={"listId": "l"})
    markdown = get_tab_text({"body": {"content": [item]}}, markdown=True)
    assert parse_markdown(markdown).plain_text == "  Cargo\n"


def test_helper_utf16_unit():
    assert utf16_len("a😀b") == 4
