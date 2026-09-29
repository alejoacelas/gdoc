"""The rewrite policy is a ceiling on what a changed full-tab rewrite loses.

Every level (strict, formatting, markdown) times every loss category, through
CLI and MCP. Both interfaces must print identical warnings and refusals.
"""

import json

import pytest

from gdoc import mcp, state
from gdoc.frontmatter import parse_frontmatter
from tests.acceptance.test_round5_workflows import NativeRoute
from tests.native_model import NativeDoc, NativeService, Unit

STYLE = {"weightedFontFamily": {"fontFamily": "Georgia", "weight": 400}}
NUMBERED = "NUMBERED_DECIMAL_ALPHA_ROMAN"


def _plain():
    return NativeDoc(("p", "Alpha."), ("p", "Beta."))


def _with_image(properties):
    def build():
        doc = _plain()
        doc.units.insert(1, Unit("[IMG:https://example.org/i.png]"))
        doc.images = 1
        return doc, properties
    return build


def _styled():
    doc = _plain()
    for unit in doc.units:
        if unit.kind == "text":
            unit.ts = dict(STYLE)
    return doc, None


def _suggested():
    doc = _plain()
    doc.units[1].sg = ("suggestedInsertionIds", "suggest.collaborator")
    return doc, None


def _numbered():
    doc = NativeDoc(("p", "Alpha.", "NORMAL_TEXT",
                     {"preset": NUMBERED, "list": 1, "nest": 0}), ("p", "Beta."))
    doc.list_starts[1] = 5
    return doc, None


# Category -> (builder, protected, the per-call flag the markdown level needs,
# a phrase its warning or refusal names).
CATEGORIES = {
    "rich content": (lambda: (_plain(), "chip"), True, "allow_lossy",
                     "people chips"),
    "pending suggestions": (_suggested, True, "discard_suggestions",
                            "collaborators' pending suggestions (1)"),
    "anchored comments": (lambda: (_plain(), "comment"), True, None,
                          "up to 1 comment anchored in the tab"),
    "image crop": (_with_image({"cropProperties": {"offsetLeft": 0.2}}), True,
                   None, "image crop on 1 image"),
    "direct styles": (_styled, False, None, "font family on 2 of 2 paragraphs"),
    "image adjustments": (_with_image({"angle": 1.5}), False, None,
                          "image rotation, brightness, contrast, transparency "
                          "or border on 1 image"),
    "image alt text": (_with_image({"description": "A map"}), False, None,
                       "image alt text on 1 image"),
    "numbering": (_numbered, False, None, "starts at 5"),
    "heading links": (lambda: (_plain(), "heading"), False, None,
                      "the IDs of 1 heading, so links to them"),
}


def run(interface, monkeypatch, tmp_path, category, level, flags):
    """cat then a changed write; returns (code, ERR/WARN lines, batches)."""
    build, *_ = CATEGORIES[category]
    doc, extra = build()
    base = tmp_path / f"{interface}-{len(list(tmp_path.iterdir()))}"
    base.mkdir()
    monkeypatch.setattr(state, "STATE_DIR", base / "state")
    monkeypatch.setenv("GDOC_REWRITE_POLICY", level)
    route = NativeRoute(interface, monkeypatch, base)
    service = route.service = NativeService(doc)
    comments = [{"id": "c1", "anchor": "kix.1", "resolved": False,
                 "quotedFileContent": {"value": "Alpha"}}]
    monkeypatch.setattr("gdoc.api.comments.list_comments",
                        lambda *a, **k: comments if extra == "comment" else [])
    snapshot = service.snapshot

    def enriched():
        value = snapshot()
        if service.batches:
            return value  # the rewrite replaced the rich content
        tab = value["tabs"][0]["documentTab"]
        if extra == "heading":
            paragraph = next(e for e in tab["body"]["content"] if "paragraph" in e)
            paragraph["paragraph"]["paragraphStyle"].update(
                namedStyleType="HEADING_1", headingId="h.abc123")
        elif extra == "chip":
            paragraph = next(e for e in tab["body"]["content"] if "paragraph" in e)
            paragraph["paragraph"]["elements"].insert(0, {"person": {
                "personProperties": {"name": "Ana", "email": "ana@example.org"}}})
        elif isinstance(extra, dict):
            for inline in tab["inlineObjects"].values():
                embedded = inline["inlineObjectProperties"]["embeddedObject"]
                image = embedded["imageProperties"]
                for key, value_ in extra.items():
                    (embedded if key == "description" else image)[key] = value_
        return value

    service.snapshot = enriched
    markdown = parse_frontmatter(route.ok("cat"))[1]
    changed = markdown.replace("Beta.", "Beta, revised.")
    assert changed != markdown
    code, output, error = route.call("write", text=changed, **flags)
    lines = [line for line in (output + "\n" + error).splitlines()
             if line.startswith(("ERR:", "WARN:"))]
    return code, lines, len(service.batches)


def both(monkeypatch, tmp_path, category, level, flags=None):
    cli = run("cli", monkeypatch, tmp_path, category, level, flags or {})
    via_mcp = run("mcp", monkeypatch, tmp_path, category, level, flags or {})
    # An MCP error result carries only the ERR lines, as for every command.
    shown = [line for line in cli[1] if not cli[0] or line.startswith("ERR:")]
    assert shown == via_mcp[1], "CLI and MCP must report identically"
    assert bool(cli[0]) == bool(via_mcp[0]) and cli[2] == via_mcp[2]
    return cli


LEVELS = ["strict", "formatting", "markdown"]


@pytest.mark.parametrize("category", list(CATEGORIES))
@pytest.mark.parametrize("level", LEVELS)
def test_each_level_limits_each_category(monkeypatch, tmp_path, level, category):
    _, protected, flag, phrase = CATEGORIES[category]
    all_flags = {"allow_lossy": True, "discard_suggestions": True}
    refused = level == "strict" or (level == "formatting" and protected)
    # Per-call flags never exceed the policy ceiling.
    code, lines, batches = both(monkeypatch, tmp_path, category, level, all_flags)
    text = "\n".join(lines)
    assert phrase in text
    if refused:
        assert code != 0 and batches == 0
        assert f"refused by rewrite policy '{level}'" in text
        allowed = "markdown" if protected else "formatting"
        assert f"Rewrite policy '{allowed}' would allow it" in text
        assert "GDOC_REWRITE_POLICY" in text and "rewrite_policy" in text
        assert "human configuration choice" in text
        # The targeted route is named before the rewrite and its cost.
        assert text.index("`edit` changes wording") < text.index(
            "A rewrite (`write`, `push`) deletes and reinserts the whole tab")
        return
    assert code == 0 and batches, text
    if flag and level == "markdown":
        # The markdown level still needs the category's own per-call consent.
        others = {k: v for k, v in all_flags.items() if k != flag}
        code, lines, batches = both(monkeypatch, tmp_path, category, level, others)
        text = "\n".join(lines)
        assert code != 0 and batches == 0
        assert "--" + flag.replace("_", "-") in text and phrase in text


@pytest.mark.parametrize("level", LEVELS)
def test_a_tab_without_losses_rewrites_at_every_level(monkeypatch, tmp_path, level):
    CATEGORIES["none"] = (lambda: (_plain(), None), False, None, "")
    try:
        code, lines, batches = both(monkeypatch, tmp_path, "none", level)
    finally:
        del CATEGORIES["none"]
    assert code == 0 and batches and lines == []


def test_config_key_sets_the_level(monkeypatch, tmp_path):
    from gdoc import util

    monkeypatch.setattr(util, "_load_config", lambda: {"rewrite_policy": "strict"})
    monkeypatch.delenv("GDOC_REWRITE_POLICY", raising=False)
    assert util.get_rewrite_policy() == "strict"
    monkeypatch.setenv("GDOC_REWRITE_POLICY", "markdown")
    assert util.get_rewrite_policy() == "markdown"


def test_an_unknown_level_refuses_the_rewrite(monkeypatch, tmp_path):
    code, lines, batches = both(monkeypatch, tmp_path, "direct styles", "loose")
    assert code != 0 and batches == 0
    assert "Invalid rewrite policy: 'loose'" in "\n".join(lines)


def test_mcp_cannot_change_the_policy():
    tools = mcp.build_tools()
    assert "gdoc_config" not in tools
    assert not any("rewrite_policy" in json.dumps(tool["inputSchema"])
                   for tool in tools.values())


SUGGESTED_SIBLING = {
    "tabProperties": {"tabId": "t.notes", "title": "Notes", "index": 1},
    "documentTab": {"body": {"content": [
        {"startIndex": 0, "endIndex": 1, "sectionBreak": {}},
        {"startIndex": 1, "endIndex": 7, "paragraph": {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "elements": [{"startIndex": 1, "endIndex": 7, "textRun": {
                "content": "Notes\n",
                "suggestedInsertionIds": ["suggest.collaborator"]}}]}},
    ]}},
}


def collapse(interface, monkeypatch, tmp_path, level, flags,
             sibling=SUGGESTED_SIBLING):
    base = tmp_path / f"{interface}-{len(list(tmp_path.iterdir()))}"
    base.mkdir()
    monkeypatch.setattr(state, "STATE_DIR", base / "state")
    monkeypatch.setenv("GDOC_REWRITE_POLICY", level)
    route = NativeRoute(interface, monkeypatch, base)
    service = route.service = NativeService(
        _plain(), extra_tabs=[json.loads(json.dumps(sibling))])
    code, output, error = route.call(
        "write", text="Alpha.\nBeta, revised.\n", force=True,
        force_collapse_tabs=True, **flags)
    lines = [line for line in (output + "\n" + error).splitlines()
             if line.startswith(("ERR:", "WARN:"))]
    service.output = output
    return code, lines, service


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("discard", [False, True])
def test_collapse_checks_the_tabs_it_deletes(monkeypatch, tmp_path, level,
                                             discard):
    """--force-collapse-tabs covers deleting content, not the policy ceiling
    or collaborators' pending suggestions in the deleted tabs."""
    flags = {"discard_suggestions": True} if discard else {}
    cli = collapse("cli", monkeypatch, tmp_path, level, flags)
    via_mcp = collapse("mcp", monkeypatch, tmp_path, level, flags)
    shown = [line for line in cli[1] if not cli[0] or line.startswith("ERR:")]
    assert shown == via_mcp[1]
    allowed = level == "markdown" and discard
    for code, lines, service in (cli, via_mcp):
        text = "\n".join(lines)
        assert "collaborators' pending suggestions (1)" in text
        assert "tab 'Notes'" in text and "--force-collapse-tabs" in text
        if allowed:
            assert code == 0 and service.extra_tabs == []
        else:
            assert code != 0 and service.batches == []


def _header_suggested_sibling():
    sibling = json.loads(json.dumps(SUGGESTED_SIBLING))
    run = sibling["documentTab"]["body"]["content"][1]["paragraph"]["elements"][0]
    run["textRun"].pop("suggestedInsertionIds")
    sibling["documentTab"]["headers"] = {"h1": {"content": [
        {"startIndex": 0, "endIndex": 7, "paragraph": {"elements": [
            {"startIndex": 0, "endIndex": 7, "textRun": {
                "content": "Header\n",
                "suggestedInsertionIds": ["suggest.header"]}}]}}]}}
    return sibling


@pytest.mark.parametrize("interface", ["cli", "mcp"])
def test_collapse_checks_a_deleted_tabs_headers(monkeypatch, tmp_path, interface):
    code, lines, service = collapse(interface, monkeypatch, tmp_path, "markdown",
                                    {}, sibling=_header_suggested_sibling())
    assert code != 0 and service.batches == []
    assert "collaborators' pending suggestions (1)" in "\n".join(lines)


@pytest.mark.parametrize("interface", ["cli", "mcp"])
def test_collapse_json_names_deleted_tab_losses(monkeypatch, tmp_path, interface):
    code, lines, service = collapse(interface, monkeypatch, tmp_path, "markdown",
                                    {"discard_suggestions": True, "json": True})
    assert code == 0 and service.extra_tabs == []
    assert ("WARN: --force-collapse-tabs deletes tab 'Notes', discarding "
            "collaborators' pending suggestions (1)") in lines
    assert json.loads(service.output)["deleted_tab_losses"] == {"t.notes": {
        "title": "Notes", "pending_suggestions": 1,
        "pending_suggestions_counted": True}}


@pytest.mark.parametrize("markdown", [
    "- one\n  - two\n    - three\n\n1. a\n2. b\n",
    "> - quoted item\n> - another\n\nafter\n",
    "1. step\n\n   > - contained\n2. next\n",
    "before\n---\nafter\n",
])
@pytest.mark.parametrize("interface", ["cli", "mcp"])
def test_gdocs_own_lists_rewrite_under_strict(monkeypatch, tmp_path, interface,
                                              markdown):
    """Lists gdoc wrote, including quoted and contained ones, report no loss."""
    monkeypatch.setattr(state, "STATE_DIR", tmp_path / "state")
    route = NativeRoute(interface, monkeypatch, tmp_path)
    route.load(NativeDoc())
    route.ok("cat")
    route.ok("write", text=markdown)
    monkeypatch.setenv("GDOC_REWRITE_POLICY", "strict")
    text = parse_frontmatter(route.ok("cat"))[1]
    code, output, error = route.call("write", text=text + "tail\n")
    assert code == 0, output + error
    assert "WARN" not in error


@pytest.mark.parametrize("interface", ["cli", "mcp"])
def test_collapse_warns_about_deleted_tabs_only_after_writing(
        monkeypatch, tmp_path, interface):
    """A refusal of the first tab leaves no claim that a sibling was deleted."""
    base = tmp_path / interface
    base.mkdir()
    monkeypatch.setattr(state, "STATE_DIR", base / "state")
    route = NativeRoute(interface, monkeypatch, base)
    doc, _ = _suggested()  # the first tab refuses without the flag
    styled = json.loads(json.dumps(SUGGESTED_SIBLING))
    run = styled["documentTab"]["body"]["content"][1]["paragraph"]["elements"][0]
    run["textRun"] = {"content": "Notes\n", "textStyle": STYLE}  # only warns
    service = route.service = NativeService(doc, extra_tabs=[styled])
    code, output, error = route.call(
        "write", text="Alpha.\nBeta, revised.\n", force=True,
        force_collapse_tabs=True)
    assert code != 0 and service.batches == []
    assert "collaborators' pending suggestions" in output + error
    assert "--force-collapse-tabs deletes tab" not in output + error
    # With the flag, the write succeeds and the deletion warning appears.
    code, output, error = route.call(
        "write", text="Alpha.\nBeta, revised.\n", force=True,
        force_collapse_tabs=True, discard_suggestions=True)
    assert code == 0, output + error
    assert "--force-collapse-tabs deletes tab 'Notes', discarding direct styles" in (
        error)


def test_config_saves_the_policy_it_later_reads(monkeypatch, tmp_path):
    from gdoc import util

    monkeypatch.setattr(util, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.delenv("GDOC_REWRITE_POLICY", raising=False)
    util.set_rewrite_policy("formatting")
    assert json.loads((tmp_path / "config.json").read_text()) == {
        "rewrite_policy": "formatting"}
    # The suite hides a developer's saved policy; read the file directly.
    monkeypatch.setattr(util, "_load_config", lambda: json.loads(
        (tmp_path / "config.json").read_text()))
    assert util.get_rewrite_policy() == "formatting"


@pytest.mark.parametrize("interface", ["cli", "mcp"])
def test_a_saved_strict_policy_refuses_a_write(monkeypatch, tmp_path, interface):
    """End to end through the real config file: config saves, write reads."""
    import contextlib
    import io

    from gdoc import cli

    monkeypatch.delenv("GDOC_REWRITE_POLICY", raising=False)
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.run_argv(["config", "--rewrite-policy", "strict"],
                            check_updates=False) == 0
    monkeypatch.setattr(state, "STATE_DIR", tmp_path / "state")
    route = NativeRoute(interface, monkeypatch, tmp_path)
    doc, _ = _styled()
    route.service = NativeService(doc)
    text = parse_frontmatter(route.ok("cat"))[1]
    code, output, error = route.call("write", text=text.replace("Beta.", "Beta!"))
    assert code != 0 and "refused by rewrite policy 'strict'" in output + error
    assert route.service.batches == []
