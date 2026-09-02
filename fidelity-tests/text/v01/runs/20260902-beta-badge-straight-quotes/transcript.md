# transcript — beta-badge-straight-quotes (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/agent-beta-badge-straight-quotes

COMMANDS:
1. `gdoc --help` / `gdoc edit --help` — learned `edit` matches raw text, is quote-strict unless `--normalize`, and accepts markdown in the replacement.
2. `gdoc cat --account … URL` — read the doc; Key dates paragraph has curly `“beta” label` and straight `"beta"  badge` (bold on "launch window").
3. `gdoc cat --plain --account … URL` — confirmed byte-exact: straight-quoted `"beta"` occurs exactly once in the whole doc.
4. `gdoc edit --account … --case-sensitive URL '"beta"' '"preview"'` — `OK replaced 1 occurrence`.
5. `gdoc cat --account … URL` + diff vs. before — text change correct, but the export showed `**launch window**` had lost its bold.
6. `gdoc structure --account … URL` — confirmed: the whole Key dates paragraph had collapsed into one text run with no bold (collateral from the edit).
7. `gdoc edit --account … --case-sensitive URL 'The launch window opens' 'The **launch window** opens'` — `OK replaced 1 occurrence` (restoring the bold).
8. `gdoc cat` + `gdoc structure` again — diff vs. before is now exactly one word (`"beta"` → `"preview"`) and the paragraph is three runs again: `The ` / `launch window` (bold: true) / rest, matching the original.

WHAT I CHANGED: In the Key dates paragraph, the straight-quoted `"beta"` before "badge" now reads `"preview"`. Marta's curly-quoted `“beta” label` is untouched, as are "Beta badge" in the Open items table and "beta badge" in the open question. I also re-applied bold to "launch window" in that paragraph after the first edit stripped it.

SUCCEEDED: yes — the requested word is changed and the markdown export of the doc differs from the before snapshot only in that one word.

CONCERNS: The `edit` command flattened the entire paragraph's inline formatting when it replaced one word — it removed the bold on "launch window", which I only caught by diffing before/after and inspecting `structure`. I restored the bold, but I had no pre-edit `structure` snapshot, so any formatting in that paragraph invisible to the markdown export (font, colour, size differences) could have been lost without my noticing. The stray double space in `"preview"  badge` was already there before and I left it. Also, `gdoc cat` reported the doc had been edited by Alejandro Acelas v5→v10 in the 25 minutes before I started — someone else was working on it recently.
