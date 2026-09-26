"""Round-2 review regressions through real CLI dispatch and MCP tools/call."""

from conftest import paragraph, tab
from test_workflows import read, requests


def _rule(start):
    return {"startIndex": start, "endIndex": start + 1, "paragraph": {
        "elements": [
            {"startIndex": start, "endIndex": start, "horizontalRule": {}},
            {"startIndex": start, "endIndex": start + 1, "textRun": {"content": "\n"}},
        ],
        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
    }}


def _leading_rule_document(scenario, middle):
    content = [_rule(1), paragraph(middle + "\n", 2)]
    after = content[-1]["endIndex"]
    content += [_rule(after), paragraph("Body text\n", after + 1)]
    scenario.document["tabs"] = [tab("draft", "Draft", content)]


def test_leading_rule_block_survives_unchanged_and_changed_writes(scenario):
    for middle in ("Status: draft", "gdoc: literal-id"):
        _leading_rule_document(scenario, middle)
        markdown = read(scenario)
        assert markdown == f"---\n---\n---\n{middle}\n---\nBody text\n"

        # Unchanged: nothing is removed, so nothing needs writing.
        scenario.ok("write", tab="draft", text=markdown)
        assert not scenario.batches

        # Changed: the leading rule block is written as content.
        scenario.ok("write", tab="draft", text=markdown + "More.\n")
        inserted = "".join(r["insertText"]["text"] for r in requests(scenario)
                           if "insertText" in r)
        assert middle in inserted and "Body text" in inserted
        scenario.service.documents.return_value.batchUpdate.reset_mock()


def _apply_text(scenario, batch_requests):
    from test_workflows import existing_helper

    body = scenario.document["tabs"][0]["documentTab"]["body"]
    return existing_helper("test_paragraph_edits", "_apply_text_requests")(
        body, batch_requests)


def _code_document(scenario, *, tail=True):
    lines = ["Intro\n", "a = 1\n", "b = 2\n", "c = 3\n"] + (["Tail\n"] if tail else [])
    content, cursor = [], 1
    for line in lines:
        content.append(paragraph(line, cursor))
        cursor += len(line)
    document_tab = tab("draft", "Draft", content)
    document_tab["documentTab"]["namedRanges"] = {
        "gdoc:code:v1": {"name": "gdoc:code:v1", "namedRanges": [{
            "namedRangeId": "code-1", "name": "gdoc:code:v1",
            "ranges": [{"startIndex": 7, "endIndex": 25, "tabId": "draft"}],
        }]},
        "reviewer": {"name": "reviewer", "namedRanges": [{
            "namedRangeId": "foreign-1", "name": "reviewer",
            "ranges": [{"startIndex": 13, "endIndex": 18, "tabId": "draft"}],
        }]},
    }
    other = tab("other", "Other", [paragraph("Else\n", 1)])
    other["documentTab"]["namedRanges"] = {"gdoc:code:v1": {
        "name": "gdoc:code:v1", "namedRanges": [{
            "namedRangeId": "code-other", "name": "gdoc:code:v1",
            "ranges": [{"startIndex": 1, "endIndex": 6, "tabId": "other"}],
        }]}}
    scenario.document["tabs"] = [document_tab, other]


def _ranges(batch_requests, text):
    deleted = [r["deleteNamedRange"]["namedRangeId"] for r in batch_requests
               if "deleteNamedRange" in r]
    created = [(r["createNamedRange"]["name"],
                text[r["createNamedRange"]["range"]["startIndex"] - 1:
                     r["createNamedRange"]["range"]["endIndex"] - 1])
               for r in batch_requests if "createNamedRange" in r]
    return deleted, created


def test_edit_inside_code_keeps_the_whole_block(scenario):
    _code_document(scenario)
    scenario.ok("edit", old_text="b = 2", new_text="b = 22", tab="draft")
    batch = requests(scenario)
    assert next(iter(batch[0])) == "deleteNamedRange"
    text = _apply_text(scenario, batch)
    assert _ranges(batch, text) == (
        ["code-1"], [("gdoc:code:v1", "a = 1\nb = 22\nc = 3\n")])


def test_structural_edit_splits_code_and_marks_its_own_blocks(scenario):
    _code_document(scenario)
    scenario.ok("edit", old_text="b = 2", new_text="> > deep", tab="draft")
    batch = requests(scenario)
    text = _apply_text(scenario, batch)
    deleted, created = _ranges(batch, text)
    assert deleted == ["code-1"]
    assert [name for name, _ in created] == [
        "gdoc:code:v1", "gdoc:code:v1", "gdoc:prefix:v1:2:0"]
    assert created[0][1] == "a = 1\n"
    assert created[1][1].strip("\n") == "c = 3"
    assert "deep" not in created[1][1] and created[2][1].startswith("deep")


def test_edit_that_adds_a_code_block_marks_it(scenario):
    _code_document(scenario)
    scenario.ok("edit", old_text="Tail", new_text="```\nx = 1\n```", tab="draft")
    batch = requests(scenario)
    text = _apply_text(scenario, batch)
    assert _ranges(batch, text) == ([], [("gdoc:code:v1", "x = 1\n")])


def test_tab_replacement_deletes_only_its_own_markers(scenario):
    _code_document(scenario)
    read(scenario)
    scenario.ok("write", tab="draft", text="New body\n", allow_lossy=True)
    deleted = [r["deleteNamedRange"]["namedRangeId"] for r in requests(scenario)
               if "deleteNamedRange" in r]
    assert deleted == ["code-1"]


def test_append_after_final_code_keeps_new_text_out_of_the_block(scenario):
    _code_document(scenario, tail=False)
    read(scenario)
    scenario.ok("insert", tab="draft", text="More\n", position="end")
    batch = requests(scenario)
    text = _apply_text(scenario, batch)
    deleted, created = _ranges(batch, text)
    assert deleted == ["code-1"]
    assert created == [("gdoc:code:v1", "a = 1\nb = 2\nc = 3")]
    assert text.endswith("c = 3\nMore\n")


def test_insert_at_start_moves_a_leading_marker_after_new_text(scenario):
    _code_document(scenario)
    ranges = scenario.document["tabs"][0]["documentTab"]["namedRanges"]
    ranges["gdoc:code:v1"]["namedRanges"][0]["ranges"][0]["startIndex"] = 1
    read(scenario)
    scenario.ok("insert", tab="draft", text="Lead\n", position="start")
    batch = requests(scenario)
    text = _apply_text(scenario, batch)
    assert _ranges(batch, text) == (
        ["code-1"], [("gdoc:code:v1", "Intro\na = 1\nb = 2\nc = 3\n")])
