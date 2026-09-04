# What adversarial review catches on gdoc

Seven pull requests on [LucaDeLeo/gdoc](https://github.com/LucaDeLeo/gdoc), 2026-08-07 to
2026-09-04, about 500 KB of review thread, read in full. Five kinds of reviewer appear:
[CodeRabbit](https://coderabbit.ai) (`coderabbitai[bot]`), the GitHub-native Codex bot
(`chatgpt-codex-connector[bot]`), external Codex audits the author ran and reported into PR
comments, local read-only Claude passes summarised in PR bodies, and humans. The two
questions: what do these reviews catch, and what do they use to check a claim against the
API spec or against Google's real behaviour.

## Bottom line

- **Reviews found about 80 real defects across the seven PRs, and 148 findings in total.**
  Codex (GitHub bot plus external audits) and the local Claude passes account for roughly 70
  of the real ones. CodeRabbit produced 46 findings and 7 real defects; a quarter of its
  findings were lint rules the repo does not enable, each withdrawn after the author cited
  `pyproject.toml`.
- **One defect class dominates: a write Google may have applied is reported as a failure.**
  Transport errors, 5xx, failed read-back, failed version lookup, failed state save, each
  turning a saved suggestion or comment into "No change was made" and inviting a duplicate
  retry. It appears at about 20 sites across PRs 53, 54 and 55, found one site per round
  across three reviewers, and the same helper was patched three times in PR 55. Nobody
  generalised it until the author wrote `_dispatch_native_write` late in PR 55.
- **The second class is account identity drifting mid-command.** PR 53 needed seven rounds
  (read, preview gate, write, read-back could each resolve a different account or token), and
  one fix introduced the next bug.
- **Spec reads and live probes caught what code reading could not.** A passing unit test was
  written to a list-shaped fixture for a field Google returns as a map; a commenter account
  received a `revisionId` Google documents as editors-only; the public Discovery document
  lacks the preview field the whole feature depends on. All three came from an external Codex
  audit reading the API reference or from the author's scratch-doc runs, never from CodeRabbit.
- **Nothing on the reviewer side ever ran against Google.** Every live check is author-side.
  PRs 56 and 58 have no live evidence at all, and PR 58 flips a sharing default on an uncited
  claim about Drive's behaviour (the claim is correct: the Drive v3 reference says
  `sendNotificationEmail` "defaults to `true` for users and groups").
- **One finding is still open in the code today.** Codex posted on PR 44 three minutes after
  merge that an array supplied for a scalar MCP option is expanded into argv tokens. Reproduced
  on the current tree: `account: ["work", "--force-collapse-tabs"]` on `gdoc_write` yields
  `['write', '--account', 'work', '--force-collapse-tabs', '--', ...]`, enabling the
  destructive flag.

## The seven PRs

| PR | Author | Reviewers present | Findings | Real defects | CodeRabbit real |
|---|---|---|---|---|---|
| [#53](https://github.com/LucaDeLeo/gdoc/pull/53) `gdoc suggest` | alejoacelas | CodeRabbit, Codex-GH, Codex-external ×2, Claude-local ×2 | 45 rows (52 items) | 30 | 0 |
| [#54](https://github.com/LucaDeLeo/gdoc/pull/54) suggestion threads | alejoacelas | Claude-local, Codex-external ×2, Codex-GH, CodeRabbit | 22 | 14 | 1 |
| [#55](https://github.com/LucaDeLeo/gdoc/pull/55) comment assignment | alejoacelas | Claude-local ×2, Codex-external, 3 closure audits, CodeRabbit, Codex-GH | 41 | 22 | 3 |
| [#56](https://github.com/LucaDeLeo/gdoc/pull/56) `?tab=` deep links | jpaddison3 | CodeRabbit, Claude swarm review | 18 | 3 | 3 (1 unanswered) |
| [#58](https://github.com/LucaDeLeo/gdoc/pull/58) share `--notify` | alejoacelas | CodeRabbit | 3 | 0 | 0 |
| [#44](https://github.com/LucaDeLeo/gdoc/pull/44) MCP server | peterhartree | Codex-GH, CodeRabbit, maintainer | 14 | 7 (+7 pre-PR) | 0 |
| [#52](https://github.com/LucaDeLeo/gdoc/pull/52) per-request credentials | LucaDeLeo | Codex-GH, CodeRabbit | 5 | 1 | 0 |

"Real defect" means the code would misbehave in use. Everything else is docs drift, lint,
wording, test hygiene or a design proposal. No human reviewer contributed a finding on any
of the seven; humans appear only as authors, fixers and rebutters.

## What the reviews catch

**1. Uncertain-outcome writes reported as failures.** The Docs preview API returns
`commentUpdateState` and per-request IDs; every step after the write can fail independently.
Reviewers found, one per round: `batchUpdate` transport exceptions
([#53 f9d5e92](https://github.com/LucaDeLeo/gdoc/commit/f9d5e92)), the read-back catching only
`GdocError`, 5xx on the batch inviting a retry that duplicates the suggestion
([#53 82c1238](https://github.com/LucaDeLeo/gdoc/commit/82c1238)), a failed Drive version lookup
hiding success, `update_state_after_command` raising on a full disk after the IDs were
printed, and in PR 55 `_read_back_threads` patched for `GdocError`
([bcf2978](https://github.com/LucaDeLeo/gdoc/commit/bcf2978)), then socket errors
([e7116bd](https://github.com/LucaDeLeo/gdoc/commit/e7116bd)), then `google.auth` refresh errors
([129c821](https://github.com/LucaDeLeo/gdoc/commit/129c821)). The `TransportError`
misclassification alone took three reviewers: the external audit said the gate did not classify
it, Claude found the fix mapped it to "Authentication expired" because `TransportError`
subclasses `GoogleAuthError`, and Codex found even that branch unreachable because
`get_credentials()` swallows it at `auth.py:55-61`.

**2. Account and credential identity across one command.** PR 53's chain: the gate proves
enrollment for project A and the write goes through project B after a token re-auth; `run_argv`
never pins the default account so a concurrent `gdoc auth --set-default` splits a command;
the fix's token-file stamp aborts on the gate's own legitimate refresh ("you were right that
the stamp comparison was the wrong identity"); comparing `client_id` alone lets a same-client
re-auth to a different user through; the identity is captured after the read instead of
before it. PR 52's single Codex finding is the same family: a service cache keyed on account
name keeps a removed account's token alive.

**3. Real API shapes versus assumed ones.** `Paragraph.suggestedPositionedObjectIds` is a
map keyed by suggestion ID, not a list; the unit test in PR 54 passed against a list-shaped
fixture until the second external audit read the `ObjectReferences` type. Deleted posts may
come back as `deleted: true` tombstones. `assigneeEmail` on a reassign lives on the new reply
post, not the head post (the author refuted a closure-audit claim with a live read-back plus
Google's `Post` reference). Overlap detection ignored `suggested*` fields on table, row and
cell containers and on `sectionBreak` and `tableOfContents` elements.

**4. UTF-16 versus code points.** Style ranges after an emoji, cleanup-position deltas, table
insertion indexes, `edit --cell` splitting a surrogate pair, and header/footer/footnote
suggestions emitted without the `segmentId` whose indexes restart at zero. Several of these
were pre-existing in shipped `edit` and `insert`, found while reviewing `suggest`.

**5. The MCP boundary as an injection surface** (Codex on PR 44). A truthy string `"false"`
enabling `--force-collapse-tabs`; `-` in `old_text` turning replace into delete; a
`![x](/tmp/private.png)` in inline text making `extract_images()` upload any server-readable
file; schemas listing `doc` as the only required field for tools that always need more; and
the still-open array expansion above.

**6. Docs drift.** CodeRabbit's real contribution: an epilog saying "Needs edit access" against
three other places saying comment access suffices; design records claiming the work shipped
in 0.20.0 when the release is 0.22.0; `gdoc.md` omitting two new commands; a docstring three
cutoffs out of sync with `state.py`. All found by cross-file reads with line citations.

**7. Noise.** MD022 (blank line after `### Added`) was raised on five of the seven PRs against
the CHANGELOG's own convention and withdrawn each time; the docstring-coverage gate failed on
all seven and nobody ever replied; Ruff B904, TRY003, ANN202, ARG001, SIM117 were raised though
the repo selects only `E, F, I, N, W, UP`. The "use `pytest-mock`" finding recurred on PRs 53,
56 and 58; the suite has 2197 `patch` calls and 31 `mocker.patch` calls in two files. The
rule CodeRabbit enforces is line 63 of the repo's own `CLAUDE.md`, which is wrong and which
no reviewer flagged.

## Which tools check against specs and reality

Reviewer side, roughly in order of how often they changed code:

- **Call-path tracing with a concrete payload** (Codex-GH). Named line ranges
  (`gdoc/auth.py:55-61`), exception hierarchies ("Neither is a `GdocError`, built-in transport
  error, or `httplib2.HttpLib2Error`"), and adversarial inputs (`force_collapse_tabs: "false"`,
  `account: ["work", "--force-collapse-tabs"]`). No commands shown; the evidence is the trace.
  This produced the most real defects per finding.
- **API reference and type reads** (Codex-external, Claude-local). `revisionId` documented for
  edit access only; `suggestedPositionedObjectIds` → `ObjectReferences`; `TransportError`
  subclasses `GoogleAuthError`. The only source of the API-shape class.
- **Diff read against the design docs** (Claude-local, pre-PR). PR 54's ten pre-review
  findings and PR 55's fourteen came from a whole-diff read against `03-cli-design.md` before
  any bot saw the code.
- **Cross-file consistency reads** (CodeRabbit). Design record versus CHANGELOG line 105, test
  docstring versus `state.py`, one code site proving a payload has null fields. The source of
  every docs-drift finding.
- **Sandbox scripts on the checkout** (CodeRabbit). `rg`, `ast-grep outline`, `git show`,
  `sed -n`, once an AST script proving every `lru_cache`d factory was reset. Used mostly to
  verify the author's rebuttals, and the AST script proved set completeness while missing the
  `None == None` early return in the same function that Codex found by reading.
- **Web queries against vendor docs** (CodeRabbit, once). Three queries against OpenAI's help
  pages established that ChatGPT desktop cannot launch a stdio MCP server. The only
  external-spec read by any bot, confirming a gap the PR body had already flagged.
- **Linters outside the repo's configuration** (CodeRabbit). markdownlint-cli2 and Ruff at
  default rule sets. Net negative.
- **A learnings database as the spec** (CodeRabbit). Rules distilled from `CLAUDE.md` drove
  the `maxsize=1` finding on PR 52, which asked to revert the PR's entire point; the author
  fixed `CLAUDE.md` and CodeRabbit stored a superseding learning. The bot's rule set is being
  edited through PR threads.

Author side:

- **Scratch-doc runs with three accounts and two Cloud projects** (registered `1009200210134`,
  unregistered `856825977485`; owner, commenter, reader). PR 53's evidence table has about
  thirty rows; PR 55's twenty. This is where Google contradicted its own documentation
  (commenters receive `revisionId`), where `Drive replyId == native postId` was established, and
  where the absence of tombstones in this project was recorded as a reason a branch is
  unit-test-only.
- **Raw HTTP where the Discovery document lags the API.** `commentsViewMode` is missing from
  the public Discovery document, so the discovery-built client raises "unexpected keyword
  argument"; the gate is an `AuthorizedSession` GET. Live probing also found the field requires
  `includeTabsContent=true` and `suggestionsViewMode=SUGGESTIONS_INLINE`.
- **Recorded error shapes as the classifier's spec.** 400 `Unknown name "comments_view_mode"`,
  400 `Invalid requests[0]: No request set.`, 403 `You do not have permission to access the
  document suggestions.`, each mapped to a specific user-facing message and a unit test.
- **A named regression test per finding and test counts after every push** (1510 → 1563 on
  PR 53, 1509 → 1738 on PR 55), plus Ruff counted against `main` rather than absolute.
- **Counting the codebase to rebut.** 26 `GdocError` raises without `from` in `docs.py`; 2086
  `@patch` versus 31 `mocker.patch`. Every such rebuttal was accepted within a minute.
- **An explicit not-live-tested list** in every author-run PR: merge-into-existing-suggestion,
  `ALL_FAILED_UNKNOWN_REASON`, unpinned reject for a commenter, header and footer suggestions.

Absent everywhere: any reviewer executing the code against Google, and any reviewer running
the test suite except the external Codex audit on PR 55.

## Process facts that shaped the record

- GitHub-native Codex answered "create a Codex account and connect to github" to every request
  from the author's account until 2026-09-02, so the audits ran externally and were reported
  into comments by hand. CodeRabbit skips draft PRs, allows one review per hour, and was
  rate-limited on most re-review requests, so its `CHANGES_REQUESTED` state often predates the
  fixes it complains about and the final commit of PRs 52, 54 and 56 was never reviewed by it.
- Fixes arrive one hole per round. Codex prefaces each with "Fresh evidence beyond the earlier
  fix"; the account-pinning chain and the read-back chain each ran to five or more rounds.
- Two bookkeeping gaps: PR 56's babysit summary reports "7 findings settled" and omits the
  outside-diff Major that `cmd_insert` never passes `written_tab_id`, so a second insert into
  the same tab is blocked as a conflict; PR 44's summary cites a CodeRabbit approval and eight
  Codex findings that the exported thread does not contain.
- Reviewers reversed each other on design in PR 55: the pre-implementation pass added a
  `suggest.` namespace guard, the whole-diff pass asked for an override to it, and the Codex
  audit had the heuristic removed.

## What would raise the yield

- Turn the dominant class into a closure-audit checklist rather than rediscovering it per
  site: for every native write, enumerate the steps after the send (read-back, version lookup,
  state save) and the exception families (`HttpError` 4xx, 5xx, socket and `httplib2`
  transport, `google.auth` refresh, `OSError`). PR 55's `_dispatch_native_write` and
  `TestDispatchFailureIsAmbiguous` (5 operations × 7 error kinds) are the template.
- Fix line 63 of `CLAUDE.md` to say `unittest.mock.patch`, and add a `.markdownlint.yaml`
  disabling MD022 or a `.coderabbit.yaml` path filter. Both would remove the two most repeated
  false positives at the source instead of through per-PR learnings.
- Add the missing test for list-valued scalar options in `gdoc/mcp.py` and reject them; the
  PR 44 payload still reconstructs a destructive flag.
- Require a live-evidence section, even a one-line "not run against Google", on every PR that
  changes a request or a default. PRs 56 and 58 show what a review looks like without one:
  cosmetic findings only, and the one behavioural claim adopted on the author's word.
- Ask each reviewer, after a finding, "where else does this pattern occur in the diff". The
  read-back and account-pinning chains suggest the bots can find the class when pointed at it
  but do not generalise unprompted.
