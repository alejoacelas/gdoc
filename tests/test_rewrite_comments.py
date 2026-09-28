"""Comments a rewrite would detach are counted before the write.

Drive names a comment's anchor but not its tab, and reports detached comments
unchanged afterwards. A comment's quoted text can be stale, so it cannot place
a comment in a tab either: in a multi-tab document every anchored comment
counts, and the count is marked inexact.
"""

import pytest

from gdoc.cli import _tab_comment_count
from gdoc.lossy import check_markdown_replacement
from gdoc.util import GdocError

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
    assert _tab_comment_count("doc", [_tab("a", "alpha beta\n")]) == (2, True)


def test_a_stale_quote_in_a_sibling_still_counts(mocker):
    """The comment is anchored in Main, whose wording changed since; its
    quote now matches only the sibling. It must still refuse at formatting."""
    main, other = _tab("main", "funding plan\n"), _tab("other", "budget plan\n")
    mocker.patch("gdoc.api.comments.list_comments",
                 return_value=[_comment("budget plan", anchor="kix.main")])
    count, exact = _tab_comment_count("doc", [main, other])
    assert (count, exact) == (1, False)
    with pytest.raises(GdocError, match="up to 1 comment anchored in the tab"):
        check_markdown_replacement(main, tab_body=True, comments=count,
                                   comments_exact=exact, policy="formatting")


def test_a_collapse_counts_every_comment_in_the_document(mocker):
    mocker.patch("gdoc.api.comments.list_comments", return_value=[
        _comment("alpha"), _comment("beta")])
    tabs = [_tab("a", "\n"), _tab("b", "beta\n")]
    assert _tab_comment_count("doc", tabs, collapse=True,
                              selected=tabs[0]) == (2, False)


def test_an_image_only_tab_still_counts(mocker):
    """Docs lets a comment anchor on an image."""
    listing = mocker.patch("gdoc.api.comments.list_comments",
                           return_value=[_comment("", anchor="kix.image")])
    image = {"id": "a", "title": "a", "body": {"content": [{"paragraph": {
        "elements": [{"inlineObjectElement": {"inlineObjectId": "i"}},
                     {"textRun": {"content": "\n"}}]}}]}}
    assert _tab_comment_count("doc", [image], selected=image) == (1, True)
    listing.assert_called_once()


def test_no_anchored_comments(mocker):
    listing = mocker.patch("gdoc.api.comments.list_comments", return_value=[])
    assert _tab_comment_count("doc", [_tab("a", "x\n")]) == (0, True)
    listing.assert_called_once_with("doc", include_anchor=True)


def test_an_empty_tab_holds_no_comment(mocker):
    """Filling a new tab is never refused over comments elsewhere."""
    listing = mocker.patch("gdoc.api.comments.list_comments",
                           return_value=[_comment("alpha")])
    tabs = [_tab("a", "alpha\n"), _tab("new", "\n")]
    assert _tab_comment_count("doc", tabs, selected=tabs[1]) == (0, True)
    listing.assert_not_called()
    assert _tab_comment_count("doc", tabs, selected=tabs[0]) == (1, False)
