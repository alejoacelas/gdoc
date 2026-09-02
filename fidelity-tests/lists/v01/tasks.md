# Tasks — gdt-lists-v01

Five fields each; see the skill's Tasks section. Slugs are the run directory names. List
ids: A+B (release plan 1–6, one list continued across a paragraph) `kix.ehmbnlna9fov`;
C (post-launch 1–2) `kix.dx1f61md5r8c`; D (onboarding 1–3) `kix.b32yuebasfdg`; E
(checklist) `kix.i11mp0ghmsa2`; F (● ○ ■) `kix.hh1ksamx4njp`; G (dash) `kix.73yxf78mr7x1`;
H (action items) `kix.w0jv2pkvzvcv`; I (glossary) `kix.tl04zsv028z9`.

## smoke-test-apple-pay

- **Request:** In the release plan, step 5 should also mention Apple Pay: "Smoke test
  the payment flow (card + SEPA + Apple Pay)".
- **Expected:** The item reads `Smoke test the payment flow (card + SEPA + Apple Pay)`,
  still in list `kix.ehmbnlna9fov` at nesting 0, so it still renders as `5.`. Step 4 keeps
  its tab character, step 6 its two trailing spaces, the `Note from Priya` paragraph stays
  a plain paragraph. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Smoke test the payment flow`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** items 1–3 and 4–6 share listId `kix.ehmbnlna9fov` with the Normal
  paragraph `Note from Priya` between them.

## insert-migration-step

- **Request:** Add a step to the release plan between "Deploy to staging" and "Smoke test
  the payment flow": "Run the DB migrations on staging (Priya)". It should become step 5
  and the ones after it shift down.
- **Expected:** A new item `Run the DB migrations on staging (Priya)` in list
  `kix.ehmbnlna9fov`, nesting 0, default text style, directly after `Deploy to
  staging⇥(infra, not us)`; the following items render 6. and 7. `Deploy to staging` keeps
  its tab; `Ship to 5% of users` keeps its two trailing spaces; list C still restarts at 1.
  Nothing else changes.
- **Target:** tab `Tab 1`, new paragraph `Run the DB migrations`.
- **Allowed:** automatic list renumbering; revision list grows; `modifiedTime` changes.
- **Preconditions:** `Deploy to staging` and `Smoke test` are adjacent items of
  `kix.ehmbnlna9fov`.

## tick-pair-with-buddy

- **Request:** In the onboarding checklist, tick off "Pair with your buddy for a week" —
  that's done now.
- **Expected:** The checkbox of `Pair with your buddy for a week` is ticked (screenshot),
  and the item carries the same struck-through grey style Docs gives the other ticked
  items. Text unchanged. The empty checklist item below it survives. Nothing else changes.
  (Expected to be impossible: the Docs API exposes no checkbox state.)
- **Target:** tab `Tab 1`, paragraph beginning `Pair with your buddy`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** checklist `kix.i11mp0ghmsa2` has four items, two ticked
  (strikethrough + grey in `structure`), one empty.

## relink-rotate-keys

- **Request:** Marco's action item links to the old rotate-keys page. Point it at
  https://example.com/runbooks/rotate-keys instead.
- **Expected:** In `Marco to rotate the API keys before Friday` the link on `rotate the
  API keys` has url `https://example.com/runbooks/rotate-keys`; the text is unchanged. The
  four other occurrences of `rotate the API keys` / `Rotate the API keys` are unchanged
  (plain, bold, plain, plain). The open comment anchored on `спросить Дмитрия` + `Marco
  to` is still there with the same quoted text. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Marco to rotate`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the open comment with `quotedFileContent` `спросить Дмитрия\nMarco
  to` exists in the copy; the link `https://example.com/rotate-keys` is present.

## staging-line-to-bullet

- **Request:** Under Environments, the "Staging shares the prod cluster" line was typed
  with a dash instead of being a real bullet. Make it a proper bullet at the same level as
  "Also a read replica", and drop the typed dash.
- **Expected:** The paragraph reads `Staging shares the prod cluster, namespace staging
  (yes, really)` with no leading `-` or tab, and is a bullet in list `kix.73yxf78mr7x1`
  (the same list as `Also a read replica…`) at nesting 0. The ● ○ ■ items above are
  unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `-⇥Staging shares`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the paragraph is Normal text with indentStart 108pt starting with a
  literal `-` and a tab; `Also a read replica` is in `kix.73yxf78mr7x1`.

## russian-readme

- **Request:** In the action items, the ship-date line says "Cyrillic README" — it should
  say "Russian README".
- **Expected:** The item reads `We ship v2.14 on 12 Sep even if the Russian README is not
  done` with the pending suggestion replacing `12` with `19` still pending (not accepted,
  not rejected; `suggestedInsertionIds`/`suggestedDeletionIds` still present). Item still
  in `kix.w0jv2pkvzvcv`. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `We ship v2.14`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the pending suggestion (`12`→`19`) is present in the copy.

## unblock-security-review

- **Request:** Sam finished the security review. Change the BLOCKED item to "DONE:
  security review signed off (Sam, 2 Sep)" and remove the yellow highlight from it.
- **Expected:** The item reads `DONE: security review signed off (Sam, 2 Sep)` with no
  background colour on any run; still a bullet in `kix.w0jv2pkvzvcv`. The empty bullet
  after it and the bold 14pt `Appendix` paragraph below are unchanged. Nothing else
  changes.
- **Target:** tab `Tab 1`, paragraph beginning `BLOCKED: waiting`.
- **Allowed:** `DONE:` may be red or default colour; revision list grows; `modifiedTime`
  changes.
- **Preconditions:** the item has yellow `backgroundColor` on its runs and red
  `foregroundColor` on `BLOCKED:`; the empty bullet after it exists.

## kubectl-namespace

- **Request:** The kubectl line in the action items should target the staging-eu
  namespace, not staging.
- **Expected:** The item reads `Kubectl rollout restart deploy/api -n staging-eu`; the
  Courier New 10pt run on `Kubectl rollout restart deploy/api` is intact and ` -n
  staging-eu` is default Arial 11. Every other `staging` in the document (`Deploy to
  staging`, `if staging is red`, `namespace staging`) is unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Kubectl rollout`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** Courier New 10pt run present on the item.
