# REPLICATE

A readable record of what substantial agent sessions accomplished in this repo.

## Test suite report (2026-09-04)

Alejo wanted a report covering every test group in the repo, at class level, with the live fidelity suite included, committed as Markdown.

- Wrote `docs/TESTS.md`: one line per test class (334 classes across 55 pytest files, grouped by layer) stating the behaviour it guarantees, a per-file note on what is mocked, and a section on the fidelity suite (fixtures, the run pipeline, verdict rules, results as of 2026-09-03, harness limits).
- Verified every class name and test count against the source with `ast`, and that the file set matches the `fidelity-tests` branch.
- The working checkout was switched to another branch by a concurrent session mid-task, so the report was written and committed from a separate worktree of `fidelity-tests`.

Agent session a5c5713c-45aa-43b0-87ad-00c0d88aeae7 · Commits f0f3704
