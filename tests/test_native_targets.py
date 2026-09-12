"""Offline regressions using invented Docs API structures and UTF-16 indices."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from gdoc.api import docs
from gdoc.cli import cmd_edit
from gdoc.util import GdocError


@pytest.fixture(autouse=True)
def no_network(mocker):
    def forbidden(*args, **kwargs):
        pytest.fail("Native target tests must remain offline")

    mocker.patch("socket.socket.connect", side_effect=forbidden)
    mocker.patch.object(docs, "get_docs_service", side_effect=forbidden)


def paragraph(text, start):
    end = start + len(text.encode("utf-16-le")) // 2
    return {"startIndex": start, "endIndex": end, "paragraph": {"elements": [
        {"startIndex": start, "endIndex": end, "textRun": {"content": text}},
    ]}}


def table(rows, start=1):
    """Build a synthetic table with the API's table/row/cell index gaps."""
    cursor = start + 1
    table_rows = []
    for values in rows:
        row_start = cursor
        cursor += 1
        cells = []
        for text in values:
            para = paragraph(text, cursor + 1)
            cells.append({"startIndex": cursor, "endIndex": para["endIndex"],
                          "content": [para]})
            cursor = para["endIndex"]
        table_rows.append({"startIndex": row_start, "endIndex": cursor,
                           "tableCells": cells})
    return {"startIndex": start, "endIndex": cursor,
            "table": {"tableRows": table_rows}}


def raw_tab(tab_id, title, children=()):
    return {"tabProperties": {"tabId": tab_id, "title": title},
            "documentTab": {"body": {"content": [paragraph("\n", 1)]}},
            "childTabs": list(children)}


@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize(("query", "expected"), [
    ("target-id", "target-id"), ("notes", "lower-id"),
    ("Notes", "target-id"), ("unique", "unique-id"),
])
def test_tab_identity_precedes_title_and_case_fallback(raw, query, expected):
    tabs = [raw_tab("decoy-id", "target-id"),
            raw_tab("target-id", "Notes", [raw_tab("lower-id", "notes")]),
            raw_tab("unique-id", "Unique")]
    before = deepcopy(tabs)
    if raw:
        result = docs.resolve_raw_tab(tabs, query)["tabProperties"]["tabId"]
    else:
        result = docs.resolve_tab(docs.flatten_tabs(tabs), query)["id"]
    assert result == expected
    assert tabs == before


@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize(("titles", "query"), [
    (("Notes", "Notes"), "Notes"), (("Notes", "notes"), "NOTES"),
])
def test_ambiguous_tab_lists_every_candidate(raw, titles, query):
    tabs = [raw_tab("parent-id", titles[0], [raw_tab("child-id", titles[1])])]
    resolver = docs.resolve_raw_tab if raw else docs.resolve_tab
    with pytest.raises(GdocError, match="ambiguous tab") as exc:
        resolver(tabs if raw else docs.flatten_tabs(tabs), query)
    assert exc.value.exit_code == 3
    for candidate in (*titles, "parent-id", "child-id"):
        assert candidate in str(exc.value)


def test_value_cell_does_not_identify_its_neighbour():
    body = {"content": [table([["Label\n", "Value\n", "Keep\n"]])]}
    assert docs.resolve_cell_range(body, "Value") is None
    assert docs.resolve_cell_range(body, "Value", col=2) is None
    assert docs.resolve_cell_range(body, "Label", col=2) == {
        "startIndex": 18, "endIndex": 22,
    }


@pytest.mark.parametrize("separate_tables", [False, True])
def test_duplicate_labels_require_explicit_coordinates(separate_tables):
    rows = [["Label\n", "First\n"], ["Label\n", "Second\n"]]
    content = ([table(rows[:1]), table(rows[1:], start=30)] if separate_tables
               else [table(rows)])
    body = {"content": content}
    with pytest.raises(GdocError, match="ambiguous cell label") as exc:
        docs.resolve_cell_range(body, "Label")
    assert exc.value.exit_code == 3
    assert "table 0 row 0" in str(exc.value)
    assert ("table 1 row 0" if separate_tables else "table 0 row 1") in str(exc.value)
    ti, ri = (1, 0) if separate_tables else (0, 1)
    assert docs.resolve_cell_range(body, f"{ri},1", table_index=ti)
    if separate_tables:
        assert docs.resolve_cell_range(body, "Label", table_index=ti)
    else:
        with pytest.raises(GdocError, match="ambiguous cell label"):
            docs.resolve_cell_range(body, "Label", table_index=ti)


def test_normalized_labels_are_checked_for_ambiguity():
    body = {"content": [table([["Team’s note\n", "First\n"],
                               ["Team's note\n", "Second\n"]])]}
    assert docs.resolve_cell_range(body, "Team's note")
    with pytest.raises(GdocError, match="ambiguous cell label"):
        docs.resolve_cell_range(body, "Team's note", normalize=True)


def edit_args(**kwargs):
    args = dict(doc="synthetic-doc", old_text="replacement", new_text=None,
                old_file=None, new_file=None, cell="Label", col=None, table=None,
                tab=None, quiet=True, plain=False, case_sensitive=False,
                normalize=False, json=False, verbose=False)
    args.update(kwargs)
    return SimpleNamespace(**args)


def test_ambiguous_cell_edit_refuses_before_mutation(mocker):
    document = {"body": {"content": [table([["Label\n", "First\n"],
                                             ["Label\n", "Second\n"]])]}}
    mocker.patch("gdoc.notify.pre_flight", return_value=None)
    mocker.patch.object(docs, "get_document", return_value=document)
    replace = mocker.patch.object(docs, "replace_formatted")
    with pytest.raises(GdocError, match="ambiguous cell label") as exc:
        cmd_edit(edit_args())
    assert exc.value.exit_code == 3
    replace.assert_not_called()


@pytest.mark.parametrize("native", [
    {"inlineObjectElement": {"inlineObjectId": "synthetic-image"}},
    {"footnoteReference": {"footnoteId": "synthetic-footnote"}},
])
def test_inline_native_objects_split_search_segments(native):
    document = {"body": {"content": [{"paragraph": {"elements": [
        {"startIndex": 1, "endIndex": 5, "textRun": {"content": "Left"}},
        {"startIndex": 5, "endIndex": 6, **native},
        {"startIndex": 6, "endIndex": 12, "textRun": {"content": "Right\n"}},
    ]}}]}}
    before = deepcopy(document)
    assert docs.find_text_in_document(document, "LeftRight") == []
    assert docs.find_text_in_document(document, "Right") == [
        {"startIndex": 6, "endIndex": 11},
    ]
    assert document == before


@pytest.mark.parametrize("allow_native_gaps", [False, True])
def test_table_splits_outer_paragraphs_and_cells(allow_native_gaps):
    middle = table([["Cell\n"]], start=6)
    end = middle["endIndex"]
    document = {"body": {"content": [paragraph("Left\n", 1), middle,
                                       paragraph("Right\n", end)]}}
    kwargs = {"allow_native_gaps": allow_native_gaps}
    for needle in ("Left\nRight", "Left\nCell", "Cell\nRight"):
        assert docs.find_text_in_document(document, needle, **kwargs) == []
    assert docs.find_text_in_document(document, "Right", **kwargs) == [
        {"startIndex": end, "endIndex": end + 5},
    ]
    assert docs.find_text_in_document(document, "Cell", **kwargs) == [
        {"startIndex": 9, "endIndex": 13},
    ]


def test_nested_table_splits_surrounding_cell_text():
    nested = table([["Nested\n"]], start=10)
    end = nested["endIndex"]
    cell = {"content": [paragraph("Before\n", 3), nested, paragraph("After\n", end)]}
    document = {"body": {"content": [{"table": {"tableRows": [
        {"tableCells": [cell]},
    ]}}]}}
    assert docs.find_text_in_document(document, "Before\nAfter") == []
    assert docs.find_text_in_document(document, "Nested") == [
        {"startIndex": 13, "endIndex": 19},
    ]
    with pytest.raises(GdocError, match="non-text content"):
        docs._cell_text_range(cell)


@pytest.mark.parametrize("explicit_block", [False, True])
def test_structural_gaps_cannot_be_searched_through(explicit_block):
    content = [paragraph("Left\n", 1)]
    if explicit_block:
        content.append({"startIndex": 6, "endIndex": 7,
                        "sectionBreak": {"sectionStyle": {}}})
    content.append(paragraph("Right\n", 7))
    assert docs.find_text_in_document({"body": {"content": content}},
                                      "Left\nRight") == []


def test_adjacent_paragraphs_and_style_runs_remain_searchable():
    first = paragraph("Left\n", 1)
    first["paragraph"]["elements"] = [
        {"startIndex": 1, "endIndex": 3, "textRun": {"content": "Le"}},
        {"startIndex": 3, "endIndex": 6,
         "textRun": {"content": "ft\n", "textStyle": {"bold": True}}},
    ]
    document = {"body": {"content": [first, paragraph("Right\n", 6)]}}
    assert docs.find_text_in_document(document, "Left\nRight") == [
        {"startIndex": 1, "endIndex": 11},
    ]


@pytest.mark.parametrize("cell_address", ["0,1", "Label"])
@pytest.mark.parametrize("object_type", ["inline", "footnote", "positioned"])
def test_cell_native_object_refuses_before_mutation(mocker, cell_address, object_type):
    grid = table([["Label\n", "Before\n"]])
    cell = grid["table"]["tableRows"][0]["tableCells"][1]
    start = cell["endIndex"]
    para = paragraph("\n", start + 1)
    if object_type == "positioned":
        # Positioned objects consume no native character position.
        para = paragraph("\n", start)
        para["paragraph"]["positionedObjectIds"] = ["synthetic-drawing"]
    else:
        native = ({"inlineObjectElement": {"inlineObjectId": "synthetic-image"}}
                  if object_type == "inline" else
                  {"footnoteReference": {"footnoteId": "synthetic-footnote"}})
        para["startIndex"] = start
        para["paragraph"]["elements"].insert(0, {
            "startIndex": start, "endIndex": start + 1, **native,
        })
    cell["content"].extend([para, paragraph("After\n", para["endIndex"])])
    cell["endIndex"] = cell["content"][-1]["endIndex"]
    grid["table"]["tableRows"][0]["endIndex"] = cell["endIndex"]
    grid["endIndex"] = cell["endIndex"]
    document = {"body": {"content": [grid]}}
    before = deepcopy(document)
    mocker.patch("gdoc.notify.pre_flight", return_value=None)
    mocker.patch.object(docs, "get_document", return_value=document)
    replace = mocker.patch.object(docs, "replace_formatted")
    with pytest.raises(GdocError, match="cell contains non-text content") as exc:
        cmd_edit(edit_args(cell=cell_address))
    assert exc.value.exit_code == 3
    replace.assert_not_called()
    assert document == before


def test_whole_cell_refuses_an_unexplained_native_gap():
    cell = {"content": [paragraph("Left\n", 3), paragraph("Right\n", 9)]}
    with pytest.raises(GdocError, match="structural gap"):
        docs._cell_text_range(cell)


def test_cross_table_edit_refuses_before_mutation(mocker):
    middle = table([["Cell\n"]], start=6)
    document = {"body": {"content": [paragraph("Left\n", 1), middle,
                                       paragraph("Right\n", middle["endIndex"])]}}
    mocker.patch("gdoc.notify.pre_flight", return_value=None)
    mocker.patch.object(docs, "get_document", return_value=document)
    replace = mocker.patch.object(docs, "replace_formatted")
    with pytest.raises(GdocError, match="no match found") as exc:
        cmd_edit(edit_args(cell=None, old_text="Left\nRight", new_text="Joined"))
    assert exc.value.exit_code == 3
    replace.assert_not_called()
