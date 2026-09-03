# transcript — key-dates-en-dash-slip (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/batch-text-key-dates-en-dash-slip

COMMANDS:
- `gdoc --help` / `gdoc edit --help` — listed subcommands; confirmed `edit` matches raw text exactly unless `--all`/`--normalize` is passed.
- `gdoc cat --account A <doc>` (piped to `cat -A`) — failed locally (`cat -A` is not available on macOS); no doc change; pre-flight banner noted the doc was at v27.
- `gdoc cat --account A <doc> > before.md` — exported markdown, 31 lines.
- `gdoc cat --plain --account A <doc> > before.plain.txt` — exported matchable raw text; showed the first sentence has "14–18 Sept 2026" (en dash + year) once, while the v2 example ("14–18 Sept", en dash, no year), the CMS example ("14—18 Sept", em dash) and the old-plan line ("The new plan is 14–18 Sept.") all lack the year.
- `gdoc edit --account A <doc> '14–18 Sept 2026' '15–19 Sept 2026'` — "OK replaced 1 occurrence".
- `gdoc cat --plain --account A <doc> > after.plain.txt` then local `diff` — only line 6 differs, and only in the first date range.

WHAT I CHANGED: In the "Key dates and labels" paragraph, the opening sentence now reads "The launch window opens 15–19 Sept 2026, not 14–18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it." The v2 and CMS examples kept their original text and dash characters (en dash and em dash respectively), and the "The new plan is 14–18 Sept." paragraph further down is untouched.

SUCCEEDED: yes — a single exact-match replacement changed only the dated range in the first sentence, verified by a before/after diff of the document text.

CONCERNS: none of substance. The new range uses the same en dash (U+2013) as the original, so the formatting is consistent. The pre-flight banner said the doc had been edited (v26 → v27) 37 seconds before my first read, so someone else was in the doc moments earlier; my export was taken after that revision, and the diff confirms my edit is the only difference since then. I did not verify character formatting (e.g. bold/link runs) beyond plain text, but `edit` replaces text in place within a single run so formatting should be preserved.
