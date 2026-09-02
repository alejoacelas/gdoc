# gdt-lists-v01 — as built

- Built 2026-09-02 by hand in Chrome, account alejandro.acelas-contractor@80000hours.org.
- Doc: https://docs.google.com/document/d/1dmd4Qf3PyZ48fJpOtzI7_2OcCSS3Iy7Ea05l4r7rtQ8/edit
- One tab (`Tab 1`). Two pages. Named version `frozen` (named last; no edits after).
- Mode left in **Editing**. One open comment, one pending suggestion (see formatting map).

## Exact text, top to bottom

Legend: `[H1]`/`[H2]`/`[H3]` heading paragraphs, `[N]` Normal text, `[L n.]` numbered list item
rendering as `n.`, `[CK ☑]`/`[CK ☐]` checklist item (ticked/unticked), `[● ]`/`[○ ]`/`[■ ]`
bullet at nesting level 1/2/3, `[- ]` real list item whose glyph is a dash. `⇥` = tab
character, `␣` = trailing space, `⏎` = soft line break (shift+Return, U+000B in the API).
`**…**`, `*…*`, `[…](url)` mark bold, italic, link (not literal characters). Indents are
paragraph indents in cm as shown on the ruler.

```
[H1] Platform team Q3 release plan and onboarding
[N]  Living doc. Marco started it in May, Priya pasted the infra steps from Slack, and the onboarding bit came from Word. Before touching prod, rotate the API keys and tell #platform-team. Last reviewed 28 Aug 2026 – still messy.
[H2] Release plan (v2.14)
[L 1.] Freeze feature branches by Friday 5pm                              ← LIST A starts at 1
[L 2.] Run the full regression suite (takes ~40 min)
[L 3.] Tag release candidate rc1 and **rotate the API keys**
[N]  Note from Priya: steps 4 to 6 are owned by infra, ping @marco if staging is red.
[L 4.] Deploy to staging⇥(infra, not us)                                  ← LIST B, "Continue previous numbering" (renders 4–6)
[L 5.] Smoke test the payment flow (card + SEPA)
[L 6.] Ship to 5% of users␣␣
[N]  Post-launch (Marco pasted this bit from Slack so the numbers start over, sorry):
[L 1.] Watch the error budget for 48h                                     ← LIST C, restarts at 1
[L 2.] Ship to 100% and close the milestone
[H2] Onboarding checklist (from the Word doc)
[L 1.] Get your laptop from IT (ask for the 16GB one)                     ← LIST D numbered, starts at 1
[L 2.] Set up access: 1) GitHub org 2) VPN 3) Vault, in that order
[L 3.] Join #platform-team and #incidents in Slack
[CK ☑] Read the runbook 📘 (the one in Notion, not the wiki)              ← LIST E checklist, separate list object, directly under D
[CK ☐] Pair with your buddy for a week
[CK ☐]                                                                    ← empty checklist item
[CK ☑] Ship a one-line fix to production
[N]  a. Ask Sam for the VPN config, he is on leave until 9 Sep            ← plain paragraph, "a. " typed as text
[H2] Environments (Priya, pasted from Slack)
[● ] Production                                                           ← LIST F bulleted, level 1
[○ ]   GKE cluster prod-eu-west1 (the old one, not prod-eu-west1-b)       ← level 2
[■ ]     Node pool n2-standard-4, autoscaling 3 to 12                     ← level 3
[■ ]     Secrets live in Vault under secret/platform/prod, rotate the API keys there
[- ]     Also a read replica in eu-west3, ask Priya before touching it    ← LIST G: separate list, dash glyph (autoformat from "- "), sits at the ■ indent
[N]      -⇥Staging shares the prod cluster, namespace staging (yes, really)   ← Normal, indent 3.81cm, "-" and tab typed as text
                                                                          ── page break (heading keeps with next) ──
[H2] Action items from the 28 Aug sync
[● H3] Decisions                                                          ← LIST H bulleted; this item has paragraph style Heading 3
[● ] We ship v2.14 on 12 Sep even if the Cyrillic README is not done      ← PENDING SUGGESTION: replace "12" with "19"
[● ] **Owners and dates**                                                 ← Normal text, bold, 14pt (fake heading inside list)
[● ] 🚀 Launch comms: José y María revisarán el correo del anuncio *(¿en español también?)*
[● ] 日本語のドキュメントを更新する (Yuki) 📝
[● ] Обновить README на русском, спросить Дмитрия                         ← COMMENT anchor starts at "спросить"
[● ] Marco to [rotate the API keys](https://example.com/rotate-keys) before Friday   ← COMMENT anchor ends after "Marco to"
[● ] Contact for infra questions:⏎priya@example.com, or DM her on Slack   ← soft line break; email autolinked (mailto:)
[N]    Actually the retro room is booked till 3pm on the 12th, use Zoom instead and skip the next two items if you are not on infra.   ← Normal, indent 1.27cm, sits INSIDE list H (H continues below)
[● ] Kubectl rollout restart deploy/api -n staging                        ← "Kubectl rollout restart deploy/api" Courier New 10pt
[● ] Approved by Legal on 14 Aug, see the thread                          ← "14 Aug, see the thread" Georgia 13pt
[● ] Owner:⇥Marco␣␣                                                       ← "Owner" Georgia 13pt (same run continues from previous item)
[● ] BLOCKED: waiting on the security review (Sam, again)                 ← "BLOCKED:" red; whole item yellow highlight
[● ]                                                                      ← empty bullet item
[N]  **Appendix**                                                         ← Normal text, bold, 14pt (fake heading)
[H2] Appendix A: glossary                                                 ← real H2 directly below the fake one
[● ] Rc = release candidate, we number them rc1, rc2, …                   ← LIST I bulleted
[● ] Error budget = the 0.1% we are allowed to break (see the SRE book, ch. 4)
[● ] Rotate the API keys = the runbook step, not the Vault UI button
[N]  Questions: ask in #platform-team, not in DMs.
```

List objects: A (1–3), B (4–6, continues A's numbering via right-click "Continue previous
numbering"), C (restarts at 1), D (numbered 1–3), E (checklist, 4 items incl. one empty),
F (three-level bullets ● ○ ■), G (one dash-glyph item created by autoformat, at level-3
indent), H (bulleted, 13 items incl. an H3 item and an empty item; the indented Normal
paragraph "Actually the retro room…" is between two H items and H resumes after it),
I (bulleted, 3 items).

## Formatting map

| Where | Text | Formatting |
|---|---|---|
| Title | Platform team Q3 release plan and onboarding | Heading 1 |
| Section titles | Release plan (v2.14) · Onboarding checklist (from the Word doc) · Environments (Priya, pasted from Slack) · Action items from the 28 Aug sync · Appendix A: glossary | Heading 2 |
| Intro | "28 Aug 2026 – still messy" | en dash (autocorrected from `--`) |
| List A item 3 | rotate the API keys | **bold** (rest of item plain) |
| List B item 4 | Deploy to staging⇥(infra, not us) | tab character between "staging" and "(infra" |
| List B item 6 | Ship to 5% of users␣␣ | two trailing spaces |
| List E ticked items | Read the runbook 📘 (the one in Notion, not the wiki) · Ship a one-line fix to production | checked; Docs auto-applied strikethrough + grey text colour |
| List E | third item | empty checklist item |
| After list E | a. Ask Sam for the VPN config, he is on leave until 9 Sep | Normal, no indent, "a." is literal text |
| List F | ● Production / ○ GKE cluster… / ■ Node pool… / ■ Secrets live… | bullets, nesting levels 1/2/3, default glyphs ● ○ ■ |
| List G | Also a read replica in eu-west3, ask Priya before touching it | separate bulleted list, glyph "-", rendered at the ■ indent |
| Below G | -⇥Staging shares the prod cluster, namespace staging (yes, really) | Normal text, left indent 3.81cm (3× increase indent), leading "-" + tab typed as text |
| List H item 1 | Decisions | paragraph style Heading 3, still a bullet item |
| List H item 3 | Owners and dates | Normal text, bold, 14pt |
| List H item 4 | (¿en español también?) | *italic* (rest of item plain); item starts with 🚀 |
| List H item 5 | 日本語のドキュメントを更新する (Yuki) 📝 | plain |
| List H item 6 | Обновить README на русском, спросить Дмитрия | plain |
| List H item 7 | rotate the API keys | link → https://example.com/rotate-keys (rest plain) |
| List H item 8 | Contact for infra questions:⏎priya@example.com, or DM her on Slack | soft line break after ":"; "priya@example.com" autolinked mailto:priya@example.com |
| Inside H | Actually the retro room is booked till 3pm on the 12th, use Zoom instead and skip the next two items if you are not on infra. | Normal text, left indent 1.27cm, not a list item |
| List H item 9 | Kubectl rollout restart deploy/api | Courier New, 10pt; " -n staging" stays Arial 11 |
| List H items 10–11 | 14 Aug, see the thread ⏎(paragraph break) Owner | one Georgia 13pt run spanning the end of item 10 and the start of item 11; "Approved by Legal on " and ":⇥Marco␣␣" stay Arial 11 |
| List H item 11 | Owner:⇥Marco␣␣ | tab char after "Owner:", two trailing spaces |
| List H item 12 | BLOCKED: | text colour red (#ff0000); whole item has yellow highlight (#ffff00) |
| List H item 13 | (empty) | empty bullet item |
| Fake heading | Appendix | Normal text, bold, 14pt, no indent |
| List I | Rc = … / Error budget = … / Rotate the API keys = … | plain bullets; "…" is a single ellipsis char |
| Closing | Questions: ask in #platform-team, not in DMs. | Normal |

**Comment (open, unresolved)** — anchored from "спросить Дмитрия" (end of list H item 6)
through the paragraph break to "Marco to" (start of item 7). Text:
"Dmitry is out until 15 Sep, so this and the key rotation both slip. Who picks them up?"
Author Alejandro Acelas, 21:50.

**Suggestion (pending, not accepted)** — in "We ship v2.14 on 12 Sep even if the Cyrillic
README is not done": replace "12" with "19". Made in Suggesting mode, then mode switched back
to Editing. Shows as "Replace: "12" with "19"", 21:51.

Phrase "rotate the API keys" occurrences: intro (plain), list A item 3 (bold), list F ■ item
(plain, followed by " there"), list H item 7 (linked), list I item 3 as "Rotate the API keys"
(capital R, autocorrected).

## Autocorrections observed

- `--` → `–` (en dash) in the intro.
- `...` → `…` in glossary item 1.
- First letter of a list item auto-capitalised: node→Node, secrets→Secrets, also→Also,
  kubectl→Kubectl, rc→Rc, error→Error, rotate→Rotate, staging→Staging (the last after a
  leading space, in a Normal paragraph).
- `a. ` at the start of a Normal paragraph became a lettered list item (undone: toggled the
  list off, then typed a space first and inserted "a." before it so no trigger fired).
- `- ` at the start of an indented Normal paragraph became a real bulleted list with a dash
  glyph (kept as list G).
- `1) … 2) … 3)` typed mid-item did not trigger anything.
- Typing `@marco` opened the people-mention popup, which swallowed the following Return
  keys; Escape dismissed it, text stayed literal "@marco".
- `priya@example.com` autolinked as mailto.
- Ticking a checklist box applied strikethrough and grey text colour to the item.
- Smart quotes did not come up (no quotes typed). Curly apostrophes avoided.

## Tried and could not do / detours

- Menu search (alt+/) does not list "Continue previous numbering", only "Restart numbering".
  Used right-click on the first item of list B → "Continue previous numbering".
- Applying Checklist (cmd+shift+9) with items 4–6 selected converted the WHOLE numbered list
  D, even across a blank paragraph splitter (list identity survives a plain paragraph). Fix:
  select items 4–6, toggle numbered list off (cmd+shift+7 with a selection only affects the
  selection), then apply checklist → separate list E; deleted the blank splitter paragraph
  with Backspace so E sits directly under D.
- Georgia was meant for "Approved by Legal on 14 Aug" only; the Home key did not register
  and the run landed on "14 Aug, see the thread" + paragraph break + "Owner". Left as is:
  a formatting run that straddles two list items.
- `End` moves to the end of the visual line, not the paragraph; a Return after a wrapped
  line once split "really)" into the next heading. Fixed by hand (Backspace/retype).
- Shift+click selection failed once because the floating Gemini widget covered the target;
  used keyboard selection (shift+Down/shift+End) instead.
- Every menu-search (alt+/) command scrolls the view back to the top of the doc; had to
  re-scroll before each subsequent click.
- The dash for the "hand-typed dash" level was first autoformatted into a real list (kept
  as list G); the genuinely typed dash is the Normal paragraph below it, made by typing a
  space, then Home, then "-", then deleting the space and inserting a tab.

## TRAP LIST

1. **`rotate the API keys`** — 4 lowercase hits + 1 "Rotate the API keys". Surroundings:
   intro sentence (plain), list A item 3 (bold, end of item), list F ■ item (plain,
   followed by " there"), list H item 7 (link to https://example.com/rotate-keys), glossary
   (capitalised, start of item). A blanket replace clobbers the link or the bold run, misses
   the capitalised one, and Docs `replaceAllText` is case-sensitive by default.
2. **Continued numbering across a paragraph** — list A (1–3) / `Note from Priya: …` (Normal)
   / list B (renders 4–6 via "Continue previous numbering") / `Post-launch (…)` (Normal) /
   list C (1–2). Markdown round-trip renumbers B to 1–3 or fuses A+B; the API sees three
   list IDs. Editing the "Note from Priya" paragraph must not make it a list item.
3. **Manual numbering inside a real item** — `Set up access: 1) GitHub org 2) VPN 3) Vault,
   in that order` is item 2 of list D. A markdown converter may split at `2)`/`3)`, and a
   renumbering pass may bump the literal digits.
4. **`a. Ask Sam for the VPN config, he is on leave until 9 Sep`** — Normal paragraph directly
   below checklist E, looks like a lettered continuation. Round-trip may convert it to a
   list item or strip "a.".
5. **Checked checklist items** — `Read the runbook 📘 (the one in Notion, not the wiki)` and
   `Ship a one-line fix to production` are ☑ with Docs-applied strikethrough + grey. Text
   inserted into them won't carry strikethrough; a rewrite may lose the checked state; the
   empty ☐ item between them tends to be dropped.
6. **Three glyph levels then two kinds of dash** — ● Production / ○ GKE cluster… / ■ Node
   pool… / ■ Secrets… / `-` Also a read replica… (separate list G, dash glyph, level-3
   indent) / `-⇥Staging shares…` (Normal, indent 3.81cm, literal dash+tab). Markdown flattens
   all to `-` bullets and cannot tell G from the typed dash; nesting depth is likely lost.
7. **Interrupting Normal paragraph inside list H** — `Actually the retro room is booked till
   3pm on the 12th, …` (indent 1.27cm) sits between `Contact for infra questions:⏎priya@…`
   and `Kubectl rollout…`; both neighbours are items of the same list. A round-trip either
   makes it a bullet or splits H in two. The preceding item holds a soft line break (U+000B)
   and a mailto autolink.
8. **Heading and fake heading inside a list, fake heading above a real one** — `Decisions`
   is an H3 that is also a bullet of list H; `Owners and dates` is bold 14pt Normal in the
   same list; `Appendix` (bold 14pt Normal) sits directly above H2 `Appendix A: glossary`.
   Markdown emits `### Decisions` outside the list or drops the bullet; heading detection by
   size promotes the fakes.
9. **Font runs that do not respect item boundaries** — `Kubectl rollout restart deploy/api`
   Courier New 10 + ` -n staging` Arial 11 (one item); one Georgia 13 run covers `14 Aug, see
   the thread` + the paragraph break + `Owner`. Replacing text at either end of that run
   changes which paragraph inherits Georgia; markdown may turn the Courier part into a code
   span and lose the size.
10. **Whitespace inside items** — `Deploy to staging⇥(infra, not us)`, `Ship to 5% of
    users␣␣`, `Owner:⇥Marco␣␣`. Tab characters and trailing spaces survive in the API but
    most text pipelines normalise them, so an "unchanged" item diffs.
11. **`BLOCKED: waiting on the security review (Sam, again)`** — "BLOCKED:" red, whole item
    yellow highlight, followed by an empty bullet and then the fake `Appendix` heading.
    Replacing "BLOCKED" changes the colour run boundary; the empty item is often deleted or
    merged; highlight is lost in markdown.
12. **Comment + suggestion + non-Latin text in the same list** — comment anchored across
    `спросить Дмитрия` / `Marco to` (two items); pending suggestion `12`→`19` in `We ship
    v2.14 on 12 Sep…`; items with 🚀 📝 (surrogate pairs), Japanese, Cyrillic, and italic
    `(¿en español también?)`. Index arithmetic in UTF-16 vs code points shifts every edit
    after the emoji; replacing either anchored item orphans the comment or resolves the
    suggestion.
