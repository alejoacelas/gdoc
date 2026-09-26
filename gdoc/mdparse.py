"""Lightweight markdown parser for Google Docs API batchUpdate requests."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field


@dataclass
class StyleRange:
    """A formatting annotation within parsed plain text."""

    start: int
    end: int
    style: dict
    type: str  # "text_style", "paragraph_style", "bullets", or inline "image"
    # Bullet-only parser metadata; never sent as native style properties.
    list_block: int | None = None
    list_depth: int = 0
    literal_tabs: int = 0
    list_group: int | None = None


@dataclass
class TableData:
    """A parsed markdown table with cell content and position info."""

    rows: list[list[str]]
    num_rows: int
    num_cols: int
    plain_text_offset: int  # code-point offset of the plain_text placeholder
    # Leading list-indent tabs inserted before this table. createParagraphBullets
    # removes those tabs, shifting the table's real position left by this many.
    removed_tabs_before: int = 0
    alignments: list[str | None] = field(default_factory=list)
    # Container prefix (quote depth, list indent) recorded by a named range.
    prefix: tuple[int, int] = (0, 0)
    # List-item indent before the quote markers of a quote inside an item.
    outer: int = 0


@dataclass
class ImageData:
    """One space placeholder, indexed before list-indent tabs are consumed."""

    plain_text_offset: int
    uri: str
    alt: str
    removed_tabs_before: int = 0
    object_size: dict | None = None


@dataclass
class CodeBlockData:
    """Complete code paragraphs, in code points before list tabs are removed."""

    start: int
    end: int


@dataclass
class ParsedMarkdown:
    """Result of parsing markdown: plain text + style annotations."""

    plain_text: str
    styles: list[StyleRange] = field(default_factory=list)
    tables: list[TableData] = field(default_factory=list)
    # Total leading list-indent tabs in plain_text. createParagraphBullets
    # removes them at apply time, so the document grows by len(plain_text)
    # minus this when the requests are applied.
    removed_tabs: int = 0
    # Numbering starts that native createParagraphBullets would reset to 1.
    non_default_list_starts: list[str] = field(default_factory=list)
    code_blocks: list[CodeBlockData] = field(default_factory=list)
    images: list[ImageData] = field(default_factory=list)
    # Per-paragraph pieces of one fenced replacement share this marker, so
    # the paragraphs they replace become one code block.
    code_group: object = None


# Inline patterns — order matters (bold+italic before bold/italic)
_BOLD_ITALIC_RE = re.compile(r"\*\*\*(.+?)\*\*\*")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
_ITALIC_RE = re.compile(
    r"(?<!\*)\*(?![\s*])(.+?)(?<![\s*])\*(?!\*)"
    r"|(?<![\w_])_(?![\s_])(.+?)(?<![\s_])_(?![\w_])"
)
# Strikethrough uses two tildes; a run of three or more is literal.
_STRIKE_RE = re.compile(r"(?<!~)~~(?!~)(.+?)(?<!~)~~(?!~)")
# Code spans follow CommonMark: a backtick string of length N (a run neither
# preceded nor followed by a backtick) opens a span that only a backtick string
# of the same length N closes; an unmatched backtick string is literal text.
# Content is inserted verbatim. This is the whole rule for fences on the inline
# path: ```code``` is a code span, and a fence that is never closed by an equal
# run is literal text.
_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\((.*)\)")

# Inline patterns in precedence order. Each entry: (regex, kind). On a tie at
# the same position, the earlier entry wins, so ***x*** beats **x**/*x*.
_INLINE_PATTERNS = [
    (_BOLD_ITALIC_RE, "bolditalic"),
    (_BOLD_RE, "bold"),
    (_ITALIC_RE, "italic"),
    (_STRIKE_RE, "strike"),
    (_CODE_RE, "code"),
    (_LINK_RE, "link"),
    (re.compile(r"&#(?:[0-9]+|x[0-9a-fA-F]+);|&[a-zA-Z][a-zA-Z0-9]+;"), "entity"),
    (re.compile(r"<img\b[^>]*>", re.IGNORECASE), "html_image"),
    # Exported run boundaries: no visible text, unlike a space or zero-width char.
    (re.compile(r"<!-- -->"), "separator"),
]

# Text-style dicts applied per emphasis kind (these recurse into their inner
# content so emphasis can nest, e.g. **bold _and italic_**).
_STYLES_FOR_KIND = {
    "bolditalic": [{"bold": True}, {"italic": True}],
    "bold": [{"bold": True}],
    "italic": [{"italic": True}],
    "strike": [{"strikethrough": True}],
}

_CODE_FONT = {"weightedFontFamily": {"fontFamily": "Courier New"}}

# Heading pattern
# A lone marker is an empty heading, so a trimmed "## " keeps its level.
_HEADING_RE = re.compile(r"^(#{1,6})(?:[ \t](.*))?$")
# Docs has two named styles with no ordinary Markdown heading equivalent.
_NAMED_STYLE_RE = re.compile(r"^<!-- gdoc:(TITLE|SUBTITLE) -->(?: (.*))?$")

# List item patterns (capture leading indentation for nesting)
_BULLET_RE = re.compile(r"^([ \t]*)[-*+](?:[ \t](.*)|$)")
_NUMBERED_RE = re.compile(r"^([ \t]*)\d+\.(?:[ \t](.*)|$)")

# Block patterns
_BLOCKQUOTE_RE = re.compile(r"^ {0,3}>\s?(.*)$")
_HR_RE = re.compile(r"^ {0,3}([-*_])[ ]*(?:\1[ ]*){2,}$")
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")


def _fence_open(line: str) -> re.Match | None:
    """Match a fence opener; a backtick fence's info string holds no backtick.

    CommonMark 4.5: ```` ```code``` ```` on one line is an inline code span,
    not an opening fence, so it must never swallow the rest of the input.
    """
    match = _FENCE_RE.match(line)
    if match and match.group(1)[0] == "`" and "`" in match.group(2):
        return None
    return match

# Table patterns
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
_TABLE_SEP_RE = re.compile(r"^\|[\s:]*-+[\s:]*(\|[\s:]*-+[\s:]*)*\|$")

# Characters a backslash may escape (CommonMark ASCII-punctuation set).
_ESCAPABLE = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

# Sentinel used to mask escaped characters so they cannot match (or break)
# the inline regexes. NUL never appears in real document text.
_MASK = "\x00"

# Indentation magnitude (PT) used for one level of blockquote indent.
_QUOTE_INDENT_PT = 36


def _mask_escapes(text: str) -> str:
    """Return a same-length copy of ``text`` with each backslash-escaped
    character blanked to a sentinel, so the inline regexes never match (or are
    broken by) an escaped marker. The backslash itself is left in place (it
    isn't a marker). Emitted text is sliced from the original, so the lengths
    must stay aligned — hence blanking in place rather than removing.
    """
    if "\\" not in text:
        return text
    out = list(text)
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "\\" and i + 1 < n and text[i + 1] in _ESCAPABLE:
            out[i + 1] = _MASK
            i += 2
        else:
            i += 1
    return "".join(out)


def _strip_escapes(s: str) -> str:
    """Drop escaping backslashes (``\\X`` -> ``X`` for escapable X), matching
    CommonMark. NOT applied inside code spans, whose content is literal.
    A backslash before a non-escapable character (or at end) is kept.
    """
    if "\\" not in s:
        return s
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "\\" and i + 1 < n and s[i + 1] in _ESCAPABLE:
            out.append(s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def _code_spans(text: str) -> list[re.Match]:
    """Code spans of ``text``, opened only by unescaped backticks."""
    spans = []
    code_end = 0
    for opener in re.finditer(r"(?<!`)(`+)(?!`)", _mask_escapes(text)):
        if opener.start() < code_end:
            continue
        if code := _CODE_RE.match(text, opener.start()):
            spans.append(code)
            code_end = code.end()
    return spans


def _table_cells(line: str) -> list[str]:
    """Split unescaped pipes, retaining inline escapes for the cell parser."""
    text = line[1:-1]
    masked = _mask_escapes(text)
    # Backslashes are literal inside code spans, where only "\\|" marks a pipe
    # of the content; elsewhere an escaped backslash leaves the pipe bare.
    in_code = [False] * len(text)
    for code in _code_spans(text):
        in_code[code.start():code.end()] = [True] * (code.end() - code.start())
    separators = [
        index for index, char in enumerate(text) if char == "|" and not (
            text[index - 1:index] == "\\" if in_code[index] else masked[index] != "|"
        )
    ]
    boundaries = [-1, *separators, len(text)]
    cells = []
    for start, end in zip(boundaries, boundaries[1:]):
        # Markdown trims only spaces and tabs; other edge whitespace is text.
        cell = text[start + 1:end].strip(" \t")
        parts = []
        cursor = 0
        for code in _code_spans(cell):
            parts.append(re.sub(r"\\.|<br>",
                                lambda m: "\n" if m[0] == "<br>" else m[0],
                                cell[cursor:code.start()]))
            parts.append(code[0].replace(r"\|", "|"))
            cursor = code.end()
        parts.append(re.sub(r"\\.|<br>",
                            lambda m: "\n" if m[0] == "<br>" else m[0],
                            cell[cursor:]))
        cells.append("".join(parts))
    return cells


def parse_inline(text: str) -> tuple[str, list[StyleRange]]:
    """Public: parse inline formatting from a single string.

    For callers (e.g. table-cell rendering and partial-paragraph edits) that
    need inline parsing without the block-level handling of `parse_markdown`.
    Only inline Markdown applies: bold, italic, strikethrough, CommonMark code
    spans, links and images. Image annotations use type="image", one space
    placeholder, and style={"uri": ..., "alt": ...}; native callers consume
    those separately from text-style requests. Every block-level construct
    (fences, list markers,
    headings, blockquotes, thematic breaks) is literal text, because inline
    content cannot start a block. Returns (plain_text, style_ranges) with
    offsets relative to plain_text.
    """
    return _parse_inline(text.replace("\r\n", "\n").replace("\r", "\n"))


def _parse_inline(
    text: str, references: dict | None = None,
) -> tuple[str, list[StyleRange]]:
    """Parse inline formatting from a text string.

    Returns (plain_text, style_ranges) with offsets relative to plain_text.
    Emphasis spans nest recursively; backslash escapes are resolved per
    segment (and left intact inside code spans).
    """
    text = _expand_link_references(text, references or {})
    return _scan(text, _mask_escapes(text), references)


def _find_link(masked: str) -> re.Match | None:
    """Find a link ending at its matching destination parenthesis.

    Escaped parentheses are already masked, so only unescaped delimiters
    contribute to depth. An unfinished destination is left as literal text.
    """
    # Match parentheses once, rather than rescanning the entire remaining input
    # for every malformed link opener (quadratic on repeated "[x](").
    closes = {}
    brackets = {}
    stack = []
    bracket_stack = []
    for index, char in enumerate(masked):
        if char == "\n":
            stack.clear()
            bracket_stack.clear()
        elif char == "[":
            bracket_stack.append(index)
        elif char == "]" and bracket_stack:
            brackets[bracket_stack.pop()] = index
        elif char == "(":
            stack.append(index)
        elif char == ")" and stack:
            closes[stack.pop()] = index
    for opener in re.finditer(r"\[", masked):
        label_end = brackets.get(opener.start())
        if label_end is None or masked[label_end + 1:label_end + 2] != "(":
            continue
        end = closes.get(label_end + 1)
        if end is not None and end > label_end + 2:
            width = label_end - opener.start() - 1
            return re.compile(r"\[([\s\S]{" + str(width)
                              + r"})\]\(([\s\S]*)\)").match(
                masked, opener.start(), end + 1,
            )
    return None


def _find_image(masked: str, references: dict):
    """Find a complete inline or defined reference image in linear time."""
    pairs = {}
    brackets = []
    parens = []
    for index, char in enumerate(masked):
        if char == "[":
            brackets.append(index)
        elif char == "]" and brackets:
            pairs[brackets.pop()] = index
        elif char == "(":
            parens.append(index)
        elif char == ")" and parens:
            pairs[parens.pop()] = index
        elif char == "\n":
            parens.clear()
    for opener in re.finditer(r"!\[", masked):
        close = pairs.get(opener.start() + 1)
        if close is None:
            continue
        after = close + 1
        alt = masked[opener.end():close]
        if masked[after:after + 1] == "(":
            end = pairs.get(after)
            if end is not None and end > after + 1:
                width = close - opener.end()
                match = re.compile(r"!\[([\s\S]{" + str(width)
                                   + r"})\]\(([\s\S]*)\)").match(
                    masked, opener.start(), end + 1,
                )
                return match, "image"
        label = alt
        end = after
        if masked[after:after + 1] == "[" and after in pairs:
            end = pairs[after] + 1
            label = masked[after + 1:end - 1] or alt
        if _ref_label(label) in references:
            width = close - opener.end()
            match = re.compile(r"!\[([\s\S]{" + str(width)
                               + r"})\](?:\[([^\]]*)\])?").match(
                masked, opener.start(), end,
            )
            return match, "image_ref"
    return None


def _protect_code(text: str, masked: str) -> str:
    # Code is literal even inside emphasis/link labels. Hide its punctuation
    # from other recognizers so an internal ** cannot close surrounding bold.
    protected = list(masked)
    code_end = 0
    for opener in re.finditer(r"(?<!`)(`+)(?!`)", masked):
        if opener.start() < code_end:
            continue
        code = _CODE_RE.match(text, opener.start())
        if code:
            protected[code.start():code.end()] = _MASK * (code.end() - code.start())
            code_end = code.end()
    return "".join(protected)


def _expand_link_references(text: str, references: dict) -> str:
    """Resolve full, collapsed and shortcut links outside literal code."""
    if not references:
        return text
    masked = _protect_code(text, _mask_escapes(text))
    # Existing image syntax and inline-link destinations are not reference links.
    protected = list(masked)
    cursor = 0
    while found := _find_image(masked[cursor:], references):
        match, _ = found
        start, end = cursor + match.start(), cursor + match.end()
        protected[start:end] = _MASK * (end - start)
        cursor = end
    cursor = 0
    while match := _find_link(masked[cursor:]):
        start, end = cursor + match.start(), cursor + match.end()
        protected[start:end] = _MASK * (end - start)
        cursor = end
    masked = "".join(protected)
    pattern = re.compile(r"(?<!!)\[([^\[\]]+)\](?:\[([^\]]*)\])?(?!\()")
    pieces = []
    cursor = 0
    for match in pattern.finditer(masked):
        label = match[2] or match[1]
        uri = references.get(_ref_label(label))
        if uri is None:
            continue
        pieces.append(text[cursor:match.start()])
        title = text[match.start(1):match.end(1)]
        destination = "".join("\\" + c if c in "\\()`" else c for c in uri)
        pieces.append(f"[{title}]({destination})")
        cursor = match.end()
    pieces.append(text[cursor:])
    return "".join(pieces)


def _expand_image_references(text: str, references: dict) -> str:
    """Make table-cell images self-contained for the standalone inline parser."""
    if not references:
        return text
    masked = _protect_code(text, _mask_escapes(text))
    # A URL may itself contain image-looking text. Only labels are Markdown.
    protected = list(masked)
    cursor = 0
    while link := _find_link(masked[cursor:]):
        start, end = cursor + link.start(2), cursor + link.end(2)
        protected[start:end] = _MASK * (end - start)
        cursor += link.end()
    masked = "".join(protected)
    parts = []
    cursor = 0
    while found := _find_image(masked[cursor:], references):
        match, kind = found
        start, end = cursor + match.start(), cursor + match.end()
        parts.append(text[cursor:start])
        if kind == "image_ref":
            alt = text[cursor + match.start(1):cursor + match.end(1)]
            label = match.group(2) or _strip_escapes(alt)
            uri = references[_ref_label(label)]
            destination = "".join("\\" + c if c in "\\()" else c for c in uri)
            parts.append(f"![{alt}]({destination})")
        else:
            parts.append(text[start:end])
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def rename_image_references(text: str, renames: dict[str, str]) -> str:
    """Rename ``gdoc-image:ID`` only where it is an inline image destination.

    Fenced code, code spans, escaped syntax, link destinations and prose keep
    the literal token.
    """
    if not renames or "gdoc-image:" not in text:
        return text

    def rename(chunk: str) -> str:
        masked = _protect_code(chunk, _mask_escapes(chunk))
        protected = list(masked)
        cursor = 0
        while link := _find_link(masked[cursor:]):
            start, end = cursor + link.start(2), cursor + link.end(2)
            protected[start:end] = _MASK * (end - start)
            cursor += link.end()
        masked = "".join(protected)
        parts = []
        cursor = 0
        while found := _find_image(masked[cursor:], {}):
            match = found[0]
            start, end = cursor + match.start(2), cursor + match.end(2)
            destination = chunk[start:end]
            target = re.fullmatch(r"(\s*<?gdoc-image:)([A-Za-z0-9_.-]+)(>?\s*)",
                                  destination)
            parts.append(chunk[cursor:start])
            if target and target[2] in renames:
                destination = target[1] + renames[target[2]] + target[3]
            parts.append(destination)
            cursor = end
        parts.append(chunk[cursor:])
        return "".join(parts)

    out = []
    prose = []
    fence = None
    for line in re.findall(r"[^\n]*\n|[^\n]+", text):
        bare = re.sub(r"^(?:[ \t]*>)*[ \t]*", "", line.rstrip("\r\n"))
        if fence is not None:
            out.append(line)
            close = _FENCE_CLOSE_RE.match(bare)
            if close and close[1][0] == fence[0] and len(close[1]) >= len(fence):
                fence = None
            continue
        opener = _fence_open(bare)
        if opener:
            out.append(rename("".join(prose)))
            prose.clear()
            out.append(line)
            fence = opener[1]
            continue
        prose.append(line)
    out.append(rename("".join(prose)))
    return "".join(out)


def _scan(
    text: str, masked: str, references: dict | None = None,
) -> tuple[str, list[StyleRange]]:
    """Recursively parse inline formatting.

    ``text`` is the original source; ``masked`` is the same length with escaped
    markers blanked to a sentinel. The regexes run against ``masked``; emitted
    text is sliced from ``text``. Escaping backslashes are stripped from normal
    content but PRESERVED inside code spans (code is literal — CommonMark).
    Spans recurse so emphasis can nest (e.g. ``**bold _and italic_**``).
    Returns (plain_text, [StyleRange]) with offsets relative to plain_text.
    """
    references = references or {}
    protected = _protect_code(text, masked)
    plain_parts: list[str] = []
    styles: list[StyleRange] = []
    offset = 0
    pos = 0
    n = len(masked)

    while pos < n:
        # Search the unconsumed tail (a fresh slice), not masked[pos:] via the
        # pos argument: a lookbehind (`(?<!\*)`) would otherwise read the
        # just-consumed marker before `pos` and wrongly block a span that abuts
        # it (e.g. the `*b*` in `**a***b*`). Match offsets are relative to the
        # slice, so shift them by `pos`.
        tail = protected[pos:]
        best: tuple[re.Match, str] | None = _find_image(tail, references)
        for pat, kind in _INLINE_PATTERNS:
            if kind == "code":
                m = None
                raw_tail = text[pos:]
                for opener in re.finditer(r"(?<!`)(`+)(?!`)", masked[pos:]):
                    m = pat.match(raw_tail, opener.start())
                    if m is not None:
                        break
            elif kind == "link":
                m = _find_link(tail)
            else:
                m = pat.search(tail)
            if m is not None and (best is None or m.start() < best[0].start()):
                best = (m, kind)
        if best is None:
            plain_parts.append(_strip_escapes(text[pos:]))
            break

        m, kind = best
        m_start = pos + m.start()
        if m_start > pos:
            lit = _strip_escapes(text[pos:m_start])
            plain_parts.append(lit)
            offset += len(lit)

        def _grp(group: int) -> tuple[int, int]:
            return pos + m.start(group), pos + m.end(group)

        seg_start = offset
        if kind == "html_image":
            from gdoc.util import GdocError

            raise GdocError("Use Markdown image syntax instead of HTML img tags",
                            exit_code=3)
        if kind == "separator":
            pass
        elif kind == "entity":
            literal = html.unescape(m[0])
            plain_parts.append(literal)
            offset += len(literal)
        elif kind == "code":
            # Code spans are literal (backslashes kept), normalised per
            # CommonMark 6.1: line endings become spaces, and one leading
            # plus one trailing space is dropped when both are present and
            # the content is not all spaces.
            a, b = _grp(2)
            inner = text[a:b].replace("\n", " ")
            if len(inner) >= 2 and inner[0] == inner[-1] == " " \
                    and inner.strip(" "):
                inner = inner[1:-1]
            plain_parts.append(inner)
            offset += len(inner)
            styles.append(StyleRange(seg_start, offset, _CODE_FONT, "text_style"))
        elif kind in ("image", "image_ref"):
            a, b = _grp(1)
            alt = _strip_escapes(text[a:b])
            if kind == "image":
                ua, ub = _grp(2)
                uri = _strip_escapes(text[ua:ub])
                if uri.startswith("<") and uri.endswith(">"):
                    uri = uri[1:-1]
            else:
                label = m.group(2) or alt
                uri = references[_ref_label(label)]
            plain_parts.append(" ")
            offset += 1
            styles.append(StyleRange(
                seg_start, offset, {"uri": uri, "alt": alt}, "image",
            ))
        elif kind == "link":
            a, b = _grp(1)
            sub_plain, sub_styles = _scan(text[a:b], masked[a:b], references)
            plain_parts.append(sub_plain)
            offset += len(sub_plain)
            for s in sub_styles:
                styles.append(StyleRange(
                    s.start + seg_start, s.end + seg_start, s.style, s.type,
                ))
            ua, ub = _grp(2)
            url = _strip_escapes(text[ua:ub])
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]  # CommonMark's bracketed destination, as for images
            styles.append(StyleRange(
                seg_start, offset, {"link": {"url": url}}, "text_style",
            ))
        else:
            # bold / italic alternations capture group 1 or 2; others, group 1.
            g = 2 if (kind in ("bold", "italic") and m.group(1) is None) else 1
            a, b = _grp(g)
            sub_plain, sub_styles = _scan(text[a:b], masked[a:b], references)
            plain_parts.append(sub_plain)
            offset += len(sub_plain)
            for s in sub_styles:
                styles.append(StyleRange(
                    s.start + seg_start, s.end + seg_start, s.style, s.type,
                ))
            for sd in _STYLES_FOR_KIND[kind]:
                styles.append(StyleRange(seg_start, offset, sd, "text_style"))

        pos = pos + m.end()

    return "".join(plain_parts), styles


def _list_level(indent: str) -> int:
    """Nesting level from a list item's leading whitespace.

    Two columns (or one tab) per level; capped at 8 (Docs' max).
    """
    columns = len(indent.replace("\t", "  "))
    return min(columns // 2, 8)


def _ref_label(label: str) -> str:
    return " ".join(label.split()).casefold()



def _unquote(line: str, limit: int | None = None) -> tuple[str, int]:
    depth = 0
    while limit is None or depth < limit:
        match = _BLOCKQUOTE_RE.match(line)
        if not match:
            break
        line = match[1]
        depth += 1
    return line, depth


def parse_markdown(text: str) -> ParsedMarkdown:
    """Parse markdown text into plain text + style annotations.

    Handles: headings (H1-H6), bullet/numbered lists (nested), bold, italic,
    bold+italic, strikethrough, inline code, links, blockquotes, horizontal
    rules, fenced code blocks, and tables. The exporter also uses explicit
    ``<!-- gdoc:TITLE -->`` / ``<!-- gdoc:SUBTITLE -->`` paragraph prefixes.
    """
    if not text:
        return ParsedMarkdown(plain_text="")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # A terminal LF closes the last paragraph; it is not an extra blank one.
    # Preserve additional LFs, each of which represents a real empty paragraph.
    lines = text.removesuffix("\n").split("\n")
    references = {}
    definition_lines = set()
    fence = None
    for line_number, line in enumerate(lines):
        line, _ = _unquote(line)
        line = line.lstrip(" ")
        if fence is not None:
            closer = _FENCE_CLOSE_RE.match(line)
            if closer and closer[1][0] == fence[0] and len(closer[1]) >= len(fence):
                fence = None
            continue
        opener = _fence_open(line)
        if opener:
            fence = opener[1]
            continue
        # Escaped brackets cannot delimit a definition's label.
        masked = re.fullmatch(r" {0,3}\[([^\]]+)\]:[ \t]*(\S+)[ \t]*",
                              _mask_escapes(line))
        definition = masked and (line[masked.start(1):masked.end(1)],
                                 line[masked.start(2):masked.end(2)])
        if definition and (re.match(r"<?[a-zA-Z][a-zA-Z0-9+.-]*:", definition[1])
                           or re.search(r"!\[[^\]]*\]\[" + re.escape(definition[0])
                                        + r"\]", text)):
            uri = _strip_escapes(definition[1])
            references[_ref_label(definition[0])] = (
                uri.removeprefix("<").removesuffix(">")
            )
            definition_lines.add(line_number)
    plain_parts: list[str] = []
    all_styles: list[StyleRange] = []
    all_tables: list[TableData] = []
    images: list[ImageData] = []
    code_blocks: list[CodeBlockData] = []
    offset = 0
    removed_tabs = 0  # running count of leading list-indent tabs (see below)
    list_levels: dict[int, tuple[str, int]] = {}
    list_block = 0
    last_list_end = 0
    groups: dict[tuple[int, str], tuple[int, int]] = {}
    next_group = 0
    quote_depth = 0
    code_indent = 0
    # A quote inside a list item: its lines, with the item indent removed,
    # parse as a quote whose container records that indent.
    contained_outer = 0
    contained_end = None
    contained_saved = None
    non_default_list_starts: list[str] = []

    def emit_paragraph(
        content: str,
        content_styles: list[StyleRange],
        para_style: dict,
        bullet_preset: str | None = None,
        leading_tabs: int = 0,
        start_number: int = 1,
    ) -> None:
        """Append one paragraph (content + newline) and its style ranges.

        ``leading_tabs`` prepends tabs for list nesting; createParagraphBullets
        counts and removes them at apply time (tracked via ``removed_tabs``).
        """
        nonlocal offset, removed_tabs, list_block, last_list_end, next_group
        group = None
        if bullet_preset is not None:
            # A parent's next item starts a new child sequence. At the same
            # depth, ordered items may continue across bullets or prose.
            for key in list(groups):
                if key[0] > leading_tabs:
                    del groups[key]
            if bullet_preset.startswith("NUMBERED"):
                for key in list(groups):
                    if key[0] == leading_tabs and not key[1].startswith("NUMBERED"):
                        del groups[key]
            key = (leading_tabs, bullet_preset)
            previous = groups.get(key)
            ordered = bullet_preset.startswith("NUMBERED")
            continuation = previous and (not ordered or start_number == previous[1] + 1)
            if not continuation:
                next_group += 1
                group = next_group
                if ordered and start_number != 1:
                    non_default_list_starts.append(
                        f"numbered list at line {i + 1} ({content!r}) "
                        f"starts at {start_number} (reset to 1)"
                    )
            else:
                group = previous[0]
            groups[key] = (group, start_number)
        if bullet_preset is None:
            # Blank paragraphs may separate items of the same numbered list.
            if content and not contained_outer:
                list_levels.clear()
        else:
            previous = list_levels.get(leading_tabs)
            ordered = bullet_preset.startswith("NUMBERED")
            across_blank = last_list_end != offset
            restart = leading_tabs == 0 and previous and ordered and start_number == 1
            continuation = ordered and previous == (bullet_preset, start_number - 1)
            if restart or (leading_tabs == 0 and across_blank and not continuation):
                list_levels.clear()
            if not list_levels:
                list_block += 1
            for level in list(list_levels):
                if level > leading_tabs:
                    del list_levels[level]
            previous = list_levels.get(leading_tabs)
            number = previous[1] + 1 if previous and previous[0] == bullet_preset else 1
            list_levels[leading_tabs] = (bullet_preset, number)
        para_start = offset
        if quote_depth or code_indent:
            para_style = dict(para_style)
            level = quote_depth + bool(code_indent or contained_outer)
            indent = {"magnitude": 36 * level, "unit": "PT"}
            para_style.update(indentStart=indent, indentFirstLine=indent)
        if leading_tabs:
            plain_parts.append("\t" * leading_tabs)
            offset += leading_tabs
            removed_tabs += leading_tabs
        text_start = offset
        plain_parts.append(content)
        offset += len(content)
        for s in content_styles:
            if s.type == "image":
                images.append(ImageData(
                    s.start + text_start, s.style["uri"], s.style["alt"],
                    removed_tabs,
                ))
                continue
            all_styles.append(StyleRange(
                s.start + text_start, s.end + text_start, s.style, s.type,
            ))
        plain_parts.append("\n")
        offset += 1
        all_styles.append(StyleRange(
            para_start, offset, para_style, "paragraph_style",
        ))
        if quote_depth or code_indent:
            prefix = {"quote": quote_depth, "indent": code_indent}
            if contained_outer:
                prefix["outer"] = contained_outer
            all_styles.append(StyleRange(
                para_start, offset, prefix, "markdown_prefix",
            ))
        if bullet_preset is not None:
            all_styles.append(StyleRange(
                para_start, offset,
                {"bulletPreset": bullet_preset}, "bullets",
                list_block=list_block, list_depth=leading_tabs, list_group=group,
                literal_tabs=len(content) - len(content.lstrip("\t")),
            ))
            last_list_end = offset

    i = 0
    table_separators: set[int] = set()
    while i < len(lines):
        if contained_end is not None and i >= contained_end:
            list_levels.clear()
            list_levels.update(contained_saved[0])
            groups.clear()
            groups.update(contained_saved[1])
            contained_outer, contained_end = 0, None
        if contained_end is None and list_levels:
            stripped = lines[i].lstrip(" ")
            outer = len(lines[i]) - len(stripped)
            if outer and stripped.startswith(">"):
                end = i
                while (end < len(lines) and lines[end][:outer] == " " * outer
                       and lines[end][outer:].startswith(">")):
                    lines[end] = lines[end][outer:]
                    end += 1
                # The quote's own lists are separate; the item's list resumes
                # after it.
                contained_saved = (dict(list_levels), dict(groups))
                list_levels.clear()
                groups.clear()
                contained_outer, contained_end = outer, end
        if i in definition_lines or i in table_separators:
            i += 1
            continue
        line, quote_depth = _unquote(lines[i])

        # Fenced code block: ``` (or ~~~) ... ```
        fence_indent = len(line) - len(line.lstrip(" "))
        in_list_code = bool(list_levels) and fence_indent > 0
        fence_m = _fence_open(line.lstrip(" ") if in_list_code else line)
        if fence_m:
            saved_levels = dict(list_levels) if in_list_code else {}
            if not in_list_code:
                list_levels.clear()
            code_indent = fence_indent if in_list_code else 0
            fence = fence_m.group(1)
            fence_char = fence[0]
            code_start = offset
            i += 1
            while i < len(lines):
                code_line, _ = _unquote(lines[i], quote_depth)
                # Fence indentation belongs to the container, not the code.
                strip = min(fence_indent, len(code_line) - len(code_line.lstrip(" ")))
                code_line = code_line[strip:]
                close = _FENCE_CLOSE_RE.match(code_line)
                if close:
                    close_fence = close.group(1)
                    if close_fence[0] == fence_char and len(
                        close_fence
                    ) >= len(fence):
                        i += 1
                        break
                styles = (
                    [StyleRange(0, len(code_line), _CODE_FONT, "text_style")]
                    if code_line else []
                )
                emit_paragraph(
                    code_line, styles, {"namedStyleType": "NORMAL_TEXT"},
                )
                i += 1
            if offset == code_start:
                emit_paragraph("", [], {"namedStyleType": "NORMAL_TEXT"})
            code_blocks.append(CodeBlockData(code_start, offset))
            list_levels.update(saved_levels)
            code_indent = 0
            continue

        # Table: header row + separator row + data rows. Tables may sit inside
        # quotes and, indented, inside list items; the container is recorded.
        table_quote = quote_depth
        table_indent = len(line) - len(line.lstrip(" "))
        in_list_table = bool(list_levels) and table_indent > 0

        def table_line(j, quote=table_quote, indent=table_indent,
                       in_list=in_list_table):
            if j >= len(lines):
                return ""
            text, depth = _unquote(lines[j], quote)
            if depth != quote:
                return ""
            if in_list:
                if len(text) - len(text.lstrip(" ")) < indent:
                    return ""
                text = text[indent:]
            return text

        header_line = table_line(i)
        if (
            _TABLE_ROW_RE.match(header_line)
            and _TABLE_SEP_RE.match(table_line(i + 1))
        ):
            table_rows: list[list[str]] = []
            saved_levels = dict(list_levels) if in_list_table else {}
            list_levels.clear()
            header_cells = _table_cells(header_line)
            table_rows.append(header_cells)
            num_cols = len(header_cells)
            alignments = []
            for separator in _table_cells(table_line(i + 1)):
                if separator.startswith(":") and separator.endswith(":"):
                    alignments.append("CENTER")
                elif separator.startswith(":"):
                    alignments.append("START")
                elif separator.endswith(":"):
                    alignments.append("END")
                else:
                    alignments.append(None)
            alignments = (alignments + [None] * num_cols)[:num_cols]
            i += 2  # skip header + separator
            # Only the line after the header is a separator, so a data row of
            # dashes stays a row, as in GFM.
            while i < len(lines) and _TABLE_ROW_RE.match(table_line(i)):
                cells = _table_cells(table_line(i))
                if len(cells) < num_cols:
                    cells.extend([""] * (num_cols - len(cells)))
                elif len(cells) > num_cols:
                    cells = cells[:num_cols]
                table_rows.append(cells)
                i += 1

            table_rows = [[_expand_link_references(
                _expand_image_references(cell, references), references) for cell in row]
                          for row in table_rows]
            para_start = offset
            all_tables.append(TableData(
                rows=table_rows,
                num_rows=len(table_rows),
                num_cols=num_cols,
                plain_text_offset=offset,
                removed_tabs_before=removed_tabs,
                alignments=alignments,
                prefix=(table_quote, table_indent if in_list_table else 0),
                outer=contained_outer,
            ))
            list_levels.update(saved_levels)
            # Canonical adjacent tables: the last blank line before a following
            # table in the same container separates them; earlier blank or
            # whitespace-only lines are paragraphs.
            j = i
            while j < len(lines):
                text, depth = _unquote(lines[j], table_quote)
                if depth != table_quote or text.strip():
                    break
                j += 1
            if (j > i and _TABLE_ROW_RE.match(table_line(j))
                    and _TABLE_SEP_RE.match(table_line(j + 1))):
                table_separators.add(j - 1)
            plain_parts.append("\n")
            offset += 1
            all_styles.append(StyleRange(
                start=para_start, end=offset,
                style={"namedStyleType": "NORMAL_TEXT"},
                type="paragraph_style",
            ))
            continue

        named_m = _NAMED_STYLE_RE.match(line)
        if named_m:
            inline_text, inline_styles = _parse_inline(
                named_m.group(2) or "", references,
            )
            emit_paragraph(
                inline_text, inline_styles, {"namedStyleType": named_m.group(1)},
            )
            i += 1
            continue

        # Heading
        heading_m = _HEADING_RE.match(line)
        if heading_m:
            level = len(heading_m.group(1))
            inline_text, inline_styles = _parse_inline(
                heading_m.group(2) or "", references,
            )
            emit_paragraph(
                inline_text, inline_styles,
                {"namedStyleType": f"HEADING_{level}"},
            )
            i += 1
            continue

        # Horizontal rule (--- / *** / ___) — an empty paragraph with a
        # bottom border (the Docs API has no direct horizontal-rule insert).
        if _HR_RE.match(line):
            emit_paragraph("", [], {
                "namedStyleType": "NORMAL_TEXT",
                "borderBottom": {
                    "color": {"color": {"rgbColor": {
                        "red": 0.5, "green": 0.5, "blue": 0.5,
                    }}},
                    "width": {"magnitude": 1, "unit": "PT"},
                    "padding": {"magnitude": 1, "unit": "PT"},
                    "dashStyle": "SOLID",
                },
            })
            i += 1
            continue

        # Bullet list item (indent-aware)
        bullet_m = _BULLET_RE.match(line)
        if bullet_m:
            item = bullet_m.group(2) or ""
            heading = _HEADING_RE.match(item)
            named = _NAMED_STYLE_RE.match(item)
            item_style = "NORMAL_TEXT"
            if heading:
                item_style = f"HEADING_{len(heading.group(1))}"
                item = heading.group(2) or ""
            elif named:
                item_style = named.group(1)
                item = named.group(2) or ""
            inline_text, inline_styles = _parse_inline(item, references)
            emit_paragraph(
                inline_text, inline_styles,
                {"namedStyleType": item_style},
                bullet_preset="BULLET_DISC_CIRCLE_SQUARE",
                leading_tabs=_list_level(bullet_m.group(1)),
            )
            i += 1
            continue

        # Numbered list item (indent-aware)
        numbered_m = _NUMBERED_RE.match(line)
        if numbered_m:
            item = numbered_m.group(2) or ""
            heading = _HEADING_RE.match(item)
            named = _NAMED_STYLE_RE.match(item)
            item_style = "NORMAL_TEXT"
            if heading:
                item_style = f"HEADING_{len(heading.group(1))}"
                item = heading.group(2) or ""
            elif named:
                item_style = named.group(1)
                item = named.group(2) or ""
            inline_text, inline_styles = _parse_inline(item, references)
            emit_paragraph(
                inline_text, inline_styles,
                {"namedStyleType": item_style},
                bullet_preset="NUMBERED_DECIMAL_ALPHA_ROMAN",
                leading_tabs=_list_level(numbered_m.group(1)),
                start_number=int(line.lstrip().split(".", 1)[0]),
            )
            i += 1
            continue

        # Normal paragraph line. Explicit NORMAL_TEXT so inserted paragraphs
        # don't inherit the style of the paragraph at the insertion point.
        inline_text, inline_styles = _parse_inline(line, references)
        emit_paragraph(
            inline_text, inline_styles, {"namedStyleType": "NORMAL_TEXT"},
        )
        i += 1

    return ParsedMarkdown(
        plain_text="".join(plain_parts),
        styles=all_styles,
        tables=all_tables,
        removed_tabs=removed_tabs,
        non_default_list_starts=non_default_list_starts,
        code_blocks=code_blocks,
        images=images,
    )


def to_docs_requests(
    parsed: ParsedMarkdown,
    insert_index: int,
    tab_id: str | None = None,
    *, include_lists: bool = True,
) -> list[dict]:
    """Convert ParsedMarkdown into Docs API batchUpdate request dicts.

    Args:
        parsed: The parsed markdown result.
        insert_index: The document index at which to insert text.
        tab_id: Optional tab ID for targeting a specific tab.

    Returns:
        List of request dicts for batchUpdate.
    """
    if not parsed.plain_text:
        return []

    requests: list[dict] = []

    # Style ranges are Python code-point offsets into plain_text; Docs API
    # indexes are UTF-16 code units, so an emoji (non-BMP) earlier in the
    # replacement shifts every later range by one extra unit.
    utf16 = _utf16_prefix(parsed.plain_text)

    def _location(index: int) -> dict:
        loc = {"index": index}
        if tab_id:
            loc["tabId"] = tab_id
        return loc

    def _range(start: int, end: int) -> dict:
        r = {"startIndex": start, "endIndex": end}
        if tab_id:
            r["tabId"] = tab_id
        return r

    # 1. Insert the plain text.
    requests.append({
        "insertText": {
            "location": _location(insert_index),
            "text": _list_insert_text(parsed),
        }
    })

    # 2. Paragraph styles (named styles, indents, borders). Applied before text
    #    styles because a `namedStyleType` re-resolves a run's direct character
    #    formatting and would clear bold/italic set afterwards.
    for sr in parsed.styles:
        if sr.type == "paragraph_style" and sr.end > sr.start:
            requests.append({
                "updateParagraphStyle": {
                    "range": _range(
                        utf16[sr.start] + insert_index,
                        utf16[sr.end] + insert_index,
                    ),
                    "paragraphStyle": sr.style,
                    "fields": _paragraph_style_fields(sr.style),
                }
            })

    # 3. Text styles (bold, italic, strikethrough, code, link). After paragraph
    #    styles so they are not clobbered; before bullets so they are already
    #    attached to their runs when bullet creation removes leading tabs.
    for sr in parsed.styles:
        if sr.type == "text_style":
            requests.append({
                "updateTextStyle": {
                    "range": _range(
                        utf16[sr.start] + insert_index,
                        utf16[sr.end] + insert_index,
                    ),
                    "textStyle": sr.style,
                    "fields": _text_style_fields(sr.style),
                }
            })

    if include_lists:
        requests.extend(list_requests(parsed, insert_index, tab_id))
        requests.extend(prefix_indent_requests(parsed, insert_index, tab_id))

    return requests


def prefix_indent_requests(parsed, insert_index, tab_id):
    """Restore container indentation after native bullet creation changes it."""
    requests = []
    bullets = [s for s in parsed.styles if s.type == "bullets"]
    for prefix in (s for s in parsed.styles if s.type == "markdown_prefix"):
        bullet = next((b for b in bullets if b.start == prefix.start), None)
        level = prefix.style["quote"] + bool(prefix.style.get("outer")) + (
            bullet.list_depth + 1 if bullet else bool(prefix.style["indent"]))
        removed_before = sum(b.list_depth for b in bullets if b.start < prefix.start)
        removed_end = sum(b.list_depth for b in bullets if b.start < prefix.end)
        start = (insert_index + utf16_len(parsed.plain_text[:prefix.start])
                 - removed_before)
        end = insert_index + utf16_len(parsed.plain_text[:prefix.end]) - removed_end
        span = {"startIndex": start, "endIndex": max(start + 1, end)}
        if tab_id:
            span["tabId"] = tab_id
        requests.append({"updateParagraphStyle": {
            "range": span,
            "paragraphStyle": {
                "indentStart": {"magnitude": 36 * level, "unit": "PT"},
                "indentFirstLine": {"magnitude": 36 * level - (18 if bullet else 0),
                                    "unit": "PT"},
            },
            "fields": "indentStart,indentFirstLine",
        }})
    return requests


def _list_insert_text(parsed: ParsedMarkdown) -> str:
    """Shield content tabs from the API's destructive nesting-tab scan."""
    text = list(parsed.plain_text)
    for item in parsed.styles:
        if item.type == "bullets" and item.literal_tabs:
            start = item.start + item.list_depth
            text[start:start + item.literal_tabs] = " " * item.literal_tabs
    for start, tabs in _unlisted_leading_tabs(parsed):
        text[start:start + tabs] = " " * tabs
    return "".join(text)


def _unlisted_leading_tabs(parsed: ParsedMarkdown) -> list[tuple[int, int]]:
    """Leading tabs of paragraphs that are not list items, such as code lines.

    A bullet request spanning a list-contained code block or continuation
    paragraph would consume those tabs as nesting, so they are inserted as
    spaces and restored after every bullet request.
    """
    if not any(s.type == "bullets" for s in parsed.styles):
        return []
    items = {s.start for s in parsed.styles if s.type == "bullets"}
    found = []
    for style in parsed.styles:
        if style.type != "paragraph_style" or style.start in items:
            continue
        line = parsed.plain_text[style.start:style.end]
        tabs = len(line) - len(line.lstrip("\t"))
        if tabs:
            found.append((style.start, tabs))
    return found


def _restore_unlisted_tabs(parsed: ParsedMarkdown, insert_index: int,
                           tab_id: str | None) -> list[dict]:
    items = [s for s in parsed.styles if s.type == "bullets"]
    offsets = _utf16_prefix(parsed.plain_text)
    requests = []
    for point, tabs in reversed(_unlisted_leading_tabs(parsed)):
        # Nesting tabs of earlier items were consumed by the bullet requests.
        start = insert_index + offsets[point] - sum(
            item.list_depth for item in items if item.start < point)
        span = {"startIndex": start, "endIndex": start + tabs}
        location = {"index": start + tabs}
        if tab_id:
            span["tabId"] = location["tabId"] = tab_id
        # Inserted after the placeholder spaces, the tabs take their style.
        requests.extend([
            {"insertText": {"location": location, "text": "\t" * tabs}},
            {"deleteContentRange": {"range": span}},
        ])
    return requests


def list_requests(parsed: ParsedMarkdown, insert_index: int,
                  tab_id: str | None = None) -> list[dict]:
    """Bullet requests, then the shielded tabs of non-item paragraphs."""
    return (_list_bullet_requests(parsed, insert_index, tab_id)
            + _restore_unlisted_tabs(parsed, insert_index, tab_id))


def _list_bullet_requests(parsed: ParsedMarkdown, insert_index: int,
                          tab_id: str | None = None) -> list[dict]:
    """Use isolated groups for nested restarts and interleaved continuation."""
    items = [s for s in parsed.styles if s.type == "bullets"]
    active = {}
    previous = {}
    for item in items:
        for depth in list(active):
            if depth > item.list_depth:
                del active[depth]
        if item.style["bulletPreset"].startswith("NUMBERED"):
            prior = active.get(item.list_depth)
            if item.list_depth and prior and prior != item.list_group:
                return _separated_list_requests(parsed, insert_index, tab_id)
            active[item.list_depth] = item.list_group
            earlier = previous.get(item.list_group)
            if earlier is not None:
                between = [s for s in parsed.styles
                           if earlier.end <= s.start < item.start]
                interleaved = any(s.type == "bullets" and
                                  s.list_depth <= item.list_depth for s in between)
                # A table or image between items interrupts the list like prose.
                objects = {t.plain_text_offset for t in parsed.tables} | {
                    image.plain_text_offset for image in parsed.images} | {
                    s.start for s in parsed.styles if s.type == "image"}
                prose = any(
                    s.type == "paragraph_style"
                    and (parsed.plain_text[s.start:s.end].strip()
                         or any(s.start <= o < s.end for o in objects))
                    and not any(b.start == s.start for b in items)
                    for s in between
                )
                if interleaved or prose:
                    return _separated_list_requests(parsed, insert_index, tab_id)
            previous[item.list_group] = item
    return _simple_list_requests(parsed, insert_index, tab_id)


def _simple_list_requests(parsed: ParsedMarkdown, insert_index: int,
                  tab_id: str | None = None) -> list[dict]:
    """Create independent lists backwards; span blanks for explicit continuation.

    createParagraphBullets joins a matching preceding list. Later blocks must
    therefore exist before earlier blocks acquire their bullets. Content tabs
    were inserted as spaces and are restored only after all bullet operations
    on their block, so only nesting tabs are consumed.
    """
    items = sorted((s for s in parsed.styles if s.type == "bullets"),
                   key=lambda s: s.start)
    blocks = []
    for item in items:
        if blocks and (
            item.list_block is not None
            and blocks[-1][-1].list_block == item.list_block
            or item.list_block is None and blocks[-1][-1].end == item.start
        ):
            blocks[-1].append(item)
        else:
            blocks.append([item])
    requests = []
    offsets = _utf16_prefix(parsed.plain_text)

    def span(start, end):
        target = {"startIndex": start, "endIndex": max(start + 1, end)}
        if tab_id:
            target["tabId"] = tab_id
        return target

    def location(index):
        target = {"index": index}
        if tab_id:
            target["tabId"] = tab_id
        return target

    for block in reversed(blocks):
        first, last = block[0], block[-1]
        root_preset = first.style["bulletPreset"]
        # A stripped final empty item still owns the retained paragraph mark.
        block_end = insert_index + offsets[last.end] + (last.start == last.end)
        requests.append({"createParagraphBullets": {
            "range": span(insert_index + offsets[first.start], block_end),
            "bulletPreset": root_preset,
        }})
        removed = 0
        previous_end = None
        restorations = []
        mixed = len({item.style["bulletPreset"] for item in block}) > 1
        if mixed:
            requests.extend(_mixed_block_requests(
                block, root_preset, insert_index, offsets, span, location,
            ))
            continue
        for item in block:
            depth = item.list_depth
            start = insert_index + offsets[item.start] - removed
            if previous_end is not None and previous_end < start:
                # These blank paragraphs linked the numbered items while the
                # bullet request ran; removing their bullets retains identity.
                requests.append({"deleteParagraphBullets": {
                    "range": span(previous_end, start),
                }})
            removed += depth
            end = max(start + 1, insert_index + offsets[item.end] - removed)
            target = span(start, end)
            previous_end = end
            if item.style["bulletPreset"] != root_preset:
                requests.append({"deleteParagraphBullets": {"range": target}})
                if depth:
                    requests.append({"insertText": {
                        "location": location(start), "text": "\t" * depth,
                    }})
                requests.append({"createParagraphBullets": {
                    "range": span(start, end + depth),
                    "bulletPreset": item.style["bulletPreset"],
                }})
            if mixed:
                requests.append({"updateParagraphStyle": {
                    "range": target,
                    "paragraphStyle": {
                        "indentStart": {"magnitude": 36 * (depth + 1), "unit": "PT"},
                        "indentFirstLine": {
                            "magnitude": 36 * (depth + 1) - 18, "unit": "PT",
                        },
                    },
                    "fields": "indentStart,indentFirstLine",
                }})
            if item.literal_tabs:
                restorations.extend([
                    # Inserted after its placeholder spaces, the tab takes their
                    # parsed style rather than the following text's.
                    {"insertText": {"location": location(start + item.literal_tabs),
                                    "text": "\t" * item.literal_tabs}},
                    {"deleteContentRange": {
                        "range": span(start, start + item.literal_tabs),
                    }},
                ])
        requests.extend(restorations)
    return requests


def _mixed_block_requests(block, root_preset, insert_index, offsets, span, location):
    """Give each nested list of a mixed block its own preset and identity.

    The block already carries the root preset. A nested list (one
    ``list_group``) whose preset differs from its enclosing list is recreated
    over its whole extent at once, including blank paragraphs between its
    items, so loose items keep one numbering. Blank paragraphs lose their
    bullets only afterwards, which retains every list's identity.
    """
    positions = []
    removed = 0
    for item in block:
        start = insert_index + offsets[item.start] - removed
        removed += item.list_depth
        end = max(start + 1, insert_index + offsets[item.end] - removed)
        positions.append((item, start, end))
    groups: dict = {}
    for item, start, end in positions:
        groups.setdefault(item.list_group, []).append((item, start, end))
    requests = []
    created = []  # (start, end, preset) of recreated extents, outermost first
    for members in sorted(groups.values(), key=lambda m: m[0][1]):
        preset = members[0][0].style["bulletPreset"]
        low, high = members[0][1], members[-1][2]
        enclosing = next((p for lo, hi, p in reversed(created) if lo <= low < hi),
                         root_preset)
        if preset == enclosing:
            continue
        requests.append({"deleteParagraphBullets": {"range": span(low, high)}})
        inside = [(item, start) for item, start, _ in positions
                  if low <= start < high and item.list_depth]
        for item, start in reversed(inside):
            requests.append({"insertText": {
                "location": location(start), "text": "\t" * item.list_depth,
            }})
        requests.append({"createParagraphBullets": {
            "range": span(low, high + sum(item.list_depth for item, _ in inside)),
            "bulletPreset": preset,
        }})
        created.append((low, high, preset))
    previous_end = None
    for item, start, end in positions:
        depth = item.list_depth
        requests.append({"updateParagraphStyle": {
            "range": span(start, end),
            "paragraphStyle": {
                "indentStart": {"magnitude": 36 * (depth + 1), "unit": "PT"},
                "indentFirstLine": {"magnitude": 36 * (depth + 1) - 18, "unit": "PT"},
            },
            "fields": "indentStart,indentFirstLine",
        }})
        if previous_end is not None and previous_end < start:
            # These blank paragraphs linked the items while the bullet
            # requests ran; removing their bullets retains identity.
            requests.append({"deleteParagraphBullets": {
                "range": span(previous_end, start),
            }})
        previous_end = end
    for item, start, _ in positions:
        if item.literal_tabs:
            requests.extend([
                # Inserted after its placeholder spaces, the tab takes their
                # parsed style rather than the following text's.
                {"insertText": {"location": location(start + item.literal_tabs),
                                "text": "\t" * item.literal_tabs}},
                {"deleteContentRange": {
                    "range": span(start, start + item.literal_tabs),
                }},
            ])
    return requests


def _separated_list_requests(parsed: ParsedMarkdown, insert_index: int,
                  tab_id: str | None = None) -> list[dict]:
    """Compile canonical numbering into independent native list identities.

    Ordered groups span intervening bullets/prose before those paragraphs are
    restored. Each deeper group is then created behind a temporary unbulleted
    paragraph: otherwise Docs can join it to a same-preset parent. All temporary
    edits cancel within the group, so subsequent ranges use stable coordinates.
    """
    items = sorted((s for s in parsed.styles if s.type == "bullets"),
                   key=lambda s: s.start)
    if not items:
        return []
    offsets = _utf16_prefix(parsed.plain_text)
    requests = []

    def span(start, end):
        target = {"startIndex": start, "endIndex": max(start + 1, end)}
        if tab_id:
            target["tabId"] = tab_id
        return target

    def location(index):
        target = {"index": index}
        if tab_id:
            target["tabId"] = tab_id
        return target

    # Remove only parser-supplied indentation; literal tabs remain shielded.
    for item in reversed(items):
        if item.list_depth:
            start = insert_index + offsets[item.start]
            requests.append({"deleteContentRange": {
                "range": span(start, start + item.list_depth),
            }})

    def coordinate(point):
        return insert_index + offsets[point] - sum(
            min(item.list_depth, max(0, point - item.start)) for item in items
        )

    groups = {}
    for item in items:
        key = item.list_group
        if key is None:
            key = (item.list_block, item.list_depth, item.style["bulletPreset"])
        groups.setdefault(key, []).append(item)
    # A list quoted inside a list item is its own list, even between items
    # of an enclosing list with the same preset.
    contained = {id(group[0]) for group in groups.values() if any(
        s.type == "markdown_prefix" and s.style.get("outer") and s.style["quote"]
        and s.start <= group[0].start < s.end for s in parsed.styles)}
    # Numbered continuity takes precedence over intervening unordered items.
    # Independent same-depth restarts are created from bottom to top, and
    # quoted lists after the lists that span them.
    ordered_groups = sorted(groups.values(), key=lambda group: (
        group[0].list_depth,
        id(group[0]) in contained,
        not group[0].style["bulletPreset"].startswith("NUMBERED"),
        -group[0].start,
    ))
    for group in ordered_groups:
        first, last = group[0], group[-1]
        start, end = coordinate(first.start), coordinate(last.end)
        end = max(start + 1, end + (last.start == last.end))
        covered = [item for item in items if first.start <= item.start <= last.start]
        requests.append({"deleteParagraphBullets": {"range": span(start, end)}})
        # This paragraph prevents preceding-list auto-join, even when the
        # preceding parent has the exact same numbered preset.
        separator = int(first.list_depth > 0 or id(first) in contained)
        if separator:
            requests.append({"insertText": {"location": location(start), "text": "\n"}})
            requests.append({"deleteParagraphBullets": {
                "range": span(start, start + 1),
            }})
        tabs = 0
        for item in reversed(covered):
            if item.list_depth:
                requests.append({"insertText": {
                    "location": location(coordinate(item.start) + separator),
                    "text": "\t" * item.list_depth,
                }})
                tabs += item.list_depth
        requests.append({"createParagraphBullets": {
            "range": span(start + separator, end + separator + tabs),
            "bulletPreset": first.style["bulletPreset"],
        }})
        if separator:
            requests.append({"deleteContentRange": {"range": span(start, start + 1)}})

    # Spanning a continuation temporarily bullets intervening prose/blank lines.
    for style in parsed.styles:
        if (style.type == "paragraph_style" and not any(
            item.start == style.start for item in items
        ) and any(group[0].start <= style.start < group[-1].end
                  for group in groups.values())):
            target = span(coordinate(style.start), coordinate(style.end))
            requests.append({"deleteParagraphBullets": {"range": target}})
            # Removing native bullets also alters indentation. Restore the
            # requested non-list paragraph style only where a group spanned it.
            paragraph_style = {
                "indentStart": {"magnitude": 0, "unit": "PT"},
                "indentFirstLine": {"magnitude": 0, "unit": "PT"},
                **style.style,
            }
            requests.append({"updateParagraphStyle": {
                "range": target, "paragraphStyle": paragraph_style,
                "fields": _paragraph_style_fields(paragraph_style),
            }})
    for item in items:
        start, end = coordinate(item.start), coordinate(item.end)
        depth = item.list_depth
        requests.append({"updateParagraphStyle": {
            "range": span(start, end),
            "paragraphStyle": {
                "indentStart": {"magnitude": 36 * (depth + 1), "unit": "PT"},
                "indentFirstLine": {"magnitude": 36 * (depth + 1) - 18, "unit": "PT"},
            },
            "fields": "indentStart,indentFirstLine",
        }})
        if item.literal_tabs:
            requests.extend([
                # Inserted after its placeholder spaces, the tab takes their
                # parsed style rather than the following text's.
                {"insertText": {"location": location(start + item.literal_tabs),
                                "text": "\t" * item.literal_tabs}},
                {"deleteContentRange": {
                    "range": span(start, start + item.literal_tabs),
                }},
            ])
    return requests


def utf16_len(text: str) -> int:
    """Length of *text* in UTF-16 code units (the Docs API index space)."""
    return sum(2 if ord(ch) > 0xFFFF else 1 for ch in text)


def _utf16_prefix(text: str) -> list[int]:
    """offsets[i] = UTF-16 length of text[:i] (len(text) + 1 entries)."""
    offsets = [0]
    total = 0
    for ch in text:
        total += 2 if ord(ch) > 0xFFFF else 1
        offsets.append(total)
    return offsets


def text_style_fields(style: dict) -> str:
    """Public: build the updateTextStyle `fields` mask for a style dict."""
    return _text_style_fields(style)


def _text_style_fields(style: dict) -> str:
    """Build the fields mask string for updateTextStyle."""
    parts = []
    for key in style:
        if key == "bold":
            parts.append("bold")
        elif key == "italic":
            parts.append("italic")
        elif key == "strikethrough":
            parts.append("strikethrough")
        elif key == "weightedFontFamily":
            parts.append("weightedFontFamily")
        elif key == "link":
            parts.append("link")
    return ",".join(parts)


# ParagraphStyle keys this module emits, each a valid Docs API field name.
_PARAGRAPH_STYLE_FIELDS = frozenset({
    "namedStyleType", "indentStart", "indentEnd", "indentFirstLine",
    "borderBottom",
})


def _paragraph_style_fields(style: dict) -> str:
    """Build the fields mask string for updateParagraphStyle.

    Whitelisted (rather than ``",".join(style.keys())``) so an unexpected key
    can't produce a malformed field mask — mirrors ``_text_style_fields``.
    """
    return ",".join(k for k in style if k in _PARAGRAPH_STYLE_FIELDS)
