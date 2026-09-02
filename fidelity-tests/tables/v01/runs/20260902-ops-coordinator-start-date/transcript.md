# transcript — ops-coordinator-start-date (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/…/scratchpad/empty

COMMANDS:
- `gdoc --help` / `gdoc edit --help` — listed subcommands and edit options.
- `gdoc cat --account A <URL>` — read the doc; found the Hiring pipeline row "Ops coordinator (Madrid) | ... | Tomás; start 2 Sept 2026 (tbc)".
- `gdoc edit --account ... --case-sensitive <URL> "2 Sept 2026 (tbc)" "2 Sept 2026"` — ERR: no match found (exit 3).
- `gdoc cat --plain --account ... <URL>` (piped to grep/od) — plain export showed ordinary spaces in "start 2 Sept 2026 (tbc)", so the mismatch wasn't a character issue.
- `gdoc structure --account ... <URL>` — raw JSON showed the date "2 Sept 2026" is a date smart chip (one code unit, displayText "2 Sept 2026") followed by a separate text run " (tbc)\n"; that's why the first edit didn't match.
- `gdoc edit --account ... --case-sensitive <URL> " (tbc)" ""` — OK replaced 1 occurrence.
- `gdoc cat --account ... <URL>` (grep) — row now reads "Tomás; start 2 Sept 2026"; "TBC after the Q3 board" in the Head of People row untouched.
- `gdoc structure --account ... <URL>` — date chip still present at the same position with displayText "2 Sept 2026"; the " (tbc)" run is gone.

WHAT I CHANGED: In the Hiring pipeline table, the Ops coordinator (Madrid) "Owner & links" cell went from "Tomás; start 2 Sept 2026 (tbc)" to "Tomás; start 2 Sept 2026". Only the literal " (tbc)" text (with its leading space) was deleted; the date smart chip and everything else in the doc were left as is.

SUCCEEDED: yes — the "(tbc)" is removed and the date chip is intact, confirmed by re-reading both the markdown export and the raw structure.

CONCERNS: The first edit attempt failed harmlessly (no match, nothing written) because the date is a smart chip rather than plain text; the second, case-sensitive deletion matched exactly one occurrence, so the unrelated "TBC after the Q3 board" cell was not affected. The doc's pre-flight banner noted it had been edited by Alejandro Acelas (v5 → v10) in the preceding 23 minutes, so someone else may be actively working in it.
