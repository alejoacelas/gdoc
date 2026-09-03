# transcript — launch-to-release-window (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/batch-text-launch-to-release-window

COMMANDS:
- `gdoc --help` — listed subcommands (edit, rename, structure, diff, revisions…)
- `gdoc cat --account … <doc>` — read the doc as markdown; 5 lowercase "launch window" (H1 heading, 3 body sentences, the "[launch window FAQ]" link text) plus 1 "Launch Window banner"
- `gdoc info --account … <doc>` — Drive title is "gdt-text-v01 batch 20260903" (no "launch window" in it), 352 words
- `gdoc tabs --account … <doc>` — single tab "Tab 1"
- `gdoc edit --help` / `gdoc rename --help` — learned `--all --case-sensitive` and markdown-aware replacement text
- `gdoc cat --plain --account … <doc>` — saved raw text; confirmed exactly 5 × "launch window" (plain spaces) and 1 × "Launch Window"
- `gdoc edit --account … --all --case-sensitive <doc> "launch window" "release window"` — OK replaced 5 occurrences
- `gdoc cat --plain --account … <doc>` — re-read; diff vs. before shows only the 5 intended word swaps, "Launch Window banner" untouched
- `gdoc cat --account … <doc> | grep window` — markdown showed two regressions: heading lost its `#`, and the FAQ link now covered only "FAQ"
- `gdoc structure --account … <doc>` — confirmed: title paragraph now NORMAL_TEXT; "release window" run unlinked, only " FAQ" linked
- `gdoc diff --help` / `gdoc revisions --help` / `gdoc cat --help` / `gdoc structure --help` / `gdoc export --help` — looked for a way to compare with the pre-edit state
- `gdoc revisions --account … <doc>` — two retained revisions (1 at 16:30, 17 at 17:16); 17 already includes my edit, so no retained snapshot immediately pre-edit
- `gdoc cat --account … --revision 1 <doc>` — older draft; confirmed heading was `# …` and link was `[launch window FAQ](…)`
- `gdoc diff --account … --rev 1 --format plain <doc>` — word-diff vs. rev 1 (exit 1 = differences); rev 1 is an older fixture state, so only useful as a rough check
- `gdoc edit --account … --case-sensitive <doc> "Northstar 2.1 release window — announcement draft (v3)" "# Northstar 2.1 release window — announcement draft (v3)"` — OK replaced 1 occurrence (restored heading)
- `gdoc edit --account … --case-sensitive <doc> "release window FAQ" "[release window FAQ](https://example.com/northstar/faq)"` — OK replaced 1 occurrence (restored full link anchor)
- `gdoc cat --account … <doc>` — final markdown is line-for-line identical to the pre-edit read except the 5 word swaps
- `gdoc structure --account … <doc>` — title paragraph is HEADING_1 again; "release window FAQ" is one run linked to the FAQ URL; other links, headings and runs unchanged

WHAT I CHANGED: Replaced all five lowercase "launch window" with "release window" in the single tab: the H1 heading ("Northstar 2.1 release window — announcement draft (v3)"), the three sentences in "Key dates and labels", and the FAQ link text. Left "Launch Window banner" as is. The Drive file title never contained the phrase, so it was not renamed. After the bulk replace I repaired two side effects it introduced: reapplied Heading 1 to the title paragraph and re-extended the FAQ hyperlink to cover the whole phrase "release window FAQ".

SUCCEEDED: yes — all five instances are renamed, the product name is untouched, and the final export and structure match the original apart from the word swaps.

CONCERNS: `gdoc edit --all` dropped the title paragraph's heading style and stripped the hyperlink from the replaced link text; I restored both, but I restored the heading as HEADING_1 (what the markdown `#` implied) and cannot rule out that it was originally the "Title" style, since there is no retained revision from immediately before my edit and `structure` has no revision option. Nothing else in the doc changed.
