"""Replacement safety uses native structure, never Markdown text heuristics."""

from types import SimpleNamespace

import pytest

from gdoc.api.docs import insert_markdown_into_tab
from gdoc.cli import build_parser, cmd_push, cmd_write
from gdoc.lossy import check_markdown_replacement
from gdoc.util import GdocError


def body(element):
    return {"content": [{
        "startIndex": 1, "endIndex": 5,
        "paragraph": {"elements": [element]},
    }]}


def tab(name, content):
    return {"tabProperties": {"tabId": name, "title": name},
            "documentTab": {"body": content}}


@pytest.fixture(autouse=True)
def no_export_network(mocker):
    mocker.patch("gdoc.api.drive.export_doc", return_value="remote")
    mocker.patch("gdoc.api.drive.get_file_version", return_value={"version": 2})


RICH = body({"person": {"personProperties": {"name": "Example"}}})
PLAIN = body({"textRun": {"content": "old\n"}})


@pytest.mark.parametrize("element", [
    {"person": {}}, {"richLink": {}}, {"dateElement": {}},
    {"inlineObjectElement": {"inlineObjectId": "image"}},
    {"footnoteReference": {"footnoteId": "fn"}}, {"equation": {}},
    {"autoText": {}}, {"pageBreak": {}}, {"columnBreak": {}},
    {"horizontalRule": {}},
    {"textRun": {"content": "pending", "suggestedInsertionIds": ["s"]}},
    {"textRun": {"textStyle": {"link": {"headingId": "h"}}}},
])
def test_native_elements_refuse(element):
    with pytest.raises(GdocError, match="--allow-lossy") as exc:
        check_markdown_replacement(body(element), tab_body=True)
    assert exc.value.exit_code == 3


def test_ordinary_formatting_and_metadata_allowed():
    check_markdown_replacement({
        "body": body({"textRun": {"content": "hello", "textStyle": {
            "bold": True, "italic": True, "strikethrough": True,
            "link": {"url": "https://example.com"},
        }}}),
        "namedStyles": {}, "namedRanges": {"label": {}},
        "lists": {"list": {"listProperties": {}}},
        "sectionBreak": {"sectionStyle": {}},
    })


@pytest.mark.parametrize("structure", [
    {"paragraph": {"positionedObjectIds": ["obj"]}},
    {"tableOfContents": {}},
    {"table": {"tableRows": [{"tableCells": [{
        "tableCellStyle": {"rowSpan": 2},
    }]}]}},
    {"table": {"tableRows": [{"tableCells": [{
        "content": [{"table": {}}],
    }]}]}},
])
def test_structural_hazards(structure):
    with pytest.raises(GdocError):
        check_markdown_replacement({"content": [structure]})


def test_simple_tables_round_trip_in_both_paths():
    header = body({"textRun": {"content": "header", "textStyle": {"bold": True}}})
    header["content"][0]["paragraph"]["elements"].append(
        {"textRun": {"content": "\n"}},
    )
    empty = body({"textRun": {"content": "\n"}})
    scope = {"content": [{"table": {"tableRows": [
        {"tableCells": [header, empty]}, {"tableCells": [PLAIN, PLAIN]},
    ]}}]}
    check_markdown_replacement(scope)
    check_markdown_replacement(scope, tab_body=True)


@pytest.mark.parametrize("target_body", [PLAIN, {}, {"content": []}])
@pytest.mark.parametrize("selector", ["TARGET", "target"])
def test_tab_scope_ignores_rich_sibling_and_headers(mocker, target_body, selector):
    target = tab("target", target_body)
    target["documentTab"]["headers"] = {"h": RICH}
    target["documentTab"]["footers"] = {"f": RICH}
    target["documentTab"]["inlineObjects"] = {"unreferenced": {}}
    target["childTabs"] = [tab("rich-child", RICH)]
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [target, tab("sibling", RICH)],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    insert_markdown_into_tab("doc", selector, "new", replace=True)
    batch = service.documents.return_value.batchUpdate
    batch.assert_called_once()
    assert batch.call_args.kwargs["body"]["writeControl"] == {
        "requiredRevisionId": "r",
    }


@pytest.mark.parametrize("target_body", [RICH, body({"horizontalRule": {}})])
@pytest.mark.parametrize("allow_lossy", [False, True])
def test_tab_refusal_precedes_every_mutation(mocker, allow_lossy, target_body):
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [tab("target", target_body)],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    table_insert = mocker.patch("gdoc.api.docs._insert_table")
    if allow_lossy:
        insert_markdown_into_tab(
            "doc", "target", "new", replace=True, allow_lossy=True,
        )
        service.documents.return_value.batchUpdate.assert_called_once()
    else:
        with pytest.raises(GdocError, match="selected tab body"):
            insert_markdown_into_tab("doc", "target", "new", replace=True)
        service.documents.return_value.batchUpdate.assert_not_called()
        table_insert.assert_not_called()


@pytest.mark.parametrize("command", ["write", "push"])
@pytest.mark.parametrize("scope", [
    {"body": RICH},
    {"tabs": [tab("plain", PLAIN), tab("rich", RICH)]},
    {"tabs": [{**tab("parent", PLAIN), "childTabs": [tab("child", RICH)]}]},
    {"headers": {"h": PLAIN}},
    {"tabs": [{"documentTab": {"footers": {"f": PLAIN}}}]},
    {"footnotes": {"f": PLAIN}},
])
@pytest.mark.parametrize("mode", ["refuse", "opt-in", "no-op"])
def test_full_write_scope(mocker, tmp_path, command, scope, mode):
    path = tmp_path / "draft.md"
    path.write_text("---\ngdoc: doc\n---\nnew", encoding="utf-8")
    args = SimpleNamespace(
        doc="doc", file=str(path), force=True, force_collapse_tabs=True,
        allow_lossy=mode == "opt-in", quiet=True,
    )
    mocker.patch("gdoc.cli._check_write_conflict", return_value=(None, mode == "no-op"))
    noop = mocker.patch("gdoc.cli._finish_noop_write", return_value=0)
    fetch = mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value=scope)
    mutation = mocker.patch("gdoc.api.drive.update_doc_content", return_value=2)
    mocker.patch("gdoc.state.update_state_after_command")
    handler = cmd_write if command == "write" else cmd_push
    if mode == "refuse":
        with pytest.raises(GdocError, match="whole document"):
            handler(args)
        mutation.assert_not_called()
    else:
        assert handler(args) == 0
        if mode == "no-op":
            noop.assert_called_once()
            mutation.assert_not_called()
            fetch.assert_not_called()
        else:
            mutation.assert_called_once_with("doc", "new")


@pytest.mark.parametrize("command", ["write", "push"])
def test_lossy_opt_in_does_not_allow_tab_collapse(mocker, tmp_path, command):
    path = tmp_path / "draft.md"
    path.write_text("---\ngdoc: doc\n---\nnew", encoding="utf-8")
    args = SimpleNamespace(doc="doc", file=str(path), allow_lossy=True)
    mocker.patch("gdoc.cli._check_write_conflict", return_value=(None, False))
    mocker.patch("gdoc.api.docs.get_document_with_tabs",
                 return_value={"tabs": [{}, {}]})
    mutation = mocker.patch("gdoc.api.drive.update_doc_content")
    with pytest.raises(GdocError, match="--force-collapse-tabs"):
        (cmd_write if command == "write" else cmd_push)(args)
    mutation.assert_not_called()


@pytest.mark.parametrize("argv", [["write", "doc", "file"], ["push", "file"]])
def test_parser_opt_in_is_separate(argv):
    parser = build_parser()
    args = parser.parse_args(argv + ["--allow-lossy"])
    assert args.allow_lossy
    assert not args.force
    assert not args.force_collapse_tabs


def test_structure_read_failure_propagates_before_upload(mocker, tmp_path):
    path = tmp_path / "draft.md"
    path.write_text("new", encoding="utf-8")
    mocker.patch("gdoc.cli._check_write_conflict", return_value=(None, False))
    mocker.patch(
        "gdoc.api.docs.get_document_with_tabs",
        side_effect=GdocError("unavailable"),
    )
    mutation = mocker.patch("gdoc.api.drive.update_doc_content")
    with pytest.raises(GdocError, match="unavailable"):
        cmd_write(SimpleNamespace(doc="doc", file=str(path)))
    mutation.assert_not_called()


@pytest.mark.parametrize("command", ["write", "push"])
def test_full_write_uses_one_safety_snapshot(mocker, tmp_path, command):
    path = tmp_path / "draft.md"
    path.write_text("---\ngdoc: doc\n---\nnew", encoding="utf-8")
    mocker.patch("gdoc.cli._check_write_conflict", return_value=(None, False))
    fetch = mocker.patch("gdoc.api.docs.get_document_with_tabs", side_effect=[
        {"tabs": [tab("Tab 1", PLAIN)]},
        {"tabs": [tab("Tab 1", PLAIN), tab("new-tab", PLAIN)]},
    ])
    mutation = mocker.patch("gdoc.api.drive.update_doc_content", return_value=2)
    mocker.patch("gdoc.state.update_state_after_command")
    args = SimpleNamespace(doc="doc", file=str(path))
    assert (cmd_write if command == "write" else cmd_push)(args) == 0
    fetch.assert_called_once_with("doc")
    mutation.assert_called_once()


def test_markdown_horizontal_rule_border_is_allowed():
    check_markdown_replacement({"content": [{"paragraph": {
        "paragraphStyle": {"borderBottom": {"dashStyle": "SOLID"}},
        "elements": [{"textRun": {"content": "\n"}}],
    }}]}, tab_body=True)


@pytest.mark.parametrize("name", [
    "person", "rowSpan", "columnSpan", "sectionBreak", "table", "headers",
    "suggestedAnything", "horizontalRule",
])
@pytest.mark.parametrize("command", ["write", "push"])
def test_named_range_names_are_not_schema_fields(mocker, tmp_path, name, command):
    path = tmp_path / "draft.md"
    path.write_text("---\ngdoc: doc\n---\nnew", encoding="utf-8")
    doc = {"tabs": [{"documentTab": {"body": PLAIN, "namedRanges": {
        name: {"namedRanges": [{"name": name, "ranges": [{
            "startIndex": 1, "endIndex": 3,
        }]}]},
    }}}]}
    mocker.patch("gdoc.cli._check_write_conflict", return_value=(None, False))
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value=doc)
    mutation = mocker.patch("gdoc.api.drive.update_doc_content", return_value=2)
    mocker.patch("gdoc.state.update_state_after_command")
    args = SimpleNamespace(doc="doc", file=str(path))
    assert (cmd_write if command == "write" else cmd_push)(args) == 0
    mutation.assert_called_once()


@pytest.mark.parametrize("style", [
    {"columnProperties": [{}, {}]},
    {"marginTop": {"magnitude": 20, "unit": "PT"}},
    {"sectionType": "NEXT_PAGE"},
    {"flipPageOrientation": True},
])
def test_whole_document_custom_sections_refuse(style):
    with pytest.raises(GdocError, match="section"):
        check_markdown_replacement({"body": {"content": [{
            "endIndex": 1, "sectionBreak": {"sectionStyle": style},
        }]}})


def test_default_section_marker_is_allowed():
    style = {
        "sectionType": "CONTINUOUS", "contentDirection": "LEFT_TO_RIGHT",
        "columnSeparatorStyle": "NONE", "columnProperties": [{}],
        "flipPageOrientation": False,
        "marginTop": {"magnitude": 72, "unit": "PT"},
    }
    check_markdown_replacement({
        "documentStyle": {"marginTop": style["marginTop"]},
        "body": {"content": [{"endIndex": 1, "sectionBreak": {
            "sectionStyle": style,
        }}]},
    })


@pytest.mark.parametrize("blank", [True, False])
def test_tab_initial_section_style_is_outside_deletion(mocker, blank):
    content = [{"endIndex": 1, "sectionBreak": {"sectionStyle": {
        "columnProperties": [{}, {}], "defaultHeaderId": "h",
    }}}]
    if not blank:
        content.extend(PLAIN["content"])
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [tab("target", {"content": content})],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    insert_markdown_into_tab("doc", "target", "new", replace=True)
    service.documents.return_value.batchUpdate.assert_called_once()


def test_tab_internal_section_refuses_before_mutation(mocker):
    content = [*PLAIN["content"], {
        "startIndex": 5, "endIndex": 6,
        "sectionBreak": {"sectionStyle": {"sectionType": "CONTINUOUS"}},
    }, {"startIndex": 6, "endIndex": 8, "paragraph": {
        "elements": [{"textRun": {"content": "x\n"}}],
    }}]
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [tab("target", {"content": content})],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    with pytest.raises(GdocError, match="section"):
        insert_markdown_into_tab("doc", "target", "new", replace=True)
    service.documents.return_value.batchUpdate.assert_not_called()


def test_map_values_are_still_checked():
    with pytest.raises(GdocError, match="people chips"):
        check_markdown_replacement({"headers": {"rowSpan": RICH}})


@pytest.mark.parametrize("custom", [False, True])
def test_section_defaults_follow_owning_tab(custom):
    def section_tab(name, margin, section_margin):
        return {"tabProperties": {"tabId": name}, "documentTab": {
            "documentStyle": {"marginTop": {"magnitude": margin, "unit": "PT"}},
            "body": {"content": [{"endIndex": 1, "sectionBreak": {
                "sectionStyle": {"marginTop": {
                    "magnitude": section_margin, "unit": "PT",
                }},
            }}]},
        }}

    parent = section_tab("parent", 72, 72)
    parent["childTabs"] = [section_tab("child", 18, 1 if custom else 18)]
    scope = {
        "documentStyle": {"marginTop": {"magnitude": 999, "unit": "PT"}},
        "tabs": [parent, section_tab("sibling", 36, 36)],
    }
    if custom:
        with pytest.raises(GdocError, match="section"):
            check_markdown_replacement(scope)
    else:
        with pytest.raises(GdocError, match="page setup") as exc:
            check_markdown_replacement(scope)
        assert "section layout" not in str(exc.value)


@pytest.mark.parametrize("in_cell", [False, True])
@pytest.mark.parametrize("mode", ["refuse", "override", "style-only"])
def test_referenced_list_inventory(mocker, capsys, in_cell, mode):
    content = body({"textRun": {"content": "old\n"}})
    content["content"][0]["paragraph"]["bullet"] = {"listId": "L"}
    if in_cell:
        content["content"][0]["paragraph"]["elements"][0]["textRun"]["textStyle"] = {
            "bold": True,
        }
        content = {"content": [{"startIndex": 1, "endIndex": 9, "table": {
            "tableRows": [{"tableCells": [{"content": content["content"]}]}],
        }}]}
    target = tab("target", content)
    definition = {"listProperties": {"nestingLevels": [{"glyphSymbol": "★"}]}}
    if mode != "style-only":
        definition["suggestedListPropertiesChanges"] = {"s": {
            "listProperties": {"nestingLevels": [{"glyphSymbol": "◆"}]},
            "listPropertiesSuggestionState": {
                "nestingLevelsSuggestionStates": [{"glyphSymbolSuggested": True}],
            },
        }}
    target["documentTab"]["lists"] = {"L": definition}
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [target],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    table_insert = mocker.patch("gdoc.api.docs._insert_table")
    markdown = "| New |\n| --- |\n| value |"
    if mode == "refuse":
        with pytest.raises(GdocError, match="pending suggestions") as exc:
            insert_markdown_into_tab("doc", "target", markdown, replace=True)
        assert exc.value.exit_code == 3
        service.documents.return_value.batchUpdate.assert_not_called()
        table_insert.assert_not_called()
    else:
        insert_markdown_into_tab(
            "doc", "target", markdown, replace=True, allow_lossy=mode == "override",
        )
        service.documents.return_value.batchUpdate.assert_called_once()
        table_insert.assert_called_once()
        warning = capsys.readouterr().err
        assert "list glyphs and list styling" in warning
        assert ("will discard: pending suggestions" in warning) == (mode == "override")


@pytest.mark.parametrize("header_only", [False, True])
def test_unreferenced_suggested_lists_are_outside_body(mocker, capsys, header_only):
    target = tab("target", PLAIN)
    target["documentTab"]["lists"] = {"unused": {
        "listProperties": {"nestingLevels": [{"glyphSymbol": "★"}]},
        "suggestedListPropertiesChanges": {"s": {"listProperties": {}}},
    }}
    if header_only:
        header = body({"textRun": {"content": "header\n"}})
        header["content"][0]["paragraph"]["bullet"] = {"listId": "unused"}
        target["documentTab"]["headers"] = {"h": header}
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [target],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    insert_markdown_into_tab("doc", "target", "new", replace=True)
    service.documents.return_value.batchUpdate.assert_called_once()
    assert capsys.readouterr().err == ""


def test_keep_lines_together_warns_about_paragraph_layout(capsys):
    check_markdown_replacement({"content": [{"paragraph": {
        "paragraphStyle": {"keepLinesTogether": True},
    }}]}, tab_body=True)
    assert "may reset styles: paragraph layout" in capsys.readouterr().err


def numbered_tab(list_ids, start=1, glyph_type="DECIMAL"):
    target = tab("target", {"content": [{
        "startIndex": 1 + i * 5, "endIndex": 6 + i * 5,
        "paragraph": {
            "elements": [{"textRun": {"content": "item\n"}}],
            "bullet": {"listId": list_id},
        },
    } for i, list_id in enumerate(list_ids)]})
    target["documentTab"]["lists"] = {list_id: {"listProperties": {
        "nestingLevels": [{"glyphType": glyph_type, "startNumber": start}],
    }} for list_id in list_ids}
    return target


def test_adjacent_numbered_restarts_refuse_before_mutation(mocker):
    from gdoc.api.docs import get_tab_text

    target = numbered_tab(["first", "second"])
    markdown = get_tab_text(target["documentTab"], markdown=True)
    # The native lists each start at 1; export loses the second restart.
    assert markdown == "1. item\n2. item\n"
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [target],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    with pytest.raises(GdocError, match="numbered list") as exc:
        insert_markdown_into_tab("doc", "target", markdown, replace=True)
    assert "first" in str(exc.value) and "second" in str(exc.value)
    service.documents.return_value.batchUpdate.assert_not_called()


@pytest.mark.parametrize("list_ids,start", [
    (["first", "second", "first"], 1),
    (["first"], 3),
    (["first"], 0),
])
@pytest.mark.parametrize("tab_body", [False, True])
def test_numbered_sequence_hazards_name_lists_and_allow_override(
    capsys, list_ids, start, tab_body,
):
    scope = numbered_tab(list_ids, start)["documentTab"]
    with pytest.raises(GdocError, match="numbered list") as exc:
        check_markdown_replacement(scope, tab_body=tab_body)
    for list_id in list_ids:
        assert list_id in str(exc.value)
    check_markdown_replacement(scope, tab_body=tab_body, allow_lossy=True)
    assert "will discard:" in capsys.readouterr().err


@pytest.mark.parametrize("list_ids,glyph_type", [
    (["first", "first", "first"], "DECIMAL"),
    (["first", "second", "first"], "GLYPH_TYPE_UNSPECIFIED"),
])
def test_continuous_numbering_and_bullets_remain_allowed(list_ids, glyph_type):
    scope = numbered_tab(list_ids, glyph_type=glyph_type)["documentTab"]
    check_markdown_replacement(scope, tab_body=True)


@pytest.mark.parametrize("same_list", [False, True])
def test_numbering_after_plain_paragraph(same_list):
    scope = numbered_tab(["first", "first" if same_list else "second"])["documentTab"]
    scope["body"]["content"].insert(1, PLAIN["content"][0])
    if same_list:
        with pytest.raises(GdocError, match="numbered list 'first' resumes"):
            check_markdown_replacement(scope, tab_body=True)
    else:
        check_markdown_replacement(scope, tab_body=True)


def test_numbered_definitions_follow_owning_tab():
    first = numbered_tab(["same"])
    second = numbered_tab(["same"])
    first["tabProperties"]["title"] = second["tabProperties"]["title"] = "Tab 1"
    check_markdown_replacement({"tabs": [first, second]})


def test_only_referenced_numbered_levels_are_checked():
    scope = numbered_tab(["first"])["documentTab"]
    scope["lists"]["unused"] = {"listProperties": {"nestingLevels": [
        {"glyphType": "DECIMAL", "startNumber": 5},
    ]}}
    scope["lists"]["first"]["listProperties"]["nestingLevels"].append({
        "glyphType": "DECIMAL", "startNumber": 3,
    })
    check_markdown_replacement(scope, tab_body=True)
    scope["body"]["content"][0]["paragraph"]["bullet"]["nestingLevel"] = 1
    with pytest.raises(GdocError, match="numbered list 'first' starts at 3"):
        check_markdown_replacement(scope, tab_body=True)


def test_numbered_restart_override_permits_tab_mutation(mocker, capsys):
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [numbered_tab(["first", "second"])],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    insert_markdown_into_tab("doc", "target", "new", replace=True, allow_lossy=True)
    service.documents.return_value.batchUpdate.assert_called_once()
    warning = capsys.readouterr().err
    assert "will discard:" in warning and "'first', 'second'" in warning


@pytest.mark.parametrize("cell_text", [" leading\n", "trailing \n", "\tleading\n"])
@pytest.mark.parametrize("tab_body", [False, True])
def test_unrenderable_table_refuses_and_names_table(capsys, cell_text, tab_body):
    from gdoc.api.docs import get_tab_text

    scope = {"body": {"content": [{"startIndex": 7, "table": {
        "tableRows": [{"tableCells": [
            body({"textRun": {"content": cell_text}}), PLAIN,
        ]}],
    }}]}}
    assert "\told\n" in get_tab_text(scope, markdown=True)
    with pytest.raises(GdocError, match="table at index 7"):
        check_markdown_replacement(scope, tab_body=tab_body)
    check_markdown_replacement(scope, tab_body=tab_body, allow_lossy=True)
    assert "will discard: table at index 7" in capsys.readouterr().err


def test_numbering_resumed_after_unordered_item_refuses(mocker):
    from gdoc.api.docs import get_tab_text

    target = numbered_tab(["first", "bullet", "first"])
    scope = target["documentTab"]
    scope["lists"]["bullet"]["listProperties"]["nestingLevels"] = [{}]
    markdown = get_tab_text(scope, markdown=True)
    assert markdown == "1. item\n- item\n1. item\n"
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [target],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    with pytest.raises(GdocError, match="numbered list 'first' resumes"):
        insert_markdown_into_tab("doc", "target", markdown, replace=True)
    service.documents.return_value.batchUpdate.assert_not_called()


@pytest.mark.parametrize("glyph_type", ["GLYPH_TYPE_UNSPECIFIED", "DECIMAL"])
def test_empty_list_item_refuses_before_mutation(mocker, glyph_type):
    from gdoc.api.docs import get_tab_text

    target = numbered_tab(["empty"], glyph_type=glyph_type)
    scope = target["documentTab"]
    scope["body"]["content"][0]["paragraph"]["elements"] = [
        {"textRun": {"content": "\n"}},
    ]
    assert get_tab_text(scope, markdown=True) == "\n"
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [target],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    with pytest.raises(GdocError, match="empty list item.*empty"):
        insert_markdown_into_tab("doc", "target", "new", replace=True)
    service.documents.return_value.batchUpdate.assert_not_called()


@pytest.mark.parametrize("header_styles", [({}, {}), ({"bold": True}, {}),
                                           ({"bold": True}, {"bold": False})])
@pytest.mark.parametrize("allow_lossy", [False, True])
def test_plain_or_mixed_table_header_requires_opt_in(
    mocker, capsys, header_styles, allow_lossy,
):
    from gdoc.api.docs import get_tab_text

    header = body({"textRun": {"content": "first", "textStyle": header_styles[0]}})
    header["content"][0]["paragraph"]["elements"].append(
        {"textRun": {"content": " second\n", "textStyle": header_styles[1]}},
    )
    scope = {"content": [{"startIndex": 7, "endIndex": 30, "table": {
        "tableRows": [{"tableCells": [header, body({"textRun": {
            "content": "bold\n", "textStyle": {"bold": True},
        }})]}, {"tableCells": [PLAIN, PLAIN]}],
    }}]}
    target = tab("target", scope)
    markdown = get_tab_text(target["documentTab"], markdown=True)
    assert "| --- | --- |" in markdown
    mocker.patch("gdoc.api.docs.get_document_with_tabs", return_value={
        "revisionId": "r", "tabs": [target],
    })
    service = mocker.patch("gdoc.api.docs.get_docs_service").return_value
    table_insert = mocker.patch("gdoc.api.docs._insert_table")
    if allow_lossy:
        insert_markdown_into_tab(
            "doc", "target", markdown, replace=True, allow_lossy=True,
        )
        service.documents.return_value.batchUpdate.assert_called_once()
        table_insert.assert_called_once()
        assert "table at index 7" in capsys.readouterr().err
    else:
        with pytest.raises(GdocError, match="table at index 7.*header") as exc:
            insert_markdown_into_tab("doc", "target", markdown, replace=True)
        assert exc.value.exit_code == 3
        assert "--allow-lossy" in str(exc.value)
        service.documents.return_value.batchUpdate.assert_not_called()
        table_insert.assert_not_called()
        with pytest.raises(GdocError, match="table at index 7.*header"):
            check_markdown_replacement(scope)
