# gdoc fidelity tests — manual review

One section per fixture. The fixture link is the frozen original (the "before" of every run); each bullet is one run: the edit as the agent was asked for it, the recorded outcome, and the edited copy to open beside the original. Details per run live in the repo under `fidelity-tests/<fixture>/runs/<run>/` (transcript, diff, verdict, screenshots).

## Start here: painted review copies

One document per fixture with all of that fixture's edits applied in sequence, then painted: green = the change a task asked for, red = collateral, amber = allowed side effect, red left border = paragraph style changed; a numbered comment T1… per task sits where it edited; a header at the top lists the tasks and outcomes and links the unpainted copy.

- **collab/v01** — https://docs.google.com/document/d/15guE3nrWCQqyz_voMato0k7yKdyRzhukzs182Lu6V80/edit — 5 edits: 3 COLLATERAL, 2 DONE
- **kitchen-sink/v01** — https://docs.google.com/document/d/18lMyyYyB0n2lYA-typ4_LaIo6UGzRCoqTYDbw7Sfgew/edit — 7 edits: 2 COLLATERAL, 4 DONE, 1 GAP-CLI
- **lists/v01** — https://docs.google.com/document/d/1C_cW3_cHTPO9U3kRocHHR61POUSa_4CpzkCj1r3PRso/edit — 12 edits: 5 COLLATERAL, 1 DECLINED-API, 5 DONE, 1 FAIL-AGENT
- **tables/v01** — https://docs.google.com/document/d/1ROv2UtcrrIx2OZer0B54P3OYLiFH-nl5H-7QOazdPHM/edit — 11 edits: 1 COLLATERAL, 9 DONE, 1 GAP-CLI
- **text/v01** — https://docs.google.com/document/d/1QgeTu7gHOcrZdIfHwv7KrkNVBz8WodXx8vjyTCwlkgg/edit — 11 edits: 8 COLLATERAL, 3 DONE

## collab/v01

Fixture (before): https://docs.google.com/document/d/16-VPn1wWF0ZmyWtlF8JbAq8qxJlfgiT71GNfjPcs00w/edit

Batch `20260903-batch` (5 edits in sequence on one copy): run copy https://docs.google.com/document/d/1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4/edit · **painted review copy** https://docs.google.com/document/d/15guE3nrWCQqyz_voMato0k7yKdyRzhukzs182Lu6V80/edit

- **handbook-link-notion** — The finance handbook link points at the old handbook — change it to https://www.notion.so/people-ops/expenses. Keep the wording.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1tjP_VgAfXiWKrRDrl0cByrP_7Qve9hrlhfvyQQayW-o/edit
- **handbook-link-notion** [batch 20260903-batch] — The finance handbook link points at the old handbook — change it to https://www.notion.so/people-ops/expenses. Keep the wording.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4/edit
- **next-review-september** — The next review isn't June any more, it's September — fix the last line.
  - Outcome: **DECLINED-API** · edited copy: https://docs.google.com/document/d/1EFNaYQbifeqD537t9dmho7geEcZbZPzPuCGsltTVv2g/edit
- **next-review-september** [batch 20260903-batch] — The next review isn't June any more, it's September — fix the last line.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4/edit
- **reopen-three-forms** — Someone resolved the comment about "three forms" but the text now says four — reopen that comment and reply "Reopening: the paragraph now says four forms, is that right?"
  - Outcome: **INVALID** · edited copy: https://docs.google.com/document/d/1txCEE5AxJbnBEWQeQ7MJF0Ou0Yl1-dRoDJ7fZP3v7es/edit
- **reply-broadband-thread** — On the broadband comment thread (the one about £15 being too low), add a reply saying "Agreed, going with £25 — finance signed off on 3 Sept." Don't resolve it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/15zKoeYqIQMuFqJ6k1h3SWYwfGqng41FeAr7Q3LdEQs8/edit
- **reply-broadband-thread** [batch 20260903-batch] — On the broadband comment thread (the one about £15 being too low), add a reply saying "Agreed, going with £25 — finance signed off on 3 Sept." Don't resolve it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4/edit
- **resolve-fake-heading-comment** — The "What changes" line is fine as it is — resolve the comment that asks to make it a real heading, with a short reply "Leaving as is for v3."
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1_ZF9_ODEESn_A316ORMLVlr8QUmkiNgPUkg1ZmQjX-U/edit
- **resolve-fake-heading-comment** [batch 20260903-batch] — The "What changes" line is fine as it is — resolve the comment that asks to make it a real heading, with a short reply "Leaving as is for v3."
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4/edit
- **suggest-contractors-sentence** — In Open questions, add — as a suggestion, not a direct edit — the sentence "Legal will confirm by 15 Sept." at the end of the contractors paragraph.
  - Outcome: **GAP-CLI** · edited copy: https://docs.google.com/document/d/1i-5K3a9a0NsGiq9pCi87QqULKRJ_FuTYxKDlIVtk1Vs/edit
- **suggest-contractors-sentence** [batch 20260903-batch] — In Open questions, add — as a suggestion, not a direct edit — the sentence "Legal will confirm by 15 Sept." at the end of the contractors paragraph.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4/edit

## kitchen-sink/v01

Fixture (before): https://docs.google.com/document/d/1uqR5yBhTMYu-3qfJ9JibyJn9NJD7RZEiCMLnQngTB9g/edit

Batch `20260903-batch` (7 edits in sequence on one copy): run copy https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit · **painted review copy** https://docs.google.com/document/d/18lMyyYyB0n2lYA-typ4_LaIo6UGzRCoqTYDbw7Sfgew/edit

- **add-open-question** — Add one more open question at the end of Tomás's list: "Do we need a rollback drill before the 15th?"
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/11lWl1NRjf1Yh5ypjPGwL4Bzl71OaZrhzYAG9XjLEHaE/edit
- **budget-cloud-credits** — In the budget table, the cloud credits line should say $12,900 now, not $12,400. Please update it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1GnVEZoRVxJwtB6L-eEtAOj-EhQXps-WYX1io6mfV59E/edit
- **fix-double-numbering** — In Tomás's open-questions list, items 2 and 3 show their number twice ("2) 2)", "3) 3)"). Remove the typed duplicates so the list just reads 1) 2) 3).
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/14LWsMKgyxKJJ_U1MswfFbROe_LgUwA2OGZnWi-_sRwo/edit
- **footnote-v8** — The footnote at the bottom still says Finance sheet v7 pulled 28 Aug by Tomás. It's v8 now, pulled 2 Sept by Priya. Please fix the footnote.
  - Outcome: **GAP-CLI** · edited copy: https://docs.google.com/document/d/1hfZ7nXKoxXOr24S2_V8mFY6oh0uiIDnf7h_vzdLLItw/edit
- **next-steps-effort** — Under Next steps, the estimated effort is now 4 dev-days, not 3. Can you change that?
  - Outcome: **INVALID** · edited copy: https://docs.google.com/document/d/1E_H_KY4SDzwLtUtou_JHJRKV3JRbO90b7mbN7zOwJOg/edit
- **next-steps-effort** — Under Next steps, the estimated effort is now 4 dev-days, not 3. Can you change that?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1q5d2UtyfPlUytPjTwOwp7gN4UpxfFjsCKTHcXelLJyw/edit
- **next-steps-effort** [command track] — Under Next steps, the estimated effort is now 4 dev-days, not 3. Can you change that?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1G-ZtJ-yw3zA_HfgCHmdTSaoFrUwXDlBG-_ls8YvikOY/edit
- **reply-and-resolve-v3-comment** — Someone left a comment asking whether v3 is the final name. Reply to it with "Yes, v3 is final — Tomás confirmed on 1 Sept." and mark it resolved.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1MvuelNtyr-OXHxrtVuO8McZ_tH9PZ9ZJkmWZgt501fQ/edit
- **rollout-to-launch-window** — In the TL;DR paragraph we now call it the "launch window", not the "rollout window". Can you rename it there? Leave the rest of the doc alone.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1qSJ9ILLnsJRdbKe6bjZi53gGQ9yzMQHu8V7tApfGuIw/edit
- **rollout-to-launch-window** [command track] — In the TL;DR paragraph we now call it the "launch window", not the "rollout window". Can you rename it there? Leave the rest of the doc alone.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/11u7dM6gcu0epIsitLmmL9y_V4iB-cbozOIXHVPpH_F8/edit
- **add-open-question** [batch 20260903-batch] — Add one more open question at the end of Tomás's list: "Do we need a rollback drill before the 15th?"
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit
- **budget-cloud-credits** [batch 20260903-batch] — In the budget table, the cloud credits line should say $12,900 now, not $12,400. Please update it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit
- **fix-double-numbering** [batch 20260903-batch] — In Tomás's open-questions list, items 2 and 3 show their number twice ("2) 2)", "3) 3)"). Remove the typed duplicates so the list just reads 1) 2) 3).
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit
- **footnote-v8** [batch 20260903-batch] — The footnote at the bottom still says Finance sheet v7 pulled 28 Aug by Tomás. It's v8 now, pulled 2 Sept by Priya. Please fix the footnote.
  - Outcome: **GAP-CLI** · edited copy: https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit
- **next-steps-effort** [batch 20260903-batch] — Under Next steps, the estimated effort is now 4 dev-days, not 3. Can you change that?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit
- **reply-and-resolve-v3-comment** [batch 20260903-batch] — Someone left a comment asking whether v3 is the final name. Reply to it with "Yes, v3 is final — Tomás confirmed on 1 Sept." and mark it resolved.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit
- **rollout-to-launch-window** [batch 20260903-batch] — In the TL;DR paragraph we now call it the "launch window", not the "rollout window". Can you rename it there? Leave the rest of the doc alone.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA/edit

## lists/v01

Fixture (before): https://docs.google.com/document/d/1dmd4Qf3PyZ48fJpOtzI7_2OcCSS3Iy7Ea05l4r7rtQ8/edit

Batch `20260903-batch` (12 edits in sequence on one copy): run copy https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit · **painted review copy** https://docs.google.com/document/d/1C_cW3_cHTPO9U3kRocHHR61POUSa_4CpzkCj1r3PRso/edit

- **checklist-insert-after-checked-runbook** — In the onboarding checklist, add "Get added to the on-call rota (ask Marco)" as a new checkbox right after the runbook one.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1cdQX3-1OK_OkBFg0uh6tgMZuHRxden7pUTsdUHvrPvM/edit
- **environments-nest-stray-lines-under-production** — Priya's Environments section is a mess — the read replica line and the staging line are meant to be sub-bullets under Production, same level as the GKE cluster one. Can you tidy that up?
  - Outcome: **GAP-CLI** · edited copy: https://docs.google.com/document/d/1ad_keNXt0cvxhq_2gNTQqEJQG9FmZuE1I7NvDvUb8QU/edit
- **insert-migration-step** — Add a step to the release plan between "Deploy to staging" and "Smoke test the payment flow": "Run the DB migrations on staging (Priya)". It should become step 5 and the ones after it shift down.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1PjSTDvCHTuhruqJNuzkLitQRMEd63h9qE_AE1sIbu8o/edit
- **key-rotation-owner-to-priya** — Marco's off the key rotation, Priya's picking it up — can you update the action items?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1lQj4IUjhYEEoIjxjZSru1I-cPqaK5Ct4UyAH3fg--_c/edit
- **kubectl-namespace** — The kubectl line in the action items should target the staging-eu namespace, not staging.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1rmfBG6B1s2eoeFxMUR6Lu9r3jzMF_q6oK7OPXGe43UU/edit
- **kubectl-namespace** [command track] — The kubectl line in the action items should target the staging-eu namespace, not staging.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/12sT33c2-eoUwm3SIbTpE7vklDU6tlYcjhnBG96mCoPk/edit
- **legal-approval-date-georgia-run** — Legal actually approved on 21 Aug, not 14 — fix the action items.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1nr4qVjh3QVsl5fV0j4MOjOt6GxFMKgs656wYhauhX1Y/edit
- **legal-approval-date-georgia-run** [command track] — Legal actually approved on 21 Aug, not 14 — fix the action items.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1l6V-tx0gqet4jex-pZ6S_kNLF0aoiSKj-bVfYRsCmWg/edit
- **relink-rotate-keys** — Marco's action item links to the old rotate-keys page. Point it at https://example.com/runbooks/rotate-keys instead.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1ySUMvKECwMRaFvHHAG2SMQrsylcFrc7wOzlAKxSLyJ8/edit
- **russian-readme** — In the action items, the ship-date line says "Cyrillic README" — it should say "Russian README".
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/12Srh6sbRZ7OfhHMjYPmU1zrOSx99I18MT1jlpvp9M_Q/edit
- **smoke-test-apple-pay** — In the release plan, step 5 should also mention Apple Pay: "Smoke test the payment flow (card + SEPA + Apple Pay)".
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1cDsJH3HR9ggjk7AnoqAAbfMTqzy7oM8sD5IltfcjlaQ/edit
- **staging-line-to-bullet** — Under Environments, the "Staging shares the prod cluster" line was typed with a dash instead of being a real bullet. Make it a proper bullet at the same level as "Also a read replica", and drop the typed dash.
  - Outcome: **GAP-CLI** · edited copy: https://docs.google.com/document/d/1i5SotBYLGvmCbyTf2KImSs8YlTeY5XwtXnJSjAj_uc4/edit
- **tick-pair-with-buddy** — In the onboarding checklist, tick off "Pair with your buddy for a week" — that's done now.
  - Outcome: **DECLINED-API** · edited copy: https://docs.google.com/document/d/1t0kUEaJHBv8HMq3Y7cFSuJyDKFjwyTFasTpwT7XUhjs/edit
- **unblock-security-review** — Sam finished the security review. Change the BLOCKED item to "DONE: security review signed off (Sam, 2 Sep)" and remove the yellow highlight from it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1eoLP2JuxOMiwtN37bPK2IaPg1xqN2yXRXxOvfxos1QA/edit
- **checklist-insert-after-checked-runbook** [batch 20260903-batch] — In the onboarding checklist, add "Get added to the on-call rota (ask Marco)" as a new checkbox right after the runbook one.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **environments-nest-stray-lines-under-production** [batch 20260903-batch] — Priya's Environments section is a mess — the read replica line and the staging line are meant to be sub-bullets under Production, same level as the GKE cluster one. Can you tidy that up?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **insert-migration-step** [batch 20260903-batch] — Add a step to the release plan between "Deploy to staging" and "Smoke test the payment flow": "Run the DB migrations on staging (Priya)". It should become step 5 and the ones after it shift down.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **key-rotation-owner-to-priya** [batch 20260903-batch] — Marco's off the key rotation, Priya's picking it up — can you update the action items?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **kubectl-namespace** [batch 20260903-batch] — The kubectl line in the action items should target the staging-eu namespace, not staging.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **legal-approval-date-georgia-run** [batch 20260903-batch] — Legal actually approved on 21 Aug, not 14 — fix the action items.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **relink-rotate-keys** [batch 20260903-batch] — Marco's action item links to the old rotate-keys page. Point it at https://example.com/runbooks/rotate-keys instead.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **russian-readme** [batch 20260903-batch] — In the action items, the ship-date line says "Cyrillic README" — it should say "Russian README".
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **smoke-test-apple-pay** [batch 20260903-batch] — In the release plan, step 5 should also mention Apple Pay: "Smoke test the payment flow (card + SEPA + Apple Pay)".
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **staging-line-to-bullet** [batch 20260903-batch] — Under Environments, the "Staging shares the prod cluster" line was typed with a dash instead of being a real bullet. Make it a proper bullet at the same level as "Also a read replica", and drop the typed dash.
  - Outcome: **FAIL-AGENT** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **tick-pair-with-buddy** [batch 20260903-batch] — In the onboarding checklist, tick off "Pair with your buddy for a week" — that's done now.
  - Outcome: **DECLINED-API** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit
- **unblock-security-review** [batch 20260903-batch] — Sam finished the security review. Change the BLOCKED item to "DONE: security review signed off (Sam, 2 Sep)" and remove the yellow highlight from it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E/edit

## tables/v01

Fixture (before): https://docs.google.com/document/d/1qkVHvm__en97IXhioB83XK4lBKV6bvq67Aq6PcWbSYM/edit

Batch `20260903-batch` (11 edits in sequence on one copy): run copy https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit · **painted review copy** https://docs.google.com/document/d/1ROv2UtcrrIx2OZer0B54P3OYLiFH-nl5H-7QOazdPHM/edit

- **acme-cost-49000** — Acme Cloud's Q3 cost went up to 49,000 — can you update the vendor table?
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1DoaABtJiJrPMo0cZIfcWslPz0xVFSHLsUD1SYX4TT0U/edit
- **contoso-status-approved** — Contoso got approved after all. In the vendor table set its status to "Aprobado ✅", same as Acme.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1Hm3RLoZl3vZQig5wtbMJOZFh_xTM7Fwh0pOwH00e6Sw/edit
- **data-engineer-owner-handover** — Priya's off the data engineer search, Tomás is running it now — can you update the doc?
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1aTmkASrLa9j3nAHhvxhElPRU-zx7UuAUizXNcTk6BS8/edit
- **datawise-status-approved** — Datawise cleared legal on Friday. Update its status in the vendor table to Aprobado ✅ (same as Acme).
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1C3vgCkLEhAFpqbDJJpMTljULic-jBDzgxfEZRE7rhX8/edit
- **fill-empty-vendor-row** — Add Globex to the vendor table — 3,200 a quarter, Priya to sign the SOW, status approved (Aprobado ✅, same as Acme). There's an empty row at the bottom you can use.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1ERvkyuWiArSdxaZEfI6rg4k_8ZS61qTOJ0iTkFcJaHg/edit
- **merged-owner-cell-interim** — In the vendor table, the owner cell that straddles Northwind and Contoso: swap "Owner TBD" for "Owner: Ops (interim)" and keep the rest of the sentence as is.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1BlKNohENUHdLKiyVS9-NXtrEAXH-_wJ-3wI3Lwp75YQ/edit
- **northwind-quote** — Northwind finally sent the revised quote: 9,800. Put that in the vendor table where it says n/a.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1dZ4zsTLV16risYF8S_D7z04K5Lv9hpmhFWiL7cQ39P8/edit
- **ops-coordinator-start-date** — The Ops coordinator start date in the hiring pipeline is confirmed now — drop the "(tbc)" after it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1imMt92cJ_DJSwMIu04GA68UQkyEMYmn3pWQz2JldAQw/edit
- **paused-until-q1** — Recruiter row in the hiring pipeline: it's paused until Q1 now, not Q4.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dhBqDTCQl5ww7f6G3EVZNqS9CbSTRUpiXkn10XGQzeo/edit
- **remove-empty-vendor-row** — There's an empty row at the bottom of the vendor comparison table — please delete it.
  - Outcome: **GAP-CLI** · edited copy: https://docs.google.com/document/d/1HCthEBYg9HxhN6DgnuXul1kUoFcjXvQHhoSITG8AMoQ/edit
- **reply-owner-comment** — Someone asked in a comment who owns the Northwind line. Reply "Finance confirmed on 2 Sept — it's Ops." but leave the comment open.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1uWlRDfjojfBdmYycc1axvyBiRi_Vm5vYIWMNclGyKL4/edit
- **acme-cost-49000** [batch 20260903-batch] — Acme Cloud's Q3 cost went up to 49,000 — can you update the vendor table?
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **contoso-status-approved** [batch 20260903-batch] — Contoso got approved after all. In the vendor table set its status to "Aprobado ✅", same as Acme.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **data-engineer-owner-handover** [batch 20260903-batch] — Priya's off the data engineer search, Tomás is running it now — can you update the doc?
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **datawise-status-approved** [batch 20260903-batch] — Datawise cleared legal on Friday. Update its status in the vendor table to Aprobado ✅ (same as Acme).
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **fill-empty-vendor-row** [batch 20260903-batch] — Add Globex to the vendor table — 3,200 a quarter, Priya to sign the SOW, status approved (Aprobado ✅, same as Acme). There's an empty row at the bottom you can use.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **merged-owner-cell-interim** [batch 20260903-batch] — In the vendor table, the owner cell that straddles Northwind and Contoso: swap "Owner TBD" for "Owner: Ops (interim)" and keep the rest of the sentence as is.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **northwind-quote** [batch 20260903-batch] — Northwind finally sent the revised quote: 9,800. Put that in the vendor table where it says n/a.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **ops-coordinator-start-date** [batch 20260903-batch] — The Ops coordinator start date in the hiring pipeline is confirmed now — drop the "(tbc)" after it.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **paused-until-q1** [batch 20260903-batch] — Recruiter row in the hiring pipeline: it's paused until Q1 now, not Q4.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **remove-empty-vendor-row** [batch 20260903-batch] — There's an empty row at the bottom of the vendor comparison table — please delete it.
  - Outcome: **GAP-CLI** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit
- **reply-owner-comment** [batch 20260903-batch] — Someone asked in a comment who owns the Northwind line. Reply "Finance confirmed on 2 Sept — it's Ops." but leave the comment open.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8/edit

## text/v01

Fixture (before): https://docs.google.com/document/d/1zU7pmkVdMCQEfJYSZ5-fTvoXUMWGtTuAcFyXNRqFZfU/edit

Batch `20260903-batch` (11 edits in sequence on one copy): run copy https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit · **painted review copy** https://docs.google.com/document/d/1QgeTu7gHOcrZdIfHwv7KrkNVBz8WodXx8vjyTCwlkgg/edit

- **beta-badge-straight-quotes** — In the Key dates paragraph, the "beta" badge — the one written with straight quotes — is called the "preview" badge now. Marta's “beta” label stays as it is.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1ZKZe1veY5CoZeso7giZevp5Ylqs8SGoZnzzoe1IvJUU/edit
- **co2-formula** — Formula card sentence: it should say CO₂, not H₂O.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1l9YR63VcYsDzwQ51QPULyyGfOdVD7ObWnMZ4qOYlftc/edit
- **drop-old-plan** — The struck-through "The old plan was to ship in August" bit has served its purpose — delete it, so the paragraph starts with the new plan.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1zTiD6HAm0xI2MicX-cikP44qWGV2tP_bOSuxnFY_X3I/edit
- **hyphen-date-fix** — In the Key dates paragraph, the v2 draft's date range uses a plain hyphen (14-18 Sept). Make it an en dash like the first one.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1JgkCn051KdkR4UCEUcgUa1MGM-p4djiAtRfe7u_wxk8/edit
- **key-dates-en-dash-slip** — Key dates: the launch window has slipped a day — it now opens 15–19 Sept 2026. Please change just that first sentence; leave the "v2 draft" and "CMS" examples as they are, and don't touch the old-plan paragraph further down, I'm still confirming that with Legal.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1MVRtdjBISP14w02P-W98cLNg3am45R6m-w3M4J7_mPY/edit
- **launch-to-release-window** — We're calling it the "release window" now, not the "launch window" — rename it everywhere in the doc, title included. "Launch Window banner" is a product name, leave that.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1bAhK5W2tB8t8l-UKqHyuKMRpuVw4DdsE_W3lhRNDadk/edit
- **marta-quote-tuesday-afternoon** — In the announcement copy paragraph, Marta's Slack quote is truncated — what she actually wrote in #launch was "we finally fixed the sync bug that ate everyone's Tuesday afternoon". Can you fix the quote?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1HqwzQHIEiWa7SGa_2RVLf4phIhmymhmcRyzCw3Zo7VI/edit
- **northstar-2-2** — The release is now Northstar 2.2, not 2.1. Update the body copy; the title gets its own review so leave that.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1kP7USBo5sRqaUXTN5q9Umvy4DyJnUw4X7-p9aTfewZE/edit
- **rename-key-dates-fake-heading** — Rename the "Key dates" subheading to "Key dates and labels" — that section now covers the beta label as well.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1-kOq8bcbBro3eRPioKNjD9jeFR1Q_GwRmve0gllmYvU/edit
- **signature-date** — Bump the date in Marta's signature line to 3 Sept 2026.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1CcjnJ_WpnmfW1tPoSHqNvSA0f7_pHeDttwy33Bi9aqU/edit
- **beta-badge-straight-quotes** [batch 20260903-batch] — In the Key dates paragraph, the "beta" badge — the one written with straight quotes — is called the "preview" badge now. Marta's “beta” label stays as it is.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **co2-formula** [batch 20260903-batch] — Formula card sentence: it should say CO₂, not H₂O.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **drop-old-plan** [batch 20260903-batch] — The struck-through "The old plan was to ship in August" bit has served its purpose — delete it, so the paragraph starts with the new plan.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **hyphen-date-fix** [batch 20260903-batch] — In the Key dates paragraph, the v2 draft's date range uses a plain hyphen (14-18 Sept). Make it an en dash like the first one.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **key-dates-en-dash-slip** [batch 20260903-batch] — Key dates: the launch window has slipped a day — it now opens 15–19 Sept 2026. Please change just that first sentence; leave the "v2 draft" and "CMS" examples as they are, and don't touch the old-plan paragraph further down, I'm still confirming that with Legal.
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **launch-to-release-window** [batch 20260903-batch] — We're calling it the "release window" now, not the "launch window" — rename it everywhere in the doc, title included. "Launch Window banner" is a product name, leave that.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **marta-quote-tuesday-afternoon** [batch 20260903-batch] — In the announcement copy paragraph, Marta's Slack quote is truncated — what she actually wrote in #launch was "we finally fixed the sync bug that ate everyone's Tuesday afternoon". Can you fix the quote?
  - Outcome: **DONE** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **northstar-2-2** [batch 20260903-batch] — The release is now Northstar 2.2, not 2.1. Update the body copy; the title gets its own review so leave that.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **rename-key-dates-fake-heading** [batch 20260903-batch] — Rename the "Key dates" subheading to "Key dates and labels" — that section now covers the beta label as well.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **signature-date** [batch 20260903-batch] — Bump the date in Marta's signature line to 3 Sept 2026.
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
- **tidy-double-spaces** — There are a bunch of stray double spaces in this draft — can you tidy them up?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1MTD0MJav8tqasmSD2qKPpIGTUHJFjhU4Ie0iNZDAOeg/edit
- **tidy-double-spaces** [batch 20260903-batch] — There are a bunch of stray double spaces in this draft — can you tidy them up?
  - Outcome: **COLLATERAL** · edited copy: https://docs.google.com/document/d/1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4/edit
