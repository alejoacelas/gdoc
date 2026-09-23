"""Concrete final-review regressions at native service boundaries."""
import pytest

from gdoc import mcp
from gdoc.api.docs import _native_docs_requests, _prepare_image_sources
from gdoc.mdparse import parse_markdown


def test_existing_image_reconstruction_keeps_native_size():
    size = {"width": {"magnitude": 120, "unit": "PT"},
            "height": {"magnitude": 80, "unit": "PT"}}
    snapshot = {"inlineObjects": {"image": {"inlineObjectProperties": {
        "embeddedObject": {"size": size, "imageProperties": {
            "contentUri": "https://example.org/fresh.png",
        }},
    }}}}
    parsed = parse_markdown("Changed ![](gdoc-image:image)")
    _prepare_image_sources(parsed, snapshot)
    requests = _native_docs_requests(parsed, 1, "main")
    image = next(r["insertInlineImage"] for r in requests if "insertInlineImage" in r)
    assert image["objectSize"] == size
    assert image["uri"] == "https://example.org/fresh.png"


@pytest.mark.parametrize("command", ["write"])
def test_mcp_rejects_combined_tab_inspection_before_any_service_call(mocker, command):
    fetch = mocker.patch("gdoc.api.docs.get_document_with_tabs")
    _, stderr, code = mcp.call_command(command, {
        "doc": "synthetic", "text": "=== Tab: First ===\nA\n=== Tab: Second ===\nB\n",
        "quiet": True,
    })
    assert code == 3
    assert "each tab separately" in stderr
    fetch.assert_not_called()
