# transcript — hyphen-date-fix (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/agent-hyphen-date-fix

COMMANDS:
1. `gdoc cat --account … URL` — read the doc; Key dates sentence had `**launch window**` bold and one plain-hyphen `14-18 Sept` (others were en/em dashes)
2. `gdoc edit --help` — learned `edit` does exact raw-text replace; `--normalize` would have matched dashes loosely, so I avoided it
3. `gdoc cat --plain --quiet --account … URL > before.txt` — saved raw snapshot; confirmed exactly 1 ASCII-hyphen `14-18 Sept`
4. `gdoc edit --account … URL "14-18 Sept" "14–18 Sept"` — `OK replaced 1 occurrence`
5. `gdoc cat --plain --quiet … > after.txt` + diff — text diff showed only the hyphen→en dash change
6. `gdoc cat --quiet … URL` (markdown view) — hyphen fixed, but `launch window` was no longer bold
7. `gdoc cat --quiet … URL | grep` — re-check; bold still gone (not export flakiness)
8. `gdoc --help` — found `structure`, `revisions`, `diff`
9. `gdoc structure --quiet … URL` — paragraph was now a single unstyled text run
10. `gdoc revisions --quiet … URL` — 2 retained revisions
11. `gdoc info --quiet … URL` — title "gdt-text-v01 run 20260902 hyphen-date-fix", owner Alejandro Acelas
12. `gdoc diff --help` — learned `--rev prev`
13. `gdoc diff --quiet --format plain --rev prev … URL` — rev1→rev2 showed exactly two changes: `14-18`→`14–18` (intended) and `**launch window**`→`launch window` (collateral from my edit)
14. `gdoc edit --quiet … URL "The launch window opens" "The **launch window** opens"` — `OK replaced 1 occurrence` (repair)
15. `gdoc cat --quiet … URL` (markdown) — `**launch window**` bold back, en dash in place
16. `gdoc cat --plain --quiet … > final.txt` + diff vs before.txt — only change is the hyphen→en dash
17. `gdoc structure --quiet … URL` — paragraph now three runs: `The ` (plain), `launch window` (bold), rest (plain)

WHAT I CHANGED: In the Key dates paragraph, replaced the plain hyphen in "14-18 Sept as the v2 draft said" with an en dash ("14–18 Sept"). The `14–18 Sept 2026` and `14—18 Sept` (em dash, "as the CMS rendered it") spans and the later `14–18 Sept` in the Copy section were untouched. I also re-applied bold to "launch window" in that same sentence, because my first `edit` call stripped it.

SUCCEEDED: yes — the requested en dash is in place, the document text is otherwise byte-identical to before, and the bold I accidentally removed has been restored.

CONCERNS: `gdoc edit` with a plain-text replacement flattened the whole paragraph's formatting (bold on "launch window", ~20 characters before the matched span, was lost), even though the matched text itself carried no formatting — that looks like a CLI bug worth filing against the fidelity suite. The repair used `gdoc edit` with markdown `**…**`, which restored bold, but I can only confirm the bold attribute itself; if "launch window" originally carried any other character styling I couldn't see in the markdown export (e.g. a colour or font), that would still be missing. The revision history also shows two edits rather than one.
