# transcript — rollout-to-launch-window (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty
scratch directory and read nothing outside it (isolation by instruction; PWD reported as
the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/…/scratchpad/empty

COMMANDS:
1. `gdoc cat --account A URL` — read the doc; found three "rollout window" occurrences, all in the TL;DR paragraph (bold, italic inside Priya's quote, and a link to https://example.com/rollout-plan).
2. `gdoc edit --help` — confirmed `edit` supports `--all`, `--case-sensitive`, `--old-file/--new-file`, and markdown in the replacement text.
3. `gdoc edit --account A --all --case-sensitive URL "rollout window" "launch window"` — "OK replaced 3 occurrences".
4. `gdoc cat --account A URL` — rename confirmed, but all three occurrences had lost their formatting (bold, italics and link stripped).
5. `gdoc edit --account A --case-sensitive URL "the launch window of 15-19 Sept" "the **launch window** of 15-19 Sept"` — "OK replaced 1 occurrence".
6. `gdoc cat … | sed -n '1,12p'` — bold restored on the first occurrence.
7. `gdoc edit --account A --case-sensitive URL "touch the launch window without" "touch the *launch window* without"` — "OK replaced 1 occurrence".
8. `gdoc edit --account A --case-sensitive URL "so the launch window is frozen" "so the [launch window](https://example.com/rollout-plan) is frozen"` — "OK replaced 1 occurrence".
9. `gdoc cat --account A URL` — link restored, but the bold from step 5 was gone again and the italics from step 7 never appeared.
10. `gdoc edit --account A --case-sensitive --old-file old.txt --new-file new.txt URL` — replaced the entire TL;DR paragraph with a version carrying all three markdown markers; "WARN: doc changed since last read / OK replaced 1 occurrence".
11. `gdoc cat --account A URL` — TL;DR paragraph now shows **launch window**, *launch window*, and [launch window](https://example.com/rollout-plan); rest of doc unchanged from the first read.

WHAT I CHANGED: In the TL;DR paragraph only, renamed all three instances of "rollout window" to "launch window" — the bold one, the italicised one inside Priya's quoted Slack message, and the linked one (link target left as https://example.com/rollout-plan). Everything outside that paragraph, including "during the rollout?" in Open questions, was left untouched.

SUCCEEDED: yes — the final read shows the paragraph with the new term and the original bold/italic/link formatting intact, and no other part of the document changed.

CONCERNS:
- The first replace-all stripped bold, italics and the hyperlink from the replaced text, and the follow-up markdown-bearing edits each appeared to reset the paragraph's formatting to only what the replacement text specified (step 8 wiped the bold restored in step 5). It took a whole-paragraph replacement to recover. The document went through six write revisions (v9 → v15 or so) for what should have been one; anyone checking version history will see the intermediate unformatted states.
- I can only verify formatting that `gdoc cat` renders (bold, italic, links). If the original paragraph had other run-level styling (colour, highlight, font size) or a paragraph style not visible in the markdown export, the whole-paragraph replacement may have flattened it. Worth a quick visual check in the browser.
- I also renamed the term inside Priya's direct quote ("don't touch the *launch window*…"). That's what "rename it there" implies for the paragraph, but it does alter a verbatim quote of what she wrote in Slack; easy to revert that one word if the colleague prefers the quote kept literal.
