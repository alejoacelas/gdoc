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
