"""Google Docs API v1 wrapper functions with error translation."""

import re
from dataclasses import dataclass, field
from functools import lru_cache
from http.client import HTTPException

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import HttpLib2Error

from gdoc.api import ACCOUNT_CACHE_SIZE, account_cache_key
from gdoc.util import (
    AuthError,
    GdocError,
    PreviewUnavailableError,
    fold_typography,
)


@lru_cache(maxsize=ACCOUNT_CACHE_SIZE)
def _docs_service(account: str | None, token_stamp):
    from gdoc.auth import get_credentials

    return build("docs", "v1", credentials=get_credentials(account))


def get_docs_service():
    """Build or reuse the Docs API v1 service for the current account."""
    return _docs_service(*account_cache_key())


def _translate_http_error(e: HttpError, doc_id: str) -> None:
    """Translate HttpError for Docs API operations."""
    status = int(e.resp.status)
    if status == 401:
        raise AuthError("Authentication expired. Run `gdoc auth`.")
    if status == 403:
        raise GdocError(f"Permission denied: {doc_id}")
    if status == 404:
        raise GdocError(f"Document not found: {doc_id}")
    raise GdocError(f"API error ({status}): {e.reason}")


def replace_all_text(
    doc_id: str,
    old_text: str,
    new_text: str,
    match_case: bool = False,
) -> int:
    """Replace text in a document using replaceAllText.

    Args:
        doc_id: The document ID.
        old_text: Text to find.
        new_text: Replacement text.
        match_case: If True, case-sensitive matching.

    Returns:
        Number of occurrences changed (from API response).
    """
    try:
        service = get_docs_service()
        body = {
            "requests": [
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": old_text,
                            "matchCase": match_case,
                        },
                        "replaceText": new_text,
                    }
                }
            ]
        }
        result = (
            service.documents()
            .batchUpdate(documentId=doc_id, body=body)
            .execute()
        )

        replies = result.get("replies", [])
        if replies:
            return replies[0].get("replaceAllText", {}).get(
                "occurrencesChanged", 0
            )
        return 0
    except HttpError as e:
        _translate_http_error(e, doc_id)


class CommentRevisionConflictError(GdocError):
    """The pinned comment write was rejected without applying it."""


def insert_comment(
    doc_id: str,
    content: str,
    start_index: int,
    end_index: int,
    tab_id: str | None = None,
    revision_id: str = "",
    segment_id: str | None = None,
) -> str:
    """Insert a comment anchored to a text range (Docs API insertComment).

    Unlike Drive's quotedFileContent (display metadata only), this creates a
    real anchored comment — highlighted in the Docs UI like one created by
    hand. The request is a Workspace Developer Preview feature: projects not
    enrolled get a 400 for the unknown request type, and comment-only access
    can't batchUpdate at all (403) but can still comment via the Drive API.
    Definite preview rejection raises PreviewUnavailableError. A revision
    mismatch raises CommentRevisionConflictError so callers can re-read the
    anchor. Uncertain write outcomes never permit fallback or blind replay.

    Args:
        doc_id: The document ID.
        content: Comment text, plain text (max 2048 UTF-8 code units).
        start_index: Range start (from find_text_in_document).
        end_index: Range end, exclusive.
        tab_id: Tab the range lives in (omitted → first tab).
        revision_id: If non-empty, sent as writeControl.requiredRevisionId
            so the anchor can't land on stale coordinates.
        segment_id: Header, footer or footnote containing the range.

    Returns:
        The new comment thread ID (same ID space as Drive API comments).
    """
    range_: dict = {"startIndex": start_index, "endIndex": end_index}
    if tab_id:
        range_["tabId"] = tab_id
    if segment_id:
        range_["segmentId"] = segment_id
    body: dict = {
        "requests": [
            {"insertComment": {"content": content, "range": range_}}
        ]
    }
    if revision_id:
        body["writeControl"] = {"requiredRevisionId": revision_id}
    try:
        service = get_docs_service()
        result = (
            service.documents()
            .batchUpdate(documentId=doc_id, body=body)
            .execute()
        )
    except HttpError as e:
        status = int(e.resp.status)
        detail = str(e)
        # Only a definite rejection permits another write. Never treat a
        # revision rejection as a missing preview feature.
        if status in (400, 409, 412) and "revision" in detail.lower():
            raise CommentRevisionConflictError(
                "Document changed before the comment could be anchored",
                exit_code=3,
            ) from e
        if status == 400 and (
            "No request set" in detail
            or (
                "insertComment" in detail
                and ("Unknown name" in detail or "Cannot find field" in detail)
            )
        ):
            raise PreviewUnavailableError(
                "insertComment preview is not enabled"
            ) from e
        if status == 403:
            raise PreviewUnavailableError(
                "insertComment not permitted for this user"
            )
        if status >= 500:
            raise GdocError(
                "Comment write outcome is uncertain; inspect the document's "
                "comments before retrying. No fallback comment was created."
            ) from e
        _translate_http_error(e, doc_id)
    except (OSError, HTTPException, HttpLib2Error) as e:
        raise GdocError(
            "Comment write outcome is uncertain; inspect the document's "
            "comments before retrying. No fallback comment was created."
        ) from e

    # Comment saves can fail even when the batchUpdate itself returns 200.
    state = result.get("commentUpdateState", "")
    if state and state != "ALL_SAVED":
        raise GdocError(
            f"Comment save outcome is uncertain ({state}); inspect comments "
            "before retrying. No fallback comment was created."
        )
    replies = result.get("replies", [])
    thread = (replies[0] if replies else {}).get(
        "insertComment", {},
    ).get("commentThread", {})
    comment_id = thread.get("commentId", "")
    if not comment_id:
        raise GdocError(
            "No comment thread ID in insertComment response; the comment may "
            "have been saved. Inspect comments before retrying. "
            "No fallback comment was created."
        )
    return comment_id


def set_page_mode(doc_id: str, pageless: bool) -> None:
    """Set a document's page mode (pageless vs paged).

    Writes ``documentStyle.documentFormat.documentMode`` via updateDocumentStyle.
    Blank docs inherit the account's page-mode default, while markdown-imported
    docs are always created paged; this makes the mode explicit either way.

    Args:
        doc_id: The document ID.
        pageless: If True, set PAGELESS; otherwise PAGES (paged).
    """
    mode = "PAGELESS" if pageless else "PAGES"
    try:
        service = get_docs_service()
        service.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "updateDocumentStyle": {
                            "documentStyle": {
                                "documentFormat": {"documentMode": mode},
                            },
                            "fields": "documentFormat.documentMode",
                        }
                    }
                ]
            },
        ).execute()
    except HttpError as e:
        _translate_http_error(e, doc_id)


def _extract_paragraphs_text(content: list[dict]) -> str:
    """Extract concatenated text from body content paragraph elements."""
    parts = []
    for element in content:
        paragraph = element.get("paragraph")
        if paragraph is None:
            continue
        for pe in paragraph.get("elements", []):
            text_run = pe.get("textRun")
            if text_run is None:
                continue
            parts.append(text_run.get("content", ""))
    return "".join(parts)


def flatten_tabs(tabs: list[dict], _level: int = 0) -> list[dict]:
    """Recursively flatten a tabs tree into a flat list with nesting level."""
    result = []
    for tab in tabs:
        props = tab.get("tabProperties", {})
        doc_tab = tab.get("documentTab", {})
        result.append({
            "id": props.get("tabId", ""),
            "title": props.get("title", ""),
            "index": props.get("index", 0),
            "nesting_level": _level,
            "body": doc_tab.get("body", {}),
            # listId -> list definition; needed to tell ordered from bullet
            # lists when rendering a tab as markdown.
            "lists": doc_tab.get("lists", {}),
            **{key: doc_tab[key] for key in ("headers", "footers", "footnotes")
               if key in doc_tab},
        })
        for child in tab.get("childTabs", []):
            result.extend(flatten_tabs([child], _level=_level + 1))
    return result


def get_document_tabs(doc_id: str) -> list[dict]:
    """Fetch document with all tab content and return flattened tab list.

    Uses the bounded Google-client retry policy documented in get_document.
    """
    try:
        service = get_docs_service()
        doc = (
            service.documents()
            .get(documentId=doc_id, includeTabsContent=True)
            .execute(num_retries=2)
        )
        return flatten_tabs(doc.get("tabs", []))
    except HttpError as e:
        _translate_http_error(e, doc_id)


def count_document_tabs(doc_id: str, *, document: dict | None = None) -> int:
    """Return the total tab count (including nested child tabs).

    No `fields` mask: the Docs API rejects masks that recursively
    expand `childTabs` (issue #14).
    """
    doc = document if document is not None else get_document_with_tabs(doc_id)
    return len(flatten_tabs(doc.get("tabs", [])))


def _list_is_ordered(lists: dict, list_id: str, level: int) -> bool:
    """Whether a list level is ordered (numbered) rather than a bullet.

    A Docs list level carries a ``glyphType`` (DECIMAL/ALPHA/ROMAN/...) when
    ordered and a ``glyphSymbol`` (a bullet character) when not.
    """
    levels = (
        lists.get(list_id, {})
        .get("listProperties", {})
        .get("nestingLevels", [])
    )
    if 0 <= level < len(levels):
        glyph_type = levels[level].get("glyphType", "")
        return bool(glyph_type) and glyph_type != "GLYPH_TYPE_UNSPECIFIED"
    return False


def _style_run_markdown(content: str, style: dict) -> str:
    """Wrap one text run's content in markdown emphasis / link syntax.

    Surrounding whitespace and the trailing paragraph newline are kept outside
    the markers (``** bold **`` is not valid markdown), so only the visible
    core is wrapped. Emphasis nests as ``***bold italic***`` and
    ``~~struck~~``; a link becomes ``[text](url)``.
    """
    newline = ""
    text = content
    if text.endswith("\n"):
        text, newline = text[:-1], "\n"
    if not text.strip():
        return content
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    core = "".join(
        "\\" + char if char in "\\`*_[]~<" else char
        for char in text.strip()
    )

    link = (style.get("link") or {}).get("url")
    if style.get("bold") and style.get("italic"):
        core = f"***{core}***"
    elif style.get("bold"):
        core = f"**{core}**"
    elif style.get("italic"):
        core = f"*{core}*"
    if style.get("strikethrough"):
        core = f"~~{core}~~"
    if link:
        destination = "".join(
            "\\" + char if char in "\\()" else char for char in link
        )
        core = f"[{core}]({destination})"
    return f"{lead}{core}{trail}{newline}"


def _runs_markdown(elements: list[dict]) -> str:
    """Join a paragraph's text runs, styling each as markdown."""
    parts = []
    for pe in elements:
        text_run = pe.get("textRun")
        if text_run is None:
            continue
        content = text_run.get("content", "")
        if content:
            rendered = _style_run_markdown(content, text_run.get("textStyle", {}))
            if parts and parts[-1][-1:] in ("*", "~") and rendered[:1] in ("*", "~"):
                # Standard Markdown's empty comment separates delimiters without
                # adding a visible character or merging differently styled runs.
                parts.append("<!-- -->")
            parts.append(rendered)
    return "".join(parts)


def _paragraph_markdown(
    paragraph: dict, lists: dict, ordered_counters: dict
) -> str:
    """Render one paragraph as markdown: headings, list items, inline styles.

    ``ordered_counters`` (nesting level -> running ordinal) is carried across
    paragraphs by the caller so numbered lists count 1, 2, 3.
    """
    text = _runs_markdown(paragraph.get("elements", []))
    newline = ""
    if text.endswith("\n"):
        text, newline = text[:-1], "\n"

    bullet = paragraph.get("bullet")
    if bullet is not None and text.strip():
        level = bullet.get("nestingLevel", 0)
        # A shallower item ends any deeper numbering.
        for deeper in [lvl for lvl in ordered_counters if lvl > level]:
            del ordered_counters[deeper]
        indent = "  " * level  # 2 columns per level (matches the md parser)
        if _list_is_ordered(lists, bullet.get("listId", ""), level):
            ordered_counters[level] = ordered_counters.get(level, 0) + 1
            marker = f"{ordered_counters[level]}."
        else:
            ordered_counters.pop(level, None)
            marker = "-"
        item = text.lstrip(" \t")
        return f"{indent}{marker} {item}{newline}"

    # Not a list item: numbering restarts at the next list.
    ordered_counters.clear()

    named_style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "")
    level = _HEADING_LEVELS.get(named_style)
    if named_style in ("TITLE", "SUBTITLE"):
        return f"<!-- gdoc:{named_style} --> {text}{newline}"
    if level and text.strip():
        # lstrip leading spaces/tabs so the "# " prefix can't stack a
        # widening gap across read->write round-trips.
        return "#" * level + " " + text.lstrip(" \t") + newline
    # Inline escaping above handles stars, underscores, and code fences. Escape
    # remaining literal block openers only after adding genuine block syntax.
    text = re.sub(r"^([ \t]*)([-#>|])", r"\1\\\2", text)
    text = re.sub(r"^([ \t]*\d+)\.(?=\s)", r"\1\\.", text)
    return text + newline


# One cell of a pipe-table header separator (``---``, ``:---:``).
_TABLE_SEP_CELL_RE = re.compile(r"[\s:]*-{3,}[\s:]*")


def _table_markdown(table: dict) -> str | None:
    """Export rectangular, unmerged tables; retain the text fallback otherwise.

    Cells with leading or trailing whitespace also keep the text fallback,
    because the parser strips pipe-delimiter padding from every cell.
    """
    rows = [row.get("tableCells", []) for row in table.get("tableRows", [])]
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        return None
    for row in rows:
        for cell in row:
            style = cell.get("tableCellStyle", {})
            if (style.get("rowSpan", 1) != 1 or style.get("columnSpan", 1) != 1
                    or any("table" in element for element in cell.get("content", []))):
                return None
    grid = []
    for row in rows:
        cells = []
        for cell in row:
            text = "".join(
                _runs_markdown(element["paragraph"].get("elements", []))
                for element in cell.get("content", []) if "paragraph" in element
            ).removesuffix("\n")
            if _TABLE_SEP_CELL_RE.fullmatch(text):
                # A data row of dashes would read as the separator of a new
                # table; the parser drops the escape again.
                text = text.replace("-", "\\-", 1)
            rendered = text.replace("|", "\\|").replace("\n", "<br>")
            if rendered != rendered.strip():
                # The parser strips delimiter padding, so boundary whitespace
                # has no lossless pipe-table form.
                return None
            cells.append(rendered)
        grid.append(cells)
    lines = ["| " + " | ".join(cells) + " |\n" for cells in grid]
    lines.insert(1, "| " + " | ".join(["---"] * len(rows[0])) + " |\n")
    return "".join(lines)


def get_tab_text(tab: dict, markdown: bool = False) -> str:
    """Extract text from a tab's body content.

    Handles paragraphs and tables (tab-joined cells per row in plain text). When
    *markdown* is True, the per-tab export (which builds markdown by hand,
    unlike the whole-doc Drive export) renders headings (``#``), bullet and
    numbered lists (nested, 2 spaces per level), and inline emphasis
    (``**bold**``, ``*italic*``, ``~~strike~~``) and ``[links](url)``, so a
    tab's supported text and styles can be reconstructed with ``write --tab``.
    Rectangular, unmerged tables use pipe rows, with the first row as a header
    and cell newlines as ``<br>``; irregular and nested tables, and tables
    with whitespace at a cell boundary, keep the text fallback. Table borders,
    widths and paragraph styles are not represented.

    Markdown export escapes literal syntax: ``1. Hello`` becomes
    ``1\\. Hello``, and ``_``, ``[``, and ``<`` gain backslashes. It uses
    ``<!-- -->`` between touching emphasis runs and ``<!-- gdoc:TITLE -->`` /
    ``<!-- gdoc:SUBTITLE -->`` prefixes for those named paragraph styles.
    This source noise is the accepted trade-off: escapes distinguish prose
    from structure, comments separate styles without adding visible characters,
    and ordinary Markdown has no TITLE/SUBTITLE equivalent. Retain these markers
    when reconstructing a tab; arbitrary Markdown tools and Drive import need
    not preserve them. With *markdown* False (``cat --plain --tab``), text is
    returned verbatim for searching, copying prose, and matching ``gdoc edit``.
    """
    body = tab.get("body", {})
    content = body.get("content", [])
    lists = tab.get("lists", {}) if markdown else {}
    parts = []
    ordered_counters: dict = {}
    for element in content:
        if "paragraph" in element:
            if not markdown:
                parts.append(_extract_paragraphs_text([element]))
                continue
            parts.append(
                _paragraph_markdown(element["paragraph"], lists, ordered_counters)
            )
        elif "table" in element:
            ordered_counters.clear()
            table = element["table"]
            rendered = _table_markdown(table) if markdown else None
            if rendered is not None:
                parts.append(rendered)
                continue
            for row in table.get("tableRows", []):
                cells = []
                for cell in row.get("tableCells", []):
                    cell_content = cell.get("content", [])
                    cell_text = _extract_paragraphs_text(cell_content).strip()
                    cells.append(cell_text)
                parts.append("\t".join(cells) + "\n")
    return "".join(parts)


def _match_tab(tabs: list[dict], tab_name: str) -> dict | None:
    """Prefer immutable IDs, then unique exact or case-insensitive titles."""
    for tab in tabs:
        if str(tab["id"]) == tab_name:
            return tab
    matches = [tab for tab in tabs if tab["title"] == tab_name]
    if not matches:
        matches = [tab for tab in tabs if tab["title"].lower() == tab_name.lower()]
    if len(matches) > 1:
        candidates = ", ".join(f'{tab["title"]!r} (id: {tab["id"]})' for tab in matches)
        raise GdocError(
            f"ambiguous tab {tab_name!r}: {candidates}; use a tab ID",
            exit_code=3,
        )
    return matches[0] if matches else None


def resolve_tab(tabs: list[dict], tab_name: str) -> dict:
    """Resolve a flattened tab by ID, exact title, or unique folded title.

    Raise GdocError with exit code 3 for missing or ambiguous titles.
    """
    match = _match_tab(tabs, tab_name)
    if match is None:
        raise GdocError(f"tab not found: {tab_name}", exit_code=3)
    return match


def get_document(doc_id: str) -> dict:
    """Fetch the full document structure via documents().get().

    Returns the document JSON including body.content and revisionId.
    Allows two additional Google-client retries for retryable transport errors,
    HTTP 5xx/429, and rate-limit 403 responses. This bounds client retries, not
    wire sends: httplib2 may retry internally. Mutations add no client retries.
    """
    try:
        service = get_docs_service()
        return service.documents().get(documentId=doc_id).execute(num_retries=2)
    except HttpError as e:
        _translate_http_error(e, doc_id)


def _utf16_len(ch: str) -> int:
    """Width of one code point in UTF-16 code units (Docs API indices)."""
    return 2 if ord(ch) > 0xFFFF else 1


def _collect_segments(
    content: list[dict], *, allow_native_gaps: bool = False,
) -> list[list[tuple[int, str]]]:
    """Group (doc_index, char) pairs into independently-searchable segments.

    Paragraph text at one level forms a segment, split at non-text inline
    elements unless allow_native_gaps is set for non-destructive anchors.
    Structural blocks and discontinuous native indices also split segments.
    Each table cell remains a separate segment, recursively, because Docs
    rejects edits that cross cell boundaries.

    Doc indices are UTF-16 code units, so a non-BMP character (emoji)
    advances the index by 2 even though it's one Python char.
    """
    segments: list[list[tuple[int, str]]] = []
    root: list[tuple[int, str]] = []
    for element in content:
        paragraph = element.get("paragraph")
        if paragraph is not None:
            for pe in paragraph.get("elements", []):
                text_run = pe.get("textRun")
                if text_run is None:
                    # An edit spanning this gap would delete the native element.
                    if root and not allow_native_gaps:
                        segments.append(root)
                        root = []
                    continue
                run = text_run.get("content", "")
                start_idx = pe.get("startIndex", 0)
                if (root and not allow_native_gaps
                        and start_idx != root[-1][0] + _utf16_len(root[-1][1])):
                    segments.append(root)
                    root = []
                offset = 0
                for ch in run:
                    root.append((start_idx + offset, ch))
                    offset += _utf16_len(ch)
            continue
        # Structural blocks interrupt surrounding paragraphs, even for anchors.
        if root:
            segments.append(root)
            root = []
        table = element.get("table")
        if table is not None:
            for row in table.get("tableRows", []):
                for cell in row.get("tableCells", []):
                    segments.extend(_collect_segments(
                        cell.get("content", []), allow_native_gaps=allow_native_gaps,
                    ))
    if root:
        segments.append(root)
    return segments


def _search_containers(document: dict):
    """Yield every supplied tab's independent index spaces, body first.

    Accept a legacy document, a raw tabs document, or one flattened tab.
    Segment IDs are sorted so API map iteration cannot change write order.
    """
    if "tabs" in document:
        for tab in flatten_tabs(document["tabs"]):
            yield from _search_containers(tab)
        return
    tab_id = document.get("id")
    coordinates = {"tabId": tab_id} if tab_id else {}
    yield document.get("body", {}), {"container": "body", **coordinates}
    for collection, kind in (("headers", "header"), ("footers", "footer"),
                             ("footnotes", "footnote")):
        for segment_id, content in sorted(document.get(collection, {}).items()):
            yield content, {"container": kind, "segmentId": segment_id,
                            **coordinates}


def find_text_in_document(
    document: dict | None,
    text: str,
    match_case: bool = False,
    body: dict | None = None,
    normalize: bool = False,
    *,
    allow_native_gaps: bool = False,
) -> list[dict]:
    """Find text in the supplied tabs' bodies and non-body containers.

    Passing ``body`` explicitly limits the search to that content and keeps
    the legacy two-key range shape. A full document or flattened tab also
    searches its headers, footers, and footnotes, retaining their addresses.

    Searches body.content per segment (top-level paragraphs, and each table
    cell on its own) so a match never crosses a table-cell boundary.

    Args:
        document: The full document dict (used if body is None).
        text: Text to search for.
        match_case: If True, case-sensitive matching.
        body: Optional body dict to search in (e.g. from a specific tab).
        normalize: If True, fold smart quotes/dashes to ASCII on both sides
            before matching. The fold is length-preserving, so returned
            indices stay correct.
        allow_native_gaps: For non-destructive anchors only, allow matches
            across inline native elements omitted from plain-text extraction.
            Such ranges include the native elements: never use this option
            for replacement or deletion. Table-cell boundaries still apply.

    Returns ranges with startIndex/endIndex, plus container, segmentId,
    and tabId where available. Containers are ordered body, headers,
    footers, footnotes; matches ascend by startIndex within each container.
    """
    if body is None:
        if document is None:
            return []
        matches = []
        for content, coordinates in _search_containers(document):
            for match in find_text_in_document(
                None, text, match_case=match_case, body=content,
                normalize=normalize, allow_native_gaps=allow_native_gaps,
            ):
                # Preserve the legacy body shape when no tab was supplied.
                if coordinates != {"container": "body"}:
                    match.update(coordinates)
                matches.append(match)
        return matches

    matches = []
    for chars in _collect_segments(
        body.get("content", []), allow_native_gaps=allow_native_gaps,
    ):
        concat = "".join(ch for _, ch in chars)

        search_text = text
        search_in = concat
        if normalize:
            search_text = fold_typography(search_text)
            search_in = fold_typography(search_in)
        # Map each transformed code point back to its original character.
        # Lowercasing can expand a character (İ -> i + combining dot).
        source_indices = [
            i for i, ch in enumerate(search_in)
            for _ in (ch if match_case else ch.lower())
        ]
        if not match_case:
            search_text = search_text.lower()
            # Lower the whole string to preserve contextual forms such as sigma.
            search_in = search_in.lower()
        if not search_text:
            continue

        start = 0
        while True:
            pos = search_in.find(search_text, start)
            if pos == -1:
                break
            end_pos = pos + len(search_text)
            start = pos + 1
            first, last = source_indices[pos], source_indices[end_pos - 1]
            # A match inside an expansion cannot select part of a native character.
            if ((pos > 0 and source_indices[pos - 1] == first)
                    or (end_pos < len(source_indices)
                        and source_indices[end_pos] == last)):
                continue
            matches.append({
                "startIndex": chars[first][0],
                "endIndex": chars[last][0] + _utf16_len(chars[last][1]),
            })

    matches.sort(key=lambda m: m["startIndex"])
    return matches


def diagnose_no_match(
    document: dict | None,
    text: str,
    match_case: bool = False,
    body: dict | None = None,
    already_normalized: bool = False,
) -> str | None:
    """Explain why an exact search for `text` found nothing.

    Returns a human-readable reason (to append to "no match found") or None
    if no near-match can explain the miss. Runs entirely on the already-
    fetched document \u2014 no extra API calls.
    """
    # Near-match that differs only in quote/dash style.
    if not already_normalized and find_text_in_document(
        document, text, match_case=match_case, body=body, normalize=True,
    ):
        return (
            "but a near-match exists with different quote/dash style "
            "(e.g. \u2019 vs '). Re-run with --normalize to match it"
        )

    # Near-match that differs only in whitespace (line breaks, runs of
    # spaces, non-breaking spaces). Folded so quote style doesn't mask it.
    if body is None and document is not None:
        body = document.get("body", {})
    segments = _collect_segments((body or {}).get("content", []))
    concat = fold_typography(
        "\n".join("".join(c for _, c in seg) for seg in segments)
    )
    needle = fold_typography(text)

    def collapse(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    hay_c, needle_c = collapse(concat), collapse(needle)
    if not match_case:
        hay_c, needle_c = hay_c.lower(), needle_c.lower()
    if needle_c and needle_c in hay_c:
        return (
            "but the text appears with different whitespace (line breaks "
            "or non-breaking spaces). Adjust the anchor to match exactly"
        )

    return None


_COORD_RE = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*$")


def _parse_coord(spec: str) -> tuple[int, int] | None:
    """Parse 'R,C' into (row, col) ints, or None if not coordinate form."""
    m = _COORD_RE.match(spec)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _cell_text_range(cell: dict) -> dict | None:
    """Editable text range of a table cell as {startIndex, endIndex}.

    Spans the cell's text but excludes the final structural paragraph mark
    (the Docs API forbids deleting a cell's last newline). An empty cell
    yields a zero-width range → pure insert. Returns None if no paragraph
    element with an index can be located. Refuse native objects or structural
    gaps: a whole-cell text replacement must not silently delete them.
    """
    first_start: int | None = None
    last_start: int | None = None
    last_content = ""
    for element in cell.get("content", []):
        para = element.get("paragraph")
        if (para is None or para.get("positionedObjectIds")
                or any("textRun" not in pe for pe in para.get("elements", []))):
            raise GdocError(
                "cell contains non-text content; replace specific text instead",
                exit_code=3,
            )
        for pe in para.get("elements", []):
            start = pe.get("startIndex")
            if start is None:
                continue
            previous_width = sum(_utf16_len(ch) for ch in last_content)
            if last_start is not None and start != last_start + previous_width:
                raise GdocError(
                    "cell contains a structural gap; replace specific text instead",
                    exit_code=3,
                )
            if first_start is None:
                first_start = start
            tr = pe.get("textRun")
            last_start = start
            last_content = tr.get("content", "") if tr else ""
    if first_start is None:
        content = cell.get("content", [])
        fs = content[0].get("startIndex") if content else None
        return {"startIndex": fs, "endIndex": fs} if fs is not None else None
    # Doc indexes are UTF-16 code units: an emoji in the cell counts as 2.
    end = last_start + sum(_utf16_len(ch) for ch in last_content)
    if last_content.endswith("\n"):
        end -= 1  # keep the cell's final paragraph mark
    if end < first_start:
        end = first_start
    return {"startIndex": first_start, "endIndex": end}


def resolve_cell_range(
    body: dict,
    cell: str,
    col: int | None = None,
    table_index: int | None = None,
    normalize: bool = False,
) -> dict | None:
    """Resolve a cell address to an editable {startIndex, endIndex} range.

    Two forms, auto-detected:
    - coordinate ('R,C'): row R, column C of a table (0-based). Uses table
      `table_index`, or the first table when `table_index` is None.
    - label (anything else): match the first column of a unique row whose
      text equals `cell`; the target is column `col` if given, else column 1.
      Searches every table by default, or only table `table_index` when given.
      Duplicate labels or labels repeated in value columns raise GdocError
      with exit code 3 before resolving a range.

    `normalize` folds smart quotes/dashes when comparing labels. Returns
    None if nothing resolves.
    """
    tables = [el["table"] for el in body.get("content", []) if "table" in el]

    coord = _parse_coord(cell)
    if coord is not None:
        r, c = coord
        ti = 0 if table_index is None else table_index
        if not 0 <= ti < len(tables):
            return None
        rows = tables[ti].get("tableRows", [])
        if not 0 <= r < len(rows):
            return None
        cells = rows[r].get("tableCells", [])
        if not 0 <= c < len(cells):
            return None
        return _cell_text_range(cells[c])

    # Only the first column identifies a row; values must not select neighbours.
    if table_index is None:
        search_tables = enumerate(tables)
    elif 0 <= table_index < len(tables):
        search_tables = [(table_index, tables[table_index])]
    else:
        return None

    target = fold_typography(cell) if normalize else cell
    target = target.strip()
    matches = []
    value_matches = []
    for ti, table in search_tables:
        for ri, row in enumerate(table.get("tableRows", [])):
            cells = row.get("tableCells", [])
            for ci, candidate in enumerate(cells):
                label = _extract_paragraphs_text(candidate.get("content", []))
                label = (fold_typography(label) if normalize else label).strip()
                if label == target:
                    if ci == 0:
                        matches.append((ti, ri, cells))
                    else:
                        value_matches.append(f"table {ti} row {ri} column {ci}")
    if len(matches) > 1 or (matches and value_matches):
        candidates = ", ".join(
            [f"table {ti} row {ri} column 0" for ti, ri, _ in matches]
            + value_matches
        )
        raise GdocError(
            f"ambiguous cell label {cell!r}: {candidates}; "
            "use --table and --cell ROW,COL",
            exit_code=3,
        )
    if not matches:
        return None
    cells = matches[0][2]
    target_col = 1 if col is None else col
    if not 0 <= target_col < len(cells):
        return None
    return _cell_text_range(cells[target_col])


def _find_table_cell_indices(
    document: dict | None,
    table_start_index: int,
    body: dict | None = None,
) -> list[list[int]]:
    """Find the startIndex of each cell's first paragraph in a table.

    Walks body.content to find the table element at or near the given
    index, then extracts cell paragraph start indices. Searches for the
    nearest table at or after the index (insertTable may place the table
    one position after the specified location).

    Returns a 2D list: cell_indices[row][col] = startIndex.
    """
    if body is None:
        if document is None:
            return []
        body = document.get("body", {})
    for element in body.get("content", []):
        if "table" not in element:
            continue
        el_start = element.get("startIndex", 0)
        # Table may be at index or up to 2 positions after
        if el_start < table_start_index or el_start > table_start_index + 2:
            continue

        table = element["table"]
        cell_indices: list[list[int]] = []
        for row in table.get("tableRows", []):
            row_indices: list[int] = []
            for cell in row.get("tableCells", []):
                cell_content = cell.get("content", [])
                if cell_content:
                    first_para = cell_content[0]
                    para = first_para.get("paragraph", {})
                    elements = para.get("elements", [])
                    if elements:
                        row_indices.append(
                            elements[0].get("startIndex", 0)
                        )
                    else:
                        row_indices.append(
                            first_para.get("startIndex", 0)
                        )
                else:
                    row_indices.append(cell.get("startIndex", 0))
            cell_indices.append(row_indices)
        return cell_indices

    return []


def _revision_conflict(error: Exception) -> bool:
    if not isinstance(error, HttpError) or int(error.resp.status) != 400:
        return False
    detail = str(error).lower()
    return "revision" in detail and any(phrase in detail for phrase in (
        "does not match", "not match", "mismatch", "not the latest",
        "not latest", "stale", "out of date", "too old",
    ))


@dataclass
class _StagedWrite:
    """Track acknowledged stages separately from an unanswered mutation."""

    doc_id: str
    applied: list[str] = field(default_factory=list)
    stage: str = "preparing content"
    sent: bool = False
    rebased: bool = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, error, traceback):
        if error is None:
            return False
        if isinstance(error, AuthError) and not self.applied:
            return False  # Raised before any send; keep the exit-2 guidance.
        conflict = _revision_conflict(error) or (
            isinstance(error, GdocError) and error.exit_code == 3
        )
        rejected = (isinstance(error, HttpError)
                    and 400 <= int(error.resp.status) < 500)
        uncertain = self.sent and not rejected
        status = "completion uncertain" if uncertain else "not applied"
        completed = "; ".join(self.applied) or "none confirmed"
        prefix = "Partial completion" if self.applied else "Write failed"
        detail = str(error)
        if isinstance(error, HttpError) and not conflict:
            try:
                _translate_http_error(error, self.doc_id)
            except AuthError:
                if not self.applied:
                    raise
            except GdocError as translated:
                detail = str(translated)
        if conflict:
            detail = f"conflict: {detail}"
        raise GdocError(
            f"{prefix}: applied: {completed}; {self.stage}: {status}; "
            f"remaining stages not attempted. {detail}. "
            "Inspect the document before retrying; "
            "completed batches were not replayed.",
            exit_code=3 if conflict and not self.applied and not uncertain else 1,
        ) from error

    def mark_sent(self):
        self.sent = True

    def read(self, stage: str, tab_id: str | None):
        self.stage, self.sent = stage, False
        kwargs = {"documentId": self.doc_id}
        if tab_id:
            kwargs["includeTabsContent"] = True
        return get_docs_service().documents().get(**kwargs).execute(num_retries=2)

    def batch(self, stage, requests, revision_id, recompute=None):
        self.stage, self.sent = stage, False
        for attempt in range(2):
            if not isinstance(revision_id, str) or not revision_id:
                raise GdocError(
                    "missing revision; refusing an unpinned write", exit_code=3,
                )
            request = get_docs_service().documents().batchUpdate(
                documentId=self.doc_id,
                body={
                    "requests": requests,
                    "writeControl": {"requiredRevisionId": revision_id},
                },
            )
            try:
                from gdoc.api.comment_transport import execute_mutation_request
                response = execute_mutation_request(request, on_send=self.mark_sent)
            except HttpError as error:
                if not _revision_conflict(error) or attempt or recompute is None:
                    raise
                self.sent = False  # A revision rejection is known not to apply.
                try:
                    requests, revision_id = recompute()
                except Exception as failure:
                    raise GdocError(
                        f"conflict: cannot safely recompute {stage}: {failure}",
                        exit_code=3,
                    ) from failure
                self.stage = stage
                self.rebased = True
                continue
            self.applied.append(stage)
            self.sent = False
            return response.get("writeControl", {}).get("requiredRevisionId", "")


def _stage_body(doc, tab_id):
    if tab_id:
        # Only an exact ID is safe once the tab was selected by the caller.
        matches = [t for t in flatten_tabs(doc.get("tabs", [])) if t["id"] == tab_id]
        if len(matches) != 1:
            raise GdocError("conflict: target tab disappeared", exit_code=3)
        return matches[0]["body"]
    return doc.get("body", {})


def _table_position_resolver(parsed, table, tab_id):
    """Use unique unchanged text before the placeholder, or refuse recovery.

    Search only a contiguous native range. Adjacent tables and table-only
    replacements have no text anchor and deliberately cannot be rebased.
    """
    from gdoc.mdparse import utf16_len

    previous = max((t.plain_text_offset + 1 for t in parsed.tables
                    if t.plain_text_offset < table.plain_text_offset), default=0)
    anchor = parsed.plain_text[previous:table.plain_text_offset]
    # createParagraphBullets consumes leading nesting tabs.
    anchor = re.sub(r"(?m)^\t+", "", anchor)

    def resolve(doc):
        candidates = find_text_in_document(
            None, anchor, match_case=True, body=_stage_body(doc, tab_id),
        ) if anchor.strip() else []
        chars = dict(pair for segment in _collect_segments(
            _stage_body(doc, tab_id).get("content", []),
        ) for pair in segment)
        candidates = [m for m in candidates
                      if m["endIndex"] - m["startIndex"] == utf16_len(anchor)
                      and chars.get(m["endIndex"]) == "\n"]
        if len(candidates) != 1:
            raise GdocError(
                "conflict: cannot uniquely relocate the table insertion point",
                exit_code=3,
            )
        return candidates[0]["endIndex"]

    return resolve


def _without_indices(value):
    if isinstance(value, dict):
        return {k: _without_indices(v) for k, v in value.items()
                if k not in ("startIndex", "endIndex")}
    if isinstance(value, list):
        return [_without_indices(v) for v in value]
    return value


def _table_at(body, index):
    matches = [e for e in body.get("content", [])
               if "table" in e and index <= e.get("startIndex", 0) <= index + 2]
    if len(matches) != 1:
        raise GdocError("conflict: inserted table cannot be identified", exit_code=3)
    return matches[0]


def _table_cell_requests(cell_indices, table, tab_id):
    # Parse each cell's markdown to plain text + inline styles, once.
    from gdoc.mdparse import (
        StyleRange,
        _utf16_prefix,
        parse_inline,
        text_style_fields,
        utf16_len,
    )

    parsed_cells: dict[tuple[int, int], tuple[str, list]] = {}
    for r_idx, row in enumerate(cell_indices):
        for c_idx in range(len(row)):
            raw = ""
            if r_idx < len(table.rows) and c_idx < len(table.rows[r_idx]):
                raw = table.rows[r_idx][c_idx]
            parsed_cells[(r_idx, c_idx)] = (
                parse_inline(raw) if raw else ("", [])
            )

    # Step 3: Insert cell plain text (reverse order, so the original cell
    # indices stay valid — inserting at a higher index never shifts a
    # lower one).
    text_requests: list[dict] = []
    for r_idx in range(len(cell_indices) - 1, -1, -1):
        row = cell_indices[r_idx]
        for c_idx in range(len(row) - 1, -1, -1):
            plain, _ = parsed_cells[(r_idx, c_idx)]
            if plain:
                cell_location = {"index": row[c_idx]}
                if tab_id:
                    cell_location["tabId"] = tab_id
                text_requests.append({
                    "insertText": {
                        "location": cell_location,
                        "text": plain,
                    }
                })

    # Apply inline styles (plus bold for the whole header row) in forward
    # index order. Each cell's final position is its original index plus the
    # total length of all earlier (lower-index) cells already inserted.
    shift = 0
    for r_idx in range(len(cell_indices)):
        row = cell_indices[r_idx]
        for c_idx in range(len(row)):
            plain, cell_styles = parsed_cells[(r_idx, c_idx)]
            cell_styles = list(cell_styles)
            if r_idx == 0 and plain:
                cell_styles.append(StyleRange(
                    0, len(plain), {"bold": True}, "text_style",
                ))
            base = row[c_idx] + shift
            # Style offsets are code points; Docs indexes are UTF-16.
            utf16 = _utf16_prefix(plain)
            for s in cell_styles:
                style_range = {
                    "startIndex": base + utf16[s.start],
                    "endIndex": base + utf16[s.end],
                }
                if tab_id:
                    style_range["tabId"] = tab_id
                text_requests.append({
                    "updateTextStyle": {
                        "range": style_range,
                        "textStyle": s.style,
                        "fields": text_style_fields(s.style),
                    }
                })
            shift += utf16_len(plain)

    return text_requests


def _table_scaffolding(parsed, table):
    """Only the parser's own separator and placeholder may be consumed."""
    offset = table.plain_text_offset
    previous_placeholder = any(t.plain_text_offset == offset - 1
                               for t in parsed.tables)
    before = (offset > 0 and parsed.plain_text[offset - 1] == "\n"
              and not previous_placeholder)
    placeholder = offset < len(parsed.plain_text)
    return int(before), int(placeholder)


def _insert_table(
    doc_id: str,
    index: int,
    table,
    tab_id: str | None = None,
    *, revision_id: str = "", progress=None, resolve_index=None,
    ordinal: int = 1, scaffolding: tuple[int, int] = (0, 0),
) -> str:
    """Insert and fill a table with revision-pinned, single-shot stages."""
    if progress is None:
        with _StagedWrite(doc_id) as progress:
            if not revision_id:
                doc = progress.read("reading table insertion point", tab_id)
                revision_id = doc.get("revisionId", "")
            return _insert_table(
                doc_id, index, table, tab_id, revision_id=revision_id,
                progress=progress, resolve_index=resolve_index, ordinal=ordinal,
                scaffolding=scaffolding,
            )

    label = f"table {ordinal} in tab {tab_id or 'default'}"

    def insertion():
        before, placeholder = scaffolding
        location = {"index": index - before}
        if tab_id:
            location["tabId"] = tab_id
        requests = []
        if before or placeholder:
            span = {"startIndex": index - before, "endIndex": index + placeholder}
            if tab_id:
                span["tabId"] = tab_id
            requests.append({"deleteContentRange": {"range": span}})
        # insertTable supplies its own leading newline. Consume our parser's
        # separators in this same pinned batch so they cannot survive as blanks.
        requests.append({"insertTable": {
            "rows": table.num_rows, "columns": table.num_cols, "location": location,
        }})
        return requests

    def relocate():
        nonlocal index
        doc = progress.read("re-reading table insertion point", tab_id)
        if resolve_index is None:
            raise GdocError("conflict: cannot relocate table insertion", exit_code=3)
        index = resolve_index(doc)
        return insertion(), doc.get("revisionId", "")

    # A previous table may have recovered from a collaborator's index shift.
    if progress.rebased:
        requests, revision_id = relocate()
    else:
        requests = insertion()
    revision_id = progress.batch(
        f"{label}: table structure inserted", requests, revision_id, relocate,
    )
    doc = progress.read("reading inserted table cells", tab_id)
    if not revision_id or doc.get("revisionId") != revision_id:
        # The collaborator moved the table before its first read-back. We
        # have no trusted table fingerprint yet; do not guess another table.
        raise GdocError(
            "conflict: document changed before the inserted table could be located",
            exit_code=3,
        )
    body = _stage_body(doc, tab_id)
    element = _table_at(body, index - scaffolding[0])
    fingerprint = _without_indices(element["table"])
    unique_before = sum(
        "table" in e and _without_indices(e["table"]) == fingerprint
        for e in body.get("content", [])
    ) == 1

    def fill(snapshot, target):
        indices = _find_table_cell_indices(None, target["startIndex"],
                                           body=_stage_body(snapshot, tab_id))
        if len(indices) != table.num_rows or any(
            len(row) != table.num_cols for row in indices
        ):
            raise GdocError("conflict: table dimensions changed", exit_code=3)
        return _table_cell_requests(indices, table, tab_id)

    def relocate_cells():
        snapshot = progress.read("re-reading table cells", tab_id)
        candidates = [e for e in _stage_body(snapshot, tab_id).get("content", [])
                      if "table" in e and _without_indices(e["table"]) == fingerprint]
        if not unique_before or len(candidates) != 1:
            raise GdocError(
                "conflict: inserted table changed or is ambiguous; cells not filled",
                exit_code=3,
            )
        return fill(snapshot, candidates[0]), snapshot.get("revisionId", "")

    requests = fill(doc, element)
    if requests:
        revision_id = progress.batch(
            f"{label}: table cells filled", requests, doc.get("revisionId", ""),
            relocate_cells,
        )
    return revision_id


def _collect_object_refs(body: dict) -> list[tuple[str, int, str]]:
    """Walk body.content for object references.

    Returns (object_id, start_index, source) tuples, where source is
    "inline" or "positioned".
    """
    refs: list[tuple[str, int, str]] = []
    for element in body.get("content", []):
        paragraph = element.get("paragraph")
        if paragraph is None:
            continue
        for pe in paragraph.get("elements", []):
            ioe = pe.get("inlineObjectElement")
            if ioe:
                obj_id = ioe.get("inlineObjectId", "")
                start = pe.get("startIndex", 0)
                refs.append((obj_id, start, "inline"))
        # Check for positioned object references
        positioned_ids = paragraph.get("positionedObjectIds", [])
        para_start = element.get("startIndex", 0)
        for pid in positioned_ids:
            refs.append((pid, para_start, "positioned"))
    return refs


def list_inline_objects(doc_id: str) -> list[dict]:
    """List all inline and positioned objects in a document, every tab.

    Walks each tab's body.content for inlineObjectElement and
    positionedObjectId references, joins with the tab's inlineObjects
    and positionedObjects maps, and classifies each object.

    Returns list of dicts with id, tab, type, title, description,
    dimensions, content_uri, source_uri, start_index, and chart
    metadata. `tab` is "" for documents fetched without tab content.
    """
    doc = get_document_with_tabs(doc_id)

    # (tab_id, body, inline_map, positioned_map) per content segment
    segments: list[tuple[str, dict, dict, dict]] = []
    tabs = doc.get("tabs")
    if tabs:
        def walk(ts: list[dict]):
            for t in ts:
                doc_tab = t.get("documentTab", {})
                yield (
                    t.get("tabProperties", {}).get("tabId", ""),
                    doc_tab.get("body", {}),
                    doc_tab.get("inlineObjects", {}),
                    doc_tab.get("positionedObjects", {}),
                )
                yield from walk(t.get("childTabs", []))

        segments = list(walk(tabs))
    else:
        segments = [(
            "",
            doc.get("body", {}),
            doc.get("inlineObjects", {}),
            doc.get("positionedObjects", {}),
        )]

    results = []
    seen = set()

    for tab_id, body, inline_map, positioned_map in segments:
        for obj_id, start_index, source in _collect_object_refs(body):
            if (tab_id, obj_id) in seen:
                continue
            seen.add((tab_id, obj_id))

            if source == "inline":
                obj_data = inline_map.get(obj_id, {})
            else:
                obj_data = positioned_map.get(obj_id, {})
            results.append(_classify_object(obj_id, obj_data, start_index, tab_id))

    return results


def _classify_object(
    obj_id: str, obj_data: dict, start_index: int, tab_id: str,
) -> dict:
    """Build the metadata entry for one inline/positioned object."""
    props = obj_data.get("inlineObjectProperties", {}) or obj_data.get(
        "positionedObjectProperties", {}
    )
    embedded = props.get("embeddedObject", {})

    # Classify type
    obj_type = "image"
    spreadsheet_id = None
    chart_id = None
    if "embeddedDrawingProperties" in embedded:
        obj_type = "drawing"
    elif "linkedContentReference" in embedded:
        lcr = embedded["linkedContentReference"]
        if "sheetsChartReference" in lcr:
            obj_type = "chart"
            scr = lcr["sheetsChartReference"]
            spreadsheet_id = scr.get("spreadsheetId")
            chart_id = scr.get("chartId")

    # Extract dimensions
    size = embedded.get("size", {})
    width = size.get("width", {}).get("magnitude", 0)
    height = size.get("height", {}).get("magnitude", 0)

    # Content URI (None for drawings)
    content_uri = None
    if obj_type != "drawing":
        image_props = embedded.get("imageProperties", {})
        content_uri = image_props.get("contentUri")

    entry = {
        "id": obj_id,
        "tab": tab_id,
        "type": obj_type,
        "title": embedded.get("title", ""),
        "description": embedded.get("description", ""),
        "width_pt": width,
        "height_pt": height,
        "content_uri": content_uri,
        "source_uri": embedded.get("imageProperties", {}).get("sourceUri"),
        "start_index": start_index,
    }
    if obj_type == "chart":
        entry["spreadsheet_id"] = spreadsheet_id
        entry["chart_id"] = chart_id
    return entry


def download_image(content_uri: str, dest_path: str) -> None:
    """Download an image from a pre-signed content URI to a local file."""
    import urllib.request

    with urllib.request.urlopen(content_uri) as resp:
        data = resp.read()
    with open(dest_path, "wb") as f:
        f.write(data)


def insert_inline_image(
    doc_id: str,
    uri: str,
    index: int,
    tab_id: str | None = None,
    revision_id: str = "",
    width_pt: float | None = None,
    height_pt: float | None = None,
) -> str:
    """Insert an inline image at a document index via insertInlineImage.

    Args:
        doc_id: The document ID.
        uri: Publicly fetchable image URL (Google's servers download it).
        index: UTF-16 insertion index (from find_text_in_document).
        tab_id: Tab the index lives in (omitted → first tab).
        revision_id: If non-empty, sent as writeControl.requiredRevisionId
            so the insert can't land on stale coordinates.
        width_pt: Optional display width in points.
        height_pt: Optional display height in points.

    Returns:
        The new inline object ID (usable with `gdoc images`/replace_image).
    """
    location: dict = {"index": index}
    if tab_id:
        location["tabId"] = tab_id
    request: dict = {"location": location, "uri": uri}
    size: dict = {}
    if width_pt:
        size["width"] = {"magnitude": width_pt, "unit": "PT"}
    if height_pt:
        size["height"] = {"magnitude": height_pt, "unit": "PT"}
    if size:
        request["objectSize"] = size
    body: dict = {"requests": [{"insertInlineImage": request}]}
    if revision_id:
        body["writeControl"] = {"requiredRevisionId": revision_id}
    try:
        service = get_docs_service()
        result = (
            service.documents()
            .batchUpdate(documentId=doc_id, body=body)
            .execute()
        )
    except HttpError as e:
        _raise_if_stale_revision(e)
        _translate_http_error(e, doc_id)
    replies = result.get("replies", [])
    return (replies[0] if replies else {}).get(
        "insertInlineImage", {},
    ).get("objectId", "")


def replace_image(
    doc_id: str,
    object_id: str,
    uri: str,
    tab_id: str | None = None,
    revision_id: str = "",
) -> None:
    """Replace an existing image's content via replaceImage.

    The existing image keeps its size; the new content is scaled and
    center-cropped to fit (CENTER_CROP is the only supported method).

    Args:
        doc_id: The document ID.
        object_id: Inline object ID of the image (see `gdoc images`).
        uri: Publicly fetchable replacement image URL.
        tab_id: Tab the image lives in (omitted → first tab).
        revision_id: If non-empty, sent as writeControl.requiredRevisionId.
    """
    request: dict = {
        "imageObjectId": object_id,
        "uri": uri,
        "imageReplaceMethod": "CENTER_CROP",
    }
    if tab_id:
        request["tabId"] = tab_id
    body: dict = {"requests": [{"replaceImage": request}]}
    if revision_id:
        body["writeControl"] = {"requiredRevisionId": revision_id}
    try:
        service = get_docs_service()
        service.documents().batchUpdate(
            documentId=doc_id, body=body,
        ).execute()
    except HttpError as e:
        _raise_if_stale_revision(e)
        _translate_http_error(e, doc_id)


def _raise_if_stale_revision(e: HttpError) -> None:
    """Turn a writeControl revision-mismatch 400 into a clear retry hint."""
    if int(e.resp.status) == 400 and "revision" in str(e).lower():
        raise GdocError(
            "document changed while the command was running; re-run it"
        )


def find_object_tab(doc: dict, object_id: str) -> str | None:
    """Find which tab holds an inline/positioned object ID.

    Walks the tab tree of a documents.get(includeTabsContent=True) response.
    Returns the tab ID, or None if no tab declares the object (including
    docs fetched without tab content).
    """
    def walk(tabs: list[dict]) -> str | None:
        for tab in tabs:
            doc_tab = tab.get("documentTab", {})
            if (
                object_id in doc_tab.get("inlineObjects", {})
                or object_id in doc_tab.get("positionedObjects", {})
            ):
                return tab.get("tabProperties", {}).get("tabId")
            found = walk(tab.get("childTabs", []))
            if found is not None:
                return found
        return None

    return walk(doc.get("tabs", []))


_HEADING_LEVELS = {
    "HEADING_1": 1, "HEADING_2": 2, "HEADING_3": 3,
    "HEADING_4": 4, "HEADING_5": 5, "HEADING_6": 6,
}


def get_document_headings(doc_id: str, body: dict | None = None) -> list[dict]:
    """Extract headings with deep-link IDs from a document body.

    If *body* is provided (e.g. from a specific tab), it is used
    directly; otherwise the document is fetched via documents().get().

    Returns a list of dicts:
        {"level": int, "heading_id": str, "text": str}
    """
    if body is None:
        doc = get_document(doc_id)
        body = doc.get("body", {})

    headings: list[dict] = []
    for element in body.get("content", []):
        paragraph = element.get("paragraph")
        if paragraph is None:
            continue
        style = paragraph.get("paragraphStyle", {})
        named_style = style.get("namedStyleType", "")
        heading_id = style.get("headingId")
        if named_style not in _HEADING_LEVELS or not heading_id:
            continue
        text = "".join(
            run.get("textRun", {}).get("content", "")
            for run in paragraph.get("elements", [])
        ).strip()
        if not text:
            continue
        headings.append({
            "level": _HEADING_LEVELS[named_style],
            "heading_id": heading_id,
            "text": text,
        })
    return headings


def get_document_with_tabs(doc_id: str) -> dict:
    """Fetch document with includeTabsContent=True.

    Returns the full document dict (including revisionId and tabs).
    Uses the bounded Google-client retry policy documented in get_document.
    HttpError is translated via _translate_http_error.
    """
    try:
        service = get_docs_service()
        return (
            service.documents()
            .get(documentId=doc_id, includeTabsContent=True)
            .execute(num_retries=2)
        )
    except HttpError as e:
        _translate_http_error(e, doc_id)


def get_document_structure(
    doc_id: str,
    fields: str | None = None,
    suggestions_view_mode: str | None = None,
) -> dict:
    """Fetch the raw documents.get JSON for native structure inspection.

    Always requests includeTabsContent=True so every tab's body is
    present. A fields mask is passed verbatim when given — note Google
    rejects masks that recursively expand childTabs (repo issue #14).
    Uses the bounded Google-client retry policy documented in get_document.

    Args:
        doc_id: The document ID.
        fields: Optional Docs API field mask.
        suggestions_view_mode: Optional SuggestionsViewMode enum value
            (e.g. PREVIEW_SUGGESTIONS_ACCEPTED). Changes returned content
            and indexes.
    """
    kwargs: dict = {"documentId": doc_id, "includeTabsContent": True}
    if fields:
        kwargs["fields"] = fields
    if suggestions_view_mode:
        kwargs["suggestionsViewMode"] = suggestions_view_mode
    try:
        service = get_docs_service()
        return service.documents().get(**kwargs).execute(num_retries=2)
    except HttpError as e:
        _translate_http_error(e, doc_id)


def resolve_raw_tab(tabs: list[dict], tab_name: str) -> dict | None:
    """Resolve a raw tab across the tree with the same identity rules as resolve_tab.

    Return None when missing; refuse ambiguous titles with exit code 3.
    """
    def walk(ts: list[dict]):
        for tab in ts:
            props = tab.get("tabProperties", {})
            yield {"id": props.get("tabId", ""), "title": props.get("title", ""),
                   "raw": tab}
            yield from walk(tab.get("childTabs", []))

    match = _match_tab(list(walk(tabs)), tab_name)
    return match["raw"] if match is not None else None


def add_tab(doc_id: str, title: str) -> dict:
    """Add a new tab to a document.

    Returns dict with 'tabId', 'title', 'index'.
    """
    service = get_docs_service()
    try:
        resp = service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"addDocumentTab": {
                "tabProperties": {"title": title},
            }}]},
        ).execute()
        try:
            props = resp["replies"][0]["addDocumentTab"]["tabProperties"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GdocError(
                f"Unexpected API response for addDocumentTab: {exc}",
            )
        return {
            "tabId": props["tabId"],
            "title": props.get("title", title),
            "index": props.get("index", 0),
        }
    except HttpError as e:
        _translate_http_error(e, doc_id)


def _build_cleanup_requests(
    body: dict, position: int, tab_id: str | None = None,
) -> list[dict]:
    """Remove an explicitly identified empty paragraph, never its neighbor.

    Call only for a separator created by the current operation. The segment's
    final newline is mandatory, and non-text elements are never scaffolding.
    """
    content = body.get("content", [])
    for element in content:
        if element.get("startIndex") != position:
            continue
        paragraph = element.get("paragraph", {})
        elements = paragraph.get("elements", [])
        if (paragraph.get("positionedObjectIds") or len(elements) != 1
                or elements[0].get("textRun", {}).get("content") != "\n"
                or elements[0].get("startIndex") != position
                or elements[0].get("endIndex") != position + 1
                or element.get("endIndex") != position + 1
                or element is content[-1]):
            return []
        target = {"startIndex": position, "endIndex": position + 1}
        if tab_id:
            target["tabId"] = tab_id
        return [{"deleteContentRange": {"range": target}}]
    return []


def _tab_body_range(body: dict) -> tuple[int, int]:
    """Return (startIndex, endIndex_exclusive_final_newline) for a tab body.

    A tab body always begins at index 1. The "end" is one less than the
    final element's endIndex because Docs stores a trailing newline that
    cannot be deleted. Returns (1, 1) for an empty body.
    """
    last_end = 1
    for elem in body.get("content", []):
        end = elem.get("endIndex")
        if end is not None and end > last_end:
            last_end = end
    if last_end <= 1:
        return (1, 1)
    return (1, last_end - 1)


def _strip_trailing_newline_unless_hr(parsed) -> None:
    """Drop the trailing \\n parse_markdown appends — the existing paragraph at
    the insertion point already owns one, so without this every write leaves an
    extra blank line. Skipped when the last paragraph is a horizontal rule (an
    intentionally-empty paragraph whose border is lost if its only character is
    removed). Mutates ``parsed`` in place.
    """
    old_len = len(parsed.plain_text)
    last_is_hr = any(
        s.type == "paragraph_style" and s.end == old_len
        and "borderBottom" in s.style
        for s in parsed.styles
    )
    if parsed.plain_text.endswith("\n") and not last_is_hr:
        parsed.plain_text = parsed.plain_text[:-1]
        for s in parsed.styles:
            if s.end == old_len:
                s.end = old_len - 1


def _reset_list_indents(parsed) -> None:
    """Clear inherited list indents without overriding explicit Markdown."""
    for style in parsed.styles:
        if style.type == "paragraph_style":
            for field in ("indentStart", "indentEnd", "indentFirstLine"):
                style.style.setdefault(field, {"magnitude": 0, "unit": "PT"})


def insert_markdown_into_tab(
    doc_id: str,
    tab_name: str,
    markdown: str,
    position: str = "start",
    replace: bool = False,
    allow_lossy: bool = False,
    *, document: dict | None = None,
) -> dict:
    """Insert (or replace) markdown content in a tab via Docs API.

    Bypasses Drive's markdown importer so multi-tab docs are never
    collapsed. Reused by both `gdoc insert` and `gdoc write --tab`.

    Args:
        doc_id: Document ID.
        tab_name: Tab title (case-insensitive) or tab ID.
        markdown: Markdown source to insert (frontmatter should be
            stripped by the caller).
        position: "start" or "end". Ignored when replace=True.
        replace: If True, delete the tab body first then insert at the
            body start.
        allow_lossy: Explicitly permit named native-content losses.
        document: Optional guard-read snapshot; its revision pins the first
            batch so a later read cannot silently adopt a collaborator edit.

    Returns:
        Dict with "tab_id", "tab_title", "insert_index".
    """
    from gdoc.mdparse import (
        _paragraph_style_fields,
        parse_markdown,
        to_docs_requests,
        utf16_len,
    )

    doc = document if document is not None else get_document_with_tabs(doc_id)
    revision_id = doc.get("revisionId", "")
    tabs = flatten_tabs(doc.get("tabs", []))
    tab_match = resolve_tab(tabs, tab_name)
    tab_id = tab_match["id"]
    body = tab_match["body"]

    if replace and any("sectionBreak" in e and e.get("startIndex", 0) > 0
                       for e in body.get("content", [])):
        raise GdocError(
            "native replacement cannot preserve multiple sections; "
            "replace specific text instead", exit_code=3,
        )
    body_start, body_end = _tab_body_range(body)

    if replace:
        insert_index = body_start
    elif position == "end":
        insert_index = body_end
    else:
        insert_index = body_start

    parsed = parse_markdown(markdown)
    if replace and parsed.non_default_list_starts:
        import sys

        losses = ", ".join(parsed.non_default_list_starts)
        if not allow_lossy:
            raise GdocError(
                "Markdown replacement refused: incoming " + losses
                + ". No content was written. Pass --allow-lossy to knowingly "
                "reset list numbering.",
                exit_code=3,
            )
        print("WARN: Markdown replacement will reset incoming " + losses,
              file=sys.stderr)
    requests: list[dict] = []

    at_end = replace or body_end == body_start or position == "end"
    if at_end:
        _strip_trailing_newline_unless_hr(parsed)
    # Trimming an empty final paragraph leaves its annotation at zero width.
    # Its style belongs on the retained native mark, not on extra inserted text.
    final_style = next((s.style for s in parsed.styles
                        if s.type == "paragraph_style"
                        and s.start == s.end == len(parsed.plain_text)), None)
    # A leading table needs no separator: InsertTableRequest adds its own
    # newline before the table, so the placeholder newline becomes the
    # existing paragraph's mark. Anything else that starts with a newline (a
    # thematic break, a deliberate blank line) is a new paragraph of its own
    # and keeps the separator so its mark never lands on existing text.
    appending = not replace and body_end > body_start and position == "end"
    leading_table = (
        appending and bool(parsed.tables) and parsed.tables[0].plain_text_offset == 0
    )
    if leading_table:
        # The placeholder newline ends the existing paragraph, whose style
        # and list membership must stay untouched.
        parsed.styles = [s for s in parsed.styles
                         if not (s.type == "paragraph_style"
                                 and s.start == 0 and s.end <= 1)]
        if not parsed.plain_text:
            final_style = None
    if (not replace and body_end > body_start and not leading_table
            and (parsed.plain_text or parsed.tables or final_style is not None)):
        if position == "end":
            # The mandatory final newline belongs to the existing paragraph.
            # Split first, then insert and style only the new paragraph.
            requests.append({"insertText": {
                "location": {"index": insert_index, "tabId": tab_id},
                "text": "\n",
            }})
            insert_index += 1
        # At start, the parser's final newline separates the inserted text
        # from the existing first paragraph; do not strip it.

    if replace and body_end > body_start:
        delete_range = {
            "startIndex": body_start,
            "endIndex": body_end,
            "tabId": tab_id,
        }
        requests.append({"deleteContentRange": {"range": delete_range}})

    if replace:
        check_tab_body_replacement(tab_match, allow_lossy=allow_lossy)
        # Deletion retains the native final paragraph. Reset that paragraph
        # before insertion so its bullets, heading, alignment and spacing do
        # not become the initial state of every new paragraph.
        retained = {"startIndex": body_start, "endIndex": body_start + 1,
                    "tabId": tab_id}
        requests.extend([
            {"deleteParagraphBullets": {"range": retained}},
            {"updateParagraphStyle": {
                "range": retained,
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "*",
            }},
            {"updateTextStyle": {
                "range": retained, "textStyle": {}, "fields": "*",
            }},
        ])

    # Only inherited bullets require indent resets. Ordinary headings and
    # paragraphs must not materialize new zero-valued indent overrides.
    # A replacement keeps the final paragraph mark, so the inserted text
    # inherits that paragraph's bullet, not the first paragraph's.
    boundary = body_end if replace or position == "end" else body_start
    inherited_bullet = any(
        paragraph.get("bullet") for paragraph, _, _ in _replacement_paragraphs(
            body.get("content", []),
            {"startIndex": boundary, "endIndex": boundary + 1},
        )
    )
    if not replace and inherited_bullet:
        _reset_list_indents(parsed)
    insertion = to_docs_requests(parsed, insert_index, tab_id=tab_id)
    if at_end and parsed.plain_text.endswith("\n") and any(
        s.type == "paragraph_style" and s.end == len(parsed.plain_text)
        and "borderBottom" in s.style for s in parsed.styles
    ):
        # A trailing thematic break kept the parser's newline so its border
        # has a range. The mandatory final newline already follows the
        # insertion point and serves as that paragraph's mark, so insert one
        # character less; the style range already lands on it.
        text = parsed.plain_text[:-1]
        if text:
            insertion[0]["insertText"]["text"] = text
        else:
            del insertion[0]
    if not replace and inherited_bullet and parsed.plain_text:
        # After a leading table placeholder the reset starts past the
        # newline that now ends the existing list item.
        insertion.insert(1, {"deleteParagraphBullets": {"range": {
            "startIndex": insert_index + (1 if leading_table else 0),
            "endIndex": insert_index + utf16_len(parsed.plain_text),
            "tabId": tab_id,
        }}})
    if final_style is not None:
        final_index = (insert_index + utf16_len(parsed.plain_text)
                       - parsed.removed_tabs)
        insertion.append({"updateParagraphStyle": {
            "range": {"startIndex": final_index, "endIndex": final_index + 1,
                      "tabId": tab_id},
            "paragraphStyle": final_style,
            "fields": _paragraph_style_fields(final_style),
        }})
    requests.extend(insertion)

    with _StagedWrite(doc_id) as progress:
        if requests:
            revision_id = progress.batch(
                "tab text and formatting applied", requests, revision_id,
            )
        if parsed.tables:
            for ordinal, table in reversed(list(enumerate(parsed.tables, 1))):
                # Earlier list-indent tabs have already been consumed.
                revision_id = _insert_table(
                    doc_id,
                    insert_index
                    + utf16_len(parsed.plain_text[:table.plain_text_offset])
                    - table.removed_tabs_before,
                    table, tab_id=tab_id, revision_id=revision_id, progress=progress,
                    resolve_index=_table_position_resolver(parsed, table, tab_id),
                    ordinal=ordinal, scaffolding=_table_scaffolding(parsed, table),
                )

    return {
        "tab_id": tab_id,
        "tab_title": tab_match["title"],
        "insert_index": insert_index,
    }


def check_tab_body_replacement(tab: dict, *, allow_lossy: bool = False) -> None:
    """Refuse native losses within one tab body before it is replaced.

    ``tab`` is a flattened tab (``body`` and ``lists`` keys). Lists live
    beside the body; only definitions used by its paragraphs (including
    cells) are inspected, not header/footer-only lists.
    """
    from gdoc.lossy import check_markdown_replacement

    body = tab.get("body", {})
    body_start, body_end = _tab_body_range(body)
    list_ids = {
        paragraph.get("bullet", {}).get("listId")
        for paragraph, _, _ in _replacement_paragraphs(
            body.get("content", []),
            {"startIndex": body_start, "endIndex": body_end + 1},
        )
    }
    scope = {"body": body, "lists": {
        key: value for key, value in tab.get("lists", {}).items()
        if key in list_ids
    }}
    check_markdown_replacement(scope, tab_body=True, allow_lossy=allow_lossy)


def _replacement_paragraphs(content: list[dict], match: dict):
    """Yield intersected native paragraphs, including paragraphs in cells."""
    for element in content:
        paragraph = element.get("paragraph")
        if paragraph:
            elements = paragraph.get("elements", [])
            if elements:
                start = elements[0].get("startIndex", element.get("startIndex", 0))
                end = elements[-1].get("endIndex", element.get("endIndex", start))
                if (start < match["endIndex"] or start == match["startIndex"]) \
                        and match["startIndex"] < end:
                    yield paragraph, start, end - 1
        for row in element.get("table", {}).get("tableRows", []):
            for cell in row.get("tableCells", []):
                yield from _replacement_paragraphs(cell.get("content", []), match)


def _covers_whole_paragraphs(content: list[dict], match: dict) -> bool:
    """True when the match spans complete native paragraphs, marks excluded."""
    native = list(_replacement_paragraphs(content, match))
    return bool(native) and (
        match["startIndex"] == native[0][1]
        and match["endIndex"] == native[-1][2]
    )


def _replacement_paragraph(content: list[dict], match: dict):
    """Find the paragraph containing the match without its paragraph mark."""
    for paragraph, start, end in _replacement_paragraphs(content, match):
        if start <= match["startIndex"] and match["endIndex"] <= end:
            return paragraph, start, end
    return None


def _paragraph_wording_matches(body: dict, match: dict, markdown: str):
    """Split a wording edit at native paragraph marks, which stay untouched.

    Retaining each mark preserves named styles, list IDs, nesting and custom
    paragraph properties without trying to reconstruct them from Markdown.
    """
    paragraphs = list(_replacement_paragraphs(body.get("content", []), match))
    if not paragraphs:
        return [(match, markdown)]
    # The matched terminal LF and its replacement denote the retained native
    # mark, not a new empty paragraph. Interior blank paragraphs still count.
    if match["endIndex"] == paragraphs[-1][2] + 1:
        markdown = markdown.removesuffix("\n")
    lines = markdown.split("\n") if markdown else [""] * len(paragraphs)
    if len(lines) != len(paragraphs):
        raise GdocError(
            f"paragraph count mismatch: matched {len(paragraphs)}, "
            f"replacement has {len(lines)}; edit each paragraph separately "
            "or use write --tab for structural body changes "
            "(--cell replaces an entire table cell)", exit_code=3,
        )
    result = []
    for (_, start, end), line in zip(paragraphs, lines):
        result.append(({**match, "startIndex": max(start, match["startIndex"]),
                        "endIndex": min(end, match["endIndex"])}, line))
    return result


def _wording_contexts(body: dict, match: dict, markdown: str):
    """Share contextual parsing between edits and suggestions, including fences."""
    from gdoc.mdparse import (
        _FENCE_RE,
        ParsedMarkdown,
        StyleRange,
        parse_markdown,
    )

    def _opens_block_fence(line: str) -> bool:
        # A backtick fence's info string cannot contain a backtick
        # (CommonMark 4.5), so a closed span such as ```code``` is inline.
        fence = _FENCE_RE.match(line)
        return bool(fence) and not (
            fence.group(1).startswith("`") and "`" in fence.group(2)
        )

    # Only complete paragraphs can become code lines (a match may include the
    # last paragraph's newline, clipped below); inside a paragraph the fence
    # lines are literal text like every other block marker.
    native = list(_replacement_paragraphs(body.get("content", []), match))
    whole = bool(native) and match["startIndex"] == native[0][1] and (
        match["endIndex"] in (native[-1][2], native[-1][2] + 1)
    )
    if "\n" in markdown and whole and any(
        _opens_block_fence(line) for line in markdown.split("\n")
    ):
        parsed = parse_markdown(markdown)
        check_inline_only_markdown(parsed)
        # Split rendered code, never its source lines: fence delimiters are
        # syntax, and asterisks/links inside the fence are literal code.
        text = parsed.plain_text.removesuffix("\n")
        rendered_count = sum(s.type == "paragraph_style" for s in parsed.styles)
        if native and rendered_count != len(native):
            raise GdocError(
                f"paragraph count mismatch: matched {len(native)}, "
                f"fenced replacement renders {rendered_count}; "
                "edit each paragraph separately", exit_code=3,
            )
        # The parser already removed its generated terminal mark. Clip the
        # old range as well so a real final empty code line is not stripped.
        clipped = ({**match, "endIndex": min(match["endIndex"], native[-1][2])}
                   if native else match)
        parts = _paragraph_wording_matches(body, clipped, text)
        offset = 0
        result = []
        for part, line in parts:
            end = offset + len(line)
            selected = ParsedMarkdown(line, [
                StyleRange(max(s.start, offset) - offset,
                           min(s.end, end) - offset, s.style, s.type)
                for s in parsed.styles if s.type == "text_style"
                and s.start < end and s.end > offset
            ])
            found = _replacement_paragraph(body.get("content", []), part)
            baseline = _inline_baseline(found[0], part, line) if found else []
            result.append((part, (selected, baseline)))
            offset = end + 1
        return result
    result = []
    for part, line in _paragraph_wording_matches(body, match, markdown):
        selected = parse_markdown(line)
        _strip_trailing_newline_unless_hr(selected)
        result.append((part, _contextual_replacement(selected, line, part, body)))
    return result


def _empty_paragraph_range(content: list[dict], match: dict):
    """Remove complete paragraphs, retaining native anchors and the final LF."""
    paragraphs = list(_replacement_paragraphs(content, match))
    if not paragraphs:
        return match
    # Positioned objects have no searchable character; their paragraph mark
    # must survive even when all of the paragraph's wording is deleted.
    if any(p.get("positionedObjectIds") for p, _, _ in paragraphs):
        return None
    first, last = paragraphs[0], paragraphs[-1]
    if match["startIndex"] != first[1] or match["endIndex"] < last[2]:
        return None
    for i, element in enumerate(content):
        if element.get("startIndex", 0) == last[1] and "paragraph" in element:
            start, end = first[1], last[2] + 1
            if i == len(content) - 1:
                end -= 1
                previous = next((e for e in content
                                 if e.get("endIndex") == start), None)
                if previous and "paragraph" in previous:
                    if not previous["paragraph"].get("positionedObjectIds"):
                        start -= 1
                elif previous and "table" in previous:
                    raise GdocError(
                        "cannot remove the mandatory final paragraph after a table; "
                        "replace its wording instead", exit_code=3,
                    )
            return {**match, "startIndex": start, "endIndex": end}
        for row in element.get("table", {}).get("tableRows", []):
            for cell in row.get("tableCells", []):
                if any(p[1] == first[1] for p in _replacement_paragraphs(
                        cell.get("content", []), match)):
                    return _empty_paragraph_range(cell.get("content", []), match)
    return None


def _replacement_text_style(runs: list[dict], match: dict, text: str):
    """Keep unique surviving runs, including plain runs, in source order.

    Unmatched gaps keep only styles common to their original runs. Ambiguous
    mixed rewrites keep common fields, never a guessed dominant style. Links
    require the full contiguous original label, uniquely at word boundaries.
    Offsets returned here are Python offsets into the replacement text.
    """
    start, end = match["startIndex"], match["endIndex"]
    targets = []
    links = []
    for run in runs:
        offset = run.get("startIndex", 0)
        source = run["textRun"]
        style = source.get("textStyle", {})
        link = style.get("link")
        if link:
            if links and links[-1][1] == offset and links[-1][3] == link:
                lo, _, label, _ = links[-1]
                links[-1] = (lo, run["endIndex"], label + source["content"], link)
            else:
                links.append((offset, run["endIndex"], source["content"], link))
        lo, hi = max(start, offset), min(end, run["endIndex"])
        if lo >= hi:
            continue
        raw = source["content"].encode("utf-16-le")
        label = raw[(lo - offset) * 2:(hi - offset) * 2].decode("utf-16-le")
        style = {k: v for k, v in style.items() if k != "link"}
        if targets and targets[-1][1] == style:
            targets[-1] = (targets[-1][0] + label, style)
        else:
            targets.append((label, style))
    if not targets or not text:
        return []

    def common(selected):
        return {k: v for k, v in selected[0][1].items()
                if all(style.get(k) == v for _, style in selected)} if selected else {}

    mapped = []
    for index, (label, style) in enumerate(targets):
        pos = text.find(label)
        if label and pos >= 0 and text.find(label, pos + 1) < 0:
            mapped.append((index, pos, pos + len(label), style))
    if any(left[2] > right[1] for left, right in zip(mapped, mapped[1:])):
        mapped = []
    result = []
    offset, source_index = 0, 0
    for index, lo, hi, style in mapped:
        if offset < lo:
            result.append((offset, lo, common(targets[source_index:index] or targets)))
        result.append((lo, hi, style))
        offset, source_index = hi, index + 1
    if offset < len(text):
        result.append((offset, len(text), common(targets[source_index:] or targets)))

    for lo, hi, label, link in links:
        if lo < start or hi > end or not label.strip():
            continue
        pos = text.find(label)
        stop = pos + len(label)
        if (pos < 0 or text.find(label, pos + 1) >= 0
                or (pos and label[0].isalnum() and text[pos - 1].isalnum())
                or (stop < len(text) and label[-1].isalnum() and text[stop].isalnum())):
            continue
        # Link spans may cross non-link formatting boundaries.
        split = []
        for a, b, style in result:
            boundaries = sorted({a, b, max(a, min(b, pos)), max(a, min(b, stop))})
            for left, right in zip(boundaries, boundaries[1:]):
                split.append((left, right, {**style, **(
                    {"link": link} if pos <= left < stop else {})}))
        result = split
    return result


def _inline_baseline(paragraph: dict, match: dict, text: str) -> list[dict]:
    """Restore target styles over inserted text, using masks for absent fields.

    Keep the complete desired style for restoring link decorations after
    explicit Markdown; only differing fields need an initial style request.
    """
    from gdoc.mdparse import utf16_len

    start, end = match["startIndex"], match["endIndex"]
    runs = [el for el in paragraph.get("elements", []) if "textRun" in el]
    if start == end:
        return []
    following = next((el["textRun"].get("textStyle", {}) for el in runs
                      if el.get("endIndex", 0) > end), {})
    neighbour = next(
        (el["textRun"].get("textStyle", {}) for el in runs
         if el.get("startIndex", 0) < start <= el.get("endIndex", 0)), following,
    )
    old_link = any("link" in el["textRun"].get("textStyle", {}) for el in runs
                   if el.get("startIndex", 0) < end and el["endIndex"] > start)
    result = []
    for lo, hi, target in _replacement_text_style(runs, match, text):
        fields = {key for key in target.keys() | neighbour.keys()
                  if target.get(key) != neighbour.get(key)}
        if old_link or "link" in target:
            fields.add("link")
        if "link" in target:
            # Setting links resets colour/underline unless included together.
            fields.update(key for key in ("foregroundColor", "underline")
                          if key in target)
        result.append({
            "range": {"startIndex": start + utf16_len(text[:lo]),
                      "endIndex": start + utf16_len(text[:hi])},
            "textStyle": dict(target), "fields": ",".join(sorted(fields)),
        })
    # A full-paragraph style request can implicitly include its retained LF.
    # Keep its direct style separately so the builder restores it last.
    if (runs and start == runs[0].get("startIndex", 0)
            and end == runs[-1]["endIndex"] - 1):
        mark = start + utf16_len(text)
        result.append({"range": {"startIndex": mark, "endIndex": mark + 1},
                       "textStyle": dict(runs[-1]["textRun"].get("textStyle", {})),
                       "fields": "", "retainedMark": True})
    return result


def _contextual_replacement(parsed, markdown: str, match: dict, body: dict):
    """Plan a paragraph edit without replacing its native paragraph mark.

    A partial-paragraph replacement is inline Markdown only (see
    ``parse_inline``): code spans follow CommonMark backtick-string matching
    and every block-level construct is literal text, because a partial
    replacement cannot start a block.
    """
    from gdoc.mdparse import ParsedMarkdown, parse_inline

    found = _replacement_paragraph(body.get("content", []), match)
    if not found:
        return parsed, None
    paragraph, start, end = found
    text, styles = parse_inline(markdown)
    explicit_paragraph = any(
        s.type == "bullets" or (s.type == "paragraph_style"
                               and s.style != {"namedStyleType": "NORMAL_TEXT"})
        for s in parsed.styles
    )
    whole = match["startIndex"] == start and match["endIndex"] == end
    # A complete paragraph can change its own style explicitly without
    # deleting its native mark or entering the block/cleanup path.
    if whole and explicit_paragraph and "\n" not in markdown and not parsed.tables:
        return parsed, []
    return (ParsedMarkdown(plain_text=text, styles=styles),
            _inline_baseline(paragraph, match, text))


def _match_space(match: dict) -> tuple[str, str]:
    """Identity of an independent Docs index space (empty segment = body)."""
    return match.get("tabId", ""), match.get("segmentId", "")


def _match_key(match: dict) -> tuple:
    return (*_match_space(match), match["startIndex"])


def _replacement_body(scope: dict | None, match: dict) -> dict | None:
    """Resolve paragraph/style context in the match's own index space."""
    if scope is None or "content" in scope:
        return scope
    for content, coordinates in _search_containers(scope):
        if _match_space(coordinates) == _match_space(match):
            return content
    raise GdocError("replacement container not found in source snapshot", exit_code=3)


def _replacement_order(match: dict) -> tuple:
    tab, segment = _match_space(match)
    kind_order = {"body": 0, "header": 1, "footer": 2, "footnote": 3}
    kind = kind_order.get(match.get("container", "body"), 4)
    return tab, bool(segment), kind, segment, -match["startIndex"]


def check_segment_replacement(parsed, markdown: str, matches: list[dict]) -> None:
    """Non-body replacements support a single plain/inline paragraph only."""
    if not any(m.get("segmentId") for m in matches):
        return
    try:
        check_inline_only_markdown(parsed)
    except GdocError:
        raise GdocError(
            "headers, footers, and footnotes support only plain or inline "
            "Markdown replacements", exit_code=3,
        ) from None
    # A fence needs its own closing line, so a single-line replacement is
    # inline Markdown: an unmatched backtick string stays literal and a
    # closed one is a code span. Reject a source newline (paragraph break or
    # fenced block) and a non-empty line the parser renders to nothing, such
    # as a fence delimiter pair, which would otherwise empty the segment.
    plain = parsed.plain_text.removesuffix("\n")
    if (markdown == "\n" or "\n" in plain
            or "\n" in markdown.removesuffix("\n")
            or (markdown.strip() and not plain.strip())):
        raise GdocError(
            "headers, footers, and footnotes support only plain or inline "
            "Markdown replacements", exit_code=3,
        )


def _build_replacement_requests(
    parsed, matches: list[dict], tab_id: str | None = None,
    *, contexts: dict | None = None, reset_bullets: set[tuple] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Build the delete+insert requests for a find/replace, last-to-first.

    Pure function shared by ``replace_formatted`` (EDIT) and
    ``suggest_replacement`` (SUGGEST). Matches are processed in descending
    startIndex order within each independent segment, with deterministic
    body/header/footer/footnote ordering between containers.

    Returns (sorted_matches, requests).
    """
    from gdoc.mdparse import to_docs_requests

    sorted_matches = sorted(matches, key=_replacement_order)
    all_requests: list[dict] = []
    for match in sorted_matches:
        match_tab = match.get("tabId", tab_id)
        segment_id = match.get("segmentId")
        # Delete the matched range (skip empty ranges — Docs API rejects
        # them with "The range should not be empty", and a zero-width
        # match is a pure insert).
        if match["endIndex"] > match["startIndex"]:
            delete_range = {
                "startIndex": match["startIndex"],
                "endIndex": match["endIndex"],
            }
            if match_tab:
                delete_range["tabId"] = match_tab
            if segment_id:
                delete_range["segmentId"] = segment_id
            all_requests.append({
                "deleteContentRange": {"range": delete_range}
            })
        selected, baseline = (contexts[_match_key(match)] if contexts is not None
                              else (parsed, None))
        requests = to_docs_requests(
            _inline_only(selected) if segment_id else selected,
            match["startIndex"], tab_id=match_tab,
        )
        if baseline is not None and selected.plain_text == "\n" and any(
            s.type == "paragraph_style" and "borderBottom" in s.style
            for s in selected.styles
        ):
            # The HR styles the retained native LF; inserting its renderer's
            # placeholder would create a second paragraph.
            requests = [r for r in requests if "insertText" not in r]
        if reset_bullets and _match_key(match) in reset_bullets:
            from gdoc.mdparse import utf16_len
            target = {"startIndex": match["startIndex"],
                      "endIndex": match["startIndex"]
                      + max(1, utf16_len(selected.plain_text))}
            if match_tab:
                target["tabId"] = match_tab
            requests.insert(1 if requests else 0,
                            {"deleteParagraphBullets": {"range": target}})
            if not selected.plain_text:
                requests.append({"updateParagraphStyle": {
                    "range": target,
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                    "fields": "namedStyleType,indentStart,indentEnd,indentFirstLine",
                }})
        if requests and baseline:
            updates = []
            for style in baseline:
                if style.get("retainedMark"):
                    continue
                target = dict(style["range"])
                if match_tab:
                    target["tabId"] = match_tab
                fields = style["fields"]
                if any("updateParagraphStyle" in request for request in requests):
                    fields = ",".join(sorted(
                        set(filter(None, fields.split(","))) | style["textStyle"].keys()
                    ))
                if fields:
                    updates.append({"updateTextStyle": {
                        "range": target,
                        "textStyle": {k: v for k, v in style["textStyle"].items()
                                      if k in fields.split(",")},
                        "fields": fields,
                    }})
                # A Markdown link replaces only the URL, retaining the target's
                # own decorations on its intersection with this style span.
                decor = {key: style["textStyle"][key]
                         for key in ("foregroundColor", "underline")
                         if key in style["textStyle"]}
                if decor:
                    for request in list(requests):
                        link = request.get("updateTextStyle", {})
                        if "link" not in link.get("textStyle", {}):
                            continue
                        lo = max(target["startIndex"], link["range"]["startIndex"])
                        hi = min(target["endIndex"], link["range"]["endIndex"])
                        if lo < hi:
                            requests.append({"updateTextStyle": {
                                "range": {**target, "startIndex": lo, "endIndex": hi},
                                "textStyle": decor, "fields": ",".join(sorted(decor)),
                            }})
            # Paragraph changes re-resolve direct text styles. Restore the
            # baseline after them, but before explicit inline styles/bullets.
            before_inline = next(
                (i for i, req in enumerate(requests)
                 if "updateTextStyle" in req or "createParagraphBullets" in req),
                len(requests),
            )
            requests[before_inline:before_inline] = updates
            for style in baseline:
                if not style.get("retainedMark"):
                    continue
                fields = set().union(*(set(r["updateTextStyle"]["fields"].split(","))
                                      for r in requests if "updateTextStyle" in r))
                if fields:
                    target = dict(style["range"])
                    if match_tab:
                        target["tabId"] = match_tab
                    requests.append({"updateTextStyle": {
                        "range": target,
                        "textStyle": {k: v for k, v in style["textStyle"].items()
                                      if k in fields},
                        "fields": ",".join(sorted(fields)),
                    }})
        if segment_id:
            for request in requests:
                operation = next(iter(request.values()))
                address = operation.get("range", operation.get("location"))
                address["segmentId"] = segment_id
        all_requests.extend(requests)
    return sorted_matches, all_requests


def replace_formatted(
    doc_id: str,
    matches: list[dict],
    new_markdown: str,
    revision_id: str,
    tab_id: str | None = None,
    *, body: dict | None = None, replace_paragraphs: bool = False,
) -> int:
    """Replace matched text ranges with formatted content.

    Builds and executes a single batchUpdate with
    writeControl.requiredRevisionId. Processes matches last-to-first
    so index shifts don't affect earlier replacements.

    Args:
        doc_id: The document ID.
        matches: List of {"startIndex": int, "endIndex": int}.
        new_markdown: Replacement text (may contain markdown).
        revision_id: The document revision ID for concurrency control.
        tab_id: Optional tab ID for targeting a specific tab.
        body: Original body with paragraph and direct run styles for inline edits.
        replace_paragraphs: Whole-cell replacement may change paragraph count.
            Plain prose replaces list items with NORMAL_TEXT; non-list prose
            preserves native paragraph styles.

    Returns:
        Number of replacements made.
    """
    from gdoc.mdparse import parse_markdown, utf16_len

    parsed = parse_markdown(new_markdown)
    check_segment_replacement(parsed, new_markdown, matches)

    # Same guard as suggest_replacement: overlapping matches ("aa" in
    # "aaa" with --all) would make the last-to-first delete/insert plan
    # land on already-shifted text and corrupt the document.
    _reject_overlapping_matches(matches)

    _strip_trailing_newline_unless_hr(parsed)

    occurrence_count = len(matches)
    planned = []
    reset_bullets = set()
    source = body
    for match in matches:
        body = _replacement_body(source, match)
        # Whole-cell selection permits structural changes. Equal-count edits
        # retain native marks, with list removal handled explicitly below.
        native = (list(_replacement_paragraphs(body.get("content", []), match))
                  if body is not None else [])
        # A table replacing complete paragraphs is structural and must reach
        # _insert_table; inside a paragraph its source stays literal text.
        whole = _covers_whole_paragraphs(body.get("content", []), match) \
            if body is not None else False
        if replace_paragraphs:
            contextual = body is not None and not parsed.tables and (
                len(native) == len(new_markdown.split("\n"))
            )
        else:
            contextual = body is not None and not (parsed.tables and whole)
        if body is not None and not new_markdown and not replace_paragraphs:
            from gdoc.mdparse import ParsedMarkdown
            parts = [
                (_empty_paragraph_range(body.get("content", []), part) or part,
                 (ParsedMarkdown(""), []))
                for part, _ in _paragraph_wording_matches(body, match, "")
            ]
        elif contextual:
            parts = _wording_contexts(body, match, new_markdown)
        elif native and replace_paragraphs and not parsed.tables and not any(
            s.type == "bullets" or (s.type == "paragraph_style"
                                   and s.style != {"namedStyleType": "NORMAL_TEXT"})
            for s in parsed.styles
        ):
            # Collapsing/expanding cell wording still inherits the native
            # paragraph's custom properties; NORMAL_TEXT would reset them.
            paragraph = {"elements": [run for p, _, _ in native
                                      for run in p.get("elements", [])]}
            parts = [(match, (_inline_only(parsed), _inline_baseline(
                paragraph, match, parsed.plain_text,
            )))]
        else:
            parts = [(match, (parsed, None))]
        for part, context in parts:
            found = (_replacement_paragraph(body.get("content", []), part)
                     if body is not None else None)
            explicit = any(s.type in ("paragraph_style", "bullets")
                           for s in context[0].styles)
            # A structural collapse keeps only the last paragraph's mark, so
            # its bullet is the one the inserted prose would inherit.
            if replace_paragraphs and not explicit and native and (
                not new_markdown or (found and found[0].get("bullet"))
                or (not contextual and native[-1][0].get("bullet"))
            ):
                # Plain whole-cell prose is the explicit list-removal route.
                # Keep non-list paragraph properties and ordinary edits intact.
                from gdoc.mdparse import StyleRange
                context[0].styles.append(StyleRange(
                    0, len(context[0].plain_text),
                    {"namedStyleType": "NORMAL_TEXT"}, "paragraph_style",
                ))
                reset_bullets.add(_match_key(part))
                _reset_list_indents(context[0])
            elif explicit and (
                (replace_paragraphs and not contextual)
                or (found and found[0].get("bullet"))
            ):
                reset_bullets.add(_match_key(part))
                _reset_list_indents(context[0])
            planned.append((part, context))
    if not new_markdown and not replace_paragraphs:
        # Final-paragraph removal borrows the preceding LF. Adjacent targets
        # may therefore overlap: delete their union once, in original indexes.
        merged = []
        for part, context in sorted(planned, key=lambda p: _match_key(p[0])):
            if (merged and _match_space(part) == _match_space(merged[-1][0])
                    and part["startIndex"] <= merged[-1][0]["endIndex"]):
                previous = merged[-1][0]
                previous["endIndex"] = max(previous["endIndex"], part["endIndex"])
            else:
                merged.append((dict(part), context))
        # A merged group ending at the segment boundary needs the LF before
        # the entire group, rather than the LF between its last two members.
        planned = []
        for part, context in merged:
            body = _replacement_body(source, part)
            if body is not None:
                part = _empty_paragraph_range(body.get("content", []), part) or part
            planned.append((part, context))
    matches = [part for part, _ in planned]
    contexts = {_match_key(part): context for part, context in planned}
    # Table insertion after the main batch tracks index shifts for a single
    # block-path match only. Inline matches insert the table source literally
    # and never reach _insert_table, so they do not count.
    block_paths = sum(1 for _, baseline in contexts.values() if baseline is None)
    if parsed.tables and block_paths > 1:
        raise GdocError(
            "replacement with tables not supported with --all", exit_code=3,
        )
    sorted_matches, all_requests = _build_replacement_requests(
        parsed, matches, tab_id=tab_id, contexts=contexts,
        reset_bullets=reset_bullets,
    )

    if not all_requests:
        return 0

    # Each lower replacement may have a different rendered length when
    # --all includes both partial and complete paragraph matches.
    shifts = {}
    totals = {}
    for match in reversed(sorted_matches):
        pos = match["startIndex"]
        selected, _ = contexts[_match_key(match)]
        space = _match_space(match)
        shifts[_match_key(match)] = totals.get(space, 0)
        totals[space] = (totals.get(space, 0) + utf16_len(selected.plain_text)
                         - selected.removed_tabs - (match["endIndex"] - pos))

    with _StagedWrite(doc_id) as progress:
        revision_id = progress.batch(
            "matched text and formatting replaced", all_requests, revision_id,
        )

        # Insert tables only for explicit structural replacements.
        if parsed.tables:
            for ordinal, table in reversed(list(enumerate(parsed.tables, 1))):
                # UTF-16 offset of the table placeholder; invariant per
                # table, so hoisted out of the per-match loop.
                offset16 = utf16_len(
                    parsed.plain_text[:table.plain_text_offset],
                )
                for match in sorted_matches:
                    if contexts[_match_key(match)][1] is not None:
                        continue
                    shift = shifts[_match_key(match)]
                    idx = (
                        match["startIndex"] + offset16
                        - table.removed_tabs_before + shift
                    )
                    revision_id = _insert_table(
                        doc_id, idx, table, tab_id=match.get("tabId", tab_id),
                        revision_id=revision_id,
                        progress=progress,
                        resolve_index=_table_position_resolver(
                            parsed, table, match.get("tabId", tab_id),
                        ),
                        ordinal=ordinal, scaffolding=_table_scaffolding(parsed, table),
                    )

        return occurrence_count


# ---------------------------------------------------------------------------
# Suggested edits (Docs API Developer Preview: writeControl.writeMode=SUGGEST)
# ---------------------------------------------------------------------------

SUGGESTIONS_INLINE = "SUGGESTIONS_INLINE"

_SUGGEST_UNSUPPORTED_HINT = (
    "suggest supports plain text and inline formatting (bold, italic, "
    "strikethrough, code, links); headings, lists, blockquotes, horizontal "
    "rules, and tables are not supported yet. Use `gdoc edit` to apply "
    "structural Markdown directly."
)


@dataclass
class SuggestionResult:
    """Outcome of a suggest-mode batchUpdate.

    ``created_suggestion_ids`` come from ``suggestionResponses[].
    createdSuggestionIds``; ``updated_suggestion_ids`` from
    ``updatedSummarySuggestionIds`` minus anything created in the same batch
    (Google merges an edit adjacent to the same author's open suggestion
    into it instead of creating a new one, and also echoes new IDs under
    "updated"). Both are flattened across responses and de-duplicated in
    order.
    """

    occurrences: int
    created_suggestion_ids: list[str] = field(default_factory=list)
    updated_suggestion_ids: list[str] = field(default_factory=list)
    comment_update_state: str = ""

    @property
    def suggestion_ids(self) -> list[str]:
        """Every affected suggestion ID, created first, no duplicates."""
        return _dedupe(self.created_suggestion_ids + self.updated_suggestion_ids)


def _dedupe(ids: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for i in ids:
        if i and i not in seen:
            seen.add(i)
            out.append(i)
    return out


def check_inline_only_markdown(parsed) -> None:
    """Reject replacement Markdown that suggest mode can't represent yet.

    Suggest mode runs one batch only — no read-back cleanup or table
    insertion phases (those would each have to stay in SUGGEST mode and
    Google's suggested-structure shapes are unverified). So anything that
    is not plain text or an inline text style fails here, before any API
    call, with a usage error (exit 3).

    Newlines are allowed: they become suggested paragraph breaks, and the
    new paragraphs inherit the anchor paragraph's style (no paragraph-style
    requests are sent in suggest mode). Fenced code blocks pass too — they
    parse to plain NORMAL_TEXT paragraphs in the code font.
    """
    if parsed.tables:
        raise GdocError(_SUGGEST_UNSUPPORTED_HINT, exit_code=3)
    for sr in parsed.styles:
        if sr.type == "text_style":
            continue
        if sr.type == "paragraph_style" and sr.style == {
            "namedStyleType": "NORMAL_TEXT",
        }:
            # Plain paragraphs carry an explicit NORMAL_TEXT; harmless.
            continue
        raise GdocError(_SUGGEST_UNSUPPORTED_HINT, exit_code=3)


def _inline_only(parsed):
    """Copy of *parsed* keeping only text styles.

    The NORMAL_TEXT paragraph-style requests ``edit`` sends would become
    suggested paragraph-style changes on the surrounding paragraph — noise
    in the review thread. Suggested text inherits the paragraph's style.
    """
    from gdoc.mdparse import ParsedMarkdown

    return ParsedMarkdown(
        plain_text=parsed.plain_text,
        styles=[s for s in parsed.styles if s.type == "text_style"],
        tables=[],
        removed_tabs=0,
    )


def _walk_suggestion_ids(node, out: set[str]) -> None:
    """Collect every suggestion ID referenced anywhere under *node*.

    Schema-tolerant: any ``suggested*`` list contributes its string values
    (``suggestedInsertionIds``) and any ``suggested*`` map contributes its
    keys (``suggestedTextStyleChanges``, and also
    ``suggestedPositionedObjectIds``, which is a map keyed by suggestion ID
    despite its name), so new suggestion kinds are picked up without a
    code change.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key.startswith("suggested"):
                if isinstance(value, list):
                    out.update(v for v in value if isinstance(v, str))
                    continue
                if isinstance(value, dict):
                    out.update(value.keys())
                    continue
            _walk_suggestion_ids(value, out)
    elif isinstance(node, list):
        for item in node:
            _walk_suggestion_ids(item, out)


def collect_suggestion_ids(doc: dict) -> set[str]:
    """All suggestion IDs present in a SUGGESTIONS_INLINE document read."""
    out: set[str] = set()
    _walk_suggestion_ids(doc, out)
    return out


def _overlaps(elem: dict, start: int, end: int) -> bool:
    e_start = elem.get("startIndex", 0)
    e_end = elem.get("endIndex", e_start)
    if start == end:
        # zero-width match: an insertion point inside (or at the end of)
        # the element
        return e_start <= start < e_end or (e_start < start <= e_end)
    return e_start < end and start < e_end


def find_suggestions_in_range(body: dict, start: int, end: int) -> set[str]:
    """Suggestion IDs whose inline content or style map touches [start, end).

    Walks paragraphs (recursing into table cells) read with
    SUGGESTIONS_INLINE. For an overlapping paragraph, its paragraph-level
    ``suggested*`` fields count, plus every overlapping element's
    (``suggestedInsertionIds``, ``suggestedDeletionIds``,
    ``suggestedTextStyleChanges``, ...). For an overlapping table, the
    table's, each overlapping row's, and each overlapping cell's own
    ``suggested*`` fields count too (suggested table/row/cell insertions,
    deletions, and style changes), before recursing into the cell content.
    Any other overlapping structural element (a section break, a table of
    contents) has no index-aware model here, so every suggestion anywhere
    under it counts — conservative, like ``_container_overlaps``.
    """
    found: set[str] = set()
    for elem in body.get("content", []):
        if not _overlaps(elem, start, end):
            continue
        paragraph = elem.get("paragraph")
        if paragraph is not None:
            _walk_container_suggestions(paragraph, found)
            for pe in paragraph.get("elements", []):
                if _overlaps(pe, start, end):
                    _walk_suggestion_ids(pe, found)
            continue
        table = elem.get("table")
        if table is not None:
            # Container-level suggestions (a suggested table, row, or cell
            # insertion/deletion/style) are recorded on the container, not
            # on the text runs inside it.
            _walk_container_suggestions(table, found)
            for row in table.get("tableRows", []):
                if not _container_overlaps(row, start, end):
                    continue
                _walk_container_suggestions(row, found)
                for cell in row.get("tableCells", []):
                    if not _container_overlaps(cell, start, end):
                        continue
                    _walk_container_suggestions(cell, found)
                    found |= find_suggestions_in_range(cell, start, end)
            continue
        # sectionBreak, tableOfContents, or a future element type: a match
        # can span one (segments concatenate across them), and a suggested
        # section break / TOC entry is someone's review thread too.
        _walk_suggestion_ids(elem, found)
    return found


def _container_overlaps(node: dict, start: int, end: int) -> bool:
    """Rows/cells without index fields are not skipped (be conservative)."""
    if "startIndex" not in node or "endIndex" not in node:
        return True
    return _overlaps(node, start, end)


def _walk_container_suggestions(node: dict, out: set[str]) -> None:
    """Collect this node's own ``suggested*`` fields (no recursion)."""
    for key, value in node.items():
        if key.startswith("suggested"):
            _walk_suggestion_ids({key: value}, out)


def _classify_suggest_error(e: HttpError, doc_id: str) -> None:
    """Translate a suggest-mode batchUpdate HttpError, preserving the reason.

    Never falls back: a suggestion that cannot be made must not become a
    direct edit.
    """
    status = int(e.resp.status)
    detail = str(e)
    lowered = detail.lower()
    if (
        status == 400
        and "revision" in lowered
        and "invalid value" not in lowered
    ):
        # A stale requiredRevisionId. A malformed one ("Invalid value at
        # 'write_control.required_revision_id'") is a bug, not a race, and
        # must not be reported as "re-run it".
        raise GdocError(
            "document changed while the command was running; re-run it "
            f"(server: {e.reason})"
        )
    if status == 400 and (
        "unknown name" in lowered
        or "cannot find field" in lowered
        or "no request set" in lowered
        or "write_mode" in lowered
        or "writemode" in lowered
    ):
        raise GdocError(
            "suggest mode not available: the OAuth client's Cloud project "
            "is not enrolled in the Google Workspace Developer Preview "
            f"(server rejected the request: {e.reason}). No change was made."
        )
    if status == 403:
        raise GdocError(
            f"Permission denied: {doc_id} (suggesting through the API needs "
            "comment or edit access on the document, or the project lacks "
            "Developer Preview access)"
        )
    if status >= 500:
        # A 5xx can arrive after Google applied the mutation: like a
        # transport failure, the outcome is unknown and a blind retry may
        # create a duplicate suggestion.
        raise GdocError(
            f"the suggest write returned a server error ({status}: "
            f"{e.reason}). The outcome is unknown — the suggestion may or "
            "may not have been saved. Inspect the document before retrying."
        )
    _translate_http_error(e, doc_id)


def _token_identity(account: str | None) -> tuple[str | None, str | None]:
    """The (client_id, refresh_token) pair in the account's token file.

    The identity that must hold still between the enrollment gate and the
    write: Developer Preview enrollment belongs to the OAuth client
    project (client_id), and the suggestion's author is the granted user
    (refresh_token — any new grant mints a new one, whether the client or
    the Google user changed). A routine access-token refresh rewrites the
    file but keeps both. Missing or unreadable token reads as (None, None).
    """
    import json

    from gdoc.util import token_path_for

    try:
        with token_path_for(account).open() as f:
            data = json.load(f)
    except (OSError, ValueError):
        return (None, None)
    if not isinstance(data, dict):
        return (None, None)
    return (data.get("client_id"), data.get("refresh_token"))


def check_suggest_preview_access(doc_id: str) -> None:
    """Non-mutating gate: is this OAuth client's project preview-enrolled?

    An unenrolled backend has been observed *ignoring* ``writeMode: SUGGEST``
    and applying the batch as a direct edit, so enrollment must be proven
    before the write, not inferred from its response. The decisive probe
    is a ``documents.get`` with the preview-only ``commentsViewMode`` field:
    a registered project echoes it (HTTP 200), an unregistered one rejects
    it (400 ``Unknown name "comments_view_mode"``). Same account, document,
    and scopes — only the client project changes the answer.

    Sent as a raw authorized GET because the bundled discovery document
    predates the field and the generated client refuses unknown parameters.
    """
    from google.auth.exceptions import GoogleAuthError, TransportError
    from google.auth.transport.requests import AuthorizedSession
    from requests.exceptions import RequestException

    from gdoc.auth import get_credentials

    account, _stamp = account_cache_key()
    try:
        session = AuthorizedSession(get_credentials(account))
        resp = session.get(
            f"https://docs.googleapis.com/v1/documents/{doc_id}",
            params={
                # Google requires the two companions ("Comments view mode
                # may only be specified if tabs content is also requested"
                # / "... if inline suggestions are also explicitly
                # requested").
                "includeTabsContent": "true",
                "suggestionsViewMode": "SUGGESTIONS_INLINE",
                "commentsViewMode": "COMMENTS_VIEW_MODE_INCLUDED",
                "fields": "documentId,commentsViewMode",
            },
            timeout=60,
        )
    except TransportError as e:
        # google-auth wraps a network failure during token refresh in
        # TransportError (a GoogleAuthError subclass) — it is a transport
        # problem, not bad credentials, so it must not become "run
        # `gdoc auth`". Fail closed — nothing has been written.
        raise GdocError(
            "suggest mode check failed before any write "
            f"(network error: {e}). No change was made."
        )
    except GoogleAuthError as e:
        # Credentials that could not be refreshed (revoked, expired).
        raise AuthError(f"Authentication expired ({e}). Run `gdoc auth`.")
    except RequestException as e:
        # Transport failure: fail closed — nothing has been written.
        raise GdocError(
            "suggest mode check failed before any write "
            f"(network error: {e}). No change was made."
        )
    status = resp.status_code
    if status == 200:
        try:
            mode = resp.json().get("commentsViewMode", "")
        except ValueError:
            mode = ""
        if mode != "COMMENTS_VIEW_MODE_INCLUDED":
            raise GdocError(
                "suggest mode not available: the server accepted but did "
                "not apply the Developer Preview read field, so suggest "
                "mode cannot be trusted. No change was made."
            )
        return
    detail = resp.text.lower()
    if status == 400 and (
        "unknown name" in detail or "cannot find field" in detail
    ):
        raise GdocError(
            "suggest mode not available: the OAuth client's Cloud project "
            "is not enrolled in the Google Workspace Developer Preview "
            "(preview read field rejected). No change was made."
        )
    if status == 401:
        raise AuthError("Authentication expired. Run `gdoc auth`.")
    if status == 403:
        raise GdocError(
            f"Permission denied: {doc_id} (reading suggestions needs comment "
            "or edit access on the document)"
        )
    if status == 404:
        raise GdocError(f"Document not found: {doc_id}")
    raise GdocError(f"API error ({status}): {resp.reason}")


def _reject_overlapping_matches(matches: list[dict]) -> None:
    """Two matches sharing text (``aa`` in ``aaa``) can't both be replaced:
    the last-to-first delete/insert plan would land on shifted text."""
    ordered = sorted(matches, key=lambda m: (_match_space(m), m["startIndex"]))
    for prev, cur in zip(ordered, ordered[1:]):
        if (_match_space(prev) == _match_space(cur)
                and cur["startIndex"] < prev["endIndex"]):
            raise GdocError(
                "matches overlap each other (the anchor repeats within "
                f"itself around index {cur['startIndex']}); use a longer "
                "anchor or drop --all",
                exit_code=3,
            )


def suggest_replacement(
    doc_id: str,
    matches: list[dict],
    new_markdown: str,
    revision_id: str,
    tab_id: str | None = None,
    expected_token_identity: tuple[str | None, str | None] | None = None,
    *, body: dict | None = None,
) -> SuggestionResult:
    """Replace matched ranges as *suggested* edits (writeMode=SUGGEST).

    One batchUpdate carries the delete + insert + inline-style requests for
    every match, with ``writeControl.requiredRevisionId`` pinned to the
    revision the matches were computed against. Before it, a non-mutating
    preview read (``check_suggest_preview_access``) proves the project is
    enrolled, because an unenrolled backend may silently apply the batch as
    a direct edit. Success requires all of:
    HTTP 200, ``commentUpdateState == ALL_SAVED``, at least one created or
    updated suggestion ID in ``suggestionResponses``, and a SUGGESTIONS_INLINE
    read-back containing every one of those IDs. Anything less raises —
    there is deliberately no fallback to a direct edit.

    Args:
        doc_id: The document ID.
        matches: ``{"startIndex", "endIndex"}`` ranges in the
            SUGGESTIONS_INLINE index space of *tab_id*.
        new_markdown: Replacement text; plain or inline Markdown only
            (see ``check_inline_only_markdown``).
        revision_id: Non-empty revision the ranges were read at.
        tab_id: Tab holding the ranges (omitted → first tab).
        expected_token_identity: ``_token_identity()`` captured before the
            document read; when given, the pre-write identity check uses it
            as the baseline, extending the re-auth guard across the read
            (the CLI passes it). Omitted → the baseline is captured here,
            guarding the gate→write pair only.
        body: Source snapshot for native paragraph marks and target run styles.
    """
    from google.auth.exceptions import GoogleAuthError, TransportError

    from gdoc.mdparse import parse_markdown

    if not revision_id:
        raise GdocError(
            "cannot suggest: the document read did not include a revision "
            "ID, so the write cannot be pinned to the text that was "
            "matched. Google withholds revisionId from users without "
            "comment or edit access; suggesting through the API needs at "
            "least commenter permission on the document."
        )

    parsed = parse_markdown(new_markdown)
    if body is None:
        check_inline_only_markdown(parsed)
    check_segment_replacement(parsed, new_markdown, matches)
    _reject_overlapping_matches(matches)
    _strip_trailing_newline_unless_hr(parsed)
    occurrence_count = len(matches)
    if body is None:
        _, requests = _build_replacement_requests(_inline_only(parsed), matches,
                                                 tab_id=tab_id)
    else:
        if parsed.tables and any(
            _covers_whole_paragraphs(
                _replacement_body(body, match).get("content", []), match)
            for match in matches
        ):
            # edit would insert a native table here; suggest cannot, and
            # literal rows would misrepresent the request. Inside a
            # paragraph the rows are literal text, as in edit.
            check_inline_only_markdown(parsed)
        planned = [part for match in matches
                   for part in _wording_contexts(
                       _replacement_body(body, match), match, new_markdown)]
        # Validate each resolved context before planning suggestion requests.
        for _, (selected, _) in planned:
            check_inline_only_markdown(selected)
        requests = []
        for match, (selected, baseline) in sorted(
                planned, key=lambda part: _replacement_order(part[0])):
            # A SUGGEST style update changes the accepted preview only. Never
            # mistake that proposal for the pending insertion's native style.
            baseline = [s for s in baseline or [] if not s.get("retainedMark")]
            scope = _replacement_body(body, match)
            found = _replacement_paragraph(scope.get("content", []), match)
            runs = [run for run in found[0].get("elements", [])
                    if "textRun" in run] if found else []
            # Unlike EDIT, SUGGEST retains the original at paragraph start.
            # Its first run supplies insertion style, not the following run
            # used by the edit baseline; an empty field mask is not proof of
            # safety. Check the desired native style at every target position.
            pending_style = next(
                (run["textRun"].get("textStyle", {}) for run in runs
                 if run.get("startIndex", 0) < match["startIndex"] <= run["endIndex"]),
                runs[0]["textRun"].get("textStyle", {}) if runs else {},
            )
            at_target_end = bool(selected.plain_text and any(
                s["fields"] or s["textStyle"] != pending_style for s in baseline))
            if at_target_end:
                source_style = next((
                    run["textRun"].get("textStyle", {})
                    for run in found[0].get("elements", [])
                    if "textRun" in run and run.get("startIndex", 0)
                    < match["endIndex"] <= run["endIndex"]
                ), {}) if found else {}
                if (not found or "link" in source_style
                        or any(s["textStyle"] != source_style for s in baseline)):
                    raise GdocError(
                        "cannot suggest this replacement while preserving its pending "
                        "text style: mixed or linked targets require "
                        "formatting that the API can only propose for acceptance; "
                        "use narrower uniformly styled, unlinked matches "
                        "or edit instead",
                        exit_code=3,
                    )
                # Insert while the matched run still exists so its own style
                # is inherited. Suggest deletion afterwards; the native pending
                # order is old+new, and rejecting retains the untouched original.
                insertion = {**match, "startIndex": match["endIndex"]}
                context = (_inline_only(selected), [])
                _, built = _build_replacement_requests(
                    parsed, [insertion], tab_id=tab_id,
                    contexts={_match_key(insertion): context},
                )
                delete_range = {key: match[key] for key in
                                ("startIndex", "endIndex", "tabId", "segmentId")
                                if key in match}
                if tab_id and "tabId" not in delete_range:
                    delete_range["tabId"] = tab_id
                built.append({"deleteContentRange": {"range": delete_range}})
            else:
                _, built = _build_replacement_requests(
                    parsed, [match], tab_id=tab_id,
                    contexts={_match_key(match): (_inline_only(selected), baseline)},
                )
            requests.extend(built)
    if not requests:
        return SuggestionResult(occurrences=0)

    # Prove enrollment with a read before the write (see the gate's doc),
    # pinning one OAuth identity across both: a re-auth landing between
    # them could otherwise swap the client project (proving enrollment for
    # one project while the batch goes through another — which an
    # unenrolled backend may apply as a direct edit) or the granted user
    # (authoring the suggestion as someone else). The pin is the token's
    # (client_id, refresh_token) pair, not the file's identity: a routine
    # access-token refresh (the gate's own get_credentials persists one
    # when a long-lived process refreshed only in memory) rewrites the
    # file but keeps both, and must not abort; any new grant mints a new
    # refresh_token.
    account, _stamp = account_cache_key()
    gate_identity = (
        expected_token_identity
        if expected_token_identity is not None
        else _token_identity(account)
    )
    # The gate, the service lookup, and the verification read each resolve
    # the active account themselves; pin the one captured above so an
    # unpinned direct call cannot have a concurrent default-account change
    # split them across two accounts (the CLI and MCP already pin — they
    # re-enter the same value).
    from gdoc.util import account_context

    with account_context(account):
        check_suggest_preview_access(doc_id)

        body = {
            "requests": requests,
            "writeControl": {
                "requiredRevisionId": revision_id,
                "writeMode": "SUGGEST",
            },
        }
        service = get_docs_service()
        if _token_identity(account) != gate_identity:
            raise GdocError(
                "credentials changed while preparing the suggest write "
                "(the account was re-authenticated between the enrollment "
                "check and the write, so the check may have proven a "
                "different OAuth client project or user). No change was "
                "made — rerun the command."
            )
        try:
            result = (
                service.documents()
                .batchUpdate(documentId=doc_id, body=body)
                .execute()
            )
        except HttpError as e:
            _classify_suggest_error(e, doc_id)
        except TransportError as e:
            # Raised only while refreshing the access token, which happens
            # before the request is sent — nothing reached Google.
            raise GdocError(
                "the suggest write failed before it was sent (network "
                f"error during token refresh: {e}). No change was made."
            )
        except GoogleAuthError as e:
            # Credential failure (revoked/expired beyond refresh) — also
            # pre-send, and an auth problem, not an indeterminate write.
            raise AuthError(f"Authentication expired ({e}). Run `gdoc auth`.")
        except Exception as e:  # noqa: BLE001 — .execute() is the network
            # call; a timeout or reset here can land after Google has
            # accepted the write, so the outcome is genuinely
            # indeterminate. A generic unexpected error would let the
            # caller retry blindly.
            raise GdocError(
                "the suggest write failed in transit "
                f"({str(e) or type(e).__name__}). The outcome is unknown — "
                "the suggestion may or may not have been saved. Inspect "
                "the document before retrying."
            )

        state = result.get("commentUpdateState", "")
        created: list[str] = []
        updated: list[str] = []
        for resp in result.get("suggestionResponses", []) or []:
            created.extend(resp.get("createdSuggestionIds", []) or [])
            updated.extend(resp.get("updatedSummarySuggestionIds", []) or [])
        created = _dedupe(created)
        # Google echoes a just-created ID under updatedSummarySuggestionIds
        # as well; report as "updated" only threads that existed before this
        # batch (i.e. the edit was merged into the author's open suggestion).
        updated = [sid for sid in _dedupe(updated) if sid not in created]
        outcome = SuggestionResult(
            occurrences=occurrence_count,
            created_suggestion_ids=created,
            updated_suggestion_ids=updated,
            comment_update_state=state,
        )

        if state != "ALL_SAVED" or not outcome.suggestion_ids:
            # The server answered 200 but produced no durable review object:
            # either it ignored writeMode (an unenrolled backend has been
            # seen applying the change directly) or the suggestion thread
            # failed to save. Say so loudly; the caller must inspect the
            # document.
            raise GdocError(
                "suggest mode was not applied: the server returned "
                f"commentUpdateState={state or 'none'} and "
                f"{len(outcome.suggestion_ids)} suggestion ID(s)"
                + (
                    # Name any IDs that did come back: some review objects
                    # may exist, and a caller deciding whether to retry
                    # must be able to find them.
                    " (" + ", ".join(outcome.suggestion_ids) + ")"
                    if outcome.suggestion_ids
                    else ""
                )
                + ". The Cloud project may lack Developer Preview access. "
                "Check the document — the text may have been edited "
                "directly."
            )

        try:
            readback = get_document_structure(
                doc_id, suggestions_view_mode=SUGGESTIONS_INLINE,
            )
        except Exception as e:  # noqa: BLE001 — the write succeeded; only
            # the verification read failed, either as a GdocError from the
            # API layer or as an untranslated transport error (timeout,
            # reset). A bare "API error (503)" — or a naked ConnectionError
            # — would hide that a suggestion very likely exists now.
            raise GdocError(
                "suggestion(s) " + ", ".join(outcome.suggestion_ids)
                + " were reported saved but could not be verified "
                f"({str(e) or type(e).__name__}); inspect the document",
                exit_code=getattr(e, "exit_code", 1),
            )
        present = collect_suggestion_ids(readback)
        missing = [
            sid for sid in outcome.suggestion_ids if sid not in present
        ]
        if missing:
            raise GdocError(
                "suggestion not found on read-back: "
                + ", ".join(missing)
                + ". The server reported it but the document does not show "
                "it as a pending suggestion; inspect the document."
            )
        return outcome
