# transcript — launch-to-release-window (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/agent-launch-to-release-window

COMMANDS:
1. `gdoc --help` — listed subcommands (edit, cat, structure, diff, revisions, ...)
2. `gdoc cat --account ... URL` — read the doc; found 5 lowercase "launch window" (H1 title, bold in Key dates, italic in Ana's note, FAQ link text, "If anything slips") plus the capitalized "Launch Window banner" and "#launch" to leave alone
3. `gdoc info --account ... URL` — Drive file name is `gdt-text-v01 run 20260902 launch-to-release-window` (doesn't contain the phrase), so "title" means the in-doc H1
4. `gdoc edit --help` — confirmed `--all`, `--case-sensitive`, markdown allowed in replacement text
5. `gdoc edit --account ... --all --case-sensitive URL "launch window" "release window"` — OK replaced 5 occurrences
6. `gdoc cat --account ... URL | grep -n -i window` — text correct, but formatting markers gone on the edited lines
7. `gdoc cat --account ... URL` — confirmed collateral damage: H1 became plain text; bold/italic on the phrase lost; bold on "checklist" (same paragraph, not in my match) lost; FAQ link shrank from "launch window FAQ" to just "FAQ"
8. `gdoc diff --help; gdoc structure --help` — found revision diff and raw-style dump
9. `gdoc revisions --account ... URL` — 2 retained revisions
10. `gdoc diff --account ... --rev head~1..latest --format plain URL` — confirmed the damage was confined to the 4 edited paragraphs; rest of doc unchanged
11. `gdoc structure --account ... --quiet URL` — title paragraph now `NORMAL_TEXT`; FAQ link on ` FAQ` only
12. `gdoc edit ... "Northstar 2.1 release window — announcement draft (v3)" "# Northstar 2.1 release window — announcement draft (v3)"` — OK replaced 1 (title back to HEADING_1)
13. `gdoc edit ... "The release window opens" "The **release window** opens"` — OK replaced 1 (bold restored)
14. `gdoc structure ...` — verified both repairs
15. `gdoc edit ... "release window FAQ" "[release window FAQ](https://example.com/northstar/faq)"` — OK replaced 1 (link re-extended)
16. `gdoc structure ...` — verified
17. `gdoc edit ... "release checklist" "[release **checklist**](https://example.com/northstar/checklist)"` — OK replaced 1; `gdoc structure` verified bold inside link
18. `gdoc edit ... "the release window is not" "the *release window* is not"` — OK replaced 1; `gdoc structure` + `gdoc cat` showed italic restored but the "checklist" bold flattened again
19. `gdoc edit ... "<span from 'the release window is not' through 'release checklist'>" "the *release window* is not ... [release **checklist**](...)"` — OK replaced 1; `gdoc structure` + `gdoc cat | grep window` confirmed italic, checklist bold, FAQ link all present together

WHAT I CHANGED: Replaced all five case-sensitive occurrences of "launch window" with "release window" — the H1 title, the bold phrase under Key dates, the italic phrase in Ana's note, the FAQ link text, and the "If anything slips" sentence. "Launch Window banner" and "#launch" were left untouched. The Drive file name was not changed (it never contained the phrase). Then restored formatting the edit had stripped from those paragraphs: H1 style on the title, bold on "release window", italic on "release window", bold on "checklist" inside its link, and the FAQ link re-extended to cover "release window FAQ". Final `cat` matches the original text-for-text except for the five word swaps, and no other paragraph changed per the revision diff.

SUCCEEDED: yes — all five occurrences renamed with the product name preserved, and the collateral formatting loss was repaired and verified via `structure`.

CONCERNS:
- `gdoc edit` (even a plain word swap) rewrites the whole paragraph and drops bold/italic and paragraph style outside the match while keeping links, and it mis-anchored one link. It took 6 repair edits to undo. Anyone using `edit` on formatted paragraphs should expect this.
- The title is now `HEADING_1`. The original rendered as `# ` in `cat`, which is consistent with HEADING_1, but I couldn't confirm whether it was the Docs "Title" style instead — if it was, the style is close but not identical.
- The doc went through ~8 revisions instead of 1; version history will show the intermediate flattened states.
