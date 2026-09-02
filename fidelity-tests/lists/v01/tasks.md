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

<!-- The four tasks below were written by a second agent that read the document cold (CLI only). -->

## checklist-insert-after-checked-runbook

- **Request:** In the onboarding checklist, add "Get added to the on-call rota (ask Marco)" as a new checkbox right after the runbook one.
- **Expected:** The checklist (listId `kix.i11mp0ghmsa2`, all items nesting level 0) has five items in this order: `Read the runbook 📘 (the one in Notion, not the wiki)` (still checked), `Get added to the on-call rota (ask Marco)` (new, unchecked), `Pair with your buddy for a week` (unchecked), an empty item (unchecked, still present), `Ship a one-line fix to production` (still checked). The new paragraph is NORMAL_TEXT with default text style (no strikethrough, no bold). Because the Docs API does not expose checkbox state, the judge checks it via `gdoc cat`: the export must read `- [x] ~~Read the runbook 📘 (the one in Notion, not the wiki)~~`, `- [ ] Get added to the on-call rota (ask Marco)`, `- [ ] Pair with your buddy for a week`, `- [ ]` (empty), `- [x] ~~Ship a one-line fix to production~~`. The numbered list above it (`kix.b32yuebasfdg`, items 1–3) and the plain paragraph `a. Ask Sam for the VPN config…` below it are untouched. Nothing else changes.
- **Target:** Tab `Tab 1`; new paragraph `Get added to the on-call rota`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** List `kix.i11mp0ghmsa2` is a checklist (glyphType `GLYPH_TYPE_UNSPECIFIED`, glyphFormat `%0`) with exactly four items; `gdoc cat` shows the first (`Read the runbook…`) and fourth (`Ship a one-line fix…`) as `[x]` with strikethrough and the third as an empty `[ ]` item. It is immediately preceded by the three-item DECIMAL list `kix.b32yuebasfdg` and followed by a non-list paragraph starting `a. Ask Sam`.

## environments-nest-stray-lines-under-production

- **Request:** Priya's Environments section is a mess — the read replica line and the staging line are meant to be sub-bullets under Production, same level as the GKE cluster one. Can you tidy that up?
- **Expected:** All six paragraphs under `Environments (Priya, pasted from Slack)` belong to list `kix.hh1ksamx4njp`, in this order and at these nesting levels: `Production` (0, ●), `GKE cluster prod-eu-west1 (the old one, not prod-eu-west1-b)` (1, ○), `Node pool n2-standard-4, autoscaling 3 to 12` (2, ■), `Secrets live in Vault under secret/platform/prod, rotate the API keys there` (2, ■), `Also a read replica in eu-west3, ask Priya before touching it` (1, ○), `Staging shares the prod cluster, namespace staging (yes, really)` (1, ○). The leading `-` and tab are removed from the staging paragraph; its remaining text is unchanged. Level-1 items have indentStart 72pt. No paragraph in the document uses list `kix.73yxf78mr7x1` any more. Text and style of the first four items are unchanged; the heading `Action items from the 28 Aug sync` and everything after it are unchanged. Nothing else changes.
- **Target:** Tab `Tab 1`; paragraph beginning `Also a read replica in eu-west3`; paragraph beginning `-⇥Staging shares`.
- **Allowed:** list `kix.73yxf78mr7x1` may disappear from the lists map; automatic list renumbering; revision list grows; `modifiedTime` changes.
- **Preconditions:** Paragraph `Also a read replica…` carries bullet listId `kix.73yxf78mr7x1` (glyphSymbol `-`, indentStart 108pt) at nesting level 0. Paragraph `-\tStaging shares…` has no bullet, indentStart and indentFirstLine 108pt, and starts with a literal hyphen followed by a tab. List `kix.hh1ksamx4njp` has glyphs ●/○/■ for levels 0/1/2 and holds `Production` (0), `GKE cluster…` (1), `Node pool…` (2), `Secrets live in Vault…` (2).

## key-rotation-owner-to-priya

- **Request:** Marco's off the key rotation, Priya's picking it up — can you update the action items?
- **Expected:** In the Action items list (`kix.w0jv2pkvzvcv`, nesting level 0) the paragraph `Marco to rotate the API keys before Friday` now reads `Priya to rotate the API keys before Friday`. The run `rotate the API keys` keeps its hyperlink to `https://example.com/rotate-keys`, underline and link colour; `Priya to ` and ` before Friday` are default style. Comment `#AAACGeAxyJI` (`Dmitry is out until 15 Sep…`) is still open, unresolved and anchored to the document (anchor text now spans `спросить Дмитрия` through `Priya to`); it is not orphaned or deleted. Every other occurrence of `Marco` is unchanged: `Marco started it in May` (intro), `ping @marco` (Priya's note), `Marco pasted this bit` (Post-launch line), `Owner:\tMarco  ` (action item, with its tab and two trailing spaces). Every other occurrence of `rotate the API keys` is unchanged: intro, bold run in release step 3, `Secrets live in Vault…` item, glossary entry. The pending suggestion `suggest.j4mbynnaesii` (`19`/`12` in `We ship v2.14 on…`) remains pending. Nothing else changes.
- **Target:** Tab `Tab 1`; paragraph beginning `Marco to rotate the API keys`; comment.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** Open comment `#AAACGeAxyJI` anchored on `спросить Дмитрия\nMarco to` (spans the end of the Russian item and the start of the Marco item). Paragraph `Marco to rotate the API keys before Friday` has three runs, the middle one linked to `https://example.com/rotate-keys` with `underline: true`. `rotate the API keys` occurs six times in the tab and `Marco` five times (case-insensitive). Suggestion `suggest.j4mbynnaesii` is pending on the `We ship v2.14 on…` item.

## legal-approval-date-georgia-run

- **Request:** Legal actually approved on 21 Aug, not 14 — fix the action items.
- **Expected:** The paragraph `Approved by Legal on 14 Aug, see the thread` reads `Approved by Legal on 21 Aug, see the thread`. Its two runs keep their styles: `Approved by Legal on ` in default style (Arial 11pt), `21 Aug, see the thread` in Georgia 13pt. It stays in list `kix.w0jv2pkvzvcv` at nesting level 0, between `Kubectl rollout restart deploy/api -n staging` and `Owner:\tMarco  `. The neighbours are unchanged: the Courier New 10pt run `Kubectl rollout restart deploy/api` with a default-style ` -n staging` tail; the Georgia 13pt run `Owne` followed by default-style `r:\tMarco  ` (tab and two trailing spaces preserved). The non-list paragraph `Actually the retro room is booked…` (indentStart 36pt, no bullet) stays where it is inside the list. The mid-item line break (`\x0b`) in `Contact for infra questions:` survives. `28 Aug` in the intro and in the heading is unchanged. The pending suggestion `suggest.j4mbynnaesii` remains pending and comment `#AAACGeAxyJI` remains anchored. Nothing else changes.
- **Target:** Tab `Tab 1`; paragraph beginning `Approved by Legal on`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** Paragraph `Approved by Legal on 14 Aug, see the thread` has two runs, the second (`14 Aug, see the thread`) in Georgia 13pt; `14 Aug` occurs exactly once in the tab. Adjacent items carry a Courier New 10pt run (`Kubectl rollout restart deploy/api`) and a Georgia 13pt run split mid-word (`Owne`). A non-list paragraph (`Actually the retro room…`) sits inside list `kix.w0jv2pkvzvcv`. Suggestion `suggest.j4mbynnaesii` is pending and comment `#AAACGeAxyJI` is open.
