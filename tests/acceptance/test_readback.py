"""Bounded request application for paragraph rewrites and one fixed table.

These helpers are deliberately incomplete: no arbitrary mutation, nesting,
image layout or general table emulation. Unexpected request types fail loudly.
"""

from copy import deepcopy

from conftest import paragraph, tab
from test_workflows import existing_helper, read, requests

from gdoc.mdparse import parse_inline, parse_markdown, utf16_len


def paragraph_rewrite_readback(original, batch):
    """Apply a full rewrite's text and masks, then expose a native read snapshot."""
    text = existing_helper("test_paragraph_edits", "_apply_text_requests")(
        original, batch
    )
    assert "\t" not in text, "Nesting-tab consumption is outside this helper"
    inserted = [i for i, r in enumerate(batch) if "insertText" in r]
    assert len(inserted) == 1
    assert batch[inserted[0]]["insertText"]["location"]["index"] == 1
    assert batch[inserted[0]]["insertText"]["text"] + "\n" == text
    after = deepcopy(batch[inserted[0] :])
    allowed = {
        "insertText",
        "updateTextStyle",
        "updateParagraphStyle",
        "createParagraphBullets",
        "createNamedRange",
    }
    assert {next(iter(r)) for r in after} <= allowed
    for request in after:
        data = next(iter(request.values()))
        address = data.get("range", data.get("location", {}))
        if "tabId" in address:
            address["tabId"] = "tab"  # Existing helper's fixture name only.
    styles = existing_helper("test_replacement_styles", "_replacement_styles")(
        after, {}
    ) + [{}]
    assert len(styles) == utf16_len(text)
    content, cursor = [], 1
    for line in text.splitlines(keepends=True):
        end = cursor + utf16_len(line)
        p = paragraph(line, cursor)
        units = line.encode("utf-16-le")
        line_styles = styles[cursor - 1 : end - 1]
        runs, start = [], 0
        while start < len(line_styles):
            finish = start + 1
            while (
                finish < len(line_styles) and line_styles[finish] == line_styles[start]
            ):
                finish += 1
            runs.append(
                {
                    "startIndex": cursor + start,
                    "endIndex": cursor + finish,
                    "textRun": {
                        "content": units[start * 2 : finish * 2].decode("utf-16-le"),
                        "textStyle": line_styles[start],
                    },
                }
            )
            start = finish
        p["paragraph"]["elements"] = runs
        content.append(p)
        cursor = end
    named_ranges = {}
    for request in after:
        if "createNamedRange" in request:
            data = request["createNamedRange"]
            named_ranges.setdefault(data["name"], {"namedRanges": []})[
                "namedRanges"
            ].append({"name": data["name"], "ranges": [data["range"]]})
        if "updateParagraphStyle" in request:
            data = request["updateParagraphStyle"]
            lo, hi = data["range"]["startIndex"], data["range"]["endIndex"]
            for p in content:
                if p["startIndex"] < hi and lo < p["endIndex"]:
                    for field in data["fields"].split(","):
                        if field in data["paragraphStyle"]:
                            p["paragraph"]["paragraphStyle"][field] = deepcopy(
                                data["paragraphStyle"][field]
                            )
                        else:
                            p["paragraph"]["paragraphStyle"].pop(field, None)
        if "createParagraphBullets" in request:
            data = request["createParagraphBullets"]
            assert data["bulletPreset"].startswith("BULLET_")
            for p in content:
                if (
                    p["startIndex"] < data["range"]["endIndex"]
                    and data["range"]["startIndex"] < p["endIndex"]
                ):
                    p["paragraph"]["bullet"] = {"listId": "synthetic-bullets"}
    return {"body": {"content": content}, "namedRanges": named_ranges}


COMBINATION = (
    "# Harbor\n"
    "Read ***[Original guide](https://example.invalid/a_(b))***.\n"
    "- Cargo\n"
    "> Keep the note\n"
    "```\n`closed span`\n# literal heading\n\nlast line\n```\n"
    "---\n"
    "Closing text.\n"
)


def assert_combination_meaning(markdown, adjective):
    parsed = parse_markdown(markdown)
    assert parsed.plain_text == (
        f"Harbor\nRead {adjective} guide.\nCargo\nKeep the note\n"
        "`closed span`\n# literal heading\n\nlast line\n\nClosing text.\n"
    )
    assert len(parsed.code_blocks) == 1
    code = parsed.code_blocks[0]
    assert (
        parsed.plain_text[code.start : code.end]
        == "`closed span`\n# literal heading\n\nlast line\n"
    )
    assert any(s.type == "bullets" for s in parsed.styles)
    assert any(s.style.get("namedStyleType") == "HEADING_1" for s in parsed.styles)
    assert any("borderBottom" in s.style for s in parsed.styles)
    phrase_start = len("Harbor\nRead ")
    phrase_end = phrase_start + len(adjective + " guide")
    for key in ("bold", "italic", "link"):
        assert any(
            s.start == phrase_start and s.end == phrase_end and key in s.style
            for s in parsed.styles
        )
    assert "> Keep the note" in markdown


def test_t04_changed_combination_has_request_applied_native_readback(scenario):
    read(scenario)
    before = deepcopy(scenario.document["tabs"][0]["documentTab"]["body"])
    scenario.ok("write", tab="draft", text=COMBINATION)
    result = paragraph_rewrite_readback(before, requests(scenario))
    scenario.document["tabs"][0]["documentTab"] = result
    scenario.document["revisionId"] = "r2"
    first = read(scenario)
    assert_combination_meaning(first, "Original")
    scenario.service.documents.return_value.batchUpdate.reset_mock()
    scenario.ok("write", tab="draft", text=first)
    assert not scenario.batches
    assert_combination_meaning(read(scenario), "Original")
    before = deepcopy(result["body"])
    scenario.ok("write", tab="draft", text=first.replace("Original", "Revised"))
    assert scenario.batches[0]["writeControl"] == {"requiredRevisionId": "r2"}
    result = paragraph_rewrite_readback(before, requests(scenario))
    scenario.document["tabs"][0]["documentTab"] = result
    assert_combination_meaning(read(scenario), "Revised")
    scenario.record["evidence"] = (
        "request_applied_paragraph_text_styles_bullets_code_quote_rule_then_public_native_read"
    )
    scenario.record["gap"] = (
        "Table/image combination and physical Google behavior are separate evidence"
    )


def fill_fixed_table(blank, batch):
    """Replay one 2x1 empty table's fill into its independently fixed API indices."""
    assert blank["table"]["tableRows"]
    rows = blank["table"]["tableRows"]
    assert len(rows) == 2 and all(len(r["tableCells"]) == 1 for r in rows)
    assert {next(iter(r)) for r in batch} <= {
        "insertText",
        "updateTextStyle",
        "updateParagraphStyle",
    }
    result = deepcopy(blank)
    inserts = [r["insertText"] for r in batch if "insertText" in r]
    assert len(inserts) == 2
    assert [r["location"]["index"] for r in inserts] == sorted(
        [r["location"]["index"] for r in inserts], reverse=True
    )
    assert all("insertText" in r for r in batch[:2])
    assigned_styles = []
    shift = 0
    for row in result["table"]["tableRows"]:
        cell = row["tableCells"][0]
        original_start = cell["content"][0]["startIndex"]
        matching = [r for r in inserts if r["location"]["index"] == original_start]
        assert len(matching) == 1
        text = matching[0]["text"]
        base = original_start + shift
        end = base + utf16_len(text) + 1
        local = [
            {"insertText": {"location": {"index": 1, "tabId": "tab"}, "text": text}}
        ]
        for index, request in enumerate(batch[2:], 2):
            address = next(iter(request.values()))["range"]
            if base <= address["startIndex"] < address["endIndex"] <= end:
                copied = deepcopy(request)
                local_address = next(iter(copied.values()))["range"]
                local_address["startIndex"] -= base - 1
                local_address["endIndex"] -= base - 1
                local_address["tabId"] = "tab"
                local.append(copied)
                assigned_styles.append(index)
        cell_result = paragraph_rewrite_readback({"content": [paragraph("\n")]}, local)
        cell["content"] = cell_result["body"]["content"]
        for p in cell["content"]:
            for node in [p, *p["paragraph"]["elements"]]:
                node["startIndex"] += base - 1
                node["endIndex"] += base - 1
        row.update(startIndex=base - 2, endIndex=end)
        cell.update(startIndex=base - 1, endIndex=end)
        shift += utf16_len(text)
    assert sorted(assigned_styles) == list(range(2, len(batch)))
    result["endIndex"] += shift
    return result


def test_t03_move_table_section_and_insert_section_with_readback(scenario):
    make_table = existing_helper("test_native_targets", "table")
    original_table = make_table([["Port\n"], ["East\n"]], 31)
    initial = [
        paragraph("Departure\n", style="HEADING_2"),
        paragraph("Check loads.\n", 11),
        paragraph("Cargo\n", 24, bullet={"listId": "original-list"}),
        paragraph("\n", 30),
        original_table,
        paragraph("Arrival\n", original_table["endIndex"], style="HEADING_2"),
    ]
    scenario.document["tabs"][0]["documentTab"]["body"]["content"] = initial
    sibling = tab("reference", "Reference", [paragraph("Keep sibling\n")])
    scenario.document["tabs"].append(sibling)
    protected = deepcopy(sibling)
    read(scenario)
    target = (
        "## Arrival\n## Departure\nCheck loads.\n- Cargo\n"
        "| Port |\n|:---|\n| **East** |\n## Sign-off\nConfirm.\n"
    )
    # Fixed API response for exactly this operation: Arrival, Departure, blank
    # table anchor, 2x1 empty table, then Sign-off and Confirm.
    prefix = "Arrival\nDeparture\nCheck loads.\nCargo\n"
    start = 1 + utf16_len(prefix)
    blank = make_table([["\n"], ["\n"]], start)
    scaffold = deepcopy(scenario.document)
    scaffold["revisionId"] = "r2"
    scaffold["tabs"][0]["documentTab"]["body"]["content"] = [
        paragraph("Arrival\n", style="HEADING_2"),
        paragraph("Departure\n", 9, style="HEADING_2"),
        paragraph("Check loads.\n", 19),
        paragraph("Cargo\n", 32, bullet={"listId": "rebuilt-list"}),
        blank,
        paragraph("Sign-off\n", blank["endIndex"], style="HEADING_2"),
        paragraph("Confirm.\n", blank["endIndex"] + 9),
    ]
    get = scenario.service.documents.return_value.get.return_value.execute
    get.side_effect = lambda **kw: deepcopy(
        scaffold if len(scenario.batches) >= 2 else scenario.document
    )
    scenario.ok("write", tab="draft", text=target)
    assert len(scenario.batches) == 3
    table_request = [
        r["insertTable"] for r in scenario.batches[1]["requests"] if "insertTable" in r
    ]
    assert len(table_request) == 1
    assert (table_request[0]["rows"], table_request[0]["columns"]) == (2, 1)
    assert table_request[0]["location"] == {"index": start - 1, "tabId": "draft"}
    # The surrounding text is produced from mutation requests, not copied from
    # target Markdown or the canned scaffold. Table structure is API-shape evidence.
    first_batch = scenario.batches[0]["requests"]
    assert first_batch[0]["deleteContentRange"]["range"] == {
        "startIndex": 1,
        "endIndex": initial[-1]["endIndex"] - 1,
        "tabId": "draft",
    }
    projected = paragraph_rewrite_readback(
        {"content": [paragraph("\n")]}, first_batch[1:]
    )
    filled = fill_fixed_table(blank, scenario.batches[2]["requests"])
    cells = [r["tableCells"][0] for r in filled["table"]["tableRows"]]
    assert [
        "".join(
            e["textRun"]["content"] for e in c["content"][0]["paragraph"]["elements"]
        ).removesuffix("\n")
        for c in cells
    ] == ["Port", "East"]
    elements = projected["body"]["content"]
    marker = next(i for i, p in enumerate(elements) if p["startIndex"] == start)
    delta = filled["endIndex"] - elements[marker]["endIndex"]
    for p in elements[marker + 1 :]:
        for node in [p, *p["paragraph"]["elements"]]:
            node["startIndex"] += delta
            node["endIndex"] += delta
    elements[marker : marker + 1] = [filled]
    scenario.document["tabs"][0]["documentTab"] = projected
    scenario.document["revisionId"] = "r2"
    get.side_effect = lambda **kw: deepcopy(scenario.document)
    result = read(scenario)
    assert (
        result.index("## Arrival")
        < result.index("## Departure")
        < result.index("| Port")
        < result.index("## Sign-off")
    )
    parsed = parse_markdown(result)
    assert [[parse_inline(c)[0] for c in row] for row in parsed.tables[0].rows] == [
        ["Port"],
        ["East"],
    ]
    assert parsed.tables[0].alignments == ["START"]
    assert "**East**" in result
    assert "Check loads.\n- Cargo\n" in result
    assert scenario.document["tabs"][1] == protected
    scenario.record["evidence"] = (
        "request_applied_text_and_cell_styles_with_fixed_API_table_scaffold_then_public_read"
    )
