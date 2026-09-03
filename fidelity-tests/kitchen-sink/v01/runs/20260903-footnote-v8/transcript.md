# transcript — footnote-v8 (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

PWD: /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/batch-kitchen-sink-footnote-v8

COMMANDS:
- `gdoc --help` — listed subcommands.
- `gdoc cat --account … URL` — read doc; footnote renders as `[^1]:  Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás.`
- `gdoc edit --help` — edit is find/replace on raw doc text, supports `--tab`, `--cell`, `--normalize`.
- `gdoc edit --account … URL 'Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás' 'Finance sheet v8, tab “Q3”, pulled 2 Sept by Priya'` — exit 3, `ERR: no match found` (banner: doc edited by Alejandro Acelas v17 → v18).
- `gdoc cat --plain --account … URL` — confirmed the footnote's exact characters (curly quotes, precomposed á) match what I searched for.
- `gdoc structure --account … URL` — footnote exists as `kix.sodj60jamoog` with text ` Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás.\n`; it's in the footnotes map, not the body.
- `gdoc revisions --account … URL` — two milestones, both Alejandro Acelas (16:16, 16:47).
- `gdoc cat --account … URL` (twice more, diffed) — body content unchanged across the session.
- `gdoc edit --verbose --account … URL 'v7' 'v8'` — exit 3, `no match found` ("v7" appears only in the footnote, so this proves `edit` doesn't search footnotes).
- `gdoc edit --normalize --account … URL '…tab "Q3"…' '…'` — exit 3, `no match found`.
- `gdoc suggest --help` — same matching engine as `edit`, plus preview-only; not a fix.
- `gdoc write --help` / `gdoc push --help` — whole-document overwrite from markdown.

WHAT I CHANGED: Nothing. The footnote still reads "Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás."

SUCCEEDED: no — `gdoc edit` (and `suggest`) only match body text and cannot see footnote content, and the only commands that could touch the footnote (`write`/`push`) rewrite the entire document from markdown, which would put a table, tab-aligned status lines, strikethrough, checkboxes and link chips at risk for a one-line fix, so I left the doc untouched.

CONCERNS:
- This looks like a real gdoc gap: the Docs API `replaceAllText` request does replace inside footnotes, but gdoc's pre-match step scans only the body and returns "no match found" before calling the API. Adding footnote text to the matchable corpus (or a `--footnote` target) would make this request a one-liner.
- The pre-flight banner reported the doc moving v17 → v18 → v19 "edited by Alejandro Acelas" while I was working, yet `cat` output was byte-identical each time and none of my commands wrote anything. Either something else on this account is touching the doc concurrently, or the revision counter advances on non-content events; worth checking before trusting that version tracking for conflict detection.
- The MCP server `google-docs-preview-local` failed to connect; irrelevant here since the rules restricted me to the CLI, but noting it.
