# Tasks — gdt-collab-v01

Five fields each; see the skill's Tasks section. Every task here needs a Docs-UI copy (comments
and suggestions). Comment ids are those of the fixture; copies keep the same ids.

## reply-broadband-thread

- **Request:** On the broadband comment thread (the one about £15 being too low), add a reply
  saying "Agreed, going with £25 — finance signed off on 3 Sept." Don't resolve it.
- **Expected:** Comment `AAACFLVgk3k` (anchored `capped at £15 a month`) has three replies, the
  new one last with exactly that text; still open. The pending suggestion `£15`→`£25` in the
  same bullet is still pending. Body byte-identical.
- **Target:** comment.
- **Allowed:** comment `modifiedTime` changes; revision list grows.
- **Preconditions:** the comment with two replies exists in the copy; the suggestion in the
  bullet is pending.

## resolve-fake-heading-comment

- **Request:** The "What changes" line is fine as it is — resolve the comment that asks to make
  it a real heading, with a short reply "Leaving as is for v3."
- **Expected:** Comment `AAACFLVgk4E` (anchored `What changes`) is resolved with one reply
  `Leaving as is for v3.`; the paragraph `What changes` is still bold 14pt Normal text; all
  other comments untouched. Body byte-identical.
- **Target:** comment.
- **Allowed:** comment `modifiedTime` changes; revision list grows.
- **Preconditions:** the open comment anchored `What changes` exists in the copy.

## reopen-three-forms

- **Request:** Someone resolved the comment about "three forms" but the text now says four —
  reopen that comment and reply "Reopening: the paragraph now says four forms, is that right?"
- **Expected:** Comment `AAACFLVgk4I` (quoted `three forms`) is no longer resolved and has a new
  reply with that text (after the existing reply). Body byte-identical, including `four forms`.
- **Target:** comment.
- **Allowed:** comment `modifiedTime` changes; revision list grows.
- **Preconditions:** the resolved comment with quoted text `three forms` exists in the copy
  (`gdoc comments --all`).

## handbook-link-notion

- **Request:** The finance handbook link points at the old handbook — change it to
  https://www.notion.so/people-ops/expenses. Keep the wording.
- **Expected:** In the paragraph `Claims go through the expenses portal`, the run `handbook` is
  still linked, now to `https://www.notion.so/people-ops/expenses`; the text is unchanged and
  the comment anchored on `handbook` (`AAACFLVgk3g`) is still open and anchored. Nothing else
  changes.
- **Target:** tab `Tab 1`, paragraph beginning `Claims go through`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the link on `handbook` and the comment anchored on it exist in the copy.

## suggest-contractors-sentence

- **Request:** In Open questions, add — as a suggestion, not a direct edit — the sentence
  "Legal will confirm by 15 Sept." at the end of the contractors paragraph.
- **Expected:** The paragraph beginning `Should contractors be eligible?` gains a pending
  suggested insertion ` Legal will confirm by 15 Sept.` at its end (after the existing pending
  insertion ` People Ops has no strong view either way.`, which stays pending). No accepted
  text changes anywhere. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Should contractors be eligible`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the pending insertion ` People Ops has no strong view either way.` is
  present in the copy.

## next-review-september

- **Request:** The next review isn't June any more, it's September — fix the last line.
- **Expected:** The paragraph beginning `Next review:` reads `Next review: September. Owner:
  People Ops. …` with the pending suggestion (`March`→`June`) resolved in whatever way the
  agent chooses, OR `Next review: {+September+}{-March-}.` with the suggestion amended — either
  is acceptable as long as no other paragraph changes and no other suggestion or comment is
  touched. (Ambiguous on purpose: the current text exists only as a suggestion.)
- **Target:** tab `Tab 1`, paragraph beginning `Next review:`.
- **Allowed:** the `March`→`June` suggestion may be accepted, replaced or amended; revision list
  grows; `modifiedTime` changes.
- **Preconditions:** the pending suggestion `March`→`June` exists in the last paragraph.
