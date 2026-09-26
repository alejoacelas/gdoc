"""Round-3 review regressions through the real CLI and MCP task routes."""

import json

from tests.acceptance.conftest import paragraph
from tests.acceptance.test_workflows import existing_image, read, requests


def _reply_with_image_ids(scenario):
    """Answer each batch as Docs does: one reply per request, new image IDs."""
    counter = iter(range(1, 1000))
    execute = scenario.service.documents.return_value.batchUpdate.return_value.execute
    batch = scenario.service.documents.return_value.batchUpdate

    def respond(*args, **kwargs):
        body = batch.call_args.kwargs["body"]
        return {
            "writeControl": {"requiredRevisionId": "r2"},
            "replies": [
                {"insertInlineImage": {"objectId": f"copy{next(counter)}"}}
                if "insertInlineImage" in request else {}
                for request in body["requests"]
            ],
        }

    execute.side_effect = respond


def _inserted_text(scenario):
    return "".join(r["insertText"]["text"] for r in requests(scenario)
                   if "insertText" in r)


def test_repeated_image_and_literal_token_survive_successive_writes(scenario):
    existing_image(scenario)
    source = read(scenario)
    assert "![Map](gdoc-image:map)" in source
    _reply_with_image_ids(scenario)
    revised = (source.replace("Before", "Revised")
               + "![Map](gdoc-image:map)\n\n```\nsee gdoc-image:map\n```\n")
    scenario.ok("write", tab="draft", text=revised)
    assert sum("insertInlineImage" in r for r in requests(scenario)) == 2

    # Google replaced the original object with the two copies.
    native = scenario.document["tabs"][0]["documentTab"]
    embedded = native["inlineObjects"].pop("map")
    native["inlineObjects"] = {"copy1": embedded, "copy2": embedded}
    for element in native["body"]["content"][1]["paragraph"]["elements"]:
        if "inlineObjectElement" in element:
            element["inlineObjectElement"]["inlineObjectId"] = "copy1"
    scenario.document["revisionId"] = "r2"
    scenario.service.documents.return_value.batchUpdate.reset_mock()

    # The agent keeps editing its own text, which still names the old object.
    scenario.ok("write", tab="draft", text=revised.replace("Revised", "Again"))
    images = [r["insertInlineImage"] for r in requests(scenario)
              if "insertInlineImage" in r]
    assert len(images) == 2
    assert {image["uri"] for image in images} == {
        "https://example.invalid/temporary-map.png"}
    # Literal code keeps the token the agent wrote.
    assert "see gdoc-image:map" in _inserted_text(scenario)


def test_quoted_soft_line_break_round_trips_through_cat(scenario):
    quoted = paragraph("line one\x0bline two\n")
    native = scenario.document["tabs"][0]["documentTab"]
    native["body"]["content"] = [quoted]
    native["namedRanges"] = {"gdoc:prefix:v1:1:0": {"namedRanges": [{
        "name": "gdoc:prefix:v1:1:0",
        "ranges": [{"startIndex": 1, "endIndex": quoted["endIndex"]}],
    }]}}
    source = read(scenario)
    assert source == "> line one\x0bline two\n"
    scenario.ok("write", tab="draft", text=source + "\nAdded\n")
    assert "> " not in _inserted_text(scenario)
    assert "line one\x0bline two" in _inserted_text(scenario)


def test_rename_image_references_changes_only_image_destinations():
    from gdoc.mdparse import rename_image_references

    source = (
        "```\n![](gdoc-image:old)\n```\n"
        "![](gdoc-image:old) prose gdoc-image:old `![](gdoc-image:old)` "
        "\\![](gdoc-image:old)\n"
        "> ```\n> ![](gdoc-image:old)\n> ```\n"
        "| ![a](gdoc-image:old) | [x](gdoc-image:old) |\n"
        "[![i](gdoc-image:old)](https://example.invalid/a)\n"
    )
    renamed = rename_image_references(source, {"old": "new"})
    assert renamed == (
        "```\n![](gdoc-image:old)\n```\n"
        "![](gdoc-image:new) prose gdoc-image:old `![](gdoc-image:old)` "
        "\\![](gdoc-image:old)\n"
        "> ```\n> ![](gdoc-image:old)\n> ```\n"
        "| ![a](gdoc-image:new) | [x](gdoc-image:old) |\n"
        "[![i](gdoc-image:new)](https://example.invalid/a)\n"
    )
    assert json.dumps(renamed)  # stays plain text
