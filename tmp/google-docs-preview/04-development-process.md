# Develop the preview PRs like recent `gdoc` PRs

Use the recent feature-PR loop, not the original six-phase milestone sprint. The
closest precedent is [PR #40](https://github.com/LucaDeLeo/gdoc/pull/40): Claude Code
implemented the preview endpoint, tests exercised the documented and observed error
shapes, and Codex plus CodeRabbit found correctness bugs before merge. Preserve the
older sprint's useful rule: a second model challenges the design before code and the
implementation after tests.

## What the repository proves

There are two development histories in the repo.

| Period | Evidence | Process we can establish |
| --- | --- | --- |
| Initial v1 build, 7–8 February 2026 | `.planning/MILESTONE-SPRINT.md`, phase plans, summaries, verifications, and Claude/Codex transcripts | `/gsd:milestone-sprint --yolo` ran six phases in 6h 3m. Claude proposed, planned, and implemented; local Codex challenged decisions and reviewed each phase; Claude subagents executed independent plans in parallel. |
| Recent feature work, August 2026 | PR descriptions, commit trailers, review threads, and test reports | Claude Code produced the initial changes. GitHub Codex and CodeRabbit reviewed the PR. Claude Code produced named review-fix commits. The author replied to or rejected each finding, reran checks, and requested another review. |

The evidence does **not** contain the initiating prompts or a transcript of the recent
Claude Code sessions. It proves Claude Code authorship through `Co-Authored-By`
trailers and “Generated with Claude Code” PR footers, but it does not prove that those
sessions used subagents. Do not describe the recent PRs as swarm-built.

### The original autonomous build

The project-local [`gsd:milestone-sprint`](../../.claude/skills/gsd-milestone-sprint/SKILL.md)
skill is a bash-controlled Claude Code workflow. It was triggered as a slash command:

```text
/gsd:milestone-sprint --yolo
```

For each phase it:

1. ran a Claude–Codex design discussion and wrote `CONTEXT.md`;
2. used research and planner agents to write dependency-ordered `PLAN.md` files;
3. used `gsd-executor` subagents to execute independent plans in parallel waves;
4. ran a `gsd-verifier` against the working code, not the summaries;
5. invoked local Codex in read-only mode at the plan and implementation boundaries;
6. committed each plan and the planning record, then moved to the next phase.

The shell loop held little context itself; durable state lived in `.planning`. Fresh
subagents received one bounded plan each. Phase 5 shows the resulting audit trail:
[`CONTEXT.md`](../../.planning/phases/05-phase-05/CONTEXT.md) records which Codex
objections Claude accepted, which it rejected, and why; `05-01-SUMMARY.md` records the
implementation and its tests.

This machinery is reproducible in Claude Code because the skill and scripts remain in
the repo. It is not ready to rerun unchanged for the preview work:

- `.planning/MILESTONE-SPRINT.md` says the v1 milestone is complete;
- `.planning/STATE.md` is stale at phase 2 even though the sprint record is complete;
- the local Codex wrapper defaults to the historical `gpt-5.2-codex` model name;
- the workflow is organized around a whole milestone, while each proposed preview PR
  should be independently reviewable.

Starting it now would require defining a new milestone, reconciling the planning
state, checking its model configuration, and accepting its automatic commits. That is
more machinery than these PRs need.

### The recent PR loop

[PR #40](https://github.com/LucaDeLeo/gdoc/pull/40) is the closest analogue because it
added `insertComment`, the first Docs Developer Preview request in `gdoc`.

1. The initial Claude Code commit added the API wrapper, CLI behavior, documentation,
   and 19 tests. The PR reported 1,232 passing tests and a live test with a project
   that lacked preview access.
2. GitHub Codex and CodeRabbit reviewed the first commit. They found tab loss, Python
   versus UTF-16 index drift, and missing revision protection.
3. A second Claude Code commit fixed the valid findings and added focused regression
   tests. The author summarized each accepted change in the PR and explained why
   style-only suggestions were not adopted.
4. Both automated reviewers ran again; CodeRabbit approved before merge.

The pattern repeats in later work:

- [PR #41](https://github.com/LucaDeLeo/gdoc/pull/41) used an initial feature commit,
  two review-fix commits, full-suite reports, and live tests.
- [PR #42](https://github.com/LucaDeLeo/gdoc/pull/42) needed several small review-fix
  commits as reviewers found state-baseline, shared-drive, pagination, and move-edge
  cases.
- [PR #44](https://github.com/LucaDeLeo/gdoc/pull/44) was reviewed through four Codex
  rounds and CodeRabbit until both found no remaining major issue. Its final comment
  records the resolved threads and verification results.
- [PR #52](https://github.com/LucaDeLeo/gdoc/pull/52) separated the initial change, a
  Codex cache-correctness fix, and CodeRabbit test/readability fixes. One CodeRabbit
  suggestion was rejected because it described the architecture being replaced; the
  PR records that reasoning rather than accepting it mechanically.

Review could be triggered from the GitHub thread:

```text
@codex review
@coderabbitai review
```

The repository's Codex integration also reported that review runs when a PR is opened
or a draft becomes ready. Manual triggers were used after fixes. CodeRabbit sometimes
rate-limited repeat requests, so its stale review state was not treated as evidence
that an addressed finding remained valid.

No `.github/workflows` files are present. The recorded gates were run locally and
reported in PR descriptions or comments. We should not assume GitHub Actions will
catch a skipped test or lint command.

## What we know well enough to implement

The codebase conventions and ordinary Google API mechanics are well established:

- command parsing and orchestration belong in `gdoc/cli.py`;
- Docs request wrappers and `HttpError` translation belong in `gdoc/api/docs.py`;
- range writes start with a tab-aware read, use UTF-16 offsets, and carry revision
  protection;
- terse, plain, and JSON output are interfaces covered by tests;
- state updates distinguish a partial write from a full read;
- unit tests mock exact request and response bodies, then the full suite guards shared
  behavior;
- live smoke tests have caught server behavior absent from the published schema.

The uncertain part is the preview API's live behavior, not where the code belongs.
Each PR must resolve its own uncertainty before merge:

| PR | Known from schema and current code | Must be established empirically |
| --- | --- | --- |
| `suggest` | `writeMode: SUGGEST`, suggestion response IDs, inline suggestion reads, current replacement planner | whether an editor and a commenter receive `revisionId`; behavior without it; exact created-versus-updated IDs; overlap/merge behavior; whether every inline style request remains suggested |
| suggestion decisions | request/response shapes and native thread summaries | list/decision status transitions; read-after-write timing; range annotations keyed by suggestion ID; delete authorship rules |
| native comment posts | insert, reply, update, delete request shapes | assignment and reassignment preconditions; ID stability; pagination/tombstones; coexistence with Drive comment reads |

Unit tests can prove our handling of documented shapes. They cannot prove that a
registered project receives those shapes or that the Docs UI exposes the intended
review object. That requires the registered and unregistered project tests in
[the access plan](02-access-tests.md).

## Process for each preview PR

Run this loop separately for each PR. Do not place all three features on one branch.

### 1. Establish the contract

Branch from the latest `origin/main`. Copy the relevant section of
[the CLI design](03-cli-design.md) into an issue or short PR-local plan and turn every
unknown into either a pre-merge live test or an explicit v1 limitation.

Before editing code, ask an independent reviewer to check only the contract. A useful
prompt is:

```text
Read 01-preview-api.md, 02-access-tests.md, 03-cli-design.md, and the current gdoc
implementation. Find cases where this PR could directly mutate a document, report
success without a durable review object, lose a tab or UTF-16 coordinate, or violate
an existing CLI/state contract. Cite files and propose a test for each finding. Do
not edit files.
```

This is the lightweight equivalent of the old Claude–Codex `CONTEXT.md` discussion.
Record accepted and rejected findings in the plan before implementation.

### 2. Implement one vertical slice

One primary agent owns the branch and integration. It should make the API wrapper,
CLI command, output, state behavior, tests, and user documentation coherent in one
initial commit. Delegate only bounded read-only questions; parallel agents editing
`gdoc/cli.py` or shared state will create more integration work than they save.

For `suggest`, a useful three-role setup is:

| Role | Bounded responsibility | Output |
| --- | --- | --- |
| Primary implementer | shared replacement refactor, API call, CLI, tests, docs | working branch and commits |
| Preview-schema reviewer | compare requests, response IDs, comments state, and live probes with the official schema | findings with exact missing tests; no edits |
| `gdoc`-invariants reviewer | inspect tabs, UTF-16, revision control, output, awareness state, and failure atomicity | findings with file references; no edits |

The primary agent resolves both reviews and remains responsible for the result. This
matches the original sprint's independent challenge without splitting ownership of
the central code path.

### 3. Test locally before opening the PR

For `suggest`, run at least:

```bash
uv run pytest tests/test_suggest.py tests/test_edit.py tests/test_api_docs.py -v
uv run pytest tests/ -v
uv run ruff check gdoc/ tests/
bash scripts/check-no-stubs.sh
```

Then run disposable-document probes in this order:

1. registered editor: create, read back, inspect in the Docs UI, accept/reject;
2. registered commenter: repeat and record whether `revisionId` is present;
3. unregistered project: send a harmless probe and record the exact rejection;
4. rerun ordinary `edit` and comment smoke tests to detect regressions.

Use new documents containing a second tab, an emoji before the target, inline
formatting, and an existing suggestion. Save redacted request/response shapes and UI
observations in the PR. Delete scratch documents only after the results are recorded.

### 4. Open a draft PR with evidence

The recent PR descriptions consistently include:

- the user-visible contract and fallback behavior;
- files and architectural choices;
- issue or design link;
- focused and full-suite test counts;
- live test identity and capability status without credentials;
- what was not live-tested;
- screenshots only when they prove a UI state the API response cannot.

Keep the first commit reviewable. Do not mix release-number conflict resolution or
unrelated cleanup into the implementation commit.

### 5. Use two independent review passes

Request GitHub Codex and CodeRabbit review. Treat every finding as a hypothesis:

1. reproduce or trace it against current code;
2. add a regression test when it is a behavior bug;
3. fix valid findings in a named review commit;
4. reply with the commit and test;
5. reject invalid findings with the conflicting code, API rule, or design constraint;
6. request another review after the fixes;
7. repeat until there is no unresolved correctness finding.

Before submission to the maintainer, ask one fresh local reviewer to inspect the
whole diff rather than the earlier plan. Its prompt should emphasize silent direct
edits, partial multi-batch writes, success criteria, permissions, and state baselines.
This final pass is important for preview work because both the schema and the intended
failure mode differ from normal Docs mutations.

### 6. Hand off a reproducible result

The final PR comment should contain:

- exact commands and passing counts from the final commit;
- registered-editor, registered-commenter, and unregistered-project results;
- every review finding and its resolution;
- remaining limitations and the issue that tracks each one;
- confirmation that no fallback performed a direct edit;
- the commit reviewed by each automated reviewer.

Then request maintainer review. Do not ask the maintainer to discover unresolved API
behavior that we can test with the enrolled project ourselves.

## How to trigger the available setups

### Recommended: current Codex session plus independent reviewers

Give the primary Codex session the chosen PR section from `03-cli-design.md` and ask it
to implement, test, red-team, commit, push, open a draft PR, and babysit reviews. Ask
explicitly for read-only subagents at the design and final-diff gates if the runtime
does not create them automatically. This reproduces the separation of roles without
depending on the stale milestone state.

### Faithful recent setup: Claude Code plus GitHub reviewers

Start Claude Code in the repo, give it the same end-to-end task, and require the local
test and live-probe gates above. After it pushes a draft PR, trigger `@codex review`
and `@coderabbitai review`. This most closely matches PRs #40–#52.

### Full historical setup: GSD milestone sprint

Use this only if the preview work becomes a multi-phase milestone rather than three
small PRs. First create a new roadmap milestone and repair `.planning/STATE.md`; then
verify the model in `.claude/skills/codex-oracle/scripts/ask_codex.sh`. In Claude Code:

```text
/gsd:milestone-sprint --yolo
```

For a preplanned range, the narrower command is:

```text
/gsd:sprint START END --yolo
```

Both run in tmux, persist resumable state under `.planning`, halt on auth or critical
review failures, and can be resumed with `--resume`. Do not run them against the
completed v1 planning files without establishing a new milestone.

## Recommended sequence here

1. Implement `suggest` with one primary agent and two read-only design reviewers.
2. Complete the registered editor/commenter and unregistered project matrix before
   opening the PR as ready for review.
3. Open a draft, run GitHub Codex and CodeRabbit, fix and retest until both have seen
   the final commit.
4. Ask Luca for review only after the evidence and remaining limitation list are in
   the PR.
5. Use the same loop for suggestion decisions, then native comment posts.

This is not guesswork about a new house style. It is the process visible in the
project's original planning record and its most recent merged feature PRs, reduced to
the parts that fit a small, high-risk preview change.
