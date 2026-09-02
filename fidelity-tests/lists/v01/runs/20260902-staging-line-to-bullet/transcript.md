# transcript — staging-line-to-bullet (agent track)

Agent: Claude Fable 5.1 via the Agent tool (general-purpose), gdoc 0.21.0. Given only the
request, the copy URL, the account to pass, "no browser", and told to cd into an empty scratch
directory and read nothing outside it (isolation by instruction; PWD reported as the empty directory).

## Agent's report (verbatim)

The trial answers the question. On the copy, `gdoc edit` did turn the line into a real bullet and dropped the typed dash, but it landed in a **new** list (`kix.ixlz9hhp8ggt`, ● glyph, 36 pt indent) — not the `-` list `kix.73yxf78mr7x1` at 108 pt that "Also a read replica" belongs to. Visually it sits at the far-left "Production" level with a round bullet, which is exactly what the colleague did not want. `gdoc edit` has no way to choose the target list or indent, and no other subcommand exposes native paragraph/list mutations (`structure` is read-only; `write`/`insert`/`push` rewrite whole tabs from markdown, which on this messy doc would risk far more collateral than the fix is worth). So I'm leaving the real document untouched.

PWD: /private/tmp/…/scratchpad/empty

COMMANDS:
- `gdoc --help` — listed subcommands; no native batchUpdate/list-mutation command exists.
- `gdoc cat --account A <URL>` — read the doc; found `\-<tab>Staging shares…` under Environments (banner: doc edited v5→v9 since last interaction, before I did anything).
- `gdoc structure --help` — confirmed it is read-only.
- `gdoc edit --help` — find/replace; replacement supports markdown bullets, no list/indent targeting.
- `gdoc structure --account … <URL> > structure.json` — "Also a read replica" is list `kix.73yxf78mr7x1` (glyph `-`, 108 pt) level 0; Staging line has no bullet, indent 108 pt, text `-\tStaging…`.
- `gdoc insert --help` / `gdoc write --help` — both whole-tab markdown uploads; too blunt for this doc.
- `gdoc cp --help` / `gdoc diff --help` — read options.
- `gdoc cp --account … <URL> "SCRATCH gdoc trial - staging bullet (safe to delete)" --json` — created scratch copy `10MPhYkV1H0qC-MSecmkBayO6faRmdiyb7zC6DIBMYE8`.
- `gdoc edit --account … --old-file old.txt --new-file new.txt --json 10MPhYkV1H0qC-…` — on the COPY only; `{"ok": true, "replaced": 1}`.
- `gdoc structure --account … --quiet 10MPhYkV1H0qC-…` — copy result: Staging is now a bullet but in new list `kix.ixlz9hhp8ggt` (●, 36 pt), not the sibling's list.
- `gdoc cat --account … --quiet 10MPhYkV1H0qC-…` — copy renders `* Staging…` (round bullet) beside `- Also a read replica…`.

WHAT I CHANGED: Nothing in the target document. I created one scratch Drive copy of it (title "SCRATCH gdoc trial - staging bullet (safe to delete)") and ran the candidate edit there to see what `gdoc edit` would produce.

SUCCEEDED: no — the gdoc CLI can only make the line a bullet in a fresh default list (● at 36 pt), not a bullet at the same level/list as "Also a read replica", so I left the doc unchanged rather than ship a visibly wrong result.

CONCERNS: The scratch copy remains in Drive because gdoc has no delete/trash command — it should be deleted by hand. The real doc showed edits by Alejandro Acelas (v5→v9) in the 18 minutes before I read it, so someone else may be working in it. If an approximate fix is acceptable (round bullet at top level, then re-indent by hand in the UI), the exact command is ready: `gdoc edit --account … --old-file old.txt --new-file new.txt <URL>` with `old.txt` = `-<tab>Staging shares the prod cluster, namespace staging (yes, really)` and `new.txt` = the same text prefixed `- `.
