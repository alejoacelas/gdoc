"""Line-numbered comment annotation engine for cat --comments."""

import re

from gdoc.util import fold_unicode_spaces


def _format_author(author_dict: dict) -> str:
    """Format author for display: prefer email, fallback to name."""
    if not author_dict:
        return "unknown"
    return (author_dict.get("emailAddress") or
            author_dict.get("displayName") or "unknown")


def _format_annotation_block(
    comment: dict,
    anchor_text: str | None = None,
    fallback_note: str = "",
) -> list[str]:
    """Build annotation lines for a single comment.

    Returns list of un-numbered annotation lines (no line-number prefix).
    """
    prefix = "      \t"
    lines = []

    cid = comment.get("id", "")
    resolved = comment.get("resolved", False)
    status = "resolved" if resolved else "open"
    author = _format_author(comment.get("author", {}))
    content = comment.get("content", "")

    # Header line
    status_part = f"[#{cid} {status}]"
    if fallback_note:
        status_part += f" [{fallback_note}]"

    if anchor_text is not None:
        # Anchored: show truncated anchor text
        display_anchor = anchor_text
        if len(display_anchor) > 40:
            display_anchor = display_anchor[:37] + "..."
        lines.append(f'{prefix}  {status_part} {author} on "{display_anchor}":')
    else:
        lines.append(f'{prefix}  {status_part} {author}: "{content}"')
        # For unanchored, content is on the header line, no separate content line
        # Add replies
        for r in comment.get("replies", []):
            reply_content = r.get("content", "")
            if not reply_content:
                continue
            r_author = _format_author(r.get("author", {}))
            lines.append(f'{prefix}    > {r_author}: "{reply_content}"')
        return lines

    # Content line (for anchored comments)
    lines.append(f'{prefix}    "{content}"')

    # Reply lines
    for r in comment.get("replies", []):
        reply_content = r.get("content", "")
        if not reply_content:
            continue  # Skip action-only replies
        r_author = _format_author(r.get("author", {}))
        lines.append(f'{prefix}    > {r_author}: "{reply_content}"')

    return lines


_FENCE_LINE_RE = re.compile(r"^(?:[ \t]*>)*[ \t]*(`{3,}|~{3,})")


def _decode_prose_escapes(markdown: str) -> str:
    """Drop Markdown escapes outside code, keeping lines and code literal.

    Fenced code lines and code spans display their backslashes, so only prose
    escapes are decoded for anchor matching.
    """
    from gdoc.mdparse import _ESCAPABLE

    lines = []
    fence = None
    for line in markdown.split("\n"):
        opener = _FENCE_LINE_RE.match(line)
        if fence is not None:
            if opener and opener[1][0] == fence[0] and len(opener[1]) >= len(fence):
                fence = None
            lines.append(line)
            continue
        if opener:
            fence = opener[1]
            lines.append(line)
            continue
        out, i = [], 0
        while i < len(line):
            if line[i] == "\\" and i + 1 < len(line) and line[i + 1] in _ESCAPABLE:
                out.append(line[i + 1])
                i += 2
            elif line[i] == "`":
                run = len(line[i:]) - len(line[i:].lstrip("`"))
                close = re.compile(r"(?<!`)" + "`" * run + r"(?!`)")
                end = close.search(line, i + run)
                stop = end.end() if end else i + run
                out.append(line[i:stop])
                i = stop
            else:
                out.append(line[i])
                i += 1
        lines.append("".join(out))
    return "\n".join(lines)


def _displayed_lines(markdown: str) -> str:
    """Each prose line as displayed (no emphasis or link syntax); code lines,
    whose characters are literal, stay as written."""
    from gdoc.mdparse import _FENCE_CLOSE_RE, _fence_open, _unquote, parse_inline

    out, fence = [], None
    for line in markdown.split("\n"):
        body = _unquote(line)[0].lstrip(" ")
        if fence is not None:
            close = _FENCE_CLOSE_RE.match(body)
            if close and close[1][0] == fence[0] and len(close[1]) >= len(fence):
                fence = None
            out.append(line)
        elif opener := _fence_open(body):
            fence = opener[1]
            out.append(line)
        else:
            out.append(parse_inline(line)[0])
    return "\n".join(out)


def _find_anchor(markdown: str, anchor_text: str) -> tuple[str, str, int]:
    """Locate an anchor exactly, then space-folded, then without prose escapes."""
    search_text, search_anchor = markdown, anchor_text
    pos = search_text.find(search_anchor)
    if pos == -1:
        search_text = fold_unicode_spaces(markdown)
        search_anchor = fold_unicode_spaces(anchor_text)
        pos = search_text.find(search_anchor)
    if pos == -1:
        # Exported Markdown escapes literal punctuation. Keep line breaks
        # while decoding so the matched line still refers to the display.
        search_text = fold_unicode_spaces(_decode_prose_escapes(markdown))
        search_anchor = fold_unicode_spaces(anchor_text)
        pos = search_text.find(search_anchor)
    if pos == -1:
        # An anchor can span emphasis or a link label: compare each line's
        # displayed text, one output line per Markdown line.
        search_text = fold_unicode_spaces(_displayed_lines(markdown))
        pos = search_text.find(search_anchor)
    return search_text, search_anchor, pos


def annotate_markdown(
    markdown: str,
    comments: list[dict],
    show_resolved: bool = False,
    other_tabs: list[str] | None = None,
) -> str:
    """Produce line-numbered annotated output with inline comment annotations.

    Args:
        markdown: Raw markdown content from export_doc.
        comments: Comment dicts from list_comments(include_anchor=True).
        show_resolved: If True, include resolved comments. If False,
            filter them out (defensive — caller should pre-filter).
        other_tabs: Markdown of the document's unselected tabs. Drive does
            not say which tab an anchor is in, so an anchor found only there
            is reported as in another tab, and one found in both as ambiguous.

    Returns:
        Annotated string with numbered content lines and un-numbered
        annotation lines.
    """
    # Defensive resolved filtering
    if not show_resolved:
        comments = [c for c in comments if not c.get("resolved", False)]

    lines = markdown.split("\n")
    # Remove trailing empty line from split if markdown ends with \n
    if lines and lines[-1] == "" and markdown.endswith("\n"):
        lines = lines[:-1]

    # Classify comments: anchored vs unanchored
    # line_annotations: line_index (0-based) -> list of (comment, anchor_text, fallback_note)
    line_annotations: dict[int, list[tuple[dict, str, str]]] = {}
    unanchored: list[tuple[dict, str]] = []  # (comment, fallback_note)

    for c in comments:
        qfc = c.get("quotedFileContent")
        if not qfc or not qfc.get("value"):
            # Unanchored comment
            unanchored.append((c, ""))
            continue

        anchor_text = qfc["value"]

        # Short anchor check
        if len(anchor_text.strip()) < 4:
            unanchored.append((c, "anchor too short"))
            continue

        search_text, search_anchor, pos = _find_anchor(markdown, anchor_text)
        elsewhere = any(_find_anchor(other, anchor_text)[2] != -1
                        for other in other_tabs or [])
        if pos == -1:
            unanchored.append((c, "anchor in another tab" if elsewhere
                               else "anchor deleted"))
            continue

        # Check for multiple matches
        second_pos = search_text.find(search_anchor, pos + 1)
        if second_pos != -1 or elsewhere:
            # Ambiguous
            unanchored.append((c, "anchor ambiguous"))
            continue

        # Single match — find line number
        # Count newlines up to end of match to find the last line of the span
        match_end = pos + len(search_anchor)
        line_idx = search_text[:match_end].count("\n")
        # Clamp to valid range
        if line_idx >= len(lines):
            line_idx = len(lines) - 1 if lines else 0

        if line_idx not in line_annotations:
            line_annotations[line_idx] = []
        line_annotations[line_idx].append((c, anchor_text, ""))

    # Build output
    output_lines: list[str] = []

    for i, line in enumerate(lines):
        line_num = i + 1
        output_lines.append(f"{line_num:>6}\t{line}")

        if i in line_annotations:
            for c, anchor_text, fallback_note in line_annotations[i]:
                annotation_lines = _format_annotation_block(
                    c, anchor_text=anchor_text, fallback_note=fallback_note,
                )
                output_lines.extend(annotation_lines)

    # Unanchored section
    if unanchored:
        output_lines.append("      \t[UNANCHORED]")
        for c, fallback_note in unanchored:
            annotation_lines = _format_annotation_block(
                c, anchor_text=None, fallback_note=fallback_note,
            )
            output_lines.extend(annotation_lines)

    # Final newline
    output_lines.append("")
    return "\n".join(output_lines)
