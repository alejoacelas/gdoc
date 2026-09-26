"""R7-2: `write` honours a pulled file's source document and tab.

A file pulled from one tab is never silently written into another: without
--tab it replaces the tab it came from, and a contradicting --tab, a different
document or a missing source tab is refused before any mutation. Metadata-free
input keeps the documented first-tab default.
"""

import json

import pytest

from tests.acceptance.test_round5_workflows import NativeRoute
from tests.native_model import NativeDoc


@pytest.fixture(params=["cli", "mcp"])
def route(request, monkeypatch, tmp_path):
    return NativeRoute(request.param, monkeypatch, tmp_path)


def _two_tabs(route):
    """The modeled tab is Main (t.0); Appendix (t.1) is a static sibling."""
    route.load(NativeDoc(("p", "Main tab content.")))
    appendix = NativeDoc(("p", "Appendix content.")).document_tab("t.1")
    route.service.extra_tabs = [{
        "tabProperties": {"tabId": "t.1", "title": "Appendix", "index": 1},
        "documentTab": appendix,
    }]


def _pulled(route, tab_id="t.1", doc="synthetic", body="Appendix revised.\n"):
    route.ok("cat", tab="Main")
    route.ok("cat", tab="Appendix")
    return (f"---\ngdoc: {doc}\ntitle: Synthetic\ntab: {tab_id}\n"
            f"gdoc-revision: r1\n---\n{body}")


def _targets(route, since):
    """The tab IDs addressed by the batches sent after *since* batches."""
    found = set()
    for batch in route.service.batches[since:]:
        text = json.dumps(batch)
        found.update(t for t in ("t.0", "t.1") if f'"tabId": "{t}"' in text)
    return found


def test_pulled_tab_file_replaces_its_own_tab_without_tab_flag(route):
    _two_tabs(route)
    text = _pulled(route)
    code, output, error = route.call("write", text=text)
    assert code == 0, output + error
    assert "Appendix" in output and "t.1" in output
    assert route.service.batches and _targets(route, 0) == {"t.1"}


def test_contradicting_tab_flag_is_refused_before_mutation(route):
    _two_tabs(route)
    text = _pulled(route)
    code, output, error = route.call("write", text=text, tab="Main")
    assert code != 0
    assert "pulled from tab 'Appendix'" in output + error
    assert route.service.batches == []


def test_matching_tab_flag_writes_that_tab(route):
    _two_tabs(route)
    text = _pulled(route)
    code, output, error = route.call("write", text=text, tab="Appendix")
    assert code == 0, output + error
    assert _targets(route, 0) == {"t.1"}


def test_file_from_another_document_is_refused(route):
    _two_tabs(route)
    text = _pulled(route, doc="another-document")
    code, output, error = route.call("write", text=text)
    assert code != 0
    assert "pulled from document another-document" in output + error
    assert route.service.batches == []


def test_missing_source_tab_needs_an_explicit_tab(route):
    _two_tabs(route)
    text = _pulled(route, tab_id="t.9")
    code, output, error = route.call("write", text=text)
    assert code != 0
    assert "no longer has" in output + error
    assert route.service.batches == []
    code, output, error = route.call("write", text=text, tab="Main")
    assert code == 0, output + error


def test_collapse_refuses_a_file_pulled_from_a_later_tab(route):
    _two_tabs(route)
    text = _pulled(route)
    code, output, error = route.call("write", text=text, force_collapse_tabs=True)
    assert code != 0
    assert "--force-collapse-tabs replaces the first tab" in output + error
    assert route.service.batches == []


@pytest.mark.parametrize("text", [
    "New first tab text.\n",
    "---\n---\nNew first tab text.\n",
    "---\ntitle: notes\n---\nNew first tab text.\n",
])
def test_metadata_free_input_keeps_the_first_tab_default(route, text):
    _two_tabs(route)
    route.ok("cat", tab="Main")
    code, output, error = route.call("write", text=text)
    assert code == 0, output + error
    assert "'Main' (t.0)" in output
    assert route.service.doc.paragraphs()
