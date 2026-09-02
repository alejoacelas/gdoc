# transcript — key-dates-en-dash-slip (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/agent-key-dates-en-dash-slip

COMMANDS:
- `gdoc cat --account … URL | cat -A` — pre-flight banner shown (doc edited by Alejandro Acelas, v5 → v10); output lost because macOS `cat` has no `-A` (my mistake, no doc impact)
- `gdoc edit --help; gdoc --help` — learned `edit` does raw-text find/replace, `--normalize` matches across dash variants, replacement supports markdown
- `gdoc cat --account … URL > before.md` — saved the markdown export; found the target sentence uses en dash / hyphen / em dash for its three ranges, and the old-plan paragraph also contains `14–18 Sept`
- `gdoc cat --plain --quiet --account … URL > before-plain.txt` — confirmed raw text `opens 14–18 Sept 2026` with plain spaces (no NBSP)
- `gdoc tabs --quiet --account … URL` — single tab (`t.0 Tab 1`)
- `gdoc edit --case-sensitive --account … URL 'opens 14–18 Sept 2026' 'opens 15–19 Sept 2026'` — `OK replaced 1 occurrence`
- `gdoc cat --account … URL > after.md` (+ diff vs before.md) — dates correct, but the export showed `**launch window**` had lost its bold
- `gdoc structure --quiet --account … URL > after-structure.json` — confirmed the paragraph had collapsed to one unstyled run; old-plan paragraph's bold/strikethrough intact
- `gdoc edit --case-sensitive --quiet --account … URL 'The launch window opens 15–19' 'The **launch window** opens 15–19'` — `OK replaced 1 occurrence`
- `gdoc cat --quiet --account … URL > final.md` (+ diff vs before.md) — the only difference from the original export is `14–18` → `15–19` in that one sentence
- `gdoc structure --quiet --account … URL > final-structure.json` — paragraph is now three runs: `The ` / `launch window` (bold) / rest; text byte-identical to original apart from the dates

WHAT I CHANGED: In the "Key dates" paragraph, the first sentence now reads "The **launch window** opens 15–19 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it." The "v2 draft" (hyphen) and "CMS" (em dash) examples are unchanged, and the struck-through old-plan paragraph ("the new plan is 14–18 Sept.") was not touched. I also re-applied the bold to "launch window", which the first edit had stripped.

SUCCEEDED: yes — the requested date change is in place and the final export differs from the original only in that one dash range, with the bold restored.

CONCERNS: `gdoc edit` dropped the bold on "launch window" even though the match started after it (at "opens"), so it appears to rewrite formatting beyond the matched span; I fixed it with a second markdown-formatted edit, but that is a CLI fidelity bug worth knowing about. I never saw a pre-edit structure dump, so my "unchanged" claims for the rest of the paragraph rest on the markdown export plus the raw-text export; both are byte-identical outside the dates. The document was already at revision v10 (edited 21 min earlier by Alejandro Acelas) when I started, in case that was unexpected.
