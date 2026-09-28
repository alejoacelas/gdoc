"""Known native structures that Markdown replacement cannot round-trip.

Scan only the caller's replacement scope. See README's hazard inventory;
ordinary styles and metadata are deliberately not a reason to refuse.
"""

import re
import sys
from dataclasses import dataclass, field

from gdoc.util import GdocError

# gdoc's own container ranges (see gdoc.api.docs._prefix_range_name).
_PREFIX_NAME = (r"gdoc:prefix:(?:v1:\d+:\d+|v2:\d+:\d+:\d+"
                r"|v3:(?:q|\d+)(?:\.(?:q|\d+))*)")

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


def _link_blue(colour: dict) -> bool:
    """Whether a foreground colour is Docs' default link colour."""
    from gdoc.api.docs import _LINK_BLUE

    if not isinstance(colour, dict):
        return False
    rgb = colour.get("color", {}).get("rgbColor", {})
    return all(abs(rgb.get(key, 0) - value) < 0.002
               for key, value in zip(("red", "green", "blue"), _LINK_BLUE))


def _indented(paragraph: dict) -> bool:
    """Whether a paragraph has a start or first-line indent."""
    style = paragraph.get("paragraphStyle", {})
    return any((style.get(key) or {}).get("magnitude", 0) > 0
               for key in ("indentStart", "indentFirstLine"))


def _table_style_losses(table: dict) -> set[str]:
    """Visual table styling a pipe table cannot carry: warned, not refused.

    Docs' defaults (no shading, 1pt solid black borders, evenly distributed
    columns) are not reported.
    """
    losses = set()
    for row in table.get("tableRows", []):
        for cell in row.get("tableCells", []):
            style = cell.get("tableCellStyle", {})
            # An empty backgroundColor is no shading; any rgbColor, even an
            # empty one (black, its zero components omitted), is shading.
            if "rgbColor" in style.get("backgroundColor", {}).get("color", {}):
                losses.add("table cell shading")
            for side in ("borderLeft", "borderRight", "borderTop", "borderBottom"):
                border = style.get(side)
                # A width whose magnitude is omitted is 0pt (the API omits
                # zero values); only a missing width is the 1pt default.
                width = (border or {}).get("width")
                if border and (
                    (width is not None and width.get("magnitude", 0) != 1)
                    or border.get("dashStyle", "SOLID") != "SOLID"
                    or any(border.get("color", {}).get("color", {})
                           .get("rgbColor", {}).values())
                ):
                    losses.add("table borders")
    for row in table.get("tableRows", []):
        row_style = row.get("tableRowStyle", {})
        if (row_style.get("minRowHeight") or {}).get("magnitude", 0) > 0:
            losses.add("table row heights")
        if row_style.get("preventOverflow") or row_style.get("tableHeader"):
            losses.add("table row settings (header rows, rows kept on one page)")
        for cell in row.get("tableCells", []):
            if cell.get("tableCellStyle", {}).get("contentAlignment") in (
                    "MIDDLE", "BOTTOM"):
                losses.add("table cell vertical alignment")
    if any(column.get("widthType") == "FIXED_WIDTH"
           for column in table.get("tableStyle", {}).get("tableColumnProperties", [])):
        losses.add("table column widths")
    return losses


def _numbered_list_hazards(content: list, lists: dict) -> set[str]:
    """Find numbering boundaries and starts reconstruction cannot preserve."""
    from gdoc.api.docs import _indent_nesting_level, _list_is_ordered

    hazards = set()
    run = {}
    seen = set()
    for element in content:
        paragraph = element.get("paragraph", {})
        bullet = paragraph.get("bullet")
        if bullet is None:
            continue
        list_id = bullet.get("listId", "")
        native_level = bullet.get("nestingLevel", 0)
        definitions = lists.get(list_id, {}).get("listProperties", {}).get(
            "nestingLevels", [],
        )
        definition = (definitions[native_level]
                      if native_level < len(definitions) else {})
        indent = paragraph.get("paragraphStyle", {}).get(
            "indentStart", definition.get("indentStart", {}),
        )
        level = _indent_nesting_level(native_level, indent, definitions)
        for deeper in [key for key in run if key > level]:
            del run[deeper]
        if not _list_is_ordered(lists, list_id, native_level):
            continue
        start = definition.get("startNumber", 1)
        if start != 1:
            hazards.add(f"numbered list {list_id!r} starts at {start} (reset to 1)")
        previous = run.get(level)
        identity = (list_id, native_level)
        if identity in seen and previous != list_id:
            hazards.add(f"numbered list {list_id!r} resumes after a break")
        run[level] = list_id
        seen.add(identity)
    return hazards



SUGGESTIONS = "pending suggestions"
IMAGE_CROP = "image crop"
IMAGE_ADJUSTMENTS = "image rotation, brightness, contrast, transparency or border"
# Style labels a rewrite loses that refuse below the markdown policy, like
# rich content. Moving a label out of here makes it an ordinary style loss.
PROTECTED_STYLES = {IMAGE_CROP}


def _image_cropped(embedded: dict) -> bool:
    return any((embedded.get("imageProperties", {})
                .get("cropProperties") or {}).values())


def _image_adjusted(embedded: dict) -> bool:
    image = embedded.get("imageProperties", {})
    border = embedded.get("embeddedObjectBorder", {})
    return (any(image.get(key) for key in (
                "angle", "brightness", "contrast", "transparency"))
            or border.get("propertyState") == "RENDERED")


# Existing targeted routes, named before any rewrite in refusals and help.
TARGETED_ROUTES = (
    "Targeted commands keep it all: `edit` changes wording (`edit --cell` "
    "fills a table cell, `suggest` proposes a reviewable change), `insert` "
    "adds Markdown at the start or end of a tab, and `insert-image` and "
    "`replace-image` change images."
)
REWRITE_COST = "A rewrite (`write`, `push`) deletes and reinserts the whole tab"
POLICY_HELP = (
    "The rewrite policy is a human configuration choice: `gdoc config "
    "--rewrite-policy LEVEL` (config key rewrite_policy) or the "
    "GDOC_REWRITE_POLICY environment variable."
)


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}{'' if count == 1 else 's'}"


@dataclass
class RewriteLosses:
    """What a changed full-tab rewrite of one scope would lose.

    CLI, MCP, push and the sync hook all build this through
    ``check_markdown_replacement``, so they refuse and report identically.
    Protected losses (rich content, suggestions, comments, image crop)
    refuse below the ``markdown`` policy; formatting losses (direct styles,
    image alt text and adjustments, numbering starts) refuse only under
    ``strict``.
    """

    content: list[str] = field(default_factory=list)
    suggestions: int = 0
    comments: int = 0
    comments_exact: bool = True
    protected_styles: list[tuple[str, int, str]] = field(default_factory=list)
    styles: list[tuple[str, int, str]] = field(default_factory=list)
    paragraphs: int = 0
    numbering: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.protected() or self.formatting())

    def suggestion_text(self) -> str:
        count = f" ({self.suggestions})" if self.suggestions > 0 else ""
        return "collaborators' pending suggestions" + count

    def comment_text(self) -> str:
        # Drive lists a comment whose text is gone as still anchored and does
        # not name a comment's tab, so the count is an upper bound.
        where = ("" if self.comments_exact else
                 "; Drive does not say which tab a comment is in, so this "
                 "counts every anchored comment in the document")
        return (f"up to {_plural(self.comments, 'comment')} anchored in the "
                f"tab (open or resolved{where})")

    def style_text(self, rows=None) -> str:
        return ", ".join(
            f"{label} on {count} of {_plural(self.paragraphs, 'paragraph')}"
            if unit == "paragraphs"
            else f"{label} on {_plural(count, unit[:-1])}"
            for label, count, unit in (self.styles if rows is None else rows)
        )

    def protected(self) -> list[str]:
        items = list(self.content)
        if self.suggestions:
            items.append(self.suggestion_text())
        if self.comments:
            items.append(self.comment_text() + ", which will detach")
        if self.protected_styles:
            items.append(self.style_text(self.protected_styles)
                         + " (the image shows its uncropped original)")
        return items

    def formatting(self) -> list[str]:
        items = []
        if self.styles:
            items.append("direct styles (" + self.style_text() + ")")
        items.extend(f"native numbering ({item})" for item in self.numbering)
        return items

    def to_json(self) -> dict:
        result: dict = {}
        if self.content:
            result["content"] = self.content
        if self.suggestions:
            # -1: the scan found suggestions it could not count.
            result["pending_suggestions"] = (
                self.suggestions if self.suggestions > 0 else None)
            result["pending_suggestions_counted"] = self.suggestions > 0
        if self.comments:
            result["comments"] = self.comments
            result["comments_scope"] = "tab" if self.comments_exact else "document"
        if self.styles or self.protected_styles:
            result["styles"] = [
                {"style": label, unit: count,
                 "protected": label in PROTECTED_STYLES}
                for label, count, unit in self.protected_styles + self.styles]
            result["paragraphs"] = self.paragraphs
        if self.numbering:
            result["numbering"] = self.numbering
        return result


def rewrite_losses(scope: dict, *, tab_body: bool = False,
                   removed: dict | None = None) -> RewriteLosses:
    """The loss inventory of rewriting *scope* from its Markdown.

    *removed* holds further segments the rewrite deletes (the footnotes its
    body references); their pending suggestions count too.
    """
    from gdoc.api.docs import pending_suggestion_ids

    extent: dict = {}
    hazards, styles, numbering = markdown_hazards(
        scope, tab_body=tab_body, extent=extent)
    rows = []
    for label in sorted(styles):
        keys = extent.get(label, set())
        kinds = {key[0] for key in keys}
        if len(kinds) == 1 and kinds != {"paragraph"}:
            rows.append((label, len(keys), kinds.pop() + "s"))
        else:
            rows.append((label, sum(key[0] == "paragraph" for key in keys),
                         "paragraphs"))
    # Style-metadata suggestions are not content the scan reports.
    ids = (pending_suggestion_ids(scope.get("body", scope))
           if SUGGESTIONS in hazards else set()) | (
        pending_suggestion_ids(removed) if removed else set())
    suggestions = len(ids)
    if SUGGESTIONS in hazards and not suggestions:
        suggestions = -1  # found by the scan but not countable: "some"
    return RewriteLosses(
        content=sorted(hazards - {SUGGESTIONS}), suggestions=suggestions,
        protected_styles=[r for r in rows if r[0] in PROTECTED_STYLES],
        styles=[r for r in rows if r[0] not in PROTECTED_STYLES],
        paragraphs=len(extent.get("", ())),
        numbering=sorted(numbering),
    )


def check_markdown_replacement(
    scope: dict, *, tab_body: bool = False, allow_lossy: bool = False,
    discard_suggestions: bool = False, comments: int = 0,
    comments_exact: bool = True, policy: str | None = None,
    where: str | None = None, removed: dict | None = None,
    deleting: bool = False,
) -> RewriteLosses:
    """Refuse or report what rewriting *scope* from Markdown would lose.

    The rewrite policy is a ceiling that per-call flags cannot exceed:

    - ``strict``: any loss refuses.
    - ``formatting`` (recommended): formatting losses reset with a warning;
      protected losses refuse.
    - ``markdown`` (default): anything may be lost, but rich content still
      needs ``allow_lossy`` and collaborators' pending suggestions still need
      ``discard_suggestions``; comments and image crop warn.

    Returns the inventory after printing its warnings.
    """
    from gdoc.util import get_rewrite_policy

    level = policy or get_rewrite_policy()
    losses = rewrite_losses(scope, tab_body=tab_body, removed=removed)
    if deleting:
        # Deleting a tab removes its headers, footers and footnotes too.
        losses.content = sorted(set(losses.content) | {
            key for key in ("headers", "footers", "footnotes")
            if (removed or {}).get(key)})
    losses.comments, losses.comments_exact = comments, comments_exact
    where = where or (
        "the selected tab body" if tab_body else "the whole document")
    protected, formatting = losses.protected(), losses.formatting()
    blocked = (protected + formatting if level == "strict"
               else protected if level == "formatting" else [])
    if blocked:
        needed = "markdown" if protected else "formatting"
        flags = []
        if needed == "markdown" and losses.content and not deleting:
            flags.append("--allow-lossy")
        if needed == "markdown" and losses.suggestions:
            flags.append("--discard-suggestions")
        raise GdocError(
            f"Markdown replacement refused by rewrite policy '{level}': "
            + (f"--force-collapse-tabs deleting {where}" if deleting
               else f"rewriting {where}")
            + " would lose " + "; ".join(blocked)
            + ". No content was written. "
            + ("" if deleting else _targeted_advice(losses) + " " + REWRITE_COST
               + ". ")
            + f"Rewrite policy '{needed}' would allow it"
            + (" with " + " and ".join(flags) if flags else "") + ". "
            + POLICY_HELP,
            exit_code=3,
        )
    missing, found = [], []
    if losses.content and not allow_lossy:
        found.extend(losses.content)
        missing.append("pass --allow-lossy to discard "
                       + ", ".join(losses.content))
    if losses.suggestions and not discard_suggestions:
        found.append(losses.suggestion_text())
        missing.append("pass --discard-suggestions to discard collaborators' "
                       "pending suggestions (--allow-lossy does not cover them)")
    if missing:
        if deleting:
            raise GdocError(
                f"Markdown replacement refused: {where}, which "
                "--force-collapse-tabs deletes, contains " + ", ".join(found)
                + ". No content was written. Accept or reject the suggestions "
                "in Docs first, or " + " and ".join(missing) + ".",
                exit_code=3,
            )
        raise GdocError(
            f"Markdown replacement refused: {where} contains "
            + ", ".join(found) + ". No content was written. "
            + _targeted_advice(losses) + " " + REWRITE_COST + "; to accept "
            "that, " + " and ".join(missing) + ". --force only bypasses "
            "conflicts; --force-collapse-tabs only allows tab collapse.",
            exit_code=3,
        )
    if deleting and losses:
        print(f"WARN: --force-collapse-tabs deletes {where}, discarding "
              + "; ".join(losses.protected() + losses.formatting()),
              file=sys.stderr)
        return losses
    for line in _warnings(losses):
        print("WARN: " + line, file=sys.stderr)
    return losses


def _warnings(losses: RewriteLosses) -> list[str]:
    lines = []
    if losses.numbering:
        lines.append("Native numbering may reset on reconstruction: "
                     + "; ".join(losses.numbering))
    if losses.content:
        lines.append("Markdown replacement will discard: "
                     + ", ".join(losses.content))
    if losses.suggestions:
        lines.append("Markdown replacement will discard "
                     + losses.suggestion_text() + " and keep the text as shown")
    if losses.comments:
        lines.append("Markdown replacement will detach "
                     + losses.comment_text()
                     + "; Docs shows them as \"Original content deleted\"")
    if losses.protected_styles:
        lines.append("Markdown replacement drops "
                     + losses.style_text(losses.protected_styles)
                     + "; the image shows its uncropped original")
    if losses.styles:
        lines.append("Markdown replacement resets direct styles: "
                     + losses.style_text())
    if len(lines) > (1 if losses.numbering else 0):
        lines.append("Targeted commands (`edit`, `insert`, `edit --cell`, "
                     "`insert-image`, `replace-image`, `suggest`) keep these.")
    return lines


def _targeted_advice(losses: RewriteLosses) -> str:
    if losses.suggestions:
        return "Accept or reject the suggestions in Docs first. " + TARGETED_ROUTES
    return TARGETED_ROUTES


def markdown_hazards(
    scope: dict, *, tab_body: bool = False, extent: dict | None = None,
) -> tuple[set[str], set[str], set[str]]:
    """Content, style and numbering losses of a Markdown round trip of *scope*.

    Content hazards are native content the Markdown cannot represent; reads
    report them as omissions and replacements require consent to lose them.
    When *extent* is a dict, it receives each style label's affected
    paragraphs (or tables) as a set of keys, and ``""`` receives every
    paragraph in the scope.
    """
    from gdoc.api.docs import _table_markdown

    hazards: set[str] = set()
    styles: set[str] = set()
    numbering: set[str] = set()

    def note(label, where):
        styles.add(label)
        if extent is not None and where is not None:
            extent.setdefault(label, set()).add(where)

    # A value that reads as "no style" (false, zero, single spacing) is still
    # an override when the paragraph's named style sets something else, and
    # reconstruction drops it.
    named_defaults = {
        "styles": (scope.get("namedStyles") or {}).get("styles", [])}
    kinds = {}

    def overrides_default(kind, field, value, where):
        style_type = kinds.get(where, "NORMAL_TEXT")
        default = next((style.get(kind, {}).get(field)
                        for style in named_defaults["styles"]
                        if style.get("namedStyleType") == style_type), None)
        if default in (None, False, {}, []) or default == value:
            return False
        if field == "lineSpacing" and default == 100 and value in (None, 100):
            return False
        if isinstance(default, dict) and "magnitude" in default and (
                default.get("magnitude", 0) == (value or {}).get("magnitude", 0)):
            return False
        return True

    def visit(value, table_depth=0, document_style=None, lists=None, images=None,
              prefixes=None, supported_prefix=False, paragraph=None):
        """Collect known hazards recursively, tracking nested table depth."""
        if isinstance(value, list):
            for item in value:
                visit(item, table_depth, document_style, lists, images,
                      prefixes, supported_prefix, paragraph)
        elif isinstance(value, dict):
            if "namedStyles" in value:
                named_defaults["styles"] = (
                    value["namedStyles"] or {}).get("styles", [])
            if "paragraph" in value:
                paragraph = ("paragraph", id(value))
                kinds[paragraph] = (value["paragraph"] or {}).get(
                    "paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
                if extent is not None:
                    extent.setdefault("", set()).add(paragraph)
            # Each documentTab owns its defaults; recursive calls keep them
            # local so a sibling or child tab cannot inherit the wrong style.
            document_style = value.get("documentStyle", document_style or {})
            lists = value.get("lists", {} if "body" in value else lists or {})
            images = value.get("inlineObjects", images or {})
            if "body" in value or isinstance(value.get("namedRanges"), dict):
                prefixes = [r for group in value.get("namedRanges", {}).values()
                            for named in group.get("namedRanges", [])
                            if re.fullmatch(_PREFIX_NAME,
                                            named.get("name", group.get("name", "")))
                            for r in named.get("ranges", [])]
            if "paragraph" in value:
                supported_prefix = any(
                    r.get("startIndex", 0) <= value.get("startIndex", -1)
                    < r.get("endIndex", 0) for r in prefixes or []
                )
            if "content" in value and isinstance(value["content"], list):
                numbering.update(_numbered_list_hazards(value["content"], lists))
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
            for field in ("bold", "italic", "strikethrough"):
                # Markdown spells emphasis, not its removal from text whose
                # named style is emphasised.
                if value.get("textStyle", {}).get(field) is False and (
                        overrides_default("textStyle", field, False, paragraph)):
                    note("emphasis removed from a named style", paragraph)
            for field, label in _TEXT_STYLE_LOSSES.items():
                if field in value.get("textStyle", {}):
                    text_style = value["textStyle"]
                    if text_style.get("link") and field in (
                            "foregroundColor", "underline"):
                        # Docs draws a link blue and underlined; only an
                        # author's other colour or removed underline is lost.
                        if field == "underline" and text_style[field] is False:
                            note(label, paragraph)
                        if field == "underline" or _link_blue(text_style[field]):
                            continue
                    if text_style[field] in (None, False, {}):
                        if overrides_default("textStyle", field,
                                             text_style[field], paragraph):
                            note(label, paragraph)
                        continue
                    # Reconstruction writes code in Courier New, so only
                    # that family survives; Consolas and others change.
                    if field == "weightedFontFamily" and value["textStyle"][field].get(
                        "fontFamily",
                    ) == "Courier New":
                        continue
                    note(label, paragraph)
            paragraph_style = value.get("paragraphStyle", {})
            quote = all(paragraph_style.get(key) == {"magnitude": 36, "unit": "PT"}
                        for key in ("indentStart", "indentFirstLine"))
            for field, label in _PARAGRAPH_STYLE_LOSSES.items():
                if field not in paragraph_style:
                    continue
                setting = paragraph_style[field]
                if (setting in (None, False, {}, [])
                        or (field == "lineSpacing" and setting == 100)
                        or (field in ("spaceAbove", "spaceBelow", "indentStart",
                                      "indentEnd", "indentFirstLine")
                            and setting.get("magnitude", 0) == 0)):
                    if overrides_default("paragraphStyle", field, setting,
                                         paragraph):
                        note(label, paragraph)
                    continue
                if field in ("indentStart", "indentFirstLine") and (
                    quote or "bullet" in value or supported_prefix
                ):
                    continue
                if field == "alignment" and table_depth and paragraph_style[field] in (
                    "START", "CENTER", "END",
                ):
                    continue
                note(label, paragraph)
            if paragraph_style.get("shading", {}).get("backgroundColor", {}).get(
                "color",
            ):
                note("paragraph shading", paragraph)
            if any(paragraph_style.get(side, {}).get("width", {}).get("magnitude", 0)
                   > 0 for side in ("borderTop", "borderLeft", "borderRight",
                                    "borderBetween")):
                note("paragraph borders", paragraph)
            if paragraph_style.get("direction") == "RIGHT_TO_LEFT":
                note("right-to-left paragraph direction", paragraph)
            border = paragraph_style.get("borderBottom", {})
            if border.get("width", {}).get("magnitude", 0) > 0:
                text = "".join(e.get("textRun", {}).get("content", "")
                               for e in value.get("elements", []))
                if text.removesuffix("\n"):
                    hazards.add("border-bottom paragraphs (custom borders are lost)")
            if value.get("listProperties"):
                levels = value["listProperties"].get("nestingLevels", [])
                if any(level.get("glyphSymbol", "") not in ("", "●", "○", "■", "•")
                       or level.get("glyphType", "DECIMAL") not in (
                           "DECIMAL", "ALPHA", "ROMAN", "GLYPH_TYPE_UNSPECIFIED",
                       ) for level in levels):
                    note("list glyphs and list styling", paragraph)
            if "bullet" in value:
                # Inspect definitions only when content references the list.
                visit(lists.get(value["bullet"].get("listId"), {}),
                      table_depth, document_style, lists, images,
                      prefixes, supported_prefix, paragraph)
            for key, child in value.items():
                # Defaults are metadata, not replaceable content. Page setup
                # is checked above; referenced list definitions are checked
                # at their paragraphs instead of scanning the whole registry.
                if key in ("namedStyles", "documentStyle", "lists",
                           "suggestedNamedStylesChanges",
                           "suggestedDocumentStyleChanges"):
                    continue
                # Empty objects are valid paragraph-element markers (equation,
                # pageBreak, etc.); empty reference lists are not hazards.
                if key in _ELEMENTS and child is not None and child != []:
                    supported_image = False
                    if key == "inlineObjectElement":
                        embedded = images.get(child.get("inlineObjectId"), {}).get(
                            "inlineObjectProperties", {},
                        ).get("embeddedObject", {})
                        # A linked Sheets chart also carries imageProperties;
                        # rewriting it would insert only its rendered image.
                        linked = "linkedContentReference" in embedded
                        if linked:
                            hazards.add("linked charts (a rewrite keeps "
                                        "only a static image)")
                        supported_image = linked or (
                            "imageProperties" in embedded
                            and "embeddedDrawingProperties" not in embedded)
                        # A rewrite re-inserts an image from its URI and size
                        # only. The URI serves the uncropped original, and the
                        # API cannot set alt text or any adjustment.
                        image = ("image", id(child))
                        if embedded.get("title") or embedded.get("description"):
                            note("image alt text", image)
                        if _image_cropped(embedded):
                            note(IMAGE_CROP, image)
                        if _image_adjusted(embedded):
                            note(IMAGE_ADJUSTMENTS, image)
                    if not supported_image:
                        hazards.add(_ELEMENTS[key])
                if key.startswith("suggested") and child:
                    hazards.add("pending suggestions")
                if key == "namedRanges" and isinstance(child, dict):
                    for group in child.values():
                        for named in group.get("namedRanges", []):
                            name = named.get("name", group.get("name", ""))
                            if (named.get("ranges") and name != "gdoc:code:v1"
                                    and not re.fullmatch(_PREFIX_NAME, name)):

                                hazards.add("custom named ranges")
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
                    # The exporter renders cell runs without paragraph bullets;
                    # pipe-table reconstruction parses only inline formatting.
                    if any(
                        "bullet" in block.get("paragraph", {})
                        for row in child.get("tableRows", [])
                        for cell in row.get("tableCells", [])
                        for block in cell.get("content", [])
                    ):
                        hazards.add(
                            f"table at index {index} "
                            "(list paragraphs become plain text)"
                        )
                    if any(
                        block.get("paragraph", {}).get("paragraphStyle", {}).get(
                            "namedStyleType", "NORMAL_TEXT",
                        ) != "NORMAL_TEXT"
                        for row in child.get("tableRows", [])
                        for cell in row.get("tableCells", [])
                        for block in cell.get("content", [])
                    ):
                        hazards.add(
                            f"table at index {index} "
                            "(named paragraph styles become plain text)"
                        )
                    cell_paragraphs = [
                        block["paragraph"]
                        for row in child.get("tableRows", [])
                        for cell in row.get("tableCells", [])
                        for block in cell.get("content", [])
                        if "paragraph" in block
                    ]
                    # A pipe-table cell holds inline Markdown only: a native
                    # rule or an indented (quote-like) paragraph in a cell
                    # has no spelling there.
                    if any("horizontalRule" in element
                           for paragraph in cell_paragraphs
                           for element in paragraph.get("elements", [])):
                        hazards.add(
                            f"table at index {index} (rules inside cells are dropped)"
                        )
                    if any(_indented(paragraph) for paragraph in cell_paragraphs):
                        hazards.add(
                            f"table at index {index} "
                            "(indented cell paragraphs become plain text)"
                        )
                    for label in _table_style_losses(child):
                        note(label, ("table", id(child)))
                    # Markdown aligns a whole column like its header cell.
                    rows = [row.get("tableCells", [])
                            for row in child.get("tableRows", [])]

                    def alignments(cell):
                        return [block["paragraph"].get("paragraphStyle", {}).get(
                            "alignment", "START") for block in cell.get("content", [])
                            if "paragraph" in block]

                    headers = [(alignments(cell) or ["START"])[0]
                               for cell in (rows[0] if rows else [])]
                    if any(
                        alignment != headers[column]
                        for row in rows
                        for column, cell in enumerate(row[:len(headers)])
                        for alignment in alignments(cell)
                    ):
                        hazards.add(
                            f"table at index {index} "
                            "(cell alignment differs from its column header)"
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
                    visit(list(child.values()), table_depth,
                          document_style, lists, images, prefixes, supported_prefix,
                          paragraph)
                else:
                    visit(child, table_depth + (key == "table"),
                          document_style, lists, images, prefixes, supported_prefix,
                          paragraph)

    visit(scope)
    return hazards, styles, numbering
