# Principles for the gdoc error-hunting campaign

These do not change during a run. Implementation choices live in `PLAN.md` and may be argued
with, replaced or dropped; a change that violates one of these is not an implementation detail.

1. **The document is the oracle.** A test passes or fails by comparing the raw document before
   and after (the Docs API representation, with suggestions and comments included), never by
   what the tool or the agent reports about itself.

2. **Success is asserted, not inferred.** Every case states exactly what the target must read
   afterwards. A run reports three separate facts: was the requested change made exactly, did
   anything else change, did the command fail. None of them is derived from another.

3. **Everything outside the declared target is protected.** Any difference outside the target
   is collateral, whether or not a reader would notice it, and whether or not it looks harmless.
   Allowed side effects are declared before the run, per case, never after.

4. **A judge must be calibrated before it is trusted.** Before a judge's verdicts count, it is
   fed known-wrong outcomes (wrong text, missing style, moved anchor, edit in the wrong place)
   and known-clean changes, and its false-positive and false-negative rates are recorded. A
   judge that cannot see a class of damage says so in its output rather than reporting clean.

5. **A failed measurement is invalid, not a pass.** A capture that did not complete, a seed that
   does not contain the intended construct, a judge that crashed, a stale result: each yields
   INVALID and is excluded from every rate.

6. **Every finding is reproducible from the repository alone.** A case is a seed built through
   the API, one command (or a short recorded sequence), and an assertion. Documents in Drive are
   disposable; the repository holds the case, the exact requests sent, the tool version and
   output, and the raw before/after captures, so any card, verdict or rate can be regenerated.

7. **Minimal and natural are kept together.** Each error is stored as the smallest case that
   reproduces it *and* the natural context it was first seen in. Minimality never erases the
   evidence that the error matters.

8. **Relevance ranks, exploration finds, and the two are reported separately.** Search may be
   as adversarial and diverse as it likes; what is reported to users and fixed first is ordered
   by evidence about real documents and real requests. A rate estimated from an adaptive search
   is never presented as the rate a user would experience; that needs a fixed sample chosen in
   advance.

9. **Duplicates are decided by cause, not by appearance.** Two cases are the same error only
   when one fix is shown to resolve both. Until then, contrasting repros are kept.

10. **Capability claims carry evidence and a date.** "The API cannot do this" is recorded with
    the API surface, account and date it was tested against, and can be overturned. Unknown
    stays unknown and does not stop hunting.

11. **The tool under test is the one on `main`.** Runs are pinned to a recorded gdoc version;
    findings against older versions are re-run before they are reported as current.

12. **Nothing in the campaign edits, copies, shares or comments on a document it did not
    create.** Documents containing other people's content stay on a private branch and never
    enter a Google Doc, a public remote or a card.

13. **Rate limits are the budget and are spent where they teach something.** Requests are
    metered centrally, including those made by the CLI under test; a case that cannot produce a
    new fact is not run.

14. **A person can review a finding in ten seconds.** Every reported error has a before image,
    an after image and one plain sentence saying what was asked and what happened instead.
