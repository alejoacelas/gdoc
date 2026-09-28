"""Comments a rewrite would detach are counted before the write.

Drive names a comment's anchor but not its tab, and reports detached comments
unchanged afterwards, so gdoc counts anchored comments (open or resolved)
first and attributes them to tabs by quoted text in multi-tab documents.
"""

import pytest

from gdoc.cli import _tab_comment_count

pytestmark = pytest.mark.comment_count


def _tab(tab_id, text):
    return {"id": tab_id, "title": tab_id, "body": {"content": [
        {"startIndex": 1, "endIndex": 1 + len(text), "paragraph": {"elements": [
            {"startIndex": 1, "endIndex": 1 + len(text),
             "textRun": {"content": text}}]}}]}}


def _comment(quote, anchor="kix.1", resolved=False):
    comment = {"id": quote, "resolved": resolved,
               "quotedFileContent": {"value": quote}}
    if anchor:
        comment["anchor"] = anchor
    return comment


def test_one_tab_counts_every_anchored_comment_exactly(mocker):
    mocker.patch("gdoc.api.comments.list_comments", return_value=[
        _comment("alpha"), _comment("beta", resolved=True),
        _comment("gamma", anchor=None)])
    assert _tab_comment_count("doc", [_tab("a", "alpha beta\n")],
                              _tab("a", "alpha beta\n")) == (2, True)


def test_several_tabs_attribute_by_quoted_text(mocker):
    main, other = _tab("main", "alpha shared\n"), _tab("other", "beta shared\n")
    mocker.patch("gdoc.api.comments.list_comments", return_value=[
        _comment("alpha"),              # only in main: counted
        _comment("beta"),               # only in the other tab: not counted
        _comment("shared"),             # in both: counted
        _comment("reworded since"),     # in no tab: may be here, counted
        _comment("beta", anchor=None),  # unanchored: never counted
    ])
    assert _tab_comment_count("doc", [main, other], main) == (3, False)


def test_no_anchored_comments(mocker):
    listing = mocker.patch("gdoc.api.comments.list_comments", return_value=[])
    assert _tab_comment_count("doc", [_tab("a", "x\n")], _tab("a", "x\n")) == (0, True)
    listing.assert_called_once_with("doc", include_anchor=True)
