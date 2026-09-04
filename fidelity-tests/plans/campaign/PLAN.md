# Campaign plan — implementation (revision 2, 2026-09-04)

Bound by `PRINCIPLES.md`. Revised after the Codex review in
`reviews/20260904-codex-plan-review.md`; each section notes what changed. Two phases: phase one
is small and produces a fix list; phase two (archive, hunters, exploration) runs only if phase
one leaves suspected fix families unexplored.

## Phase one — validated judge, small campaign, fix list

### 1. The case format and the runner

A case is a JSON file: `seed` (constructs built through the Docs API, including anchored comments
and pending suggestions via the preview surface), `command` (one gdoc command with `{DOC}`,
`{A}`, `{TAB}` placeholders; a short `sequence` of commands is allowed when the error needs
state), `assert` (the exact after-text of each target paragraph, the expected replacement count,
and the styles that must remain, by range), `target` and `allowed` (locators as today).

The runner, per case: create the document directly in the campaign folder (Drive
`files.create` with `parents`), seed in one `batchUpdate` where the API permits (text and
styles together; table cell fills batched in descending index order; footnotes need their
returned ids, so two calls), **read the seed back and check that every intended construct is
present**, capture before with one `documents.get` (all tabs, `SUGGESTIONS_INLINE`,
`commentsViewMode` via an authorised GET), run the command through the real CLI (`--quiet`
for the bulk sweep; a small cohort without it to exercise pre-flight), capture after, judge
in-process, write `result.json`. Outcome fields, independent of each other:
`completion` (assert met / not met / n-a), `collateral` (none / list of items with
visible-invisible flag), `command` (exit code and last line), `validity` (VALID / INVALID with
the failed gate). Every run gets a unique directory and unique temp files; nothing is reused.

Changed from revision 1: exact assertion instead of "an expected item exists"; seed read-back;
INVALID on any incomplete capture, malformed JSON or judge error; one capture call; runner reads
account and folder from environment variables with `config.yaml` as fallback so review checkouts
can run it.

### 2. The judge, and its calibration

`gdt-diff` stays the structural judge with these changes: comment anchors are mapped onto the
aligned text (anchor ranges survive normalisation as text spans, with tab and segment identity)
so a shrunk or orphaned anchor is an item; paragraph-level items inside the target are expected
only when the assertion names them; the requested-style rule matches the case's `assert`, not
free text. Before any sweep counts, a **calibration set** of about twenty cases runs: right text
in the wrong place, off-by-one replacement, missing style, moved anchor, edit in the wrong tab,
a known-clean change, an inserted paragraph, a deleted paragraph. False positives and false
negatives are recorded in `CALIBRATION.md` and the sweep does not start until both are zero on
that set. The visual judge is not used in phase one; PDF or browser images are captured for cards
only (see §5) and a sample of passes is checked by eye.

### 3. What to run

Not a Cartesian grid. A **constrained pairwise design** (NIST ACTS style) over:

- commands: `edit` (plain replacement; markdown replacement; `--all`; `--cell`; `--tab`;
  multi-paragraph via files), `suggest`, `insert` (start, end), `write` (whole doc, `--tab`),
  `push`, `comment --quote`, `reply`, `resolve`; `rename` and `mv` with metadata assertions;
  Sheets `cells` excluded;
- constructs near the match: bold / italic / strike / underline / small caps / highlight /
  colour / font / size runs; link; sub- and superscript; emoji or other non-BMP text before the
  match; tab and NBSP; heading styles; alignment, spacing, indent; bullet, numbered, checklist
  at levels 0–2, including a list that ends the tab; table cell (plain, merged, holding a list);
  footnote; header and footer; named range and bookmark; second tab; an anchored comment on or
  across the match; a pending suggestion on or next to the match; the same phrase twice in a
  paragraph;
- match position: paragraph start, end, spanning a run boundary, spanning two paragraphs,
  inside a comment anchor, inside a suggestion.

Inapplicable combinations are rejected before any call is spent. Target size: 60 to 100 cases
covering every pair of (command, construct) and (command, position) at least once, ordered so
that observed workflows (see §4) come first. Around five longer recorded sequences (two or three
commands on one document) are kept for state bugs such as damage masked by an earlier
flattening. Every case that fails is re-run once on a fresh seed before it is reported.

### 4. Relevance evidence (what "observed workflows" means)

Two sources, kept separate from the search corpus:

- **Genuine requests holdout.** Thirty to fifty real edit requests with their target context,
  collected in advance from sources to be agreed (candidates: gdoc's per-document state files,
  past Claude Code sessions, colleagues' asks), deduplicated by workflow and document, fixed
  before the sweep. Its completion and collateral rates are the only numbers presented as
  "what a user would see"; search yield is reported separately.
- **Document census** (private branch, read-only): a pilot of 30 to 50 documents stratified by
  owner (shared-with-me first, capped per owner), document type and recent use, excluding test
  and generated copies; then, if the pilot is informative, a few hundred. It counts constructs
  in edit-local windows and their co-occurrence, not document-level presence, and extracts
  skeletons whose neutral text preserves UTF-16 lengths, punctuation, repeated matches and run
  boundaries. URLs, identities and object metadata are sanitised explicitly. Percentages are
  reported as sample descriptions.
- **Intent census**: the agent transcripts we have (weighted down: the tasks were traps, the
  command choices are still informative), README and help, the issue tracker.

Search effort is split roughly 70% cases drawn from observed workflows and census skeletons,
20% constrained pairwise combinations, 10% free exploration. Ranking of findings uses coarse
frequency bands, severity (silent loss first) and detectability, not a product of two estimates.

### 5. Cards and the gallery

For each retained representative: before and after images of the lines that changed, including
the collateral, not only the target; one plain sentence; command, reply, case id. Images come
from a scripted browser capture (in progress: `gdt-shot-headless`) with PDF export as the
fallback only where a documented comparison shows the two agree; images are captured while the
disposable document exists and stored with the run. `gallery.html` is a static page generated
from the ledger, sorted by rank, with filters; no write-back until phase two.

### 6. Ledger, classification and the fix list

`ledger.jsonl`: one line per run (case id, seed hash, gdoc version, the three outcome fields,
validity, signature hint, provenance, natural-context reference). `FIXES.md`: one row per
suspected fix family, grouped by suspected code path in gdoc, with the minimal repro, the
natural-context case, evidence, severity and uncertainty. Classification (CLI-fixable,
CLI-missing, capability evidence for "no API surface", agent) is written per family with the
API method or its dated absence. Signatures are triage hints; two families merge only when one
fix is shown to resolve both. `LIMITATIONS.md` holds capability evidence with date, surface and
account, and the user-facing sentence.

### 7. Budget and pacing

Published Docs defaults: 60 writes and 300 reads per minute per user per project; configured
quotas are checked first. One dispatcher meters every request, including the CLI's, per
account and per API; retries quota errors with bounded jittered backoff; treats permission
errors and ambiguous write timeouts differently from safe retries. A paced pilot of 20 to 30
cases records endpoint counts, latency percentiles and throttles before the sweep. Planning
rate 10 to 20 mixed cases per minute; start with four workers. No personal-account spillover for
employer-derived seeds. Nightly cleanup trashes documents in the campaign folder older than a
day via the Drive API.

### 8. Phase one deliverables

`CALIBRATION.md`, the pairwise case set, `ledger.jsonl`, `FIXES.md` with one confirmed minimal
repro per family, `LIMITATIONS.md` (dated evidence), `gallery.html`, and a short report:
relevance-weighted coverage of the observed-workflow cases, holdout rates, and confirmed new
fix families per hour of API budget.

## Phase two — only if phase one leaves families unexplored

Archive keyed by (command, construct, position) with the smallest *and* the natural case per
cell; a seeded mutation queue (one change at a time from confirmed cases) rather than
MAP-Elites selection; hunting agents on API-generated documents given the empty high-relevance
cells as a wish-list, each ending by handing a description and a document id to a reducer that
applies delta debugging locally on the seed before confirming live; classifier agent over new
families. Stopping is by planned coverage plus one bounded expansion round, never by "three
duplicates in a row".

## References

Metamorphic testing (Chen et al. 2018, https://doi.org/10.1145/3143561) with explicit
preconditions per relation; differential testing needs an independent implementation, so a
small reference range-editor is the oracle for supported operations (McKeeman 1998,
https://www.cs.dartmouth.edu/~mckeeman/references/DifferentialTestingForSoftware.pdf; Csmith,
https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf). Reduction: delta debugging
(Zeller & Hildebrandt 2002, https://www.st.cs.uni-saarland.de/papers/tse2002/). Case design:
constrained combinatorial testing (NIST ACTS, https://csrc.nist.gov/projects/automated-combinatorial-testing-for-software).
Diversity archives for phase two: MAP-Elites (https://arxiv.org/abs/1504.04909), Rainbow Teaming
(https://arxiv.org/abs/2402.16822); Go-Explore and Evol-Instruct as inspiration only.

## Open decisions

- Source of the 30–50 genuine requests for the holdout.
- Whether phase two starts at all after phase one.
