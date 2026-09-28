"""One richly formatted offline document for targeted edits and rewrites.

The document has direct fonts and colours on every run, a heading with a
hand-set size, a numbered list starting at 5, a table, an inline image, a
collaborator's pending suggestion, anchored comments and a sibling tab.

Targeted commands (`edit`, `insert`, `edit --cell`, `insert-image`,
`replace-image`, `suggest`) must leave everything they do not target natively
identical, through CLI and MCP. Changed rewrites report what they lose and
obey the rewrite policy; CLI and MCP give identical warnings and refusals.
"""

import copy
import json

import pytest

from gdoc import state
from gdoc.api import docs
from gdoc.frontmatter import parse_frontmatter
from tests.acceptance.test_round5_workflows import NativeRoute
from tests.native_model import NativeDoc, NativeService, Unit

NUMBERED = "NUMBERED_DECIMAL_ALPHA_ROMAN"
STYLE = {
    "weightedFontFamily": {"fontFamily": "Georgia", "weight": 400},
    "foregroundColor": {"color": {"rgbColor": {"blue": 0.5}}},
}
HEADING_STYLE = {**STYLE, "fontSize": {"magnitude": 28, "unit": "PT"}}
IMAGE = "https://example.org/map.png"
COMMENTS = [
    {"id": "c1", "anchor": "kix.a1", "resolved": False,
     "quotedFileContent": {"value": "approves the budget"}},
    {"id": "c2", "anchor": "kix.a2", "resolved": True,
     "quotedFileContent": {"value": "Sixth step"}},
    # Not anchored: gdoc's quote-only fallback is not detached by a rewrite.
    {"id": "c3", "resolved": False, "quotedFileContent": {"value": "Owner"}},
]
SIBLING = {
    "tabProperties": {"tabId": "t.appendix", "title": "Appendix", "index": 1},
    "documentTab": {"body": {"content": [
        {"startIndex": 0, "endIndex": 1, "sectionBreak": {}},
        {"startIndex": 1, "endIndex": 10, "paragraph": {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "elements": [{"startIndex": 1, "endIndex": 10, "textRun": {
                "content": "Appendix\n", "textStyle": STYLE}}]}},
    ]}},
}


def rich_document():
    """Build the standard rich document; returns (doc, image object ID)."""
    doc = NativeDoc(
        ("p", "Harbor brief", "HEADING_1"),
        ("p", "The committee approves the budget."),
        ("p", "Map: shown here."),
        ("p", "Fifth step", "NORMAL_TEXT", {"preset": NUMBERED, "list": 1, "nest": 0}),
        ("p", "Sixth step", "NORMAL_TEXT", {"preset": NUMBERED, "list": 1, "nest": 0}),
        ("t", [["Owner", "Ana"], ["Status", "draft"]]),
        ("p", "Closing remark. Pending note."),
    )
    doc.list_starts[1] = 5
    heading = True
    for unit in doc.units:
        if unit.kind == "text":
            unit.ts = dict(HEADING_STYLE if heading else STYLE)
            heading = heading and unit.ch != "\n"
    def find(needle):
        # One character per unit, so string and unit indexes agree.
        return "".join(u.ch[:1] or "\0" for u in doc.units).index(needle)

    image_at = find("Map: ") + len("Map: ")
    doc.units.insert(image_at, Unit(f"[IMG:{IMAGE}]", STYLE))
    doc.images = 1
    pending = find("Pending note.")
    for unit in doc.units[pending:pending + len("Pending note.")]:
        unit.sg = ("suggestedInsertionIds", "suggest.collaborator")
    return doc, f"obj{image_at}"


class Rich:
    """The rich document behind one interface, with isolated state."""

    def __init__(self, interface, monkeypatch, tmp_path, comments=COMMENTS):
        monkeypatch.setattr(state, "STATE_DIR", tmp_path / interface / "state")
        self.route = NativeRoute(interface, monkeypatch, tmp_path / interface)
        (tmp_path / interface).mkdir(exist_ok=True)
        self.doc, self.image = rich_document()
        self.route.service = NativeService(self.doc, extra_tabs=[SIBLING])
        monkeypatch.setattr("gdoc.api.comments.list_comments",
                            lambda *a, **k: copy.deepcopy(comments))
        monkeypatch.setattr(docs, "check_suggest_preview_access", lambda *a: None)
        monkeypatch.setattr(docs, "_token_identity", lambda *a: ("client", "token"))

    def call(self, command, **arguments):
        return self.route.call(command, **arguments)

    def ok(self, command, **arguments):
        return self.route.ok(command, **arguments)


@pytest.fixture(params=["cli", "mcp"])
def rich(request, monkeypatch, tmp_path):
    return Rich(request.param, monkeypatch, tmp_path)


def native(doc):
    """Every paragraph as (units, paragraph style, list), units carrying
    their character, direct text style and suggestion mark."""
    out = []
    for start, mark in doc.paragraphs():
        units = tuple((u.ch, json.dumps(u.ts, sort_keys=True), u.sg)
                      for u in doc.units[start:mark + 1] if not u.cont)
        bullet = doc.units[mark].bullet
        out.append((units, json.dumps(doc.units[mark].ps, sort_keys=True),
                    bullet and (bullet["list"], bullet["nest"])))
    return out


def text_of(paragraph):
    return "".join(ch for ch, _, sg in paragraph[0]
                   if not (sg and sg[0] == "suggestedInsertionIds"))


def assert_only_changed(before, after, changed):
    """Paragraphs whose text is not in *changed* are natively identical, in
    order; returns the changed paragraphs after the command."""
    kept_before = [p for p in before if text_of(p) not in changed]
    touched = [p for p in after if p not in kept_before]
    assert [p for p in after if p not in touched] == kept_before
    return touched


def sibling_untouched(rich):
    for batch in rich.route.service.batches:
        assert "t.appendix" not in json.dumps(batch)
    assert rich.route.service.snapshot()["tabs"][1] == SIBLING


def styled(paragraph, style=STYLE):
    return all(json.loads(ts) == style for ch, ts, _ in paragraph[0]
               if not ch.startswith("[IMG"))


# -- targeted commands keep everything they do not target ----------------------

def test_edit_changes_one_word_and_keeps_every_style(rich):
    before = native(rich.doc)
    rich.ok("cat")
    rich.ok("edit", old_text="approves", new_text="endorses")
    [changed] = assert_only_changed(before, native(rich.doc),
                                    {"The committee approves the budget.\n"})
    assert text_of(changed) == "The committee endorses the budget.\n"
    assert styled(changed)
    sibling_untouched(rich)


def test_insert_at_end_keeps_every_existing_paragraph(rich):
    before = native(rich.doc)
    rich.ok("cat")
    rich.ok("insert", text="Added line.\n", tab="Main", position="end")
    after = native(rich.doc)
    # The tab's last paragraph gains a successor; its own units are unchanged.
    assert after[:len(before)] == before
    assert [text_of(p) for p in after[len(before):]] == ["Added line.\n"]
    sibling_untouched(rich)


def test_insert_at_start_keeps_every_existing_paragraph(rich):
    before = native(rich.doc)
    rich.ok("cat")
    rich.ok("insert", text="Opening line.\n", tab="Main", position="start")
    after = native(rich.doc)
    assert after[-len(before):] == before
    assert [text_of(p) for p in after[:-len(before)]] == ["Opening line.\n"]
    sibling_untouched(rich)


def test_edit_cell_replaces_only_that_cell(rich):
    before = native(rich.doc)
    rich.ok("cat")
    rich.ok("edit", cell="Status", new_text="final", tab="Main")
    [changed] = assert_only_changed(before, native(rich.doc), {"draft\n"})
    assert text_of(changed) == "final\n"
    sibling_untouched(rich)


def test_insert_image_adds_only_the_image(rich):
    before = native(rich.doc)
    rich.ok("cat")
    rich.ok("insert-image", image="https://example.org/new.png", tab="Main",
            after="the budget")
    [changed] = assert_only_changed(before, native(rich.doc),
                                    {"The committee approves the budget.\n"})
    assert [ch for ch, _, _ in changed[0]] == [
        *"The committee approves the budget",
        "[IMG:https://example.org/new.png]", ".", "\n"]
    assert styled(changed)
    sibling_untouched(rich)


def test_replace_image_changes_only_the_image(rich):
    before = native(rich.doc)
    rich.ok("cat")
    rich.ok("replace-image", object_id=rich.image,
            image="https://example.org/replacement.png")
    after = native(rich.doc)
    swapped = [(u if not u[0].startswith("[IMG:") else
                ("[IMG:https://example.org/replacement.png]", *u[1:]))
               for u in before[2][0]]
    assert after == [*before[:2], (tuple(swapped), *before[2][1:]), *before[3:]]
    sibling_untouched(rich)


def test_suggest_marks_only_the_matched_words(rich):
    before = native(rich.doc)
    rich.ok("cat")
    rich.ok("suggest", old_text="budget", new_text="plan")
    [changed] = assert_only_changed(before, native(rich.doc),
                                    {"The committee approves the budget.\n"})
    # The original wording stays until a reviewer accepts the suggestion.
    kept = "".join(ch for ch, _, sg in changed[0]
                   if not (sg and sg[0] == "suggestedInsertionIds"))
    added = "".join(ch for ch, _, sg in changed[0]
                    if sg and sg[0] == "suggestedInsertionIds")
    deleted = "".join(ch for ch, _, sg in changed[0]
                      if sg and sg[0] == "suggestedDeletionIds")
    assert (kept, added, deleted) == (
        "The committee approves the budget.\n", "plan", "budget")
    assert styled(changed)
    sibling_untouched(rich)


# -- changed rewrites report their losses --------------------------------------

def rewrite(rich, **flags):
    markdown = parse_frontmatter(rich.ok("cat"))[1]
    changed = markdown.replace("Closing remark.", "Closing remark, revised.")
    assert changed != markdown
    return rich.call("write", text=changed, **flags)


def test_default_rewrite_needs_the_suggestions_flag_not_allow_lossy(rich):
    code, output, error = rewrite(rich, allow_lossy=True)
    assert code != 0
    assert "collaborators' pending suggestions (1)" in output + error
    assert "--discard-suggestions" in output + error
    assert rich.route.service.batches == []


def test_default_rewrite_reports_extent_comments_and_numbering(rich):
    code, output, error = rewrite(rich, discard_suggestions=True, json=True)
    assert code == 0, output + error
    losses = json.loads(output)["losses"]
    assert losses["paragraphs"] == 10
    assert {"style": "font family", "paragraphs": 10, "protected": False} in (
        losses["styles"])
    assert {"style": "colour", "paragraphs": 10, "protected": False} in (
        losses["styles"])
    assert {"style": "font size", "paragraphs": 1, "protected": False} in (
        losses["styles"])
    assert losses["comments"] == 2 and losses["comments_exact"] is False
    assert losses["pending_suggestions"] == 1
    assert "starts at 5" in losses["numbering"][0]
    assert "font family on 10 of 10 paragraphs" in error
    assert "will detach 2 comments" in error
    sibling_untouched(rich)
