"""Known native structures that Markdown replacement cannot round-trip.

Scan only the caller's replacement scope. See README's hazard inventory;
ordinary styles and metadata are deliberately not a reason to refuse.
"""

import sys

from gdoc.util import GdocError

_ELEMENTS = {
    "person": "people chips",
    "richLink": "rich-link chips",
    "dateElement": "date chips",
    "inlineObjectElement": "inline images or embedded objects",
    "positionedObjectIds": "positioned objects",
    "footnoteReference": "footnotes",
    "equation": "equations",
    "autoText": "automatic text (such as page numbers)",
    "tableOfContents": "generated tables of contents",
    "pageBreak": "page breaks",
    "columnBreak": "column breaks",
}


# These fields contain ID/name -> object maps, not schema-keyed objects.
_MAP_FIELDS = {
    "headers", "footers", "footnotes", "inlineObjects", "positionedObjects",
    "lists", "namedRanges",
}


def _custom_section_layout(style: dict, document_style: dict) -> bool:
    """Recognize layout overrides without flagging the default section marker."""
    columns = style.get("columnProperties", [])
    if len(columns) > 1 or any(
        c.get("paddingEnd", {}).get("magnitude", 0) for c in columns
    ):
        return True
    for key, default in (
        ("columnSeparatorStyle", "NONE"),
        ("contentDirection", "LEFT_TO_RIGHT"),
        ("sectionType", "CONTINUOUS"),
    ):
        value = style.get(key, default)
        if value != default and not value.endswith("_UNSPECIFIED"):
            return True
    defaults = {"flipPageOrientation": False,
                "useFirstPageHeaderFooter": False, "pageNumberStart": 1}
    for key in (
        "marginTop", "marginBottom", "marginLeft", "marginRight",
        "marginHeader", "marginFooter", "flipPageOrientation",
        "useFirstPageHeaderFooter", "pageNumberStart",
    ):
        if key in style and style[key] != document_style.get(key, defaults.get(key)):
            return True
    return False


# Bounded, observed Drive-import defaults; this is not an unknown-field denylist.
_IMPORT_PAGE_SETUP = {
    "pageSize": {"height": {"magnitude": 792, "unit": "PT"},
                 "width": {"magnitude": 612, "unit": "PT"}},
    **{name: {"magnitude": 72, "unit": "PT"} for name in
       ("marginTop", "marginBottom", "marginLeft", "marginRight")},
    **{name: {"magnitude": 36, "unit": "PT"} for name in
       ("marginHeader", "marginFooter")},
    "documentFormat": {"documentMode": "PAGES"},
    "background": {"color": {}},
    "pageNumberStart": 1,
    "useCustomHeaderFooterMargins": False,
    "useFirstPageHeaderFooter": False,
    "flipPageOrientation": False,
}
_TEXT_STYLE_LOSSES = {
    "foregroundColor": "colour", "backgroundColor": "highlight",
    "underline": "underline", "smallCaps": "small caps", "fontSize": "font size",
    "weightedFontFamily": "font family", "baselineOffset": "baseline",
}
_PARAGRAPH_STYLE_LOSSES = {
    "alignment": "alignment", "lineSpacing": "line spacing",
    "spaceAbove": "paragraph spacing", "spaceBelow": "paragraph spacing",
    "keepWithNext": "paragraph layout", "keepLinesTogether": "paragraph layout",
    "avoidWidowAndOrphan": "paragraph layout", "pageBreakBefore": "paragraph layout",
    "indentStart": "indentation", "indentEnd": "indentation",
    "indentFirstLine": "indentation", "tabStops": "tab stops",
}


def _numbered_list_hazards(content: list, lists: dict) -> set[str]:
    """Find numbering boundaries and starts reconstruction cannot preserve."""
    from gdoc.api.docs import _list_is_ordered, _runs_markdown

    hazards = set()
    run = set()
    seen = set()
    for element in content:
        paragraph = element.get("paragraph", {})
        bullet = paragraph.get("bullet")
        if bullet is None:
            run.clear()
            continue
        list_id = bullet.get("listId", "")
        if not _runs_markdown(paragraph.get("elements", [])).strip():
            hazards.add(f"empty list item in list {list_id!r} (omitted by export)")
            run.clear()
            continue
        level = bullet.get("nestingLevel", 0)
        if not _list_is_ordered(lists, list_id, level):
            run.clear()
            continue
        start = lists[list_id]["listProperties"]["nestingLevels"][level].get(
            "startNumber", 1,
        )
        if start != 1:
            hazards.add(f"numbered list {list_id!r} starts at {start} (reset to 1)")
        if run - {list_id}:
            names = ", ".join(repr(name) for name in sorted(run | {list_id}))
            hazards.add(f"adjacent or interleaved numbered lists {names}")
        if list_id in seen and list_id not in run:
            hazards.add(f"numbered list {list_id!r} resumes after a break")
        run.add(list_id)
        seen.add(list_id)
    return hazards


def _table_header_adds_bold(table: dict) -> bool:
    """Pipe-table reconstruction bolds all text except the final cell newline."""
    for cell in table["tableRows"][0]["tableCells"]:
        runs = [element["textRun"]
                for block in cell.get("content", [])
                for element in block.get("paragraph", {}).get("elements", [])
                if element.get("textRun", {}).get("content")]
        for index, run in enumerate(runs):
            text = run["content"]
            if index == len(runs) - 1:
                text = text.removesuffix("\n")
            if text and not run.get("textStyle", {}).get("bold"):
                return True
    return False


def check_markdown_replacement(
    scope: dict, *, tab_body: bool = False, allow_lossy: bool = False,
) -> None:
    """Refuse known lossy structures in a body or a complete Docs response."""
    from gdoc.api.docs import _table_markdown

    hazards: set[str] = set()
    styles: set[str] = set()

    def visit(value, table_depth=0, document_style=None, lists=None):
        """Collect known hazards recursively, tracking nested table depth."""
        if isinstance(value, list):
            for item in value:
                visit(item, table_depth, document_style, lists)
        elif isinstance(value, dict):
            # Each documentTab owns its defaults; recursive calls keep them
            # local so a sibling or child tab cannot inherit the wrong style.
            document_style = value.get("documentStyle", document_style or {})
            lists = value.get("lists", {} if "body" in value else lists or {})
            if "content" in value and isinstance(value["content"], list):
                hazards.update(_numbered_list_hazards(value["content"], lists))
            if "sectionBreak" in value:
                # Tab deletion starts at 1: the initial [0, 1) marker and
                # its section style survive, even in an otherwise blank tab.
                initial = value.get("startIndex", 0) == 0
                if tab_body and initial and value.get("endIndex", 1) <= 1:
                    return
                style = value["sectionBreak"].get("sectionStyle", {})
                if not initial or _custom_section_layout(
                    style, document_style,
                ):
                    hazards.add("section boundaries or custom section layout")
            if not tab_body:
                title = value.get("tabProperties", {}).get("title")
                if title and title != "Tab 1":
                    hazards.add(f"tab title {title!r} (import resets it to 'Tab 1')")
                page_style = value.get("documentStyle", {})
                if any(page_style.get(key, default) != default
                       for key, default in _IMPORT_PAGE_SETUP.items()):
                    hazards.add("page setup "
                                "(import resets page size, margins or page mode)")
            for field, label in _TEXT_STYLE_LOSSES.items():
                if field in value.get("textStyle", {}):
                    styles.add(label)
            for field, label in _PARAGRAPH_STYLE_LOSSES.items():
                if field in value.get("paragraphStyle", {}):
                    styles.add(label)
            if value.get("listProperties"):
                styles.add("list glyphs and list styling")
            for key, child in value.items():
                # Empty objects are valid paragraph-element markers (equation,
                # pageBreak, etc.); empty reference lists are not hazards.
                if key in _ELEMENTS and child is not None and child != []:
                    hazards.add(_ELEMENTS[key])
                if tab_body and key == "horizontalRule":
                    hazards.add("native horizontal rules (omitted by tab export)")
                if key.startswith("suggested") and child:
                    hazards.add("pending suggestions")
                if key == "link" and isinstance(child, dict) and any(
                    k in child for k in (
                        "bookmarkId", "headingId", "tabId",
                        "bookmark", "heading",
                    )
                ):
                    hazards.add("internal document links")
                if key == "table":
                    if table_depth:
                        hazards.add("nested tables")
                    index = value.get("startIndex", "unknown")
                    if _table_markdown(child) is None:
                        hazards.add(
                            f"table at index {index} (cannot export as a pipe table)"
                        )
                    elif _table_header_adds_bold(child):
                        hazards.add(
                            f"table at index {index} (header row gains bold formatting)"
                        )
                if key in ("rowSpan", "columnSpan") and child > 1:
                    hazards.add("merged table cells")
                if not tab_body and key in ("headers", "footers", "footnotes"):
                    if child:
                        hazards.add(key)
                if isinstance(child, dict) and (
                    key in _MAP_FIELDS or key.startswith("suggested")
                ):
                    # Map entry names are arbitrary, including "person" or
                    # "rowSpan"; only their values have Docs schema fields.
                    visit(list(child.values()), table_depth, document_style, lists)
                else:
                    visit(child, table_depth + (key == "table"), document_style, lists)

    visit(scope)
    if hazards and not allow_lossy:
        where = "selected tab body" if tab_body else "whole document"
        raise GdocError(
            f"Markdown replacement refused: {where} contains "
            + ", ".join(sorted(hazards))
            + ". No content was written. Use targeted edits to preserve native "
            "content, or pass --allow-lossy to knowingly discard it. "
            "--force only bypasses conflicts; --force-collapse-tabs only "
            "allows tab collapse.",
            exit_code=3,
        )
    if hazards:
        print("WARN: Markdown replacement will discard: " +
              ", ".join(sorted(hazards)), file=sys.stderr)
    if styles:
        print("WARN: Markdown replacement may reset styles: " +
              ", ".join(sorted(styles)), file=sys.stderr)
